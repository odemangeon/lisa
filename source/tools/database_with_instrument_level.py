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

from .name import Name
from .dico_database import Nesteddict_wfixellvlnb


## Logger object
logger = getLogger()

__kwargs_names = ["inst_model", "inst_name", "inst_cat", "instmod_fullname"]


def check_args(inst_model=None, inst_name=None, inst_cat=None, instmod_fullname=None):
    """Check arguments for DatabaseInstLevel."""
    if ((inst_model is not None) or (inst_name is not None)) and (instmod_fullname is not None):
        raise ValueError("You should provide inst_model and inst_name or instmod_fullname not both")
    if instmod_fullname is not None:
        inst_model, inst_name = instmod_fullname.split("_")
    return inst_model, inst_name, inst_cat


def look4instcat(dico_db, inst_name):
    """Look in all the instrument categories to find the inst_cat corresponding to inst_name."""
    for inst_cat in dico_db:
        if inst_name in dico_db[inst_cat]:
            return inst_cat
    return None


def check_instcat(dico_db, inst_name, inst_cat):
    """Look in all the instrument categories to find the inst_cat corresponding to inst_name."""
    if (inst_name is not None) and (inst_cat is None):
        inst_cat = look4instcat(dico_db, inst_name)
        if inst_cat is None:
            raise ValueError("There is no instrument named {} in the database."
                             "".format(inst_name))
    return inst_cat, inst_name

# def add_object_in_resultdict(resultdict, obj, inst_model, inst_name, inst_cat,
#                              sortby_instcat=False, sortby_instname=False, force=False):
#     """Add object in result dictonary."""
#     if sortby_instcat:
#         if inst_cat not in resultdict:
#             resultdict[inst_cat] = {}
#     if sortby_instname:
#         if sortby_instcat:
#             if inst_name not in resultdict[inst_cat]:
#                 resultdict[inst_cat][inst_name] = {}
#         else:
#             if inst_name not in resultdict:
#                 resultdict[inst_name] = {}
#     raiseerror = False
#     if sortby_instcat and sortby_instname:
#         if (inst_model not in resultdict[inst_cat][inst_name]) or force:
#             resultdict[inst_cat][inst_name][inst_model] = obj
#         else:
#             raiseerror = True
#     elif sortby_instcat:
#         if (inst_model not in resultdict[inst_cat]) or force:
#             resultdict[inst_cat][inst_model] = obj
#         else:
#             raiseerror = True
#     elif sortby_instname:
#         if (inst_model not in resultdict[inst_name]) or force:
#             resultdict[inst_name][inst_model] = obj
#         else:
#             raiseerror = True
#     else:
#         if (inst_model in resultdict) or force:
#             resultdict[inst_name] = obj
#         else:
#             raiseerror = True
#     if raiseerror:
#         raise ValueError("Object {}_{}_{} alredy exist if you want to overwrite pass force=True."
#                          "".format(inst_model, inst_name, inst_cat))


class Nesteddict_getitIMFN(Nesteddict_wfixellvlnb):
    """Subclass of Nesteddict_wfixellvlnb to implement a getitem with instrument model full name."""

    def __getitem__(self, key):
        if key in self:
            return super(Nesteddict_getitIMFN, self).__getitem__(key)
        else:
            try:
                if self.lvl == 0:
                    for inst_cat in self.inst_categories:
                        if key in self.get_instnames(inst_cat=inst_cat):
                            return self[inst_cat][key]
                    inst_name, inst_model = key.split("_")
                    for inst_cat in self.inst_categories:
                        if inst_name in self.get_instnames(inst_cat=inst_cat):
                            return self[inst_cat][inst_name][inst_model]
                elif self.lvl == 1:
                    inst_name, inst_model = key.split("_")
                    return self[inst_name][inst_model]
                else:
                    raise KeyError
            except:
                return super(Nesteddict_getitIMFN, self).__getitem__(key)

    def __missing__(self, key, cls=None):
        return super(Nesteddict_getitIMFN, self).__missing__(key, cls=Nesteddict_getitIMFN)


class DatabaseInstLevel(Nesteddict_getitIMFN, Name):
    """docstring for DatabaseInstLevel."""
    def __init__(self, object_stored, database_name=None, ordered=False, default=None):
        Name.__init__(self, name=object_stored, name_prefix=database_name)
        Nesteddict_wfixellvlnb.__init__(self, nb_lvl=3, ordered=ordered, default=default)

    # def __getitem__(self, key):
    #     if key in self:
    #         return super(DatabaseInstLevel, self).__getitem__(key)
    #     else:
    #         try:
    #             inst_name, inst_model = key.split("_")
    #             for inst_cat in self.inst_categories:
    #                 if inst_name in self.get_instnames(inst_cat=inst_cat):
    #                     return self[inst_cat][inst_name][inst_model]
    #         except:
    #             return super(DatabaseInstLevel, self).__getitem__(key)
    #
    # def __missing__(self, key):
    #     return super(DatabaseInstLevel, self).__missing__(key,
    #                                                       cls=Nesteddict_getitem_instmodfullname)

    @property
    def database_name(self):
        """Return the name of the database."""
        return self.name_prefix

    @property
    def object_stored(self):
        """Return the name of the objects stored in the database."""
        return self.name

    @property
    def inst_categories(self):
        """Return the list of current isntrument categories."""
        return list(self.keys())

    def has_instcat(self, inst_cat):
        """Return True if inst_cat is an existing instrument category."""
        return inst_cat in self

    def get_instnames(self, inst_cat=None, sortby_instcat=False):
        """Return the list instrument names in the database."""
        return self.get_lvl2_keys(level1_key=inst_cat, sortby_lvl1key=sortby_instcat)

    def has_instname(self, inst_name, inst_cat=None):
        """Return True if inst_name is an existing instrument name in the instrument category."""
        return inst_name in self.get_instnames(inst_cat=inst_cat)

    def get_instmodels(self, inst_name=None, inst_cat=None,
                       sortby_instname=False, sortby_instcat=False):
        """Return the list instrument names in the database."""
        return self.get_lvl3_keys(level1_key=inst_cat, level2_key=inst_name,
                                  sortby_lvl1key=sortby_instcat, sortby_lvl2key=sortby_instname)

    def has_instmodel(self, inst_model=None, inst_name=None, inst_cat=None, **kwargs):
        """Return True if inst_model exist in the database for the category and name provided."""
        inst_model, inst_name, inst_cat = check_args(inst_model=inst_model, inst_name=inst_name,
                                                     inst_cat=inst_cat, **kwargs)
        return inst_model in self.get_instmodels(inst_name=inst_name, inst_cat=inst_cat)

    def get_objects(self, inst_model=None, inst_name=None, inst_cat=None,
                    sortby_instcat=False, sortby_instname=False, sortby_instmodel=False, **kwargs):
        inst_model, inst_name, inst_cat = check_args(inst_model=inst_model, inst_name=inst_name,
                                                     inst_cat=inst_cat, **kwargs)
        return self.get_lvl3_values(level1_key=inst_cat, level2_key=inst_name,
                                    sortby_lvl1key=sortby_instcat, sortby_lvl2key=sortby_instname,
                                    sortby_lvl3key=sortby_instmodel)

# class DatabaseInstLevel(Name):
#     """docstring for DatabaseInstLevel."""
#
#     __def_instmod_level = None
#
#     __msg = "Instrument {} {} {} in database {}. {}."
#     __add1 = "already"
#     __rm1 = "not"
#     __addobj1 = "object already defined"
#     __addobjforce1 = "object has been overwritten"
#     __add2 = "The add command is ignored"
#     __rm2 = "The rm command is ignored"
#     __get2 = "The get command is impossible"
#     __addobj2 = "If you want to overwrite pass force=True"
#
#     def __init__(self, object_stored, database_name):
#         """docstring of the init method of DatabaseInstLevel."""
#         super(DatabaseInstLevel, self).__init__(name=object_stored, name_prefix=database_name)
#         self._database = dict()
#
#     def __getitem__(self, key):
#         if key in self.inst_categories:
#             return self._database[key]
#         else:
#             inst_name, inst_model = key.split("_")
#             for inst_cat in self.inst_categories:
#                 if inst_name in self.get_instnames(inst_cat=inst_cat):
#                     return self._database[inst_cat][inst_name][inst_model]
#
#     @property
#     def object_name(self):
#         """Return the name of the object concerned by the database."""
#         return self.name_prefix
#
#     @property
#     def database_name(self):
#         """Return the name of the database which indicate what it contains."""
#         return self.name
#
#     def add_instcat(self, inst_cat):
#         """Add an instrument category."""
#         if self.has_instcat(inst_cat):
#             logger.warning(self.__msg.format("category", inst_cat, self.__add1, self.full_name,
#                                              self.__add2))
#         else:
#             self._database[inst_cat] = {}
#
#     def rm_instcat(self, inst_cat):
#         """Add an instrument category."""
#         res = self._database.pop(inst_cat, None)
#         if res is None:
#             logger.warning(self.__msg.format("category", inst_cat, self.__rm1, self.full_name,
#                            self.__rm2))
#
#     @property
#     def inst_categories(self):
#         """Return the list of current isntrument categories."""
#         return list(self._database.keys())
#
#     def has_instcat(self, inst_cat):
#         """Return True if inst_cat is an existing instrument category."""
#         return inst_cat in self.inst_categories
#
#     def add_instname(self, inst_name, inst_cat):
#         """Add an instrument name to an instrument category."""
#         if self.has_instcat(inst_cat):
#             if self.has_instname(inst_name, inst_cat):
#                 logger.warning(self.__msg.format("name", inst_cat + "_" + inst_name, self.__add1,
#                                self.full_name, self.__add2))
#             else:
#                 self._database[inst_cat][inst_name] = OrderedDict()
#         else:
#             logger.warning(self.__msg.format("category", inst_cat, self.__rm1, self.full_name,
#                                              self.__add2))
#
#     def rm_instname(self, inst_name, inst_cat):
#         """Add an instrument name to an instrument category."""
#         if self.has_instcat(inst_cat):
#             res = self._database[inst_cat].pop(inst_name, None)
#             if res is None:
#                 logger.warning(self.__msg.format("name", inst_cat + "_" + inst_name, self.__rm1,
#                                                  self.full_name, self.__rm2))
#         else:
#             logger.warning(self.__msg.format("category", inst_cat, self.__rm1, self.full_name,
#                                              self.__rm2))
#
#     def get_instnames(self, inst_cat=None):
#         """Return the list instrument names in the database."""
#         return get_content_2ndlevel(self._database, level1_key=inst_cat)
#
#     def has_instname(self, inst_name, inst_cat):
#         """Return True if inst_name is an existing instrument name in the instrument category."""
#         if self.has_instcat(inst_cat):
#             return inst_name in self.get_instnames(inst_cat=inst_cat)
#         else:
#             return False
#
#     def add_instmodel(self, inst_model, inst_name, inst_cat, **kwargs):
#         """Add an instrument model to an instrument name of an instrument category."""
#         inst_model, inst_name, inst_cat = check_args(inst_model=inst_model, inst_name=inst_name,
#                                                      inst_cat=inst_cat, **kwargs)
#         if self.has_instname(inst_name, inst_cat):
#             if self.has_instmodel(inst_model, inst_name, inst_cat):
#                 logger.warning(self.__msg.format("model", inst_cat + "_" + inst_name + "_" +
#                                                  inst_model, self.__add1, self.full_name,
#                                                  self.__add2))
#             else:
#                 self._database[inst_cat][inst_name][inst_model] = self.__def_instmod_level
#         else:
#             logger.warning(self.__msg.format("name", inst_cat + "_" + inst_name, self.__rm1,
#                                              self.full_name, self.__add2))
#
#     def rm_instmodel(self, inst_model, inst_name, inst_cat, **kwargs):
#         """Add an instrument name to an instrument category."""
#         inst_model, inst_name, inst_cat = check_args(inst_model=inst_model, inst_name=inst_name,
#                                                      inst_cat=inst_cat, **kwargs)
#         if self.has_instname(inst_name, inst_cat):
#             res = self._database[inst_cat][inst_name].pop(inst_model, "notfound")
#             if res == "notfound":
#                 logger.warning(self.__msg.format("model", inst_cat + "_" + inst_name + "_" +
#                                                  inst_model, self.__rm1, self.full_name,
#                                                  self.__rm2))
#         else:
#             logger.warning(self.__msg.format("name", inst_cat + "_" + inst_name, self.__rm1,
#                                              self.full_name, self.__rm2))
#
#     def get_instmodels(self, inst_name=None, inst_cat=None):
#         """Return the list instrument names in the database."""
#         return get_content_3ndlevel(self._database, level1_key=inst_cat, level2_key=inst_name)
#
#     def has_instmodel(self, inst_model, inst_name, inst_cat, **kwargs):
#         """Return True if inst_model exist in the database for the category and name provided."""
#         inst_model, inst_name, inst_cat = check_args(inst_model=inst_model, inst_name=inst_name,
#                                                      inst_cat=inst_cat, **kwargs)
#         if self.has_instname(inst_name, inst_cat):
#             return inst_model in self.get_instmodels(inst_name=inst_name, inst_cat=inst_cat)
#         else:
#             return False
#
#     @classmethod
#     def _is_object_default(cls, object):
#         return object is cls.__def_instmod_level
#
#     def has_object(self, inst_model, inst_name, inst_cat, **kwargs):
#         """Return True if an object is stored in the database for the category, name and model."""
#         inst_model, inst_name, inst_cat = check_args(inst_model=inst_model, inst_name=inst_name,
#                                                      inst_cat=inst_cat, **kwargs)
#         if self.has_instmodel(inst_model, inst_name, inst_cat):
#             return self._is_object_default(self._database[inst_cat][inst_name][inst_model])
#         else:
#             return False
#
#     def add_object(self, object, inst_model, inst_name, inst_cat, force=False, **kwargs):
#         """ Add an object to the database."""
#         inst_model, inst_name, inst_cat = check_args(inst_model=inst_model, inst_name=inst_name,
#                                                      inst_cat=inst_cat, **kwargs)
#         add_object = False
#         if self.has_instmodel(inst_model, inst_name, inst_cat):
#             if self.get_object(inst_model, inst_name, inst_cat) is self.__def_instmod_level:
#                 add_object = True
#             else:
#                 if force:
#                     logger.info(self.__msg.format("model", inst_cat + "_" + inst_name + "_" +
#                                                   inst_model, self.__addobjforce1, self.full_name))
#                     add_object = True
#                 else:
#                     raise ValueError(self.__msg.format("model", inst_cat + "_" + inst_name + "_" +
#                                                        inst_model, self.__addobj1, self.full_name,
#                                                        self.__addobj2))
#         else:
#             add_object = True
#             if not(self.has_instcat(inst_cat)):
#                 self.add_instcat(inst_cat)
#             if not(self.has_instname(inst_name, inst_cat)):
#                 self.add_instname(inst_name, inst_cat)
#         if add_object:
#             self._database[inst_cat][inst_name][inst_model] = object
#             logger.debug("Added instrument model {} in model {}"
#                          "".format(inst_cat + '_' + inst_name + '_' + inst_model, self.name))
