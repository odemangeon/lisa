#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
database_func module.

The objective of this module is to define the class DatabaseFunc.

@DONE:
    -

@TODO:
    -
"""
from logging import getLogger

from .instmodel4dataset import Instmodel4DatasetAttr
from .database_instlevelsanddataset import DstDbLockAttr, DatabaseInstLvlDataset
from ...tools.name import Named
from ...tools.lockable_dict import LockableDict
# from ...tools.miscellaneous import interpret_data_filename


## logger object
logger = getLogger()


class DatabaseFunc(Named, Instmodel4DatasetAttr, DstDbLockAttr):
    """docstring for DatabaseFunc.

    """

    _alldtst_key = "all"

    def __init__(self, object_stored, database_name, instmodel4dataset=None, list_datasetnames=None,
                 instordered=False, use_samelock=False, lock_dataset=None, lock_database=None):
        """Initialise the DatabaseFunc instance.

        TODO:
        """
        # Initialise the Name attributes.
        Named.__init__(self, name=object_stored, prefix=database_name)
        # Set the instordered
        self.__instordered = instordered
        # Initialise the locks
        DstDbLockAttr.__init__(self, use_samelock=use_samelock, lock_dataset=lock_dataset,
                               lock_database=lock_database)
        # Initialise the Instmodel4Dataset
        Instmodel4DatasetAttr.__init__(self, instmodel4dataset=instmodel4dataset,
                                       list_datasetnames=list_datasetnames,
                                       lock=self.get_dataset_Lock_instance())
        # Initialise the instrument_db attribute with the above instmodel4dataset if exist or without
        # instmodel4dataset if not.
        self.__instrument_db = DatabaseInstLvlDataset(object_stored=self.object_stored,
                                                      database_name=self.database_name,
                                                      instmodel4dataset=self.instmodel4dataset,
                                                      ordered=self.instordered,
                                                      use_samelock=self.samelock,
                                                      lock_dataset=self.get_dataset_Lock_instance(),
                                                      lock_database=(self.
                                                                     get_database_Lock_instance()))
        # Initialise the dataset_db attribute as a LockableDict with the lock_dataset defined above.
        # Add an _alldtst_key key with value None for the func including all datasets and key for
        # datasets in instmodel4dataset
        self.dataset_db = LockableDict(lock=self.get_dataset_Lock_instance())
        self.dataset_db[self._alldtst_key] = None
        self.__update_datasets_dataset_db()

    @property
    def database_name(self):
        """Return the name of the database."""
        return self.name.prefix.get(include_prefix=False, code_version=False)

    @property
    def object_stored(self):
        """Return the name of the objects stored in the database."""
        return self.name.get(include_prefix=False, code_version=False)

    @property
    def instordered(self):
        """Return the boolean instordered values."""
        return self.__instordered

    @property
    def instrument_db(self):
        """Return the instrument_db."""
        return self.__instrument_db

    @property
    def dataset_db(self):
        """Return the dataset_db."""
        return self.__dataset_db

    @dataset_db.setter
    def dataset_db(self, db):
        """Set the dataset_db property.

        :param LockableDict db: LockableDict used as container for the dataset database.
        """
        if db is None:
            logger.debug("No dataset database provided for instance {} of class {}."
                         "".format(self.name, self.__class__.__name__))
        else:
            if isinstance(db, LockableDict):
                logger.debug("The dataset database of instance {} of class {} set to {}."
                             "".format(self.name, self.__class__.__name__, db))
                # TODO: Check that dataset_db has the good lock.
                self.__dataset_db = db
            else:
                raise ValueError("db should be a LockableDict instance")

    @property
    def list_datasets_in_datasetdb(self):
        """Return the list of dataset names currently in dataset_db."""
        return list(self.dataset_db.keys())

    def __update_datasets_dataset_db(self):
        """Update datasets in dataset_db.

        1a. Get datasetnames that are in instmodel4dataset but not currently in
             dataset_db
        1b. Add them to dataset_db and initialize them to None
        2a. Get datasetnames that are in dataset_db but not in instmodel4dataset
        2b. Delete them from dataset_db
        """
        set_new = set(self.instmodel4dataset.list_datasets)
        set_old = set(self.list_datasets_in_datasetdb)
        set_old.remove(self._alldtst_key)
        set_add = set_new - set_old  # 1a
        set_delete = set_old - set_new  # 2a
        logger.debug("Datasets to add to dataset_db: {}\nDatasets to delete: {}"
                     "".format(set_add, set_delete))
        for dataset_name in set_add:
            self.dataset_db[dataset_name] = None  # 1b
        for dataset_name in set_delete:
            self.dataset_db.pop(dataset_name)  # 2b

    def update_datasets(self, list_datasetnames=None):
        """Update the datasets in the DatabaseFunc instance (instrument_db and dataset_db).

        1. Update the datasets in the instrument_db
        2. Update the instruments in the dataset_db
        """
        if list_datasetnames is not None:
            self.update_datasets_instmodel4dataset(list_datasetnames)  # 1.
        self.__update_datasets_dataset_db()  # 2.
