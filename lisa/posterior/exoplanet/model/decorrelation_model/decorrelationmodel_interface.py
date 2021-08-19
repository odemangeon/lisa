#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Decorrelation model interface module.

TODO:
- If I want several decorrelation methods beside the Linear Decorrelation and do not want to have to
modify this module than I will need to implement a decorrelation method manager.
"""
from logging import getLogger

from .linear_decorrelation import LinearDecorrelation


## Logger object
logger = getLogger()


class DecorrelationModelInterface(LinearDecorrelation):
    """docstring for DecorrelationModelInterface.

    This is an interface class for subclasses of the Core_Model class.
    """

    # models available for the indicators
    __available_decorrelationmodel_class__ = {LinearDecorrelation.category: LinearDecorrelation, }  # The first one is the default one

    # Each dec
    # TO BE DELETED
    # # Define the dictionary providing the default parameters values for each model
    # _default_param_values_4_decorrelation_model = {LinearDecorrelationInterface._method_name: LinearDecorrelationInterface._default_param_values}
    #
    # String giving the name of the dictionary used to define the model to use for each decorrelation in the instrument category specific parameter file
    # __names_decorrelation_model_dict = {LinearDecorrelationInterface._method_name: LinearDecorrelationInterface._name_model_dict}

    # models available for the indicators
    __available_decorrelation_quantities__ = ["raw", ]  # "residuals", "model", The first one is the default one

    def __init__(self):
        # Define the dictionary giving the function to use to create the text of the dictionaries to defined the paremeters of each model for the parameter file
        self.__create_text_decorrelation_methods = {self._linear: self.__create_text_lineardecorr_model}
        # Define the dictionary giving the function to use to load the text of the dictionaries to defined the paremeters of each model for the parameter file
        self.__load_text_decorrelation_methods = {self._linear: self.__load_text_lineardecorr_model}

    def get_available_decorrelationmodel_4_instcat(inst_cat):
        """Return the list of available decorrelation model name for a given instrument category
        """
        raise NotImplementedError

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

    def create_specific_text_decorrelationmodel(inst_cat, decorrelationmodel, datasets):
        """Return the text to be written in an inst_cat specific param_file for a given decorrelation model

        Arguments
        ---------
        inst_cat            : str
            Instrument category of the param_file in which you wish to write the decorrelation model text.
            Necessary to access the right function.
        decorrelationmodel  : str
            Category of decorrelation model of which you wish to write the text.
            Necessary to access the right function.
        datasets            : list of Datasets?
            List of datasets of category inst_cat for which the decorrelation model decorrelationmodel
            has been chosen.
            Necessary for all datasets to be addressed in the text.
        """
        raise NotImplementedError

    def load_specific_text_decorrelationmodel(dico_inputs, inst_cat, decorrelationmodel, datasets):
        """Load the dictionary from the inst_cat specific param_file for a given decorrelation model

        Arguments
        ---------
        dico_inputs         : dict
            Dictionary which contains the content of the inst_cat specific parameter file.
        inst_cat            : str
            Instrument category of the param_file in which you wish to write the decorrelation model text.
            Necessary to access the right function that will load the content
        decorrelationmodel  : str
            Category of decorrelation model of which you wish to write the text.
            Necessary to access the right function and the right dictionary within dico_inputs.
        datasets            : list of Datasets?
            List of datasets of category inst_cat for which the decorrelation model decorrelationmodel
            has been chosen. To check that all of them are actually addressed and store the info properly.
        """
        raise NotImplementedError
