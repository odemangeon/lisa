#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
instmodel4dataset module.

The objective of this package is to provides the core Instmodel4Dataset class.

@DONE:
    -

@TODO:
    -
"""
from logging import getLogger
from collections import defaultdict
from copy import copy

from ...tools.miscellaneous import interpret_data_filename
from ...tools.dico_database import init_result, add_obj_in_result
from ...tools.lockable_dict import LockableDict, Lock  # , func_name_getinstance_lock
# from .database_func import func_name_samelock

## Logger
logger = getLogger()


class Instmodel4Dataset(LockableDict):
    """docstring for Instmodel4Dataset.

    1. To define Instmodel4Dataset, you should provide either instmodel4dataset or
       list_datasetnames not both. If both raise an error
    2. If none of the 2 provided the instmodel4dataset attribute is not define. Log that.
    3. If instmodel4dataset provided, check that no lock argument (that would be redundant with the
       Lock in instmodel4dataset) is provided and set it to the instmodel4dataset attribute
    4. If list_datasetnames provided, we create a new LockableDict to be set to instmodel4dataset
       and update it with the datasets provided.
    """
    def __init__(self, list_datasetnames=None, lock=None):
        super(Instmodel4Dataset, self).__init__(ordered=False, lock=lock)
        if list_datasetnames is not None:
            self.update_datasets(list_datasetnames)

    # The idea behind commenting it is that maybe I can used the inherited update method.
    # def update_content_instmodel4dataset(self, instmodel4dataset):
    #     """
    #     1. Check that the proposed instmodel4dataset is a LockableDict
    #     2.
    #     """
    #     if not isinstance(instmodel4dataset, LockableDict):  # 1
    #         raise ValueError("instmodel4dataset has  to be LockableDict subclass instance. You "
    #                          "tried to assign a {}.".format(type(instmodel4dataset)))
    #     if not self.isdefined_instmodel4dataset:
    #         self.instmodel4dataset = LockableDict(lock=self.get_Lock_instance())
    #     for key, value in instmodel4dataset:
    #         self.instmodel4dataset[key] = value

    # @property
    # def isdefined_instmodel4dataset(self):
    #     """Return True if a instmodel4dataset is defined."""
    #     return hasattr(self, "instmodel4dataset")

    def name_instmodels_used(self, inst_name=None, sortby_instname=False):
        """Return a dict which for each instrument name give the instrument models to use."""
        if sortby_instname:
            result = defaultdict(list)
        else:
            result = []
        for dataset_name, mod_name in self.items():
            file_info = interpret_data_filename(dataset_name)
            if (file_info["inst_name"] == inst_name) or (inst_name is None):
                if sortby_instname:
                    result[file_info["inst_name"]].append(mod_name)
                else:
                    result.append("{}_{}".format(file_info["inst_name"], mod_name))
        return result

    def get_instmod_fullname(self, dataset_name):
        """Return the full name of the instrument model used for the specified dataset."""
        instmod_name = self[dataset_name]
        file_info = interpret_data_filename(dataset_name)
        return "{}_{}".format(file_info["inst_name"], instmod_name)

    @property
    def list_datasets(self):
        """Return the lsit of dataset names currently in instmodel4dataset attribute."""
        return list(self.keys())

    def update_datasets(self, list_datasetnames):
        """Update the datasets in instmodel4dataset.

        1a. Get datasetnames that are in list_datasetnames but not currently in instmodel4dataset
        1b. Add them to instmodel4dataset and initialize them to "default"
        2a. Get datasetnames that are in instmodel4dataset but not in list_datasetnames
        2b. Delete them from instmodel4dataset
        """
        set_new = set(list_datasetnames)
        set_old = set(self.list_datasets)
        set_add = set_new - set_old  # 1a
        set_delete = set_old - set_new  # 2a
        for dataset_name in set_add:
            self[dataset_name] = "default"  # 1b
        for dataset_name in set_delete:
            self.pop(dataset_name)  # 2b

    def __copy__(self):
        new_copy = type(self)()
        new_copy.update(self)
        if self.locked:
            new_copy.lock()
        return new_copy

    def copy(self, lock=None):
        new_copy = copy(self)
        if lock is not None:
            new_copy.set_Lock_instance(lock)
        return new_copy


class Instmodel4DatasetAttr(object):
    """docstring for ProvideDatasetDbAttr."""
    def __init__(self, instmodel4dataset=None, list_datasetnames=None, lock=None):
        """Initialise the instmodel4dataset attribute.
        ----
        Args:
            - instmodel4dataset: Even if it has a lock the lock of the new instance is decided by
                the lock arg (see below).
            - Lock : This argument will decide of the lock affected to the new instance.

        """
        self.replace_instmodel4dataset(instmodel4dataset=instmodel4dataset,
                                       list_datasetnames=list_datasetnames, lock=lock)
        if type(self) is Instmodel4DatasetAttr:  #
            raise NotImplementedError("Instmodel4DatasetAttr should not be instanciated !")

    @property
    def instmodel4dataset(self):
        """Dictionnary giving the name of the instrument model to use for which dataset.

        Warning: It give the name and not the full_name
        """
        return self.__instmodel4dataset

    # @property
    # def isdefined_instmodel4dataset(self):
    #     """Return True if self has an instmodel4dataset.
    #     """
    #     return hasattr(self, "instmodel4dataset")

    def replace_instmodel4dataset(self, instmodel4dataset=None, list_datasetnames=None, lock=None):
        """
        1. Decide of the Lock instance the new instmodel4dataset depending on the value of lock arg:
            if "old", the old lock
            elif a Lock instance, this lock instance
            elif "self" the lock object of self
            else a newly created lock object
        2. if instmodel4dataset arg provided, copy it setting the lock of step 1
        3. else create a new empty instmodel4dataset setting the lock of step 1
            and update the dataset with the list_datasetnames arg
        """
        if lock == "old":  # 1
            lock = self.instmodel4dataset.get_Lock_instance()
        elif lock == "self":
            lock = self.get_Lock_instance()
        elif lock == "self dataset":
            lock = self.get_dataset_Lock_instance()
        elif lock == "instmodel4dataset":
            lock = instmodel4dataset.get_Lock_instance()
        elif isinstance(lock, Lock):
            pass
        else:
            lock = Lock()
        if instmodel4dataset is not None:  # 2
            if list_datasetnames is not None:
                raise ValueError("You should provide instmodel4dataset or list_datasetnames not "
                                 "both.")
            else:
                if not(isinstance(instmodel4dataset, Instmodel4Dataset)):
                    raise ValueError("instmodel4dataset should be an Instmodel4Dataset instance.")
                if not(self.__isdefined_instmodel4dataset):
                    new = instmodel4dataset
                else:
                    new = instmodel4dataset.copy(lock=lock)
        else:  # 3
            new = Instmodel4Dataset(list_datasetnames=list_datasetnames, lock=lock)
        self.__instmodel4dataset = new
        logger.debug("New Instmodel4Dataset provided for instance of class {}: {}"
                     "".format(self.__class__.__name__, self.instmodel4dataset))

    def get_instmodels_used(self, inst_name=None, inst_cat=None,
                            sortby_instcat=False, sortby_instname=False, sortby_instmodel=False):
        """Return the dictionnary of instrument models used.

        TODO: For now the name of the model and not the fullname seems to be stored in
            instmodel4dataset, so this function is wrong.
        """
        result = init_result(sortby_lvl1key=sortby_instcat, sortby_lvl2key=sortby_instname,
                             default_value=[])
        for instmodel_fullname in self.name_instmodels_used():
            inst_model_obj = self.instruments[instmodel_fullname]
            inst_model = inst_model_obj.name
            inst_cat = inst_model_obj.instrument.category
            inst_name = inst_model_obj.instrument.name
            add_obj_in_result(result, inst_model_obj, lvl3_key=inst_model, lvl2_key=inst_name,
                              lvl1_key=inst_cat,
                              sortby_lvl1key=sortby_instcat, sortby_lvl2key=sortby_instname,
                              sortby_lvl3key=sortby_instmodel)
        return result

    def name_instmodels_used(self, inst_name=None, sortby_instname=False):
        """Return a dict which for each instrument name give the instrument models to use.

        For more details see instmodel4dataset.name_instmodels_used
        """
        return self.instmodel4dataset.name_instmodels_used(inst_name=inst_name,
                                                           sortby_instname=sortby_instname)

    def get_instmod_fullname(self, dataset_name):
        """Return the full name of the instrument model used for the specified dataset.

        For more details see instmodel4dataset.name_instmodels_used
        """
        return self.get_instmod_fullname(dataset_name=dataset_name)

    def get_instmod(self, dataset_name):
        """Return the instrument model used for the specified dataset.

        For more details see instmodel4dataset.name_instmodels_used
        """
        instmodel_fullname = self.get_instmod_fullname(dataset_name=dataset_name)
        return self.instruments[instmodel_fullname]

    @property
    def __isdefined_instmodel4dataset(self):
        return hasattr(self, "instmodel4dataset")
