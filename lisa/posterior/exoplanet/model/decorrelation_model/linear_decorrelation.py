#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Decorrelation model module.
"""
import numpy as np
from logging import getLogger
from scipy.interpolate import interp1d

from ....core.model.core_decorrelation_model import Core_DecorrelationModel
from ....core.parameter import Parameter
from .....tools.function_from_text_toolbox import add_param_argument, par_vec_name, add_nonparam_argument
from .....tools.name import check_name


## Logger object
logger = getLogger()


def scale_and_interpolate(t, x, scale=None):
    """Function taken from https://github.com/pmaxted/pycheops/ pycheops/dataset.py
    """
    if scale is None:
        z = x
    elif np.ptp(x) == 0:
        z = np.zeros_like(x)
    elif scale == 'max':
        z = (x - min(x)) / np.ptp(x)
    elif scale == 'range':
        z = (2 * x - (x.min() + x.max())) / np.ptp(x)
    else:
        raise ValueError('scale must be None, max or range')
    return interp1d(t, z, bounds_error=False, fill_value=(z[0], z[-1]))


class LinearDecorrelation_LC(Core_DecorrelationModel):
    """docstring for LinearDecorrelation_LC."""

    # Mandatory attributes from Core_DecorrelationModel
    __category__ = "linear"
    __name_dict_paramfile__ = "linear_decorr"
    __format_config_dict__ = "{'quantity': 'raw'}"
    __allowed_quantity_strs__ = ['raw', ]

    root_name_coeffcorr = "L"

    # def __init__(self, arg):
    #     super(LinearDecorrelation_LC, self).__init__()
    #     self.arg = arg

    # Mandatory method from Core_DecorrelationModel
    @classmethod
    def load_text_decorr_paramfile(cls, inst_mod_obj, decorrelation_config_inst_decorr_paramfile, decorrelation_config_inst_decorr, allowed_what2decorrelate_strs):
        """load the parametrisation for the decorrelation of one instrument model from the inst cat param file.

        This function is used by Core_InstCat_Model.load_config_decorrelation
        This function checks that the inputs provided are valid and store them in decorrelation_config_inst_decorr

        Arguments
        ---------
        inst_mod_obj                                : Core_InstrumentModel
            Instrument model object of which you want to load the decorrelation parameterisation
        decorrelation_config_inst_decorr_paramfile  : dict
            Dictionary providing the configuration of the decorrelation for the instrument model inst_mod_obj
            and the current decorrelation method.
        decorrelation_config_inst_decorr            : dict
            Dictionary where the decorrelation configuration is stored for the instrument model inst_mod_obj
            and the current decorrelation method.
            Structure:
               key0: do
               value0: bool, say if the decorelation should be performed
               Keyn: decorrelation model name
               valuen: dict, parameters of the decorrelation model
        allowed_what2decorrelate_strs               : list of str
            List of strings allowed for the part of the model to decorrelate
        """
        super(LinearDecorrelation_LC, cls).load_text_decorr_paramfile(inst_mod_obj=inst_mod_obj,
                                                                      decorrelation_config_inst_decorr_paramfile=decorrelation_config_inst_decorr_paramfile,
                                                                      decorrelation_config_inst_decorr=decorrelation_config_inst_decorr,
                                                                      skip_load=True)
        for inst_mod_obj_decorr_var_name in decorrelation_config_inst_decorr_paramfile.keys():
            # Check that the "quantity" is in the dictionary
            if "quantity" not in decorrelation_config_inst_decorr_paramfile[inst_mod_obj_decorr_var_name]:
                raise ValueError(f"The dictionary for the configuration of the linear decorrelation of {inst_mod_obj.full_name}"
                                 f" with {inst_mod_obj_decorr_var_name} must include the key 'quantity'.")
            quantity = decorrelation_config_inst_decorr_paramfile[inst_mod_obj_decorr_var_name]["quantity"]
            # Check that the "quantity" value is valid
            if quantity not in cls.__allowed_quantity_strs__:
                raise ValueError(f"'quantity' for the configuration of the linear decorrelation of {inst_mod_obj.full_name}"
                                 f" with {inst_mod_obj_decorr_var_name} must be in {cls.__allowed_quantity_strs__}.")
            # If quantity is raw, check that "match datasets" is in the dictionary
            if quantity == "raw":
                if "match datasets" not in decorrelation_config_inst_decorr_paramfile[inst_mod_obj_decorr_var_name]:
                    raise ValueError(f"Since quantity is {quantity}, the dictionary for the configuration of the linear decorrelation of {inst_mod_obj.full_name}"
                                     f" with {inst_mod_obj_decorr_var_name} must include the key 'match datasets'.")
            # Store the decorrelation configuration
            decorrelation_config_inst_decorr[inst_mod_obj_decorr_var_name] = decorrelation_config_inst_decorr_paramfile[inst_mod_obj_decorr_var_name]

    @classmethod
    def apply_parametrisation(cls, inst_mod_obj, decorrelation_config_inst_decorr, model_part=""):
        """Apply the parametrisation for the decorrelation to an instrument model.

        This function is used by parametrisation_gravgroup.apply_instmodel_parametrisation

        Arguments
        ---------
        inst_mod_obj                        : Instrument_Model instance
            Instrument model object to which you want to apply the parametrisation associated to the
            decorrelation model
        decorrelation_config_inst_decorr    : dict
            Dictionary where the decorrelation configuration is stored for the instrument model inst_mod_obj
            and the current decorrelation method.
            Structure:
               key0: do
               value0: bool, say if the decorelation should be performed
               Keyn: decorrelation model name
               valuen: dict, parameters of the decorrelation model
        model_part                          : str
            String giving the model part concerned
        """
        for inst_mod_obj_decorr_var_name in decorrelation_config_inst_decorr.keys():
            inst_mod_obj.add_parameter(Parameter(name=f"{cls.root_name_coeffcorr}{model_part}{inst_mod_obj_decorr_var_name}",
                                                 name_prefix=inst_mod_obj.name, main=True, unit="w/o unit"))

    @classmethod
    def get_text_decorrelation(cls, multi, inst_mod_obj, idx_inst_mod_obj, l_dataset_name_inst_mod, dataset_db, time_arg_name,
                               decorrelation_config, param_nb, arg_list, key_param, key_mand_kwargs,
                               key_opt_kwargs, key_func, ldict, model_part=""):
        """Produce the text for the decorrelation model of this category

        This function creates the text for the decorrelation model of this category.

        Arguments
        ---------
        multi                   : bool
            If True the datasimulator being created is simulating multiple instruments and/or datasets
            and the time is a list of time arrays. Otherwise only one instrument/dataset is simulated
            and time is time array.
        inst_mod_obj            : Instrument_Model instance
            Instrument model object to which you want to apply the decorrelation model
        idx_inst_mod_obj                : int
            Index of the instrument model object (inst_mod_obj) in the list of instrument model object
            simulated by the datasimulator function. This is use when multi is True to know what is the
            index of the corresponding time array in the list of time arrays.
        l_dataset_name_inst_mod : List of dataset names (list of strings)
            Dataset being simulated for the instrument model (inst_mod_obj)
        dataset_db              : DatasetDatabase
            Dataset database to access the dataset for the decorrelation.
        time_arg_name           : str
            Str used to designate the time vector(s)
        decorrelation_config    : dict
            Dictionary where the decorrelation configuration is stored for the instrument model inst_mod_obj
            and the current decorrelation method.
            Structure:
               Keyn: Indicator instrument model name
               valuen: dict providing the parameters for the current decorrelation model
        param_nb        : dict_of_int
            dictionary giving the current number of free parameters in the function being produced.
            key = str key designating the function being built and provided by key_func
            value = int giving the current number of parameter in the model
            Format: {"name_of_function": int_current_nb_of_model_parameters_of_the_datasimulator}
            THIS DICTIONARY IS MODIFIED EVEN IF NOT RETURNED
        arg_list        : dict_of_dict_of_list_of_str
            dictionary giving the arguments of the functions currently being produced with the following format:
            - key = str designating the function being built and provided by key_func.
            - value = dict with three str keys and values
                - <key_param>: empty list that will receive the full names of the parameters of the function (content of the param_vector)
                - <key_mand_kwargs>: empty list that will receive the mandatory keyword arguments (beside the param_vector)
                - <key_opt_kwargs>: empty list that will receive the optional keyword arguments
            If it's not added to ldict instead the arguments provided by arguments are going to be added to the key_mand_kwargs or key_opt_kwargs
            of sub-dictionaries specified by key_func.
            THIS DICTIONARY IS MODIFIED EVEN IF NOT RETURNED
        key_param       : str
            Key used for the parameters entry of arg_list values
        key_mand_kwargs         : str
            Key used for the mandatory keyword argument entry of arg_list
        key_opt_kwargs          : str
            Key used for the optional keyword argument entry of arg_list
        key_func       : str
            Key used in arg_list and param for the function simulating the whole system (all planets together)
        ldict           : dict of dict
            Local dictionary for the later execution (exec) of the text of the functions. All variables
            that will not be passed explicitly to the function by the user need to be defined there.
            Format:
            - key = str designating the function being built and provided by key_func
            - value = dictionary
            THIS DICTIONARY IS MODIFIED EVEN IF NOT RETURNED
        model_part                          : str
            String giving the model part concerned

        Returns
        -------
        text_decor   : str
            Text providing the decorrelation component for the linear decorrelation model for the whole
            system model
        """
        text_decor = ""
        for inst_mod_obj_decorr_var_name, decorrelation_config_decorr_var in decorrelation_config.items():
            # Get the coefficient parameter inside the inst_mod_obj
            param_cor_coeff = inst_mod_obj.parameters[check_name(f"{cls.root_name_coeffcorr}{model_part}{inst_mod_obj_decorr_var_name}")]
            # Add this parameters to the parameters of the function
            cor_coeff = add_param_argument(param=param_cor_coeff, arg_list=arg_list, key_param=key_param,
                                           param_nb=param_nb, key_arglist=key_func, param_vector_name=par_vec_name
                                           )[key_func]
            if len(text_decor) > 0:
                text_decor += " + "
            if decorrelation_config_decorr_var["quantity"] == "raw":
                # Get the list of decorrelation variable datasets.
                l_dataset_name_decor_var = [decorrelation_config_decorr_var['match datasets'][dataset_name] for dataset_name in l_dataset_name_inst_mod]
                l_dataset_decor_var = [dataset_db[dataset_name] for dataset_name in l_dataset_name_decor_var]
                if len(l_dataset_decor_var) > 1:
                    time = np.concatenate([dataset.get_time() for dataset in l_dataset_decor_var])
                    data = np.concatenate([dataset.get_data() for dataset in l_dataset_decor_var])
                else:
                    time = l_dataset_decor_var[0].get_time()
                    data = l_dataset_decor_var[0].get_data()
                idx_sort = np.argsort(time)
                ldict[key_func][inst_mod_obj_decorr_var_name.replace("-", "")] = scale_and_interpolate(t=time[idx_sort], x=data[idx_sort], scale='range')
                if multi:
                    text_decor += f"{cor_coeff} * {inst_mod_obj_decorr_var_name.replace('-','')}({time_arg_name}[{idx_inst_mod_obj}])"
                else:
                    text_decor += f"{cor_coeff} * {inst_mod_obj_decorr_var_name.replace('-','')}({time_arg_name})"
            else:
                raise NotImplementedError(f"Quantity {decorrelation_config_decorr_var['quantity']} is not yet implemented for decorrelation method {cls.category}")
        return text_decor
