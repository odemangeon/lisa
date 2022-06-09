#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
indicator module.

The objective of this package is to provides the IND_Instrument and IND_Dataset classes.

@TODO:
"""
from logging import getLogger
import matplotlib.pyplot as plt
from numpy import array

from .dataset import Core_DatasetTimeSeries
from .instrument import Core_Instrument


## Logger
logger = getLogger()

## IND instrument category
IND_inst_cat = "IND"


class IND_Instrument(Core_Instrument):
    """docstring for RV_Instrument."""

    __category__ = IND_inst_cat
    __sub_category__ = "indicator_category"
    __params_model__ = {}
    # __mean_level__ = "mean"
    # __drift_basename__ = "drift"

    def __init__(self, name, subcat, model=None, params_indicator_models=None):
        self.__indicator_category = subcat
        self.__indicator_model = model
        self.__params_indicator_models = params_indicator_models
        super(IND_Instrument, self).__init__(name=name, subcat=subcat)

    @property
    def indicator_category(self):
        return self.__indicator_category

    @property
    def indicator_model(self):
        return self.__indicator_model

    @indicator_model.setter
    def indicator_model(self, value):
        self.__indicator_model = value

    @property
    def params_indicator_models(self):
        return self.__params_indicator_models

    @params_indicator_models.setter
    def params_indicator_models(self, dict):
        self.__params_indicator_models = dict


class IND_Dataset(Core_DatasetTimeSeries):
    """docstring for IND_Dataset class.

    This class is designed to habor a indicator data file.
    It contains functions to visualize (plot) and manipulate the indicator (detrend??)

    To be properly ingested, the datasets of this type have to obey to the following format:
    IND-{INDICATORTYPE}_{TARGETNAME}_{INSTRUMENTNAME}(_{NB}).txt
    {INDICATORTYPE} is the type of indicator
    {TARGETNAME} is the name of the target,
    {INSTRUMENTNAME} is the name of the instrument used,
    {NB} is the number of the dataset if there is several dataset on the same target and with the same instrument.
    The part in between parenthesis is facultative.
    """

    __instrument_subclass__ = IND_Instrument

    ## name of the data  and data error columns
    __data_column_name = "{}"
    __data_err_column_name = "{}_err"

    def __init__(self, file_path, instrument_instance):
        super(IND_Dataset, self).__init__(file_path, instrument_instance)
        filename_info = self.interpret_data_filename(self.filename)
        self.__indicator_category = filename_info["inst_subcat"]
        self.__data_column_name = self.__data_name.format(self.__indicator_category)
        self.__data_err_column_name = self.__data_err_name.format(self.__indicator_category)

    @property
    def indicator_category(self):
        """Get the category of indicator."""
        return self.__indicator_category


HARPS_FWHM = IND_Instrument("HARPS", subcat="FWHM")
ESPRESSO_FWHM = IND_Instrument("ESPRESSO", subcat="FWHM")
