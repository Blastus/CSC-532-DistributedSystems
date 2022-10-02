#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test the compiler module.

This program will attempt to validate the compiler module and verify its
correctness. The module is capable of raising various errors and must do
so when appropriate. Knowledge of the Whitespace language will be needed
when modifying this test code. Otherwise, errors could be introduced."""

import datetime
import unittest

import compiler

# Public Names
__all__ = (
    'TestTokenizer',
)

# Module Documentation
__version__ = 1, 0, 0
__date__ = datetime.date(2022, 10, 2)
__author__ = 'Stephen Paul Chappell'
__credits__ = 'CSC-532'


class TestTokenizer(unittest.TestCase):
    """Class that examines the compiler.Tokenizer class functionality."""

    def test_init(self):
        """Validate the initialization of the Tokenizer class."""
        self.assertRaises(ValueError, compiler.Tokenizer, ' ' * 2, ())
        tokenizer = compiler.Tokenizer('\t\n ', '\t\n ')
        self.assertIsNotNone(tokenizer)
        self.assertIsInstance(tokenizer, compiler.Tokenizer)


if __name__ == '__main__':
    unittest.main()
