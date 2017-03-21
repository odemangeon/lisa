#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Lockable_dict module.

The objective of this package is to provides the class LockableDict

@ DONE:
    -
@TODO:
    -
"""
from logging import getLogger
from collections import MutableMapping, OrderedDict
from copy import copy


## logger object
logger = getLogger()

func_name_getinstance_lock = "get_Lock_instance"


class Lock(object):
    def __init__(self, value=False):
        self.__lock = value

    def lock(self):
        self.__lock = True

    def unlock(self):
        self.__lock = False

    def __str__(self):
        return str(self.__lock)

    # def __repr__(self):
    #     return str("Lock({})".format(self.__lock))

    def __call__(self):
        return self.__lock


class LockableAttr(object):
    """docstring for LockableAttr."""
    def __init__(self, lock=None):
        self.set_Lock_instance(lock=lock)

    @property
    def locked(self):
        return self.__lock()

    def set_Lock_instance(self, lock=None):
        if lock is None:
            self.__lock = Lock()
        elif isinstance(lock, Lock):
            self.__lock = lock
        else:
            raise ValueError("lock has to be a Lock instance.")

    def get_Lock_instance(self):
        return self.__lock

    def lock(self):
        self.__lock.lock()

    def unlock(self):
        self.__lock.unlock()


class LockableDict(MutableMapping, LockableAttr):
    def __init__(self, ordered=False, lock=None):
        LockableAttr.__init__(self, lock=lock)
        self.ordered = ordered
        if self.ordered:
            self.__data = OrderedDict()
        else:
            self.__data = dict()

    def __len__(self):
        return len(self.__data)

    def __iter__(self):
        return iter(self.__data)

    def __setitem__(self, key, value):
        if (key not in self.__data) and self.locked:
            raise KeyError("The key {} is not defined and the dictionnary is locked."
                           "".format(key))
        self.__data[key] = value

    def __delitem__(self, key):
        if self.locked:
            raise ValueError("The dictionnary is locked. It's not possible to pop a key.")
        else:
            del self.__data[key]

    def __getitem__(self, key):
        if key in self.__data:
            return self.__data[key]
        else:
            if hasattr(self, "__missing__"):
                return self.__missing__(key)
            else:
                raise KeyError(key)

    def __contains__(self, key):
        return key in self.__data

    def __str__(self):
        return str(self.__data)

    def get_data(self):
        return self.__data

    @property
    def ordered(self):
        return self.__ordered

    @ordered.setter
    def ordered(self, boolean):
        if isinstance(boolean, bool):
            self.__ordered = boolean
        else:
            raise ValueError("ordered has to be a boolean.")

    def __copy__(self):
        res = type(self)(ordered=self.ordered)
        res.update(self.__data)
        if self.locked:
            res.lock()
        return res

    def copy(self, lock=None):
        res = copy(self)
        if lock is not None:
            res.set_Lock_instance(lock)
        return res
