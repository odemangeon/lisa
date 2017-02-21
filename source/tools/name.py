#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
name module.

Provide the Name interface Class.

@TODO:
    - See if it's not better to do a try catch in hasnameprefix instead of using the hasattr
      function as in default_folders_data_run.
"""
from logging import getLogger

## Logger object
logger = getLogger()


def check_name_for_prohibitedchar(name, prohibitedchars=""):
    """Check that there is no prohibited characters in name and remove it if there is."""
    if not isinstance(name, str):
        raise ValueError("Name should be a string or None")
    result = name
    for char in prohibitedchars:
        if result.count(char) > 0:
            result = result.replace(char, "")
            logger.warning("Name can't contain {} caracter so they have been removed.".format(char))
    if result != name:
        logger.warning("Proposed name: {}, Returned name: {}".format(name, result))
    return result


def check_name(name):
    """Check that there is no '_' in name and remove it if there is."""
    return check_name_for_prohibitedchar(name=name, prohibitedchars="_")


def check_name_code(name):
    """Check that there is no '-' in name and remove it if there is."""
    return check_name_for_prohibitedchar(name=name, prohibitedchars="-")


class Name(object):
    """docstring for Name."""
    def __init__(self, name, name_prefix=None):
        # 1.
        self.__name = check_name(name)
        logger.debug("Name of the instance of class {} set to {}.".format(self.__class__.__name__,
                                                                          self.name))
        # 2.
        self.name_prefix = name_prefix
        # 3.
        if type(self) is Name:
            raise NotImplementedError("Name should not be instanciated !")

    @property
    def name(self):
        """Return the name of the instance."""
        return self.__name

    @property
    def name_prefix(self):
        """Return the name of the instance."""
        return self.__name_prefix

    @property
    def hasnameprefix(self):
        """Return True is name_prefix has been set already, False otherwise."""
        return hasattr(self, "name_prefix")

    @name_prefix.setter
    def name_prefix(self, name_prefix):
        """Set the prefix of the ame of the instance."""
        if self.hasnameprefix:
                logger.warning("The name prefix of the instance has already been defined."
                               "One should not redefined it so set command is ignored.")
        else:
            if name_prefix is None:
                logger.debug("No name_prefix provided for instance {} of class {}."
                             "".format(self.name, self.__class__.__name__))
            else:
                logger.debug("Name prefix of instance {} of class {} set to {}."
                             "".format(self.name, self.__class__.__name__, name_prefix))
                self.__name_prefix = name_prefix

    @property
    def full_name(self):
        """Return the full name of the instance."""
        if self.hasnameprefix:
            return self.name_prefix + "_" + self.name
        else:
            return self.name

    @property
    def name_code(self):
        """Return the name of the instance that can be used in code."""
        return check_name_code(self.name)

    @property
    def full_name_code(self):
        """Return the full name of the CelestialBody."""
        return check_name_code(self.full_name)
