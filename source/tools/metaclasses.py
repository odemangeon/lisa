#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
metaclasses module.

Provide the MandatoryReadOnlyAttr, MandatoryMethods and CategorisedType metaclass.

@TODO:
"""
from logging import getLogger

## Logger object
logger = getLogger()


def getinstattr(attrname):
    def _getmethod(self):
        return getattr(self, "__{}__".format(attrname))

    return _getmethod


def getclassattr(attrname):
    def _getmethod(cls):
        return getattr(cls, "__{}__".format(attrname))

    return _getmethod


class MandatoryReadOnlyAttr(type):

    def __new__(cls, classname, bases, classdict):
        for attr in classdict.get("__mandatoryattrs__", []):
            setattr(cls, attr, property(getclassattr(attr)))
            # print(cls, classname, bases, classdict)
            classdict[attr] = property(getinstattr(attr))
        return super(MandatoryReadOnlyAttr, cls).__new__(cls, classname, bases, classdict)

    def __init__(cls, name, bases, attrs):
        # print(cls, name, bases, attrs)
        if name.startswith("Core_"):
            missing_attrs = ["{}".format(attr) for attr in ["__mandatoryattrs__"]
                             if not hasattr(cls, attr)]
            if len(missing_attrs) > 0:
                raise AttributeError("class '{}' requires attribute {}".format(name, missing_attrs))
        if not(name.startswith("Core_")) and not(name.startswith("Default_")):
            # Check for missing attributes
            missing_attrs = ["{}".format(attr) for attr in getattr(cls, "__mandatoryattrs__", [])
                             if not hasattr(cls, attr)]
            if len(missing_attrs) > 0:
                raise AttributeError("class '{}' requires attribute {}".format(name, missing_attrs))


class MandatoryMethods(type):

    def __init__(cls, name, bases, attrs):
        # print(cls, name, bases, attrs)
        if not(name.startswith("Core_")):
            # Check for missing attributes
            missing_meths = ["{}".format(meth) for meth in getattr(cls, "__mandatorymeths__", [])
                             if not hasattr(cls, meth)]
            if len(missing_meths) > 0:
                raise AttributeError("class '{}' requires attribute {}".format(name, missing_meths))


def getcategory():
    def _getmethod(self):
        return self.__category__
    return _getmethod


class CategorisedType(type):

    @property
    def category(cls):
        """Return the category of the object."""
        return cls.__category__

    def __new__(cls, classname, bases, classdict):
        classdict["category"] = property(getcategory())
        return super(CategorisedType, cls).__new__(cls, classname, bases, classdict)

    def __init__(cls, name, bases, attrs):
        if not(name.startswith("Core_")) and not(name.startswith("Default_")):
            missing_attrs = ["{}".format(attr) for attr in ["__category__"]
                             if not hasattr(cls, attr)]
            if len(missing_attrs) > 0:
                raise AttributeError("class '{}' requires attribute {}".format(name, missing_attrs))
