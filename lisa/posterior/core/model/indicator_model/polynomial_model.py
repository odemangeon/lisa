#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Datasim creator for the polynomial model of indicator
"""
from logging import getLogger

from .core_indicator_model import Core_Indicator_Model
from ..polynomial_model import apply_polymodel_parametrisation, set_dico_config, get_dico_config, get_polymodel
# from ....core.parameter import Parameter


## Logger object
logger = getLogger()


tab = "    "


class PolynomialIndicatorModel(Core_Indicator_Model):
    """docstring for PolynomialIndicatorModel."""

    # Define name of indicator models
    __model_name__ = "polynomial"

    __drift_basename__ = "drift"
    __name_coeff_const_inst__ = "C0"
    __name_coeff_const_sys__ = "{indicator}0"
    # # Define name of polynomial model parameters
    # _polynomial_order_name = "order"

    # # Default parameter values
    # _default_param_values = {_polynomial_order_name: 0}

    @classmethod
    def apply_parametrisation(cls, param_container, indicator_category, instrument_per_instrument=True, prefix=None):
        """Apply the parametrisation for the polynomial modelling of a given instrument category.

        Arguments
        ---------
        param_container             : Param_Container
        indicator_category          : str
        instrument_per_instrument   : bool
        prefix                      : str
        """
        if instrument_per_instrument:
            name_coeff_const = cls.__name_coeff_const_inst__
        else:
            name_coeff_const = cls.__name_coeff_const_sys__.format(indicator=indicator_category)
        apply_polymodel_parametrisation(param_container=param_container, name_coeff_const=name_coeff_const,
                                        func_param_name=lambda order: cls.get_param_name(order=order, prefix=prefix),
                                        full_category_4_unit=indicator_category,
                                        prefix=prefix)

    @classmethod
    def get_param_name(cls, order, prefix):
        """Return the parameter name of the coefficient of the RV drift model."""
        if prefix is None:
            return f"{cls.__drift_basename__}{order}"
        else:
            return f"{prefix}{cls.__drift_basename__}{order}"

    @classmethod
    def set_dico_config(cls, param_container, prefix, dico_config=None):
        """Get the dictionary that configures the polynomial model for a given instrument category
        Proxy for lisa.posterior.core.model.polynomial_model.set_dico_config

        Arguments
        ---------
        param_container     : Param_Container
        prefix  : str
        dico_config         : dict
            Updates that you might want to do to the dico that configure the polynomial model
        """
        set_dico_config(param_container=param_container, prefix=prefix, dico_config=dico_config)

    @classmethod
    def get_dico_config(cls, param_container, prefix, notexist_ok=False, return_None_if_notexist=False):
        """Get the dictionary that configures the polynomial model for a given instrument category
        Proxy for lisa.posterior.core.model.polynomial_model.set_dico_config

        Arguments
        ---------
        inst_cat        : str
            Instrument category
        dico_config     : dict
            Updates that you might want to do to the dico that configure the polynomial model
        """
        return get_dico_config(param_container=param_container, prefix=prefix, notexist_ok=notexist_ok,
                               return_None_if_notexist=return_None_if_notexist)

    # def _init_polynomialind_model(self, inst_model_obj, kwargs_indicator_model):
    #     """Initialise the polynomial indicator model for a given instrument model
    #
    #     Create the required parameters in the instrument model object and define the associated attributes
    #
    #     Arguments
    #     ---------
    #     inst_model_obj         : Instrument_Model
    #         Instance of the Instrument_Model class
    #     kwargs_indicator_model : dictionary
    #         Dictionary giving the arguments required by the indicator model
    #     """
    #     # Set attribute indicator_model and _polynomial_order_name (content of this variable) in inst_model_obj
    #     inst_model_obj.indicator_model = self._polynomial_method_name
    #     ind_cat = inst_model_obj.instrument.indicator_category
    #     inst_model_obj.params_indicator_models = kwargs_indicator_model[ind_cat]
    #     # Create the parameters for the polynomial model in inst_model_obj
    #     for order in range(kwargs_indicator_model[ind_cat][self._polynomial_order_name] + 1):
    #         inst_model_obj.add_parameter(Parameter(name=self.get_polynom_param_order(order),
    #                                                name_prefix=inst_model_obj.name,
    #                                                main=True,
    #                                                unit="[time]^(-{})".format(order)))

    # def get_polynom_param_order(self, order):
    #     """Return the name of the parameter of the given order for the polynomial model of an instrument model
    #
    #     Arguments
    #     ---------
    #     order :  int
    #         Order of the polynomial for which you want the name of the parameter
    #
    #     Returns
    #     -------
    #     param_name : str
    #         Name of the parameter
    #     """
    #     return f"C{order}"

    @classmethod
    def create_datasimulator(cls, model_instance, multi, l_inst_model, l_dataset, get_times_from_datasets,
                             tab, time_vec_name, l_time_vec_name, INDcat_model, indicator_category,
                             dataset_db, function_builder, l_function_shortname, ext_func_fullname):
        """Create a datasimulator for indicators using the polynomial model

        Arguments
        ---------
        model_instance
        multi
        l_inst_model   :
        l_dataset
        get_times_from_datasets  : bool
            If True the times at which the LC model is computed is taken from the datasets.
            Else it is an input of the datasimulator function produced.
        tab
        time_vec_name
        l_time_vec_name
        INDcat_model                 : IND_InstCat_Model
            Instance of the IND_InstCat_Model
        indicator_category          : str
        dataset_db                  : DatasetDatabase
            Dataset database, this will be used by the function to access the all the dataset of a given instrument model,
            not only the datasets to be simulated.
        function_builder
        l_function_shortname
        ext_func_fullname

        Returns
        -------
        d_dico_docf : dict_of_dict_of_DatasimDocFunc
            A dictionary with DocFunctions containing the data
            simulator function for the whole system ("whole") and for the each planet individually
            ("planet_name")
        """
        #######################################################
        # Produce instrumental variations models per instrument
        #######################################################
        d_l_instvar = get_polymodel(multi=multi, l_inst_model=l_inst_model, l_dataset=l_dataset, get_times_from_datasets=get_times_from_datasets,
                                    tab=tab, time_vec_name=time_vec_name, l_time_vec_name=l_time_vec_name, inst_cat_model=INDcat_model,
                                    dataset_db=dataset_db, function_builder=function_builder, l_function_shortname=l_function_shortname,
                                    polyonly_func_shortname=f"{indicator_category}_inst_var", ext_func_fullname=ext_func_fullname,
                                    name_coeff_const=cls.__name_coeff_const_inst__,
                                    func_param_name=lambda order: cls.get_param_name(order=order, prefix=None),
                                    instrument_per_instrument_model=True, param_container=None, prefix_config=None,
                                    )

        #######################################################
        # Produce instrumental variations models per instrument
        #######################################################
        d_l_sysvar = get_polymodel(multi=multi, l_inst_model=l_inst_model, l_dataset=l_dataset, get_times_from_datasets=get_times_from_datasets,
                                   tab=tab, time_vec_name=time_vec_name, l_time_vec_name=l_time_vec_name, inst_cat_model=INDcat_model,
                                   dataset_db=dataset_db, function_builder=function_builder, l_function_shortname=l_function_shortname,
                                   polyonly_func_shortname=f"{indicator_category}_sys_var", ext_func_fullname=ext_func_fullname,
                                   name_coeff_const=cls.__name_coeff_const_sys__.format(indicator=indicator_category),
                                   func_param_name=lambda order: cls.get_param_name(order=order, prefix=indicator_category),
                                   instrument_per_instrument_model=False, param_container=model_instance, prefix_config=indicator_category,
                                   )

        return {f"{indicator_category}_poly_instvar": d_l_instvar, f"{indicator_category}_poly_sysvar": d_l_sysvar}

        # #############################################################
        # # Check the content of the datasets and inst_models arguments
        # #############################################################
        # # - Check the content of inst_models and datasets argument and transform them into two list l_inst_model
        # # and l_dataset which provide the couple (inst_model_obj, dataset) for each output of the datasimulator
        # # - Set multi True if the datasimulator has several outputs (several datasets to be simulated)
        # # - Set the inst_model_fullnames argument for the Datasim_DocFunc (instmod_docf)
        # # - Set the dst_ext extension to be used for the name of the datasimulator function
        # # - Set the instcat_docf, instmod_docf, dtsts_docf to be used as arguments inst_cat, inst_model_fullname,
        # # datasets in the Datasim_DocFunc.
        # (l_dataset, l_inst_model, multi, inst_model_full_name, dst_ext, instcat_docf, instmod_docf,
        #  dtsts_docf) = check_datasets_and_instmodels(datasets, inst_models)
        #
        # #####################################################################################################
        # ## Initialise the function in the function builder for the whole system and the planet and planet only functions
        # #####################################################################################################
        # # Create the FunctionBuilder
        # function_builder = FunctionBuilder(parameter_vector_name=par_vec_name)
        # # Initialise the whole function
        # function_builder.add_new_function(shortname=function_whole_shortname)
        # if multi:
        #     func_full_name_MultiOrDst_ext = "_multi"
        # else:
        #     func_full_name_MultiOrDst_ext = f"{l_dataset[0].dataset_code_name}"
        # function_builder.set_function_fullname(full_name=f"INDpolynomailsim__{function_whole_shortname}_{func_full_name_MultiOrDst_ext}", shortname=function_whole_shortname)
        #
        # #######################
        # # Add the time argument
        # #######################
        # # Even if the model is a constant you want to generate a vector of constant values that can
        # # compared with the data (for the likelihood computation) or plotted without issue
        # time_arg_name = add_time_argument(function_builder=function_builder, function_shortname=function_whole_shortname,
        #                                   multi=multi, get_times_from_datasets=get_times_from_datasets,
        #                                   l_dataset=l_dataset, time_vec_name=time_vec, l_time_vec_name=l_time_vec,
        #                                   exist_ok=True)
        #
        # ####################################################################
        # # Get the polynomial variations for each couple instrument - dataset
        # ####################################################################
        # l_return_polyvar = []
        # # For each instrument model and dataset, ...
        # for ii, instmdl, dst in zip(range(len(l_inst_model)), l_inst_model, l_dataset):
        #     l_return_polyvar.append("")
        #     # ..., For each order in the required polynomial model, ...
        #     for order in range(instmdl.params_indicator_models[polynomial_order_name] + 1):
        #         # ..., get the name and full name of the parameter for this order
        #         coef_param_name = self.get_polynom_param_order(order)
        #         # ..., If this parameter is a main parameter (it should be), ...
        #         if instmdl.parameters[coef_param_name].main:
        #             value_not0 = True
        #             function_builder.add_parameter(parameter=instmdl.parameters[coef_param_name], function_shortname=function_whole_shortname)
        #             text_coef_param = function_builder.get_text_4_parameter(parameter=instmdl.parameters[coef_param_name], function_shortname=function_whole_shortname)
        #             # ..., if the parameter is free or the fixed value is not zero, ...
        #             if text_coef_param != str(0.0):
        #                 if (order == 0) and (instmdl.params_indicator_models[polynomial_order_name] == 0):
        #                     function_builder.add_variable_to_ldict(variable_name="ones_like", variable_content=ones_like,
        #                                                            function_shortname=function_whole_shortname, exist_ok=True)
        #                     if multi:
        #                         l_return_polyvar[ii] += f"{text_coef_param} * ones_like({time_arg_name}[{ii}])"
        #                     else:
        #                         l_return_polyvar[ii] += f"{text_coef_param} * ones_like({time_arg_name})"
        #                 else:
        #                     if l_return_polyvar[ii] == "":
        #                         pretext = ""
        #                     else:
        #                         pretext = " + "
        #                     l_return_polyvar[ii] += f"{pretext}{text_coef_param}"
        #             # ..., else, since the fixed value is zero, this order doesn't have any
        #             # contribution
        #             else:
        #                 value_not0 = False
        #             # ..., if the order has a contribution to the out of transit variation and
        #             # the considered order is more than 0 meaning the time plays a role, ...
        #             if value_not0 and order > 0:
        #                 # ..., and you need a time reference. There is one time reference per instrument
        #                 # model, which is automatically set to the time of the first measurement
        #                 # among the datasets associated with this instrument model.
        #                 # So start be creating the name of the instrument model
        #                 timeref_instmod = f"timeref_polyvar_{instmdl.full_code_name}"
        #                 # if this time_reference is not already in the ldict of the function ...
        #                 if timeref_instmod not in function_builder.get_ldict(function_shortname=function_whole_shortname):
        #                     # we have to compute its value and add it to the ldict
        #                     l_dataset_name_instmod = INDcat_model.get_l_datasetname(instmod_fullnames=instmdl.full_name)
        #                     timeref_instmod_value = min([min(dataset_db[dataset_name].get_time()) for dataset_name in l_dataset_name_instmod])
        #                     function_builder.add_variable_to_ldict(variable_name=timeref_instmod, variable_content=timeref_instmod_value, function_shortname=function_whole_shortname)
        #                 # ..., add the end of this order's contribution to the text of the polynomial variations
        #                 if order == 1:
        #                     if multi:
        #                         l_return_polyvar[ii] += f" * ({time_arg_name}[{ii}] - {timeref_instmod}) "
        #                     else:
        #                         l_return_polyvar[ii] += f" * ({time_arg_name} - {timeref_instmod}) "
        #                 elif order > 1:
        #                     if multi:
        #                         l_return_polyvar[ii] += f" * ({time_arg_name}[{ii}] - {timeref_instmod})**{order}"
        #                     else:
        #                         l_return_polyvar[ii] += f" * ({time_arg_name} - {timeref_instmod})**{order}"
        #             # # If the is no contribution to the oot of transit variation from this order
        #             # # add only a space.
        #             # elif value_not0 and order == 0:
        #             #     l_return_polyvar[ii] += " "
        #
        # #####################################
        # # Finalize the whole function
        # #####################################
        # function_builder.add_to_body_text(text=f"{tab}return {', '.join(l_return_polyvar)}", function_shortname=function_whole_shortname)
        #
        # ###################################
        # # Execute the text of all functions
        # ###################################
        # # Create and fill the output dictionnary containing the datasimulators functions.
        # # dico_docf = dict.fromkeys(text_def_func.keys(), None)
        # dico_docf = {}
        # for func_shortname in function_builder.l_function_shortname:
        #     logger.debug(f"text of {func_shortname} IND simulator function with polynomial model :\n{function_builder.get_full_function_text(shortname=func_shortname)}")
        #     exec(function_builder.get_full_function_text(shortname=func_shortname), function_builder._get_ldict(function_shortname=func_shortname))
        #     params_model = [param.full_name for param in function_builder.get_free_parameter_vector(function_shortname=func_shortname)]
        #     dico_param_nb = {nb: param for nb, param in enumerate(params_model)}
        #     if len(function_builder.get_l_mandatory_argument(function_shortname=func_shortname)) > 0:
        #         mand_kwargs = function_builder.get_l_mandatory_argument(function_shortname=func_shortname)
        #     else:
        #         mand_kwargs = None
        #     if len(function_builder.get_d_optional_argument(function_shortname=func_shortname)) > 0:
        #         opt_kwargs = function_builder.get_d_optional_argument(function_shortname=func_shortname)
        #     else:
        #         opt_kwargs = None
        #     logger.debug(f"Parameters for {func_shortname} LC simulator function :\n{dico_param_nb}")
        #     dico_docf[func_shortname] = DatasimDocFunc(function=function_builder._get_ldict(function_shortname=func_shortname)[function_builder.get_function_fullname(shortname=func_shortname)],
        #                                                param_model_names_list=params_model,
        #                                                params_model_vect_name=par_vec_name,
        #                                                inst_cats_list=instcat_docf,
        #                                                inst_model_fullnames_list=instmod_docf,
        #                                                dataset_names_list=dtsts_docf,
        #                                                include_dataset_kwarg=get_times_from_datasets,
        #                                                mand_kwargs_list=mand_kwargs,
        #                                                opt_kwargs_dict=opt_kwargs,
        #                                                )
        # return dico_docf
