#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test connections across Virtual Machines via the multiprocessing module.

This program will attempt to register an arbitrary class with a manager
and then communicate with it over a network connection. This should not
strictly require having multiple VMs for testing initially. Interaction
with managed objects can first be tested over the network. Once testing
has been completed at the network level, VMs can be used to finish what
is needed for final verification. See UNLICENSE for legal restrictions."""

import datetime
import logging
import multiprocessing
import multiprocessing.managers
import pathlib
import sys
import uuid

# Public Names
__all__ = (
    'PORT',
    'AUTHKEY',
    'main',
    'Stack',
    'StackManager'
)

# Module Documentation
__version__ = 1, 0, 0
__date__ = datetime.date(2022, 9, 25)
__author__ = 'Stephen Paul Chappell'
__credits__ = 'CSC-532'

# Symbolic Constants
PORT = 46656
AUTHKEY = uuid.UUID('912e7512-0630-40f4-a62d-71d6a613d2ed')


def main():
    """Starts the test for using multiprocessing over a network."""
    logger = multiprocessing.log_to_stderr(logging.INFO)
    logger.info(f'Starting {pathlib.Path(sys.argv[0]).name} ...')
    manager = StackManager(('', PORT), AUTHKEY.bytes)
    server = manager.get_server()
    server.serve_forever()


class Stack:
    """Acts as a data structure for a VM supporting various operations."""

    def __init__(self, debug=False):
        """Initializes the stack's internal data structures."""
        self.__debug = debug
        self.__data = []

    def push(self, value):
        """Adds an item to the stack."""
        if self.__debug:
            print(f'{type(self).__name__!s}.push({value!r})')
        self.__data.append(value)

    def add(self):
        """Adds top two items together and places result on top."""
        if self.__debug:
            print(f'{type(self).__name__!s}.add()')
        b, a = self.pop(), self.pop()
        self.__data.append(a + b)

    def sub(self):
        """Subtracts top two items together and places result on top."""
        if self.__debug:
            print(f'{type(self).__name__!s}.sub()')
        b, a = self.pop(), self.pop()
        self.__data.append(a - b)

    def mul(self):
        """Multiplies top two items together and places result on top."""
        if self.__debug:
            print(f'{type(self).__name__!s}.mul()')
        b, a = self.pop(), self.pop()
        self.__data.append(a * b)

    def div(self):
        """Divides top two items together and places result on top."""
        if self.__debug:
            print(f'{type(self).__name__!s}.div()')
        b, a = self.pop(), self.pop()
        self.__data.append(a / b)

    def pop(self):
        """Gets top item off stack and returns it."""
        value = self.__data.pop()
        if self.__debug:
            print(f'{type(self).__name__!s}.pop() -> {value!r}')
        return value


class StackManager(multiprocessing.managers.BaseManager):
    """Allows the creation of a stack object usable over a network."""


StackManager.register('Stack', Stack)


if __name__ == '__main__':
    main()
