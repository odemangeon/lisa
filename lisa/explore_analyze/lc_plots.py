"""
Module to create plot specifically for light curve data

@TODO:
"""
from __future__ import annotations
from loguru import logger
from numpy import ones_like

from .core_compute_load import get_key_compute_model as get_key_compute_model_core
from .core_compute_load import is_valid_model_available as is_valid_model_available_core
from .core_compute_load import compute_raw_models as compute_raw_models_core

from ..posterior.core.model.core_model import Core_Model


key_whole = Core_Model.key_whole

dict_model_false = {key: False for key in ["1", "contamination", "stellar_var", "inst_var", "decorrelation", "decorrelation_likelihood"]}
dict_model_true = {key: True for key in ["1", "contamination", "stellar_var", "inst_var", "decorrelation", "decorrelation_likelihood"]}

d_name_component_removed_to_print = {'stellar_var': "Stellar Var", 'inst_var': "Inst Var", 'decorrelation': "Decorrelation",
                                     'decorrelation_likelihood': "Decorrelation Likelihood", 'contamination': "Contamination",
                                     'GP': "GP",
                                     }


def get_key_compute_model(key_model):
    """
    """
    if key_model == "contamination":
        key_compute_model = "contam"
    else:
        key_compute_model = get_key_compute_model_core(key_model=key_model)
    return key_compute_model


def is_valid_model_available(key_model, datasetname, post_instance):
    """
    """
    if key_model == "stellar_var":
        star = post_instance.model.stars[list(post_instance.model.stars.keys())[0]]
        inst_mod_fullname = post_instance.datasimulators.get_instmod_fullname(datasetname)
        inst_mod = post_instance.model.instruments[inst_mod_fullname]
        return ((star.get_dico_config_polymodel(inst_cat=inst_mod.instrument.category, notexist_ok=True, return_None_if_notexist=True) is not None) and
                 star.get_dico_config_polymodel(inst_cat=inst_mod.instrument.category, notexist_ok=True, return_None_if_notexist=True)["do"]
                )
    elif key_model == "inst_var":
        inst_mod_fullname = post_instance.datasimulators.get_instmod_fullname(datasetname)
        inst_mod = post_instance.model.instruments[inst_mod_fullname]
        return ((inst_mod.get_dico_config_polymodel(notexist_ok=True, return_None_if_notexist=True) is not None) and
                inst_mod.get_dico_config_polymodel(notexist_ok=True, return_None_if_notexist=True)["do"]
                )
    elif key_model == "contamination":
        return True
    else:
        return is_valid_model_available_core(key_model=key_model, datasetname=datasetname, post_instance=post_instance)


def compute_raw_models(tsim, key_model, datasetname, post_instance,
                       df_fittedval, datasim_kwargs, exptime, supersamp,
                       get_key_compute_model_func=get_key_compute_model,
                       kwargs_get_key_compute_model=None,
                       split_GP_computation=None,
                       ):
    """
    """
    if key_model == "1":
        model = ones_like(tsim)
        model_err = None
        return model, model_err
    else:
        return compute_raw_models_core(tsim=tsim, key_model=key_model,
                                       datasetname=datasetname, post_instance=post_instance,
                                       df_fittedval=df_fittedval, datasim_kwargs=datasim_kwargs,
                                       exptime=exptime, supersamp=supersamp, get_key_compute_model_func=get_key_compute_model_func,
                                       kwargs_get_key_compute_model=kwargs_get_key_compute_model,
                                       split_GP_computation=split_GP_computation
                                       )