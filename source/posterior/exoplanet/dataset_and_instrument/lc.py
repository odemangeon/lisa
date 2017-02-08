#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
lc module.

The objective of this package is to provides the LC_Instrument and LC_Dataset classes.

@TODO:
"""
import logging
import matplotlib.pyplot as plt

from source.posterior.core.dataset_and_instrument.dataset import Dataset
from source.posterior.core.dataset_and_instrument.instrument import Instrument

## Logger
logger = logging.getLogger()


class LC_Dataset(Dataset):
    """docstring for LC_Datasetc class.

    This class is designed to habor a light-curve data file for study of transits.
    It contains functions to visualize (plot) and manipulate the light-curve (cut around the
    transit, detrend)
    """

    _mandatory_columns = ["time", "flux", "flux_err"]

    def plot(self, y="flux", yerr="flux_err", **kwargs):
        """
        Plot function to visualise the data.

        This is not very pretty but it plots the flux versus time and the error bars
        """
        self.get_data().plot(y=y, yerr=yerr, **kwargs)
        plt.show()


class LC_Instrument(Instrument):
    """docstring for LC_Instrument."""

    _inst_type = "LC"

    def __init__(self, name):
        super(LC_Instrument, self).__init__(name=name)


K2 = LC_Instrument("K2")
Kepler = LC_Instrument("Kepler")
CHEOPS = LC_Instrument("CHEOPS")
CoRoT = LC_Instrument("CoRoT")
