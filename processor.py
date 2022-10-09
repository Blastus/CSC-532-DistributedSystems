#! /usr/bin/env python3
"""Provide classes that facilitate executing WS Code instances.

This module makes available several classes that are designed to run VMC
(Virtual Machine Code) produced by the compiler. A processor instance can
execute a code instance after arranging absolute jump address computation."""

__author__ = 'Stephen "Zero" Chappell <Noctis.Skytower@gmail.com>'
__date__ = '5 June 2013'
__version__ = 2, 0, 0

################################################################################

import collections
import compiler

################################################################################

# The executable converts code into a form that runs on the processor.

class Executable(tuple):

    "Executable(instructions) -> Executable instance"

    def __new__(cls, instructions):
        "Create a new Executable after checking the type of instructions."
        if not isinstance(instructions, compiler.Code):
            raise TypeError('Instructions must be an instance of Code!')
        return super().__new__(cls, cls.__compute_jumps(instructions))

    @staticmethod
    def __compute_jumps(instructions):
        "Catalogue jump locations and resolve their absolute addresses."
        marker, offset, action = {}, 0, collections.deque()
        for operation, argument in instructions:
            if operation == compiler.OP.MARK_LOCATION:
                if argument in marker:
                    raise ValueError('{!r} is duplicated!'.format(argument))
                marker[argument] = offset
            else:
                action.append((operation, argument))
                offset += 1
        for operation, argument in action:
            if compiler.INS[operation].argument == compiler.ARG.LABEL:
                try:
                    yield operation, marker[argument]
                except KeyError:
                    raise ValueError('{!r} is unavailable!'.format(argument))
            else:
                yield operation, argument

################################################################################

# The stack implements all of the various stack operations.

class Stack(collections.deque):

    "Stack() -> Stack instance"

    def modulo(self, null):
        "Replace the top two values with the results of the % operator."
        value = self.pop()
        self[-1] %= value

    def integer_division(self, null):
        "Replace the top two values with the results of the // operator."
        value = self.pop()
        self[-1] //= value

    def subtraction(self, null):
        "Replace the top two values with the results of the - operator."
        value = self.pop()
        self[-1] -= value

    def multiplication(self, null):
        "Replace the top two values with the results of the * operator."
        value = self.pop()
        self[-1] *= value

    def addition(self, null):
        "Replace the top two values with the results of the + operator."
        value = self.pop()
        self[-1] += value

    def slide(self, number):
        "Remove the number of values underneath the top value."
        pop = self.pop
        value = pop()
        for _ in range(number):
            pop()
        self.append(value)

    def copy(self, number):
        "Replicate the indexed value to the top of the stack."
        self.append(self[-(number + 1)])

    def swap(self, null):
        "Switch the position of the top two values on the stack."
        pop, append = self.pop, self.append
        a, b = pop(), pop()
        append(a)
        append(b)

    def discard(self, null):
        "Remove the top value from off of the stack."
        self.pop()

    def duplicate(self, null):
        "Replicate the top value back onto the stack."
        self.append(self[-1])

    # Stack.push is a synonym for deque.append.

    push = collections.deque.append

################################################################################

# The heap acts as the virtual machine's global memory manager.

class Heap(dict):

    "Heap() -> Heap instance"

    def retrieve(self, address):
        "Get the virtual value stored at the address."
        return self.get(address, 0)

    def store(self, value, address):
        "Set the virtual value meant for the address."
        if value:
            self[address] = value
        else:
            self.pop(address, None)

################################################################################

# The processor takes code and executes it in a virtual machine.

class Processor:

    "Processor(code, io) -> Code instance"

    def __init__(self, code, io):
        "Initialize the Processor with both Executable and IO instances."
        self.__exe, self.__io = Executable(code), io

    def run(self):
        "Execute the stored program while utilizing the given interface."
        # Create all needed runtime variables.
        stack, heap, io, index, call, executable = \
            Stack(), Heap(), self.__io, 0, collections.deque(), self.__exe
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
        def retrieve(null):
            stack_push(heap_retrieve(stack_pop()))
        def store(null):
            heap_store(stack_pop(), stack_pop())
        # Create input and output handlers.
        def read_number(null):
            heap_store(io_read_number(), stack_pop())
        def read_character(null):
            heap_store(ord(io_read_character()), stack_pop())
        def output_number(null):
            io_output_number(stack_pop())
        def output_character(null):
            io_output_character(chr(stack_pop()))
        # Create flow control handlers.
        def jump_if_negative(number):
            nonlocal index
            if stack_pop() < 0:
                index = number
        def end_subroutine(null):
            nonlocal index
            index = call_pop()
        def jump_if_zero(number):
            nonlocal index
            if not stack_pop():
                index = number
        def end_program(null):
            raise SystemExit()
        def call_subroutine(number):
            nonlocal index
            call_append(index)
            index = number
        def jump_always(number):
            nonlocal index
            index = number
        def mark_location(null):
            raise NotImplementedError()
        # Create handler mapping for operations.
        handlers = {compiler.OP.RETRIEVE: retrieve,
                    compiler.OP.STORE: store,
                    compiler.OP.READ_NUMBER: read_number,
                    compiler.OP.READ_CHARACTER: read_character,
                    compiler.OP.OUTPUT_NUMBER: output_number,
                    compiler.OP.OUTPUT_CHARACTER: output_character,
                    compiler.OP.MODULO: stack.modulo,
                    compiler.OP.INTEGER_DIVISION: stack.integer_division,
                    compiler.OP.SUBTRACTION: stack.subtraction,
                    compiler.OP.MULTIPLICATION: stack.multiplication,
                    compiler.OP.ADDITION: stack.addition,
                    compiler.OP.JUMP_IF_NEGATIVE: jump_if_negative,
                    compiler.OP.END_SUBROUTINE: end_subroutine,
                    compiler.OP.JUMP_IF_ZERO: jump_if_zero,
                    compiler.OP.END_PROGRAM: end_program,
                    compiler.OP.CALL_SUBROUTINE: call_subroutine,
                    compiler.OP.JUMP_ALWAYS: jump_always,
                    compiler.OP.MARK_LOCATION: mark_location,
                    compiler.OP.SLIDE: stack.slide,
                    compiler.OP.COPY: stack.copy,
                    compiler.OP.SWAP: stack.swap,
                    compiler.OP.DISCARD: stack.discard,
                    compiler.OP.DUPLICATE: stack.duplicate,
                    compiler.OP.PUSH: stack.push}
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

################################################################################

def test():
    import interface
    code = compiler.Code(((compiler.OP.PUSH, 1),
                          (compiler.OP.PUSH, 2),
                          (compiler.OP.PUSH, 3),
                          (compiler.OP.DUPLICATE, None),
                          (compiler.OP.COPY, 3),
                          (compiler.OP.COPY, 3),
                          (compiler.OP.COPY, 2),
                          (compiler.OP.PUSH, 0),
                          (compiler.OP.DUPLICATE, None),
                          (compiler.OP.COPY, 4),
                          (compiler.OP.CALL_SUBROUTINE, 'A'),
                          (compiler.OP.JUMP_ALWAYS, 'B'),
                          (compiler.OP.MARK_LOCATION, 'D'),
                          (compiler.OP.ADDITION, None),
                          (compiler.OP.JUMP_IF_ZERO, 'E'),
                          (compiler.OP.MARK_LOCATION, 'C'),
                          (compiler.OP.JUMP_ALWAYS, 'C'),
                          (compiler.OP.MARK_LOCATION, 'B'),
                          (compiler.OP.DISCARD, None),
                          (compiler.OP.END_PROGRAM, None),
                          (compiler.OP.MARK_LOCATION, 'A'),
                          (compiler.OP.STORE, None),
                          (compiler.OP.RETRIEVE, None),
                          (compiler.OP.COPY, 1),
                          (compiler.OP.COPY, 3),
                          (compiler.OP.MODULO, None),
                          (compiler.OP.INTEGER_DIVISION, None),
                          (compiler.OP.SWAP, None),
                          (compiler.OP.SUBTRACTION, None),
                          (compiler.OP.MULTIPLICATION, None),
                          (compiler.OP.ADDITION, None),
                          (compiler.OP.DUPLICATE, None),
                          (compiler.OP.JUMP_IF_NEGATIVE, 'D'),
                          (compiler.OP.JUMP_ALWAYS, 'C'),
                          (compiler.OP.MARK_LOCATION, 'E'),
                          (compiler.OP.SLIDE, 2),
                          (compiler.OP.END_SUBROUTINE, None)))
    Processor(code, interface.ProcessorInterface()).run()

################################################################################

if __name__ == '__main__':
    test()
