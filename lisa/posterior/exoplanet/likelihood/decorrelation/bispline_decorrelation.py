#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Decorrelation model module.
"""
from logging import getLogger
from scipy.interpolate import SmoothBivariateSpline
from scipy.interpolate import LSQBivariateSpline  # This should allow to specify the knots
from numpy import concatenate, linspace, mean, meshgrid  # argsort
from matplotlib.pyplot import subplots, axes
from textwrap import dedent
from collections import defaultdict
from copy import deepcopy

from ....core.likelihood.core_decorrelation_likelihood import Core_DecorrelationLikelihood
from .....tools.name import check_name_code

## Logger object
logger = getLogger()

tab = "    "


class BiSplineDecorrelation(Core_DecorrelationLikelihood):
    """docstring for SplineDecorrelation."""

    # Mandatory attributes from Core_DecorrelationModel
    __category__ = "bispline"
    __format_config_dict__ = "{'category': 'bispline', 'spline_type': 'SmoothBivariateSpline' or 'LSQBivariateSpline', 'spline_kwargs': {'kx': 3, 'ky': 3}, 'match datasets': {<dataset name>: {'X': <indicator dataset name>, 'Y':<indicator dataset name>}}"
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
        This function checks that the inputs provided are valid and store them in decorrelation_config_inst_decorr

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
        spline_type = config_model_paramfile.get("spline_type", "SmoothBivariateSpline")
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
        if spline_type not in ["SmoothBivariateSpline", "LSQBivariateSpline"]:
            raise ValueError(f"Spline_type for the spline likelihood decorrelation model {model_name} is invalid. "
                             f"Must be in ['SmoothBivariateSpline', 'LSQBivariateSpline'] got {spline_type}.")
        # Check the match datasets values (keys have been checked in Core_InstCat_Model.load_config_decorrelation)
        for dataset_name, xy_ind_dataset_names in config_model_paramfile['match datasets'].items():
            # Check that for each dataset na
            err_msg = (f"Decorrelation likelihood model definition {model_name}: 'match datasets', "
                       f"dataset {dataset_name} should be associated to a dictionary with to keys 'X' and 'Y'"
                       " and values the corresponding indicator datasets."
                       )
            if not(isinstance(xy_ind_dataset_names, dict)):
                raise ValueError(err_msg)
            for xy, xy_dataset_name in xy_ind_dataset_names.items():
                if xy not in ['X', 'Y']:
                    raise ValueError(err_msg)
                # Check that ind_dataset is the name of an existing dataset
                if not(model_instance.dataset_db.isavailable_dataset(dataset=xy_dataset_name)):
                    raise ValueError(f"Decorrelation likelihood model definition {model_name}: "
                                     f"The indicator dataset {xy_dataset_name} associated to dataset {dataset_name} "
                                     f"{xy} keys is not an existing dataset."
                                     )
        # TODO: Check content of spline_kwargs which will be passed to scipy.interpolate.UnivariateSpline
        # Store the decorrelation configuration
        config_model_storage.update(deepcopy(config_model_paramfile))

        # for bispline_decorr_name in decorrelation_config_inst_decorr_paramfile.keys():
        #     # Check that the "quantity" and "spline_kwargs" are in the dictionary
        #     if not(all([key in decorrelation_config_inst_decorr_paramfile[bispline_decorr_name] for key in ['IND instument models', 'quantity', 'spline_type', 'spline_kwargs', 'match datasets']])):
        #         raise ValueError(f"The dictionary for the configuration of the bispline decorrelation of {inst_mod_obj.full_name}"
        #                          f" with {bispline_decorr_name} must include the keys 'quantity', 'spline_type' and 'spline_kwargs'.")
        #     quantity = decorrelation_config_inst_decorr_paramfile[bispline_decorr_name]["quantity"]
        #     spline_type = decorrelation_config_inst_decorr_paramfile[bispline_decorr_name]["spline_type"]
        #     spline_kwargs = decorrelation_config_inst_decorr_paramfile[bispline_decorr_name]["spline_kwargs"]
        #     l_indinstmodel_fullname = decorrelation_config_inst_decorr_paramfile[bispline_decorr_name]['IND instument models']
        #     # Check that the "quantity" value is valid
        #     if quantity not in cls.__allowed_quantity_strs__:
        #         raise ValueError(f"'quantity' for the configuration of the spline decorrelation of {inst_mod_obj.full_name}"
        #                          f" with {bispline_decorr_name} must be in {cls.__allowed_quantity_strs__}.")
        #     # Check spline_type
        #     if spline_type not in ["SmoothBivariateSpline", "LSQBivariateSpline"]:
        #         raise ValueError(f"Spline_type for the decorrelation of {inst_mod_obj.full_name}"
        #                          f" with {bispline_decorr_name} is invalid. Must be in ['SmoothBivariateSpline', 'LSQBivariateSpline'] got {spline_type}.")
        #     # Check l_indinstmodel_fullname
        #     if len(l_indinstmodel_fullname) != 2:
        #         raise ValueError(f"'IND instument models' for the decorrelation of {inst_mod_obj.full_name}"
        #                          f" with {bispline_decorr_name} should contain two elements.")
        #     # TODO: Check content of spline_kwargs which will be passed to scipy.interpolate.UnivariateSpline
        #     # Store the decorrelation configuration
        #     decorrelation_config_inst_decorr[bispline_decorr_name] = decorrelation_config_inst_decorr_paramfile[bispline_decorr_name]

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
        l_ind_instmodel_obj         :
        decorr_name                 :
        dico_decorr_bispline        :
        dico_decorr_config_bispline :
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
        # Get the type of spline requested
        spline_type = dico_decorr_config["spline_type"]
        x_indinstmod_fullname = dico_decorr_config['IND instument models'][0]
        y_indinstmod_fullname = dico_decorr_config['IND instument models'][1]
        # Get the x vector values
        # x_vect = concatenate([inddataset_kwargs[inddataset_name]['data'] for inddataset_name in dico_decorr_bispline["l_inddataset_name_4_indinstmod_fullname"][x_indinstmod_fullname]])
        # y_vect = concatenate([inddataset_kwargs[inddataset_name]['data'] for inddataset_name in dico_decorr_bispline["l_inddataset_name_4_indinstmod_fullname"][y_indinstmod_fullname]])
        text_all_x_indval = f"concatenate([inddataset_kwargs[inddataset_name]['data'] for inddataset_name in l_x_inddataset_name_{inst_model_obj.full_code_name}_{decorr_name}])"
        text_all_y_indval = f"concatenate([inddataset_kwargs[inddataset_name]['data'] for inddataset_name in l_y_inddataset_name_{inst_model_obj.full_code_name}_{decorr_name}])"
        # idx_sort_x_vect = argsort(x_vect)
        if datasim_has_multioutputs:
            text_all_resi = f"concatenate([dataset_kwargs[l_dataset_name[idx]]['data'] - sim_data[idx] for idx in {dico_decorr['l_idx_simdata']}])"
        else:
            text_all_resi = f"concatenate([dataset_kwargs[l_dataset_name[idx]]['data'] - sim_data for idx in {dico_decorr['l_idx_simdata']}])"
        decorr_body_text = f"all_resi = {text_all_resi}\n"
        decorr_body_text += f"sp_{inst_model_obj.full_code_name}_{decorr_name} = {spline_type}(x={text_all_x_indval}, y={text_all_y_indval} ,z=all_resi - mean(all_resi), **spline_kargs_{inst_model_obj.full_code_name}_{decorr_name})\n"
        for function_shortname in l_function_shortname:
            # You need to store in ldict spline_kargs_{ind_inst_model_fullname.strip('-')}
            function_builder.add_variable_to_ldict(variable_name="mean", variable_content=mean, function_shortname=function_shortname, exist_ok=True, overwrite=False)
            function_builder.add_variable_to_ldict(variable_name="concatenate", variable_content=concatenate, function_shortname=function_shortname, exist_ok=True, overwrite=False)
            function_builder.add_variable_to_ldict(variable_name="l_dataset_name", variable_content=l_dataset_name, function_shortname=function_shortname, exist_ok=True, overwrite=False)
            function_builder.add_variable_to_ldict(variable_name=f"spline_kargs_{inst_model_obj.full_code_name}_{decorr_name}", variable_content=dico_decorr_config['spline_kwargs'], function_shortname=function_shortname, exist_ok=False, overwrite=False)
            function_builder.add_variable_to_ldict(variable_name=f"l_x_inddataset_name_{inst_model_obj.full_code_name}_{decorr_name}", variable_content=dico_decorr["l_inddataset_name_4_indinstmod_fullname"][x_indinstmod_fullname], function_shortname=function_shortname, exist_ok=False, overwrite=False)
            function_builder.add_variable_to_ldict(variable_name=f"l_y_inddataset_name_{inst_model_obj.full_code_name}_{decorr_name}", variable_content=dico_decorr["l_inddataset_name_4_indinstmod_fullname"][y_indinstmod_fullname], function_shortname=function_shortname, exist_ok=False, overwrite=False)
            if spline_type == "SmoothBivariateSpline":
                function_builder.add_variable_to_ldict(variable_name="SmoothBivariateSpline", variable_content=SmoothBivariateSpline, function_shortname=function_shortname, exist_ok=True, overwrite=False)
            elif spline_type == "LSQBivariateSpline":
                function_builder.add_variable_to_ldict(variable_name="LSQBivariateSpline", variable_content=LSQBivariateSpline, function_shortname=function_shortname, exist_ok=True, overwrite=False)
            # function_builder.add_variable_to_ldict(variable_name=f"idx_sort_{inst_model_obj.full_code_name}_{ind_instmodel_obj.full_code_name}", variable_content=idx_sort_x_vect, function_shortname=function_shortname, exist_ok=False, overwrite=False)
            # function_builder.add_to_body_text(f"{tab}sp_{inst_model_obj.full_code_name}_{ind_instmodel_obj.full_code_name} = {spline_type}(x={text_all_indval}, y={text_all_resi}, **spline_kargs_{inst_model_obj.full_code_name}_{ind_instmodel_obj.full_code_name})\n", function_shortname=function_shortname)
        if plot_functionshortname in l_function_shortname:
            function_builder.add_variable_to_ldict(variable_name="subplots", variable_content=subplots, function_shortname=plot_functionshortname, exist_ok=True)
            function_builder.add_variable_to_ldict(variable_name="axes", variable_content=axes, function_shortname=plot_functionshortname, exist_ok=True)
            function_builder.add_variable_to_ldict(variable_name="linspace", variable_content=linspace, function_shortname=plot_functionshortname, exist_ok=True)
            function_builder.add_variable_to_ldict(variable_name="meshgrid", variable_content=meshgrid, function_shortname=plot_functionshortname, exist_ok=True)
            function_builder.add_optional_argument(argument_name="npt_spline", default_value=100, function_shortname=plot_functionshortname, exist_ok=True)
            plotdecorr_body_text = f"""
            {{tab}}fig, ax = subplots()
            {{tab}}ax = axes(projection='3d')
            {{tab}}x_{inst_model_obj.full_code_name}_{decorr_name}, y_{inst_model_obj.full_code_name}_{decorr_name} = (linspace(min({text_all_x_indval}), max({text_all_x_indval}), npt_spline), linspace(min({text_all_y_indval}), max({text_all_y_indval}), npt_spline))
            {{tab}}z_{inst_model_obj.full_code_name}_{decorr_name} = sp_{inst_model_obj.full_code_name}_{decorr_name}(x_{inst_model_obj.full_code_name}_{decorr_name}, y_{inst_model_obj.full_code_name}_{decorr_name}, grid=True)
            {{tab}}ax.scatter3D({text_all_x_indval}, {text_all_y_indval}, {text_all_resi}, c={text_all_resi}, cmap='Greens')
            {{tab}}ax.contour3D(*meshgrid(x_{inst_model_obj.full_code_name}_{decorr_name}, y_{inst_model_obj.full_code_name}_{decorr_name}), z_{inst_model_obj.full_code_name}_{decorr_name}, 50, cmap='binary')
            {{tab}}ax.set_xlabel('{x_indinstmod_fullname}')
            {{tab}}ax.set_ylabel('{y_indinstmod_fullname}')
            """
            plotdecorr_body_text = dedent(plotdecorr_body_text)
            plotdecorr_body_text = plotdecorr_body_text.format(tab=tab)
            # function_builder.add_to_body_text(f"{tab}fig, ax = subplots()\n", function_shortname=function_shortname)
            # function_builder.add_to_body_text(f"{tab}x_{inst_model_obj.full_code_name}_{ind_instmodel_obj.full_code_name} = linspace(min({text_all_indval}), max({text_all_indval}), npt_spline)\n", function_shortname=function_shortname)
            # function_builder.add_to_body_text(text=f"{tab}ax.plot({text_all_indval}, {text_all_resi}, '.', label='residuals')\n", function_shortname=function_shortname)
            # function_builder.add_to_body_text(text=f"{tab}ax.plot(x_{inst_model_obj.full_code_name}_{ind_instmodel_obj.full_code_name}, sp_{inst_model_obj.full_code_name}_{ind_instmodel_obj.full_code_name}(x_{inst_model_obj.full_code_name}_{ind_instmodel_obj.full_code_name}), label='spline fit')\n", function_shortname=function_shortname)
            # function_builder.add_to_body_text(text=f"{tab}ax.set_xlabel('{ind_instmodel_obj.full_code_name}')\n", function_shortname=function_shortname)
            # function_builder.add_to_body_text(text=f"{tab}ax.set_ylabel('{inst_model_obj.full_code_name}')\n", function_shortname=function_shortname)
            # function_builder.add_to_body_text(text=f"{tab}ax.legend()\n", function_shortname=function_shortname)
        simdata_decorr_4_dataset = {dst_name: "" for dst_name in l_dataset_name_4_instmod}
        for dataset_name in l_dataset_name_4_instmod:
            simdata_decorr_4_dataset[dataset_name] = f"sp_{inst_model_obj.full_code_name}_{decorr_name}(inddataset_kwargs['{dico_decorr_config['match datasets'][dataset_name][x_indinstmod_fullname]}']['data'], inddataset_kwargs['{dico_decorr_config['match datasets'][dataset_name][y_indinstmod_fullname]}']['data'], grid=False)"
        return simdata_decorr_4_dataset, decorr_body_text, plotdecorr_body_text, l_paramsfullname_likelihood

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
        for dataset_name, inddataset_name_4_indinstmod_fullname in decorr_config["match datasets"].items():
            dico_decorr_instmod_decorr_cat[cls.category][decorr_name]["l_idx_simdata"].append(l_dataset_name.index(dataset_name))
            dico_decorr_instmod_decorr_cat[cls.category][decorr_name]["l_datasetkwargs_req"].append(cls.l_required_datasetkwarg_keys)
            for datasetkwarg in cls.l_required_datasetkwarg_keys:
                if datasetkwarg not in d_required_datasetkwargkeys_4_dataset[dataset_name]:
                    d_required_datasetkwargkeys_4_dataset[dataset_name].append(datasetkwarg)
            for indinstmod_fullname in decorr_config['IND instument models']:
                ind_dataset_name = inddataset_name_4_indinstmod_fullname[indinstmod_fullname]
                dico_decorr_instmod_decorr_cat[cls.category][decorr_name]["l_inddataset_name_4_indinstmod_fullname"][indinstmod_fullname].append(ind_dataset_name)
                dico_decorr_instmod_decorr_cat[cls.category][decorr_name]["l_inddataset_name"].append(ind_dataset_name)
                dico_decorr_instmod_decorr_cat[cls.category][decorr_name]["l_inddatasetkwargs_req"].append(cls.l_required_inddatasetkwarg_keys)
                for datasetkwarg in cls.l_required_inddatasetkwarg_keys:
                    if datasetkwarg not in d_required_datasetkwargkeys_4_inddataset[ind_dataset_name]:
                        d_required_datasetkwargkeys_4_inddataset[ind_dataset_name].append(datasetkwarg)

        return dico_decorr_instmod_decorr_cat, d_required_datasetkwargkeys_4_dataset, d_required_datasetkwargkeys_4_inddataset

    @classmethod
    def defdic_decorr_func(cls):
        def def_dic():
            return {"l_idx_simdata": [],
                    "l_datasetkwargs_req": [],
                    "l_inddataset_name_4_indinstmod_fullname": defaultdict(list),
                    "l_inddataset_name": [],
                    "l_inddatasetkwargs_req": [],
                    }
        return def_dic

    @classmethod
    def defdic_decorr_func(cls):
        return {"l_idx_simdata": [],
                "l_datasetkwargs_req": [],
                "l_inddataset_name_4_indinstmod_fullname": defaultdict(list),
                "l_inddataset_name": [],
                "l_inddatasetkwargs_req": [],
                }
