#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
dataset_with_instrument_level module.

The objective of this package is to provides a database object with instrument levels.
The instrument levels are instrument category, instrument name, instrument model

@ DONE:
    -
@TODO:
    -
"""
from logging import getLogger
from collections import OrderedDict

from .name import Name
from .dico_database import get_content_2ndlevel, get_content_3ndlevel

## Logger object
logger = getLogger()


class DatabaseInstLevel(Name):
    """docstring for DatabaseInstLevel."""

    __def_instmod_level = None

    __msg = "Instrument {} {} {} in database {}. {}."
    __add1 = "already"
    __rm1 = "not"
    __addobj1 = "object already defined"
    __addobjforce1 = "object has been overwritten"
    __add2 = "The add command is ignored"
    __rm2 = "The rm command is ignored"
    __get2 = "The get command is impossible"
    __addobj2 = "If you want to overwrite pass force=True"

    def __init__(self, object_name, database_name):
        """docstring of the init method of DatabaseInstLevel."""
        super(DatabaseInstLevel, self).__init__(name=database_name, name_prefix=object_name)
        self._database = dict()

    def __getitem__(self, key):
        return self._database[key]

    @property
    def object_name(self):
        """Return the name of the object concerned by the database."""
        return self.name_prefix

    @property
    def database_name(self):
        """Return the name of the database which indicate what it contains."""
        return self.name

    def add_instcat(self, inst_cat):
        """Add an instrument category."""
        if self.has_instcat(inst_cat):
            logger.warning(self.__msg.format("category", inst_cat, self.__add1, self.full_name,
                                             self.__add2))
        else:
            self._database[inst_cat] = {}

    def rm_instcat(self, inst_cat):
        """Add an instrument category."""
        res = self._database.pop(inst_cat, None)
        if res is None:
            logger.warning(self.__msg.format("category", inst_cat, self.__rm1, self.full_name,
                           self.__rm2))

    @property
    def inst_categories(self):
        """Return the list of current isntrument categories."""
        return list(self._database.keys())

    def has_instcat(self, inst_cat):
        """Return True if inst_cat is an existing instrument category."""
        return inst_cat in self.inst_categories

    def add_instname(self, inst_cat, inst_name):
        """Add an instrument name to an instrument category."""
        if self.has_instcat(inst_cat):
            if self.has_instname(inst_cat, inst_name):
                logger.warning(self.__msg.format("name", inst_cat + "_" + inst_name, self.__add1,
                               self.full_name, self.__add2))
            else:
                self._database[inst_cat][inst_name] = OrderedDict()
        else:
            logger.warning(self.__msg.format("category", inst_cat, self.__rm1, self.full_name,
                                             self.__add2))

    def rm_instname(self, inst_cat, inst_name):
        """Add an instrument name to an instrument category."""
        if self.has_instcat(inst_cat):
            res = self._database[inst_cat].pop(inst_name, None)
            if res is None:
                logger.warning(self.__msg.format("name", inst_cat + "_" + inst_name, self.__rm1,
                                                 self.full_name, self.__rm2))
        else:
            logger.warning(self.__msg.format("category", inst_cat, self.__rm1, self.full_name,
                                             self.__rm2))

    def get_instnames(self, inst_cat=None):
        """Return the list instrument names in the database."""
        return get_content_2ndlevel(self._database, level1_key=inst_cat)

    def has_instname(self, inst_cat, inst_name):
        """Return True if inst_name is an existing instrument name in the instrument category."""
        if self.has_instcat(inst_cat):
            return inst_name in self.get_instnames(inst_cat=inst_cat)
        else:
            return False

    def add_instmodel(self, inst_cat, inst_name, inst_model):
        """Add an instrument model to an instrument name of an instrument category."""
        if self.has_instname(inst_cat, inst_name):
            if self.has_instmodel(inst_cat, inst_name, inst_model):
                logger.warning(self.__msg.format("model", inst_cat + "_" + inst_name + "_" +
                                                 inst_model, self.__add1, self.full_name,
                                                 self.__add2))
            else:
                self._database[inst_cat][inst_name][inst_model] = self.__def_instmod_level
        else:
            logger.warning(self.__msg.format("name", inst_cat + "_" + inst_name, self.__rm1,
                                             self.full_name, self.__add2))

    def rm_instmodel(self, inst_cat, inst_name, inst_model):
        """Add an instrument name to an instrument category."""
        if self.has_instname(inst_cat, inst_name):
            res = self._database[inst_cat][inst_name].pop(inst_model, None)
            if res is None:
                logger.warning(self.__msg.format("model", inst_cat + "_" + inst_name + "_" +
                                                 inst_model, self.__rm1, self.full_name,
                                                 self.__rm2))
        else:
            logger.warning(self.__msg.format("name", inst_cat + "_" + inst_name, self.__rm1,
                                             self.full_name, self.__rm2))

    def get_instmodels(self, inst_cat=None, inst_name=None):
        """Return the list instrument names in the database."""
        return get_content_3ndlevel(self._database, level1_key=inst_cat, level2_key=inst_name)

    def has_instmodel(self, inst_cat, inst_name, inst_model):
        """Return True if inst_model exist in the database for the category and name provided."""
        if self.has_instname(inst_cat, inst_name):
            return inst_model in self.get_instmodels(inst_cat=inst_cat, inst_name=inst_name)
        else:
            return False

    @classmethod
    def _is_object_default(cls, object):
        return object is cls.__def_instmod_level

    def has_object(self, inst_cat, inst_name, inst_model):
        """Return True if an object is stored in the database for the category, name and model."""
        if self.has_instmodel(inst_cat, inst_name, inst_model):
            return self._is_object_default(self._database[inst_cat][inst_name][inst_model])
        else:
            return False

    def add_object(self, inst_cat, inst_name, inst_model, object, force=False):
        """ Add an object to the database."""
        add_object = False
        if self.has_instmodel(inst_cat, inst_name, inst_model):
            if self.get_object(inst_cat, inst_name, inst_model) is self.__def_instmod_level:
                add_object = True
            else:
                if force:
                    logger.info(self.__msg.format("model", inst_cat + "_" + inst_name + "_" +
                                                  inst_model, self.__addobjforce1, self.full_name))
                    add_object = True
                else:
                    raise ValueError(self.__msg.format("model", inst_cat + "_" + inst_name + "_" +
                                                       inst_model, self.__addobj1, self.full_name,
                                                       self.__addobj2))
        else:
            add_object = True
            if not(self.has_instcat(inst_cat)):
                self.add_instcat(inst_cat)
            if not(self.has_instname(inst_cat, inst_name)):
                self.add_instname(inst_cat, inst_name)
        if add_object:
            self._database[inst_cat][inst_name][inst_model] = object
