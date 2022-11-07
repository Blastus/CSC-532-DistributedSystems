#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""Provide classes that facilitate executing WS Code instances.

This module makes available several classes that are designed to run VMC
(Virtual Machine Code) produced by the compiler. A processor instance can
execute a code instance after arranging absolute jump address computation."""

import collections
import datetime

import compiler

# Public Names
__all__ = (
    'main',
    'Executable',
    'Stack',
    'Heap',
    'Processor'
)

# Module Documentation
__version__ = 2, 0, 1
__date__ = datetime.date(2022, 10, 9)
__author__ = 'Stephen Paul Chappell'
__credits__ = 'CSC-532'


def main():
    """Tests the various operations that a Processor should perform."""
    # import interface
    import unittest.mock
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
    # Processor(code, interface.ProcessorInterface()).run()
    interface = unittest.mock.Mock(spec_set=(
        'read_number', 'read_character', 'output_number', 'output_character'))
    Processor(code, interface).run()


class Executable(tuple):
    """Executable(instructions) -> Executable instance

    The executable converts code into a form that runs on the processor."""

    def __new__(cls, instructions):
        """Create a new Executable after checking the type of instructions."""
        if not isinstance(instructions, compiler.Code):
            raise TypeError('Instructions must be an instance of Code!')
        return super().__new__(cls, cls.__compute_jumps(instructions))

    @staticmethod
    def __compute_jumps(instructions):
        """Catalogue jump locations and resolve their absolute addresses."""
        marker, offset, action = {}, 0, collections.deque()
        for operation, argument in instructions:
            if operation == compiler.Op.MARK_LOCATION:
                if argument in marker:
                    raise ValueError('{!r} is duplicated!'.format(argument))
                marker[argument] = offset
            else:
                action.append((operation, argument))
                offset += 1
        for operation, argument in action:
            if compiler.INS[operation - 1].argument == compiler.Arg.LABEL:
                try:
                    yield operation, marker[argument]
                except KeyError:
                    raise ValueError('{!r} is unavailable!'.format(argument))
            else:
                yield operation, argument


class Stack(collections.deque):
    """Stack() -> Stack instance

    The stack implements all of the various stack operations."""

    def modulo(self, _):
        """Replace the top two values with the results of the % operator."""
        value = self.pop()
        self[-1] %= value

    def integer_division(self, _):
        """Replace the top two values with the results of the // operator."""
        value = self.pop()
        self[-1] //= value

    def subtraction(self, _):
        """Replace the top two values with the results of the - operator."""
        value = self.pop()
        self[-1] -= value

    def multiplication(self, _):
        """Replace the top two values with the results of the * operator."""
        value = self.pop()
        self[-1] *= value

    def addition(self, _):
        """Replace the top two values with the results of the + operator."""
        value = self.pop()
        self[-1] += value

    def slide(self, number):
        """Remove the number of values underneath the top value."""
        pop = self.pop
        value = pop()
        for _ in range(number):
            pop()
        self.append(value)

    # noinspection PyMethodOverriding
    def copy(self, number):
        """Replicate the indexed value to the top of the stack."""
        self.append(self[-(number + 1)])

    def swap(self, _):
        """Switch the position of the top two values on the stack."""
        pop, append = self.pop, self.append
        a, b = pop(), pop()
        append(a)
        append(b)

    def discard(self, _):
        """Remove the top value from off of the stack."""
        self.pop()

    def duplicate(self, _):
        """Replicate the top value back onto the stack."""
        self.append(self[-1])

    # Stack.push is a synonym for deque.append.
    push = collections.deque.append


class Heap(dict):
    """Heap() -> Heap instance

    The heap acts as the virtual machine's global memory manager."""

    def retrieve(self, address):
        """Get the virtual value stored at the address."""
        return self.get(address, 0)

    def store(self, value, address):
        """Set the virtual value meant for the address."""
        if value:
            self[address] = value
        else:
            self.pop(address, None)


class Processor:
    """Processor(code, io) -> Code instance

    The processor takes code and executes it in a virtual machine."""

    def __init__(self, code, io, executable_manager=None, stack_manager=None,
                 heap_manager=None):
        """Initialize the Processor with both Executable and IO instances."""
        self.__executable_manager = executable_manager
        self.__stack_manager = stack_manager
        self.__heap_manager = heap_manager
        self.__exe, self.__io = self.__new_executable(code), io

    def __new_executable(self, code):
        """Create a new executable with respect to the executable manager."""
        return (Executable(code)
                if self.__executable_manager is None else
                self.__executable_manager.Executable(code))

    def __new_stack(self):
        """Create a new stack with respect to the stack manager."""
        return (Stack()
                if self.__stack_manager is None else
                self.__stack_manager.Stack())

    def __new_heap(self):
        """Create a new heap with respect to the heap manager."""
        return (Heap()
                if self.__heap_manager is None else
                self.__heap_manager.Heap())

    def run(self):
        """Execute the stored program while utilizing the given interface."""
        # Create all needed runtime variables.
        stack, heap, io, index, call, executable = (self.__new_stack(),
                                                    self.__new_heap(),
                                                    self.__io,
                                                    0,
                                                    collections.deque(),
                                                    self.__exe)
        # Create method shortcuts to improve lookup time.
        (stack_pop, stack_push,
         heap_retrieve, heap_store,
         io_read_number, io_read_character,
         io_output_number, io_output_character,
         call_pop, call_append) = \
            (stack.pop, stack.push,
             heap.retrieve, heap.store,
             io.read_number, io.read_character,
             io.output_number, io.output_character,
             call.pop, call.append)

        # Create heap control handlers.
        def retrieve(_):
            # noinspection PyArgumentList
            stack_push(heap_retrieve(stack_pop()))

        def store(_):
            # noinspection PyArgumentList
            heap_store(stack_pop(), stack_pop())

        # Create input and output handlers.
        def read_number(_):
            # noinspection PyArgumentList
            heap_store(io_read_number(), stack_pop())

        def read_character(_):
            # noinspection PyArgumentList
            heap_store(ord(io_read_character()), stack_pop())

        def output_number(_):
            io_output_number(stack_pop())

        def output_character(_):
            io_output_character(chr(stack_pop()))

        # Create flow control handlers.
        def jump_if_negative(number):
            nonlocal index
            if stack_pop() < 0:
                index = number

        def end_subroutine(_):
            nonlocal index
            index = call_pop()

        def jump_if_zero(number):
            nonlocal index
            if not stack_pop():
                index = number

        def end_program(_):
            raise SystemExit()

        def call_subroutine(number):
            nonlocal index
            call_append(index)
            index = number

        def jump_always(number):
            nonlocal index
            index = number

        def mark_location(_):
            raise NotImplementedError()

        # Create handler mapping for operations.
        handlers = {0: None,
                    compiler.Op.RETRIEVE: retrieve,
                    compiler.Op.STORE: store,
                    compiler.Op.READ_NUMBER: read_number,
                    compiler.Op.READ_CHARACTER: read_character,
                    compiler.Op.OUTPUT_NUMBER: output_number,
                    compiler.Op.OUTPUT_CHARACTER: output_character,
                    compiler.Op.MODULO: stack.modulo,
                    compiler.Op.INTEGER_DIVISION: stack.integer_division,
                    compiler.Op.SUBTRACTION: stack.subtraction,
                    compiler.Op.MULTIPLICATION: stack.multiplication,
                    compiler.Op.ADDITION: stack.addition,
                    compiler.Op.JUMP_IF_NEGATIVE: jump_if_negative,
                    compiler.Op.END_SUBROUTINE: end_subroutine,
                    compiler.Op.JUMP_IF_ZERO: jump_if_zero,
                    compiler.Op.END_PROGRAM: end_program,
                    compiler.Op.CALL_SUBROUTINE: call_subroutine,
                    compiler.Op.JUMP_ALWAYS: jump_always,
                    compiler.Op.MARK_LOCATION: mark_location,
                    compiler.Op.SLIDE: stack.slide,
                    compiler.Op.COPY: stack.copy,
                    compiler.Op.SWAP: stack.swap,
                    compiler.Op.DISCARD: stack.discard,
                    compiler.Op.DUPLICATE: stack.duplicate,
                    compiler.Op.PUSH: stack.push}
        # Verify and optimize handler mapping.
        if handlers.keys() != set(range(len(handlers))):
            raise ValueError('A contiguous set of handlers is needed!')
        handlers = tuple(handlers[operation] for operation in sorted(handlers))
        # Enter virtual machine code processing loop.
        try:
            while True:
                operation, argument = executable[index]
                index += 1
                handlers[operation](argument)
        except SystemExit:
            pass


if __name__ == '__main__':
    main()
