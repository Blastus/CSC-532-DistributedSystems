#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run a GUI application on top of the WS virtual machine.

This program is designed to run a virtual machine using a GUI for interaction.
It is primarily being included to check that safe_tkinter works properly while
on a Linux operating system. By this point, python3-tk is already installed."""

import datetime
import os
import sys
import threading
import time
import traceback

import compiler
import interface
import processor
import safe_tkinter
import threadbox

# Public Names
__all__ = (
    'Example',
    'TkinterIO'
)

# Module Documentation
__version__ = 2, 0, 0
__date__ = datetime.date(2022, 11, 23)
__author__ = 'Stephen Paul Chappell'
__credits__ = 'CSC-532'


class Example(safe_tkinter.Tk):
    """Provides an example of how to write a GUI application for a VM."""

    @classmethod
    def main(cls):
        """Runs the overlying code to get the GUI up and running."""
        root = cls.get_root()
        io = TkinterIO(root)
        filename = safe_tkinter.Open(
            root,
            filetypes=(('Program Files', '.ws'),
                       ('All Files', '*')),
            initialdir=os.path.dirname(sys.argv[0]),
            parent=root,
            title='Please select a program to run.'
        ).show()
        try:
            with open(filename) as file:
                source = file.read()
        except OSError:
            io.handle_error()
        else:
            root.title(os.path.basename(filename) + ' - ' + root.title())
            my_compiler = compiler.Compiler(compiler.Prototype.SYMBOLS)
            try:
                code = my_compiler.compile(source)
            except ValueError:
                io.handle_error()
            else:
                cpu = processor.Processor(code, io)
                try:
                    cpu.run()
                except (EOFError, KeyboardInterrupt):
                    io.handle_error()
        time.sleep(10)

    @classmethod
    def get_root(cls):
        """Starts the GUI root in another thread for testing purposes."""
        barrier = threading.Barrier(2)
        container = []
        thread = threading.Thread(
            target=cls.run_root,
            args=(barrier, container),
            daemon=True
        )
        thread.start()
        barrier.wait()
        return container[0]

    @classmethod
    def run_root(cls, barrier, container):
        """Executes the GUI mainloop in its own dedicated thread."""
        root = cls()
        container.append(root)
        barrier.wait()
        root.mainloop()

    def __init__(self):
        """Initializes a Tk root window and configures the geometry grid."""
        super().__init__()
        self.title(type(self).__name__)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)


class TkinterIO(interface.TkinterIO):
    """Adds some extra features not provided in the default implementation."""

    from tkinter.constants import NSEW

    def __init__(self, master):
        """Initialize the interface and add a tag specifically for errors."""
        super().__init__(master)
        self.tag_config('error', foreground='red')
        self.grid(sticky=self.NSEW)

    @threadbox.MetaBox.thread
    def handle_error(self, message=None):
        """Displays exception information in the window based on context."""
        if message is None:
            message = traceback.format_exc()
        self.mark_set(self.INSERT, self.END)
        prefix = '' if self.line_begin else '\n'
        self.insert(self.INSERT, prefix + message, 'error')


if __name__ == '__main__':
    Example.main()
