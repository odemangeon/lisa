#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Decorrelation model module.
"""
from logging import getLogger
from scipy.interpolate import UnivariateSpline
from scipy.interpolate import LSQUnivariateSpline  # This should allow to specify the knots
from numpy import concatenate, argsort, linspace, mean
from matplotlib.pyplot import subplots
from textwrap import dedent
from copy import deepcopy

from ....core.likelihood.core_decorrelation_likelihood import Core_DecorrelationLikelihood
from .....tools.name import check_name_code

## Logger object
logger = getLogger()

tab = "    "


class SplineDecorrelation(Core_DecorrelationLikelihood):
    """docstring for SplineDecorrelation."""

    # Mandatory attributes from Core_DecorrelationModel
    __category__ = "spline"
    __format_config_dict__ = "{'category': 'spline', 'spline_type': 'UnivariateSpline' or 'LSQUnivariateSpline', 'spline_kwargs': {'k': 3}, 'match datasets': {<dataset name>: <indicator dataset name>}}"
    __allowed_quantity_strs__ = ['raw', ]

    ##  List of keys (string) giving the dataset kwargs of the indicators dataset required for
    # the computation of the decorrelation model.
    # This info will be used to get these dataset_kwargs out of the indicator datasets and produce the
    # inddataset_kwargs variable which will contain all the dataset_kwargs of the indicators required
    # for the decorrelation prior to the likelihood computation.
    __l_required_inddatasetkwarg_keys__ = ["data", ]

    # List of keys (string) giving the dataset kwargs of the datasets (not the indicator
    # datasets, the datasets associated to the indicator dataset for the decorrelation) required for
    # the computation of the decorrelation model.
    # This info will be used to get these dataset_kwargs out of the dataset and produce the dataset_kwargs
    # variable which will contain all the dataset_kwargs required for the decorrelation prior to the
    # likelihood computation.
    __l_required_datasetkwarg_keys__ = ["data", ]

    # Mandatory method from Core_DecorrelationModel
    @classmethod
    def load_text_decorr_paramfile(cls, model_name, config_model_paramfile, config_model_storage, model_instance):
        """load the parametrisation for the decorrelation of one instrument model from the inst cat param file.

        This function is used by Core_InstCat_Model.load_config_decorrelation
        This function checks that the inputs provided are valid and store them in config_model_storage

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
        quantity = config_model_paramfile.get('quantity', 'raw')
        spline_type = config_model_paramfile.get("spline_type", "UnivariateSpline")
        if 'spline_kwargs' in config_model_paramfile:
            spline_kwargs = config_model_paramfile["spline_kwargs"]
        else:
            raise ValueError(f"Decorrelation likelihood model definition {model_name}: missing mandatory "
                             "key 'spline_kwargs' which must contain a dict with the kwargs to pass to the spline function"
                             )
        # Check that the "quantity" value is valid
        if quantity not in cls.__allowed_quantity_strs__:
            raise ValueError(f"'quantity' for the configuration of the spline likelihood decorrelation "
                             f"model {model_name} must be in {cls.__allowed_quantity_strs__}.")
        # Check spline_type
        if spline_type not in ["UnivariateSpline", "LSQUnivariateSpline"]:
            raise ValueError(f"Spline_type for the spline likelihood decorrelation model {model_name} is invalid. "
                             f"Must be in ['UnivariateSpline', 'LSQUnivariateSpline'] got {spline_type}.")
        # Check the match datasets values (keys have been checked in Core_InstCat_Model.load_config_decorrelation)
        for dataset_name, ind_dataset_name in config_model_paramfile['match datasets'].items():
            # Check that ind_dataset is the name of an existing dataset
            if not(model_instance.dataset_db.isavailable_dataset(dataset=ind_dataset_name)):
                raise ValueError(f"Decorrelation likelihood model definition {model_name}: "
                                 f"Indicator dataset {ind_dataset_name} associated to dataset {dataset_name} "
                                 "is not an existing dataset."
                                 )
        # TODO: Check content of spline_kwargs which will be passed to scipy.interpolate.UnivariateSpline
        # Store the decorrelation configuration
        config_model_storage.update(deepcopy(config_model_paramfile))

    @classmethod
    def apply_parametrisation(cls, decorr_model_config):
        """Apply the parametrisation for the decorrelation to an instrument model.

        This function is used by parametrisation_gravgroup.apply_instmodel_parametrisation.
        For now there is no parameters for this type of decorrelation

        Arguments
        ---------
        decorr_model_config    : dict
            Dictionary where the decorrelation configuration is stored for the model
        """
        pass

    @classmethod
    def create_decorrelation_likelihood(cls, function_builder, l_function_shortname, inst_model_obj,
                                        decorr_name, dico_decorr, dico_decorr_config, l_dataset_name_4_instmod,
                                        l_dataset_name, l_paramsfullname_likelihood, dataset_kwargs, inddataset_kwargs,
                                        datasim_has_multioutputs, plot_functionshortname=None):
        """Create the likelihood decorrelation for a given instrument model and a given indicator model.

        Arguments
        ---------
        function_builder            :
        l_function_shortname        :
        inst_model_obj              :
        decorr_name                 :
        dico_decorr                 :
        dico_decorr_config          :
        l_dataset_name_4_instmod    :
        l_dataset_name              :
        l_paramsfullname_likelihood :
        dataset_kwargs              :
        inddataset_kwargs           :
        datasim_has_multioutputs    :
        plot_functionshortname      :

        Return
        ------
        decorrtext_4_dataset        :
        l_paramsfullname_likelihood  :
        """
        decorr_name = check_name_code(decorr_name)
        if len(l_function_shortname) == 0:
            raise ValueError("l_function_shortname should not be empty !")
        spline_type = dico_decorr_config.get("spline_type", "UnivariateSpline")
        x_vect = concatenate([inddataset_kwargs[inddataset_name]['data'] for inddataset_name in dico_decorr["l_inddataset_name"]])
        text_all_indval = f"concatenate([inddataset_kwargs[inddataset_name]['data'] for inddataset_name in l_inddataset_name_{inst_model_obj.full_code_name}_{decorr_name}])[idx_sort_{inst_model_obj.full_code_name}_{decorr_name}]"
        idx_sort_x_vect = argsort(x_vect)
        if datasim_has_multioutputs:
            text_all_resi = f"concatenate([dataset_kwargs[l_dataset_name[idx]]['data'] - sim_data[idx] for idx in {dico_decorr['l_idx_simdata']}])[idx_sort_{inst_model_obj.full_code_name}_{decorr_name}]"
        else:
            text_all_resi = f"concatenate([dataset_kwargs[l_dataset_name[idx]]['data'] - sim_data for idx in {dico_decorr['l_idx_simdata']}])[idx_sort_{inst_model_obj.full_code_name}_{decorr_name}]"
        decorr_body_text = f"all_resi = {text_all_resi}\n"
        decorr_body_text += f"sp_{inst_model_obj.full_code_name}_{decorr_name} = {spline_type}(x={text_all_indval}, y=all_resi - mean(all_resi), **spline_kargs_{inst_model_obj.full_code_name}_{decorr_name})\n"
        for function_shortname in l_function_shortname:
            # You need to store in ldict spline_kargs_{ind_inst_model_fullname.strip('-')}
            function_builder.add_variable_to_ldict(variable_name="mean", variable_content=mean, function_shortname=function_shortname, exist_ok=True, overwrite=False)
            function_builder.add_variable_to_ldict(variable_name="concatenate", variable_content=concatenate, function_shortname=function_shortname, exist_ok=True, overwrite=False)
            function_builder.add_variable_to_ldict(variable_name="l_dataset_name", variable_content=l_dataset_name, function_shortname=function_shortname, exist_ok=True, overwrite=False)
            function_builder.add_variable_to_ldict(variable_name=f"spline_kargs_{inst_model_obj.full_code_name}_{decorr_name}", variable_content=dico_decorr_config['spline_kwargs'], function_shortname=function_shortname, exist_ok=False, overwrite=False)
            function_builder.add_variable_to_ldict(variable_name=f"l_inddataset_name_{inst_model_obj.full_code_name}_{decorr_name}", variable_content=dico_decorr["l_inddataset_name"], function_shortname=function_shortname, exist_ok=False, overwrite=False)
            if spline_type == "UnivariateSpline":
                function_builder.add_variable_to_ldict(variable_name="UnivariateSpline", variable_content=UnivariateSpline, function_shortname=function_shortname, exist_ok=True, overwrite=False)
            elif spline_type == "LSQUnivariateSpline":
                function_builder.add_variable_to_ldict(variable_name="LSQUnivariateSpline", variable_content=LSQUnivariateSpline, function_shortname=function_shortname, exist_ok=True, overwrite=False)
            function_builder.add_variable_to_ldict(variable_name=f"idx_sort_{inst_model_obj.full_code_name}_{decorr_name}", variable_content=idx_sort_x_vect, function_shortname=function_shortname, exist_ok=False, overwrite=False)
            # function_builder.add_to_body_text(f"{tab}sp_{inst_model_obj.full_code_name}_{decorr_name} = {spline_type}(x={text_all_indval}, y={text_all_resi}, **spline_kargs_{inst_model_obj.full_code_name}_{decorr_name})\n", function_shortname=function_shortname)
        if plot_functionshortname in l_function_shortname:
            function_builder.add_variable_to_ldict(variable_name="subplots", variable_content=subplots, function_shortname=plot_functionshortname, exist_ok=True)
            function_builder.add_variable_to_ldict(variable_name="linspace", variable_content=linspace, function_shortname=plot_functionshortname, exist_ok=True)
            function_builder.add_optional_argument(argument_name="npt_spline", default_value=100, function_shortname=plot_functionshortname, exist_ok=True)
            plotdecorr_body_text = f"""
            {{tab}}fig, ax = subplots()
            {{tab}}x_{inst_model_obj.full_code_name}_{decorr_name} = linspace(min({text_all_indval}), max({text_all_indval}), npt_spline)
            {{tab}}ax.plot({text_all_indval}, {text_all_resi}, '.', label='residuals')
            {{tab}}ax.plot(x_{inst_model_obj.full_code_name}_{decorr_name}, sp_{inst_model_obj.full_code_name}_{decorr_name}(x_{inst_model_obj.full_code_name}_{decorr_name}), label='spline fit')
            {{tab}}ax.set_xlabel('{decorr_name}')
            {{tab}}ax.set_ylabel('{inst_model_obj.full_code_name}')
            {{tab}}ax.grid(b=True, which='both', axis='y', alpha=0.5)
            {{tab}}ax.legend()
            """
            plotdecorr_body_text = dedent(plotdecorr_body_text)
            plotdecorr_body_text = plotdecorr_body_text.format(tab=tab)
            # function_builder.add_to_body_text(f"{tab}fig, ax = subplots()\n", function_shortname=function_shortname)
            # function_builder.add_to_body_text(f"{tab}x_{inst_model_obj.full_code_name}_{decorr_name} = linspace(min({text_all_indval}), max({text_all_indval}), npt_spline)\n", function_shortname=function_shortname)
            # function_builder.add_to_body_text(text=f"{tab}ax.plot({text_all_indval}, {text_all_resi}, '.', label='residuals')\n", function_shortname=function_shortname)
            # function_builder.add_to_body_text(text=f"{tab}ax.plot(x_{inst_model_obj.full_code_name}_{decorr_name}, sp_{inst_model_obj.full_code_name}_{decorr_name}(x_{inst_model_obj.full_code_name}_{decorr_name}), label='spline fit')\n", function_shortname=function_shortname)
            # function_builder.add_to_body_text(text=f"{tab}ax.set_xlabel('{decorr_name}')\n", function_shortname=function_shortname)
            # function_builder.add_to_body_text(text=f"{tab}ax.set_ylabel('{inst_model_obj.full_code_name}')\n", function_shortname=function_shortname)
            # function_builder.add_to_body_text(text=f"{tab}ax.legend()\n", function_shortname=function_shortname)
        simdata_decorr_4_dataset = {dst_name: "" for dst_name in l_dataset_name_4_instmod}
        for dataset_name in l_dataset_name_4_instmod:
            simdata_decorr_4_dataset[dataset_name] = f"sp_{inst_model_obj.full_code_name}_{decorr_name}(inddataset_kwargs['{dico_decorr_config['match datasets'][dataset_name]}']['data'])"
        return simdata_decorr_4_dataset, decorr_body_text, plotdecorr_body_text, l_paramsfullname_likelihood
