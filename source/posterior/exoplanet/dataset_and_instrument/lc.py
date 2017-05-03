#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
lc module.

The objective of this package is to provides the LC_Instrument and LC_Dataset classes.

@TODO:
"""
import logging
import matplotlib.pyplot as plt
from numpy import array

from source.posterior.core.dataset_and_instrument.dataset import Dataset
from source.posterior.core.dataset_and_instrument.instrument import Core_Instrument

## Logger
logger = logging.getLogger()


class LC_Dataset(Dataset):
    """docstring for LC_Datasetc class.

    This class is designed to habor a light-curve data file for study of transits.
    It contains functions to visualize (plot) and manipulate the light-curve (cut around the
    transit, detrend)
    """

    __mandatory_columns__ = ["time", "flux", "flux_err"]

    def plot(self, y="flux", yerr="flux_err", **kwargs):
        """
        Plot function to visualise the data.

        This is not very pretty but it plots the flux versus time and the error bars
        """
        self.get_data().plot(y=y, yerr=yerr, **kwargs)
        plt.show()

    def get_kwargs(self):
        pandas_df = self.get_data()
        return {"data": array(pandas_df["flux"]),
                "data_err": array(pandas_df["flux_err"]),
                "t": array(pandas_df["time"])}

    def get_time(self):
        pandas_df = self.get_data()
        return array(pandas_df["time"])

    def create_datasimulator_for_dataset(self, datasim_func):
        return datasim_func


class LC_Instrument(Core_Instrument):
    """docstring for LC_Instrument."""

    __category__ = "LC"
    __params_model__ = {"DeltaOOT": {"unit": "wo unit"},
                        "driftOOT": {"unit": "wo unit/s"}}

    def __init__(self, name):
        super(LC_Instrument, self).__init__(name=name)


K2 = LC_Instrument("K2")
Kepler = LC_Instrument("Kepler")
CHEOPS = LC_Instrument("CHEOPS")
CoRoT = LC_Instrument("CoRoT")
