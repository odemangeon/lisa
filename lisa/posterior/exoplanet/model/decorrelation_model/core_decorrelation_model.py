#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Decorrelation model module.
"""
from logging import getLogger


## Logger object
logger = getLogger()


class DecorrelationModelInterface(LinearDecorrelationInterface):
    """docstring for DecorrelationModelInterface.

    This is an interface class for subclasses of the Core_Model class.
    """

    # models available for the indicators
    __available_decorrelation_models__ = [LinearDecorrelationInterface._method_name, ]  # The first one is the default one

    # Define the dictionary providing the default parameters values for each model
    _default_param_values_4_decorrelation_model = {LinearDecorrelationInterface._method_name: LinearDecorrelationInterface._default_param_values}

    # String giving the name of the dictionary used to define the model to use for each indicator in the parameter file
    __names_decorrelation_model_dict = {LinearDecorrelationInterface._method_name: LinearDecorrelationInterface._name_model_dict}

    # models available for the indicators
    __available_quantities__ = ["raw", "residuals", "model"]  # The first one is the default one
    __available_decorrelation_function__ = ["linear", "quadratic"]  # The first one is the default one

    def __init__(self):
        # Define the dictionary giving the function to use to create the text of the dictionaries to defined the paremeters of each model for the parameter file
        self.__create_text_decorrelation_methods = {self._linear: self.__create_text_lineardecorr_model}
        # Define the dictionary giving the function to use to load the text of the dictionaries to defined the paremeters of each model for the parameter file
        self.__load_text_decorrelation_methods = {self._linear: self.__load_text_lineardecorr_model}
