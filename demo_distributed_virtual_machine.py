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
import socket
import threading
import uuid

import compiler
import demo_virtual_machine_gui
import processor

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
    'run_processor_client_server',
    'run_user_terminal_client',
    'VirtualMachineGUI',
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


def run_processor_client_server():
    """Create a managed client & server for a distributed processor."""
    LOGGER.info('Starting the processor client & server ...')
    # The following is just test code to get a processor to connect
    # to distributed systems -- the heap, stack, and executable.
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
    interface_manager = InterfaceManager(
        ('zero-Virtual-Machine-E', PORT), AUTHKEY.bytes)
    interface_manager.connect()
    executable_manager = ExecutableManager(
        ('zero-Virtual-Machine-C', PORT), AUTHKEY.bytes)
    executable_manager.connect()
    stack_manager = StackManager(
        ('zero-Virtual-Machine-B', PORT), AUTHKEY.bytes)
    stack_manager.connect()
    heap_manager = HeapManager(
        ('zero-Virtual-Machine-A', PORT), AUTHKEY.bytes)
    heap_manager.connect()
    # noinspection PyUnresolvedReferences
    interface = interface_manager.get_interface()
    process = processor.Processor(
        code, interface, executable_manager, stack_manager, heap_manager)
    process.run()


def run_user_terminal_client():
    """Create a managed client for a distributed user terminal."""
    global INTERFACE_INSTANCE
    LOGGER.info('Starting the user terminal client ...')
    root = demo_virtual_machine_gui.Example()
    VirtualMachineGUI.set_master(root)
    INTERFACE_INSTANCE = VirtualMachineGUI()
    manager = InterfaceManager(('', PORT), AUTHKEY.bytes)
    server = manager.get_server()
    threading.Thread(target=server.serve_forever, daemon=True).start()
    root.mainloop()


class VirtualMachineGUI(demo_virtual_machine_gui.TkinterIO):
    """Handles displaying a GUI terminal to the user."""

    __master = None

    @classmethod
    def set_master(cls, master):
        """Arrange for class instances to have an automatic master widget."""
        print(f'{cls.__name__} setting master to {master} ...')
        if not isinstance(master, demo_virtual_machine_gui.Example):
            raise TypeError('master must be an instance of Example')
        cls.__master = master

    def __init__(self):
        """Initialize the widget and arrange for automatically showing up."""
        print(f'Creating new {type(self).__name__} instance ...')
        master = self.__master
        if master is None:
            raise RuntimeError('master should be set before instantiation')
        super().__init__(master)


class InterfaceManager(multiprocessing.managers.BaseManager):
    """Allows the creation of managed, distributed GUI terminals."""


InterfaceManager.register(
    'get_interface',
    lambda: INTERFACE_INSTANCE,
    None,
    ('read_number', 'read_character', 'output_number', 'output_character')
)


# Another Symbolic Constant
DISPATCH_TABLE = {
    'zero-Virtual-Machine-A': run_heap_server,
    'zero-Virtual-Machine-B': run_stack_server,
    'zero-Virtual-Machine-C': run_executable_server,
    'zero-Virtual-Machine-D': run_processor_client_server,
    'zero-Virtual-Machine-E': run_user_terminal_client
}

if __name__ == '__main__':
    main()
