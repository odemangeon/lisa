#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
lc module.

The objective of this package is to provides the LC_Instrument and LC_Dataset classes.

@TODO:
"""
import logging

from ...core.dataset_and_instrument.dataset import Core_DatasetTimeSeries
from ...core.dataset_and_instrument.instrument import Core_Instrument
# from ...core.parameter import Parameter
from ...core.model.polynomial_model import get_dico_config, set_dico_config
from ...core.model.polynomial_model import apply_polymodel_parametrisation as apply_polymodel_parametrisation_def


## Logger
logger = logging.getLogger()

## LC instrument category
LC_inst_cat = "LC"


class LC_Instrument(Core_Instrument):
    """docstring for LC_Instrument."""

    __category__ = LC_inst_cat
    __sub_category__ = None
    __params_model__ = {'contam': {'main': True, 'free': False, 'value': 0, 'unit': 'wo unit'},
                        'DeltaF': {'main': True, 'free': False, 'value': 0, 'unit': 'wo unit'},
                        }
    __drift_basename__ = "drift"
    __name_coeff_const__ = "DeltaF"

    # @classmethod
    # def init_inst_var_parameters(cls, inst_model, with_inst_var=False, inst_var_order=1):
    #     """Initialise/Create the required parameter for the modelling of the instrument variations."""
    #     inst_model.__with_inst_var = with_inst_var
    #     inst_model.__inst_var_order = inst_var_order
    #     if with_inst_var:
    #         if isinstance(inst_var_order, int) and inst_var_order >= 0:
    #             for order in range(inst_var_order + 1):
    #                 inst_model.add_parameter(Parameter(name=(inst_model.get_inst_var_param_name(order)),
    #                                                    name_prefix=inst_model.get_name(include_prefix=True, recursive=True),
    #                                                    main=True,
    #                                                    unit="[time]^(-{})".format(order)))
    #         else:
    #             raise ValueError("If you want to model instrument variations variations you need to "
    #                              "provide an inst_var_order that is positive !")
    #
    # @classmethod
    # def get_with_inst_var(cls, inst_model):
    #     """True if the instrument model includes instrument variations variations."""
    #     try:
    #         return inst_model.__with_inst_var
    #     except AttributeError:
    #         return False
    #
    # @classmethod
    # def get_inst_var_order(cls, inst_model):
    #     """Return the order of the instrument variations variation model or None, if it's not modeled."""
    #     if cls.get_with_inst_var(inst_model):
    #         return inst_model.__inst_var_order
    #     else:
    #         return None
    #
    # def get_inst_var_param_name(self, order, inst_model):  # instrument is necessary don't remove it
    #     """Return the parameter name of the coefficient of the instrument variation model."""
    #     return "{}{}".format(self.__inst_var_basename__, order)
    @classmethod
    def apply_parametrisation(cls, inst_model):
        """Apply the parametrisation to the instrument model.

        Arguments
        ---------
        inst_model_obj  : RV_inst_model object
            WARNING you cannot change the name of this argument for it to work with the __getattr__
            of lisa.posterior.core.dataset_and_instrument.instrument.Instrument_Model
        """
        cls.apply_polymodel_parametrisation(inst_model=inst_model)

    @classmethod
    def apply_polymodel_parametrisation(cls, inst_model):
        """Apply the parametrisation for the polynomial modelling to the instrument model.

        Arguments
        ---------
        inst_model_obj  : RV_inst_model object
            WARNING you cannot change the name of this argument for it to work with the __getattr__
            of lisa.posterior.core.dataset_and_instrument.instrument.Instrument_Model
        """
        apply_polymodel_parametrisation_def(param_container=inst_model, name_coeff_const=cls.__name_coeff_const__,
                                            func_param_name=lambda order: cls.get_polymodel_param_name(inst_model=inst_model, order=order),
                                            full_category_4_unit=cls.category,
                                            prefix=None)

    @classmethod
    def get_polymodel_param_name(cls, inst_model, order):
        """Return the parameter name of the coefficient of the polynomial model.

        Arguments
        ---------
        inst_model_obj  : RV_inst_model object
            WARNING you cannot delete or change the name of this argument for it to work with the __getattr__
            of lisa.posterior.core.dataset_and_instrument.instrument.Instrument_Model
        """
        return f"{cls.__drift_basename__}{order}"

    @classmethod
    def set_dico_config_polymodel(cls, inst_model, dico_config=None):
        """Get the dictionary that configures the polynomial model of the instrument model.
        Proxy for lisa.posterior.core.model.polynomial_model.set_dico_config

        Arguments
        ---------
        inst_model  : RV_inst_model object
            WARNING you cannot change the name of this argument for it to work with the __getattr__
            of lisa.posterior.core.dataset_and_instrument.instrument.Instrument_Model
        dico_config     : dict
            Updates that you might want to do to the dico that configure the polynomial model
        """
        set_dico_config(param_container=inst_model, prefix=None, dico_config=dico_config)

    @classmethod
    def get_dico_config_polymodel(cls, inst_model, notexist_ok=False, return_None_if_notexist=False):
        """Get the dictionary that configures the polynomial model of the instrument model.
        Proxy for lisa.posterior.core.model.polynomial_model.set_dico_config

        Arguments
        ---------
        inst_model  : RV_inst_model object
            WARNING you cannot change the name of this argument for it to work with the __getattr__
            of lisa.posterior.core.dataset_and_instrument.instrument.Instrument_Model
        dico_config     : dict
            Updates that you might want to do to the dico that configure the polynomial model
        """
        return get_dico_config(param_container=inst_model, prefix=None, notexist_ok=notexist_ok,
                               return_None_if_notexist=return_None_if_notexist
                               )


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
