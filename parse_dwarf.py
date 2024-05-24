import lief
import capstone
import argparse
import os
import json
from elftools.elf.elffile import ELFFile
from elftools.dwarf.descriptions import describe_form_class

def create_func_address_map(dwarfinfo):
    address_map = {}
    # Iterate over all compilation units
    for CU in dwarfinfo.iter_CUs():
        comp_dir = CU.get_top_DIE().attributes.get('DW_AT_comp_dir', {}).value
        for DIE in CU.iter_DIEs():
            if DIE.tag == 'DW_TAG_subprogram':
                try:
                    func_name = DIE.attributes['DW_AT_name'].value

                    low_pc = DIE.attributes['DW_AT_low_pc'].value
                    high_pc_attr = DIE.attributes['DW_AT_high_pc']
                    high_pc_class = describe_form_class(high_pc_attr.form)
                    
                    if high_pc_class == 'address':
                        high_pc = high_pc_attr.value
                    elif high_pc_class == 'constant':
                        high_pc = low_pc + high_pc_attr.value
                    else:
                        continue

                    # Retrieve the line information for the function start
                    lineprog = dwarfinfo.line_program_for_CU(CU)
                    prevstate = None
                    file_name = None
                    line_number = None

                    for entry in lineprog.get_entries():
                        if entry.state is None:
                            continue
                        if entry.state.address == low_pc:
                            file_index = entry.state.file
                            file_entry = lineprog['file_entry'][file_index]
                            directory = comp_dir.decode()
                            file_name = os.path.join(directory, file_entry.name.decode())
                            line_number = entry.state.line
                            break

                    if file_name and line_number:
                        address_map[low_pc] = (func_name.decode(), file_name, line_number)

                except KeyError:
                    continue
    return address_map

def create_map(functions, address_map):
    function_map = {}
    for func in functions:
        if func.address in address_map:
            name, file, line = address_map[func.address]
            function_map[func.address] = (name, file, line)
    return function_map

def parse_args():
    parser = argparse.ArgumentParser(description='Parse ELF files')
    parser.add_argument('elf', type=str, help='ELF file to parse')
    parser.add_argument('-o', '--output', type=str, help='Output file')
    return parser.parse_args()

def extract_callees(binary_path, function_name):
    binary = lief.parse(binary_path)
    ELF = ELFFile(open(binary_path, 'rb'))
    if not ELF.has_dwarf_info():
        print("No DWARF info found")
    dwarf_info = ELF.get_dwarf_info()
    address_map = create_func_address_map(dwarf_info)
    # Specify the function name you are looking for
    
    function_map = {func.address:func for func in binary.functions}
    function_address = binary.get_function_address(function_name)
    if function_address not in function_map:
        return {}
    function = function_map[function_address]
    match binary.header.machine_type:
        case lief.ELF.ARCH.x86_64:
            arch = capstone.CS_ARCH_X86
        case lief.ELF.ARCH.i386:
            arch = capstone.CS_ARCH_X86
        case _:
            raise Exception("Unsupported architecture")
    mode = capstone.CS_MODE_64 if arch == lief.ELF.ARCH.x86_64 else capstone.CS_MODE_32

    md = capstone.Cs(arch, mode)
    # Extract the bytes of the function
    section = binary.section_from_virtual_address(function_address)
    if section is None:
        raise ValueError(f"Section containing address {function_address} not found.")

    # Calculate the offset within the section
    offset = function_address - section.virtual_address
    function_bytes = section.content[offset:offset + function.size]

    callees = []
    # disassemble the function
    for instruction in md.disasm(function_bytes, function.address):
        # print(f"{instruction.mnemonic} {instruction.op_str}")
        if instruction.mnemonic.startswith('call'):
            # print(f"Call to {instruction.op_str}")
            # get the callee address
            callee_address = int(instruction.op_str, 16)
            # get the callee function
            callee = function_map.get(callee_address)
            if callee:
                callees.append(callee)
    result_map = create_map(callees, address_map)
    return result_map

def main():
    args = parse_args()
    binary_path = args.elf
    function_name = "LLVMFuzzerTestOneInput"
    result_map = extract_callees(binary_path, function_name)
    with open(args.output, 'w') as f:
        json.dump(result_map, f)
    

if __name__ == '__main__':
    main()