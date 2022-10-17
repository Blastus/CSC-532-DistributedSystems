#! /usr/bin/env python3
"""Provide a flexible API for interfacing IO with a VM running WS.

This module has classes that define input/output interfaces along with
classes that provide several implementations of those interfaces. Well-
written classes may be used provide IO capabilities to virtual machines."""

__author__ = 'Stephen "Zero" Chappell <Noctis.Skytower@gmail.com>'
__date__ = '16 September 2013'
__version__ = 2, 0, 0

################################################################################

import codecs
import collections
import string
import threadbox

################################################################################

##class ChainIO(ChannelInterface):
##
##    def __init__(self, *channels):
##        self.__channels = collections.deque(channels)
##
##    def read_number(self):
##        while self.__channels:
##            try:
##                return self.__channels[0].read_number()
##            except EOFError:
##                self.__channels.popleft()
##        return 0
##
##    def read_character(self):
##        while self.__channels:
##            try:
##                return self.__channels[0].read_character()
##            except EOFError:
##                self.__channels.popleft()
##        return self.EOF
##
##    def output_number(self, number):
##        if self.__channels:
##            self.__channels[0].output_number(number)
##
##    def output_character(self, character):
##        if self.__channels:
##            self.__channels[0].output_character(character)

class ProcessorInterface:

    "ProcessorInterface() -> ProcessorInterface instance"

    def __init__(self):
        "Initialize the ProcessorInterface to track its EOF status."
        self.__streaming = True

    @threadbox.MetaBox.thread
    def read_number(self):
        "Read and return a number from the terminal interface."
        if self.__streaming is True:
            self.__purge_stream()
            buffer = ''
            while True:
                char = self()
                if char == '\r' and buffer not in {'', '-', '+'}:
                    self('\n')
                    return int(buffer)
                if char == self.EOF:
                    self.__streaming = None
                    break
                if char in {'-', '+'} and not buffer or '0' <= char <= '9':
                    buffer += self(char)
                elif char == '\b' and buffer:
                    buffer = buffer[:-1]
                    self.__backspace()
        elif self.__streaming is False:
            raise EOFError()
        self('\n')
        return 0

    @threadbox.MetaBox.thread
    def read_character(self):
        "Read and return a character from the terminal interface."
        if self.__streaming is True:
            self.__purge_stream()
            while True:
                char = self()
                if char in string.printable:
                    return self(char.replace('\r', '\n'))
                if char == self.EOF:
                    break
        elif self.__streaming is False:
            raise EOFError()
        self.__streaming = False
        return self.EOF

    def output_number(self, number):
        "Display a number using the terminal interface."
        for digit in str(number):
            self(digit)

    def output_character(self, character):
        "Display a character using the terminal interface."
        self(character)

    @threadbox.MetaBox.thread
    def __purge_stream(self):
        "Empty the input buffer of accumulated key presses."
        while self:
            self()

    def __backspace(self):
        "Run the control sequence to erase the last character."
        self('\b')
        self(' ')
        self('\b')

################################################################################

class TerminalInterface:

    "TerminalInterface() -> TerminalInterface instance"

    def __bool__(self):
        "Check if the input buffer is currently holding any characters."
        return self._kbhit()

    @threadbox.MetaBox.thread
    def __call__(self, *args):
        "Retrieve an input buffer character or print the given character."
        if len(args) > 1:
            raise TypeError('Please call with one or zero arguments!')
        return self.__check(self._putwch(self.__check(args[0]))
                            if args else self._getwch())

    @staticmethod
    def __check(unicode_char):
        "Verify that the given character has the correct type and length."
        if not isinstance(unicode_char, str):
            raise TypeError('unicode_char must be a str instance')
        if len(unicode_char) != 1:
            raise ValueError('unicode_char must be one in length')
        return unicode_char

    def _kbhit(self):
        "Indicate that this method needs to be implemented."
        raise NotImplementedError('This is an abstract method!')

    def _getwch(self):
        "Indicate that this method needs to be implemented."
        raise NotImplementedError('This is an abstract method!')

    def _putwch(self, unicode_char):
        "Indicate that this method needs to be implemented."
        raise NotImplementedError('This is an abstract method!')

################################################################################

class ChannelInterface(TerminalInterface, ProcessorInterface):

    "ChannelInterface() -> ChannelInterface instance"

    EOF = '\x1A'

################################################################################

class FileIO(ChannelInterface):

    "FileIO(stdin, stdout) -> FileIO instance"

    def __init__(self, stdin, stdout):
        "Initialize the FileIO instance with standard in and out."
        super().__init__()
        self.__stdin, self.__stdout = stdin, stdout

    def _kbhit(self):
        "Return whether or not the input buffer is occupied."
        return False

    def _getwch(self):
        "Get the next character from the input buffer and return it."
        unicode_char = self.__stdin.read(1).replace('\n', '\r')
        return unicode_char if unicode_char else self.EOF

    def _putwch(self, unicode_char):
        "Display the character on the proper underlying channel."
        self.__stdout.write(unicode_char)
        return unicode_char

################################################################################

class SocketIO(FileIO):

    "SocketIO(socket, encoding='utf-8', errors='strict') -> SocketIO instance"

    def __init__(self, socket, encoding='utf-8', errors='strict'):
        "Initialize the SocketIO instance with a socket-based file."
        info = codecs.lookup(encoding)
        file = codecs.StreamReaderWriter(socket.makefile('rwb', False),
                                         info.streamreader,
                                         info.streamwriter,
                                         errors)
        super().__init__(file, file)

################################################################################

try:
    import msvcrt
except ImportError:
    pass
else:
    class ConsoleIO(ChannelInterface):

        "ConsoleIO() -> ConsoleIO instance"

        def _kbhit(self):
            "Return true if a keypress is waiting to be read."
            return bool(msvcrt.kbhit())

        def _getwch(self):
            "Read a keypress and return the resulting character."
            while True:
                unicode_char = msvcrt.getwch()
                if unicode_char in {'\x00', '\xE0'}:
                    msvcrt.getwch()
                    continue
                return unicode_char

        def _putwch(self, unicode_char):
            "Print the character to the console without buffering."
            msvcrt.putwch(unicode_char)
            return unicode_char

################################################################################

try:
    import curses
    import warnings
except ImportError:
    pass
else:
    class CursesIO(ChannelInterface):

        "CursesIO() -> CursesIO instance"

        def __init__(self):
            "Initialize the CursesIO instance with a screen for IO."
            warnings.warn('CursesIO is untested and will likely fail!')
            super().__init__()
            self.__stdscr = curses.initscr()
            curses.cbreak()
            curses.noecho()
            self.__stdscr.keypad(1)

        def __del__(self):
            "Close the screen and reset the terminal's settings."
            self.__stdscr.keypad(0)
            curses.echo()
            curses.nocbreak()
            curses.endwin()

        def _kbhit(self):
            "Check if the input buffer has any characters waiting in it."
            self.__stdscr.nodelay(1)
            ch = self.__stdscr.getch()
            self.__stdscr.nodelay(0)
            curses.ungetch(ch)
            return ch != -1

        def _getwch(self):
            "Get a character code from the input buffer and convert it."
            return chr(self.__stdscr.getch())

        def _putwch(self, unicode_char):
            "Print a character to the screen and update the display."
            self.__stdscr.addstr(unicode_char)
            self.__stdscr.refresh()
            return unicode_char

################################################################################

try:
    import queue
    import safetkinter
except ImportError:
    pass
else:
    class TkinterIO(safetkinter.Text, ChannelInterface):

        "TkinterIO(master, cnf={}, **kw) -> TkinterIO instance"

        from tkinter.constants import END, INSERT
        CURSOR = 'cursor'
        INSERT_1C = INSERT + '-1c'

        def __init__(self, master, cnf={}, **kw):
            "Initialize the TkinterIO instance to act like a terminal."
            super().__init__(master, cnf, **kw)
            ChannelInterface.__init__(self)
            self.__buffer = queue.Queue()
            self.__events = queue.Queue()
            self.bind('<Key>', self.__handle_key)
            self.bind('<Button>', self.__handle_button)
            self.bind('<Control-c>', self.__handle_keyboard_interrupt)
            self.bind('<Control-C>', self.__handle_keyboard_interrupt)
            self.mark_set(self.CURSOR, self.END)

        def destroy(self):
            "Destroy this and all descendant widgets."
            self.__signal(SystemExit)
            super().destroy()

        def __handle_key(self, event):
            "Place text-based key events in the input buffer."
            if event.char:
                self.__buffer.put(event.char)
            return 'break'

        def __handle_button(self, event):
            "Get focus for this widget when someone clicks on it."
            self.focus_set()
            return 'break'

        def __handle_keyboard_interrupt(self, event):
            "Signal that a keyboard interrupt event has occurred."
            self.__signal(KeyboardInterrupt)
            return 'break'

        def __signal(self, event):
            "Record an event in the buffer and post end-of-file."
            self.__events.put(event)
            self.__buffer.put(self.EOF)

        @threadbox.MetaBox.thread
        def __handle_events(self):
            "Try to raise any events that may have occurred."
            try:
                event = self.__events.get_nowait()
            except queue.Empty:
                pass
            else:
                raise event()

        @threadbox.MetaBox.thread
        def _kbhit(self):
            "Check on whether or not the input buffer has data."
            self.__handle_events()
            return not self.__buffer.empty()

        @threadbox.MetaBox.thread
        def _getwch(self):
            "Wait on the input buffer for data and return it."
            self.__handle_events()
            return self.__buffer.get()

        def _putwch(self, unicode_char):
            "Display a character while running in the GUI thread."
            self.__handle_events()
            self.mark_set(self.INSERT, self.CURSOR)
            if unicode_char != '\b':
                if not self.line_begin or not self.buffer_end:
                    self.delete(self.INSERT)
                self.insert(self.INSERT, unicode_char)
            elif not self.line_begin:
                self.mark_set(self.INSERT, self.INSERT_1C)
            self.see(self.INSERT)
            self.mark_set(self.CURSOR, self.INSERT)
            return unicode_char

        @property
        def line_begin(self):
            "Beginning-of-line flag property."
            return self.get(self.INSERT_1C) == '\n'

        @property
        def buffer_end(self):
            "Ending-of-buffer flag property."
            return self.get(self.INSERT, self.END) == '\n'

################################################################################

def test():
    import io
    import compiler
    import processor
    code = compiler.Code(((compiler.OP.PUSH, 2),
                          (compiler.OP.PUSH, 1),
                          (compiler.OP.COPY, 1),
                          (compiler.OP.COPY, 1),
                          (compiler.OP.READ_NUMBER, None),
                          (compiler.OP.READ_CHARACTER, None),
                          (compiler.OP.RETRIEVE, None),
                          (compiler.OP.OUTPUT_NUMBER, None),
                          (compiler.OP.RETRIEVE, None),
                          (compiler.OP.OUTPUT_CHARACTER, None),
                          (compiler.OP.END_PROGRAM, None)))
    stdin, stdout = map(io.StringIO, ('123\nA', None))
    processor.Processor(code, FileIO(stdin, stdout)).run()
    if stdout.getvalue() != '123\nA123A':
        raise ValueError('Processor did not produce the expected output!')
    stdin, stdout = map(io.StringIO, ('B4C5D6E\n\x1A', None))
    processor.Processor(code, FileIO(stdin, stdout)).run()
    if stdout.getvalue() != '456\n456\x1A':
        raise ValueError('Processor did not produce the expected output!')
    code = tuple(map(list, code))
    code[-1][0] = compiler.OP.READ_CHARACTER
    code = compiler.Code(code)
    stdin, stdout = map(io.StringIO, ('F7G8H9I\n\x1A', None))
    try:
        processor.Processor(code, FileIO(stdin, stdout)).run()
    except EOFError:
        if stdout.getvalue() != '789\n789\x1A':
            raise ValueError('Processor did not produce the expected output!')
    else:
        raise RuntimeError('An EOFError should have been raised!')

################################################################################

if __name__ == '__main__':
    test()
