#!/usr/bin/env python3

import sys
import datetime
import argparse
import xml.etree.ElementTree as ET


def parse_args():
    """Construct input argument list and parse it"""
    parser = argparse.ArgumentParser(
            description='Parse Vivado project file and convert it file format used by other tool',
            epilog="Example:\n\
                    %(prog)s --no-verilog -no-sv --type toml --fileset sources_4 input.xpr vhdl_ls.toml")
    parser.add_argument('--no-vhdl', action='store_true')
    parser.add_argument('--no-verilog', action='store_true')
    parser.add_argument('--no-sv', action='store_true')
    parser.add_argument('--fileset', action='store', default='sources_1',
            help='Active project fileset to parse. Default: sources_1')
    parser.add_argument('--type', choices=('toml', 'hdlcc'), help='Type of the output file')
    parser.add_argument('input_xpr')
    parser.add_argument('output_file', nargs='?', type=argparse.FileType('w'),
            default=sys.stdout)

    args = parser.parse_args()

    return args


def parse_xpr(xml_tree, filetypes, fileset_name='sources_1'):
    """Parse Vivado XPR project file and return list of HDL files

    xml_tree - Root tree object as returned by xml.etree module
    filetype - list of file extensions that are accepted
    fileset_name - name of target Fileset in Vivado project (default sources_1)
    """
    fset = xml_tree.find("FileSets/FileSet[@Name='{}']".format(fileset_name))
    file_list = []

    for child in fset:
        if child.tag == 'File':
            path = child.get('Path')
            ext = path.split('.')[-1].lower()
            if ext in filetypes:
                file = {'path': child.get('Path').replace('$PPRDIR/', '')}
                file_lib = child.find("./FileInfo/Attr[@Name='Library']")
                if file_lib is not None:
                    file['lib'] = file_lib.get('Val')
                else:
                    file['lib'] = "work"
                file_list.append(file)

    return file_list


def fileview2libview(file_list):
    """Convert list of files to list of libraries (with files in a lib)

    file_list - list of files (with library information)
    """
    # list of library dictionaries
    # each lib dict has following form {'name' : str, 'files' : list(files)}
    lib_list = []
    for file in file_list:
        # if library exists add file, otherwise create library first
        lib_dict = next((item for item in lib_list if item['name'] == file['lib']), False)
        if lib_dict:
            lib_dict['files'].append(file['path'])
        else:
            new_lib = {'name': file['lib'], 'files': [file['path']]}
            lib_list.append(new_lib)

    return lib_list


def write_header(fstream):
    fstream.write('###############################################################\n')
    fstream.write('# This file was automatically generated from Vivado XPR project file\n')
    fstream.write('# Creation date: {:%Y/%m/%d %H:%M}\n'.format(datetime.datetime.now()))
    fstream.write('###############################################################\n')
    fstream.write('\n')


def write_toml(lib_list, fstream):
    """Write a vhdl_ls.toml file

    lib_list - library list, each library should be a dictionary with
                a list of associated files
    fstream - opened file handle
    """
    write_header(fstream)
    fstream.write('[libraries]\n')
    for lib in lib_list:
        fstream.write(lib['name'] + ".files = [\n")
        for path in lib['files'][:-1]:
            fstream.write("'{}',\n".format(path))
        fstream.write("'{}'\n".format(lib['files'][-1]))
        fstream.write(']\n\n')


def write_hdlcc(files, fstream):
    """Write a vhdl_ls.toml file

    files - list of files (+ additional info in dict)
    fstream - opened file handle
    """
    write_header(fstream)
    for f in files:
        ext = f['path'].split('.')[-1].lower()
        if ext in ('vhd', 'vhdl'):
            ftype = 'vhdl'
        elif ext in ('v',):
            ftype = 'verilog'
        elif ext in ('sv',):
            ftype = 'systemverilog'
        else:
            continue
        fstream.write(' '.join((ftype, f['lib'], f['path'])))
        fstream.write('\n')


def main():
    args = parse_args()
    tree = ET.parse(args.input_xpr)

    filetypes = []
    if not args.no_vhdl:
        filetypes.extend(('vhd', 'vhdl'))
    if not args.no_verilog:
        filetypes.append('v')
    if not args.no_sv:
        filetypes.append('sv')

    file_list = parse_xpr(tree, filetypes, args.fileset)
    lib_list = fileview2libview(file_list)
    if args.type == 'toml':
        write_toml(lib_list, args.output_file)
    elif args.type == 'hdlcc':
        write_hdlcc(file_list, args.output_file)


if __name__ == '__main__':
    main()
