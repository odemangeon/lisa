#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
dataset_with_instrument_level module.

The objective of this package is to provides a database object with instrument levels.
The instrument levels are instrument category, instrument name, instrument model

@ DONE:
    -
@TODO:
    - Perhaps had a check existance attribute to the database that will prevent to automatically
      create a new entry when it doesn't exists.
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
    def __init__(self, object_stored, database_name=None, lock=None, ordered=False, default=None):
        Name.__init__(self, name=object_stored, name_prefix=database_name)
        Nesteddict_getitIMFN.__init__(self, nb_lvl=3, lock=lock, ordered=ordered, default=default)

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

    def hasatleast1instmod(self, inst_name=None, inst_cat=None):
        """Return True if inst_name contain at least one inst_mod."""
        return len(self.get_instmodels(inst_name=inst_name, inst_cat=inst_cat)) > 0
