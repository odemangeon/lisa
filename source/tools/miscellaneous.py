#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
miscellaneous module.

Provide toolbox with miscellaneous tools.

@TODO:
"""
import logging


## Logger object
logger = logging.getLogger()


def spacestring_like(string):
    """Return an empty string with the same size than string."""
    return " " * len(string)


def check_name(name):
    """Check that there is no '_' in name and remove it if there is."""
    if name.count("_") > 0:
        logger.warning("name can't contain '_' caracter so they have been removed."
                       " Got {}".format(name))
        return name.replace("_", "")
    else:
        return name


def check_name_code(name):
    """Check that there is no '-' in name and remove it if there is."""
    if name.count("-") > 0:
        logger.warning("name can't contain '-' caracter so they have been removed."
                       " Got {}".format(name))
        return name.replace("-", "")
    else:
        return name
