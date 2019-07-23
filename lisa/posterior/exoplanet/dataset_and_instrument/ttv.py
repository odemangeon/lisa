#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
ttv module.

The objective of this package is to provides the TTV_Instrument and TTV_Dataset classes.

@TODO:
"""
import logging
import matplotlib.pyplot as plt
from numpy import array, percentile

from lisa.posterior.core.dataset_and_instrument.dataset import Dataset
from lisa.posterior.core.dataset_and_instrument.instrument import Core_Instrument
from lisa.posterior.core.parameter import Parameter


## Logger
logger = logging.getLogger()


class TTV_Dataset(Dataset):
    """docstring for LC_Datasetc class.

    This class is designed to habor a light-curve data file for study of transits.
    It contains functions to visualize (plot) and manipulate the light-curve (cut around the
    transit, detrend)
    """

    __mandatory_columns__ = ["planet", "transit_time", "transit_time_err"]

    ## name of the data  and data error columns
    _data_name = "transit_time"
    _data_err_name = "transit_time_err"

    def plot(self, y=_data_name, yerr=_data_err_name, **kwargs):
        """
        Plot function to visualise the data.

        This is not very pretty but it plots the flux versus time and the error bars
        """
        self.get_datatable().plot(y=y, yerr=yerr, **kwargs)
        plt.show()

    def get_kwargs(self):
        pandas_df = self.get_datatable()
        return {"data": array(pandas_df[self._data_name]),
                "data_err": array(pandas_df[self._data_name_err]),
                "planet": array(pandas_df["planet"])}

    def get_planet_transit_time(self, planet):
        pandas_df = self.get_datatable()
        return pandas_df[pandas_df.planet == planet]

    def create_datasimulator_for_dataset(self, datasim_func):
        return datasim_func


class TTV_Instrument(Core_Instrument):
    """docstring for TTV_Instrument."""

    __category__ = "TTV"
    __params_model__ = {}

    def __init__(self, name):
        super(TTV_Instrument, self).__init__(name=name)


K2 = TTV_Instrument("K2")
Kepler = TTV_Instrument("Kepler")
CHEOPS = TTV_Instrument("CHEOPS")
CoRoT = TTV_Instrument("CoRoT")
