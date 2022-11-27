#! /usr/bin/env python3
"""Provide a tool for converting assembly into machine code.

This module has a simple definition for WS assembly, several utility
functions, and a class that can assemble source into code objects. A
test verifies that the assembler operates properly by specification."""

__author__ = 'Stephen "Zero" Chappell <Noctis.Skytower@gmail.com>'
__date__ = '25 October 2013'
__version__ = 2, 0, 0

################################################################################

# These modules are used in some of the source down below.

import itertools
import re
import compiler

################################################################################

# This is a description of an original assembly language for WS.

WSA_V1 = dict(retrieve =         '     get',
              store =            '     set',
              read_number =      '     iint',
              read_character =   '     ichr',
              output_number =    '     oint',
              output_character = '     ochr',
              modulo =           '     mod',
              integer_division = '     div',
              subtraction =      '     sub',
              multiplication =   '     mul',
              addition =         '     add',
              jump_if_negative = '     less "{label}"',
              end_subroutine =   '     back',
              jump_if_zero =     '     zero "{label}"',
              end_program =      '     exit',
              call_subroutine =  '     call "{label}"',
              jump_always =      '     goto "{label}"',
              mark_location =    'part "{label}"',
              slide =            '     away {number}',
              copy =             '     copy {number}',
              swap =             '     swap',
              discard =          '     away',
              duplicate =        '     copy',
              push =             '     push {number}',
              number =           '[+-]?\d+',
              label =            '\w+',
              comment =          '#.*',
              empty =            '')

################################################################################

# The following utility functions help when working with enumerations.

starfilter = lambda function, iterable: \
    (args for args in iterable if function(*args))

enum_items = lambda enum: \
    starfilter(lambda k, v: isinstance(v, int), vars(type(enum)).items())

enum_normal = lambda enum: \
    ((k.lower(), v) for k, v in sorted(enum_items(enum), key=lambda p: p[1]))

################################################################################

# Assemblers can make code objects from assembly in specified languages.

class Assembler:

    "Assembler(description) -> Assembler instance"

    GROUP = '(?P<{}>{})'
    LINES = re.compile('\r\n|\r|\n', re.ASCII).split
    OP = dict(enum_normal(compiler.OP))

    def __init__(self, description):
        "Initialize the Assembler with a compiled language description."
        language, alias, group = description.copy(), {}, []
        argument = tuple((language.pop(key, None), key)
                         for key, value in enum_normal(compiler.ARG))
        for key, value in enum_normal(compiler.OP):
            expression = language.pop(key)
            sub_expression, name = argument[compiler.INS[value].argument]
            if sub_expression is not None:
                sub_key = '{}_{}'.format(key, name.upper())
                expression = expression.format(
                    **{name: self.GROUP.format(sub_key, sub_expression)})
                alias[sub_key] = name
            group.append(self.GROUP.format(key, expression))
        group.extend(itertools.starmap(self.GROUP.format, language.items()))
        self.__match, self.__alias = (
            re.compile('^({})$'.format('|'.join(group)), re.ASCII).search,
            lambda name: alias.get(name, name))

    def tokenize(self, assembly):
        "Separate the assembly into its individual token items."
        for line, text in enumerate(self.LINES(assembly), 1):
            token = self.__match(text)
            if token is None:
                raise SyntaxError('Line {!s}: {!r}'.format(line, text))
            yield {self.__alias(key): value for key, value in
                   token.groupdict().items() if value is not None}

    def assemble(self, assembly):
        "Create a coded instruction stream from the assembly."
        for token in self.tokenize(assembly):
            number = token.pop('number', None)
            label = token.pop('label', None)
            key, value = token.popitem()
            if token:
                raise ValueError('Token should be empty!')
            if key in self.OP:
                pattern, argument, code = compiler.INS[self.OP[key]]
                if argument == compiler.ARG.NUMBER:
                    yield code, int(number)
                elif argument == compiler.ARG.LABEL:
                    yield code, label
                else:
                    yield code, None

    def make_code(self, assembly):
        "Generate a code object that is suitable for a processor."
        return compiler.Code(self.assemble(assembly))

################################################################################

def test():
    code = compiler.Code((
        (0, None),  (1, None), (2, None),  (3, None),  (4, None),  (5, None),
        (6, None),  (7, None), (8, None),  (9, None),  (10, None), (11, 'A'),
        (12, None), (13, 'B'), (14, None), (15, 'C'),  (16, 'D'),  (17, 'E'),
        (18, 0),    (19, 1),   (20, None), (21, None), (22, None), (23, -2)))
    source = '''
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
     push -2
# This is a comment.'''
    if Assembler(WSA_V1).make_code(source) != code:
        raise ValueError('Assembler did not produce valid code!')

################################################################################

if __name__ == '__main__':
    test()
