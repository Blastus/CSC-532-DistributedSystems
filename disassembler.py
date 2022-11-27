#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""Provide a way to convert code objects back into assembly.

This module contains a class that can process code instances and return
valid source code for the given assembly dialect. Multiple code objects
may be converted into the same dialect using one disassembler instance."""

import datetime

import assembler
import compiler
from assembler_languages import WSA_V1, WSA_V2, WSA_PY, WSA_ES, WSA_X86

# Public Names
__all__ = (
    'main',
    'Disassembler'
)

# Module Documentation
__version__ = 2, 0, 1
__date__ = datetime.date(2022, 11, 26)
__author__ = 'Stephen Paul Chappell'
__credits__ = 'CSC-532'


def main():
    canonical_code = compiler.Code((
        (1, None),  (2, None), (3, None),  (4, None),  (5, None),  (6, None),
        (7, None),  (8, None), (9, None),  (10, None), (11, None), (12, 'A'),
        (13, None), (14, 'B'), (15, None), (16, 'C'),  (17, 'D'),  (18, 'E'),
        (19, 0),    (20, 1),   (21, None), (22, None), (23, None), (24, -2)))
    # noinspection SpellCheckingInspection
    case = {'''\
     get
     set
     iint
     ichr
     oint
     ochr
     mod
     div
     sub
     mul
     add
     less "A"
     back
     zero "B"
     exit
     call "C"
     goto "D"
part "E"
     away 0
     copy 1
     swap
     away
     copy
     push -2''': WSA_V1, '''\
    retrieve
    store
    read_number
    read_character
    output_number
    output_character
    modulo
    integer_division
    subtraction
    multiplication
    addition
    jump_if_negative A
    end_subroutine
    jump_if_zero B
    end_program
    call_subroutine C
    jump_always D
E:
    slide 0
    copy 1
    swap
    discard
    duplicate
    push -2''': WSA_V2, '''\
    LOAD_GLOBAL
    STORE_GLOBAL
    CALL_FUNCTION sys.read_int
    CALL_FUNCTION sys.read_chr
    CALL_FUNCTION sys.write_int
    CALL_FUNCTION sys.write_chr
    INPLACE_MODULO
    INPLACE_FLOOR_DIVIDE
    INPLACE_SUBTRACT
    INPLACE_MULTIPLY
    INPLACE_ADD
    POP_JUMP_IF_NEGATIVE A
    RETURN_VALUE
    POP_JUMP_IF_ZERO B
    CALL_FUNCTION sys.exit
    CALL_FUNCTION C
    JUMP_ABSOLUTE D
>>  E
    POP_TOS 0
    DUP_TOS 1
    ROT_TWO
    POP_TOP
    DUP_TOP
    LOAD_CONST -2''': WSA_PY, '''\
    cobrar
    almacenar
    leer_numero
    leer_caracter
    imprimir_numero
    imprimir_caracter
    modulo
    division_entera
    sustraccion
    multiplicacion
    adicion
    saltar_si_negativo A
    terminar_subrutina
    saltar_si_cero B
    terminar_programa
    llamar_subrutina C
    saltar_siempre D
E:
    resbalar 0
    copiar 1
    intercambiar
    desechar
    duplicar
    fomentar -2''': WSA_ES, '''\
    pop ax push [ax]
    pop ax pop bx mov [bx], ax
    call .read_int
    mov ah, 0 int 22 pop bx mov [bx], al
    call .write_int
    pop al mov ah, 14 int 16
    pop bx pop ax idiv bx push dx
    pop bx pop ax idiv bx push ax
    pop bx pop ax sub ax, bx push ax
    pop bx pop ax imul bx push ax
    pop bx pop ax add ax, bx push ax
    pop ax cmp ax, 0 jl A
    ret
    pop ax cmp ax, 0 je B
    hlt
    call C
    jmp D
E:
    pop ax add sp, 0 * 2 push ax
    push [ss:sp+1*2]
    pop ax pop bx push ax push bx
    sub sp, 2
    push [ss:sp]
    push -2''': WSA_X86}
    for source, description in case.items():
        test_disassembler = Disassembler(description)
        tokens = test_disassembler.disassemble(canonical_code)
        if '\n'.join(tokens) != source:
            raise ValueError('Disassembler did not produce valid assembly!')


class Disassembler:
    """Disassembler(description) -> Disassembler instance"""

    TABLE = tuple(key for value, key in sorted(
        (value, key) for key, value in assembler.Assembler.OP.items()))

    def __init__(self, description):
        """Initialize the Disassembler with assembly instructions."""
        self.__lines = tuple(description[op] for op in self.TABLE)

    def disassemble(self, code):
        """Create a stream of assembly instructions from the given dialect."""
        for op, arg in code:
            op -= 1  # Correct for enumerations beginning with 1.
            arg_type = compiler.INS[op].argument
            line = self.__lines[op]
            if arg_type is compiler.Arg.NUMBER:
                yield line.format(number=arg)
            elif arg_type is compiler.Arg.LABEL:
                yield line.format(label=arg)
            else:
                yield line


if __name__ == '__main__':
    main()
