#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Decorrelation model module.

TODO:
- If I want several decorrelation methods beside the Linear Decorrelation and do not want to have to
modify this module than I will need to implement a decorrelation method manager.
"""
from logging import getLogger

from ....tools.metaclasses import MandatoryReadOnlyAttrAndMethod


## Logger object
logger = getLogger()


class Core_DecorrelationModel(object, metaclass=MandatoryReadOnlyAttrAndMethod):
    """docstring for Core_DecorrelationModel class, Parent class of all Decorrelation Model Class"""

    ## List of mandatory arguments which have to be defined in the subclasses.
    # For example "category" is in this list. It has to be defined in the subclass as a class
    # attribute like this:
    # __category__ = "ModelCategory"
    # It then be read as self.category
    __mandatoryattrs__ = ["category", "name_dict_paramfile", "format_config_dict"]
    # category: String which designate the decorrelation model (for example: "linear"). To choose the
    #   decorrelation model to be used, the user will use this string.
    # name_dict_paramfile: String which gives the str to be used for the dictionary that will be used in the
    #   isntrument category specific paramfile to contain the parameter of the decorrelation method.
    __mandatorymeths__ = ["create_text_decorr_paramfile", "load_text_decorr_paramfile"]
    # create_text_instcat_paramfile: Method which create the text to be written in an instrument category
    #   specific paramfile to contain the parameterisation of the decorrelation models for each associated dataset.
    #   The arguments of this function are the inst_cat requested (inst_cat) and the list of Datasets object (datasets)
    # load_text_instcat_paramfile: Method which load the dictionary written in an instrument category
    #   specific paramfile and which contains the parameterisation of the decorrelation models for each associated dataset.
    #   The arguments of this function are the content of the inst_cat param file (dico_input), the
    #   inst_cat requested (inst_cat) and the list of Datasets object (datasets)
