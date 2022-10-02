#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""Provide a way to compile WS into a basic machine representation.

This module contains facilities for compiling WS code into a representation
suitable as a starting point for interpretation. Several tables can be read
to provide further support for understanding the generated code objects."""

import collections
import datetime
import enum
import functools
import string

# Public Names
__all__ = (
    'INSTRUCTION_DOCUMENTATION',
    'main',
    'Tokenizer',
    'auto',
    'Arg',
    'Op',
    'Prototype',
    'INS',
    'Compiler',
    'Code'
)

# Module Documentation
__version__ = 2, 0, 1
__date__ = datetime.date(2022, 10, 2)
__author__ = 'Stephen Paul Chappell'
__credits__ = 'CSC-532'

# Symbolic Constants
INSTRUCTION_DOCUMENTATION = r'''
--------------------------------
'\t\t'  Heap Access
        '\t'    Retrieve
        ' '     Store
--------------------------------
'\t\n'  I/O
        '\t\t'  Read Number
        '\t '   Read Character
        ' \t'   Output Number
        '  '    Output Character
--------------------------------
'\t '   Arithmetic
        '\t\t'  Modulo
        '\t '   Integer Division
        ' \t'   Subtraction
        ' \n'   Multiplication
        '  '    Addition
--------------------------------
'\n'    Flow Control
        '\t\t'  Jump If Negative
        '\t\n'  End Subroutine
        '\t '   Jump If Zero
        '\n\n'  End Program
        ' \t'   Call Subroutine
        ' \n'   Jump Always
        '  '    Mark Location
--------------------------------
' '     Stack Manipulation
        '\t\n'  Slide
        '\t '   Copy
        '\n\t'  Swap
        '\n\n'  Discard
        '\n '   Duplicate
        ' '     Push
--------------------------------
'''


def main():
    """Tests the capabilities of the compiler code for its correctness."""
    source = ('\t\t\t',
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
              ' \t ', ' \n',
              ' \n\t',
              ' \n\n',
              ' \n ',
              '  ', '  \n')
    code = Code(enumerate((None, None, None, None, None, None, None, None,
                           None, None, None, 'A',  None, 'B',  None, 'C',
                           'D',  'E',  0,    0,    None, None, None, 0), 1))
    compiled_code = Compiler(Prototype.SYMBOLS).compile(''.join(source))
    if compiled_code != code:
        raise ValueError('Code was not compiled correctly!')


class Tokenizer(collections.deque):

    """Tokenizer(symbols, source) -> Tokenizer instance

    The tokenizer converts the source into an enumeration of symbols."""

    def __init__(self, symbols, source):
        """Initialize the Tokenizer with a symbol table and source tokens."""
        base = tuple(symbols)
        if len(base) != len(set(base)):
            raise ValueError('All symbols must be unique!')
        self.__base = base
        super().__init__(self(symbol) for symbol in source if symbol in self)

    def __contains__(self, symbol):
        """Check if symbol is recognized by the tokenizer."""
        return symbol in self.__base

    def __call__(self, symbol):
        """Convert symbol into its enumerated form if possible."""
        return self.__base.index(symbol)

    def consume(self, pattern):
        """Try to pop the pattern off the front of the token stream."""
        pattern_len = len(pattern)
        if len(self) < pattern_len:
            return False
        if all(s == p for s, p in zip(self, pattern)):
            for _ in range(pattern_len):
                self.pop()
            return True
        return False

    def pop(self):
        """Pull a token off the front of the token stream."""
        return self.popleft()


def auto():
    """Helps simplify inspections against instantiating the auto class."""
    # noinspection PyArgumentList
    return enum.auto()


class Arg(enum.IntEnum):
    """The ARG table contains argument types."""

    NULL = auto()
    NUMBER = auto()
    LABEL = auto()


class Op(enum.IntEnum):
    """The OP table contains operation codes."""

    RETRIEVE = auto()
    STORE = auto()
    READ_NUMBER = auto()
    READ_CHARACTER = auto()
    OUTPUT_NUMBER = auto()
    OUTPUT_CHARACTER = auto()
    MODULO = auto()
    INTEGER_DIVISION = auto()
    SUBTRACTION = auto()
    MULTIPLICATION = auto()
    ADDITION = auto()
    JUMP_IF_NEGATIVE = auto()
    END_SUBROUTINE = auto()
    JUMP_IF_ZERO = auto()
    END_PROGRAM = auto()
    CALL_SUBROUTINE = auto()
    JUMP_ALWAYS = auto()
    MARK_LOCATION = auto()
    SLIDE = auto()
    COPY = auto()
    SWAP = auto()
    DISCARD = auto()
    DUPLICATE = auto()
    PUSH = auto()


class Prototype(collections.namedtuple('base', 'pattern, argument, code')):

    """Prototype(pattern, argument, code) -> Prototype instance

    Prototypes provide data for decoding individual instructions correctly."""

    SYMBOLS = functools.partial(Tokenizer, '\t\n ')

    def __new__(cls, pattern, argument, code):
        """Check and fix the arguments before creating the Prototype."""
        prototype = tuple(cls.SYMBOLS(pattern))
        if len(pattern) != len(prototype):
            raise ValueError('An unexpected symbol was found!')
        if not isinstance(argument, Arg):
            raise TypeError('An unexpected argument type was given!')
        cls._check(code)
        # noinspection PyArgumentList
        return super().__new__(cls, prototype, argument, code)

    @staticmethod
    def _check(code):
        """Validate that instruction code is in operation table."""
        try:
            Op(code)
        except ValueError:
            raise TypeError('An unexpected operation code was given!')


INS = (Prototype('\t\t\t', Arg.NULL, Op.RETRIEVE),
       Prototype('\t\t ', Arg.NULL, Op.STORE),
       Prototype('\t\n\t\t', Arg.NULL, Op.READ_NUMBER),
       Prototype('\t\n\t ', Arg.NULL, Op.READ_CHARACTER),
       Prototype('\t\n \t', Arg.NULL, Op.OUTPUT_NUMBER),
       Prototype('\t\n  ', Arg.NULL, Op.OUTPUT_CHARACTER),
       Prototype('\t \t\t', Arg.NULL, Op.MODULO),
       Prototype('\t \t ', Arg.NULL, Op.INTEGER_DIVISION),
       Prototype('\t  \t', Arg.NULL, Op.SUBTRACTION),
       Prototype('\t  \n', Arg.NULL, Op.MULTIPLICATION),
       Prototype('\t   ', Arg.NULL, Op.ADDITION),
       Prototype('\n\t\t', Arg.LABEL, Op.JUMP_IF_NEGATIVE),
       Prototype('\n\t\n', Arg.NULL, Op.END_SUBROUTINE),
       Prototype('\n\t ', Arg.LABEL, Op.JUMP_IF_ZERO),
       Prototype('\n\n\n', Arg.NULL, Op.END_PROGRAM),
       Prototype('\n \t', Arg.LABEL, Op.CALL_SUBROUTINE),
       Prototype('\n \n', Arg.LABEL, Op.JUMP_ALWAYS),
       Prototype('\n  ', Arg.LABEL, Op.MARK_LOCATION),
       Prototype(' \t\n', Arg.NUMBER, Op.SLIDE),
       Prototype(' \t ', Arg.NUMBER, Op.COPY),
       Prototype(' \n\t', Arg.NULL, Op.SWAP),
       Prototype(' \n\n', Arg.NULL, Op.DISCARD),
       Prototype(' \n ', Arg.NULL, Op.DUPLICATE),
       Prototype('  ', Arg.NUMBER, Op.PUSH))

assert INS == tuple(sorted(INS, key=lambda ins: ins.pattern)), \
       'Patterns were not in the expected order!'
assert INS == tuple(sorted(INS, key=lambda ins: ins.code)), \
       'Codes were not in the expected order!'


class Compiler:

    """Compiler(tokenizer) -> Compiler instance

    The compiler generates code objects subject to further processing."""

    HEAD_CHAR = ''.join(sorted(string.ascii_letters + '_'))
    TAIL_CHAR = ''.join(sorted(string.digits + HEAD_CHAR))
    HEAD_BASE, TAIL_BASE = len(HEAD_CHAR), len(TAIL_CHAR)

    def __init__(self, tokenizer):
        """Initialize the Compiler with the tokenizer to use on the source."""
        self.__tokenizer = tokenizer
        self.__handlers = {Arg.NULL: lambda: None,
                           Arg.NUMBER: self.__parse_number,
                           Arg.LABEL: self.__parse_label}
        self.__stream = None

    def compile(self, source):
        """Compile the source into a code object to be used elsewhere."""
        self.__stream = self.__tokenizer(source)
        return Code(self.__parse_instructions())

    def __parse_instructions(self):
        """Process the stream and return the relative instruction codes."""
        while self.__stream:
            for pattern, argument, code in INS:
                if self.__stream.consume(pattern):
                    try:
                        yield code, self.__handlers[argument]()
                    except KeyError:
                        raise ValueError('Unexpected argument type found!')
                    break
            else:
                raise ValueError('Unexpected instruction code found!')

    def __parse_number(self):
        """Interpret the head of the stream as a number."""
        bits = tuple(self.__get_bits())
        if bits:
            sign, *bits = bits
            return self.__binary_bits_to_number(bits) * (+1, -1)[sign]
        return 0

    def __get_bits(self):
        """Return the bits of either a number or a label."""
        while True:
            value = self.__stream.pop()
            if value == self.__stream('\n'):
                break
            yield 1 - (value >> 1)

    @staticmethod
    def __binary_bits_to_number(bits):
        """Convert a binary bit string into a number."""
        value = 0
        for bit in bits:
            value = value << 1 | bit
        return value

    def __parse_label(self):
        """Interpret the head of the stream as a label."""
        bits = tuple(self.__get_bits())
        number = self.__name_bits_to_number(bits)
        return self.__number_to_name(number)

    @classmethod
    def __name_bits_to_number(cls, bits):
        """Convert a name bit string into a number."""
        return cls.__binary_bits_to_number(bits) + (1 << len(bits)) - 1

    @classmethod
    def __number_to_name(cls, number):
        """Convert a number into a valid identifier."""
        if number < cls.HEAD_BASE:
            return cls.HEAD_CHAR[number]
        q, r = divmod(number - cls.HEAD_BASE, cls.TAIL_BASE)
        return cls.__number_to_name(q) + cls.TAIL_CHAR[r]


class Code(tuple):

    """Code(iterable) -> Code instance

    The code object verifies all instructions provided at creation time."""

    VALIDATORS = {Arg.NULL: lambda argument: argument is None,
                  Arg.NUMBER: lambda argument: isinstance(argument, int),
                  Arg.LABEL: lambda argument: isinstance(argument, str)}

    def __new__(cls, iterable):
        """Create a new Code object while verifying the iterable."""
        return super().__new__(cls, (cls._check(item) for item in iterable))

    @classmethod
    def _check(cls, item):
        """Make sure that the item has the expected instruction format."""
        try:
            code, argument = item
        except ValueError:
            raise ValueError('Items in iterable must be code/argument pairs!')
        else:
            # noinspection PyProtectedMember
            Prototype._check(code)
            try:
                if not cls.VALIDATORS[INS[code - 1].argument](argument):
                    raise TypeError('Code argument was of unexpected type!')
            except KeyError:
                raise ValueError('Unexpected argument type found!')
        return code, argument


if __name__ == '__main__':
    main()
