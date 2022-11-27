#! /usr/bin/env python3
"""Provide a way to convert code objects back into assembly.

This module contains a class that can process code instances and return
valid source code for the given assembly dialect. Multiple code objects
may be converted into the same dialect using one disassembler instance."""

__author__ = 'Stephen "Zero" Chappell <Noctis.Skytower@gmail.com>'
__date__ = '2 January 2014'
__version__ = 2, 0, 0

################################################################################

import assembler
import compiler

################################################################################

# Whitespace
WSA_V2 = dict(retrieve         = '    retrieve',
              store            = '    store',
              read_number      = '    read_number',
              read_character   = '    read_character',
              output_number    = '    output_number',
              output_character = '    output_character',
              modulo           = '    modulo',
              integer_division = '    integer_division',
              subtraction      = '    subtraction',
              multiplication   = '    multiplication',
              addition         = '    addition',
              jump_if_negative = '    jump_if_negative {label}',
              end_subroutine   = '    end_subroutine',
              jump_if_zero     = '    jump_if_zero {label}',
              end_program      = '    end_program',
              call_subroutine  = '    call_subroutine {label}',
              jump_always      = '    jump_always {label}',
              mark_location    = '{label}:',
              slide            = '    slide {number}',
              copy             = '    copy {number}',
              swap             = '    swap',
              discard          = '    discard',
              duplicate        = '    duplicate',
              push             = '    push {number}',
              number           = '0|[+-]?[1-9]\d*',
              label            = '[A-Z_a-z]\w*',
              comment          = '( {4})*#(\s.*\S)?',
              empty            = '')

# Python
WSA_PY = dict(retrieve         = '    LOAD_GLOBAL',
              store            = '    STORE_GLOBAL',
              read_number      = '    CALL_FUNCTION sys.read_int',
              read_character   = '    CALL_FUNCTION sys.read_chr',
              output_number    = '    CALL_FUNCTION sys.write_int',
              output_character = '    CALL_FUNCTION sys.write_chr',
              modulo           = '    INPLACE_MODULO',
              integer_division = '    INPLACE_FLOOR_DIVIDE',
              subtraction      = '    INPLACE_SUBTRACT',
              multiplication   = '    INPLACE_MULTIPLY',
              addition         = '    INPLACE_ADD',
              jump_if_negative = '    POP_JUMP_IF_NEGATIVE {label}',
              end_subroutine   = '    RETURN_VALUE',
              jump_if_zero     = '    POP_JUMP_IF_ZERO {label}',
              end_program      = '    CALL_FUNCTION sys.exit',
              call_subroutine  = '    CALL_FUNCTION {label}',
              jump_always      = '    JUMP_ABSOLUTE {label}',
              mark_location    = '>>  {label}',
              slide            = '    POP_TOS {number}',
              copy             = '    DUP_TOS {number}',
              swap             = '    ROT_TWO',
              discard          = '    POP_TOP',
              duplicate        = '    DUP_TOP',
              push             = '    LOAD_CONST {number}',
              number           = '[+-]?([1-9]\d*|0+)',
              label            = '[a-zA-Z_]\w*',
              comment          = '\s*#.*',
              empty            = '')

# Spanish
WSA_ES = dict(retrieve         = '    cobrar',
              store            = '    almacenar',
              read_number      = '    leer_numero',
              read_character   = '    leer_caracter',
              output_number    = '    imprimir_numero',
              output_character = '    imprimir_caracter',
              modulo           = '    modulo',
              integer_division = '    division_entera',
              subtraction      = '    sustraccion',
              multiplication   = '    multiplicacion',
              addition         = '    adicion',
              jump_if_negative = '    saltar_si_negativo {label}',
              end_subroutine   = '    terminar_subrutina',
              jump_if_zero     = '    saltar_si_cero {label}',
              end_program      = '    terminar_programa',
              call_subroutine  = '    llamar_subrutina {label}',
              jump_always      = '    saltar_siempre {label}',
              mark_location    = '{label}:',
              slide            = '    resbalar {number}',
              copy             = '    copiar {number}',
              swap             = '    intercambiar',
              discard          = '    desechar',
              duplicate        = '    duplicar',
              push             = '    fomentar {number}',
              number           = '0|[+-]?[1-9]\d*',
              label            = '[A-Z_a-z]\w*',
              comment          = '( {4})*#(\s.*\S)?',
              empty            = '')

# x86
WSA_X86 = dict(retrieve         = '    pop ax push [ax]',
               store            = '    pop ax pop bx mov [bx], ax',
               read_number      = '    call .read_int',
               read_character   = '    mov ah, 0 int 22 pop bx mov [bx], al',
               output_number    = '    call .write_int',
               output_character = '    pop al mov ah, 14 int 16',
               modulo           = '    pop bx pop ax idiv bx push dx',
               integer_division = '    pop bx pop ax idiv bx push ax',
               subtraction      = '    pop bx pop ax sub ax, bx push ax',
               multiplication   = '    pop bx pop ax imul bx push ax',
               addition         = '    pop bx pop ax add ax, bx push ax',
               jump_if_negative = '    pop ax cmp ax, 0 jl {label}',
               end_subroutine   = '    ret',
               jump_if_zero     = '    pop ax cmp ax, 0 je {label}',
               end_program      = '    hlt',
               call_subroutine  = '    call {label}',
               jump_always      = '    jmp {label}',
               mark_location    = '{label}:',
               slide            = '    pop ax add sp, {number} * 2 push ax',
               copy             = '    push [ss:sp+{number}*2]',
               swap             = '    pop ax pop bx push ax push bx',
               discard          = '    sub sp, 2',
               duplicate        = '    push [ss:sp]',
               push             = '    push {number}',
               number           = '0|[+-]?[1-9]\d*',
               label            = '[A-Z_a-z]\w*',
               comment          = '\s*;.*',
               empty            = '')

################################################################################

class Disassembler:

    "Disassembler(description) -> Disassembler instance"

    TABLE = tuple(key for value, key in sorted(
        (value, key) for key, value in assembler.Assembler.OP.items()))

    def __init__(self, description):
        "Initialize the Disassembler with assembly instructions."
        self.__lines = tuple(description[op] for op in self.TABLE)

    def disassemble(self, code):
        "Create a stream of assembly instructions from the given dialect."
        for op, arg in code:
            arg_type, line = compiler.INS[op].argument, self.__lines[op]
            if arg_type == compiler.ARG.NUMBER:
                yield line.format(number=arg)
            elif arg_type == compiler.ARG.LABEL:
                yield line.format(label=arg)
            else:
                yield line

################################################################################

def test():
    code = compiler.Code((
        (0, None),  (1, None), (2, None),  (3, None),  (4, None),  (5, None),
        (6, None),  (7, None), (8, None),  (9, None),  (10, None), (11, 'A'),
        (12, None), (13, 'B'), (14, None), (15, 'C'),  (16, 'D'),  (17, 'E'),
        (18, 0),    (19, 1),   (20, None), (21, None), (22, None), (23, -2)))
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
     push -2''': assembler.WSA_V1, '''\
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
        if '\n'.join(Disassembler(description).disassemble(code)) != source:
            raise ValueError('Disassembler did not producwe valid assembly!')

################################################################################

if __name__ == '__main__':
    test()
