#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
lc module.

The objective of this package is to provides the LC_Instrument and LC_Dataset classes.

@TODO:
"""
import logging

from lisa.posterior.core.dataset_and_instrument.dataset import Core_DatasetTimeSeries
from lisa.posterior.core.dataset_and_instrument.instrument import Core_Instrument
from lisa.posterior.core.parameter import Parameter


## Logger
logger = logging.getLogger()

## LC instrument category
LC_inst_cat = "LC"


class LC_Instrument(Core_Instrument):
    """docstring for LC_Instrument."""

    __category__ = LC_inst_cat
    __sub_category__ = None
    __params_model__ = {'contam': {'main': True, 'free': False, 'value': 0, 'unit': 'wo unit'}, }
    __inst_var_basename__ = "instvar"

    @classmethod
    def init_inst_var_parameters(cls, inst_model, with_inst_var=False, inst_var_order=1):
        """Initialise/Create the required parameter for the modelling of the instrument variations."""
        inst_model.__with_inst_var = with_inst_var
        inst_model.__inst_var_order = inst_var_order
        if with_inst_var:
            if isinstance(inst_var_order, int) and inst_var_order >= 0:
                for order in range(inst_var_order + 1):
                    inst_model.add_parameter(Parameter(name=(inst_model.get_inst_var_param_name(order)),
                                                       name_prefix=inst_model.get_name(include_prefix=True, recursive=True),
                                                       main=True,
                                                       unit="[time]^(-{})".format(order)))
            else:
                raise ValueError("If you want to model instrument variations variations you need to "
                                 "provide an inst_var_order that is positive !")

    @classmethod
    def get_with_inst_var(cls, inst_model):
        """True if the instrument model includes instrument variations variations."""
        try:
            return inst_model.__with_inst_var
        except AttributeError:
            return False

    @classmethod
    def get_inst_var_order(cls, inst_model):
        """Return the order of the instrument variations variation model or None, if it's not modeled."""
        if cls.get_with_inst_var(inst_model):
            return inst_model.__inst_var_order
        else:
            return None

    def get_inst_var_param_name(self, order, inst_model):  # instrument is necessary don't remove it
        """Return the parameter name of the coefficient of the instrument variation model."""
        return "{}{}".format(self.__inst_var_basename__, order)


class LC_Dataset(Core_DatasetTimeSeries):
    """docstring for LC_Dataset class.

    This class is designed to habor a light-curve data file for study of transits.
    It contains functions to visualize (plot) and manipulate the light-curve (cut around the
    transit, detrend)

    To be properly ingested, the datasets of this type have to obey to the following format:
    LC_{TARGETNAME}_{INSTRUMENTNAME}(_{NB}).txt
    {TARGETNAME} is the name of the target,
    {INSTRUMENTNAME} is the name of the instrument used,
    {NB} is the number of the dataset if there is several dataset on the same target and with the same instrument.
    The part in between parenthesis is facultative.
    """

    __instrument_subclass__ = LC_Instrument
    __mandatory_columns__ = ["time", "data", "data_err"]

    def __init__(self, file_path, instrument_instance, exp_time=None):
        super(LC_Dataset, self).__init__(file_path, instrument_instance)
        self.dico_common_column_names["data"] = "flux"
        self.dico_common_column_names["data_err"] = "flux_err"


K2 = LC_Instrument("K2")
Kepler = LC_Instrument("Kepler")
CHEOPS = LC_Instrument("CHEOPS")
CoRoT = LC_Instrument("CoRoT")
