#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
name module.

Provide the Name interface Class.

@TODO:
    - See if it's not better to do a try catch in hasnameprefix instead of using the hasattr
      function as in default_folders_data_run.
"""
from loguru import logger
from copy import deepcopy


def check_name_for_prohibitedchar(name, prohibitedchars="", verbose=0):
    """Check that there is no prohibited characters in name and remove it if there is."""
    if not isinstance(name, str):
        raise ValueError("Name should be a string or None")
    result = name
    for char in prohibitedchars:
        if result.count(char) > 0:
            result = result.replace(char, "")
            if verbose:
                logger.warning("Name can't contain {} caracter so they have been removed.".format(char))
    if result != name and verbose:
        logger.warning("Proposed name: {}, Returned name: {}".format(name, result))
    return result


def check_name(name, verbose=0):
    """Check that there is no '_' in name and remove it if there is."""
    return check_name_for_prohibitedchar(name=name, prohibitedchars="_", verbose=verbose)


def check_name_code(name, verbose=0):
    """Check that there is no '-' in name and remove it if there is."""
    return check_name_for_prohibitedchar(name=name, prohibitedchars="-", verbose=verbose)


def check_getname_kwargs(kwargs_getname):
    """Check the name of the argument provided with dictionnary for the Name.get method.

    :param dict kwargs_getname: Dictionary with the keyword argument to be later passed to the
        Name.get method.
    """
    set_valid_kwargs = set(["include_prefix", "code_version", "recursive", "prefix_kwargs"])
    if not(set_valid_kwargs >= set(kwargs_getname.keys())):
        raise TypeError("{} are not valid arguments for the Name.get method".format(set(kwargs_getname.keys()) - set_valid_kwargs))


class Name(object):
    """docstring for Name.

    Class to handle names. A Name is composed of a name with eventually a prefix. This can be seen
    and used as a first name (name) and a familly name (prefix). The prefix is stored as a Name
    instance itself.
    """
    def __init__(self, name, prefix=None):
        """Initialise the Name object

        Arguments
        ---------
        name : String
            first part of the name (like the first name of a person).
        prefix : String or Name
            rest of the name (like the family name(s) of a person)
        """
        # Specify the name
        self.__name = check_name(name)
        logger.debug("Name of the instance of class {} set to {}.".format(self.__class__.__name__,
                                                                          self.__name))
        # Specify the name prefix
        self.__prefix = None
        self.prefix = prefix

    # @property
    # def name(self):
    #     """Return the name of the instance."""
    #     return self.__name

    @property
    def prefix(self):
        """Return the name of the instance."""
        return self.__prefix

    @prefix.setter
    def prefix(self, prefix):
        """Set the prefix of the name of the instance."""
        if self.__prefix is not None:
            logger.warning("The name prefix of the instance has already been defined."
                           "One should not redefined it so set command is ignored.")
        else:
            if prefix is None:
                logger.debug("No name_prefix provided for instance {} of class {}."
                             "".format(self.__name, self.__class__.__name__))
            else:
                logger.debug("Name prefix of instance {} of class {} set to {}."
                             "".format(self.__name, self.__class__.__name__, prefix))
                if isinstance(prefix, str) or isinstance(prefix, Name):
                    if isinstance(prefix, str):
                        prefix = Name(name=prefix)
                else:
                    raise ValueError("prefix should be a string or a Name instance.")
                self.__prefix = prefix

    # @property
    # def name_prefix_code(self):
    #     """Return the name of the instance."""
    #     return check_name_code(self.__name_prefix, verbose=0)

    @property
    def has_prefix(self):
        """Return True is name_prefix has been set already, False otherwise."""
        return self.__prefix is not None

    # @property
    # def full_name(self):
    #     """Return the full name of the instance."""
    #     if self.hasnameprefix:
    #         return self.name_prefix.full_name + "_" + self.name
    #     else:
    #         return self.name
    #
    # @property
    # def name_code(self):
    #     """Return the name of the instance that can be used in code."""
    #     return check_name_code(self.name, verbose=0)
    #
    # @property
    # def full_name_code(self):
    #     """Return the full name of the CelestialBody."""
    #     return check_name_code(self.full_name, verbose=0)

    # DO NOT CHANGE THE DEFAULT VALUES !
    def get(self, include_prefix=False, code_version=False, recursive=False, prefix_kwargs=None):
        """Return the name of the parameter.

        :param bool include_prefix: If True (default False) include the name prefix in the output.
        :param bool code_version: If True (default False) return the code version of the name of the parameter
        :param bool recursive: If True (default False) apply the arguments include_prefix, code_version,
            and recursive itself to the prefix (Superseed the content of prefix_kwargs).
        :param dict prefix_kwargs: Dictionary with the arguments to pass to the get_name method of
            name_prefix
        :return str name: String providing the name
        """
        if prefix_kwargs is None:
            prefix_kwargs = {}
        else:
            prefix_kwargs = deepcopy(prefix_kwargs)
        if recursive:
            prefix_kwargs["include_prefix"] = include_prefix
            prefix_kwargs["code_version"] = code_version
            prefix_kwargs["recursive"] = True
        else:
            if include_prefix and ("code_version" not in prefix_kwargs):
                prefix_kwargs["code_version"] = code_version
        name = self.__name
        if code_version:
            name = check_name_code(name, verbose=0)
        if include_prefix and (self.has_prefix):
            name = self.prefix.get(**prefix_kwargs) + "_" + name
        return name

    def is_name(self, name):
        """Return True if the name provided is one formulation of the name of the instance.

        :param str name: Name provided
        :return bool res: True if the name provided is one formulation of the name of the instance.
        """
        for code_version in [True, False]:
            result = self.get(include_prefix=False, code_version=code_version, recursive=False)
            if result == name:
                return True
        full_prefix_kwargs = {}
        prefix_kwargs = full_prefix_kwargs
        while True:
            for code_version in [True, False]:
                new_result = self.get(include_prefix=True, code_version=code_version, recursive=False,
                                      prefix_kwargs=full_prefix_kwargs)
                if new_result == name:
                    return True
            if result == new_result:
                return False
            else:
                result = new_result
                prefix_kwargs["include_prefix"] = True
                prefix_kwargs["recursive"] = False
                prefix_kwargs["prefix_kwargs"] = {}
                prefix_kwargs = prefix_kwargs["prefix_kwargs"]


class Named(object):
    """docstring for Named.

    This is meant as an inferface for a class for which you want to have a Name.
    """

    def __init__(self, name, prefix=None, kwargs_getname_4_storename=None, kwargs_getname_4_codename=None, kwargs_getname_4_fullname=None):
        """docstring for Named.

        Arguments
        ---------
        name : String
            first part of the name (like the first name of a person).
        prefix: str/Name
            rest of the name (like the family name(s) of a person)
        kwargs_getname_4_storename : Dictionary
            Parameters for the Named.get_name method to construct the parameter names for storing in a param container database
        kwargs_getname_4_codename : Dictionary
            Parameters for the Named.get_name method to construct the parameter names for reference in codes.
        kwargs_getname_4_fullname : Dictionary
            Parameters for the Named.get_name method to construct the parameter full name for finding it.
        """
        self.__name = Name(name=name, prefix=prefix)
        ## Indicate the rules to construct the name for storage
        if kwargs_getname_4_storename is None:
            kwargs_getname_4_storename = {}
        check_getname_kwargs(kwargs_getname_4_storename)
        self.__store_name_rules = kwargs_getname_4_storename
        ## Indicate the rules to construct the name for code use
        if kwargs_getname_4_codename is None:
            kwargs_getname_4_codename = {}
        if "code_version" not in kwargs_getname_4_codename:
            kwargs_getname_4_codename["code_version"] = True
        check_getname_kwargs(kwargs_getname_4_codename)
        self.__code_name_rules = kwargs_getname_4_codename
        ## Indicate the rules to construct full name for finding the object
        if kwargs_getname_4_fullname is None:
            kwargs_getname_4_fullname = {"include_prefix": True, "recursive": True}
        check_getname_kwargs(kwargs_getname_4_fullname)
        self.__full_name_rules = kwargs_getname_4_fullname

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__, self.get_name(include_prefix=True, recursive=True))

    @property
    def name(self):
        """Return the name of the instance."""
        return self.__name

    @property
    def store_name_rules(self):
        """Rules used for the construction of the store name."""
        return self.__store_name_rules

    @property
    def store_name(self):
        """Store name for the Named Object.

        This name is used to store the Named Object in a paramcontainer database.
        """
        return self.get_name(**(self.store_name_rules))

    @property
    def code_name_rules(self):
        """Rules used for the construction of the code name."""
        return self.__code_name_rules

    @property
    def code_name(self):
        """Code name for the Named Object.

        This name is used to in the parameter file.
        """
        return self.get_name(**(self.code_name_rules))

    @property
    def full_name_rules(self):
        """Rules used for the construction of the full name."""
        return self.__full_name_rules

    @property
    def full_name(self):
        """Full name for the Named Object.

        This name is used to find the Named Object.
        """
        return self.get_name(**(self.full_name_rules))

    @property
    def full_code_name(self):
        """Code version of the full name for the Named Object.

        This name is used to find the Named Object.
        """
        name_rules = self.full_name_rules.copy()
        name_rules["code_version"] = True
        return self.get_name(**(name_rules))

    # DO NOT CHANGE THE DEFAULT VALUES !
    def get_name(self, include_prefix=False, code_version=False, recursive=False, prefix_kwargs=None):
        """Return the name of the parameter.

        :param bool include_prefix: If True (default False) include the name prefix in the output.
        :param bool code_version: If True (default False) return the code version of the name of the parameter
        :param bool recursive: If True (default False) apply the arguments include_prefix, code_version,
            and recursive itself to the prefix (Superseed the content of prefix_kwargs).
        :param dict prefix_kwargs: Dictionary with the arguments to pass to the get_name method of
            name_prefix
        :return str name: String providing the name of the instance
        """
        return self.name.get(include_prefix=include_prefix, code_version=code_version, recursive=recursive,
                             prefix_kwargs=prefix_kwargs)
