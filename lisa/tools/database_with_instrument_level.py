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
from loguru import logger

from .name import Named
from .dico_database import Nesteddict_wfixellvlnb


__kwargs_names = ["inst_model", "inst_name", "inst_fullcat", "instmod_fullname"]


def check_args(inst_model=None, inst_name=None, inst_fullcat=None, instmod_fullname=None):
    """Check arguments for DatabaseInstLevel."""
    if ((inst_model is not None) or (inst_name is not None)) and (instmod_fullname is not None):
        raise ValueError("You should provide inst_model and inst_name or instmod_fullname not both")
    if instmod_fullname is not None:
        inst_model, inst_name = instmod_fullname.split("_")
    return inst_model, inst_name, inst_fullcat


def look4instcat(dico_db, inst_name):
    """Look in all the instrument categories to find the inst_fullcat corresponding to inst_name."""
    for inst_fullcat in dico_db:
        if inst_name in dico_db[inst_fullcat]:
            return inst_fullcat
    return None


def check_instfullcat(dico_db, inst_name, inst_fullcat):
    """Look in all the instrument categories to find the inst_fullcat corresponding to inst_name."""
    if (inst_name is not None) and (inst_fullcat is None):
        inst_fullcat = look4instcat(dico_db, inst_name)
        if inst_fullcat is None:
            raise ValueError("There is no instrument named {} in the database."
                             "".format(inst_name))
    return inst_fullcat, inst_name


class DatabaseInstLevel(Nesteddict_wfixellvlnb, Named):
    """docstring for DatabaseInstLevel.

    Subclass of Nesteddict_wfixellvlnb to implement a getitem with instrument model full name.
    """

    def __init__(self, object_stored, database_name=None, lock=None, ordered=False, default=None):
        Named.__init__(self, name=object_stored, prefix=database_name)
        Nesteddict_wfixellvlnb.__init__(self, nb_lvl=3, lock=lock, ordered=ordered, default=default)

    def __getitem__(self, key):
        if key in self:
            return super(DatabaseInstLevel, self).__getitem__(key)
        else:
            try:
                if self.lvl == 0:
                    # for inst_fullcat in self.inst_fullcategories:  # self.inst_categories doesn't
                    #     if key in self.get_instnames(inst_fullcat=inst_fullcat):
                    #         return self[inst_fullcat][key]
                    cuts = key.split("_")
                    assert len(cuts) == 3
                    inst_fullcat, inst_name, inst_model = cuts
                    return self[inst_fullcat][inst_name][inst_model]
                elif self.lvl == 1:
                    cuts = key.split("_")
                    assert len(cuts) == 3
                    inst_fullcat, inst_name, inst_model = cuts
                    return self[inst_name][inst_model]
                else:
                    raise KeyError
            except (AssertionError, KeyError):
                return super(DatabaseInstLevel, self).__getitem__(key)

    def __missing__(self, key, cls=None):
        return super(DatabaseInstLevel, self).__missing__(key, cls=Nesteddict_wfixellvlnb)

    def __repr__(self):
        return Named.__repr__(self) + ":" + Nesteddict_wfixellvlnb.__repr__(self)

    @property
    def database_name(self):
        """Return the name of the database."""
        return self.name.prefix.get_name()

    @property
    def object_stored(self):
        """Return the name of the objects stored in the database."""
        return self.get_name()

    @property
    def inst_fullcategories(self):
        """Return the list of current isntrument categories."""
        return list(self.keys())

    def has_instcat(self, inst_fullcat):
        """Return True if inst_fullcat is an existing instrument category."""
        return inst_fullcat in self

    def get_instnames(self, inst_fullcat=None, sortby_instfullcat=False):
        """Return the list instrument names in the database."""
        return self.get_lvl2_keys(level1_key=inst_fullcat, sortby_lvl1key=sortby_instfullcat)

    def has_instname(self, inst_name, inst_fullcat=None):
        """Return True if inst_name is an existing instrument name in the instrument category."""
        return inst_name in self.get_instnames(inst_fullcat=inst_fullcat)

    def get_instmodels(self, inst_name=None, inst_fullcat=None,
                       sortby_instname=False, sortby_instfullcat=False):
        """Return the list instrument names in the database."""
        return self.get_lvl3_keys(level1_key=inst_fullcat, level2_key=inst_name,
                                  sortby_lvl1key=sortby_instfullcat, sortby_lvl2key=sortby_instname)

    def has_instmodel(self, inst_model=None, inst_name=None, inst_fullcat=None, **kwargs):
        """Return True if inst_model exist in the database for the category and name provided."""
        inst_model, inst_name, inst_fullcat = check_args(inst_model=inst_model, inst_name=inst_name,
                                                         inst_fullcat=inst_fullcat, **kwargs)
        return inst_model in self.get_instmodels(inst_name=inst_name, inst_fullcat=inst_fullcat)

    def get_objects(self, inst_name=None, inst_fullcat=None,
                    sortby_instfullcat=False, sortby_instname=False, sortby_instmodel=False, **kwargs):
        inst_model, inst_name, inst_fullcat = check_args(inst_name=inst_name,
                                                         inst_fullcat=inst_fullcat, **kwargs)
        return self.get_lvl3_values(level1_key=inst_fullcat, level2_key=inst_name,
                                    sortby_lvl1key=sortby_instfullcat, sortby_lvl2key=sortby_instname,
                                    sortby_lvl3key=sortby_instmodel)

    def hasatleast1instmod(self, inst_name=None, inst_fullcat=None):
        """Return True if inst_name contain at least one inst_mod."""
        return len(self.get_instmodels(inst_name=inst_name, inst_fullcat=inst_fullcat)) > 0
