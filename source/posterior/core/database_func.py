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
from .dataset_database_locks import DstDbLockAttr
from ...tools.database_with_instrument_level import DatabaseInstLevel
from ...tools.name import Name
from ...tools.lockable_dict import LockableDict
from ...tools.miscellaneous import interpret_data_filename


## logger object
logger = getLogger()


class DatabaseInstLvlDataset(DatabaseInstLevel, Instmodel4DatasetAttr, DstDbLockAttr):
    """docstring for DatabaseInstLvlDataset."""

    def __init__(self, object_stored, database_name, instmodel4dataset=None, list_datasetnames=None,
                 ordered=False, use_samelock=False, lock_dataset=None, lock_database=None):
        """doctstring of DatabaseInstLvlDataset __init__ method."""
        DstDbLockAttr.__init__(self, use_samelock=use_samelock, lock_dataset=lock_dataset,
                               lock_database=lock_database)
        Instmodel4DatasetAttr.__init__(self, instmodel4dataset=instmodel4dataset,
                                       list_datasetnames=list_datasetnames,
                                       lock=self.get_dataset_Lock_instance())
        DatabaseInstLevel.__init__(self, object_stored=object_stored,
                                   database_name=database_name, ordered=ordered,
                                   lock=self.get_database_Lock_instance(), default={"all": None})

    def __getitem__(self, key):
        if key in self.instmodel4dataset:
            inst_model = self.instmodel4dataset[key]
            dataset_info = interpret_data_filename(key)
            instmodel_fullname = "{}_{}".format(dataset_info["inst_name"], inst_model)
            return self[instmodel_fullname]
        else:
            return super(DatabaseInstLvlDataset, self).__getitem__(key)

    @property
    def locked(self):  # Allow the __setitem__ method of Lockabledict to know use self.locked
        return self.database_locked

    def get_Lock_instance(self):  # Allow the __missing__ method of dico_database to know use
        return self.get_database_Lock_instance()  # self.get_Lock_instance


class DatabaseFunc(Name, Instmodel4DatasetAttr, DstDbLockAttr):
    """docstring for DatabaseStoreFuncInstLvl.

    1. Initialise the Name attributes.
    2. Set the instordered
    3. Initialise the locks
    4. Initialise the Instmodel4Dataset
    5. Initialise the instrument_db attribute with the above instmodel4dataset if exist or without
       instmodel4dataset if not.
    6. Initialise the dataset_db attribute as a LockableDict with the lock_dataset defined above.
       Add an "all" key with value None for the func including all datasets and key for datasets in
       instmodel4dataset
    """
    def __init__(self, object_stored, database_name, instmodel4dataset=None, list_datasetnames=None,
                 instordered=False, use_samelock=False, lock_dataset=None, lock_database=None):
        Name.__init__(self, name=object_stored, name_prefix=database_name)  # 1
        self.__instordered = instordered  # 2
        DstDbLockAttr.__init__(self, use_samelock=use_samelock, lock_dataset=lock_dataset,
                               lock_database=lock_database)  # 3
        Instmodel4DatasetAttr.__init__(self, instmodel4dataset=instmodel4dataset,
                                       list_datasetnames=list_datasetnames,
                                       lock=self.get_dataset_Lock_instance())  # 4
        self.__instrument_db = DatabaseInstLvlDataset(object_stored=self.object_stored,  # 5
                                                      database_name=self.database_name,
                                                      instmodel4dataset=self.instmodel4dataset,
                                                      ordered=self.instordered,
                                                      use_samelock=self.samelock,
                                                      lock_dataset=self.get_dataset_Lock_instance(),
                                                      lock_database=(self.
                                                                     get_database_Lock_instance()))
        self.dataset_db = LockableDict(lock=self.get_dataset_Lock_instance())  # 6
        self.dataset_db["all"] = None
        self.__update_datasets_dataset_db()

    @property
    def database_name(self):
        """Return the name of the database."""
        return self.name_prefix

    @property
    def object_stored(self):
        """Return the name of the objects stored in the database."""
        return self.name

    # @Instmodel4Dataset.instmodel4dataset.setter
    # def instmodel4dataset(self, instmodel4dataset):
    #     """The  idea is that if you try to set instmodel4dataset of DatabaseFunc directly.
    #     You check if it's already existe and if yes you check if it's the same and if not raise an
    #     error.
    #     1. Once set instmodel4dataset should by modified but not replaced. So if it's already set
    #        if identical do nothing otherwise raise an error.
    #     2. If not defined already set it using the setter of Instmodel4Dataset class and if the
    #        DatabaseFunc has an instrument_db already, set its instmodel4Dataset to the same object
    #     """
    #     if self.isdefined_instmodel4dataset:  # 1
    #         if self.instmodel4dataset is instmodel4dataset:
    #             return None
    #         else:
    #             raise ValueError("instmodel4dataset already exists in {}.".format(self.full_name))
    #     else:  # 2
    #         super(DatabaseFunc, self.__class__).instmodel4dataset.fset(self, instmodel4dataset)
    #         if hasattr(self, "instrument_db"):
    #             self.instrument_db.instmodel4dataset = instmodel4dataset

    @property
    def instordered(self):
        """Return the boolean instordered values."""
        return self.__instordered

    @property
    def instrument_db(self):
        """Return the instrument_db."""
        return self.__instrument_db

    # def replace_instrumentdb(self, db):
    #     """The idea is that if you try to assign instrument db the instmodel4dataset is still the
    #     same than for DatabaseFunc. So the idea would be that when you try to set instrument_db
    #     if there is no instmodel4dataset defined yet you affect the one instrument_db to
    #     Databasefunc. If there is you check that it's the same or if the new instrument_db doesn't
    #     have one you attribute it the one of DatabaseFunc
    #
    #     1. If db is None do not do anything
    #     Else,
    #     2. If db is not an instance of DatabaseInstLvlDataset, Raise an error
    #     3. Else if db has an instmodel4dataset and Databasefunc has an instmodel4dataset they have
    #        to be identical.
    #     4. If only DatabaseFunc has an instmodel4dataset, than you want to get the content of this
    #        instmodel4dataset into the instrument_db if not already done.
    #        create it empty and the copy the content of db into it
    #     5. If only db has an instmodel4dataset affect it to DatabaseFunc
    #     6. Assign db to instrument_db
    #     """
    #     if db is None:  # 1
    #         logger.debug("No instrument database provided for instance {} of class {}."
    #                      "".format(self.name, self.__class__.__name__))
    #     else:
    #         if not isinstance(db, DatabaseInstLvlDataset):  # 2
    #             raise ValueError("db should be a DatabaseInstLvlDataset instance")
    #         elif self.isdefined_instmodel4dataset and db.isdefined_instmodel4dataset:  # 3
    #             if self.instmodel4dataset is not db.instmodel4dataset:
    #                 raise ValueError("The new instrument db must have the same instmodel4dataset "
    #                                  "than the DatabaseFunc")
    #         elif self.isdefined_instmodel4dataset:  # 4
    #             instmodel4dataset = self.instmodel4dataset
    #
    #                 self.__instrument_db = inst_db
    #         elif db.isdefined_instmodel4dataset:
    #             instmodel4dataset = db.instmodel4dataset
    #         else:
    #             instmodel4dataset = None
    #         self.instmodel4dataset = db.instmodel4dataset
    #         inst_db = DatabaseInstLvlDataset(object_stored=self.object_stored,
    #                                          database_name=self.database_name,
    #                                          instmodel4dataset=self.instmodel4dataset,
    #                                          ordered=self.__instordered,
    #                                          use_samelock=self.samelock,
    #                                          lock_dataset=self.get_dataset_Lock_instance(),
    #                                          lock_database=self.get_database_Lock_instance())
    #
    #
    #         logger.debug("The instrument database of instance {} of class {} set to {}."
    #                      "".format(self.name, self.__class__.__name__, db))
    #         self.__instrument_db = db  # 6

    # @property
    # def isdefined_instrumentdb(self):
    #     """Return True if a instrument_db is defined."""
    #     return hasattr(self, "instrument_db")

    @property
    def dataset_db(self):
        """Return the dataset_db."""
        return self.__dataset_db

    @dataset_db.setter
    def dataset_db(self, db):
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

    # @property
    # def uptodate(self):
    #     """Return True if a database is uptodate. false if an update is needed."""
    #     return hasattr(self, "instmodel4dataset")

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
        set_old.remove("all")
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
