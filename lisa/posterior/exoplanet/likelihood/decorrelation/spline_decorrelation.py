#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Decorrelation model module.
"""
from loguru import logger
from scipy.interpolate import UnivariateSpline
from scipy.interpolate import LSQUnivariateSpline  # This should allow to specify the knots
from numpy import concatenate, argsort, linspace, mean, isfinite
from matplotlib.pyplot import subplots
from textwrap import dedent
from copy import deepcopy

from ....core.likelihood.core_decorrelation_likelihood import Core_DecorrelationLikelihood
from .....tools.name import check_name_code


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
    def set_parametrisation(cls, decorr_model_config):
        """Apply the parametrisation for the decorrelation to an instrument model.

        This function is used by parametrisation_gravgroup.set_instmodel_parametrisation.
        For now there is no parameters for this type of decorrelation

        Arguments
        ---------
        decorr_model_config    : dict
            Dictionary where the decorrelation configuration is stored for the model
        """
        pass

    @classmethod
    def create_decorrelation_likelihood(cls, function_builder, l_function_shortname, inst_cat, model_name,
                                        dico_config, l_dataset_name, l_paramsfullname_likelihood, dataset_kwargs, inddataset_kwargs,
                                        datasim_has_multioutputs, plot_functionshortname=None
                                        ):
        """Create the text for the likelihood decorrelation for a given decorrelation model of a given
        instrument category.

        This function add the necessary variables to the functions ldict and create the texts but
        doesn't add the text to the body of the function (this is done in Core_Likelihood._create_lnlikelihood)

        This function is called by Core_InstCat_Model.create_decorrelation_likelihood

        Arguments
        ---------
        function_builder            : FunctionBuilder
        l_function_shortname        : list of str
            List of function shortnames
        inst_cat                    : str
            Instrument category associated to the decorrelation model (decorr_model_name) being done
        decorr_model_name           : str
            Name of the decorrelation model
        dico_config                 : dict
            Configuration dictionary for the model being done
        l_dataset_name              : list of str
            List of all dataset names corresponding to the outputs of the datasim function used by the
            likelihood.
        dataset_kwargs              : dict
        inddataset_kwargs           : dict
        l_paramsfullname_likelihood : list of str
            list of the current parameter full names of the likelihood function. This function adds
            the likelihood decorrelation parameter if there is any.
        datasim_has_multioutputs    : bool
            True if the datasim function used by the likelihood has multiplue outputs
        plot_functionshortname      : str
            Short name of the plotting function

        Return
        ------
        simdata_decorr_text         : str
            Text that modify the simulated data according to the decorrelation model.
        l_decorr_output_text        : list of str
            List of text providing the decorrelation model component for each dataset in l_dataset_name.
            If there is no decorrelation model for a dataset the element in the list is None.
        decorr_body_text            : str
            Text that compute the spline functions for the decorrelation model.
        plotdecorr_body_text        : str
            Text for the plotting function which show the spline fit of the residuals.
        l_paramsfullname_likelihood : list of str
            Updated list of parameter full names of the likelihood function. This function adds the
            likelihood decorrelation parameter if there is any.
        """
        model_name = check_name_code(model_name)
        if len(l_function_shortname) == 0:
            raise ValueError("l_function_shortname should not be empty !")
        spline_type = dico_config["spline_type"]
        l_dataset_name_decorr_model = dico_config["match datasets"].keys()
        l_inddataset_name_decorr_model = [dico_config["match datasets"][dataset_name] for dataset_name in l_dataset_name_decorr_model]
        l_inddataset_name_decorr_model_name = f"l_inddataset_name_{inst_cat}_{model_name}"
        x_vect = concatenate([inddataset_kwargs[inddataset_name]['data'] for inddataset_name in l_inddataset_name_decorr_model])
        idx_sort_x_vect = argsort(x_vect)
        x_vect = x_vect[idx_sort_x_vect]
        x_vect_name = f"indvector_{inst_cat}_{model_name}"
        idx_sort_x_vect_name = f"idx_sort_{inst_cat}_{model_name}"
        l_idx_simdata = [l_dataset_name.index(dataset_name_decorr_model) for dataset_name_decorr_model in l_dataset_name_decorr_model]
        l_idx_simdata_name = f"l_idx_simdata_{inst_cat}_{model_name}"
        if datasim_has_multioutputs:
            text_all_resi = f"concatenate([dataset_kwargs[l_dataset_name[idx]]['data'] - sim_data[idx] for idx in {l_idx_simdata_name}])[{idx_sort_x_vect_name}]"
        else:
            text_all_resi = f"concatenate([dataset_kwargs[l_dataset_name[idx]]['data'] - sim_data for idx in {l_idx_simdata_name}])[{idx_sort_x_vect_name}]"
        decorr_body_text = f"all_resi = {text_all_resi}\n"
        spline_kwargs = dico_config['spline_kwargs']
        spline_kwargs_name = f"spline_kargs_{inst_cat}_{model_name}"
        spline_object_name = f"sp_{inst_cat}_{model_name}"
        decorr_body_text += f"{spline_object_name} = {spline_type}(x={x_vect_name}, y=all_resi - mean(all_resi), **{spline_kwargs_name})\n"
        simdata_decorr_text = f"for idx_sim_data, ind_dataset_name in zip({l_idx_simdata_name}, {l_inddataset_name_decorr_model_name}):\n"
        simdata_decorr_text += f"    sim_data_decorr = {spline_object_name}(inddataset_kwargs[ind_dataset_name]['data'])\n"
        simdata_decorr_text += "    if isfinite(sim_data_decorr).all():\n"
        if datasim_has_multioutputs:
            simdata_decorr_text += "        sim_data[idx_sim_data] += sim_data_decorr\n"
        else:
            simdata_decorr_text += "        sim_data += sim_data_decorr\n"
        l_decorr_output_text = [None for dataset_name in l_dataset_name]
        for idx_sim_data, ind_dataset_name in zip(l_idx_simdata, l_inddataset_name_decorr_model):
            l_decorr_output_text[idx_sim_data] = f"{spline_object_name}(inddataset_kwargs['{ind_dataset_name}']['data'])"
        for function_shortname in l_function_shortname:
            function_builder.add_variable_to_ldict(variable_name=x_vect_name, variable_content=x_vect, function_shortname=function_shortname, exist_ok=True, overwrite=False)
            function_builder.add_variable_to_ldict(variable_name=idx_sort_x_vect_name, variable_content=idx_sort_x_vect, function_shortname=function_shortname, exist_ok=False, overwrite=False)
            function_builder.add_variable_to_ldict(variable_name=l_idx_simdata_name, variable_content=l_idx_simdata, function_shortname=function_shortname, exist_ok=False, overwrite=False)
            function_builder.add_variable_to_ldict(variable_name="concatenate", variable_content=concatenate, function_shortname=function_shortname, exist_ok=True, overwrite=False)
            function_builder.add_variable_to_ldict(variable_name="mean", variable_content=mean, function_shortname=function_shortname, exist_ok=True, overwrite=False)
            function_builder.add_variable_to_ldict(variable_name="isfinite", variable_content=isfinite, function_shortname=function_shortname, exist_ok=True, overwrite=False)
            function_builder.add_variable_to_ldict(variable_name="l_dataset_name", variable_content=l_dataset_name, function_shortname=function_shortname, exist_ok=True, overwrite=False)
            function_builder.add_variable_to_ldict(variable_name=spline_kwargs_name, variable_content=spline_kwargs, function_shortname=function_shortname, exist_ok=False, overwrite=False)
            if spline_type == "UnivariateSpline":
                function_builder.add_variable_to_ldict(variable_name="UnivariateSpline", variable_content=UnivariateSpline, function_shortname=function_shortname, exist_ok=True, overwrite=False)
            elif spline_type == "LSQUnivariateSpline":
                function_builder.add_variable_to_ldict(variable_name="LSQUnivariateSpline", variable_content=LSQUnivariateSpline, function_shortname=function_shortname, exist_ok=True, overwrite=False)
            function_builder.add_variable_to_ldict(variable_name=l_inddataset_name_decorr_model_name, variable_content=l_inddataset_name_decorr_model, function_shortname=function_shortname, exist_ok=True, overwrite=False)
        if plot_functionshortname in l_function_shortname:
            function_builder.add_variable_to_ldict(variable_name="subplots", variable_content=subplots, function_shortname=plot_functionshortname, exist_ok=True)
            function_builder.add_variable_to_ldict(variable_name="linspace", variable_content=linspace, function_shortname=plot_functionshortname, exist_ok=True)
            function_builder.add_optional_argument(argument_name="npt_spline", default_value=100, function_shortname=plot_functionshortname, exist_ok=True)
            x_plotmodel_name = f"x_{inst_cat}_{model_name}"
            plotdecorr_body_text = f"""
            fig, ax = subplots()
            {x_plotmodel_name} = linspace(min({x_vect_name}), max({x_vect_name}), npt_spline)
            ax.plot({x_vect_name}, {text_all_resi}, '.', label='residuals')
            ax.plot({x_plotmodel_name}, {spline_object_name}({x_plotmodel_name}), label='spline {inst_cat} {model_name}')
            ax.set_xlabel('indicators {model_name}')
            ax.set_ylabel('residuals {model_name}')
            ax.grid(b=True, which='both', axis='y', alpha=0.5)
            ax.legend()
            """
            plotdecorr_body_text = dedent(plotdecorr_body_text)
        return simdata_decorr_text, l_decorr_output_text, decorr_body_text, plotdecorr_body_text, l_paramsfullname_likelihood
