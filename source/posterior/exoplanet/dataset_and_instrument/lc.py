#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
lc module.

The objective of this package is to provides the LC_Instrument and LC_Dataset classes.

@TODO:
"""
import logging
import matplotlib.pyplot as plt
from numpy import array, percentile

from source.posterior.core.dataset_and_instrument.dataset import Dataset
from source.posterior.core.dataset_and_instrument.instrument import Core_Instrument
from source.posterior.core.parameter import Parameter


## Logger
logger = logging.getLogger()


class LC_Dataset(Dataset):
    """docstring for LC_Datasetc class.

    This class is designed to habor a light-curve data file for study of transits.
    It contains functions to visualize (plot) and manipulate the light-curve (cut around the
    transit, detrend)
    """

    __mandatory_columns__ = ["time", "flux", "flux_err"]

    ## name of the data  and data error columns
    _data_name = "flux"
    _data_err_name = "flux_err"

    def plot(self, y="flux", yerr="flux_err", **kwargs):
        """
        Plot function to visualise the data.

        This is not very pretty but it plots the flux versus time and the error bars
        """
        self.get_datatable().plot(y=y, yerr=yerr, **kwargs)
        plt.show()

    def get_kwargs(self):
        pandas_df = self.get_datatable()
        return {"data": array(pandas_df["flux"]),
                "data_err": array(pandas_df["flux_err"]),
                "t": array(pandas_df["time"]),
                "tref": array(pandas_df["time"]).min()}

    def get_time(self):
        pandas_df = self.get_datatable()
        return array(pandas_df["time"])

    def get_tref(self):
        return (self.get_time()).min()

    def get_exptime(self, quartile=50):
        time = self.get_time()
        return percentile(time[1:] - time[:-1], quartile)

    def create_datasimulator_for_dataset(self, datasim_func):
        return datasim_func


class LC_Instrument(Core_Instrument):
    """docstring for LC_Instrument."""

    __category__ = "LC"
    # __params_model__ = {"DeltaOOT": {"unit": "wo unit"},
    #                     "driftOOT": {"unit": "wo unit/s"}}
    __params_model__ = {}
    __OOT_var_basename__ = "OOT"

    def __init__(self, name):
        super(LC_Instrument, self).__init__(name=name)

    @classmethod
    def init_OOT_var_parameters(cls, inst_model, with_OOT_var=False, OOT_var_order=1):
        """Initialise/Create the required parameter for the modelling of the out-of transit
        variations."""
        inst_model.__with_OOT_var = with_OOT_var
        inst_model.__OOT_var_order = OOT_var_order
        if with_OOT_var:
            if isinstance(OOT_var_order, int) and OOT_var_order >= 0:
                for order in range(OOT_var_order + 1):
                    inst_model.add_parameter(Parameter(name=(inst_model.get_OOT_param_name(order)),
                                                       name_prefix=inst_model.full_name,
                                                       main=True,
                                                       unit="s^(-{})".format(order)))
            else:
                raise ValueError("If you want to model out-of-transit variations you need to "
                                 "provide an OOT_var_order that is positive !")

    @classmethod
    def get_with_OOT_var(cls, inst_model):
        """True if the instrument model includes out-of-transit variations."""
        try:
            return inst_model.__with_OOT_var
        except:
            return False

    @classmethod
    def get_OOT_var_order(cls, inst_model):
        """Return the order of the out-of-transit variation model or None, if it's not modeled."""
        if cls.get_with_OOT_var(inst_model):
            return inst_model.__OOT_var_order
        else:
            return None

    def get_OOT_param_name(self, order, inst_model):  # instrument is necessary don't remove it
        """Return the parameter name of the coefficient of the out-of-transit model."""
        return "{}{}".format(self.__OOT_var_basename__, order)


K2 = LC_Instrument("K2")
Kepler = LC_Instrument("Kepler")
CHEOPS = LC_Instrument("CHEOPS")
CoRoT = LC_Instrument("CoRoT")
