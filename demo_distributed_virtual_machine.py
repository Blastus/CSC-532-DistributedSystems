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
import multiprocessing.managers
import pathlib
import socket
import sys
import uuid

import compiler
import demo_virtual_machine_gui
import processor
import safe_tkinter

# Public Names
__all__ = (
    'LOGGER',
    'PORT',
    'AUTHKEY',
    'INTERFACE_INSTANCE',
    'main',
    'run_heap_server',
    'HeapManager',
    'run_stack_server',
    'StackManager',
    'run_executable_server',
    'ExecutableManager',
    'run_processor_client',
    'create_client_connections',
    'get_interface_and_path_to_ws_program',
    'run_user_terminal_server',
    'InterfaceManager',
    'DISPATCH_TABLE'
)

# Module Documentation
__version__ = 1, 0, 0
__date__ = datetime.date(2022, 11, 6)
__author__ = 'Stephen Paul Chappell'
__credits__ = 'CSC-532'

# Symbolic Constants
LOGGER = logging.Logger('default')
PORT = 46656
AUTHKEY = uuid.UUID('cebee708-7986-4c06-8640-c7bcd4e9c1d6')
INTERFACE_INSTANCE = None


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
    manager = HeapManager(('', PORT), AUTHKEY.bytes)
    server = manager.get_server()
    server.serve_forever()


class HeapManager(multiprocessing.managers.BaseManager):
    """Allows the creation of managed, distributed heaps."""


HeapManager.register('Heap', processor.Heap)


def run_stack_server():
    """Create a managed server for a distributed stack."""
    LOGGER.info('Starting the stack server ...')
    manager = StackManager(('', PORT), AUTHKEY.bytes)
    server = manager.get_server()
    server.serve_forever()


class StackManager(multiprocessing.managers.BaseManager):
    """Allows the creation of managed, distributed stacks."""


StackManager.register('Stack', processor.Stack)


def run_executable_server():
    """Create a managed server for a distributed executable."""
    LOGGER.info('Starting the executable server ...')
    manager = ExecutableManager(('', PORT), AUTHKEY.bytes)
    server = manager.get_server()
    server.serve_forever()


class ExecutableManager(multiprocessing.managers.BaseManager):
    """Allows the creation of managed, distributed executables."""


ExecutableManager.register('Executable', processor.Executable)


def run_processor_client():
    """Create a managed client for a distributed processor."""
    LOGGER.info('Starting the processor client & server ...')
    servers = create_client_connections()
    io, path = get_interface_and_path_to_ws_program()
    try:
        with path.open() as file:
            source = file.read()
    except OSError:
        io.handle_error()
    else:
        my_compiler = compiler.Compiler(compiler.Prototype.SYMBOLS)
        try:
            code = my_compiler.compile(source)
        except ValueError:
            io.handle_error()
        else:
            cpu = processor.Processor(
                code,
                io,
                servers[ExecutableManager],
                servers[StackManager],
                servers[HeapManager]
            )
            try:
                cpu.run()
            except (EOFError, KeyboardInterrupt):
                io.handle_error()


def create_client_connections():
    """Connect the processor to the other nodes of the virtual machine."""
    servers = {
        'zero-Virtual-Machine-A': HeapManager,
        'zero-Virtual-Machine-B': StackManager,
        'zero-Virtual-Machine-C': ExecutableManager,
        'zero-Virtual-Machine-E': InterfaceManager
    }
    for host, manager_class in servers.copy().items():
        manager = manager_class((host, PORT), AUTHKEY.bytes)
        manager.connect()
        servers[manager_class] = manager
    return servers


def get_interface_and_path_to_ws_program():
    """Handles the GUI responsibilities of the processor client."""
    root = demo_virtual_machine_gui.Example.get_root()
    root.withdraw()
    # noinspection PyUnresolvedReferences
    io = servers[InterfaceManager].get_interface()
    path = pathlib.Path(safe_tkinter.Open(
        root,
        filetypes=(('Program Files', '.ws'),
                   ('All Files', '*')),
        initialdir=pathlib.PurePath(sys.argv[0]).parent,
        parent=root,
        title='Please select a program to run.'
    ).show())
    return io, path


def run_user_terminal_server():
    """Create a managed server for a distributed user terminal."""
    global INTERFACE_INSTANCE
    LOGGER.info('Starting the user terminal server ...')
    root = demo_virtual_machine_gui.Example.get_root()
    INTERFACE_INSTANCE = demo_virtual_machine_gui.TkinterIO(root)
    manager = InterfaceManager(('', PORT), AUTHKEY.bytes)
    server = manager.get_server()
    server.serve_forever()


class InterfaceManager(multiprocessing.managers.BaseManager):
    """Allows the creation of managed, distributed GUI terminals."""


InterfaceManager.register(
    'get_interface',
    lambda: INTERFACE_INSTANCE,
    None,
    ('read_number', 'read_character', 'output_number', 'output_character',
     'handle_error')
)


# Another Symbolic Constant
DISPATCH_TABLE = {
    'zero-Virtual-Machine-A': run_heap_server,
    'zero-Virtual-Machine-B': run_stack_server,
    'zero-Virtual-Machine-C': run_executable_server,
    'zero-Virtual-Machine-D': run_processor_client,
    'zero-Virtual-Machine-E': run_user_terminal_server
}

if __name__ == '__main__':
    main()
