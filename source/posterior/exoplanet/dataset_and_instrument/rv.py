#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
rv module.

The objective of this package is to provides the RV_Instrument and RV_Dataset classes.

@TODO:
"""
import logging
import matplotlib.pyplot as plt

from source.posterior.core.dataset_and_instrument.dataset import Dataset
from source.posterior.core.dataset_and_instrument.instrument import Instrument

## Logger
logger = logging.getLogger()


class RV_Dataset(Dataset):
    """docstring for RV_Datasetc class.

    This class is designed to habor a radial velocity data file.
    It contains functions to visualize (plot) and manipulate the radial velocities (detrend??)
    """

    _mandatory_columns = ["time", "RV", "RV_err"]

    def plot(self, y="RV", yerr="RV_err", **kwargs):
        """
        Plot function to visualise the data.

        This is not very pretty but it plots the flux versus time and the error bars
        """
        self.get_data().plot(y=y, yerr=yerr, **kwargs)
        plt.show()


class RV_Instrument(Instrument):
    """docstring for RV_Instrument."""

    _inst_type = "RV"
    _params_model = {"jitter": {"unit": "wo unit"}}

    def __init__(self, name):
        super(RV_Instrument, self).__init__(name=name)


HARPS = RV_Instrument("HARPS")
SOPHIE_HE = RV_Instrument("SOPHIE-HE")
SOPHIE_HR = RV_Instrument("SOPHIE-HR")
