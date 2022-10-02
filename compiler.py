#! /usr/bin/env python3
"""Provide a way to compile WS into a basic machine representation.

This module contains facilities for compiling WS code into a representation
suitable as a starting point for interpretation. Several tables can be read
to provide further support for understanding the generated code objects."""

__author__ = 'Stephen "Zero" Chappell <Noctis.Skytower@gmail.com>'
__date__ = '19 September 2013'
__version__ = 2, 0, 0

################################################################################

# These are modules that are used in the code below.

import collections
import functools
import string

################################################################################

# The tokenizer converts the source into an enumeration of symbols.

class Tokenizer(collections.deque):

    "Tokenizer(symbols, source) -> Tokenizer instance"

    def __init__(self, symbols, source):
        "Initialize the Tokenizer with a symbol table and source tokens."
        base = tuple(symbols)
        if len(base) != len(set(base)):
            raise ValueError('All symbols must be unique!')
        self.__base = base
        super().__init__(self(symbol) for symbol in source if symbol in self)

    def __contains__(self, symbol):
        "Check if symbol is recognized by the tokenizer."
        return symbol in self.__base

    def __call__(self, symbol):
        "Convert symbol into its enumerated form if possible."
        return self.__base.index(symbol)

    def consume(self, pattern):
        "Try to pop the pattern off the front of the token stream."
        pattern_len = len(pattern)
        if len(self) < pattern_len:
            return False
        if all(s == p for s, p in zip(self, pattern)):
            for _ in range(pattern_len):
                self.pop()
            return True
        return False

    def pop(self):
        "Pull a token off the front of the token stream."
        return self.popleft()

################################################################################

# The ARG table contains argument types; the OP table contains operation codes.

def enum(names):
    "Create a simple enumeration having similarities to C."
    return type('enum', (), dict(map(reversed, enumerate(
        names.replace(',', ' ').split())), __slots__=()))()

ARG = enum('NULL, NUMBER, LABEL')

OP = enum('''\
RETRIEVE, STORE, READ_NUMBER, READ_CHARACTER, OUTPUT_NUMBER, OUTPUT_CHARACTER,
MODULO, INTEGER_DIVISION, SUBTRACTION, MULTIPLICATION, ADDITION,
JUMP_IF_NEGATIVE, END_SUBROUTINE, JUMP_IF_ZERO, END_PROGRAM, CALL_SUBROUTINE,
JUMP_ALWAYS, MARK_LOCATION, SLIDE, COPY, SWAP, DISCARD, DUPLICATE, PUSH''')

################################################################################

# Prototypes provide data for decoding individual instructions correctly.

class Prototype(collections.namedtuple('base', 'pattern, argument, code')):

    "Prototype(pattern, argument, code) -> Prototype instance"

    SYMBOLS = functools.partial(Tokenizer, '\t\n ')

    def __new__(cls, pattern, argument, code):
        "Check and fix the arguments before creating the Prototype."
        prototype = tuple(cls.SYMBOLS(pattern))
        if len(pattern) != len(prototype):
            raise ValueError('An unexpected symbol was found!')
        if argument not in vars(type(ARG)).values():
            raise ValueError('An unexpected argument type was given!')
        cls._check(code)
        return super().__new__(cls, prototype, argument, code)

    @staticmethod
    def _check(code):
        "Validate that instruction code is in operation table."
        if code not in vars(type(OP)).values():
            raise ValueError('An unexpected operation code was given!')

########################################
# '\t\t'    Heap Access
#           '\t'    Retrieve
#           ' '     Store
########################################
# '\t\n'    I/O
#           '\t\t'  Read Number
#           '\t '   Read Character
#           ' \t'   Output Number
#           '  '    Output Character
########################################
# '\t '     Arithmetic
#           '\t\t'  Modulo
#           '\t '   Integer Division
#           ' \t'   Subtraction
#           ' \n'   Multiplication
#           '  '    Addition
########################################
# '\n'      Flow Control
#           '\t\t'  Jump If Negative
#           '\t\n'  End Subroutine
#           '\t '   Jump If Zero
#           '\n\n'  End Program
#           ' \t'   Call Subroutine
#           ' \n'   Jump Always
#           '  '    Mark Location
########################################
# ' '       Stack Manipulation
#           '\t\n'  Slide
#           '\t '   Copy
#           '\n\t'  Swap
#           '\n\n'  Discard
#           '\n '   Duplicate
#           ' '     Push
########################################

################################################################################

# The INS table is created from the documentation above and then checked.

INS = (Prototype('\t\t\t', ARG.NULL, OP.RETRIEVE),
       Prototype('\t\t ', ARG.NULL, OP.STORE),
       Prototype('\t\n\t\t', ARG.NULL, OP.READ_NUMBER),
       Prototype('\t\n\t ', ARG.NULL, OP.READ_CHARACTER),
       Prototype('\t\n \t', ARG.NULL, OP.OUTPUT_NUMBER),
       Prototype('\t\n  ', ARG.NULL, OP.OUTPUT_CHARACTER),
       Prototype('\t \t\t', ARG.NULL, OP.MODULO),
       Prototype('\t \t ', ARG.NULL, OP.INTEGER_DIVISION),
       Prototype('\t  \t', ARG.NULL, OP.SUBTRACTION),
       Prototype('\t  \n', ARG.NULL, OP.MULTIPLICATION),
       Prototype('\t   ', ARG.NULL, OP.ADDITION),
       Prototype('\n\t\t', ARG.LABEL, OP.JUMP_IF_NEGATIVE),
       Prototype('\n\t\n', ARG.NULL, OP.END_SUBROUTINE),
       Prototype('\n\t ', ARG.LABEL, OP.JUMP_IF_ZERO),
       Prototype('\n\n\n', ARG.NULL, OP.END_PROGRAM),
       Prototype('\n \t', ARG.LABEL, OP.CALL_SUBROUTINE),
       Prototype('\n \n', ARG.LABEL, OP.JUMP_ALWAYS),
       Prototype('\n  ', ARG.LABEL, OP.MARK_LOCATION),
       Prototype(' \t\n', ARG.NUMBER, OP.SLIDE),
       Prototype(' \t ', ARG.NUMBER, OP.COPY),
       Prototype(' \n\t', ARG.NULL, OP.SWAP),
       Prototype(' \n\n', ARG.NULL, OP.DISCARD),
       Prototype(' \n ', ARG.NULL, OP.DUPLICATE),
       Prototype('  ', ARG.NUMBER, OP.PUSH))

assert INS == tuple(sorted(INS, key=lambda ins: ins.pattern)), \
       'Patterns were not in the expected order!'
assert INS == tuple(sorted(INS, key=lambda ins: ins.code)), \
       'Codes were not in the expected order!'

################################################################################

# The compiler generates code objects that can be processed further if needed.

class Compiler:

    "Compiler(tokenizer) -> Compiler instance"

    HEAD_CHAR = ''.join(sorted(string.ascii_letters + '_'))
    TAIL_CHAR = ''.join(sorted(string.digits + HEAD_CHAR))
    HEAD_BASE, TAIL_BASE = len(HEAD_CHAR), len(TAIL_CHAR)

    def __init__(self, tokenizer):
        "Initialize the Compiler with the tokenizer to use on the source."
        self.__tokenizer = tokenizer
        self.__handlers = {ARG.NULL: lambda: None,
                           ARG.NUMBER: self.__parse_number,
                           ARG.LABEL: self.__parse_label}

    def compile(self, source):
        "Compile the source into a code object to be used elsewhere."
        self.__stream = self.__tokenizer(source)
        return Code(self.__parse_instructions())

    def __parse_instructions(self):
        "Process the stream and return the relative instruction codes."
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
        "Interpret the head of the stream as a number."
        bits = tuple(self.__get_bits())
        if bits:
            sign, *bits = bits
            return self.__binary_bits_to_number(bits) * (+1, -1)[sign]
        return 0

    def __get_bits(self):
        "Return the bits of either a number or a label."
        while True:
            value = self.__stream.pop()
            if value == self.__stream('\n'):
                break
            yield 1 - (value >> 1)

    @staticmethod
    def __binary_bits_to_number(bits):
        "Convert a binary bit string into a number."
        value = 0
        for bit in bits:
            value = value << 1 | bit
        return value

    def __parse_label(self):
        "Interpret the head of the stream as a label."
        bits = tuple(self.__get_bits())
        number = self.__name_bits_to_number(bits)
        return self.__number_to_name(number)

    @classmethod
    def __name_bits_to_number(cls, bits):
        "Convert a name bit string into a number."
        return cls.__binary_bits_to_number(bits) + (1 << len(bits)) - 1

    @classmethod
    def __number_to_name(cls, number):
        "Convert a number into a valid identifier."
        if number < cls.HEAD_BASE:
            return cls.HEAD_CHAR[number]
        q, r = divmod(number - cls.HEAD_BASE, cls.TAIL_BASE)
        return cls.__number_to_name(q) + cls.TAIL_CHAR[r]

################################################################################

# The code object verifies all instructions provided at creation time.

class Code(tuple):

    "Code(iterable) -> Code instance"

    VALIDATORS = {ARG.NULL: lambda argument: argument is None,
                  ARG.NUMBER: lambda argument: isinstance(argument, int),
                  ARG.LABEL: lambda argument: isinstance(argument, str)}

    def __new__(cls, iterable):
        "Create a new Code object while verifying the iterable."
        return super().__new__(cls, (cls._check(item) for item in iterable))

    @classmethod
    def _check(cls, item):
        "Make sure that the item has the expected instruction format."
        try:
            code, argument = item
        except ValueError:
            raise ValueError('Items in iterable must be code/argument pairs!')
        else:
            Prototype._check(code)
            try:
                if not cls.VALIDATORS[INS[code].argument](argument):
                    raise TypeError('Code argument was of unexpected type!')
            except KeyError:
                raise ValueError('Unexpected argument type found!')
        return code, argument

################################################################################

def test():
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
                           'D',  'E',  0,    0,    None, None, None, 0)))
    compiled_code = Compiler(Prototype.SYMBOLS).compile(''.join(source))
    if compiled_code != code:
        raise ValueError('Code was not compiled correctly!')

################################################################################

if __name__ == '__main__':
    test()
