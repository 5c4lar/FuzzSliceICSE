import argparse
import clang.cindex as cindex
import json
from pathlib import Path
from copy import deepcopy
import re
import os
# cindex.Config.library_path = '/usr/lib'

parser = cindex.Index.create()

def parse_args():
    parser = argparse.ArgumentParser(description='Extract function from a C file')
    parser.add_argument('--source', type=str, help='Path to the C file')
    parser.add_argument('--function', type=str, help='Name of the function to extract')
    parser.add_argument('--output', type=str, help='Path to the output file')
    return parser.parse_args()

def get_node_content(lines, node):
    # get the content of the node as a string, considering the line number and column number
    content = ''
    if node.extent.start.line == node.extent.end.line:
        content = lines[node.extent.start.line-1][node.extent.start.column-1:node.extent.end.column]
    else:
        content = lines[node.extent.start.line-1][node.extent.start.column-1:]
        for i in range(node.extent.start.line, node.extent.end.line-1):
            content += lines[i]
        content += lines[node.extent.end.line-1][:node.extent.end.column]
    return content + "\n"

def get_signature(node):
    assert node.kind == cindex.CursorKind.FUNCTION_DECL
    # get the signature by find the first occurrence of '{'
    with open(node.extent.start.file.name, 'r') as f:
        lines = f.readlines()
    signature = ''
    content = get_node_content(lines, node)
    if '{' in content:
        signature = content[:content.index('{')].strip()
    else:
        signature = content.strip()
    if node.storage_class == cindex.StorageClass.STATIC:
        # find the first occurrence of 'static' and remove it with regex
        signature = re.sub(r'static ', '', signature)
        
    return signature

def merge_extents(extents, lines):
    # print(extents)
    # converting list of extents to non-overlapping extents
    lines_to_offset = {}
    current_offset = 0
    for i, line in enumerate(lines):
        lines_to_offset[i+1] = current_offset
        current_offset += len(line)
    extent_ranges = []
    for extent in extents:
        extent_start_offset = lines_to_offset[extent.start.line] + extent.start.column - 1
        extent_end_offset = lines_to_offset[extent.end.line] + extent.end.column
        extent_ranges.append((extent_start_offset, extent_end_offset))
    extent_ranges.sort(key=lambda x: x[0])
    merged_extents = []
    for extent_range in extent_ranges:
        if not merged_extents:
            merged_extents.append(extent_range)
        else:
            last_extent = merged_extents[-1]
            if extent_range[0] > last_extent[1]:
                merged_extents.append(extent_range)
            else:
                merged_extents[-1] = (last_extent[0], max(last_extent[1], extent_range[1]))
    content = "".join(lines)
    merged_result = ";\n".join([content[start:end] if not content[start:end].startswith('static') else re.sub(r'static ', '', content[start:end]) for start, end in merged_extents])
    # print(merged_extents)
    return merged_extents, merged_result
    
def extract(source, function_name, output):
    if not os.path.exists(output):
        os.makedirs(output, exist_ok=True)
    header_output, function_output, remaining_output = os.path.join(output, 'header.h'), os.path.join(output, 'function.c'), os.path.join(output, 'remaining.c')
    file = Path(source)
    tu = parser.parse(file.absolute(), options=cindex.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD)
    header_lines = []
    function_extents = []
    remaining_extents = []
    include_extents = []
    # print(tu.cursor.kind, tu.cursor.spelling, tu.cursor.location.file)
    with open(source, 'r') as f:
        lines = f.readlines()
    for node in tu.cursor.get_children():
        node: cindex.Cursor = node # for type hint
        # print(node.kind, node.spelling, node.location.file)

        if not str(node.location.file).endswith(".c"):
            # if no need to dive into header files
            continue
        
        # print(node.kind, node.spelling, node.location.file, node.is_definition(), node.kind.is_statement(), node.extent)
        if node.kind == cindex.CursorKind.INCLUSION_DIRECTIVE:
            include_extents.append(node.extent)
            
        elif node.kind in [cindex.CursorKind.STRUCT_DECL, cindex.CursorKind.UNION_DECL, cindex.CursorKind.ENUM_DECL, cindex.CursorKind.TYPEDEF_DECL, cindex.CursorKind.VAR_DECL]:
            include_extents.append(node.extent)

        elif node.kind == cindex.CursorKind.FUNCTION_DECL:
            if node.is_definition():
                current_function = get_node_content(lines, node)
                if node.storage_class == cindex.StorageClass.STATIC:
                    # find the first occurrence of 'static' and remove it
                    current_function = re.sub(r'static ', '', current_function)
                if node.spelling == function_name:
                    function_extents.append(node.extent)
                else:
                    if node.spelling == "LLVMFuzzerTestOneInput" or node.spelling == "main":
                        continue
                    remaining_extents.append(node.extent)
                signature = get_signature(node)
                if not signature.startswith("extern"):
                    signature = f"extern {signature}"
                header_lines.append(f"{signature};\n")
            else:
                include_extents.append(node.extent)
        else:
            include_extents.append(node.extent)
            
    with open(header_output, 'w') as f:
        f.write(merge_extents(include_extents, lines)[1] + "\n" + "".join(header_lines))

    with open(function_output, 'w') as f:
        f.write(f'#include "header.h"\n' + merge_extents(function_extents, lines)[1])

    with open(remaining_output, 'w') as f:
        f.write(f'#include "header.h"\n' + merge_extents(remaining_extents, lines)[1])
    return header_output, function_output, remaining_output
        
def main():
    args = parse_args()
    extract(args.source, args.function, args.output)
    
if __name__ == '__main__':
    main()
    