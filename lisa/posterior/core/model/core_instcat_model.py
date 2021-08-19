#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
core_instcat_model module.

The objective of this package is to provides the core Core_InstCat_Model class.
It is a Parent meant to be subclassed and which defines what the subclasses needs to implement.
These subclasses will be used as interface classes for a Core_Model subclass to provide the necessary
methods and attributes to model a data of a given insttument category.

@DONE:
    -

@TODO:
    -
"""
from ....tools.metaclasses import MandatoryReadOnlyAttrAndMethod


class Core_InstCat_Model(MandatoryReadOnlyAttrAndMethod):

    __mandatorymeths__ = ["datasim_creator", "create_instcat_paramfile", "load_instcat_paramfile"]
    # datasim_creator: Methods that creates the datasimulator functions
    # create_instcat_paramfile: Methods to create the param file specific to the instrument category
    #   This methods needs to be defined even if there is no specific instcat_paramfile.
    #   Just make a function that raises an error
    # load_instcat_paramfile: Methods to load the param file specific to the instrument category
    #   This methods needs to be defined even if there is no specific instcat_paramfile.
    #   Just make a function that raises an error
    __mandatoryattrs__ = ["inst_cat", "has_instcat_paramfile", "datasim_creator_name"]
    # inst_cat: string specifiying the instrument category that the InstCat_Model will handle
    # has_instcat_paramfile: bool that says if there is an instcat specific param_file
    # datasim_creator_name: str giving the name of the datasim creator function.
    #   If the same name is used for several inst_cat then the Model will use the same datasimcreator method
    #   for several inst_cat meaning that the datasim_creator function needs to handle them all.
