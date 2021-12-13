#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Datasim creator for the polynomial model of indicator
"""
from logging import getLogger
from textwrap import dedent
from numpy import ones_like

from ....core.parameter import Parameter
from ....core.model.datasimulator_toolbox import check_datasets_and_instmodels  # , get_has_datasets
from ....core.model.datasimulator_timeseries_toolbox import (add_time_argument, time_vec,
                                                             l_time_vec, add_timeref_arguments,
                                                             time_ref, l_time_ref)
from ....core.model.datasim_docfunc import DatasimDocFunc
from .....tools.function_from_text_toolbox import (init_arglist_paramnb_arguments_ldict, add_param_argument,
                                                   par_vec_name, add_argskwargs_argument, argskwargs)


## Logger object
logger = getLogger()


INDpoly_tref_name = f"{time_ref}_RVdrift"


class PolynomialIndicatorInterface(object):
    """docstring for PolynomialIndicatorInterface."""

    # Define name of indicator models
    _polynomial_method_name = "polynomial"

    # Define name of polynomial model parameters
    _polynomial_order_name = "order"

    # Default parameter values
    _default_param_values = {_polynomial_order_name: 0}

    def _init_polynomialind_model(self, inst_model_obj, kwargs_indicator_model):
        """Initialise the polynomial indicator model for a given instrument model

        Create the required parameters in the instrument model object and define the associated attributes

        Arguments
        ---------
        inst_model_obj         : Instrument_Model
            Instance of the Instrument_Model class
        kwargs_indicator_model : dictionary
            Dictionary giving the arguments required by the indicator model
        """
        # Set attribute indicator_model and _polynomial_order_name (content of this variable) in inst_model_obj
        inst_model_obj.indicator_model = self._polynomial_method_name
        ind_cat = inst_model_obj.instrument.indicator_category
        inst_model_obj.params_indicator_models = kwargs_indicator_model[ind_cat]
        # Create the parameters for the polynomial model in inst_model_obj
        for order in range(kwargs_indicator_model[ind_cat][self._polynomial_order_name] + 1):
            inst_model_obj.add_parameter(Parameter(name=self.get_polynom_param_order(order),
                                                   name_prefix=inst_model_obj.name,
                                                   main=True,
                                                   unit="[time]^(-{})".format(order)))

    def get_polynom_param_order(self, order):
        """Return the name of the parameter of the given order for the polynomial model of an instrument model

        Arguments
        ---------
        order :  int
            Order of the polynomial for which you want the name of the parameter

        Returns
        -------
        param_name : str
            Name of the parameter
        """
        return f"C{order}"

    def _create_datasimulator_IND_Poly(self, key_whole, key_param, key_mand_kwargs, key_opt_kwargs,
                                       polynomial_order_name,
                                       inst_models, datasets,
                                       get_times_from_datasets,
                                       l_time_vec_format=None,
                                       param_vector_name=par_vec_name,
                                       ):
        """Create a datasimulator for indicators using the polynomial model

        Arguments
        ---------
        key_whole         : String
            key to use to identify the whole system in the output dictionary (dico_docf).
        key_param         : String
            Key used for the parameters entry of arg_list
        key_mand_kwargs   : String
            Key used for the mandatory keyword argument entry of arg_list
        key_opt_kwargs    : String
            Key used for the optional keyword argument entry of arg_list
        inst_models       : Instrument_Model or List of Inst Instrument_Model or None
            List of instrument model object which if datasets is provided should correspond to the datasets provided.
        datasets          : Dataset/list_of_Dataset/None
            If Dataset, the datasimulator include the kwargs of the dataset, so provided parameters
                of for the model, it simulates the data in the dataset.
            If None, the datasimulator function requires the time (and eventually the t_ref) on top
                of the parameters of the model.
            If list of Dataset, it has to provide exactly one dataset (no None) for each Instrument
                model in inst_models and the produced datasimulator will include the kwargs of the
                datasets.
        get_times_from_datasets  : bool
            If True the times at which the LC model is computed is taken from the datasets.
            Else it is an input of the datasimulator function produced.
        param_vector_name : String
            string giving the name of the vector of parameters argument of the
            datasimulator function.
        l_time_vec_format : str
            format for f_time_vect

        Returns
        -------
        dico_docf : dict_of_DatasimDocFunc
            A dictionary with DocFunctions containing the data
            simulator function for the whole system ("whole") and for the each planet individually
            ("planet_name")
        """
        # Check the content of inst_models argument. Set multi_inst_model to True if several inst models
        # are provided, to False otherwise. Finally set the inst_model_fullnames argument for the
        # Datasim_DocFunc (instmod_docf)
        # Check the content of datasets argument: Set multi_dataset to True if several datasets
        # are provided, to False otherwise. Finally set the datasets argument for the
        # Datasim_DocFunc (dtsts_docf)
        # Set the list of instrument categories for the Datasim_DocFunc (instcat_docf)
        # Produce the list of datasets and list of models (even of 1 element)
        # Set multi indicating if multiple outputs are required for the datasimulator
        # Set the inst_model_full_name for the name of the function and the inst_cat input
        # (instcat_docf) for the datasim_docfunc
        (l_dataset, l_inst_model, multi, inst_model_full_name, instcat_docf, instmod_docf,
         dtsts_docf) = check_datasets_and_instmodels(datasets, inst_models)

        # Check if datasets are provided
        # has_dataset = get_has_datasets(l_dataset)

        # text_def_func is a dictionary which will received the text of the datasimulator functions
        # It has several keys for several datasimulator functions:
        #   - "whole" for the whole system with all the planets
        #   - "b", "c", ... ("planet name") for only the contribution of one planet.
        text_def_func = {}

        ## Initialise param_nb and arg_list
        # param_nb is a dictionary that will keep track of the number of parameter for each
        # function in text_def_func (so the keys are the same).
        # arg_list is a dictionary which will receive the argument list of the datasimulator
        # function in text_def_func (so the keys are the same).
        # The argument list of a function is itself a dictionary (OrderedDict) that get at least two
        # keys:
        #   - "param": list of the free parameters name in order
        #   - "kwargs": list of the additional argument taht you need to provide to simulate the
        #               data. For example the time]
        # Create the "arguments" text variable and intial with the parameter vector
        # Create and intialise the "ldict" dictionary variable which will be used as local dictionary
        # for the creation of the datasim functions with exec
        (param_nb,
         arg_list,
         arguments,
         ldict) = init_arglist_paramnb_arguments_ldict(key_param=key_param, keys=[key_whole], key_mand_kwargs=key_mand_kwargs,
                                                       key_opt_kwargs=key_opt_kwargs, param_vector_name=par_vec_name)
        # Add the time as additional argument: TODO: time_arg_name is a new return and is not used in
        # the rest of the function. Check if it can be used.
        (arguments, time_arg_name, time_arg, time_arg_in_arguments
         ) = add_time_argument(arguments=arguments, multi=multi, get_times_from_datasets=get_times_from_datasets, arg_list=arg_list,
                               key_arglist=key_whole, key_mand_kwargs=key_mand_kwargs, key_opt_kwargs=key_opt_kwargs,
                               ldict=ldict, l_dataset=l_dataset, time_vec_name=time_vec, l_time_vec_name=l_time_vec,
                               add_to_ldict=True, backup_add_to_args=True)

        # Initialise the template function text
        function_name = ("INDpolynomailsim_{{object}}_{instmod_fullname}"
                         "".format(instmod_fullname=inst_model_full_name))
        template_function = """
        def {function_name}({{arguments}}):
        {{tab}}return {{returns}}
        """.format(function_name=function_name)
        tab = "    "
        template_function = dedent(template_function)

        # Get the polynomial variations for each couple instrument - dataset
        # Create the text for oot_var
        l_poly_var = []
        # For each instrument model and dataset, ...
        for ii, instmdl, dst in zip(range(len(l_inst_model)), l_inst_model, l_dataset):
            l_poly_var.append("")
            # ..., For each order in the required polynomial model, ...
            for order in range(instmdl.params_indicator_models[polynomial_order_name] + 1):
                # ..., get the name and full name of the parameter for this order
                coef_param_name = self.get_polynom_param_order(order)
                # ..., If this parameter is a main parameter (it should be), ...
                if instmdl.parameters[coef_param_name].main:
                    value_not0 = True
                    text_coef_param = add_param_argument(param=instmdl.parameters[coef_param_name],
                                                         arg_list=arg_list, key_param=key_param, param_nb=param_nb,
                                                         key_arglist=key_whole, param_vector_name=par_vec_name)[key_whole]
                    # ..., if the parameter is free or the fixed value is not zero, ...
                    if text_coef_param != str(0.0):
                        if order == 0:
                            if multi:
                                if l_time_vec_format is None:
                                    l_poly_var[ii] += f"{text_coef_param} * ones_like({l_time_vec}[{ii}])"
                                else:
                                    l_poly_var[ii] += f"{text_coef_param} * ones_like({l_time_vec_format.format(ii=ii)})"
                            else:
                                l_poly_var[ii] += f"{text_coef_param} * ones_like({time_vec})"
                        else:
                            l_poly_var[ii] += "+ {}".format(text_coef_param)
                    # ..., else, since the fixed value is zero, this order doesn't have any
                    # contribution
                    else:
                        value_not0 = False
                    # ..., if the order has a contribution to the out of transit variation and
                    # the considered order is more than 0 meaning the time plays a role, ...
                    if value_not0 and order > 0:
                        # ..., if neither "tref" nor "l_tref" are in the list of kwargs and
                        # no dataset is provided, ...
                        if INDpoly_tref_name not in arg_list[key_whole][key_mand_kwargs] + arg_list[key_whole][key_opt_kwargs]:
                            (arguments, timeref_arg_name, timeref_arg, timeref_arg_in_arguments
                             ) = add_timeref_arguments(arguments=arguments, multi=multi, vect_for_multi=False,
                                                       use_dataset=False, arg_list=arg_list, key_arglist=key_whole,
                                                       key_mand_kwargs=key_mand_kwargs, key_opt_kwargs=key_opt_kwargs,
                                                       ldict=ldict, has_dataset=has_dataset,
                                                       l_dataset=l_dataset, timeref_name=INDpoly_tref_name,
                                                       time_vec_name=time_vec, l_time_vec_name=l_time_vec)
                            if timeref_arg is None:
                                # The value has been added to ldict and you nned to use timeref_arg_name in the text of the function
                                timeref = timeref_arg_name
                            else:
                                # The value to use in the text is timeref_arg
                                timeref = timeref_arg
                        # ..., add the end of this order's contribution to the text of the out of
                        # transit variation, ...
                        if order == 1:
                            if multi:
                                if l_time_vec_format is None:
                                    l_time_ii = f"{l_time_vec}[{ii}]"
                                else:
                                    l_time_ii = l_time_vec_format.format(ii=ii)
                                l_poly_var[ii] += f" * ({l_time_ii} - {timeref}) "
                            else:
                                l_poly_var[ii] += f" * ({time_vec} - {timeref}) "
                        elif order > 1:
                            if multi:
                                l_time_ii = l_time_vec_format.format(ii=ii)
                                l_poly_var[ii] += f" * ({l_time_ii} - {timeref})**{order}"
                            else:
                                l_poly_var[ii] += f" * ({time_vec} - {timeref})**{order}"
                    # If the is no contribution to the oot of transit variation from this order
                    # add only a space.
                    elif value_not0 and order == 0:
                        l_poly_var[ii] += " "

        returns_whole = ""
        for poly_var in l_poly_var:
            returns_whole += poly_var
            returns_whole += ", "
        if not(multi):  # If multi, the coma in the end ensure that the output is always a tuple (even there is actually just one dataset). This is very important for output of datasim_all_datasets.
            returns_whole = returns_whole[:-2]

        # Finalise the text of simulator
        if argskwargs not in arguments:
            arguments = add_argskwargs_argument(arguments)

        text_def_func[key_whole] = (template_function.
                                    format(object=key_whole,
                                           arguments=arguments, returns=returns_whole,
                                           tab=tab))

        # Create and fill the output dictionnary containing the datasimulators functions.
        dico_docf = dict.fromkeys(text_def_func.keys(), None)
        # Add necessary objects to ldict
        ldict["ones_like"] = ones_like
        for obj_key in dico_docf:
            logger.debug("text of {object} IND polynomial simulator function :\n{text_func}"
                         "".format(object=obj_key, text_func=text_def_func[obj_key]))
            exec(text_def_func[obj_key], ldict)
            params_model = arg_list[obj_key][key_param]
            if len(arg_list[obj_key][key_mand_kwargs]) > 0:
                mand_kwargs = str(arg_list[obj_key][key_mand_kwargs])
            else:
                mand_kwargs = None
            if len(arg_list[obj_key][key_opt_kwargs]) > 0:
                opt_kwargs = str(arg_list[obj_key][key_opt_kwargs])
            else:
                opt_kwargs = None
            logger.debug("Parameters for {object} IND polynomial simulator function :\n{dico_param}"
                         "".format(object=obj_key, dico_param={nb: param for nb, param in enumerate(params_model)}))
            dico_docf[obj_key] = DatasimDocFunc(function=ldict[function_name.format(object=obj_key)],
                                                params_model=params_model,
                                                inst_cat=instcat_docf,
                                                include_dataset_kwarg=has_dataset,
                                                mand_kwargs=mand_kwargs,
                                                opt_kwargs=opt_kwargs,
                                                inst_model_fullname=instmod_docf,
                                                dataset=dtsts_docf)
        return dico_docf
