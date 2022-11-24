#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""Register tkinter classes with threadbox for immediate usage.

This module clones several classes from the tkinter library for use with
threads. Instances from these new classes should run on whatever thread
the root was created on. Child classes inherit the parent's safety."""

import datetime
import time
import tkinter.filedialog
import tkinter.font
import tkinter.messagebox
import tkinter.scrolledtext
import tkinter.ttk

import _tkinter

import threadbox

# Public Names
__all__ = (
    'mainloop',
    'Canvas',
    'Listbox',
    'Menu',
    'PhotoImage',
    'Spinbox',
    'Text',
    'Tk',
    'Toplevel',
    'OldButton',
    'OldFrame',
    'BooleanVar',
    'DoubleVar',
    'IntVar',
    'StringVar',
    'Button',
    'Checkbutton',
    'Entry',
    'Frame',
    'Label',
    'Labelframe',
    'Progressbar',
    'Radiobutton',
    'Scale',
    'Scrollbar',
    'Sizegrip',
    'Treeview',
    'Directory',
    'Font',
    'Message',
    'Open',
    'ScrolledText'
)

# Module Documentation
__version__ = 2, 0, 0
__date__ = datetime.date(2022, 11, 23)
__author__ = 'Stephen Paul Chappell'
__credits__ = 'CSC-532'

tkinter.NoDefaultRoot()


@threadbox.MetaBox.thread
def mainloop(self):
    """Creates a synthetic main loop so that threads can still run."""
    while True:
        try:
            self.update()
        except tkinter.TclError:
            break
        else:
            time.sleep(_tkinter.getbusywaitinterval() / 1000)


threadbox.MetaBox.clone(tkinter.Misc, {'mainloop': mainloop})

# Widget Classes From tkinter
Canvas = threadbox.MetaBox.clone(tkinter.Canvas)
Listbox = threadbox.MetaBox.clone(tkinter.Listbox)
Menu = threadbox.MetaBox.clone(tkinter.Menu)
PhotoImage = threadbox.MetaBox.clone(tkinter.PhotoImage)
Spinbox = threadbox.MetaBox.clone(tkinter.Spinbox)
Text = threadbox.MetaBox.clone(tkinter.Text)
Tk = threadbox.MetaBox.clone(tkinter.Tk)
Toplevel = threadbox.MetaBox.clone(tkinter.Toplevel)
OldButton = threadbox.MetaBox.clone(tkinter.Button)
OldFrame = threadbox.MetaBox.clone(tkinter.Frame)

# Variable Classes From tkinter
BooleanVar = threadbox.MetaBox.clone(tkinter.BooleanVar)
DoubleVar = threadbox.MetaBox.clone(tkinter.DoubleVar)
IntVar = threadbox.MetaBox.clone(tkinter.IntVar)
StringVar = threadbox.MetaBox.clone(tkinter.StringVar)

# Widget Classes From ttk
Button = threadbox.MetaBox.clone(tkinter.ttk.Button)
Checkbutton = threadbox.MetaBox.clone(tkinter.ttk.Checkbutton)
Entry = threadbox.MetaBox.clone(tkinter.ttk.Entry)
Frame = threadbox.MetaBox.clone(tkinter.ttk.Frame)
Label = threadbox.MetaBox.clone(tkinter.ttk.Label)
Labelframe = threadbox.MetaBox.clone(tkinter.ttk.Labelframe)
Progressbar = threadbox.MetaBox.clone(tkinter.ttk.Progressbar)
Radiobutton = threadbox.MetaBox.clone(tkinter.ttk.Radiobutton)
Scale = threadbox.MetaBox.clone(tkinter.ttk.Scale)
Scrollbar = threadbox.MetaBox.clone(tkinter.ttk.Scrollbar)
Sizegrip = threadbox.MetaBox.clone(tkinter.ttk.Sizegrip)
Treeview = threadbox.MetaBox.clone(tkinter.ttk.Treeview)

# Miscellaneous Classes From tkinter
Directory = threadbox.MetaBox.clone(tkinter.filedialog.Directory)
Font = threadbox.MetaBox.clone(tkinter.font.Font)
Message = threadbox.MetaBox.clone(tkinter.messagebox.Message)
Open = threadbox.MetaBox.clone(tkinter.filedialog.Open)
ScrolledText = threadbox.MetaBox.clone(tkinter.scrolledtext.ScrolledText)
