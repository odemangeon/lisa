#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Datasim creator LC module.

TODO:
- Not clear if the planet (not planet only) function always includes the instruments component, espreciallu for multi instrument functions
- At the moment, when I am producing a datasimulator for multiple datasets but I am producing a batman TransitParams instance
for each dataset even if the datasets are using the same instruments. It looks not necessary and I should probably test that I can use the
same TransitParams instance for multiple TransitModel instances and if yes only create one TransitParams instance per transit model.
(I need to create on TransitParams instance per instrument because of the LD coefficients.)
- Currently I am never using this code to produce datsimulators for multiple instruments without provide the dataset and using the time.
So all the code handling this configuration is untest and probably bugged at this point.
- In the docstring of create_datasimulator_LC for the arguments inst_models, I wrote that it could be
None, now I am not sure that it's actually possible for it to be None. To Check.
- time_arg_name is a new return of add_time_argument and is not used in the rest of the create_datasimulator_LC function.
Check if it can be used.
- I am not sure that some of the comments are still valid. So I need to check if this comment are still valid or not.
Search for TODO_CHECK_THIS_COMMENT which I put in front each one of these comments.
"""
from logging import getLogger
from textwrap import dedent
from copy import deepcopy, copy
from math import acos, degrees, sqrt
from numpy import ones_like, inf
from collections import Iterable

from batman import TransitModel, TransitParams
# from pytransit import MandelAgol  # Temporarily? remove pytransit from the available rv_models
from spiderman import ModelParams

from ...core.model.datasim_docfunc import DatasimDocFunc
from ...core.model.datasimulator_toolbox import check_datasets_and_instmodels, get_has_datasets
from ...core.model.datasimulator_timeseries_toolbox import (add_time_argument, time_vec,
                                                            l_time_vec, add_timeref_arguments,
                                                            time_ref, l_time_ref)
from ....tools.function_from_text_toolbox import (init_arglist_paramnb_arguments_ldict, add_param_argument,
                                                  par_vec_name, add_argskwargs_argument, argskwargs)
from ....posterior.exoplanet.model.convert import getaoverr, getomega_fast, getomega_deg_fast


## Logger object
logger = getLogger()


def create_datasimulator_LC(star, planets, key_whole, key_param, key_mand_kwargs, key_opt_kwargs, ext_plonly,
                            parametrisation, ldmodel4instmodfname, LDs, transit_model, SSE4instmodfname,
                            phasecurve_model,
                            inst_models=None, datasets=None,
                            param_vector_name=par_vec_name):
    """Return datasimulator functions.

    A datasimualtor function is created for the whole dataset_database and for each planet
    individually.

    Arguments
    ---------
    star                    : Star object
        Star instance of the parent star
    planets                 : dict of Planets
        Dictionary of Planet instance providing the planets in the system
        Format: {"planet name": Planet instance}
    key_whole               : str
        key to use to identify the whole system in the output dictionary (dico_docf).
    key_param               : str
        Key used for the parameters entry of arg_list
    key_mand_kwargs         : str
        Key used for the mandatory keyword argument entry of arg_list
    key_opt_kwargs          : str
        Key used for the optional keyword argument entry of arg_list
    ext_plonly              : str
        extension to the planet name used for planet only model (without star, nor instrument)
    parametrisation         : str
        string refering to the parametrisation to use
    ldmodel4instmodfname    : dict of dict of str
        Dictionary giving Limd darkening model to use for each instrument model and for each star
        Format: {"<instrument_model_name>: {"<star_name>": "<LD_model_name>"}
    LDs                     : dict of CoreLD
        Dictionary of subclasses of CoreLD instances providing the different limb-darkening models
        Format: {f"<star_name>_<LD model name>"": CoreLD_subclass instance, }
    transit_model           : dict
        Dictionary describing the transit model to use. The format of this disctionary is:
        {"do": True,  # Should we model the transit
         'instrument_variable': False,  # Whether or not different instruemnt can have different transit model
         'all_instruments': {'model': 'batman'  #String refering to the transit model to use (can be 'pytransit' or 'batman')
                             },
         'instrument_specific': {'<instrument_full_name>': 'all_instruments' # all instrument or dictionary like the 'all_instruments' one
                                 }
         }
    SSE4instmodfname        : dict of dict of str int and float
        Dictionary giving the supersampling factor and the exposure time to use for each instrument model
        Format: {"instrument model name": {'supersamp': int_supersampling_factor, 'exptime': float_exposure_time}}
    phasecurve_model        : dict
        Dictionary describing the phasecurve model to use. The format of this disctionary is:
        {"do": True,  # Should we model the transit
         'instrument_variable': False,  # Whether or not different instruemnt can have different transit model
         'all_instruments': [{'model': "spiderman", #String refering to the transit model to use (can be 'spiderman')
                              "args": {"ModelParams_kwargs": {"brightness_model": "zhang", },
                                       "attributes": {}
                              }
                             ]
         'instrument_specific': {'<instrument_full_name>': 'all_instruments' # all instrument or dictionary like the 'all_instruments' one
                                 }
         }
    inst_models             : Instrument_Model or List of Instrument_Model or None
        List of Instrument_Model instance which, if datasets is provided, should be the instrument models
        to use for each dataset provided in the datasets arguments.
    datasets                : Dataset or list_of_Dataset or None
        List of datasets to be simulated.
        If no dataset is provided (datasets=None), the datasimulator function produced by this function will
        have as arguments the times on top of the parameter vector of the model.
        If at least one dataset is provided (datasets!=None), then the datasimulator function produced
        by this function will include the times, so it will not be an argument.
        If provided the number of datasets needs to match the number of instrument models provided by
        the inst_models arguments
    param_vector_name       : str
        string giving the name of the vector of parameters argument of the datasimulator function.

    Returns
    -------
    dico_docf : dict_of_DatasimDocFunc
        A dictionary with DocFunctions containing the data
        simulator function for the whole system ("whole") and for the each planet individually
        ("planet_name")
    """
    # Get the transit_implementation to use
    do_transit = transit_model['do']

    # Get the phasecurve_implementation to use
    do_phasecurve = phasecurve_model['do']

    ## Check the content of the datasets and inst_models arguments
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
    (l_dataset, l_inst_model, multi, inst_model_full_name, dst_ext, instcat_docf, instmod_docf,
     dtsts_docf) = check_datasets_and_instmodels(datasets, inst_models)

    ## Check if datasets are provided and store the answer in the has_dataset variable
    has_dataset = get_has_datasets(l_dataset)

    ## Initialise text_def_func
    # text_def_func is a dictionary which will received the text of the datasimulator functions
    # It has several keys for several datasimulator functions:
    #   - "whole" for the whole system with all the planets
    #   - "b", "c", ... ("planet name") for only the contribution of one planet.
    # Format: {"System part name": str_text_of_the_datasimulator_for_the_system_part}
    text_def_func = {}

    ## Initialise param_nb, arg_list, arguments and ldict
    # - param_nb is a dictionary that will keep track of the number of parameter for each
    # function in text_def_func (so the keys are the same).
    # Format: {"System part name": int_current_nb_of_model_parameters_of_the_datasimulator}
    # - arg_list is a dictionary which will receive the argument list of the datasimulator
    # function in text_def_func (so the keys are the same).
    # The argument list of a function is itself a dictionary (OrderedDict) that get at least two
    # keys:
    #   - "param": list of the free parameters name in order
    #   - "kwargs": list of the additional argument that you need to provide to simulate the
    #               data. For example the time]
    # Format: {"System part name": {"params": [str_name_of_model_parameter_in_the_parameter_vector, ],
    #                               "kwargs": [str_name_of_additional_argument_for the datasimulator, ]}
    # - arguments is ...
    # Create the "arguments" text variable and intial with the parameter vector
    # - ldict is the dictionary which will be used as local dictionary for the creation/co;plilation
    # of the datasimulator functions with exec
    # Format: {"variable name": variable, }
    (param_nb,
     arg_list,
     arguments,
     ldict) = init_arglist_paramnb_arguments_ldict(key_param=key_param, keys=[key_whole], key_mand_kwargs=key_mand_kwargs,
                                                   key_opt_kwargs=key_opt_kwargs, param_vector_name=par_vec_name)

    ## Initialise arg_list and param_nb keys and values for the planet and the planet only datasimulators
    for planet in planets.values():
        arg_list[planet.get_name() + ext_plonly] = deepcopy(arg_list[key_whole])
        param_nb[planet.get_name() + ext_plonly] = param_nb[key_whole]
        ldict[planet.get_name() + ext_plonly] = copy(ldict[key_whole])
        arg_list[planet.get_name()] = deepcopy(arg_list[key_whole])
        param_nb[planet.get_name()] = param_nb[key_whole]
        ldict[planet.get_name()] = copy(ldict[key_whole])

    ## Get the ld_parcont_name, ld_parcont and ld_param_list variable
    # (This needs to be done before the creation of arglist and param_nb for planet_only !)
    # - l_LD_parcont_name is the List of limb darkening models name (parameter container name) associated with the Instrument_Model instances
    # in l_inst_model.
    # Format: ["<limb darkening model name>", ]
    # - l_LD_parcont is the list of limb darkening models (parameter container object) associated with the Instrument_Model instances
    # in l_inst_model.
    # Format: [<limb darkening model>, ]
    # - l_LD_param_list is the list of string which themself write the list of limb darkening parameters values associated with the Instrument_Model instances
    # in l_inst_model.
    # Format: ["[p[1], p[2]]", ]
    (l_LD_parcont_name,
     l_LD_parcont,
     l_LD_param_list) = get_LD_parcont_and_param(l_inst_model=l_inst_model, ldmodel4instmodfname=ldmodel4instmodfname,
                                                 star=star, LDs=LDs, param_nb=param_nb,
                                                 arg_list=arg_list, key_arglist=None, key_param=key_param)

    ## Define the orbital parameters for each planet
    (rhostar, params_whole, params_planet, params_planet_only
     ) = get_orbital_params(param_nb=param_nb, arg_list=arg_list, star=star, planets=planets, parametrisation=parametrisation,
                            ext_plonly=ext_plonly, key_whole=key_whole, key_param=key_param)

    #####################################
    # Define the template of the function
    #####################################
    # Initialise function_name and template_function the template function name and the template function text
    function_name = ("LCsim_{{object}}_{instmod_fullname}{dst_ext}"
                     "".format(instmod_fullname=inst_model_full_name, dst_ext=dst_ext))
    template_function = """
    def {function_name}({{arguments}}):
    {{tab}}{{preambule_tr}}
    {{tab}}{{preambule_pc}}
    {{tab}}{{condition}}
    {{tab}}try:
    {{tab}}    return {{returns}}
    {{tab}}except RuntimeError:
    {{tab}}    return {{returns_except}}
    """.format(function_name=function_name)
    # Below this was used for debugging purposes
    # template_function = """
    # def {function_name}({{arguments}}):
    # {{tab}}{{preambule}}
    # {{tab}}{{condition}}
    # {{tab}}with open("chain.dat", "a") as file
    # {{tab}}    print(" ".join([str(p_i) for p_i in p]), file=file)
    # {{tab}}return {{returns}}
    # """.format(function_name=function_name)
    tab = "    "
    template_function = dedent(template_function)

    # Create the text of what to return when condition is met or the RuntimeError is catched
    error_return = get_catchederror_return(multi=multi, l_inst_model=l_inst_model)

    # Initialise template_returns_instmod, the template of the return for each instrument model
    template_returns = "(1 {oot_var}) * (1 {tr_planets}{pc_planets})"

    # Initialise template_returns_pl_only, the template for planetary contibution only (No instrument nor star) (used for the phase folded plot to remove the other planet contributions)
    template_returns_plonly = "{tr_planets}{pc_planets}"

    ######################
    # Add Time as argument
    ######################
    # Add the time as additional argument for the functions or include it in ldict
    (arguments, time_arg_name, time_arg, time_arg_in_arguments
     ) = add_time_argument(arguments=arguments, multi=multi, has_dataset=has_dataset, arg_list=arg_list,
                           key_arglist=None, key_mand_kwargs=key_mand_kwargs, key_opt_kwargs=key_opt_kwargs,
                           ldict=ldict, l_dataset=l_dataset, time_vec_name=time_vec, l_time_vec_name=l_time_vec,
                           add_to_ldict=True, backup_add_to_args=True)

    ####################
    # Produce OOT models
    ####################
    ## Get the l_oot_var and add the t_ref(s) to the list of arguments for the functions
    # l_oot_var is the list of strings giving the string representation of the out of transit variation model
    # for each couple instrument model - dataset in l_inst_model and l_dataset.
    # Format: ["oot model", ]
    oot_vars, arguments = get_ootvar(l_inst_model=l_inst_model, l_dataset=l_dataset, multi=multi,
                                     ldict=ldict, arguments=arguments, param_nb=param_nb, arg_list=arg_list,
                                     key_arglist=None, key_param=key_param, key_mand_kwargs=key_mand_kwargs,
                                     key_opt_kwargs=key_opt_kwargs,
                                     time_vec_name=time_vec, l_time_vec_name=l_time_vec,
                                     timeref_name=time_ref, l_timeref_name=l_time_ref)

    ########################
    # Produce Transit models
    ########################
    if do_transit:
        (preambule_tr_planet, preambule_tr_planet_only, preambule_tr_whole,
         l_tr_ret_planet, l_tr_ret_planet_only, l_tr_ret_whole_planets,
         ) = get_transit(multi=multi, l_inst_model=l_inst_model, l_dataset=l_dataset, has_dataset=has_dataset, transit_model=transit_model,
                         l_LD_parcont=l_LD_parcont, l_LD_param_list=l_LD_param_list, parametrisation=parametrisation,
                         key_whole=key_whole, key_param=key_param, SSE4instmodfname=SSE4instmodfname, planets=planets,
                         ext_plonly=ext_plonly, arg_list=arg_list, param_nb=param_nb, ldict=ldict, tab=tab,
                         rhostar=rhostar, params_planet=params_planet, params_planet_only=params_planet_only, params_whole=params_whole)
    else:
        preambule_tr_planet = preambule_tr_planet_only = preambule_tr_whole = {}

    ############################
    # Produce phase curve models
    ############################
    if do_phasecurve:
        (preambule_pc_planet, preambule_pc_planet_only, preambule_pc_whole,
         l_pc_ret_planet, l_pc_ret_planet_only, l_pc_ret_whole_planets,
         ) = get_phasecurve(multi=multi, l_inst_model=l_inst_model, l_dataset=l_dataset, phasecurve_model=phasecurve_model,
                            l_LD_parcont=l_LD_parcont, l_LD_param_list=l_LD_param_list, parametrisation=parametrisation,
                            key_whole=key_whole, key_param=key_param, SSE4instmodfname=SSE4instmodfname, planets=planets, star=star,
                            ext_plonly=ext_plonly, arg_list=arg_list, param_nb=param_nb, ldict=ldict, tab=tab, did_transit=do_transit,
                            rhostar=rhostar, params_planet=params_planet, params_planet_only=params_planet_only, params_whole=params_whole)

    ########################
    # Get the condition text
    ########################
    (condition_planet, condition_planet_only, condition_whole
     ) = get_conditions(planets=planets, parametrisation=parametrisation,
                        params_planet=params_planet, params_planet_only=params_planet_only, params_whole=params_whole,
                        tab=tab, error_return=error_return)

    #############################################
    # Fill the functions template for each planet
    #############################################
    for jj, planet in enumerate(planets.values()):
        # Fill returns text for each planet
        returns_pl = ""
        returns_pl_only = ""
        for (oot_var_planet, oot_var_planet_only, planet_tr, planet_only_tr, planet_pc, planet_only_pc
             ) in zip(oot_vars[planet.get_name()], oot_vars[planet.get_name() + ext_plonly],
                      l_tr_ret_planet[planet.get_name()], l_tr_ret_planet_only[planet.get_name()],
                      l_pc_ret_planet[planet.get_name()], l_pc_ret_planet_only[planet.get_name()]):
            tr_plusornot_pl = "+ " if planet_tr != "" else ""
            pc_plusornot_pl = "+ " if planet_pc != "" else ""
            returns_pl += template_returns.format(oot_var=oot_var_planet,
                                                  tr_planets=tr_plusornot_pl + planet_tr,
                                                  pc_planets=pc_plusornot_pl + planet_pc)
            pc_plusornot_plonly = "+ " if ((planet_only_tr != "") and (planet_only_pc != "")) else ""
            returns_pl_only += template_returns_plonly.format(tr_planets=planet_only_tr, pc_planets=pc_plusornot_plonly + planet_only_pc)
            returns_pl += ", "
            returns_pl_only += ", "
        if not(multi):  # If multi, the coma in the end ensure that the output is always a tuple (even there is actually just one dataset). This is very important for output of datasim_all_datasets.
            returns_pl = returns_pl[:-2]
            returns_pl_only = returns_pl_only[:-2]

        # Finalise the text of planet LC simulator functions
        if argskwargs not in arguments:
            arguments = add_argskwargs_argument(arguments)
        text_def_func[planet.get_name()] = (template_function.format(object=planet.get_name(),
                                                                     preambule_tr=preambule_tr_planet[planet.get_name()],
                                                                     preambule_pc=preambule_pc_planet[planet.get_name()],
                                                                     condition=condition_planet,
                                                                     arguments=arguments, returns=returns_pl,
                                                                     returns_except=error_return,
                                                                     tab=tab))
        text_def_func[planet.get_name() + ext_plonly] = (template_function.format(object=planet.get_name() + ext_plonly,
                                                                                  preambule_tr=preambule_tr_planet_only[planet.get_name()],
                                                                                  preambule_pc=preambule_pc_planet_only[planet.get_name()],
                                                                                  condition=condition_planet_only,
                                                                                  arguments=arguments,
                                                                                  returns=returns_pl_only,
                                                                                  returns_except=error_return,
                                                                                  tab=tab))
        # logger.debug("text of {object} LC simulator function :\n{text_func}"
        #              "".format(object=planet.get_name(), text_func=text_def_func[planet.get_name()]))

    ##################################################
    # Fill the functions template for the whole system
    ##################################################
    returns_whole = ""
    for oot_var, whole_tr_planet, whole_pc_planet in zip(oot_vars[key_whole], l_tr_ret_whole_planets, l_pc_ret_whole_planets):
        tr_plusornot_pl = "+ " if whole_tr_planet != "" else ""
        pc_plusornot_pl = "+ " if whole_pc_planet != "" else ""
        returns_whole += template_returns.format(oot_var=oot_var,
                                                 tr_planets=tr_plusornot_pl + whole_tr_planet, pc_planets=pc_plusornot_pl + whole_pc_planet)
        returns_whole += ", "
    if not(multi):  # If multi, the coma in the end ensure that the output is always a tuple (even there is actually just one dataset). This is very important for output of datasim_all_datasets.
        returns_whole = returns_whole[:-2]

    text_def_func[key_whole] = (template_function.
                                format(object=key_whole, preambule_tr=preambule_tr_whole, preambule_pc=preambule_pc_whole, condition=condition_whole,
                                       arguments=arguments, returns=returns_whole, returns_except=error_return,
                                       tab=tab))

    ###################################
    # Execute the text of all functions
    ###################################
    # Create and fill the output dictionnary containing the datasimulators functions.
    dico_docf = dict.fromkeys(text_def_func.keys(), None)
    for obj_key in dico_docf:
        ldict[obj_key]["ones_like"] = ones_like
        ldict[obj_key]["inf"] = inf
        ldict[obj_key]["sqrt"] = sqrt
        ldict[obj_key]["acos"] = acos
        ldict[obj_key]["degrees"] = degrees
        if parametrisation == "Multis":
            ldict[obj_key]["getaoverr"] = getaoverr
        logger.debug("text of {object} LC simulator function :\n{text_func}"
                     "".format(object=obj_key, text_func=text_def_func[obj_key]))
        exec(text_def_func[obj_key], ldict[obj_key])
        params_model = arg_list[obj_key][key_param]
        if len(arg_list[obj_key][key_mand_kwargs]) > 0:
            mand_kwargs = str(arg_list[obj_key][key_mand_kwargs])
        else:
            mand_kwargs = None
        if len(arg_list[obj_key][key_opt_kwargs]) > 0:
            opt_kwargs = str(arg_list[obj_key][key_opt_kwargs])
        else:
            opt_kwargs = None
        logger.debug("Parameters for {object} LC simulator function :\n{dico_param}"
                     "".format(object=obj_key, dico_param={nb: param for nb, param in enumerate(params_model)}))
        dico_docf[obj_key] = DatasimDocFunc(function=ldict[obj_key][function_name.format(object=obj_key)],
                                            params_model=params_model,
                                            inst_cat=instcat_docf,
                                            include_dataset_kwarg=has_dataset,
                                            mand_kwargs=mand_kwargs,
                                            opt_kwargs=opt_kwargs,
                                            inst_model_fullname=instmod_docf,
                                            dataset=dtsts_docf)
    return dico_docf


def get_ootvar(l_inst_model, l_dataset, multi, ldict, arguments, param_nb, arg_list,
               key_arglist, key_param, key_mand_kwargs, key_opt_kwargs,
               time_vec_name=time_vec, l_time_vec_name=l_time_vec, l_time_vec_format=None,
               timeref_name=time_ref, l_timeref_name=l_time_ref, l_timeref_format=None, use_dataset_4_tref=False,
               time_ref_val=None):
    """Get the out of transit variation contribution to the light-curve

    Arguments
    ---------
    l_inst_model        : list_of_Instrument_Model
        Checked list of Instrument_Model instance(s).
    l_dataset           : list_of_Dataset
        Checked list of Dataset instance(s).
    multi               : bool
        True if the datasim function needs to give multiple outputs.
    ldict       : dict_of_dict
        Dictionary giving the dictionaries to be used as local dictionary argument of the exec functions.
        - key = str key designating part of the system or the whole system
        - value = dictionary
        THIS DICTIONARY IS MODIFIED EVEN IF NOT RETURNED
    arguments           : str
        string giving the current text of arguments for the functions
    param_nb            : dict_of_int
        dictionary giving the current number of free parameters in the function being produced.
        key = str key designating part of the system or the whole system
        value = int giving the current number of parameter in the model
        Format: {"name_of_function": int_current_nb_of_model_parameters_of_the_datasimulator}
        THIS DICTIONARY IS MODIFIED EVEN IF NOT RETURNED
    arg_list            : dict_of_dict_of_list_of_str
        dictionary giving the arguments of the functions currently being produced with the following format:
        - key = str designating the function being built and provided by keys.
        - value = dict with three str keys and values
            - <key_param>: empty list that will receive the full names of the parameters of the function (content of the param_vector)
            - <key_mand_kwargs>: empty list that will receive the mandatory keyword arguments (beside the param_vector)
            - <key_opt_kwargs>: empty list that will receive the optional keyword arguments
        If the parameter of the OOT variation are is free. Their names will be added to the key_param lists of the
        functions specified by key_arglist
        THIS DICTIONARY IS MODIFIED EVEN IF NOT RETURNED
    key_arglist         : str or list_of_str or None
        Name/Ref or list of name/ref of the function being produced for which you want to add the OOT params as
        a parameter. These names are keys of the arg_list and param_nb dictionaries
        If key_arglist is None, all available keys in arglist are assumed.
    key_param           : str
        Key used for the parameters entry of arg_list values
    key_mand_kwargs     : str
        Key used for the mandatory keyword argument entry of arg_list values
    key_opt_kwargs      : str
        Key used for the optional keyword argument entry of arg_list values
    time_vec_name       : str
        Str used to designate the time vector
    l_time_vec_name     : str
        Str used to designate the list of time vectors
    l_time_vec_format   : str
        Str used to access an element of l_time_vec_name
    timeref_name        : str
        Str used to designate the time reference
    l_timeref_name      : str
        Str used to designate the list of time references
    l_timeref_format    : str
        Str used to access an element of l_timeref_name
    use_dataset_4_tref  : bool
        If True, then the dataset will be used to compute the reference time
    time_ref_val        :
        Value of the time reference(s) if not computed from the datasets

    Returns
    -------
    oot_vars    : dict of list_of_string
        Dictionary providing, for all functions specified by key_arglist, the list of the string representations
        of the out of transit variation model for each couple instrument model - dataset in l_inst_model and l_dataset.
        Format of the dictionary:
        - key : key or keys specificied by key_arglist
        - value: List = ["<oot model for instrument1 and dataset1>", ...]
    arguments   : str
        Updated string giving the new text of arguments
    """
    if isinstance(key_arglist, str):
        l_key_arglist = [key_arglist]
    elif key_arglist is None:
        l_key_arglist = list(arg_list.keys())
    elif isinstance(key_arglist, Iterable):
        l_key_arglist = key_arglist
    else:
        raise ValueError("key_arglist should be None or a string or in iterable of string")

    # Check if datasets are provided
    has_dataset = get_has_datasets(l_dataset)
    # Create the oot_vars dictionary
    oot_vars = {}

    for key_arglist in l_key_arglist:
        oot_vars[key_arglist] = []
        # For each instrument model and dataset, ...
        for ii, instmdl, dst in zip(range(len(l_inst_model)), l_inst_model, l_dataset):
            oot_vars[key_arglist].append("")
            # ..., if out of transit variation has been asked, ...
            if instmdl.get_with_OOT_var():
                # ..., For each order in the required polynomial model, ...
                for order in range(instmdl.get_OOT_var_order() + 1):
                    # ..., get the name and full name of the parameter for this order
                    OOT_param_name = instmdl.get_OOT_param_name(order)
                    # ..., If this parameter is a main parameter (it should be), ...
                    if instmdl.parameters[OOT_param_name].main:
                        value_not0 = True
                        text_OOT_param = add_param_argument(param=instmdl.parameters[OOT_param_name],
                                                            arg_list=arg_list, key_param=key_param, param_nb=param_nb,
                                                            key_arglist=key_arglist, param_vector_name=par_vec_name)[key_arglist]
                        # ..., if the parameter is free or the fixed value is not zero, ...
                        if text_OOT_param != str(0.0):
                            oot_vars[key_arglist][ii] += "+ {}".format(text_OOT_param)
                        # ..., else, since the fixed value is zero, this order doesn't have any
                        # contribution
                        else:
                            value_not0 = False
                        # ..., if the order has a contribution to the out of transit variation and
                        # the considered order is more than 0 meaning the time plays a role, ...
                        if value_not0 and order > 0:
                            # ..., if neither "tref" nor "l_tref" are in the list of kwargs and
                            # no dataset is provided, ...
                            if ((timeref_name not in arg_list[key_arglist][key_mand_kwargs] +
                                 arg_list[key_arglist][key_opt_kwargs]) and
                                (l_timeref_name not in arg_list[key_arglist][key_mand_kwargs] +
                                 arg_list[key_arglist][key_opt_kwargs])):
                                def get_time_ref(time):
                                    return time[0]
                                (arguments, timeref_arg_name, timeref_arg
                                 ) = add_timeref_arguments(arguments=arguments, multi=multi, vect_for_multi=True,
                                                           use_dataset=use_dataset_4_tref,
                                                           arg_list=arg_list, key_arglist=key_arglist,
                                                           key_mand_kwargs=key_mand_kwargs, key_opt_kwargs=key_opt_kwargs,
                                                           ldict=ldict, has_dataset=has_dataset, get_time_ref=get_time_ref,
                                                           time_ref_val=time_ref_val, l_dataset=l_dataset,
                                                           timeref_name=timeref_name, l_timeref_name=l_timeref_name,
                                                           time_vec_name=time_vec_name, l_time_vec_name=l_time_vec_name)
                            # ..., add the end of this order's contribution to the text of the out of
                            # transit variation, ...
                            if order == 1:
                                if multi:
                                    if l_time_vec_format is None:
                                        l_time_ii = ("{ltimevec}[{ii}]"
                                                     "".format(ltimevec=l_time_vec_name, ii=ii))
                                    else:
                                        l_time_ii = l_time_vec_format.format(ii=ii)
                                    if l_timeref_format is None:
                                        l_timeref_ii = ("{ltimeref}[{ii}]"
                                                        "".format(ltimeref=l_timeref_name, ii=ii))
                                    else:
                                        l_timeref_ii = l_timeref_format.format(ii=ii)
                                    oot_vars[key_arglist][ii] += (" * ({l_time_ii} - {l_timeref_ii}) "
                                                                  "".format(ii=ii, l_time_ii=l_time_ii,
                                                                            l_timeref_ii=l_timeref_ii))
                                else:
                                    oot_vars[key_arglist][ii] += (" * ({time} - {timeref}) "
                                                                  "".format(time=time_vec_name,
                                                                            timeref=timeref_name))
                            elif order > 1:
                                if multi:
                                    l_time_ii = l_time_vec_format.format(ii=ii)
                                    l_timeref_ii = l_timeref_format.format(ii=ii)
                                    oot_vars[key_arglist][ii] += (" * ({l_time_ii} - {l_timeref_ii})"
                                                                  "**{order}".format(order=order, ii=ii,
                                                                                     l_time_ii=l_time_ii,
                                                                                     l_timeref_ii=l_timeref_ii))
                                else:
                                    oot_vars[key_arglist][ii] += (" * ({time} - {timeref})**{order}"
                                                                  "".format(order=order, time=time_vec_name,
                                                                            timeref=timeref_name))
                        # If the is no contribution to the oot of transit variation from this order
                        # add only a space.
                        elif value_not0 and order == 0:
                            oot_vars[key_arglist][ii] += " "
    return oot_vars, arguments


def get_LD_parcont_and_param(l_inst_model, ldmodel4instmodfname, star, LDs, param_nb, arg_list, key_arglist,
                             key_param):
    """Return the list of LD param container name, instance and parameter string list for a given star.

    Arguments
    ---------
    l_inst_model            : list_of_Instrument_Model
        Checked list of Instrument_Model instance(s).
    ldmodel4instmodfname    : dict of dict of str
        Dictionary giving Limd darkening model to use for each instrument model and for each star
        Format: {"<instrument_model_name>: {"<star_name>": "<LD_model_name>"}
    star                    : Star
        Star object
    LDs                     : dict of CoreLD
        Dictionary of subclasses of CoreLD instances providing the different limb-darkening models
        Format: {f"<star_name>_<LD model name>"": CoreLD_subclass instance, }
    param_nb                : dict_of_int
        dictionary giving the current number of free parameters in the function being produced.
        key = str key designating part of the system or the whole system
        value = int giving the current number of parameter in the model
        Format: {"name_of_function": int_current_nb_of_model_parameters_of_the_datasimulator}
        THIS DICTIONARY IS MODIFIED EVEN IF NOT RETURNED
    arg_list                : dict_of_dict_of_list_of_str
        dictionary giving the arguments of the functions currently being produced with the following format:
        - key = str designating the function being built and provided by keys.
        - value = dict with three str keys and values
            - <key_param>: empty list that will receive the full names of the parameters of the function (content of the param_vector)
            - <key_mand_kwargs>: empty list that will receive the mandatory keyword arguments (beside the param_vector)
            - <key_opt_kwargs>: empty list that will receive the optional keyword arguments
        If the LD parameters are is free. Their names will be added to the key_param lists of the
        functions specified by key_arglist
        THIS DICTIONARY IS MODIFIED EVEN IF NOT RETURNED
    key_arglist             : str or list_of_str or None
        Name/Ref or list of name/ref of the function being produced for which you want to add the LD params
        a parameter. These names are keys of the arg_list and param_nb dictionaries
        If key_arglist is None, all available keys in arglist are assumed.
    key_param               : str
        Key used for the parameters entry of arg_list values

    Returns
    -------
    dico_LD_parcont_name   : dict_of_list_of_string
        Dictionary providing, for all functions specified by key_arglist, the list of limb darkening models
        name (parameter container name) associated with the Instrument_Model instances in l_inst_model.
        Format of the dictionary:
        - key : key or keys specificied by key_arglist
        - value: List = ["<LD parameter container name for instrument1>", ...]
    dico_LD_parcont        : dict_of_list_of_LD
        Dictionary providing, for all functions specified by key_arglist, the list of limb darkening models
        (parameter container object) associated with the Instrument_Model instances in l_inst_model.
        Format of the dictionary:
        - key : key or keys specificied by key_arglist
        - value: List = [<LD parameter container for instrument1>, ...]
    dico_LD_param_list     : dict_of_list_of_str
        Dictionary providing, for all functions specified by key_arglist, the list of string which themself
        write the list of limb darkening parameters values associated with the Instrument_Model instances
        in l_inst_model.
        Format of the dictionary:
        - key : key or keys specificied by key_arglist
        - value: List = ["[<value for LD param1 for instrument1> , <value for LD param2 for instrument1>, ...]", ...]
    """
    if isinstance(key_arglist, str):
        l_key_arglist = [key_arglist]
    elif key_arglist is None:
        l_key_arglist = list(arg_list.keys())
    elif isinstance(key_arglist, Iterable):
        l_key_arglist = key_arglist
    else:
        raise ValueError("key_arglist should be None or a string or in iterable of string")

    # Get the ld_parcont and ld_param_list
    l_LD_parcont_name = {}
    l_LD_parcont = {}
    l_LD_param_list = {}

    for key_arglist in l_key_arglist:
        l_LD_parcont_name[key_arglist] = []
        l_LD_parcont[key_arglist] = []
        l_LD_param_list[key_arglist] = []
        for ii, instmdl in enumerate(l_inst_model):
            l_LD_parcont_name[key_arglist].append(ldmodel4instmodfname[instmdl.get_name(include_prefix=True, code_version=True, recursive=True)][star.code_name])
            l_LD_parcont[key_arglist].append(LDs[star.code_name + "_" + l_LD_parcont_name[key_arglist][ii]])
            l_LD_param_list[key_arglist].append("[")
            for param in l_LD_parcont[key_arglist][ii].get_list_params(main=True):
                l_LD_param_list[key_arglist][ii] += (add_param_argument(param=param, arg_list=arg_list, key_param=key_param,
                                                                        param_nb=param_nb, key_arglist=key_arglist, param_vector_name=par_vec_name)[key_arglist] +
                                                     ", ")
            l_LD_param_list[key_arglist][ii] += "]"
    return l_LD_parcont_name, l_LD_parcont, l_LD_param_list


def get_orbital_params(param_nb, arg_list, star, planets, parametrisation, ext_plonly, key_param, key_whole):
    """Return the orbital parameters instance and parameter string list for all planets

    Arguments
    ---------
    param_nb        : dict_of_int
        dictionary giving the current number of free parameters in the function being produced.
        key = str key designating part of the system or the whole system
        value = int giving the current number of parameter in the model
        Format: {"name_of_function": int_current_nb_of_model_parameters_of_the_datasimulator}
        THIS DICTIONARY IS MODIFIED EVEN IF NOT RETURNED
    arg_list        : dict_of_dict_of_list_of_str
        dictionary giving the arguments of the functions currently being produced with the following format:
        - key = str designating the function being built and provided by key_arglist.
        - value = dict with three str keys and values
            - <key_param>: empty list that will receive the full names of the parameters of the function (content of the param_vector)
            - <key_mand_kwargs>: empty list that will receive the mandatory keyword arguments (beside the param_vector)
            - <key_opt_kwargs>: empty list that will receive the optional keyword arguments
        If it's not added to ldict instead the arguments provided by arguments are going to be added to the key_mand_kwargs or key_opt_kwargs
        of sub-dictionaries specified by key_arglist.
        THIS DICTIONARY IS MODIFIED EVEN IF NOT RETURNED
    star            : Star
        Star object
    planets         : planets                 : dict of Planets
        Dictionary of Planet instance providing the planets in the system
        Format: {"planet name": Planet instance}
    parametrisation : parametrisation         : str
        string refering to the parametrisation to use
    ext_plonly      : str
        extension to the planet name used for planet only model (without star, nor instrument)
    key_param       : str
        Key used for the parameters entry of arg_list values
    key_whole       : str
        Key used in arg_list for the function simulating the whole system (all planets together)

    Returns
    -------
    rhostar             : dict_of_str
        Dictionary providing the str to use in the function for rhostar for all function available in arg_list
        Format:
        - key: str designating the function being built and provided by key_arglist.
        - value: str to use for rhostar for this function
    params_whole        : dict_of_dict_of_str
        Dictionary providing the strs to use for the other orbital parameters and for the key_whole function ("whole system with all the planets")
        Format:
        - key: planet name
        - value: dict_of_str with the following format
            - key: Parameter full name
            - value: str to use for this parameter for this function
    params_planet       : dict_of_dict_of_str
        Dictionary providing the strs to use for the other orbital parameters and for the planet function (1planet+star+instrument)
        Format:
        - key: planet name
        - value: dict_of_str with the following format
            - key: Parameter full name
            - value: str to use for this parameter for this function
    params_planet_only  : dict_of_dict_of_str
        Dictionary providing the strs to use for the other orbital parameters and for the planet only function (1planet and nothing else)
        Format:
        - key: planet name
        - value: dict_of_str with the following format
            - key: Parameter full name
            - value: str to use for this parameter for this function
    """
    params_whole = {}
    params_planet = {}
    params_planet_only = {}
    for planet in planets.values():
        params_whole[planet.get_name()] = {}
        params_planet[planet.get_name()] = {}
        params_planet_only[planet.get_name()] = {}
    # Add the stellar density the model parameter vectors (in arg_list) if required by the parametrisation
    # (This needs to be done before the creation of arglist and param_nb for planet_only !)
    # rhostar is the reference to the value of rho star (if rho star is a free parameter it's "p[ii]"
    # the reference to rho star within the parameter vector of the function simulating the whole system.
    # Otherwise it's the fixed value of rho star)
    if parametrisation == "Multis":
        rhostar = add_param_argument(param=star.rho, arg_list=arg_list, key_param=key_param, param_nb=param_nb,
                                     key_arglist=None, param_vector_name=par_vec_name)
    else:
        rhostar = {}
        for key_arglist in arg_list.keys():
            rhostar[key_arglist] = None

    # Create the text for each planet parameter for the current planet model (planet and planet_only) and for the whole system.
    l_param = [planet.ecosw, planet.esinw, planet.cosinc, planet.tic, planet.P]

    if parametrisation != "Multis":
        l_param.append(planet.aR)

    for planet in planets.values():
        for param in l_param:
            param_text = add_param_argument(param=param, arg_list=arg_list, key_param=key_param, param_nb=param_nb,
                                            key_arglist=[key_whole, planet.get_name(), planet.get_name() + ext_plonly],
                                            param_vector_name=par_vec_name)
            params_whole[planet.get_name()][param.get_name()] = param_text[key_whole]
            params_planet[planet.get_name()][param.get_name()] = param_text[planet.get_name()]
            params_planet_only[planet.get_name()][param.get_name()] = param_text[planet.get_name() + ext_plonly]
        if parametrisation == "Multis":
            params_whole[planet.get_name()]["aR"] = None
            params_planet[planet.get_name()]["aR"] = None
            params_planet_only[planet.get_name()]["aR"] = None
    return rhostar, params_whole, params_planet, params_planet_only


def get_conditions(planets, parametrisation, params_planet, params_planet_only, params_whole,
                   tab, error_return):
    """
    Return the text related to the condition to test if the planet goes into the star

    Arguments
    ---------
    planets             :
    parametrisation     :
    params_planet       :
    params_planet_only  :
    params_whole        :
    tab                 :
    error_return        :

    Returns
    -------
    condition_planet        : dictionary of str
        Dictionary containing the text for the condition to put in the function text for the function
        of each planet (planet+star+inst). The format of the dictionary is:
        - key: planet name
        - value: text of the condition
    condition_planet_only   : dictionary of str
        Dictionary containing the text for the condition to put in the function text for the function
        of each planet only. The format of the dictionary is:
        - key: planet name
        - value: text of the condition
    condition_whole         : str
        text to put in the function text for the function of the whole system (inst+star+all planets)
    """
    ################################################################
    # Produce template condition code which return a LC full of infs
    ################################################################
    # Initialise template_condition, the template for the condition (no planet should pass into the star)
    template_condition = """
    {tab}{preambule}
    {tab}if {condition}:
    {tab}    return {returns}
    """
    template_condition = dedent(template_condition)

    # Create the templates to conpute the condition to know if the planet passes in the star
    # and of what tho return if condition is True
    # Fill return if condition planet goes in the star is True
    # The condition is taken from https://iopscience.iop.org/article/10.1086/592381/fulltext/75178.text.html (section 3.1)
    if parametrisation == "Multis":  # aR is not a main parameter
        template_preambule_cond_pl_wRrat = "condition_{planet} = (aR_{planet} < ((1.5 / (1 - ecc_{planet})) + {Rrat}))\n"
        template_preambule_cond_pl_woRrat = "condition_{planet} = (aR_{planet} < (1.5 / (1 - ecc_{planet})))\n"
    else:  # aR is a main parameter
        template_preambule_cond_pl_wRrat = "condition_{planet} = ({aR} < ((1.5 / (1 - ecc_{planet})) + {Rrat}))\n"
        template_preambule_cond_pl_woRrat = "condition_{planet} = ({aR} < (1.5 / (1 - ecc_{planet})))\n"

    preambule_cond_whole = "condition = False\n"
    for ii, planet in enumerate(planets.values()):
        # Fill the template_preambule_condition
        if "Rrat" in params_planet[planet.get_name()]:
            preambule_cond_planet = template_preambule_cond_pl_wRrat.format(planet=planet.get_name(), aR=params_planet[planet.get_name()]["aR"],
                                                                            Rrat=params_planet[planet.get_name()]["Rrat"])
            preambule_cond_planet_only = template_preambule_cond_pl_wRrat.format(planet=planet.get_name(), aR=params_planet_only[planet.get_name()]["aR"],
                                                                                 Rrat=params_planet[planet.get_name()]["Rrat"])
            preambule_cond_whole += tab + template_preambule_cond_pl_wRrat.format(planet=planet.get_name(), aR=params_whole[planet.get_name()]["aR"],
                                                                                  Rrat=params_whole[planet.get_name()]["Rrat"])
        else:
            preambule_cond_planet = template_preambule_cond_pl_woRrat.format(planet=planet.get_name(), aR=params_planet[planet.get_name()]["aR"])
            preambule_cond_planet_only = template_preambule_cond_pl_woRrat.format(planet=planet.get_name(), aR=params_planet_only[planet.get_name()]["aR"])
            preambule_cond_whole += tab + template_preambule_cond_pl_woRrat.format(planet=planet.get_name(), aR=params_whole[planet.get_name()]["aR"])
        condition_planet_only = condition_planet = "condition_{planet}".format(planet=planet.get_name())
        preambule_cond_whole += "{tab}condition = condition or condition_{planet}\n".format(planet=planet.get_name(), tab=tab)

    # Fill condition text for each planet
    # template_condition = """"
    # {tab}{preambule}
    # {tab}if {condition}:
    # {tab}    return {returns}
    # """
    condition_planet = template_condition.format(preambule=preambule_cond_planet, condition=condition_planet, returns=error_return, tab=tab)
    condition_planet_only = template_condition.format(preambule=preambule_cond_planet_only, condition=condition_planet_only, returns=error_return, tab=tab)

    # Finalise the text of whole system LC simulator function
    condition_whole = template_condition.format(preambule=preambule_cond_whole, condition="condition", returns=error_return, tab=tab)

    return condition_planet, condition_planet_only, condition_whole


def get_catchederror_return(multi, l_inst_model):
    """Provide the text of what to return when an error is catched.

    Arguments
    ---------
    multi           : bool
    l_inst_model    : list_of_Instrument_Model

    Returns
    -------
    error_return : str
        Text oif what to return if an error is catched
    """
    if multi:
        template_returns_condition = "ones_like({ltime_vec}) * (- inf)"  # "ones_like({ltime_vec}[{ii}]) * (- inf)"
    else:
        template_returns_condition = "ones_like({time_vec}) * (- inf)"

    l_returns = []
    for ii in range(len(l_inst_model)):
        l_returns.append(template_returns_condition.format(ltime_vec=l_time_vec, time_vec=time_vec))

    error_return = ""
    for ret in l_returns:
        error_return += ret
        error_return += ", "
    if not(multi):
        error_return = error_return[:-2]

    return error_return


def get_transit(multi, l_inst_model, l_dataset, has_dataset, transit_model, l_LD_parcont, l_LD_param_list, parametrisation,
                key_whole, key_param, SSE4instmodfname, planets, ext_plonly, arg_list, param_nb, ldict,
                tab,
                rhostar, params_planet, params_planet_only, params_whole):
    """Provide the text for the transit part of the LC model text (preambule and return).

    Arguments
    ---------

    Returns
    -------
    preambule_tr_planet
    preambule_tr_planet_only
    preambule_tr_whole
    l_tr_planet
    l_tr_planet_only
    l_tr_whole_planets
    """
    transit_imp = transit_model['all_instruments']['model']

    ###################################################################################
    # Produce template for transit model preambule code and define/initialise variables
    ###################################################################################
    # Initialise template_preambule_pl, the template of the preambule of the function for each planet
    template_tr_preambule_pl = """
        {tab}ecc_{planet} = sqrt({ecosw} * {ecosw} + {esinw} * {esinw})"""

    if transit_imp == "batman":
        template_tr_preambule_pl += """
        {tab}omega_{planet} = getomega_deg_fast({ecosw}, {esinw})
        {tab}inc_{planet} = degrees(acos({cosinc}))"""
        if parametrisation == "Multis":
            template_tr_preambule_pl += """
        {tab}aR_{planet} = getaoverr({P}, {rhostar}, ecc_{planet}, omega_{planet})"""

        for instmdl, dst, LD_parcont, ld_param_list in zip(l_inst_model, l_dataset, l_LD_parcont[key_whole],
                                                           l_LD_param_list[key_whole]):  # In principle the LD params are the same for all function because they are made at the beginning and affect all functions
            # TODO_CHECK_THIS_COMMENT: If the same model is used for several dataset a model will be several times in
            # l_inst_model. So to avoid the repetition we check if this instrument has already been
            # done.
            if multi:
                template_batman_pl = """
        {{tab}}params_{{planet}}_{instmod_fullname}_dataset{dst_key}.t0 = {{tic}}
        {{tab}}params_{{planet}}_{instmod_fullname}_dataset{dst_key}.per = {{P}}
        {{tab}}params_{{planet}}_{instmod_fullname}_dataset{dst_key}.rp = {{Rrat}}
        {{tab}}params_{{planet}}_{instmod_fullname}_dataset{dst_key}.inc = inc_{{planet}}
        {{tab}}params_{{planet}}_{instmod_fullname}_dataset{dst_key}.ecc = ecc_{{planet}}
        {{tab}}params_{{planet}}_{instmod_fullname}_dataset{dst_key}.w = omega_{{planet}}
        {{tab}}params_{{planet}}_{instmod_fullname}_dataset{dst_key}.u = {ld_param_list}
        {{tab}}params_{{planet}}_{instmod_fullname}_dataset{dst_key}.limb_dark = '{ld_mod_name}'"""
                template_batman_pl = (template_batman_pl.
                                      format(instmod_fullname=instmdl.get_name(include_prefix=True, code_version=True, recursive=True),
                                             dst_key=dst.number,
                                             ld_mod_name=LD_parcont.ld_type,
                                             ld_param_list=ld_param_list))
            else:
                template_batman_pl = """
        {{tab}}params_{{planet}}.t0 = {{tic}}
        {{tab}}params_{{planet}}.per = {{P}}
        {{tab}}params_{{planet}}.rp = {{Rrat}}
        {{tab}}params_{{planet}}.inc = inc_{{planet}}
        {{tab}}params_{{planet}}.ecc = ecc_{{planet}}
        {{tab}}params_{{planet}}.w = omega_{{planet}}
        {{tab}}params_{{planet}}.u = {ld_param_list}
        {{tab}}params_{{planet}}.limb_dark = '{ld_mod_name}'"""
                template_batman_pl = template_batman_pl.format(ld_mod_name=LD_parcont.ld_type,
                                                               ld_param_list=ld_param_list)
            template_tr_preambule_pl += template_batman_pl

            if parametrisation == "Multis":
                if multi:
                    template_tr_preambule_pl += """
        {{tab}}params_{{planet}}_{instmod_fullname}_dataset{dst_key}.a = aR_{{planet}}
        """.format(instmod_fullname=instmdl.get_name(include_prefix=True, code_version=True, recursive=True), dst_key=dst.number)
                else:
                    template_tr_preambule_pl += """
        {tab}params_{planet}.a = aR_{planet}
        """
            else:
                if multi:
                    template_tr_preambule_pl += """
        {{tab}}params_{{planet}}_{instmod_fullname}_dataset{dst_key}.a = {{aR}}
        """.format(instmod_fullname=instmdl.get_name(include_prefix=True, code_version=True, recursive=True), dst_key=dst.number)
                else:
                    template_tr_preambule_pl += """
        {tab}params_{planet}.a = {aR}
        """
    else:  # pytransit
        template_tr_preambule_pl += """
        {tab}omega_{planet} = getomega_fast({esinw}, {ecosw})
        {tab}inc_{planet} = acos({cosinc})
        """
        if parametrisation == "Multis":
            template_tr_preambule_pl += """
        {tab}aR_{planet} = getaoverr({P}, {rhostar}, ecc_{planet}, degrees(omega_{planet}))"""
    template_tr_preambule_pl = dedent(template_tr_preambule_pl)

    ## Add or not the initialisation of the TransitModel instance or MandelAgol instance (to the template_preambule)
    l_par_bat = []
    for ii, instmdl, dst, LD_parcont in zip(range(len(l_inst_model)), l_inst_model, l_dataset,
                                            l_LD_parcont[key_whole]):  # In principle the LD params are the same for all function because they are made at the beginning and affect all functions
        supersamp = SSE4instmodfname.get_supersamp(instmdl.get_name(include_prefix=True, code_version=True, recursive=True))
        # If you need to supersample the model
        if supersamp > 1:
            exptime = SSE4instmodfname.get_exptime(instmdl.get_name(include_prefix=True, code_version=True, recursive=True))
            if transit_imp == "batman":
                if dst is None:
                    if multi:
                        ## WARNING this section of the code is untested and would not work if it was because params_{{planet}}_{instmod_fullname} is not declared
                        template_batman_pl_4 = ("{{tab}}m_{{planet}}_{instmod_fullname}_"
                                                "dataset{dst_key} = TransitModel("
                                                "params_{{planet}}_{instmod_fullname}, "
                                                "{{ltime_vec}}[{ii}], "
                                                "supersample_factor={supersamp},"
                                                "exp_time={exptime})"
                                                "\n".format(supersamp=supersamp,
                                                            exptime=exptime,
                                                            ii=ii,
                                                            instmod_fullname=instmdl.get_name(include_prefix=True, code_version=True, recursive=True),
                                                            dst_key=dst.number))
                    else:
                        template_batman_pl_4 = ("{{tab}}m_{{planet}} = TransitModel("
                                                "params_{{planet}}, {{time_vec}}, "
                                                "supersample_factor={supersamp},"
                                                "exp_time={exptime})"
                                                "\n".format(supersamp=supersamp,
                                                            exptime=exptime))
                    template_tr_preambule_pl += template_batman_pl_4
                    l_par_bat.append({})
                    for planet in planets.values():
                        for key in [planet.get_name(), planet.get_name() + ext_plonly, key_whole]:
                            l_par_bat[ii][key] = TransitParams()
                else:
                    l_par_bat.append({})
                    for planet in planets.values():
                        for key in [planet.get_name(), planet.get_name() + ext_plonly, key_whole]:
                            l_par_bat[ii][key] = TransitParams()
                            if multi:  # time of inf. conjunction
                                l_par_bat[ii][key].t0 = ldict[planet.get_name()][l_time_vec][ii].mean()
                            else:
                                l_par_bat[ii][key].t0 = ldict[planet.get_name()][time_vec].mean()
                            l_par_bat[ii][key].per = 1.   # orbital period
                            l_par_bat[ii][key].rp = 0.1   # planet radius(in stel radii)
                            l_par_bat[ii][key].a = 15.    # semi-major axis(in stel radii)
                            l_par_bat[ii][key].inc = 90.  # orbital inclination (in degrees)
                            l_par_bat[ii][key].ecc = 0.   # eccentricity
                            l_par_bat[ii][key].w = 90.    # long. of periastron (in deg.)
                            l_par_bat[ii][key].limb_dark = LD_parcont.ld_type  # LD model
                            l_par_bat[ii][key].u = LD_parcont.init_LD_values  # LDC init val
            else:
                m_pytransit = MandelAgol(supersampling=supersamp, exptime=exptime,
                                         model=LD_parcont.ld_type)
        # If you DON'T need to supersample the model
        else:
            if transit_imp == "batman":
                if dst is None:
                    if multi:
                        ## WARNING this section of the code is untested and would not work if it was because params_{{planet}}_{instmod_fullname} is not declared
                        template_batman_pl_5 = ("{{tab}}m_{{planet}} = TransitModel("
                                                "params_{{planet}}}_{instmod_fullname}, {{ltime_vec}}[{ii}])"
                                                "\n".format(ii=ii))
                        template_tr_preambule_pl += template_batman_pl_5
                    else:
                        template_tr_preambule_pl += ("{tab}m_{planet} = TransitModel("
                                                     "params_{planet}, {time_vec})\n")
                    l_par_bat.append({})
                    for planet in planets.values():
                        for key in [planet.get_name(), planet.get_name() + ext_plonly, key_whole]:
                            l_par_bat[ii][key] = TransitParams()
                else:
                    l_par_bat.append({})
                    for planet in planets.values():
                        for key in [planet.get_name(), planet.get_name() + ext_plonly, key_whole]:
                            l_par_bat[ii][key] = TransitParams()
                            if multi:  # time of inf. conjunction
                                l_par_bat[ii][key].t0 = ldict[planet.get_name()][l_time_vec][ii].mean()
                            else:
                                l_par_bat[ii][key].t0 = ldict[planet.get_name()][time_vec].mean()
                            l_par_bat[ii][key].per = 1.   # orbital period
                            l_par_bat[ii][key].rp = 0.1   # planet radius(in stel radii)
                            l_par_bat[ii][key].a = 15.    # semi-major axis(in stel radii)
                            l_par_bat[ii][key].inc = 90.  # orbital inclination (in degrees)
                            l_par_bat[ii][key].ecc = 0.   # eccentricity
                            l_par_bat[ii][key].w = 90.    # long. of periastron (in deg.)
                            l_par_bat[ii][key].limb_dark = LD_parcont.ld_type  # LD model
                            l_par_bat[ii][key].u = LD_parcont.init_LD_values  # LDC init val
            else:
                m_pytransit = MandelAgol(model=LD_parcont.ld_type)

    ###############################################################
    # Produce template code for the transit component of the return
    ###############################################################
    # Create the text for template_tr_planet
    if transit_imp == "batman":
        if multi:
            template_tr_planet = ("m_{planet}_{instmod_fullname}_dataset{dst_key}.light_curve("
                                  "params_{planet}_{instmod_fullname}_dataset{dst_key}) - 1 ")
        else:
            template_tr_planet = ("m_{planet}.light_curve(params_{planet}) - 1 ")
    else:
        if parametrisation == "Multis":
            if multi:
                template_tr_planet = ("m.evaluate({ltime_vec}[{ii}], {Rrat}, {ld_param_list}, "
                                      "{tic}, {P}, aR_{planet}, inc_{planet}, "
                                      "ecc_{planet}, omega_{planet}) - 1 ")
            else:
                template_tr_planet = ("m.evaluate({time_vec}, {Rrat}, {ld_param_list}, {tic}, {P},"
                                      " aR_{planet}, inc_{planet}, ecc_{planet}, "
                                      "omega_{planet}) - 1 ")
        else:
            if multi:
                template_tr_planet = ("m.evaluate({ltime_vec}[{ii}], {Rrat}, {ld_param_list}, "
                                      "{tic}, {P}, {aR}, inc_{planet}, "
                                      "ecc_{planet}, omega_{planet}) - 1 ")
            else:
                template_tr_planet = ("m.evaluate({time_vec}, {Rrat}, {ld_param_list}, {tic}, "
                                      "{P}, {aR}, inc_{planet}, ecc_{planet}, "
                                      "omega_{planet}) - 1 ")

    # Initialise the text for the whole system preambule
    l_tr_whole_planets = []
    for instmdl in l_inst_model:
        l_tr_whole_planets.append("")
    preambule_tr_planet = {}
    preambule_tr_planet_only = {}
    l_tr_planet = {}
    l_tr_planet_only = {}
    preambule_tr_whole = ""
    for jj, planet in enumerate(planets.values()):
        # Only for Batman: Add the TransitParams and TransitModel instances to ldict
        if transit_imp == "batman":
            for ii, instmdl, dst, par_bat in zip(range(len(l_inst_model)), l_inst_model,
                                                 l_dataset, l_par_bat):
                if dst is not None:
                    if multi:
                        params_pl_inst = ("params_{planet}_{instmod_fullname}_dataset{dst_key}"
                                          "".format(planet=planet.get_name(),
                                                    instmod_fullname=instmdl.get_name(include_prefix=True, code_version=True, recursive=True),
                                                    dst_key=dst.number))
                        tt = ldict[planet.get_name()][l_time_vec][ii]
                    else:
                        params_pl_inst = "params_{planet}".format(planet=planet.get_name())
                        tt = ldict[planet.get_name()][time_vec]
                    ldict[planet.get_name()][params_pl_inst] = par_bat[planet.get_name()]
                    ldict[planet.get_name() + ext_plonly][params_pl_inst] = par_bat[planet.get_name() + ext_plonly]
                    ldict[key_whole][params_pl_inst] = par_bat[key_whole]
                    supersamp = SSE4instmodfname.get_supersamp(instmdl.get_name(include_prefix=True, code_version=True, recursive=True))
                    m_batman = {}
                    if supersamp > 1:
                        exptime = SSE4instmodfname.get_exptime(instmdl.get_name(include_prefix=True, code_version=True, recursive=True))
                        m_batman[planet.get_name()] = TransitModel(ldict[planet.get_name()][params_pl_inst],
                                                                   tt, supersample_factor=supersamp,
                                                                   exp_time=exptime)
                        m_batman[planet.get_name() + ext_plonly] = TransitModel(ldict[planet.get_name() + ext_plonly][params_pl_inst],
                                                                                tt, supersample_factor=supersamp,
                                                                                exp_time=exptime)
                        m_batman[key_whole] = TransitModel(ldict[key_whole][params_pl_inst],
                                                           tt, supersample_factor=supersamp,
                                                           exp_time=exptime)  # This should not be done here it will be repeated
                    else:
                        m_batman[planet.get_name()] = TransitModel(ldict[planet.get_name()][params_pl_inst], tt)
                        m_batman[planet.get_name() + ext_plonly] = TransitModel(ldict[planet.get_name() + ext_plonly][params_pl_inst], tt)
                        m_batman[key_whole] = TransitModel(ldict[key_whole][params_pl_inst], tt)  # This should not be done here it will be repeated

                    if multi:
                        m_pl_inst = ("m_{planet}_{instmod_fullname}_dataset{dst_key}"
                                     "".format(planet=planet.get_name(),
                                               instmod_fullname=instmdl.get_name(include_prefix=True, code_version=True, recursive=True),
                                               dst_key=dst.number))

                    else:
                        m_pl_inst = "m_{planet}".format(planet=planet.get_name())
                    ldict[planet.get_name()][m_pl_inst] = m_batman[planet.get_name()]
                    ldict[planet.get_name() + ext_plonly][m_pl_inst] = m_batman[planet.get_name() + ext_plonly]
                    ldict[key_whole][m_pl_inst] = m_batman[key_whole]
                else:
                    if multi:
                        ## WARNING: This part of the code is untested and there will be a problem because dst_key is not define since there is not dataset.
                        params_pl_inst = ("params_{planet}_{instmod_fullname}_dataset{dst_key}"
                                          "".format(planet=planet.get_name(),
                                                    instmod_fullname=instmdl.get_name(include_prefix=True, code_version=True, recursive=True),
                                                    dst_key=dst.number))
                    else:
                        params_pl_inst = "params_{planet}".format(planet=planet.get_name())
                    ldict[planet.get_name()][params_pl_inst] = par_bat[planet.get_name()]
                    ldict[planet.get_name() + ext_plonly][params_pl_inst] = par_bat[planet.get_name() + ext_plonly]
                    ldict[key_whole][params_pl_inst] = par_bat[key_whole]
        # Create the radius ratio parameters
        param_text = add_param_argument(param=planet.Rrat, arg_list=arg_list, key_param=key_param, param_nb=param_nb,
                                        key_arglist=[key_whole, planet.get_name(), planet.get_name() + ext_plonly],
                                        param_vector_name=par_vec_name)
        params_whole[planet.get_name()][planet.Rrat.get_name()] = param_text[key_whole]
        params_planet[planet.get_name()][planet.Rrat.get_name()] = param_text[planet.get_name()]
        params_planet_only[planet.get_name()][planet.Rrat.get_name()] = param_text[planet.get_name() + ext_plonly]

        # Fill the template_tr_preambule_pl and create the preambule text for the transit model that compute intermediate variables
        # No need to make different cases for if batman or not or is dataset is None or not
        # because if one argument is not in the template, it is not used and this is it.
        preambule_tr_planet[planet.get_name()] = (
            template_tr_preambule_pl.format(planet=planet.get_name(), ltime_vec=l_time_vec, time_vec=time_vec,
                                            ecosw=params_planet[planet.get_name()]["ecosw"],
                                            esinw=params_planet[planet.get_name()]["esinw"],
                                            tic=params_planet[planet.get_name()]["tic"], rhostar=rhostar[planet.get_name()],
                                            cosinc=params_planet[planet.get_name()]["cosinc"], P=params_planet[planet.get_name()]["P"],
                                            Rrat=params_planet[planet.get_name()]["Rrat"], aR=params_planet[planet.get_name()]["aR"],
                                            tab=tab))
        preambule_tr_planet_only[planet.get_name()] = (
            template_tr_preambule_pl.format(planet=planet.get_name(), ltime_vec=l_time_vec, time_vec=time_vec,
                                            ecosw=params_planet_only[planet.get_name()]["ecosw"],
                                            esinw=params_planet_only[planet.get_name()]["esinw"],
                                            tic=params_planet_only[planet.get_name()]["tic"], rhostar=rhostar[planet.get_name() + ext_plonly],
                                            cosinc=params_planet_only[planet.get_name()]["cosinc"], P=params_planet_only[planet.get_name()]["P"],
                                            Rrat=params_planet_only[planet.get_name()]["Rrat"], aR=params_planet_only[planet.get_name()]["aR"],
                                            tab=tab))
        preambule_tr_whole += (template_tr_preambule_pl.
                               format(planet=planet.get_name(), ltime_vec=l_time_vec, time_vec=time_vec,
                                      ecosw=params_whole[planet.get_name()]["ecosw"],
                                      esinw=params_whole[planet.get_name()]["esinw"], tic=params_whole[planet.get_name()]["tic"],
                                      cosinc=params_whole[planet.get_name()]["cosinc"], P=params_whole[planet.get_name()]["P"],
                                      Rrat=params_whole[planet.get_name()]["Rrat"], aR=params_whole[planet.get_name()]["aR"],
                                      # ld_mod_name=LD_parcont.ld_type,
                                      rhostar=rhostar[key_whole],
                                      # ld_param_list=ld_param_list,
                                      tab=tab))

        # Fill the template_tr_planet that define the transit component of the return for each planet
        # planets LC contribution (planet_lc and whole_planets_lc)
        # No need for case if batman or if dataset is None. Same reason than above
        l_tr_planet[planet.get_name()] = []
        l_tr_planet_only[planet.get_name()] = []
        for ii, instmdl, dst, ld_param_list in zip(range(len(l_inst_model)), l_inst_model,
                                                   l_dataset, l_LD_param_list[key_whole]):
            if instmdl is None:
                instmdl_fname = None
            else:
                instmdl_fname = instmdl.get_name(include_prefix=True, code_version=True, recursive=True)
            if dst is None:
                dst_nb = None
            else:
                dst_nb = dst.number
            l_tr_planet[planet.get_name()].append(
                template_tr_planet.format(planet=planet.get_name(),
                                          ltime_vec=l_time_vec,
                                          time_vec=time_vec,
                                          instmod_fullname=instmdl_fname,
                                          dst_key=dst_nb,
                                          aR=params_planet[planet.get_name()]["aR"],
                                          Rrat=params_planet[planet.get_name()]["Rrat"],
                                          tic=params_planet[planet.get_name()]["tic"],
                                          P=params_planet[planet.get_name()]["P"],
                                          ld_param_list=ld_param_list,
                                          ii=ii
                                          ))
            l_tr_planet_only[planet.get_name()].append(
                template_tr_planet.format(planet=planet.get_name(),
                                          ltime_vec=l_time_vec,
                                          time_vec=time_vec,
                                          instmod_fullname=instmdl_fname,
                                          dst_key=dst_nb,
                                          aR=params_planet_only[planet.get_name()]["aR"],
                                          Rrat=params_planet_only[planet.get_name()]["Rrat"],
                                          tic=params_planet_only[planet.get_name()]["tic"],
                                          P=params_planet_only[planet.get_name()]["P"],
                                          ld_param_list=ld_param_list,
                                          ii=ii
                                          ))
            l_tr_whole_planets[ii] += "+ " + template_tr_planet.format(planet=planet.get_name(),
                                                                       ltime_vec=l_time_vec,
                                                                       time_vec=time_vec,
                                                                       instmod_fullname=instmdl_fname,
                                                                       dst_key=dst_nb,
                                                                       aR=params_planet[planet.get_name()]["aR"],
                                                                       Rrat=params_whole[planet.get_name()]["Rrat"],
                                                                       tic=params_whole[planet.get_name()]["tic"],
                                                                       P=params_whole[planet.get_name()]["P"],
                                                                       ld_param_list=ld_param_list,
                                                                       ii=ii
                                                                       )
            for key in [planet.get_name(), planet.get_name() + ext_plonly]:
                if transit_imp == "batman":
                    if not(has_dataset):
                        ldict[key]["TransitModel"] = TransitModel
                    ldict[key]["getomega_deg_fast"] = getomega_deg_fast
                else:
                    ldict[key]["getomega_fast"] = getomega_fast
                    ldict[key]["m"] = m_pytransit
    if transit_imp == "batman":
        if not(has_dataset):
            ldict[key_whole]["TransitModel"] = TransitModel
        ldict[key_whole]["getomega_deg_fast"] = getomega_deg_fast
    else:
        ldict[key_whole]["getomega_fast"] = getomega_fast
        ldict[key_whole]["m"] = m_pytransit

    return (preambule_tr_planet, preambule_tr_planet_only, preambule_tr_whole,
            l_tr_planet, l_tr_planet_only, l_tr_whole_planets,
            )


def get_phasecurve(multi, l_inst_model, l_dataset, phasecurve_model, l_LD_parcont, l_LD_param_list, parametrisation,
                   key_whole, key_param, SSE4instmodfname, star, planets, ext_plonly, arg_list, param_nb, ldict,
                   tab, did_transit,
                   rhostar, params_planet, params_planet_only, params_whole):
    """Provide the text for the phase curve part of the LC model text (preambule and return).

    Arguments
    ---------

    Returns
    -------

    """
    if phasecurve_model["instrument_variable"]:
        raise NotImplementedError(f"instrument_variable = True is not currently implemented")

    # dico to store_text for stellar params
    star_param_text = {}

    preambule_pl = {}
    preambule_pl_only = {}
    preambule_whole = ""
    l_return_pl = {}
    l_return_pl_only = {}
    l_return_whole = []

    for jj, planet in enumerate(planets.values()):

        planet_name = planet.get_name()

        preambule_pl[planet_name] = ""
        preambule_pl_only[planet_name] = ""
        l_return_pl[planet_name] = []
        l_return_pl_only[planet_name] = []

        for kk, pc_comp in enumerate(phasecurve_model['all_instruments']):
            pc_model = pc_comp['model']

            if pc_model == "spiderman":

                brightness_model = pc_comp["args"]["ModelParams_kwargs"]["brightness_model"]
                if ('lightcurve_kwargs' in pc_comp["args"]) and (len(pc_comp["args"]['lightcurve_kwargs']) > 0):
                    for key in [planet_name, planet_name + ext_plonly, key_whole]:
                        ldict[key]['lightcurve_kwargs'] = pc_comp["args"]['lightcurve_kwargs']
                    lightcurve_kwargs = ", **lightcurve_kwargs"
                else:
                    lightcurve_kwargs = ""

                if (brightness_model == "zhang"):
                    ########################################################################################################
                    # Produce the text for the model parameters and for the different function planet, planet only and whole
                    ########################################################################################################
                    if star.Teff.get_name() not in star_param_text:
                        star_param_text[star.Teff.get_name()] = add_param_argument(param=star.Teff, arg_list=arg_list, key_param=key_param, param_nb=param_nb,
                                                                                   key_arglist=None, param_vector_name=par_vec_name)

                    # Create the additional planetary model parameters for the phasecurve model
                    l_params = [planet.u1, planet.u2, planet.a, planet.xi, planet.deltaT, planet.Tn]
                    for param in l_params:
                        param_text = add_param_argument(param=param, arg_list=arg_list, key_param=key_param, param_nb=param_nb,
                                                        key_arglist=[key_whole, planet_name, planet_name + ext_plonly],
                                                        param_vector_name=par_vec_name)
                        params_whole[planet_name][param.get_name()] = param_text[key_whole]
                        params_planet[planet_name][param.get_name()] = param_text[planet_name]
                        params_planet_only[planet_name][param.get_name()] = param_text[planet_name + ext_plonly]

                    ######################################################
                    # Produce the template for phase curve model preambule
                    ######################################################
                    if not(did_transit):
                        template_preambule_pl = dedent(f"""
                            {{tab}}ecc_{planet_name} = sqrt({{ecosw}} * {{ecosw}} + {{esinw}} * {{esinw}})
                            {{tab}}omega_{planet_name} = getomega_deg_fast({{ecosw}}, {{esinw}})
                            {{tab}}inc_{planet_name} = degrees(acos({{cosinc}}))""")
                        if parametrisation == "Multis":
                            template_preambule_pl += dedent(f"""
                        {{tab}}aR_{planet_name} = getaoverr({{P}}, {{rhostar}}, ecc_{planet_name}, omega_{planet_name})""")
                    else:
                        template_preambule_pl = ""

                    done_preambule4instmodel = []
                    for ii, (instmdl, dst) in enumerate(zip(l_inst_model, l_dataset)):
                        instmod_name = instmdl.get_name(include_prefix=True, code_version=True, prefix_kwargs={'include_prefix': False, 'code_version': True})
                        # Define extension for the name of spiderman ModelParams instances
                        sp_param_ext = get_planet_inst_dst_ext(planet=planet, inst_model=instmdl, multi=multi)
                        params_pl_inst = f"param_spiderman{sp_param_ext}"
                        if instmod_name not in done_preambule4instmodel:
                            for key in [planet_name, planet_name + ext_plonly, key_whole]:
                                ldict[key][params_pl_inst] = ModelParams(**pc_comp["args"]["ModelParams_kwargs"])
                            template_preambule_pl += dedent(f"""
                                {{tab}}{params_pl_inst}.t0 = {{tic}}
                                {{tab}}{params_pl_inst}.per = {{P}}
                                {{tab}}{params_pl_inst}.a_abs = {{a}}
                                {{tab}}{params_pl_inst}.rp = {{Rrat}}
                                {{tab}}{params_pl_inst}.inc = inc_{planet_name}
                                {{tab}}{params_pl_inst}.ecc = ecc_{planet_name}
                                {{tab}}{params_pl_inst}.w = omega_{planet_name}
                                {{tab}}{params_pl_inst}.p_u1 = {{u1}}
                                {{tab}}{params_pl_inst}.p_u2 = {{u2}}
                                {{tab}}{params_pl_inst}.xi = {{xi}}
                                {{tab}}{params_pl_inst}.T_n = {{Tn}}
                                {{tab}}{params_pl_inst}.delta_T = {{deltaT}}
                                {{tab}}{params_pl_inst}.T_s = {{Ts}}""")
                            if parametrisation == "Multis":
                                template_preambule_pl += dedent(f"""
                                    {{tab}}{params_pl_inst}.a = aR_{planet_name}
                                    """)
                            else:
                                template_preambule_pl += dedent(f"""
                                    {{tab}}{params_pl_inst}.a = {{aR}}
                                    """)
                            # Add the non free parameters attribute to params_spiderman
                            spiderman_dico_attr = copy(pc_comp["args"]["attributes"])
                            filter = spiderman_dico_attr.pop("filter", None)
                            n_layers = spiderman_dico_attr.pop("n_layers", 5)
                            l1 = spiderman_dico_attr.pop("l1")
                            l2 = spiderman_dico_attr.pop("l2")
                            if filter is not None:
                                template_preambule_pl += dedent(f"""
                                    {{tab}}{params_pl_inst}.filter = '{filter}'
                                    """)
                            template_preambule_pl += dedent(f"""
                                {{tab}}{params_pl_inst}.l1 = {l1}
                                {{tab}}{params_pl_inst}.l2 = {l2}
                                {{tab}}{params_pl_inst}.n_layers = {n_layers}
                                """)
                            ############################################################################################################
                            # Fill the template for phase curve model preambule for the different function planet, planet only and whole
                            ############################################################################################################
                            preambule_pl[planet.get_name()] += (
                                template_preambule_pl.format(ecosw=params_planet[planet_name]["ecosw"],
                                                             esinw=params_planet[planet_name]["esinw"],
                                                             tic=params_planet[planet_name]["tic"],
                                                             cosinc=params_planet[planet_name]["cosinc"],
                                                             P=params_planet[planet_name]["P"],
                                                             Rrat=params_planet[planet_name]["Rrat"],
                                                             aR=params_planet[planet_name]["aR"],
                                                             a=params_planet[planet_name]["a"],
                                                             u1=params_planet[planet_name]["u1"],
                                                             u2=params_planet[planet_name]["u2"],
                                                             xi=params_planet[planet_name]["xi"],
                                                             deltaT=params_planet[planet_name]["deltaT"],
                                                             Tn=params_planet[planet_name]["Tn"],
                                                             rhostar=rhostar[planet_name],
                                                             Ts=star_param_text[star.Teff.get_name()][planet_name],
                                                             # ltime_vec=l_time_vec, time_vec=time_vec,
                                                             tab=tab
                                                             ))
                            preambule_pl_only[planet_name] += (
                                template_preambule_pl.format(ecosw=params_planet_only[planet_name]["ecosw"],
                                                             esinw=params_planet_only[planet_name]["esinw"],
                                                             tic=params_planet_only[planet_name]["tic"],
                                                             cosinc=params_planet_only[planet_name]["cosinc"],
                                                             P=params_planet_only[planet_name]["P"],
                                                             Rrat=params_planet_only[planet_name]["Rrat"],
                                                             aR=params_planet_only[planet_name]["aR"],
                                                             a=params_planet_only[planet_name]["a"],
                                                             u1=params_planet_only[planet_name]["u1"],
                                                             u2=params_planet_only[planet_name]["u2"],
                                                             xi=params_planet_only[planet_name]["xi"],
                                                             deltaT=params_planet_only[planet_name]["deltaT"],
                                                             Tn=params_planet_only[planet_name]["Tn"],
                                                             rhostar=rhostar[planet_name + ext_plonly],
                                                             Ts=star_param_text[star.Teff.get_name()][planet_name + ext_plonly],
                                                             # ltime_vec=l_time_vec, time_vec=time_vec,
                                                             tab=tab
                                                             ))
                            preambule_whole += (template_preambule_pl.
                                                format(ecosw=params_whole[planet_name]["ecosw"],
                                                       esinw=params_whole[planet_name]["esinw"],
                                                       tic=params_whole[planet_name]["tic"],
                                                       cosinc=params_whole[planet_name]["cosinc"],
                                                       P=params_whole[planet_name]["P"],
                                                       Rrat=params_whole[planet_name]["Rrat"],
                                                       aR=params_whole[planet_name]["aR"],
                                                       a=params_whole[planet_name]["a"],
                                                       u1=params_whole[planet_name]["u1"],
                                                       u2=params_whole[planet_name]["u2"],
                                                       xi=params_whole[planet_name]["xi"],
                                                       deltaT=params_whole[planet_name]["deltaT"],
                                                       Tn=params_whole[planet_name]["Tn"],
                                                       rhostar=star_param_text[star.Teff.get_name()][key_whole],
                                                       Ts=star_param_text[star.Teff.get_name()][key_whole],
                                                       # ltime_vec=l_time_vec, time_vec=time_vec,
                                                       tab=tab
                                                       ))
                            done_preambule4instmodel.append(instmod_name)
                        ####################################################
                        # Produce the template for phase curve model returns
                        ####################################################
                        if multi:
                            template_return_pl = (f"{params_pl_inst}.lightcurve({{ltime_vec}}[{ii}]{lightcurve_kwargs}) - 1 ")
                        else:
                            template_return_pl = (f"{params_pl_inst}.lightcurve({{time_vec}}{lightcurve_kwargs}) - 1 ")
                        ##########################################################################################################
                        # Fill the template for phase curve model returns for the different function planet, planet only and whole
                        ##########################################################################################################
                        # No need for case for same reason than above
                        ret_pl = template_return_pl.format(ltime_vec=l_time_vec, ii=ii, time_vec=time_vec)
                        if kk == 0:
                            l_return_pl[planet_name].append(ret_pl)
                            l_return_pl_only[planet_name].append(ret_pl)
                            if jj == 0:
                                l_return_whole.append(ret_pl)
                        else:
                            l_return_pl[planet_name] += "+ " + ret_pl
                            l_return_pl_only[planet_name] += "+ " + ret_pl
                            l_return_whole[ii] += "+ " + ret_pl
                else:
                    raise NotImplementedError(f"brightness_model {brightness_model} of spiderman is not implemented.")
            else:
                raise NotImplementedError(f"phasecurve model {pc_model} is not implemented.")
    return (preambule_pl, preambule_pl_only, preambule_whole,
            l_return_pl, l_return_pl_only, l_return_whole,
            )


def get_planet_inst_dst_ext(planet, inst_model, multi):
    if multi:
        sp_param_ext = f"_{planet.get_name()}_{inst_model.get_name(include_prefix=True, code_version=True, prefix_kwargs={'include_prefix': False, 'code_version': True})}"
    else:
        sp_param_ext = f"_{planet.get_name()}"
    return sp_param_ext
