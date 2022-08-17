#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
core_indicator_model module.

The objective of this package is to provides the core Core_InstCat_Model class.
It is a Parent meant to be subclassed and which defines what the subclasses needs to implement.
These subclasses will be used as interface classes for a Core_Model subclass to provide the necessary
methods and attributes to model a data of a given insttument category.

@DONE:
    -

@TODO:
    - __available_decorrelation_quantities__ = ["raw", "residuals", "model"]. This choice will have to
    be made indicator by indicator
    - The load_config_decorrelation
"""
from .....tools.metaclasses import MandatoryReadOnlyAttrAndMethod


class Core_Indicator_Model(metaclass=MandatoryReadOnlyAttrAndMethod):
    """docstring for Core_Indicator_Model."""

    __mandatoryattrs__ = ["model_name", ]
    __mandatorymeths__ = ["get_dico_config", "set_dico_config", "get_dico_config"]
