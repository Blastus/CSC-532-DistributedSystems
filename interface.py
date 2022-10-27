#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""Provide a flexible API for interfacing IO with a VM running WS.

This module has classes that define input/output interfaces along with
classes that provide several implementations of those interfaces. Well -
written classes may be used provide IO capabilities to virtual machines."""

import abc
import codecs
import datetime
import string

import threadbox

# Public Names
__all__ = (
    'main',
    'TerminalInterface',
    'ProcessorInterface',
    'FileIO',
    'SocketIO',
    'ConsoleIO',
    'CursesIO',
    'TkinterIO'
)

# Module Documentation
__version__ = 2, 0, 2
__date__ = datetime.date(2022, 10, 26)
__author__ = 'Stephen Paul Chappell'
__credits__ = 'CSC-532'


def main():
    """Tests some interface usage when integrated with a Processor instance."""
    import io
    import compiler
    import processor
    code = compiler.Code(((compiler.Op.PUSH, 2),
                          (compiler.Op.PUSH, 1),
                          (compiler.Op.COPY, 1),
                          (compiler.Op.COPY, 1),
                          (compiler.Op.READ_NUMBER, None),
                          (compiler.Op.READ_CHARACTER, None),
                          (compiler.Op.RETRIEVE, None),
                          (compiler.Op.OUTPUT_NUMBER, None),
                          (compiler.Op.RETRIEVE, None),
                          (compiler.Op.OUTPUT_CHARACTER, None),
                          (compiler.Op.END_PROGRAM, None)))
    print('Test 1 ...')
    stdin, stdout = map(io.StringIO, ('123\nA', None))
    processor.Processor(code, FileIO(stdin, stdout)).run()
    if stdout.getvalue() != '123\nA123A':
        raise ValueError('Processor did not produce the expected output!')
    print('Test 2 ...')
    stdin, stdout = map(io.StringIO, ('B4C5D6E\n\x1A', None))
    processor.Processor(code, FileIO(stdin, stdout)).run()
    if stdout.getvalue() != '456\n456\x1A':
        raise ValueError('Processor did not produce the expected output!')
    code = tuple(map(list, code))
    code[-1][0] = compiler.Op.READ_CHARACTER
    code = compiler.Code(code)
    print('Test 3 ...')
    stdin, stdout = map(io.StringIO, ('F7G8H9I\n\x1A', None))
    try:
        processor.Processor(code, FileIO(stdin, stdout)).run()
    except EOFError:
        if stdout.getvalue() != '789\n789\x1A':
            raise ValueError('Processor did not produce the expected output!')
    else:
        raise RuntimeError('An EOFError should have been raised!')
    print('Done')


class TerminalInterface(metaclass=abc.ABCMeta):
    """TerminalInterface() -> TerminalInterface instance"""

    EOF = '\x1A'

    def __init__(self):
        """Prevent this abstract class from being initialized."""
        pass

    def __bool__(self):
        """Check if the input buffer is currently holding any characters."""
        return self._kbhit()

    @threadbox.MetaBox.thread
    def read(self):
        """Retrieve an input buffer character."""
        return self.__check(self._getwch())

    @threadbox.MetaBox.thread
    def write(self, character):
        """Print the given character."""
        return self.__check(self._putwch(self.__check(character)))

    @staticmethod
    def __check(unicode_char):
        """Verify that the given character has the correct type and length."""
        if not isinstance(unicode_char, str):
            raise TypeError('unicode_char must be a str instance')
        if len(unicode_char) != 1:
            raise ValueError('unicode_char must be one in length')
        return unicode_char

    # noinspection SpellCheckingInspection
    @abc.abstractmethod
    def _kbhit(self):
        """Return True if a keypress is waiting to be read."""
        pass

    # noinspection SpellCheckingInspection
    @abc.abstractmethod
    def _getwch(self):
        """Wide char variant of getch(), returning a Unicode value."""
        pass

    # noinspection SpellCheckingInspection
    @abc.abstractmethod
    def _putwch(self, unicode_char):
        """Wide char variant of putch(), accepting a Unicode value."""
        pass


class ProcessorInterface(TerminalInterface):
    """ProcessorInterface() -> ProcessorInterface instance"""

    @abc.abstractmethod
    def __init__(self):
        """Initialize the ProcessorInterface to track its EOF status."""
        super().__init__()
        self.__streaming = True

    @threadbox.MetaBox.thread
    def read_number(self):
        """Read and return a number from the terminal interface."""
        if self.__streaming is True:
            self.__purge_stream()
            buffer = ''
            while True:
                char = self.read()
                if char == '\r' and buffer not in {'', '-', '+'}:
                    self.write('\n')
                    return int(buffer)
                if char == self.EOF:
                    self.__streaming = None
                    break
                if char in {'-', '+'} and not buffer or '0' <= char <= '9':
                    buffer += self.write(char)
                elif char == '\b' and buffer:
                    buffer = buffer[:-1]
                    self.__backspace()
        elif self.__streaming is False:
            raise EOFError()
        self.write('\n')
        return 0

    @threadbox.MetaBox.thread
    def read_character(self):
        """Read and return a character from the terminal interface."""
        if self.__streaming is True:
            self.__purge_stream()
            while True:
                char = self.read()
                if char in string.printable:
                    return self.write(char.replace('\r', '\n'))
                if char == self.EOF:
                    break
        elif self.__streaming is False:
            raise EOFError()
        self.__streaming = False
        return self.EOF

    def output_number(self, number):
        """Display a number using the terminal interface."""
        for digit in str(number):
            self.write(digit)

    def output_character(self, character):
        """Display a character using the terminal interface."""
        self.write(character)

    @threadbox.MetaBox.thread
    def __purge_stream(self):
        """Empty the input buffer of accumulated key presses."""
        while self:
            self.read()

    def __backspace(self):
        """Run the control sequence to erase the last character."""
        self.write('\b')
        self.write(' ')
        self.write('\b')


class FileIO(ProcessorInterface):
    """FileIO(stdin, stdout) -> FileIO instance"""

    def __init__(self, stdin, stdout):
        """Initialize the FileIO instance with standard in and out."""
        super().__init__()
        self.__stdin, self.__stdout = stdin, stdout

    # noinspection SpellCheckingInspection
    def _kbhit(self):
        """Return whether the input buffer is occupied."""
        return False

    # noinspection SpellCheckingInspection
    def _getwch(self):
        """Get the next character from the input buffer and return it."""
        unicode_char = self.__stdin.read(1).replace('\n', '\r')
        return unicode_char if unicode_char else self.EOF

    # noinspection SpellCheckingInspection
    def _putwch(self, unicode_char):
        """Display the character on the proper underlying channel."""
        self.__stdout.write(unicode_char)
        return unicode_char


class SocketIO(FileIO):
    """SocketIO(socket, encoding='utf-8', errors='strict')
    -> SocketIO instance"""

    def __init__(self, socket, encoding='utf-8', errors='strict'):
        """Initialize the SocketIO instance with a socket-based file."""
        info = codecs.lookup(encoding)
        file = codecs.StreamReaderWriter(socket.makefile('rwb', False),
                                         info.streamreader,
                                         info.streamwriter,
                                         errors)
        super().__init__(file, file)


try:
    import msvcrt
except ImportError:
    msvcrt = None
    ConsoleIO = None
else:
    class ConsoleIO(ProcessorInterface):
        """ConsoleIO() -> ConsoleIO instance"""

        def __init__(self):
            """Initialize an instance to show that this is not abstract."""
            super().__init__()

        # noinspection SpellCheckingInspection
        def _kbhit(self):
            """Return true if a keypress is waiting to be read."""
            return bool(msvcrt.kbhit())

        # noinspection SpellCheckingInspection
        def _getwch(self):
            """Read a keypress and return the resulting character."""
            while True:
                unicode_char = msvcrt.getwch()
                if unicode_char in {'\x00', '\xE0'}:
                    msvcrt.getwch()
                    continue
                return unicode_char

        # noinspection SpellCheckingInspection
        def _putwch(self, unicode_char):
            """Print the character to the console without buffering."""
            msvcrt.putwch(unicode_char)
            return unicode_char

try:
    import curses
except ImportError:
    curses = None
    CursesIO = None
else:
    import warnings


    class CursesIO(ProcessorInterface):
        """CursesIO() -> CursesIO instance"""

        def __init__(self):
            """Initialize the CursesIO instance with a screen for IO."""
            warnings.warn('CursesIO is untested and will likely fail!')
            super().__init__()
            self.__std_scr = curses.initscr()
            curses.cbreak()
            curses.noecho()
            self.__std_scr.keypad(True)

        def __del__(self):
            """Close the screen and reset the terminal's settings."""
            self.__std_scr.keypad(False)
            curses.echo()
            curses.nocbreak()
            curses.endwin()

        # noinspection SpellCheckingInspection
        def _kbhit(self):
            """Check if the input buffer has any characters waiting in it."""
            self.__std_scr.nodelay(True)
            ch = self.__std_scr.getch()
            self.__std_scr.nodelay(False)
            curses.ungetch(ch)
            return ch != -1

        # noinspection SpellCheckingInspection
        def _getwch(self):
            """Get a character code from the input buffer and convert it."""
            return chr(self.__std_scr.getch())

        # noinspection SpellCheckingInspection
        def _putwch(self, unicode_char):
            """Print a character to the screen and update the display."""
            self.__std_scr.addstr(unicode_char)
            self.__std_scr.refresh()
            return unicode_char

try:
    import safe_tkinter
except ImportError:
    safe_tkinter = None
else:
    import queue


    class TkinterIO(safe_tkinter.Text, ProcessorInterface):
        """TkinterIO(master, cnf={}, **kw) -> TkinterIO instance"""

        from tkinter.constants import END, INSERT
        DEFAULT = object()
        CURSOR = 'cursor'
        INSERT_1C = INSERT + '-1c'

        def __init__(self, master, cnf=DEFAULT, **kw):
            """Initialize the TkinterIO instance to act like a terminal."""
            if cnf is self.DEFAULT:
                cnf = {}
            # noinspection PyArgumentList
            super().__init__(master, cnf, **kw)
            ProcessorInterface.__init__(self)
            self.__buffer = queue.Queue()
            self.__events = queue.Queue()
            self.bind('<Key>', self.__handle_key)
            self.bind('<Button>', self.__handle_button)
            self.bind('<Control-c>', self.__handle_keyboard_interrupt)
            self.bind('<Control-C>', self.__handle_keyboard_interrupt)
            self.mark_set(self.CURSOR, self.END)

        def destroy(self):
            """Destroy this and all descendant widgets."""
            self.__signal(SystemExit)
            # noinspection PyUnresolvedReferences
            super().destroy()

        def __handle_key(self, event):
            """Place text-based key events in the input buffer."""
            if event.char:
                self.__buffer.put(event.char)
            return 'break'

        # noinspection PyUnusedLocal
        def __handle_button(self, event):
            """Get focus for this widget when someone clicks on it."""
            self.focus_set()
            return 'break'

        # noinspection PyUnusedLocal
        def __handle_keyboard_interrupt(self, event):
            """Signal that a keyboard interrupt event has occurred."""
            self.__signal(KeyboardInterrupt)
            return 'break'

        def __signal(self, event):
            """Record an event in the buffer and post end-of-file."""
            self.__events.put(event)
            self.__buffer.put(self.EOF)

        @threadbox.MetaBox.thread
        def __handle_events(self):
            """Try to raise any events that may have occurred."""
            try:
                event = self.__events.get_nowait()
            except queue.Empty:
                pass
            else:
                raise event()

        # noinspection SpellCheckingInspection
        @threadbox.MetaBox.thread
        def _kbhit(self):
            """Check on whether the input buffer has data."""
            self.__handle_events()
            return not self.__buffer.empty()

        # noinspection SpellCheckingInspection
        @threadbox.MetaBox.thread
        def _getwch(self):
            """Wait on the input buffer for data and return it."""
            self.__handle_events()
            return self.__buffer.get()

        # noinspection SpellCheckingInspection
        def _putwch(self, unicode_char):
            """Display a character while running in the GUI thread."""
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
            """Beginning-of-line flag property."""
            return self.get(self.INSERT_1C) == '\n'

        @property
        def buffer_end(self):
            """Ending-of-buffer flag property."""
            return self.get(self.INSERT, self.END) == '\n'


if __name__ == '__main__':
    main()
