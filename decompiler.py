#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""Provide the ability to convert code objects into WS source.

This module supplies the Decompiler class that helps when transforming
code objects back into a trinary stream. When the original source code
is needed, the decompile method maps the trinary stream to characters."""

import datetime

import compiler

# Public Names
__all__ = (
    'main',
    'Decompiler'
)

# Module Documentation
__version__ = 2, 0, 1
__date__ = datetime.date(2022, 11, 26)
__author__ = 'Stephen Paul Chappell'
__credits__ = 'CSC-532'


def main():
    source = ''.join(('\t\t\t',
                      '\t\t ',
                      '\t\n\t\t',
                      '\t\n\t ',
                      '\t\n \t',
                      '\t\n  ',
                      '\t \t\t',
                      '\t \t ',
                      '\t  \t',
                      '\t  \n',
                      '\t   ',
                      '\n\t\t', '\n',
                      '\n\t\n',
                      '\n\t ', ' \n',
                      '\n\n\n',
                      '\n \t', '\t\n',
                      '\n \n', '  \n',
                      '\n  ', ' \t\n',
                      ' \t\n', '\n',
                      ' \t ', ' \t\n',
                      ' \n\t',
                      ' \n\n',
                      ' \n ',
                      '  ', '\t\t \n'))
    code = compiler.Compiler(compiler.Prototype.SYMBOLS).compile(source)
    output = Decompiler(code).decompile()
    if output != source:
        raise ValueError('Code was not decompiled correctly!')


class Decompiler:
    """Decompiler(code) -> Decompiler instance"""

    HC, TC, HB, TB = (compiler.Compiler.HEAD_CHAR, compiler.Compiler.TAIL_CHAR,
                      compiler.Compiler.HEAD_BASE, compiler.Compiler.TAIL_BASE)

    def __init__(self, code):
        """Initialize the Decompiler instance with code to decompile."""
        self.__code = code

    def __iter__(self):
        """Iterate over the code and yield back equivalent trinary."""
        for code, argument in self.__code:
            p_pattern, p_argument, p_code = compiler.INS[code - 1]
            if p_code != code:
                raise LookupError('Prototype was incorrectly retrieved!')
            yield from p_pattern
            if p_argument == compiler.Arg.LABEL:
                yield from self.__number_to_name_bits(
                    self.__name_to_number(argument))
            elif p_argument == compiler.Arg.NUMBER:
                yield from self.__number_to_binary_bits(argument)
            # If there is an argument, close its value with a 1.
            if p_argument != compiler.Arg.NULL:
                yield 1

    def decompile(self):
        """Transform the code into an equivalent WS source string."""
        symbols = compiler.Prototype.SYMBOLS.args[0]
        return ''.join(map(symbols.__getitem__, self))

    @classmethod
    def __name_to_number(cls, name):
        """Convert a valid identifier into a number."""
        if not name.isidentifier():
            raise ValueError('Name must be a Python identifier!')
        head, *tail = name
        number = cls.HC.index(head)
        for character in tail:
            number = number * cls.TB + cls.TC.index(character)
        return number + sum(cls.HB * cls.TB ** p for p in range(len(tail)))

    @classmethod
    def __number_to_name_bits(cls, number):
        """Convert a number into a name bit string."""
        size, bits = (number + 1).bit_length() - 1, []
        number += 1 - (1 << size)
        for _ in range(size):
            number, bit = divmod(number, 2)
            bits.append(cls.__binary_to_trinary(bit))
        return reversed(bits)

    @classmethod
    def __number_to_binary_bits(cls, number):
        """Convert a number into a binary bit string."""
        if number:
            yield cls.__binary_to_trinary(number < 0)
            number, bits = abs(number), []
            while number:
                number, bit = divmod(number, 2)
                bits.append(cls.__binary_to_trinary(bit))
            yield from reversed(bits)

    @staticmethod
    def __binary_to_trinary(bit):
        """Translate boolean values to trinary digits."""
        return 0 if bit else 2


if __name__ == '__main__':
    main()
