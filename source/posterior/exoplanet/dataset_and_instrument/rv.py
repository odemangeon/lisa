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
from source.posterior.core.dataset_and_instrument.instrument import Core_Instrument


## Logger
logger = logging.getLogger()


class RV_Dataset(Dataset):
    """docstring for RV_Datasetc class.

    This class is designed to habor a radial velocity data file.
    It contains functions to visualize (plot) and manipulate the radial velocities (detrend??)
    """

    __mandatory_columns__ = ["time", "RV", "RV_err"]

    def plot(self, y="RV", yerr="RV_err", **kwargs):
        """
        Plot function to visualise the data.

        This is not very pretty but it plots the flux versus time and the error bars
        """
        self.get_data().plot(y=y, yerr=yerr, **kwargs)
        plt.show()


class RV_Instrument(Core_Instrument):
    """docstring for RV_Instrument."""

    __category__ = "RV"
    __params_model__ = {"jitter": {"unit": "wo unit"},
                        "drift": {"unit": "[K]/day"},
                        "DeltaRV": {"unit": "[K]"},
                        }
    __name_RV_ref_var__ = "RVref"
    __name_RV_ref_global_var__ = "RVrefGlob"

    @classmethod
    def _get_inst_paramfilesection(cls, text_tab, model_instance, inst_name):
        def_instmod_name = (model_instance.get_instmodel_names(inst_name=inst_name,
                                                               inst_cat=cls.category)[0])
        return "{}'{}': '{}',\n".format(text_tab, cls.__name_RV_ref_var__, def_instmod_name)

    @classmethod
    def _get_instcat_paramfilesection(cls, text_tab, model_instance):
        RVrefglobale_instname = model_instance.RV_globalref_instname
        return "{}{} = '{}'\n".format(text_tab, cls.__name_RV_ref_global_var__,
                                      RVrefglobale_instname)

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
        model_instance.set_RVref4inst_modname(inst_name, dico_config_inst[cls.__name_RV_ref_var__])

    @classmethod
    def _load_config_instcat(cls, dico_config, model_instance):
        model_instance.set_RV_globalref_instname(dico_config[cls.__name_RV_ref_global_var__])

    def __init__(self, name):
        super(RV_Instrument, self).__init__(name=name)


HARPS = RV_Instrument("HARPS")
SOPHIE_HE = RV_Instrument("SOPHIE-HE")
SOPHIE_HR = RV_Instrument("SOPHIE-HR")
