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


def check_name_for_prohibitedchar(name, prohibitedchars="", verbose=1):
    """Check that there is no prohibited characters in name and remove it if there is."""
    if not isinstance(name, str):
        raise ValueError("Name should be a string or None")
    result = name
    for char in prohibitedchars:
        if result.count(char) > 0:
            result = result.replace(char, "")
            if not(verbose):
                logger.warning("Name can't contain {} caracter so they have been removed.".format(char))
    if result != name and not(verbose):
        logger.warning("Proposed name: {}, Returned name: {}".format(name, result))
    return result


def check_name(name, verbose=1):
    """Check that there is no '_' in name and remove it if there is."""
    return check_name_for_prohibitedchar(name=name, prohibitedchars="_", verbose=verbose)


def check_name_code(name, verbose=1):
    """Check that there is no '-' in name and remove it if there is."""
    return check_name_for_prohibitedchar(name=name, prohibitedchars="-", verbose=verbose)


class Name(object):
    """docstring for Name."""
    def __init__(self, name, name_prefix=None):
        # 1.
        self.__name = check_name(name)
        logger.debug("Name of the instance of class {} set to {}.".format(self.__class__.__name__,
                                                                          self.name))
        # 2.
        self.__name_prefix = None
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
    def name_prefix_code(self):
        """Return the name of the instance."""
        return check_name_code(self.__name_prefix, verbose=0)

    @property
    def hasnameprefix(self):
        """Return True is name_prefix has been set already, False otherwise."""
        return self.__name_prefix is not None

    @name_prefix.setter
    def name_prefix(self, name_prefix):
        """Set the prefix of the ame of the instance."""
        if self.__name_prefix is not None:
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
        return check_name_code(self.name, verbose=0)

    @property
    def full_name_code(self):
        """Return the full name of the CelestialBody."""
        return check_name_code(self.full_name, verbose=0)

    def get_name(self, full_name=False, code_name=False, prefix=False):
        """Return the name of the parameter.

        :param bool full_name: If True (default False) return the full name of the parameter
        :param bool code_name: If True (default False) return the code version of the name of the parameter
        :param bool prefix: If True (default False) return the prefix of the full name of the parameter
            This argument and full_name cannot be true at the same time
        :return str name: String providing the name of the parameter
        """
        if full_name and prefix:
            raise ValueError("full_name and prefix cannot be True at the same time.")
        if prefix:
            name = self.name_prefix
        elif full_name:
            name = self.full_name
        else:
            name = self.name
        if code_name:
            return check_name_code(name, verbose=0)
