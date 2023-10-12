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
from loguru import logger
from copy import copy

from ...tools.dico_database import init_result, add_obj_in_result
from ...tools.lockable_dict import LockableDict, Lock


class NoiseModel4InstModel(LockableDict):
    """docstring for NoiseModel4InstModel.

    Dictionary with keys being instrument model full names and values noise model categories

    Arguments
    ---------
    l_instmodels_fullname   : list of string
        List of instrument model full names 
    l_noisemodel_category   : list of string
        List of noise model category corresponding to each instrument model
    lock                :
    """
    def __init__(self, l_noisemodel_category=None, l_instmodel_fullname=None, lock=None):
        """Check if None is really a possibility for list_datasetnames and if it should be for list_instmodels
        """
        super(NoiseModel4InstModel, self).__init__(ordered=True, lock=lock)
        if l_instmodel_fullname is not None:
            self.update(l_instmodel_fullname=l_instmodel_fullname, l_noisemodel_category=l_noisemodel_category)

    @property
    def s_noisemodel_categories_used(self):
        """Return the set of noise model categories used."""
        return set(self.values())

    @property
    def s_instmod_fullname(self):
        """Return the s of instrument model full names used."""
        return list(self.keys())

    def _update(self, l_instmodel_fullname, l_noisemodel_category=None):
        """Update the datasets in instmodel4dataset.

        1a. Get datasetnames that are in list_datasetnames but not currently in instmodel4dataset
        1b. Add them to instmodel4dataset and initialize them to "default"
        2a. Get datasetnames that are in instmodel4dataset but not in list_datasetnames
        2b. Delete them from instmodel4dataset
        """
        set_new = set(l_instmodel_fullname)
        set_old = self.s_instmod_fullname
        set_add = set_new - set_old  # 1a
        set_delete = set_old - set_new  # 2a
        for instmodel in set_add:
            if l_noisemodel_category is None:
                noise_model_cat = None
            else:
                idx = l_instmodel_fullname.index(instmodel)
                noise_model_cat = l_noisemodel_category[idx]
            self[instmodel] = noise_model_cat  # 1b
        for instmodel in set_delete:
            self.remove(instmodel)  # 2b

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


class NoiseModel4InstModelAttr(object):
    """docstring for NoiseModel4InstModelAttr."""
    def __init__(self, noisemodel4instmodel=None, l_instmodel_fullname=None, lock=None):
        """Initialise the noisemodel4instmodel attribute.

        :param noisemodel4instmodel: Even if it has a lock, the lock of the new instance is decided by
                the lock arg (see below).
        :param l_instmodel_fullname:
        :param lock: This argument will decide of the lock affected to the new instance.

        """
        self.replace_noisemodel4instmodel(noisemodel4instmodel=noisemodel4instmodel,
                                          l_instmodel_fullname=l_instmodel_fullname, lock=lock)
        if type(self) is NoiseModel4InstModelAttr:  #
            raise NotImplementedError("NoiseModel4InstModelAttrs should not be instanciated !")

    def replace_noisemodel4instmodel(self, noisemodel4instmodel=None, l_instmodel_fullname=None, lock=None):
        """
        1. Decide of the Lock instance the new noisemodel4instmodel depending on the value of lock arg:
            if "old", the old lock
            elif a Lock instance, this lock instance
            elif "self" the lock object of self
            else a newly created lock object
        2. if noisemodel4instmodel arg provided, copy it setting the lock of step 1
        3. else create a new empty noisemodel4instmodel setting the lock of step 1
            and update the instrument models with the l_instmodel_fullname arg
        """
        if lock == "old":  # 1
            lock = self.noisemodel4instmodel.get_Lock_instance()
        elif lock == "self":
            lock = self.get_Lock_instance()
        elif lock == "self dataset":
            lock = self.get_dataset_Lock_instance()
        elif lock == "noisemodel4instmodel":
            lock = noisemodel4instmodel.get_Lock_instance()
        elif isinstance(lock, Lock):
            pass
        else:
            lock = Lock()
        if noisemodel4instmodel is not None:  # 2
            if l_instmodel_fullname is not None:
                raise ValueError("You should provide noisemodel4instmodel or l_instmodel_fullname not both.")
            else:
                if not(isinstance(noisemodel4instmodel, NoiseModel4InstModel)):
                    raise ValueError("noisemodel4instmodel should be an NoiseModel4InstModel instance.")
                if not(self.__isdefined_noisemodel4instmodel):
                    new = noisemodel4instmodel
                else:
                    new = noisemodel4instmodel.copy(lock=lock)
        else:  # 3
            new = NoiseModel4InstModel(l_instmodel_fullname=l_instmodel_fullname, lock=lock)
        self._noisemodel4instmodel = new
        logger.debug(f"New NoiseModel4InstModel provided for instance of class {self.__class__.__name__}: {self.noisemodel4instmodel}")

    def d_noisemodel_class_used(self):
        """Return the dictionary of noise models used.

        Key are noise model categories and values noise model classes
        """
        result = {}
        for noisemodel_cat in self.noisemodel4instmodel.s_noisemodel_categories_used():
            result[noisemodel_cat] = self.noise_model_classes(instmod_fullname=instmod_fullname)
        return result

    def get_noisemodel_category(self, instmod_fullname):
        """Return the noise model category for the instrument model specified.

        """
        return self._noisemodel4instmodel[instmod_fullname]

    def get_noisemodel_class(self, instmod_fullname):
        """Return the noise model class for the instrument model specified.
        """
        noisemodel_cat = self.get_noisemodel_category(instmod_fullname=instmod_fullname)
        return self.get_NoiseModelClass(noise_model_category=noisemodel_cat)

    def get_linstmodel4noisemodel(self, noise_model_category):
        """Return list of dataset name using a given instrument model.

        Arguments
        ---------
        noise_model_category : String
            Category of the noise model

        Returns
        -------
        l_instmod_fullname : List of String
            List of instrument model full names using the noise model category provided
        """
        res = []
        for instmodel_fullname_ii in self._noisemodel4instmodel.keys():
            noisemodel_cat_ii = self.get_noisemodel_category(instmod_fullname=instmodel_fullname_ii)
            if instmodel_fullname_ii == noise_model_category:
                res.append(instmodel_fullname_ii)
        return res
    
    def update_noisemodel4instmodel(self, l_instmodel_fullname, l_noisemodel_category):
        """Update noisemodel4instmodel dictionary and check 

        Arguments
        ---------
        noise_model_category : String
            Category of the noise model

        Returns
        -------
        l_instmod_fullname : List of String
            List of instrument model full names using the noise model category provided
        """
        for instmod_fullname in l_instmodel_fullname:
            
        for noisemod_cat in l_noisemodel_category:
            if noisemod_cat not in self.possible_noise_model_categories:
                raise ValueError(f"noise model category {noisemod_cat} is not a noise model category available for {self.cat} models")
        self._noisemodel4instmodel.update(self, l_instmodel_fullname, l_noisemodel_category=None)

    @property
    def __isdefined_noisemodel4instmodel(self):
        return hasattr(self, "_noisemodel4instmodel")
