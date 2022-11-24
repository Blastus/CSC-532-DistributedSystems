#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""Provide a way to run instance methods on a single thread.

This module allows hierarchical classes to be cloned so that their instances
run on one thread. Method calls are automatically routed through a special
execution engine. This is helpful when building thread-safe GUI code."""

import abc
import datetime
import functools

import affinity

# Public Names
__all__ = (
    'MetaBox',
)

# Module Documentation
__version__ = 2, 0, 0
__date__ = datetime.date(2022, 11, 23)
__author__ = 'Stephen Paul Chappell'
__credits__ = 'CSC-532'


class _Object:
    __slots__ = '_MetaBox__exec', '__dict__'


# Symbolic Constants
_META_BOX_REGISTRY = {object: _Object}
_META_BOX_SENTINEL = object()


class MetaBox(abc.ABCMeta):
    """MetaBox(name, bases, namespace, old=None) -> MetaBox instance"""

    @classmethod
    def clone(mcs, old, new=None):
        """Creates a class preferring thread affinity after update."""
        return mcs(old.__name__, old.__bases__, vars(old) | (new or {}), old)

    @classmethod
    def thread(mcs, func):
        """Marks a function to be completely threaded when running."""
        func.__thread = _META_BOX_SENTINEL
        return func

    def __new__(mcs, name, bases, namespace, old=None):
        """Allocates space for a new class after altering its data."""
        for test in _deny('__new__'), _deny('__slots__'), _need('__module__'):
            test(namespace)
        valid = []
        for base in bases:
            if base in _META_BOX_REGISTRY:
                valid.append(_META_BOX_REGISTRY[base])
            elif base in _META_BOX_REGISTRY.values():
                valid.append(base)
            else:
                valid.append(mcs.clone(base))
        for key, value in namespace.items():
            if callable(value):
                flag = getattr(value, '_MetaBox__thread', None)
                if flag is not _META_BOX_SENTINEL:
                    namespace[key] = mcs.__wrap(value)
        namespace.update({
            '__new__': mcs.__new,
            '__slots__': (),
            '__module__': f'{__name__}.{namespace["__module__"]}'
        })
        new = super().__new__(mcs, name, tuple(valid), namespace)
        # noinspection PyTypeChecker
        _META_BOX_REGISTRY[object() if old is None else old] = new
        return new

    # noinspection PyUnusedLocal
    def __init__(cls, name, bases, namespace, old=None):
        """Initializes class instance while ignoring the old class."""
        super().__init__(name, bases, namespace)

    @staticmethod
    def __wrap(func):
        """Wraps a method so execution runs via an affinity engine."""

        @functools.wraps(func)
        def box(self, *args, **kwargs):
            return self.__exec(func, self, *args, **kwargs)

        return box

    @classmethod
    def __new(mcs, cls, *args, **kwargs):
        """Allocates space for instance and finds __exec attribute."""
        self = object.__new__(cls)
        if 'master' in kwargs:
            self.__exec = kwargs['master'].__exec
        else:
            valid = tuple(_META_BOX_REGISTRY.values())
            for value in args:
                if isinstance(value, valid):
                    self.__exec = value.__exec
                    break
            else:
                self.__exec = affinity.Affinity()
        return self


def _need(name):
    """Creates a test that states the need for a name in a dictionary."""

    def test(dictionary):
        if name not in dictionary:
            raise RuntimeError(f'{name} must be defined')

    return test


def _deny(name):
    """Creates a test that states a name must not be in a dictionary."""

    def test(dictionary):
        if name in dictionary:
            raise RuntimeError(f'{name} must not be defined')

    return test
