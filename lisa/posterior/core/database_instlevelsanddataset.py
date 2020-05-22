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

from .dataset_and_instrument.dataset import Core_Dataset
from .instmodel4dataset import Instmodel4DatasetAttr
from ...tools.lockable_dict import LockableAttr, Lock
from ...tools.database_with_instrument_level import DatabaseInstLevel
# from ...tools.miscellaneous import interpret_data_filename


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


class DatabaseInstLvlDataset(DatabaseInstLevel, Instmodel4DatasetAttr, DstDbLockAttr):
    """docstring for DatabaseInstLvlDataset.

    This class is database, sublass of DatabaseInstLevel (lockable nested dictionnary database with
    levels: inst_cat, inst_name, inst_model), associated with a Instmodel4Dataset attribute that
    allows to access convert the dataset_name into a instrument model name and access the
    corresponding value in the database. There can be two different locks for the database and the
    Instmodel4Dataset attribute.
    """

    def __init__(self, object_stored, database_name, instmodel4dataset=None, list_datasetnames=None,
                 ordered=False, use_samelock=False, lock_dataset=None, lock_database=None,
                 default={"all": None}):
        """doctstring of DatabaseInstLvlDataset __init__ method."""
        DstDbLockAttr.__init__(self, use_samelock=use_samelock, lock_dataset=lock_dataset,
                               lock_database=lock_database)
        Instmodel4DatasetAttr.__init__(self, instmodel4dataset=instmodel4dataset,
                                       list_datasetnames=list_datasetnames,
                                       lock=self.get_dataset_Lock_instance())
        DatabaseInstLevel.__init__(self, object_stored=object_stored,
                                   database_name=database_name, ordered=ordered,
                                   lock=self.get_database_Lock_instance(), default=default)

    def __getitem__(self, key):
        if key in self.instmodel4dataset:
            inst_model = self.instmodel4dataset[key]
            dataset_info = Core_Dataset.interpret_data_filename(key)
            instmodel_fullname = "{}_{}".format(dataset_info["inst_name"], inst_model)
            return self[instmodel_fullname]
        else:
            return super(DatabaseInstLvlDataset, self).__getitem__(key)

    @property
    def locked(self):  # Allow the __setitem__ method of Lockabledict to know use self.locked
        return self.database_locked

    def get_Lock_instance(self):  # Allow the __missing__ method of dico_database to know use
        return self.get_database_Lock_instance()  # self.get_Lock_instance
