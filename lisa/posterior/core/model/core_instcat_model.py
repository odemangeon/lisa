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
    - __available_decorrelation_quantities__ = ["raw", "residuals", "model"]. This choice will have to
    be made indicator by indicator
"""
from ....tools.metaclasses import MandatoryReadOnlyAttrAndMethod


class Core_InstCat_Model(metaclass=MandatoryReadOnlyAttrAndMethod):

    __mandatorymeths__ = ["datasim_creator", "create_instcat_paramfile", "load_instcat_paramfile"]
    # datasim_creator: Methods that creates the datasimulator functions
    # create_instcat_paramfile: Methods to create the param file specific to the instrument category
    #   This methods needs to be defined even if there is no specific instcat_paramfile.
    #   Just make a function that raises an error
    # load_instcat_paramfile: Methods to load the param file specific to the instrument category
    #   This methods needs to be defined even if there is no specific instcat_paramfile.
    #   Just make a function that raises an error
    __mandatoryattrs__ = ["inst_cat", "has_instcat_paramfile", "datasim_creator_name", "decorrelation_models"]
    # inst_cat: string specifiying the instrument category that the InstCat_Model will handle
    # has_instcat_paramfile: bool that says if there is an instcat specific param_file
    # datasim_creator_name: str giving the name of the datasim creator function.
    #   If the same name is used for several inst_cat then the Model will use the same datasimcreator method
    #   for several inst_cat meaning that the datasim_creator function needs to handle them all.
    # decorrelation_models: list of Decorrelation_Model classes implemented for the InstCat_Model

    @property
    def available_decorrelationmodel_names(self):
        """Return the list of available decorrelation model name
        """
        raise [Decor_Model.category for Decor_Model in self.decorrelation_models]

    def create_general_text_decorrelation():
        """Return the text to be written in any inst_cat specific param_file for to choose the decorrelation models
        for each dataset.
        """
        raise NotImplementedError

    def load_general_text_decorrelation():
        """Load the dict in any inst_cat specific param_file about to choosen the decorrelation models
        for each dataset.
        """
        raise NotImplementedError

    def create_decorr_specific_texts(self):
        """Return the text to be written in the param_file for all decorrelation models used.
        """
        raise NotImplementedError

    def load_decorr_specific_texts():
        """Load the dictionary from the param_file for all decorrelation models used.
        """
        raise NotImplementedError
