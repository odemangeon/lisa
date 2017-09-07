!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Datasim creator rebound module.
"""
from logging import getLogger


## Logger object
logger = getLogger()


def create_datasimulator_rebound(star, planets, key_whole, parametrisation,
                                 LC_multis_parametrisations, ldmodel4instmodfname, LDs,
                                 transit_model, SSE4instmodfname,
                                 RV_globalref_instname, RV_instref_modnames, RV_inst_db,
                                 inst_models=None, datasets=None):
    """Return datasimulator functions.

    A datasimualtor function is created for the whole dataset_database and for each planet
    individually.

    :param Star star: Star object
    :param dict_of_Planet planets: dictionary: key: planet name, value: Planet object
    :param string key_whole: key to use to identify the whole system in the output dictionary
        (dico_docf).
    :param string parametrisation: String refering to the parametrisation to use
    :param list_of_string LC_multis_parametrisations: List of string giving the parametrisation that
        specially made for multi-planetary systems.
    :param dict_of_ ldmodel4instmodfname: Dictionary giving Limd darkening model to use for each
        instrument model
    :param string transit_model: String refering to the transit model to be used.
    :param dict_of_ SSE4instmodfname: Dictionary giving the supersampling factor and the exposure
        time to use for each instrument model
    :param string RV_globalref_instname: Name of the instrument used as global RV reference. All the
        Delta RV for the other instruments are relative to this instrument.
    :param dict_of_string RV_instref_modnames: Dictionary giving the name of the instrument model
        (not the full name) that is used has reference for this instrument. The other instrument
        models for this instrument will have an extra Delta RV relative to this instrument model.
    :param RV_inst_db:
    :param Instrument_Model inst_model: instance of Instrument_Model
    :param Dataset dataset: instance of Dataset

    :return dict_of_DatasimDocFunc dico_docf: A dictionary with DocFunctions containing the data
        simulator function for the whole system ("whole") and for the each planet individually
        ("planet_name")
    """
    
