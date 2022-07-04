#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Decorrelation model module.
"""
from logging import getLogger
from scipy.interpolate import UnivariateSpline
from scipy.interpolate import LSQUnivariateSpline  # This should allow to specify the knots
from numpy import concatenate, argsort, linspace
from matplotlib.pyplot import subplots

from ....core.likelihood.core_decorrelation_likelihood import Core_DecorrelationLikelihood


## Logger object
logger = getLogger()

tab = "    "


class SplineDecorrelation(Core_DecorrelationLikelihood):
    """docstring for SplineDecorrelation."""

    # Mandatory attributes from Core_DecorrelationModel
    __category__ = "spline"
    __format_config_dict__ = "{'quantity': 'raw', 'spline_type': 'UnivariateSpline', 'spline_kwargs': {}}"
    __allowed_quantity_strs__ = ['raw', ]
    __modelpart_4_decorrlikelihood__ = "add"

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
    def load_text_decorr_paramfile(cls, inst_mod_obj, decorrelation_config_inst_decorr_paramfile, decorrelation_config_inst_decorr):
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
        """
        super(SplineDecorrelation, cls).load_text_decorr_paramfile(inst_mod_obj=inst_mod_obj,
                                                                   decorrelation_config_inst_decorr_paramfile=decorrelation_config_inst_decorr_paramfile,
                                                                   decorrelation_config_inst_decorr=decorrelation_config_inst_decorr,
                                                                   skip_load=True)
        for inst_mod_obj_decorr_var_name in decorrelation_config_inst_decorr_paramfile.keys():
            # Check that the "quantity" and "spline_kwargs" are in the dictionary
            if not(all([key in decorrelation_config_inst_decorr_paramfile[inst_mod_obj_decorr_var_name] for key in ["quantity", "spline_kwargs"]])):
                raise ValueError(f"The dictionary for the configuration of the spline decorrelation of {inst_mod_obj.full_name}"
                                 f" with {inst_mod_obj_decorr_var_name} must include the keys 'quantity' and 'spline_kwargs'.")
            quantity = decorrelation_config_inst_decorr_paramfile[inst_mod_obj_decorr_var_name]["quantity"]
            spline_type = decorrelation_config_inst_decorr_paramfile[inst_mod_obj_decorr_var_name].get("spline_type", "UnivariateSpline")
            spline_kwargs = decorrelation_config_inst_decorr_paramfile[inst_mod_obj_decorr_var_name]["spline_kwargs"]
            # Check that the "quantity" value is valid
            if quantity not in cls.__allowed_quantity_strs__:
                raise ValueError(f"'quantity' for the configuration of the spline decorrelation of {inst_mod_obj.full_name}"
                                 f" with {inst_mod_obj_decorr_var_name} must be in {cls.__allowed_quantity_strs__}.")
            # If quantity is raw, check that "match datasets" is in the dictionary
            if quantity == "raw":
                if "match datasets" not in decorrelation_config_inst_decorr_paramfile[inst_mod_obj_decorr_var_name]:
                    raise ValueError(f"Since quantity is {quantity}, the dictionary for the configuration of the spline decorrelation of {inst_mod_obj.full_name}"
                                     f" with {inst_mod_obj_decorr_var_name} must include the key 'match datasets'.")
            # Check spline_type
            if spline_type not in ["UnivariateSpline", "LSQUnivariateSpline"]:
                raise ValueError(f"Spline_type for the decorrelation of {inst_mod_obj.full_name}"
                                 f" with {inst_mod_obj_decorr_var_name} is invalid. Must be in ['UnivariateSpline', 'LSQUnivariateSpline'] got {spline_type}.")
            # TODO: Check content of spline_kwargs which will be passed to scipy.interpolate.UnivariateSpline
            # Store the decorrelation configuration
            decorrelation_config_inst_decorr[inst_mod_obj_decorr_var_name] = decorrelation_config_inst_decorr_paramfile[inst_mod_obj_decorr_var_name]

    @classmethod
    def apply_parametrisation(cls, inst_mod_obj, decorrelation_config_inst_decorr, model_part=""):
        """Apply the parametrisation for the decorrelation to an instrument model.

        This function is used by parametrisation_gravgroup.apply_instmodel_parametrisation.
        For now there is no parameters for this type of decorrelation

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
        pass

    @classmethod
    def create_decorrelation_likelihood(cls, function_builder, l_function_shortname, inst_model_obj, ind_instmodel_obj,
                                        dico_decorr_ind, dico_decorr_config_ind, l_dataset_name_4_instmod,
                                        l_dataset_name, l_paramsfullname_likelihood, dataset_kwargs, inddataset_kwargs,
                                        datasim_has_multioutputs, plot_functionshortname=None):
        """Create the likelihood decorrelation for a given instrument model and a given indicator model.

        Arguments
        ---------
        function_builder            :
        l_function_shortname        :
        inst_model_obj              :
        ind_instmodel_obj           :
        dico_decorr_ind             :
        dico_decorr_config_ind      :
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
        for function_shortname in l_function_shortname:
            # You need to store in ldict spline_kargs_{ind_inst_model_fullname.strip('-')}
            function_builder.add_variable_to_ldict(variable_name="concatenate", variable_content=concatenate, function_shortname=function_shortname, exist_ok=True, overwrite=False)
            function_builder.add_variable_to_ldict(variable_name="l_dataset_name", variable_content=l_dataset_name, function_shortname=function_shortname, exist_ok=True, overwrite=False)
            function_builder.add_variable_to_ldict(variable_name=f"spline_kargs_{inst_model_obj.full_code_name}_{ind_instmodel_obj.full_code_name}", variable_content=dico_decorr_config_ind['spline_kwargs'], function_shortname=function_shortname, exist_ok=False, overwrite=False)
            function_builder.add_variable_to_ldict(variable_name=f"l_inddataset_name_{inst_model_obj.full_code_name}_{ind_instmodel_obj.full_code_name}", variable_content=dico_decorr_ind["l_inddataset_name"], function_shortname=function_shortname, exist_ok=False, overwrite=False)
            spline_type = dico_decorr_config_ind.get("spline_type", "UnivariateSpline")
            if spline_type == "UnivariateSpline":
                function_builder.add_variable_to_ldict(variable_name="UnivariateSpline", variable_content=UnivariateSpline, function_shortname=function_shortname, exist_ok=True, overwrite=False)
            elif spline_type == "LSQUnivariateSpline":
                function_builder.add_variable_to_ldict(variable_name="LSQUnivariateSpline", variable_content=LSQUnivariateSpline, function_shortname=function_shortname, exist_ok=True, overwrite=False)
            x_vect = concatenate([inddataset_kwargs[inddataset_name]['data'] for inddataset_name in dico_decorr_ind["l_inddataset_name"]])
            text_all_indval = f"concatenate([inddataset_kwargs[inddataset_name]['data'] for inddataset_name in l_inddataset_name_{inst_model_obj.full_code_name}_{ind_instmodel_obj.full_code_name}])[idx_sort_{inst_model_obj.full_code_name}_{ind_instmodel_obj.full_code_name}]"
            idx_sort_x_vect = argsort(x_vect)
            function_builder.add_variable_to_ldict(variable_name=f"idx_sort_{inst_model_obj.full_code_name}_{ind_instmodel_obj.full_code_name}", variable_content=idx_sort_x_vect, function_shortname=function_shortname, exist_ok=False, overwrite=False)
            if datasim_has_multioutputs:
                text_all_resi = f"concatenate([dataset_kwargs[l_dataset_name[idx]]['data'] - sim_data[idx] for idx in {dico_decorr_ind['l_idx_simdata']}])[idx_sort_{inst_model_obj.full_code_name}_{ind_instmodel_obj.full_code_name}]"
            else:
                text_all_resi = f"concatenate([dataset_kwargs[l_dataset_name[idx]]['data'] - sim_data for idx in {dico_decorr_ind['l_idx_simdata']}])[idx_sort_{inst_model_obj.full_code_name}_{ind_instmodel_obj.full_code_name}]"
            function_builder.add_to_body_text(f"{tab}sp_{inst_model_obj.full_code_name}_{ind_instmodel_obj.full_code_name} = {spline_type}(x={text_all_indval}, y={text_all_resi}, **spline_kargs_{inst_model_obj.full_code_name}_{ind_instmodel_obj.full_code_name})\n", function_shortname=function_shortname)
            if function_shortname == plot_functionshortname:
                function_builder.add_variable_to_ldict(variable_name="subplots", variable_content=subplots, function_shortname=function_shortname, exist_ok=True)
                function_builder.add_variable_to_ldict(variable_name="linspace", variable_content=linspace, function_shortname=function_shortname, exist_ok=True)
                function_builder.add_optional_argument(argument_name="npt_spline", default_value=100, function_shortname=function_shortname, exist_ok=True)
                function_builder.add_to_body_text(f"{tab}fig, ax = subplots()\n", function_shortname=function_shortname)
                function_builder.add_to_body_text(f"{tab}x_{inst_model_obj.full_code_name}_{ind_instmodel_obj.full_code_name} = linspace(min({text_all_indval}), max({text_all_indval}), npt_spline)\n", function_shortname=function_shortname)
                function_builder.add_to_body_text(text=f"{tab}ax.plot({text_all_indval}, {text_all_resi}, '.', label='residuals')\n", function_shortname=function_shortname)
                function_builder.add_to_body_text(text=f"{tab}ax.plot(x_{inst_model_obj.full_code_name}_{ind_instmodel_obj.full_code_name}, sp_{inst_model_obj.full_code_name}_{ind_instmodel_obj.full_code_name}(x_{inst_model_obj.full_code_name}_{ind_instmodel_obj.full_code_name}), label='spline fit')\n", function_shortname=function_shortname)
                function_builder.add_to_body_text(text=f"{tab}ax.set_xlabel('{ind_instmodel_obj.full_code_name}')\n", function_shortname=function_shortname)
                function_builder.add_to_body_text(text=f"{tab}ax.set_ylabel('{inst_model_obj.full_code_name}')\n", function_shortname=function_shortname)
                function_builder.add_to_body_text(text=f"{tab}ax.legend()\n", function_shortname=function_shortname)
            decorrtext_4_dataset = {dst_name: "" for dst_name in l_dataset_name_4_instmod}
            for dataset_name in l_dataset_name_4_instmod:
                decorrtext_4_dataset[dataset_name] = f"sp_{inst_model_obj.full_code_name}_{ind_instmodel_obj.full_code_name}(inddataset_kwargs['{dico_decorr_config_ind['match datasets'][dataset_name]}']['data'])"
        return decorrtext_4_dataset, l_paramsfullname_likelihood
