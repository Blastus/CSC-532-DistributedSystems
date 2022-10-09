#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test the processor module.

This program will attempt to validate the processor module and verify its
correctness. In particular, there are several classes that need to have a
thorough check of their operations and to all ensure that exceptions will
be raised when needed. At the moment, the tests are not yet completed."""

import datetime
import unittest

import compiler
import processor

# Public Names
__all__ = (
    'TestExecutable',
)

# Module Documentation
__version__ = 1, 0, 0
__date__ = datetime.date(2022, 10, 9)
__author__ = 'Stephen Paul Chappell'
__credits__ = 'CSC-532'


class TestExecutable(unittest.TestCase):
    """Class that examines the processor.Executable class functionality."""

    def test_init(self):
        """Validate the initialization of the Executable class."""
        self.assertRaises(TypeError, processor.Executable, [None] * 10)
        code = compiler.Code(((compiler.Op.PUSH, 1),
                              (compiler.Op.PUSH, 2),
                              (compiler.Op.PUSH, 3),
                              (compiler.Op.DUPLICATE, None),
                              (compiler.Op.COPY, 3),
                              (compiler.Op.COPY, 3),
                              (compiler.Op.COPY, 2),
                              (compiler.Op.PUSH, 0),
                              (compiler.Op.DUPLICATE, None),
                              (compiler.Op.COPY, 4),
                              (compiler.Op.CALL_SUBROUTINE, 'A'),
                              (compiler.Op.JUMP_ALWAYS, 'B'),
                              (compiler.Op.MARK_LOCATION, 'D'),
                              (compiler.Op.ADDITION, None),
                              (compiler.Op.JUMP_IF_ZERO, 'E'),
                              (compiler.Op.MARK_LOCATION, 'C'),
                              (compiler.Op.JUMP_ALWAYS, 'C'),
                              (compiler.Op.MARK_LOCATION, 'B'),
                              (compiler.Op.DISCARD, None),
                              (compiler.Op.END_PROGRAM, None),
                              (compiler.Op.MARK_LOCATION, 'A'),
                              (compiler.Op.STORE, None),
                              (compiler.Op.RETRIEVE, None),
                              (compiler.Op.COPY, 1),
                              (compiler.Op.COPY, 3),
                              (compiler.Op.MODULO, None),
                              (compiler.Op.INTEGER_DIVISION, None),
                              (compiler.Op.SWAP, None),
                              (compiler.Op.SUBTRACTION, None),
                              (compiler.Op.MULTIPLICATION, None),
                              (compiler.Op.ADDITION, None),
                              (compiler.Op.DUPLICATE, None),
                              (compiler.Op.JUMP_IF_NEGATIVE, 'D'),
                              (compiler.Op.JUMP_ALWAYS, 'C'),
                              (compiler.Op.MARK_LOCATION, 'E'),
                              (compiler.Op.SLIDE, 2),
                              (compiler.Op.END_SUBROUTINE, None)))
        executable = processor.Executable(code)
        self.assertIsNotNone(executable)
        self.assertIsInstance(executable, processor.Executable)


if __name__ == '__main__':
    unittest.main()
