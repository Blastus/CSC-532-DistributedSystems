#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""Provide a tool for converting assembly into machine code.

This module has a simple definition for WS assembly, several utility
functions, and a class that can assemble source into code objects. A
test verifies that the assembler operates properly by specification."""

import datetime
import itertools
import re

import compiler
from assembler_languages import WSA_V1

# Public Names
__all__ = (
    'main',
    'star_filter',
    'enum_items',
    'enum_normal',
    'Assembler'
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
    test_assembler = Assembler(WSA_V1)
    test_code = test_assembler.make_code(source)
    if test_code != canonical_code:
        raise ValueError('Assembler did not produce valid code!')


def star_filter(function, iterable):
    """Filter iterable by passing all values to test function."""
    return (args for args in iterable if function(*args))


def enum_items(enum):
    """Get values from an enumeration if they are integers."""
    return star_filter(
        lambda k, v: isinstance(v, int),
        enum.__members__.items()
    )


def enum_normal(enum):
    """Normalize the values being retrieved from an enumeration."""
    return (
        (k.lower(), v)
        for k, v in sorted(enum_items(enum), key=lambda p: p[1])
    )


class Assembler:
    """Assembler(description) -> Assembler instance

    Assemblers can make code objects from assembly in specified languages."""

    GROUP = '(?P<{}>{})'
    LINES = re.compile('\r\n|\r|\n', re.ASCII).split
    OP = dict(enum_normal(compiler.Op))

    def __init__(self, description):
        """Initialize the Assembler with a compiled language description."""
        language, alias, group = description.copy(), {}, []
        argument = tuple((language.pop(key, None), key)
                         for key, value in enum_normal(compiler.Arg))
        for key, value in enum_normal(compiler.Op):
            expression = language.pop(key)
            instruction = compiler.INS[value - 1]
            sub_expression, name = argument[instruction.argument - 1]
            if sub_expression is not None:
                sub_key = f'{key}_{name.upper()}'
                filler = {name: self.GROUP.format(sub_key, sub_expression)}
                expression = expression.format(**filler)
                alias[sub_key] = name
            group.append(self.GROUP.format(key, expression))
        group.extend(itertools.starmap(self.GROUP.format, language.items()))
        self.__match = re.compile(f'({"|".join(group)})$', re.ASCII).search
        self.__alias = lambda identifier: alias.get(identifier, identifier)

    def tokenize(self, assembly):
        """Separate the assembly into its individual token items."""
        for line, text in enumerate(self.LINES(assembly), 1):
            token = self.__match(text)
            if token is None:
                raise SyntaxError(f'Line {line!s}: {text!r}')
            yield {self.__alias(key): value for key, value in
                   token.groupdict().items() if value is not None}

    def assemble(self, assembly):
        """Create a coded instruction stream from the assembly."""
        for token in self.tokenize(assembly):
            number = token.pop('number', None)
            label = token.pop('label', None)
            key, value = token.popitem()
            if token:
                raise ValueError('Token should be empty!')
            if key in self.OP:
                pattern, argument, code = compiler.INS[self.OP[key] - 1]
                if argument is compiler.Arg.NUMBER:
                    yield code, int(number)
                elif argument is compiler.Arg.LABEL:
                    yield code, label
                else:
                    yield code, None

    def make_code(self, assembly):
        """Generate a code object that is suitable for a processor."""
        return compiler.Code(self.assemble(assembly))


if __name__ == '__main__':
    main()
