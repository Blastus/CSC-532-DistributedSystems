#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test ability to connect to a manager server using a client.

This program should be used in conjunction with test_multiprocessing_server
included in this project. The goal is to connect to the server and interact
with objects managed by it. This is the author's first attempt and is going
to be a learning experience. See UNLICENSE for program copying information."""

import datetime
import logging
import multiprocessing.managers
import pathlib
import sys
import uuid

# Public Names
__all__ = (
    'HOST',
    'PORT',
    'AUTHKEY',
    'main',
    'StackManager'
)

# Module Documentation
__version__ = 1, 0, 0
__date__ = datetime.date(2022, 9, 25)
__author__ = 'Stephen Paul Chappell'
__credits__ = 'CSC-532'

# Symbolic Constants
HOST = 'ZERO-FINALE'
PORT = 46656
AUTHKEY = uuid.UUID('912e7512-0630-40f4-a62d-71d6a613d2ed')


def main():
    """Tries to connect to a server and interact with an object there."""
    logger = multiprocessing.log_to_stderr(logging.DEBUG)
    logger.info(f'Starting {pathlib.Path(sys.argv[0]).name} ...')
    manager = StackManager((HOST, PORT), AUTHKEY.bytes)
    manager.connect()
    # noinspection PyUnresolvedReferences
    stack = manager.Stack(True)
    print(f'{stack.push(12) = }')
    print(f'{stack.push(30) = }')
    print(f'{stack.add() = }')
    print(f'{stack.pop() = }')


class StackManager(multiprocessing.managers.BaseManager):
    """Allows the creation of a stack object usable over a network."""


StackManager.register('Stack')


if __name__ == '__main__':
    main()
