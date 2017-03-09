#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
dataset_database_locks module.

The objective of this package is to provides the class

@ DONE:
    -
@TODO:
    -
"""
from logging import getLogger

from ...tools.lockable_dict import LockableAttr, Lock

## logger object
logger = getLogger()


def check_lockargs(use_samelock=True, lock_dataset=None, lock_database=None):
    if use_samelock:
        if (lock_dataset is None) and (lock_database is None):
            lock_dataset = lock_database = Lock()
        elif (lock_dataset is None):
            lock_dataset = lock_database
        elif (lock_database is None):
            lock_database = lock_dataset
        else:
            if lock_dataset is not lock_database:
                raise ValueError("If you want to you the same lock the lock_database and "
                                 "lock_dataset argument should be identical or one of them "
                                 "None.")
    return lock_dataset, lock_database


class DstDbLockAttr(LockableAttr):
    """docstring for DstDbLockAttr."""

    __err_msg = ("{} is not accessible when you are not using the same "
                 "Lock for instmodel4dataset and DatabaseInstLevel")

    def __init__(self, lock_dataset=None, lock_database=None, use_samelock=False):
        self.__samelock = use_samelock
        lock_dataset, lock_database = check_lockargs(use_samelock=self.samelock,
                                                     lock_dataset=lock_dataset,
                                                     lock_database=lock_database)
        super(DstDbLockAttr, self).__init__(lock=lock_dataset)
        self.set_database_Lock_instance(lock=lock_database)

    @property
    def samelock(self):
        """Returns True if the same Lock must be used for instmodel4dataset and DatabaseInstLevel.
        """
        return self.__samelock

    @property
    def locked(self):
        if self.samelock:
            return super(DstDbLockAttr, self).locked
        else:
            raise ValueError(self.__err_msg.format("locked property"))

    @property
    def dataset_locked(self):
        return super(DstDbLockAttr, self).lock()

    @property
    def database_locked(self):
        return self.__db_lock()

    def set_dataset_Lock_instance(self, lock=None):
        super(DstDbLockAttr, self).__init__(lock=lock)

    def set_database_Lock_instance(self, lock=None):
        if lock is None:
            self.__db_lock = Lock()
        elif isinstance(lock, Lock):
            self.__db_lock = lock
        else:
            raise ValueError("lock has to be a Lock instance.")

    def get_Lock_instance(self):
        if self.samelock:
            return super(DstDbLockAttr, self).get_Lock_instance()
        else:
            raise ValueError(self.__err_msg.format("get_Lock_instance method"))

    def get_dataset_Lock_instance(self):
        return super(DstDbLockAttr, self).get_Lock_instance()

    def get_database_Lock_instance(self):
        return self.__db_lock

    def lock(self):
        if self.samelock:
            self.lock_database()
        else:
            raise ValueError(self.__err_msg.format("lock method"))

    def unlock(self):
        if self.samelock:
            self.unlock_database()
        else:
            raise ValueError(self.__err_msg.format("unlock method"))

    def dataset_lock(self):
        super(DstDbLockAttr, self).lock()

    def dataset_unlock(self):
        super(DstDbLockAttr, self).unlock()

    def database_lock(self):
        self.__db_lock.lock()

    def database_unlock(self):
        self.__db_lock.unlock()
