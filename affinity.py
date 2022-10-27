#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""Allow a simple way to ensure execution is confined to one thread.

This module defines the Affinity data type that runs code on a single thread.
An instance of the class will execute functions only on the thread that made
the object in the first place. The class is useful in a GUI's main loop."""

import _thread
import datetime
import inspect
import queue
import sys

# Public Names
__all__ = (
    'Affinity',
)

# Module Documentation
__version__ = 2, 0, 0
__date__ = datetime.date(2022, 10, 26)
__author__ = 'Stephen Paul Chappell'
__credits__ = 'CSC-532'


def _slots(names=''):
    """Sets __slots__ variable in the calling context with private names."""
    inspect.currentframe().f_back.f_locals['__slots__'] = \
        tuple(f'__{name}' for name in names.replace(',', ' ').split())


class Affinity:
    """Affinity() -> Affinity instance"""

    _slots('thread, action')

    def __init__(self):
        """Initializes instance with thread identity and job queue."""
        self.__thread = _thread.get_ident()
        self.__action = queue.Queue()

    def __call__(self, func, *args, **kwargs):
        """Executes function on creating thread and returns result."""
        if _thread.get_ident() == self.__thread:
            while not self.__action.empty():
                self.__action.get_nowait()()
            return func(*args, **kwargs)
        delegate = _Delegate(func, args, kwargs)
        self.__action.put_nowait(delegate)
        return delegate.value


class _Delegate:
    """_Delegate(func, args, kwargs) -> _Delegate instance"""

    _slots('func, args, kwargs, value, error, mutex')

    def __init__(self, func, args, kwargs):
        """Initializes instance from arguments and prepares to run."""
        self.__func = func
        self.__args = args
        self.__kwargs = kwargs
        self.__value = None
        self.__error = True
        self.__mutex = _thread.allocate_lock()
        self.__mutex.acquire()

    def __call__(self):
        """Executes code with arguments and allows value retrieval."""
        # noinspection PyBroadException
        try:
            self.__value = self.__func(*self.__args, **self.__kwargs)
            self.__error = False
        except BaseException:
            self.__value = sys.exc_info()[1]
        finally:
            self.__mutex.release()

    @property
    def value(self):
        """Waits for value availability and raises or returns data."""
        self.__mutex.acquire()
        if self.__error:
            raise self.__value
        return self.__value
