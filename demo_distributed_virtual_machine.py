#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""Demonstrate that a distributed virtual machine is possible.

This program should run different parts of the virtual machine depending on
which remote computer it is started on. A mapping is required to decide the
responsibilities of each remote computer. If the connections must be formed
in a particular order, then the program may need special logic and code for
the startup procedure to either ensure the proper startup procedure or else
to produce helpful warning messages for the initiator of code execution."""

import datetime
import logging
import multiprocessing
import socket

# Public Names
__all__ = (
    'main',
    'run_heap_server',
    'run_stack_server',
    'run_executable_server',
    'run_processor_client_server',
    'run_user_terminal_client',
    'DISPATCH_TABLE'
)

# Module Documentation
__version__ = 1, 0, 0
__date__ = datetime.date(2022, 11, 6)
__author__ = 'Stephen Paul Chappell'
__credits__ = 'CSC-532'


def main():
    """Determine which node is running and start the right server or client."""
    global LOGGER
    LOGGER = multiprocessing.log_to_stderr(logging.DEBUG)
    hostname = socket.gethostname()
    try:
        handler = DISPATCH_TABLE[hostname]
    except KeyError:
        LOGGER.critical(f'Host {hostname!r} not found.')
    else:
        handler()


def run_heap_server():
    """Create a managed server for a distributed heap."""
    LOGGER.info('Starting the heap server ...')


def run_stack_server():
    """Create a managed server for a distributed stack."""
    LOGGER.info('Starting the stack server ...')


def run_executable_server():
    """Create a managed server for a distributed executable."""
    LOGGER.info('Starting the executable server ...')


def run_processor_client_server():
    """Create a managed client & server for a distributed processor."""
    LOGGER.info('Starting the processor client & server ...')


def run_user_terminal_client():
    """Create a managed client for a distributed user terminal."""
    LOGGER.info('Starting the user terminal client ...')


# Symbolic Constants
LOGGER = logging.Logger('default')
DISPATCH_TABLE = {
    'zero-Virtual-Machine-A': run_heap_server,
    'zero-Virtual-Machine-B': run_stack_server,
    'zero-Virtual-Machine-C': run_executable_server,
    'zero-Virtual-Machine-D': run_processor_client_server,
    'zero-Virtual-Machine-E': run_user_terminal_client
}


if __name__ == '__main__':
    main()
