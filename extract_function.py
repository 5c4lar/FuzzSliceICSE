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
            
def extract(source, function_name, output):
    if not os.path.exists(output):
        os.makedirs(output, exist_ok=True)
    header_output, function_output, remaining_output = os.path.join(output, 'header.h'), os.path.join(output, 'function.c'), os.path.join(output, 'remaining.c')
    file = Path(source)
    tu = parser.parse(file.absolute(), options=cindex.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD)
    header_lines = []
    function_lines = []
    remaining_lines = []
    include_lines = []
    # print(tu.cursor.kind, tu.cursor.spelling, tu.cursor.location.file)
    with open(source, 'r') as f:
        lines = f.readlines()
    for node in tu.cursor.get_children():
        node: cindex.Cursor = node # for type hint
        # print(node.kind, node.spelling, node.location.file)

        if not str(node.location.file).endswith(".c"):
            # if no need to dive into header files
            continue
        
        print(node.kind, node.spelling, node.location.file)
        if node.kind == cindex.CursorKind.INCLUSION_DIRECTIVE:
            include_lines.append(get_node_content(lines, node))
            
        elif node.kind in [cindex.CursorKind.STRUCT_DECL, cindex.CursorKind.UNION_DECL, cindex.CursorKind.ENUM_DECL, cindex.CursorKind.TYPEDEF_DECL, cindex.CursorKind.VAR_DECL]:
            include_lines.append(get_node_content(lines, node))

        elif node.kind == cindex.CursorKind.FUNCTION_DECL:
            
            
            current_function = get_node_content(lines, node)
            if node.storage_class == cindex.StorageClass.STATIC:
                # find the first occurrence of 'static' and remove it
                current_function = re.sub(r'static ', '', current_function)
            if node.spelling == function_name:
                function_lines.append(current_function)
            else:
                remaining_lines.append(current_function)
            signature = get_signature(node)
            header_lines.append(f"extern {signature};\n")
        else:
            include_lines.append(get_node_content(lines, node))

    # Add the includes to the header file
    header_lines = include_lines + header_lines

    # Add the include for the header file to the function and remaining files
    function_lines = [f'#include "{header_output}"\n'] + function_lines
    remaining_lines = [f'#include "{header_output}"\n'] + remaining_lines

    with open(header_output, 'w') as f:
        f.writelines(header_lines)

    with open(function_output, 'w') as f:
        f.writelines(function_lines)

    with open(remaining_output, 'w') as f:
        f.writelines(remaining_lines)
    return header_output, function_output, remaining_output
        
def main():
    args = parse_args()
    extract(args.source, args.function, args.output)
    
if __name__ == '__main__':
    main()
    