#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""Automatically compile all assembly files in WS program files.

This program is designed to automatically search a directory for assembly
files, determine if they need to be compiled into WS files, and create an
actual WS file when needed based on the modification times for the files."""

import datetime
import pathlib
import sys

import assembler
import assembler_languages
import decompiler

# Public Names
__all__ = (
    'main',
    'get_program_directory',
    'needs_compilation'
)

# Module Documentation
__version__ = 1, 0, 0
__date__ = datetime.date(2022, 11, 26)
__author__ = 'Stephen Paul Chappell'
__credits__ = 'CSC-532'


def main():
    """Looks for assembly files that need to be compiled and does so."""
    program_directory = get_program_directory()
    my_assembler = assembler.Assembler(assembler_languages.WSA_V1)
    for source in program_directory.glob('*.wsa'):
        destination = source.with_suffix('.ws')
        if needs_compilation(destination, source):
            # Create the code object.
            with source.open('r') as file:
                assembly_code = file.read()
            code_object = my_assembler.make_code(assembly_code)
            # Decompile the code into a real WS file.
            my_decompiler = decompiler.Decompiler(code_object)
            ws_code = my_decompiler.decompile()
            with destination.open('w') as file:
                file.write(''.join(ws_code))


def get_program_directory(default='vm_programs'):
    """Calculates the location of the program directory."""
    root = pathlib.Path(sys.argv[0]).parent
    program_directory = root / default
    if not program_directory.is_dir():
        raise RuntimeError(f'{program_directory} should be a directory')
    return program_directory


def needs_compilation(destination, source):
    """Determines if source needs to be compiled based on destination."""
    if not destination.exists():
        return True
    if not destination.is_file():
        raise RuntimeError(f'{destination} should be a file')
    source_mtime = source.stat().st_mtime
    destination_mtime = destination.stat().st_mtime
    return source_mtime > destination_mtime


if __name__ == '__main__':
    main()
