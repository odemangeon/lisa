"""
Module to create plots specifically for radial velocity data

@TODO:
"""
from loguru import logger
from collections import OrderedDict

from .core_compute_load import get_key_compute_model as get_key_compute_model_core
from .core_compute_load import is_valid_model_available as is_valid_model_available_core
from .core_compute_load import compute_raw_models as compute_raw_models_core

from ..posterior.core.model.core_model import Core_Model


key_whole = Core_Model.key_whole

y_name = "RV"

dict_model_false = {key: False for key in ["stellar_var", "inst_var", "decorrelation", "decorrelation_likelihood"]}
dict_model_true = {key: True for key in ["stellar_var", "inst_var", "decorrelation", "decorrelation_likelihood"]}

d_name_component_removed_to_print = {'inst_var': "Inst Var", 'stellar_var': "Stellar var",
                                     'decorrelation': "Decorrelation",
                                     'decorrelation_likelihood': "Decorrelation Likelihood",
                                     'contamination': "Contamination",
                                     'GP': "GP",
                                     }


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
    else:
        return is_valid_model_available_core(key_model=key_model, datasetname=datasetname, post_instance=post_instance)
