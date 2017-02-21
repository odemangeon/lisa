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
    """docstring for DocFunction."""
    def __init__(self, function, arg_list):
        super(DocFunction, self).__init__()
        self.__function = function
        self.__arg_list = arg_list

    @property
    def function(self):
        """Return the function."""
        return self.__function

    @property
    def arg_list(self):
        """Return the list of arguments names."""
        return self.__arg_list

    def __call__(self, *args):
        return self.function(*args)
