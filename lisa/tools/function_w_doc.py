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

    Attributes
    ----------
    arg_list : List of the arguments of the function
    function : The function itself. Note: DocFunction is callable and calls the function attibutes
        docfunction(...) is equivalent to docfunction.function(...)

    Methods
    -------
    info : Return a string with general info about the DocFunction instance
    """
    def __init__(self, function, arg_list):
        """
        Arguments
        ---------
        function : Function object
        arg_list : Usually OrderedDict describing the arguments of the function.
        """
        super(DocFunction, self).__init__()
        self.__function = function
        self.__arg_list = arg_list

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__, self.function)

    @property
    def function(self):
        """Return the function."""
        return self.__function

    @property
    def arg_list(self):
        """Return the list of arguments names."""
        return self.__arg_list

    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)

    @property
    def _info(self):
        """String with information about the function."""
        return "{repr}\narg_list: {arg_list}".format(repr=self.__repr__(), arg_list=self.arg_list)

    def info(self):
        """Provide informations about the function."""
        print(self._info)
