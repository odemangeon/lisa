"""
Module to create plot specifically for light curve data

@TODO:
"""
from __future__ import annotations
from loguru import logger
from numpy import ones_like
from pandas import DataFrame
from typing import Callable, Dict
from matplotlib.figure import Figure
from matplotlib.gridspec import SubplotSpec


from .core_compute_load import get_key_compute_model as get_key_compute_model_core
from .core_compute_load import is_valid_model_available as is_valid_model_available_core
from .core_compute_load import compute_raw_models as compute_raw_models_core
from .ts_plots import create_TS_plots, PlotsDefinition_TS
from .pf_plots import create_PF_plots, PlotsDefinition_PF
from .core_plot import ComputedModels_Database
from .misc import AandA_fontsize

from ..posterior.core.model.core_model import Core_Model
from ..posterior.core.posterior import Posterior


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
                       df_param_value, datasim_kwargs, exptime, supersamp,
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
                                       df_param_value=df_param_value, datasim_kwargs=datasim_kwargs,
                                       exptime=exptime, supersamp=supersamp, get_key_compute_model_func=get_key_compute_model_func,
                                       kwargs_get_key_compute_model=kwargs_get_key_compute_model,
                                       split_GP_computation=split_GP_computation
                                       )
    

def create_LC_TS_plots(post_instance:Posterior,
                       plotdef:PlotsDefinition_TS,
                       computedmodels_db:ComputedModels_Database|None=None,
                       split_GP_computation:int|None=None,
                       datasim_kwargs:dict|None=None,
                       create_axes_main_gridspec:dict|None=None,
                       create_axes_dataresi_gridspec:dict|None=None,
                       npt_model_default:int|None=None,
                       extra_dt_model:float|None=None,
                       fontsize:int=AandA_fontsize,
                       fig:Figure|None=None,
                       subplotspec:SubplotSpec|None=None,
                       ):
    
    return create_TS_plots(post_instance=post_instance, compute_raw_models_func=compute_raw_models,
                           plotdef=plotdef, computedmodels_db=computedmodels_db, split_GP_computation=split_GP_computation,
                           datasim_kwargs=datasim_kwargs,
                           create_axes_main_gridspec=create_axes_main_gridspec,
                           create_axes_dataresi_gridspec=create_axes_dataresi_gridspec,
                           npt_model_default=npt_model_default, extra_dt_model=extra_dt_model,
                           fontsize=fontsize,
                           get_key_compute_model_func=get_key_compute_model,
                           kwargs_get_key_compute_model=None,
                           fig=fig, subplotspec=subplotspec,
                           )


def create_LC_PF_plots(post_instance:Posterior,
                       plotdef:PlotsDefinition_PF,
                       computedmodels_db:ComputedModels_Database|None=None,
                       split_GP_computation:int|None=None,
                       datasim_kwargs:dict|None=None,
                       create_axes_main_gridspec:dict|None=None,
                       create_axes_dataresi_gridspec:dict|None=None,
                       npt_model_default:int|None=None,
                       extra_dt_model:float|None=None,
                       fontsize:int=AandA_fontsize,
                       fig:Figure|None=None,
                       subplotspec:SubplotSpec|None=None,
                       ):
    
    return create_PF_plots(post_instance=post_instance, compute_raw_models_func=compute_raw_models,
                           plotdef=plotdef, computedmodels_db=computedmodels_db, split_GP_computation=split_GP_computation,
                           datasim_kwargs=datasim_kwargs,
                           create_axes_main_gridspec=create_axes_main_gridspec,
                           create_axes_dataresi_gridspec=create_axes_dataresi_gridspec,
                           npt_model_default=npt_model_default, extra_dt_model=extra_dt_model,
                           fontsize=fontsize,
                           get_key_compute_model_func=get_key_compute_model,
                           kwargs_get_key_compute_model=None,
                           fig=fig, subplotspec=subplotspec,
                           )