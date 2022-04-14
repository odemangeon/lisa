#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
rv module.

The objective of this package is to provides the RV_Instrument and RV_Dataset classes.

@TODO:
"""
from logging import getLogger
import matplotlib.pyplot as plt
from numpy import array

from lisa.posterior.core.dataset_and_instrument.dataset import Core_Dataset
from lisa.posterior.core.dataset_and_instrument.instrument import Core_Instrument
from lisa.posterior.core.parameter import Parameter


## Logger
logger = getLogger()

## RV instrument category
RV_inst_cat = "RV"


class RV_Instrument(Core_Instrument):
    """docstring for RV_Instrument."""

    __category__ = RV_inst_cat
    __sub_category__ = None
    __params_model__ = {"driftRV": {"unit": "[amplitude of the RV data]/[time of the RV data]"},
                        "DeltaRV": {"unit": "[amplitude of the RV data]"},
                        }
    __name_RV_ref_var__ = "RVref"
    __name_RV_ref_global_var__ = "RVrefGlob"
    __inst_var_basename__ = "instvar"

    @classmethod
    def _get_inst_paramfilesection(cls, text_tab, model_instance, inst_name, entete_symb=": "):
        def_instmod_name = (model_instance.get_instmodel_names(inst_name=inst_name,
                                                               inst_fullcat=cls.category)[0])
        return "{}'{}'{}'{}',\n".format(text_tab, cls.__name_RV_ref_var__, entete_symb, def_instmod_name)

    @classmethod
    def _get_instcat_paramfilesection(cls, text_tab, model_instance, entete_symb=": "):
        RVrefglobale_instname = model_instance.instcat_models[RV_inst_cat].RV_globalref_instname
        return "{}'{}'{}'{}'\n".format(text_tab, cls.__name_RV_ref_global_var__, entete_symb, RVrefglobale_instname)

    @classmethod
    def _update_inst_paramfile_info(cls, paramfile_info_inst_RV_inst):
        paramfile_info_inst_RV_inst.append(cls.__name_RV_ref_var__)

    @classmethod
    def _update_instcat_paramfile_info(cls, paramfile_info_inst_RV_misc):
        paramfile_info_inst_RV_misc.append(cls.__name_RV_ref_global_var__)

    @classmethod
    def _load_config_listspecifickeys_inst(cls):
        return [cls.__name_RV_ref_var__]

    @classmethod
    def _load_config_specifickeys_inst(cls, dico_config_inst, inst_name, model_instance):
        model_instance.instcat_models[RV_inst_cat].set_RVref4inst_modname(inst_name, dico_config_inst[cls.__name_RV_ref_var__])

    @classmethod
    def _load_config_instcat(cls, dico_config_fullcat, model_instance):
        model_instance.instcat_models[RV_inst_cat].set_RV_globalref_instname(dico_config_fullcat[cls.__name_RV_ref_global_var__])

    @classmethod
    def init_inst_var_parameters(cls, inst_model, with_inst_var=False, inst_var_order=1):
        """Initialise/Create the required parameter for the modelling of the instrument variations."""
        inst_model.__with_inst_var = with_inst_var
        inst_model.__inst_var_order = inst_var_order
        if with_inst_var:
            if isinstance(inst_var_order, int) and inst_var_order >= 1:
                for order in range(1, inst_var_order + 1):
                    inst_model.add_parameter(Parameter(name=(inst_model.get_inst_var_param_name(order)),
                                                       name_prefix=inst_model.get_name(include_prefix=True, recursive=True),
                                                       main=True,
                                                       unit="[RV_unit].[time]^(-{})".format(order)))
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


class RV_Dataset(Core_Dataset):
    """docstring for RV_Dataset class.

    This class is designed to habor an radial velocity data file.
    It contains functions to visualize (plot) and manipulate the radial velocities (detrend??)

    To be properly ingested, the datasets of this type have to obey to the following format:
    RV_{TARGETNAME}_{INSTRUMENTNAME}(_{NB}).txt
    {TARGETNAME} is the name of the target,
    {INSTRUMENTNAME} is the name of the instrument used,
    {NB} is the number of the dataset if there is several dataset on the same target and with the same instrument.
    The part in between parenthesis is facultative.
    """

    __instrument_subclass__ = RV_Instrument
    __mandatory_columns__ = ["time", "RV", "RV_err"]

    ## name of the data  and data error columns
    _data_name = "RV"
    _data_err_name = "RV_err"

    def plot(self, y="RV", yerr="RV_err", **kwargs):
        """
        Plot function to visualise the data.

        This is not very pretty but it plots the flux versus time and the error bars
        """
        self.get_datatable().plot(y=y, yerr=yerr, **kwargs)
        plt.show()

    def get_kwargs(self):
        pandas_df = self.get_datatable()
        return {"data": array(pandas_df[self._data_name]),
                "data_err": array(pandas_df[self._data_err_name]),
                "t": array(pandas_df["time"]),
                "tref": array(pandas_df["time"]).min()}

    def get_time(self):
        pandas_df = self.get_datatable()
        return array(pandas_df["time"])

    def get_tref(self):
        return (self.get_time()).min()

    def create_datasimulator_for_dataset(self, datasim_func):
        # t_dtst = self.get_time()
        # tmin = t_dtst.min()
        # tmax = t_dtst.max()
        # nt = len(t_dtst)
        # oversamp = 10
        # tsamp = (tmax - tmin) / (nt * oversamp)
        # tmin_moins = tmin - oversamp * tsamp
        # tmax_plus = tmax + oversamp * tsamp
        # func = datasim_func.function
        # arg_list = datasim_func.arg_list
        # arg_list_new = OrderedDict()
        # arg_list_new["param"] = arg_list["param"]
        # arg_list_new["kwargs"] = ["tsamp", "tmin", "tmax"]

        # def datasim_func_fordataset(p, tsamp=tsamp, tmin=tmin_moins, tmax=tmax_plus):
        #     t = linspace(tmin, tmax, (tmax - tmin) / tsamp)
        #     return func(p, t=t)
        #
        # return DocFunction(function=datasim_func_fordataset, arg_list=arg_list_new)
        return datasim_func


HARPS = RV_Instrument("HARPS")
SOPHIE_HE = RV_Instrument("SOPHIE-HE")
SOPHIE_HR = RV_Instrument("SOPHIE-HR")
