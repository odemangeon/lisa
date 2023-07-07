#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
dico_database module.

The objective of this package is to provides a toolbox to manipulate dico_datases

@ DONE:
    -
@TODO:
    -
"""
from loguru import logger
from collections import defaultdict
from copy import deepcopy, copy
from .lockable_dict import LockableDict


def init_result(sortby_lvl1key=False, sortby_lvl2key=False, sortby_lvl3key=False,
                default_value=None):
    """Return a lsit a Nesteddict_wfixellvlnb or a dict."""
    if sum([sortby_lvl1key, sortby_lvl2key, sortby_lvl3key]) == 3:
        result = Nesteddict_wfixellvlnb(nb_lvl=3, default=default_value)
    elif sum([sortby_lvl1key, sortby_lvl2key, sortby_lvl3key]) == 2:
        result = Nesteddict_wfixellvlnb(nb_lvl=2, default=default_value)
    elif sum([sortby_lvl1key, sortby_lvl2key, sortby_lvl3key]) == 1:
        if isinstance(default_value, type):
            result = defaultdict(default_value)
        else:
            result = defaultdict(type(default_value))
    else:
        result = []
    # logger.debug("Result initialised with {}".format(result))
    return result


def add_obj_in_result(result, obj, lvl1_key=None, lvl2_key=None, lvl3_key=None,
                      sortby_lvl1key=False, sortby_lvl2key=False, sortby_lvl3key=False,
                      type_finallvl=None):
    if sortby_lvl1key and sortby_lvl2key and sortby_lvl3key:
        if type_finallvl is list:
            if isinstance(obj, list):
                result[lvl1_key][lvl2_key][lvl3_key].extend(obj)
            else:
                result[lvl1_key][lvl2_key][lvl3_key].append(obj)
        else:
            result[lvl1_key][lvl2_key][lvl3_key] = obj
    elif sortby_lvl1key and sortby_lvl3key:
        if type_finallvl is list:
            if isinstance(obj, list):
                result[lvl1_key][lvl3_key].extend(obj)
            else:
                result[lvl1_key][lvl3_key].append(obj)
        else:
            result[lvl1_key][lvl3_key] = obj
    elif sortby_lvl1key and sortby_lvl2key:
        if type_finallvl is list:
            if isinstance(obj, list):
                result[lvl1_key][lvl2_key].extend(obj)
            else:
                result[lvl1_key][lvl2_key].append(obj)
        else:
            result[lvl1_key][lvl2_key] = obj
    elif sortby_lvl2key and sortby_lvl3key:
        if type_finallvl is list:
            if isinstance(obj, list):
                result[lvl2_key][lvl3_key].extend(obj)
            else:
                result[lvl2_key][lvl3_key].append(obj)
        else:
            result[lvl2_key][lvl3_key] = obj
    elif sortby_lvl1key:
        if type_finallvl is list:
            if isinstance(obj, list):
                result[lvl1_key].extend(obj)
            else:
                result[lvl1_key].append(obj)
        else:
            result[lvl1_key] = obj
    elif sortby_lvl2key:
        if type_finallvl is list:
            if isinstance(obj, list):
                result[lvl2_key].extend(obj)
            else:
                result[lvl2_key].append(obj)
        else:
            result[lvl2_key] = obj
    elif sortby_lvl3key:
        if type_finallvl is list:
            if isinstance(obj, list):
                result[lvl3_key].extend(obj)
            else:
                result[lvl3_key].append(obj)
        else:
            result[lvl3_key] = obj
    else:
        if isinstance(obj, list):
            result.extend(obj)
        else:
            result.append(obj)
    return result


class Nesteddict(LockableDict):
    def __init__(self, ordered=False, lock=None):
        super(Nesteddict, self).__init__(ordered=ordered, lock=lock)

    def __missing__(self, key):
        value = self[key] = type(self)(ordered=self.ordered, lock=self.get_Lock_instance())
        return value


class Nesteddict_wlvl(Nesteddict):
    """docstring for Nesteddict_wlvl."""
    def __init__(self, lvl=0, ordered=False, lock=None):
        super(Nesteddict_wlvl, self).__init__(ordered=ordered, lock=lock)
        self.__lvl = lvl

    def __missing__(self, key, cls=None):
        # for Inheritance when you don't to create instance of the subclass
        if cls is None:
            cls = type(self)
        # retain local pointer to value
        value = self[key] = cls(self.lvl + 1, ordered=self.ordered, lock=self.get_Lock_instance())
        return value                      # faster to return than dict lookup

    def __copy__(self):
        new = type(self)(lvl=self.lvl, ordered=self.ordered, lock=self.lock)
        for key, value in self.items():
            new[key] = value
        return new

    def __deepcopy__(self, memo={}):
        new = type(self)(lvl=self.lvl, ordered=self.ordered, lock=self.lock)
        for key, value in self.items():
            new[key] = deepcopy(value, memo)
        return new

    @property
    def lvl(self):
        """Return the current level number."""
        return self.__lvl


class Nesteddict_wfixellvlnb(Nesteddict_wlvl):
    """docstring for Nesteddict_wfixellvlnb."""
    def __init__(self, nb_lvl, lvl=0, ordered=False, default=None, lock=None):
        super(Nesteddict_wfixellvlnb, self).__init__(lvl=lvl, ordered=ordered, lock=lock)
        self.__nb_lvl = nb_lvl
        self.__default = default

    def __missing__(self, key, cls=None):
        if cls is None:
            cls = type(self)
        if self.lvl < (self.nb_lvl - 1):
            value = self[key] = cls(nb_lvl=self.nb_lvl, lvl=self.lvl + 1,
                                    ordered=self.ordered, default=self.default,
                                    lock=self.get_Lock_instance())
        else:
            value = self[key] = self.default
        return value

    def __copy__(self):
        new = type(self)(nb_lvl=self.nb_lvl, lvl=self.lvl, ordered=self.ordered,
                         default=self.default)
        for key, value in self.items():
            new[key] = value
        return new

    def __deepcopy__(self, memo={}):
        new = type(self)(nb_lvl=self.nb_lvl, lvl=self.lvl, ordered=self.ordered,
                         default=self.default)
        for key, value in self.items():
            new[key] = deepcopy(value, memo)
        return new

    @property
    def nb_lvl(self):
        """Return the number of levels in the nested dictionnary."""
        return self.__nb_lvl

    @property
    def default(self):
        """Return the default value for the last level."""
        if isinstance(self.__default, type):
            return self.__default()
        else:
            return copy(self.__default)

    def get_lvl2_keys(self, level1_key=None, sortby_lvl1key=False):
        """Return the keys of the 2nd level in the nested dictionary.

        If the level1 key is specified return only the 2nd level keys of the this key otherwise
        return them for all the level 1 keys.
        If sortby_lvl1key is False, return 1 list with all the 2nd level keys. If True return a dict
        with for keys the level 1 keys and for values the list of level 2 keys for each level 1 key.
        """
        if self.nb_lvl < 2:
            raise ValueError("get_lvl2_keys can only be used for Nesteddict_wfixellvlnb instance "
                             "with nb_lvl superior or equal to 2")
        result = init_result(sortby_lvl1key=sortby_lvl1key, default_value=[])
        if level1_key is None:
            iter_level1key = self.keys()
        else:
            iter_level1key = [level1_key, ]
        for key_lvl1 in iter_level1key:
            if key_lvl1 in self:
                keys_level2 = list(self[key_lvl1].keys())
                add_obj_in_result(result, keys_level2, lvl1_key=key_lvl1,
                                  sortby_lvl1key=sortby_lvl1key, type_finallvl=list)
        return result

    def get_lvl2_values(self, level1_key=None, sortby_lvl1key=False, sortby_lvl2key=False,
                        raise_duplicateerror=True):
        """Return the values of the 2nd level in the nested dictionary.

        If the level1 key is specified return only the 2nd level values of the this key otherwise
        return them for all the level 1 keys.
        If sortby_lvl1key is False, return 1 list with all the 2nd level values. If True return a
        dict with for keys the level 1 keys and for values the list of level 2 keys for each level 1
        key.
        """
        if self.nb_lvl < 2:
            raise ValueError("get_lvl2_values can only be used for Nesteddict_wfixellvlnb instance "
                             "with nb_lvl superior or equal to 2.")
        if sortby_lvl1key and sortby_lvl2key:
            if raise_duplicateerror:
                raise ValueError("It doesn't make sense to ask to sort by level 1 and level 2 keys."
                                 " The result is the self itself or self[level1_key]!")
            else:
                if level1_key is None:
                    return deepcopy(self)
                else:
                    if level1_key in self:
                        return deepcopy(self[level1_key])
                    else:
                        return {}
        else:
            result = init_result(sortby_lvl1key=sortby_lvl1key, sortby_lvl2key=sortby_lvl2key,
                                 default_value=[])
        if level1_key is None:
            iter_level1key = self.keys()
        else:
            iter_level1key = [level1_key, ]
        for key_lvl1 in iter_level1key:
            for key_lvl2, value_lvl2 in self[key_lvl1].items():
                add_obj_in_result(result, value_lvl2, lvl1_key=key_lvl1, lvl2_key=key_lvl2,
                                  sortby_lvl1key=sortby_lvl1key, sortby_lvl2key=sortby_lvl2key,
                                  type_finallvl=list)
        return result

    def get_lvl3_keys(self, level1_key=None, level2_key=None,
                      sortby_lvl1key=False, sortby_lvl2key=False):
        """Return the keys of the 3nd level in the nested dictionary.

        If the level1 key is specified return only the 2nd level keys of the this key otherwise
        return them for all the level 1 keys.
        If sortby_lvl1key is False, return 1 list with all the 2nd level keys. If True return a dict
        with for keys the level 1 keys and for values the list of level 2 keys for each level 1 key.
        """
        if self.nb_lvl < 3:
            raise ValueError("get_lvl3_keys can only be used for Nesteddict_wfixellvlnb instance "
                             "with nb_lvl superior or equal to 3")
        result = init_result(sortby_lvl1key=sortby_lvl1key, sortby_lvl2key=sortby_lvl2key,
                             default_value=[])
        if level1_key is None:
            iter_level1key = self.keys()
        else:
            iter_level1key = [level1_key, ]
        for key_lvl1 in iter_level1key:
            res = self[key_lvl1].get_lvl2_keys(level1_key=level2_key, sortby_lvl1key=sortby_lvl2key)
            if len(res) > 0:
                if sortby_lvl1key:
                    result[key_lvl1] = res
                else:
                    if sortby_lvl2key:
                        for key_lvl2, list_key_lvl3 in res.items():
                            result[key_lvl2].extend(list_key_lvl3)
                    else:
                        result.extend(res)
        return result

    def get_lvl3_values(self, level1_key=None, level2_key=None,
                        sortby_lvl1key=False, sortby_lvl2key=False, sortby_lvl3key=False):
        """Return the values of the 3nd level in the nested dictionary.

        If the level1 key is specified return only the 2nd level values of the this key otherwise
        return them for all the level 1 keys.
        If sortby_lvl1key is False, return 1 list with all the 2nd level values. If True return a
        dict with for keys the level 1 keys and for values the list of level 2 keys for each level 1
        key.
        """
        if self.nb_lvl < 3:
            raise ValueError("get_lvl3_values can only be used for Nesteddict_wfixellvlnb instance "
                             "with nb_lvl superior or equal to 3.")
        if sortby_lvl1key and sortby_lvl2key and sortby_lvl3key:
            raise ValueError("It doesn't make sense to ask to sort by level 1 and level 2 keys."
                             "The result is the self itself or self[level1_key]([level2_key])!")
        else:
            result = init_result(sortby_lvl1key=sortby_lvl1key, sortby_lvl2key=sortby_lvl2key,
                                 sortby_lvl3key=sortby_lvl3key, default_value=list)
        if level1_key is None:
            iter_level1key = self.keys()
        else:
            iter_level1key = [level1_key, ]
        for key_lvl1 in iter_level1key:
            res = self[key_lvl1].get_lvl2_values(level1_key=level2_key,
                                                 sortby_lvl1key=sortby_lvl2key,
                                                 sortby_lvl2key=sortby_lvl3key,
                                                 raise_duplicateerror=False)
            if len(res) > 0:
                if sortby_lvl1key:
                    result[key_lvl1] = res
                else:
                    if sortby_lvl2key and sortby_lvl3key:
                        for key_lvl2, values_lvl2 in res.items():
                            for key_lvl3 in res[key_lvl2]:
                                result[key_lvl2][key_lvl3].append(res[key_lvl2][key_lvl3])
                    elif sortby_lvl2key or sortby_lvl3key:
                        for key_lvl, values in res.items():
                            result[key_lvl].extend(values)
                    else:
                        result.extend(res)
        return result
