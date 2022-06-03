#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
function_w_doc module.

The objective of this package is to provides a class for  documented functions.

@ DONE:
    -
@TODO:
    -
"""
from logging import getLogger


## logger object
logger = getLogger()


class DocFunction(object):
    """DocFunction is a class to create dynamical function with documentation that can be queried at runtime.
    """
    def __init__(self, function, mand_kwargs_list=None, opt_kwargs_dict=None):
        """
        Arguments
        ---------
        function : Function object
        mand_kwargs_list : list
            List of the name of the mandatory arguments of the function
        opt_kwargs_dict  : dict
            Dictionary whose keys are the name of the optional arguments of the function and the values
            are the default values for these arguments
        """
        super(DocFunction, self).__init__()
        self.__function = function
        if mand_kwargs_list is None:
            mand_kwargs_list = []
        self.__mand_kwargs_list = mand_kwargs_list
        if opt_kwargs_dict is None:
            opt_kwargs_dict = {}
        self.__opt_kwargs_dict = opt_kwargs_dict

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__, self.function)

    @property
    def function(self):
        """Return the function."""
        return self.__function

    @property
    def mand_kwargs_list(self):
        """Return the list of mandatory keyword argument parameters"""
        return self.__mand_kwargs_list

    @property
    def opt_kwargs_dict(self):
        """Return the dictionary of the pair of optional argument name and their default value"""
        return self.__opt_kwargs_dict

    @property
    def all_kwargs_list(self):
        """Return the list of all the arguments names (mandatory and optional)."""
        return self.mand_kwargs_list + list(self.opt_kwargs_dict.keys())

    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)

    @property
    def _info(self):
        """String with information about the function."""
        return (f"{self.__repr__()}\nList of mandatory argument names: {self.mand}\n"
                f"List of optional arguments: {', '.join([f'{arg}={value}' for arg, value in self.mand_kwargs_dict])}"
                )

    def info(self):
        """Provide informations about the function."""
        print(self._info)
