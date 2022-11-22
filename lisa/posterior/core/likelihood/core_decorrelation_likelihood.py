#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Decorrelation model module.

TODO:
- If I want several decorrelation methods beside the Linear Decorrelation and do not want to have to
modify this module than I will need to implement a decorrelation method manager.
"""
from logging import getLogger
from collections import defaultdict
from copy import deepcopy

from ....tools.metaclasses import MandatoryReadOnlyAttrAndMethod
# from ....tools.miscellaneous import spacestring_like
from ..dataset_and_instrument.manager_dataset_instrument import Manager_Inst_Dataset


## Logger object
logger = getLogger()

mgr_inst_dst = Manager_Inst_Dataset()
mgr_inst_dst.load_setup()


class Core_DecorrelationLikelihood(object, metaclass=MandatoryReadOnlyAttrAndMethod):
    """docstring for Core_DecorrelationLikelihood class, Parent class of all Decorrelation likelihood Class"""

    ## List of mandatory arguments which have to be defined in the subclasses.
    # For example "category" is in this list. It has to be defined in the subclass as a class
    # attribute like this:
    # __category__ = "ModelCategory"
    # It then be read as self.category
    __mandatoryattrs__ = ["category", "format_config_dict", "l_required_inddatasetkwarg_keys",
                          "l_required_datasetkwarg_keys", ]
    # category: String which designate the decorrelation model (for example: "linear"). To choose the
    #   decorrelation model to be used, the user will use this string.
    # format_config_dict is a strong to be used as the example of how to specify the dictionary in the
    #   Instrument specific parameter file
    __mandatorymeths__ = ["apply_parametrisation", "create_decorrelation_likelihood"]
    # apply_parametrisation: Method that creates the parameters necessary for the decorrelation model
    #  for each instrument model object of the instrument category to which this decorrelation model applies
    #  The arguments must be inst_mod_obj, the Instrument model object and decorrelation_config_inst_decorr
    #  the dictionary that contains the configuration of the decorrelation model for the instrument model object
    #  considered
    # get_text_decorrelation: This function produces the text for the decorrelation model for all decorrelation
    #  variable using a given decorrelation category

    @classmethod
    def load_text_decorr_paramfile(cls, model_name, config_model_paramfile, config_model_storage, model_instance):
        """load the parametrisation for the decorrelation of the instrument model from the inst cat param file.

        Method which load the dictionary written in an instrument category  specific paramfile and which
        contains the parameterisation of the decorrelation models for an likelihood decorrelation model

        This function is used by Core_InstCat_Model.load_config_decorrelation
        It is advised to overload this function in the child Core_DecorrelationLikelihood class to make
        some additional checks on the specific content required by the likelihood decorrelation model

        Arguments
        ---------
        model_name              : str
            Name of the likelihood decorrelation model being loaded
        config_model_paramfile  : dict
            Dictionary providing the configuration one the decorrelation likelihood model
        config_model_storage    : dict
            Dictionary where the decorrelation likelihood model configuration will be stored.
        model_instance          : Subclass of Core_Model
        """
        config_model_storage = deepcopy(config_model_paramfile)

    @classmethod
    def get_required_dataset(cls, decorr_config_instmod_decorr_cat, dico_decorr_instmod_decorr_cat, decorr_name,
                             d_required_datasetkwargkeys_4_dataset, d_required_datasetkwargkeys_4_inddataset,
                             l_dataset_name
                             ):
        """Fill the dictionary dico_decorr_instmod_decorr_cat, d_required_datasetkwargkeys_4_dataset, d_required_datasetkwargkeys_4_inddataset

        This function is called by instcat model class

        Arguments
        ---------
        decorr_config_instmod_decorr_cat            :
        dico_decorr_instmod_decorr_cat              :
        decorr_name                                 :
        d_required_datasetkwargkeys_4_dataset       :
        d_required_datasetkwargkeys_4_inddataset    :
        l_dataset_name                              :

        Returns
        -------
        dico_decorr_instmod_decorr_cat              :
        d_required_datasetkwargkeys_4_dataset       :
        d_required_datasetkwargkeys_4_inddataset    :
        """
        decorr_config = decorr_config_instmod_decorr_cat[decorr_name]
        if cls.category not in dico_decorr_instmod_decorr_cat:
            dico_decorr_instmod_decorr_cat[cls.category] = defaultdict(cls.defdic_decorr_func)
        for dataset_name, ind_dataset_name in decorr_config["match datasets"].items():
            dico_decorr_instmod_decorr_cat[cls.category][decorr_name]["l_idx_simdata"].append(l_dataset_name.index(dataset_name))
            dico_decorr_instmod_decorr_cat[cls.category][decorr_name]["l_datasetkwargs_req"].append(cls.l_required_datasetkwarg_keys)
            for datasetkwarg in cls.l_required_datasetkwarg_keys:
                if datasetkwarg not in d_required_datasetkwargkeys_4_dataset[dataset_name]:
                    d_required_datasetkwargkeys_4_dataset[dataset_name].append(datasetkwarg)
            dico_decorr_instmod_decorr_cat[cls.category][decorr_name]["l_inddataset_name"].append(ind_dataset_name)
            dico_decorr_instmod_decorr_cat[cls.category][decorr_name]["l_inddatasetkwargs_req"].append(cls.l_required_inddatasetkwarg_keys)
            for datasetkwarg in cls.l_required_inddatasetkwarg_keys:
                if datasetkwarg not in d_required_datasetkwargkeys_4_inddataset[ind_dataset_name]:
                    d_required_datasetkwargkeys_4_inddataset[ind_dataset_name].append(datasetkwarg)

        return dico_decorr_instmod_decorr_cat, d_required_datasetkwargkeys_4_dataset, d_required_datasetkwargkeys_4_inddataset

    @classmethod
    def defdic_decorr_func(cls):
        return {"l_idx_simdata": [],
                "l_datasetkwargs_req": [],
                "l_inddataset_name": [],
                "l_inddatasetkwargs_req": [],
                }
