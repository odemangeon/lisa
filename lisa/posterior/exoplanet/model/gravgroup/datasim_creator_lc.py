#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Datasim creator LC module.

TODO:
- At the moment, when I am producing a datasimulator for multiple datasets and I am producing it with batman. I do a TransitParams instance
for each dataset even if the datasets are using the same instruments. It looks not necessary and I should probably test that I can use the
same TransitParams instance for multiple TransitModel instances and if yes only create one TransitParams instance per transit model.
(I need to create on TransitParams instance per instrument because of the LD coefficients.)
- Currently I am never using this code to produce datsimulators for multiple instruments without using the times from the datasets.
So all the code handling this configuration is untested and probably bugged at this point.
- I am not sure that some of the comments are still valid. So I need to check if this comment are still valid or not.
Search for TODO_CHECK_THIS_COMMENT which I put in front each one of these comments.
"""
from logging import getLogger
from textwrap import dedent
from copy import deepcopy, copy
from math import acos, degrees, sqrt
from numpy import ones_like, inf, mean
from collections import Iterable

from batman import TransitModel, TransitParams
# from pytransit import MandelAgol  # Temporarily? remove pytransit from the available rv_models
from spiderman import ModelParams

from . import get_function_planet_shortname
from ....core import function_whole_shortname
from ....core.model import par_vec_name
from ....core.model.datasim_docfunc import DatasimDocFunc
from ....core.model.datasimulator_toolbox import check_datasets_and_instmodels
from ....core.model.datasimulator_timeseries_toolbox import add_time_argument, time_vec, l_time_vec
from .....tools.function_from_text_toolbox import FunctionBuilder, argskwargs
from .....posterior.exoplanet.model.convert import getaoverr, getomega_fast, getomega_deg_fast


## Logger object
logger = getLogger()


def create_datasimulator_LC(star, planets, parametrisation, ldmodel4instmodfname, LDs, transit_model, SSE4instmodfname,
                            phasecurve_model, decorrelation_config, dataset_db, LCcat_model,
                            inst_models, datasets, get_times_from_datasets,
                            ):
    """Return datasimulator functions.

    A datasimualtor function is created for the whole dataset_database and for each planet
    individually.

    Arguments
    ---------
    star                        : Star object
        Star instance of the parent star
    planets                     : dict of Planets
        Dictionary of Planet instance providing the planets in the system
        Format: {"planet name": Planet instance}
    parametrisation             : str
        string refering to the parametrisation to use
    ldmodel4instmodfname        : dict of dict of str
        Dictionary giving Limd darkening model to use for each instrument model and for each star
        Format: {"<instrument_model_name>: {"<star_name>": "<LD_model_name>"}
    LDs                         : dict of CoreLD
        Dictionary of subclasses of CoreLD instances providing the different limb-darkening models
        Format: {f"<star_name>_<LD model name>"": CoreLD_subclass instance, }
    transit_model               : dict
        Dictionary describing the transit model to use. The format of this disctionary is:
        {"do": True,  # Should we model the transit
         'instrument_variable': False,  # Whether or not different instruemnt can have different transit model
         'all_instruments': {'model': 'batman'  #String refering to the transit model to use (can be 'pytransit' or 'batman')
                             },
         'instrument_specific': {'<instrument_full_name>': 'all_instruments' # all instrument or dictionary like the 'all_instruments' one
                                 }
         }
    SSE4instmodfname            : dict of dict of str int and float
        Dictionary giving the supersampling factor and the exposure time to use for each instrument model
        Format: {"instrument model name": {'supersamp': int_supersampling_factor, 'exptime': float_exposure_time}}
    phasecurve_model            : dict
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
    decorrelation_config        : dict
        Dictionary decribing the decorrelation models for the LC instrument models.
        The format is {'<instrument model name>': {'do': <bool>,
                                                   'what to decorrelate': {'<model part>': {'<decorrelation model name>': {'<IND isntrument model name>': {<parameters of the decorrelation>},
                                                                                                                          ...
                                                                                                                          },
                                                                                            ...
                                                                                            },
                                                                           ...
                                                                           }
                                                   }
    dataset_db                  : DatasetDatabase
        Dataset database, this will be used by the function to access the dataset for the decorrelation,
        not to access the LC datasets to be simulated.
    LCcat_model                 : LC_InstCat_Model
        Instance of the LC_InstCat_Model
    inst_models                 : Instrument_Model or List of Instrument_Model
        List of Instrument_Model instance which, if datasets is provided, should be the instrument models
        to use for each dataset provided in the datasets arguments.
    datasets                    : Dataset or list_of_Datase
        List of datasets to be simulated. The number of datasets needs to match the number of instrument
        models provided by the inst_models arguments
    get_times_from_datasets     : bool
        If True the times at which the LC model is computed is taken from the datasets.
        Else it is an input of the datasimulator function produced.
    param_vector_name           : str
        string giving the name of the vector of parameters argument of the datasimulator function.

    Returns
    -------
    dico_docf : dict_of_DatasimDocFunc
        A dictionary with DocFunctions containing the datasimulator functions. This function produces
        several data simulator functions. The keys of the dictionary are the shortname of the datasimulators.
        - "<function_whole_shortname>": model with all the components
        - "tr_<planet>": only the transit model of one planet (mean stellar flux at zero)
        - "pc_<comp>_<planet>": only 1 component of the phasecurve model of one planet (mean stellar flux at zero)
        - "pc_<planet>": only the full phasecurve model of 1 planet (mean stellar flux at zero)
        - "<planet>": only the transit and the full phasecurve model of 1 planet (mean stellar flux at zero)
        - "inst_var": only the instrumental variations
    """
    #############################################################
    # Check the content of the datasets and inst_models arguments
    #############################################################
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

    # Create the FunctionBuilder
    func_builder = FunctionBuilder(parameter_vector_name=par_vec_name)

    #####################################################################################################
    ## Initialise the function in the function builder for the whole system and the planet and planet only functions
    #####################################################################################################
    func_builder.add_new_function(shortname=function_whole_shortname)
    if multi:
        func_full_name_MultiOrDst_ext = "_multi"
    else:
        func_full_name_MultiOrDst_ext = f"{l_dataset[0].dataset_name}"
    func_builder.set_function_fullname(full_name=f"LC_sim_{function_whole_shortname}{func_full_name_MultiOrDst_ext}", shortname=function_whole_shortname)
    l_function_planet_shortname = [get_function_planet_shortname(planet) for planet in planets.values()]
    for function_shortname in l_function_planet_shortname:
        func_builder.add_new_function(shortname=function_shortname)
        func_builder.set_function_fullname(full_name=f"LC_sim_{function_shortname}{func_full_name_MultiOrDst_ext}", shortname=function_whole_shortname)

    #####################################
    # Define the templates of the function
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
    tab = "    "
    template_function = dedent(template_function)

    #########################################################################################
    # Create the text of what to return when condition is met or the RuntimeError is catched
    ########################################################################################
    error_return = get_catchederror_return(multi=multi, l_inst_model=l_inst_model)

    #####################################
    # Produce instrumental variations models
    #####################################
    ## Get the d_l_inst_var and add the t_ref(s) to the list of arguments for the functions
    # d_l_inst_var is the list of strings giving the string representation of the out of transit variation model
    # for each couple instrument model - dataset in l_inst_model and l_dataset.
    # Format: ["oot model", ]
    d_l_inst_var = get_instvar(l_inst_model=l_inst_model, l_dataset=l_dataset, multi=multi,
                               function_builder=func_builder, l_function_shortname=[function_whole_shortname, "inst_var"],
                               get_times_from_datasets=get_times_from_datasets, time_vec_name=time_vec, l_time_vec_name=l_time_vec)

    ########################
    # Produce Transit models
    ########################
    do_transit = transit_model['do']
    if do_transit:
        ## Get the ld_parcont_name, ld_parcont and ld_param_list variable
        # - l_LD_parcont_name is the List of limb darkening models name (parameter container name) associated with the Instrument_Model instances
        # in l_inst_model.
        # Format: ["<limb darkening model name>", ]
        # - l_LD_parcont is the list of limb darkening models (parameter container object) associated with the Instrument_Model instances
        # in l_inst_model.
        # Format: [<limb darkening model>, ]
        # - l_LD_param_list is the list of string which themself write the list of limb darkening parameters values associated with the Instrument_Model instances
        # in l_inst_model.
        # Format: ["[p[1], p[2]]", ]
        # (dico_l_LD_parcont_name, dico_l_LD_parcont, dico_l_LD_param_list
        #  ) = get_LD_parcont_and_param(l_inst_model=l_inst_model, ldmodel4instmodfname=ldmodel4instmodfname,
        #                               star=star, l_planet_name=[planet.get_name() for planet in planets.values()], LDs=LDs,
        #                               function_builder=func_builder, l_function_shortname=[function_whole_shortname, ] + l_function_planet_shortname
        #                               )

        (preambules, returns
         ) = get_transit(multi=multi, l_inst_model=l_inst_model, l_dataset=l_dataset, get_times_from_datasets=get_times_from_datasets,
                         transit_model=transit_model, ldmodel4instmodfname=ldmodel4instmodfname, LDs=LDs,
                         parametrisation=parametrisation, SSE4instmodfname=SSE4instmodfname, star=star, planets=planets,
                         tab=tab, time_vec_name=time_vec, l_time_vec_name=l_time_vec, function_builder=func_builder
                         )
    else:
        preambule_tr_planet = preambule_tr_planet_only = {plnt: "" for plnt in planets}
        preambule_tr_whole = ""
        d_l_tr_ret_planet = d_l_tr_ret_planet_only = {plnt: ["" for instmod in l_inst_model] for plnt in planets}
        l_tr_ret_whole_planets = ["" for instmod in l_inst_model]

    ############################
    # Produce phase curve models
    ############################
    do_phasecurve = phasecurve_model['do']
    if do_phasecurve:
        (preambule_pc_planet, preambule_pc_planet_only, preambule_pc_whole,
         d_l_pc_ret_planet, d_l_pc_ret_planet_only, l_pc_ret_whole_planets,
         ) = get_phasecurve(multi=multi, l_inst_model=l_inst_model, phasecurve_model=phasecurve_model,
                            dico_l_LD_parcont=dico_l_LD_parcont, dico_l_LD_param_list=dico_l_LD_param_list, parametrisation=parametrisation,
                            key_whole=key_whole, key_param=key_param, SSE4instmodfname=SSE4instmodfname, planets=planets, star=star,
                            ext_plonly=ext_plonly, arg_list=arg_list, param_nb=param_nb, ldict=ldict, tab=tab, did_transit=do_transit,
                            rhostar=rhostar, params_planet=params_planet, params_planet_only=params_planet_only, params_whole=params_whole)
    else:
        preambule_pc_planet = preambule_pc_planet_only = {plnt: "" for plnt in planets}
        preambule_pc_whole = ""
        d_l_pc_ret_planet = d_l_pc_ret_planet_only = {plnt: ["" for instmod in l_inst_model] for plnt in planets}
        l_pc_ret_whole_planets = ["" for instmod in l_inst_model]

    ###########################
    # Produce the decorrelation
    ###########################
    (d_l_decorr_planet, d_l_decorr_planet_only, l_decorr_whole
     ) = get_decorrelation(multi=multi, planets=planets, l_inst_model=l_inst_model, l_dataset=l_dataset,
                           arguments=arguments,
                           decorrelation_config=decorrelation_config, dataset_db=dataset_db, param_nb=param_nb, arg_list=arg_list,
                           key_param=key_param, key_mand_kwargs=key_mand_kwargs, key_opt_kwargs=key_opt_kwargs,
                           key_whole=key_whole, ldict=ldict, ext_plonly=ext_plonly, LCcat_model=LCcat_model,
                           time_arg_name=time_arg_name)

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
        # Get the returns text for each planet
        returns_pl = ""
        returns_pl_only = ""
        for (oot_var_planet, oot_var_planet_only, planet_tr, planet_only_tr, planet_pc, planet_only_pc,
             decorr_planet, decorr_planet_only
             ) in zip(d_l_inst_var[planet.get_name()], d_l_inst_var[planet.get_name() + ext_plonly],
                      d_l_tr_ret_planet[planet.get_name()], d_l_tr_ret_planet_only[planet.get_name()],
                      d_l_pc_ret_planet[planet.get_name()], d_l_pc_ret_planet_only[planet.get_name()],
                      d_l_decorr_planet[planet.get_name()], d_l_decorr_planet_only[planet.get_name()]):

            returns_pl += combine_return_models(which_model="full", stellar_var=oot_var_planet, transit=planet_tr, phasecurve=planet_pc,
                                                decorrelation=decorr_planet)
            returns_pl_only += combine_return_models(which_model="pl_only", stellar_var=oot_var_planet_only, transit=planet_only_tr, phasecurve=planet_only_pc,
                                                     decorrelation=decorr_planet_only)
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
    # Get the return text for the whole system
    returns_whole = ""
    for oot_var, whole_transit, whole_phasecurve, whole_decorr in zip(d_l_inst_var[key_whole], l_tr_ret_whole_planets, l_pc_ret_whole_planets, l_decorr_whole):
        returns_whole += combine_return_models(which_model="full", stellar_var=oot_var, transit=whole_transit, phasecurve=whole_phasecurve,
                                               decorrelation=whole_decorr)
    if not(multi):  # If multi, the coma in the end ensure that the output is always a tuple (even there is actually just one dataset). This is very important for output of datasim_all_datasets.
        returns_whole = returns_whole[:-2]
    # Finalise the text of whole system LC simulator function
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
                                            include_dataset_kwarg=get_times_from_datasets,
                                            mand_kwargs=mand_kwargs,
                                            opt_kwargs=opt_kwargs,
                                            inst_model_fullname=instmod_docf,
                                            dataset=dtsts_docf)
    return dico_docf


def get_instvar(l_inst_model, l_dataset, multi, function_builder, l_function_shortname, get_times_from_datasets,
                time_vec_name, l_time_vec_name):
    """Get the instrumental variation contribution to the light-curve

    Arguments
    ---------
    l_inst_model            : list_of_Instrument_Model
        Checked list of Instrument_Model instance(s).
    l_dataset               : list_of_Dataset
        Checked list of Dataset instance(s).
    multi                   : bool
        True if the datasim function needs to give multiple outputs.
    function_builder        : FunctionBuilder
        Function builder instance
    l_function_shortname    : list of str
        List of the short name of the functions for which you want to add the instrument variation component
    get_times_from_datasets : bool
        True the datasets should be used to extract the time vectors
    time_vec_name           : str
        Str used to design the time vector
    l_time_vec_name         : str
        Str used to design the list of time vector

    Returns
    -------
    d_l_inst_var   : dict of list_of_string
        Dictionary providing, for all functions specified by l_function_shortname, the list of the string representations
        of the instrumental variations model for each couple instrument model - dataset in l_inst_model and l_dataset.
        Format of the dictionary:
        - key : key or keys specificied by l_function_shortname
        - value: List = ["<inst variation model for instrument1 and dataset1>", ...]
    """
    d_l_inst_var = {}

    for function_shortname in l_function_shortname:
        d_l_inst_var[function_shortname] = []
        # For each instrument model and dataset, ...
        for ii, instmdl in enumerate(l_inst_model):
            d_l_inst_var[function_shortname].append("")
            # ..., if instrument variations have been asked, ...
            if instmdl.get_with_inst_var():
                # ..., For each order in the required polynomial model, ...
                for order in range(instmdl.get_inst_var_order() + 1):
                    # ..., get the name and full name of the parameter for this order
                    instvar_param_name = instmdl.get_inst_var_param_name(order)
                    # ..., If this parameter is a main parameter (it should be), ...
                    if instmdl.parameters[instvar_param_name].main:
                        value_not0 = True
                        function_builder.add_parameter(parameter=instmdl.parameters[instvar_param_name], function_shortname=function_shortname)
                        text_instvar_param = function_builder.get_text_4_parameter(parameter=instmdl.parameters[instvar_param_name], function_shortname=function_shortname)
                        # ..., if the parameter is free or the fixed value is not zero, ...
                        if text_instvar_param != 0.0:
                            d_l_inst_var[function_shortname][ii] += "+ {}".format(text_instvar_param)
                        # ..., else, since the fixed value is zero, this order doesn't have any
                        # contribution
                        else:
                            value_not0 = False
                        # ..., if the order has a contribution to the instrumental variations and
                        # the considered order is more than 0 meaning the time plays a role, ...
                        if value_not0 and order > 0:
                            # ..., and you need a time reference. There is one time reference per instrument
                            # model, which is automatically set to the time of the first measurement
                            # among the datasets associated with this instrument model.
                            # So start be creating the name of the instrument model
                            timeref_instmod = f"timeref_instvar_{instmdl.full_code_name}"
                            # if this time_reference is not already in the ldict of the function ...
                            if timeref_instmod not in function_builder.get_ldict(function_shortname=function_shortname):
                                # we have to compute its value and add it to the ldict
                                l_dataset_name_instmod = [dst.dataset_name for i_dst, dst in enumerate(l_dataset) if l_inst_model[i_dst] == instmdl]
                                timeref_instmod_value = min([min(dst.get_time()) for dst in l_dataset_name_instmod])
                                function_builder.add_variable_to_ldict(variable_name=l_dataset_name_instmod, variable_content=timeref_instmod_value, function_shortname=function_shortname)
                            # ..., add the end of this order's contribution to the text of the instruments variations, ...
                            # add the time argument
                            time_arg_name = add_time_argument(function_builder=function_builder, function_shortname=function_shortname,
                                                              multi=multi, get_times_from_datasets=get_times_from_datasets,
                                                              l_dataset=l_dataset, time_vec_name=time_vec_name, l_time_vec_name=l_time_vec_name,
                                                              exist_ok=True)
                            if order == 1:
                                if multi:
                                    d_l_inst_var[function_shortname][ii] += f" * ({time_arg_name}[{ii}] - {timeref_instmod}) "
                                else:
                                    d_l_inst_var[function_shortname][ii] += f" * ({time_arg_name} - {timeref_instmod}) "
                            elif order > 1:
                                if multi:
                                    d_l_inst_var[function_shortname][ii] += (f" * ({time_arg_name}[{ii}] - {timeref_instmod})**{order}")
                                else:
                                    d_l_inst_var[function_shortname][ii] += (f" * ({time_arg_name} - {timeref_instmod})**{order}")
                        # If the is no contribution to the oot of transit variation from this order
                        # add only a space.
                        elif value_not0 and order == 0:
                            d_l_inst_var[function_shortname][ii] += " "
    return d_l_inst_var


def get_LD_parcont_and_param(l_inst_model, ldmodel4instmodfname, star, l_planet_name, LDs, function_builder, l_function_shortname):
    """Return the list of LD param container name, instance and parameter string list for a given star.

    Arguments
    ---------
    l_inst_model                : list_of_Instrument_Model
        Checked list of Instrument_Model instance(s).
    ldmodel4instmodfname        : dict of dict of str
        Dictionary giving Limd darkening model to use for each instrument model and for each star
        Format: {"<instrument_model_name>: {"<star_name>": "<LD_model_name>"}
    star                        : Star
        Star object
    l_planet_name               : list of str
        List of the planet names (needed for the short name of the function of each planet and planet only models)
    LDs                         : dict of CoreLD
        Dictionary of subclasses of CoreLD instances providing the different limb-darkening models
        Format: {f"<star_name>_<LD model name>"": CoreLD_subclass instance, }
    function_builder            : FunctionBuilder
        Function builder instance
    l_function_shortname        : list_of_str
        List of the short name of the functions for which you want to add the LD parameters

    Returns
    -------
    dico_l_LD_parcont_name   : dict_of_list_of_string
        Dictionary providing, for all functions specified by l_function_shortname, the list of limb darkening models
        name (parameter container name) associated with the Instrument_Model instances in l_inst_model.
        Format of the dictionary:
        - key : key or keys specificied by l_function_shortname
        - value: List = ["<LD parameter container name for instrument1>", ...]
    dico_l_LD_parcont        : dict_of_list_of_LD
        Dictionary providing, for all functions specified by l_function_shortname, the list of limb darkening models
        (parameter container object) associated with the Instrument_Model instances in l_inst_model.
        Format of the dictionary:
        - key : key or keys specificied by l_function_shortname
        - value: List = [<LD parameter container for instrument1>, ...]
    dico_l_LD_param_list     : dict_of_list_of_str
        Dictionary providing, for all functions specified by l_function_shortname, the list of string which themself
        write the list of limb darkening parameters values associated with the Instrument_Model instances
        in l_inst_model.
        Format of the dictionary:
        - key : key or keys specificied by l_function_shortname
        - value: List = ["[<value for LD param1 for instrument1> , <value for LD param2 for instrument1>, ...]", ...]
    """
    # Get the ld_parcont and ld_param_list
    dico_l_LD_parcont_name = {}
    dico_l_LD_parcont = {}
    dico_l_LD_param_list = {}

    for function_shortname in l_function_shortname:
        dico_l_LD_parcont_name[function_shortname] = []
        dico_l_LD_parcont[function_shortname] = []
        dico_l_LD_param_list[function_shortname] = []
        for ii, instmdl in enumerate(l_inst_model):
            dico_l_LD_parcont_name[function_shortname].append(ldmodel4instmodfname[instmdl.get_name(include_prefix=True, code_version=True, recursive=True)][star.code_name])
            dico_l_LD_parcont[function_shortname].append(LDs[star.code_name + "_" + dico_l_LD_parcont_name[function_shortname][ii]])
            dico_l_LD_param_list[function_shortname].append("[")
            for param in dico_l_LD_parcont[function_shortname][ii].get_list_params(main=True):
                function_builder.add_parameter(parameter=param, function_shortname=function_shortname)
                LD_coeff_text = function_builder.get_text_4_parameter(parameter=param, function_shortname=function_shortname)
                dico_l_LD_param_list[function_shortname][ii] += LD_coeff_text + ", "
            dico_l_LD_param_list[function_shortname][ii] += "]"
    return dico_l_LD_parcont_name, dico_l_LD_parcont, dico_l_LD_param_list


def define_orbital_params(star, planets, parametrisation, function_builder):
    """Define the orbital parameters as model parameters in the function builder

    Arguments
    ---------
    star                        : Star
        Star object
    planets                     : dict of Planets
        Dictionary of Planet instance providing the planets in the system
        Format: {"planet name": Planet instance}
    parametrisation             : str
        string refering to the parametrisation to use
    function_builder            : FunctionBuilder
        Object which help building the function

    TBR
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
    l_function_shortname_add_rho = [function_whole_shortname, ]
    for planet in planets.values():
        l_function_shortname_add_rho.extend([planet.get_name(), planet.get_name() + ext_plonly])
    # Add the stellar density the model parameter vectors
    if parametrisation == "Multis":
        for function_shortname in l_function_shortname_add_rho:
            function_builder.add_parameter(parameter=star.rho, function_shortname=function_shortname)

    # Create the text for each planet parameter for the current planet model (planet and planet_only) and for the whole system.
    for planet in planets.values():
        l_param = [planet.ecosw, planet.esinw, planet.cosinc, planet.tic, planet.P]
        if parametrisation != "Multis":
            l_param.append(planet.aR)
        for function_shortname in [function_whole_shortname, planet.get_name(), planet.get_name() + ext_plonly]:
            for param in l_param:
                function_builder.add_parameter(parameter=param, function_shortname=function_shortname)


def get_conditions(planets, parametrisation, function_builder, l_function_shortname, tab, error_return):
    """
    Return the text related to the condition to test if the planet goes into the star

    Arguments
    ---------
    planets                     : dict of Planets
        Dictionary of Planet instance providing the planets in the system
        Format: {"planet name": Planet instance}
    parametrisation             : str
        string refering to the parametrisation to use
    function_builder            : FunctionBuilder
        Function builder instance
    l_function_shortname        : List of str
        List of the short name of the function for which you want to had the condition
    tab                         : str
        String providing the space to put in front of each new line
    error_return                : str
        Text of what to return if an error is catched (in principle a LC full of inf)

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
    # Initialise template_condition, the template for the condition (no planet should pass into the star)
    template_condition = """
    {tab}{preambule}
    {tab}if {condition}:
    {tab}    return {returns}
    """
    template_condition = dedent(template_condition)

    preambule_cond_whole = "condition = False\n"
    condition_planet = {}
    condition_planet_only = {}
    for ii, planet in enumerate(planets.values()):
        planet_name = planet.get_name()
        # Fill the template_preambule_condition
        for function_shortname in [planet_name, planet_name + ext_plonly, function_whole_shortname]:
            if parametrisation == "Multis":
                aR_text = f"aR_{planet_name}"
            else:
                aR_text = function_builder.get_text_4_parameter(parameter=planet.aR, function_shortname=function_shortname)
            if planet.Rrat in function_builder.get_parameter_vector(function_shortname=function_shortname):
                Rrat_text = function_builder.get_text_4_parameter(parameter=planet.Rrat, function_shortname=function_shortname)
                preambule_cond_planet = f"condition_{planet_name} = ({aR_text} < ((1.5 / (1 - ecc_{planet_name})) + {Rrat_text}))\n"
            else:
                preambule_cond_planet = f"condition_{planet_name} = ({aR_text} < (1.5 / (1 - ecc_{planet_name})))\n"
            if function_shortname == function_whole_shortname:
                preambule_cond_whole += tab + preambule_cond_planet
            elif function_shortname == planet_name:
                condition_planet[planet_name] = template_condition.format(preambule=preambule_cond_planet, condition=f"condition_{planet_name}", returns=error_return, tab=tab)
            else:
                condition_planet_only[planet_name] = template_condition.format(preambule=preambule_cond_planet, condition=f"condition_{planet_name}", returns=error_return, tab=tab)
    preambule_cond_whole += f"{tab}condition = condition or condition_{planet_name}\n"
    condition_whole = template_condition.format(preambule=preambule_cond_whole, condition="condition", returns=error_return, tab=tab)

    return condition_planet, condition_planet_only, condition_whole


def get_catchederror_return(multi, l_inst_model, time_vec_name=time_vec, l_time_vec_name=l_time_vec):
    """Provide the text of what to return when an error is catched.

    Arguments
    ---------
    multi           : bool
        True if the datasim function needs to give multiple outputs.
    l_inst_model    : list_of_Instrument_Model
        List of the instrument models instances for each output of the datasim function
    time_vec_name       : str
        Str used to designate the time vector
    l_time_vec_name     : str
        Str used to designate the list of time vectors

    Returns
    -------
    error_return : str
        Text of what to return if an error is catched
    """
    if multi:
        template_returns_condition = "ones_like({ltime_vec}) * (- inf)"  # "ones_like({ltime_vec}[{ii}]) * (- inf)"
    else:
        template_returns_condition = "ones_like({time_vec}) * (- inf)"

    l_returns = []
    for ii in range(len(l_inst_model)):
        l_returns.append(template_returns_condition.format(ltime_vec=l_time_vec_name, time_vec=time_vec_name))

    error_return = ""
    for ret in l_returns:
        error_return += ret
        error_return += ", "
    if not(multi):
        error_return = error_return[:-2]

    return error_return


def get_transit(multi, l_inst_model, l_dataset, get_times_from_datasets, transit_model,
                ldmodel4instmodfname, LDs, parametrisation, SSE4instmodfname,
                star, planets, tab, time_vec_name, l_time_vec_name, function_builder,
                ):
    """Provide the text for the transit part of the LC model text (preambule and return).

    This function should generate the text for the "<function_whole_shortname>" function, the "<planet>"
    functions and the "tr_<planet>" function.

    Arguments
    ---------
    multi                   : bool
        True if the datasim function needs to give multiple outputs.
    l_inst_model            : list_of_Instrument_Model
        List of the instrument models instances for each output of the datasim function. Each instrument model
        in this list is the instrument model which has to be used for the corresponding dataset provided in l_dataset.
    l_dataset               : list of Datasets
        List of the Dataset intances for each output of the datasim function. The instrument model to be used for
        each dataset is provided in l_inst_model.
    get_times_from_datasets : bool
        If True the times at which the model should be computed will be taken from the datasets and
        included into the function. I False the user of the function will have to provide the times.
    transit_model           : dict
        Dictionary describing the transit model to use. The format of this disctionary is:
        {"do": True,  # Should we model the transit
         'instrument_variable': False,  # Whether or not different instruemnt can have different transit model
         'all_instruments': {'model': 'batman'  #String refering to the transit model to use (can be 'pytransit' or 'batman')
                             },
         'instrument_specific': {'<instrument_full_name>': 'all_instruments' # all instrument or dictionary like the 'all_instruments' one
                                 }
         }
    ldmodel4instmodfname    : dict of dict of str
        Dictionary giving Limd darkening model to use for each instrument model and for each star
        Format: {"<instrument_model_name>: {"<star_name>": "<LD_model_name>"}
    LDs                     : dict of CoreLD
        Dictionary of subclasses of CoreLD instances providing the different limb-darkening models
        Format: {f"<star_name>_<LD model name>"": CoreLD_subclass instance, }
    parametrisation         : str
        string refering to the parametrisation to use
    SSE4instmodfname        : dict of dict of str int and float
        Dictionary giving the supersampling factor and the exposure time to use for each instrument model
        Format: {"instrument model name": {'supersamp': int_supersampling_factor, 'exptime': float_exposure_time}}
    star                    : Star
        Star object
    planets                 : dict of Planets
        Dictionary of Planet instance providing the planets in the system
        Format: {"planet name": Planet instance}
    tab                     : str
        String providing the space to put in front of each new line
    time_vec_name           : str
        Str used to designate the time vector
    l_time_vec_name         : str
        Str used to designate the list of time vectors
    function_builder        : FunctionBuilder
        FunctionBuilder instance

    Returns
    -------
    preambules  : dict of str
        Dictionary of string giving the preambule for the transit model for each function
    returns     : dict of list of str
        Dictionary of list of str giving the return for transit model for each function and each output
    """
    transit_imp = transit_model['all_instruments']['model']

    ########################
    # Initialise the outputs
    ########################
    preambules = {}
    returns = {}

    ########################################################################
    # Define the functions to populate and initialise entries in the outputs
    ########################################################################
    # Defines the lists of function shortnames
    l_whole_function_shortname = [function_whole_shortname, ]
    l_planet_function_shortname_ext = ["", "_tr"]
    l_planet_function_shortname = []
    d_l_function_shortname_4_planet = {}
    for planet in planets.values():
        d_l_function_shortname_4_planet[planet.get_name()] = []
        for planet_func_shortname_ext in l_planet_function_shortname_ext:
            l_planet_function_shortname.append(f"{get_function_planet_shortname(planet)}{planet_func_shortname_ext}")
            d_l_function_shortname_4_planet[planet.get_name()].append(f"{get_function_planet_shortname(planet)}{planet_func_shortname_ext}")
    l_function_shortname = l_whole_function_shortname + l_planet_function_shortname

    ##################################################
    # Initialise the new functions in function_builder
    ##################################################
    l_planet_func_shortname_ext_to_create = ["_tr"]
    for planet_func_shortname_ext in l_planet_func_shortname_ext_to_create:
        for planet in planets.values():
            function_builder.add_new_function(shortname=f"{get_function_planet_shortname(planet)}{planet_func_shortname_ext}")

    ##############
    # Add the time
    ##############
    for func_shortname in l_function_shortname:
        time_arg_name = add_time_argument(function_builder=function_builder, function_shortname=func_shortname,
                                          multi=multi, get_times_from_datasets=get_times_from_datasets,
                                          l_dataset=l_dataset, time_vec_name=time_vec_name, l_time_vec_name=l_time_vec_name,
                                          exist_ok=True)

    ############################################################
    # Initialise the preambule and return text for all functions
    ############################################################
    for func_shortname in l_function_shortname:
        preambules[func_shortname] = ""
        returns[func_shortname] = []
        for i_inputoutput in range(len(l_inst_model)):
            returns[func_shortname].append("")

    #############################################################
    # Add the parameters required for the model for all functions
    #############################################################
    # Add rhostar if needed
    if parametrisation == "Multis":
        for func_shortname in l_function_shortname:
            function_builder.add_parameter(parameter=star.rhostar, function_shortname=func_shortname, exist_ok=True)

    # Add the planet parameters: Rrat, ecosw, esinw, cosinc, P, tic and aR if needed
    for planet in planets.values():
        l_param = [planet.Rrat, planet.ecosw, planet.esinw, planet.P, planet.tic]
        if parametrisation != "Multis":
            l_param.append(planet.aR)
        for param in l_param:
            for func_shortname in l_whole_function_shortname + d_l_function_shortname_4_planet[planet.get_name()]:
                function_builder.add_parameter(parameter=param, function_shortname=func_shortname, exist_ok=True)

    # Add the LD coefficients
    for instmod in l_inst_model:
        for func_shortname in l_function_shortname:
            LD_mod_name = ldmodel4instmodfname[instmod.get_name(include_prefix=True, code_version=True, recursive=True)][star.code_name]
            LD_mod = LDs[star.code_name + "_" + LD_mod_name]
            for param in LD_mod.get_list_params(main=True):
                function_builder.add_parameter(parameter=param, function_shortname=func_shortname)

    ##############
    # Batman model
    ##############
    if transit_imp == "batman":
        ## Creation of the TransitParams instances and add them to the ldicts
        for planet in planets.values():
            for i_instmod, instmod in enumerate(l_inst_model):
                params_bat = TransitParams()
                params_bat.per = 1.   # orbital period
                params_bat.rp = 0.1   # planet radius(in stel radii)
                params_bat.a = 15.    # semi-major axis(in stel radii)
                params_bat.inc = 90.  # orbital inclination (in degrees)
                params_bat.ecc = 0.   # eccentricity
                params_bat.w = 90.    # long. of periastron (in deg.)
                time_arg_value = function_builder.get_ldict(function_shortname=function_whole_shortname)[time_arg_name]  # Time is the same for all function
                if multi:
                    t_mean = mean(time_arg_value[0])
                else:
                    t_mean = mean(time_arg_value)
                params_bat.t0 = t_mean
                LD_mod_name = ldmodel4instmodfname[i_instmod.get_name(include_prefix=True, code_version=True, recursive=True)][star.code_name]
                LD_mod = LDs[star.code_name + "_" + LD_mod_name]
                params_bat.limb_dark = LD_mod.ld_type  # LD model
                params_bat.u = LD_mod.init_LD_values  # LDC init val
                for func_shortname in l_whole_function_shortname + d_l_function_shortname_4_planet[planet.get_name()]:
                    function_builder.add_variable_to_ldict(variable_name=f"params_{planet.get_name()}_{instmod.full_code_name}",
                                                           variable_content=copy(params_bat), function_shortname=func_shortname, exist_ok=True)
        ## writing the preambule and return (First preambuless after returns)
        for planet in planets.values():
            planet_name = planet.get_name()
            for func_shortname in l_whole_function_shortname + d_l_function_shortname_4_planet[planet.get_name()]:
                ## preambule: planetary parameter conversions
                ecosw = function_builder.get_text_4_parameter(parameter=planet.ecosw, function_shortname=func_shortname)
                esinw = function_builder.get_text_4_parameter(parameter=planet.esinw, function_shortname=func_shortname)
                function_builder.add_variable_to_ldict(variable_name="sqrt", variable_content=sqrt, function_shortname=func_shortname, exist_ok=True)
                preambules[func_shortname] += f"{tab}ecc_{planet_name} = sqrt({ecosw} * {ecosw} + {esinw} * {esinw})\n"
                function_builder.add_variable_to_ldict(variable_name="getomega_deg_fast", variable_content=getomega_deg_fast, function_shortname=func_shortname, exist_ok=True)
                preambules[func_shortname] += f"{tab}omega_{planet_name} = getomega_deg_fast({ecosw}, {esinw})\n"
                cosinc = function_builder.get_text_4_parameter(parameter=planet.cosinc, function_shortname=func_shortname)
                function_builder.add_variable_to_ldict(variable_name="degrees", variable_content=degrees, function_shortname=func_shortname, exist_ok=True)
                function_builder.add_variable_to_ldict(variable_name="acos", variable_content=acos, function_shortname=func_shortname, exist_ok=True)
                preambules[func_shortname] += f"{tab}inc_{planet_name} = degrees(acos({cosinc}))\n"
                period = function_builder.get_text_4_parameter(parameter=planet.P, function_shortname=func_shortname)
                if parametrisation == "Multis":
                    rhostar = function_builder.get_text_4_parameter(parameter=star.rhostar, function_shortname=func_shortname)
                    function_builder.add_variable_to_ldict(variable_name="getaoverr", variable_content=getaoverr, function_shortname=func_shortname, exist_ok=True)
                    preambules[func_shortname] += f"{tab}aR_{planet_name} = getaoverr({period}, {rhostar}, ecc_{planet_name}, omega_{planet_name})\n"
                ## preambule: Modifing the parameter values in the TransitParams object
                tic = function_builder.get_text_4_parameter(parameter=planet.tic, function_shortname=func_shortname)
                Rrat = function_builder.get_text_4_parameter(parameter=planet.Rrat, function_shortname=func_shortname)
                if parametrisation == "Multis":
                    aR = f"aR_{planet_name}\n"
                else:
                    aR = function_builder.get_text_4_parameter(parameter=planet.aR, function_shortname=func_shortname)
                for i_inputoutput, (instmod, dst) in enumerate(zip(l_inst_model, l_dataset)):
                    instmod_fullname = instmod.full_code_name
                    preambules[func_shortname] += f"{tab}params_{planet_name}_{instmod_fullname}.t0 = {tic}\n"
                    preambules[func_shortname] += f"{tab}params_{planet_name}_{instmod_fullname}.per = {period}\n"
                    preambules[func_shortname] += f"{tab}params_{planet_name}_{instmod_fullname}.rp = {Rrat}\n"
                    preambules[func_shortname] += f"{tab}params_{planet_name}_{instmod_fullname}.inc = inc_{planet_name}\n"
                    preambules[func_shortname] += f"{tab}params_{planet_name}_{instmod_fullname}.ecc = ecc_{planet_name}\n"
                    preambules[func_shortname] += f"{tab}params_{planet_name}_{instmod_fullname}.w = omega_{planet_name}\n"
                    LD_mod_name = ldmodel4instmodfname[instmod.get_name(include_prefix=True, code_version=True, recursive=True)][star.code_name]
                    LD_mod = LDs[star.code_name + "_" + LD_mod_name]
                    ld_param_list = "["
                    for param in LD_mod.get_list_params(main=True):
                        ld_param_list += function_builder.get_text_4_parameter(parameter=param, function_shortname=func_shortname) + ", "
                    ld_param_list += "]"
                    preambules[func_shortname] += f"{tab}params_{planet_name}_{instmod_fullname}.u = {ld_param_list}\n"
                    preambules[func_shortname] += f"{tab}params_{planet_name}_{instmod_fullname}.limb_dark = '{LD_mod_name}'\n"
                    preambules[func_shortname] += f"{tab}params_{planet_name}_{instmod_fullname}.a = {aR}\n"""
                    # preambule: Create the TransitModel object
                    if get_times_from_datasets:
                        time_arg_value = function_builder.get_ldict(function_shortname=function_whole_shortname)[time_arg_name]
                        if multi:
                            time_vect_value = time_arg_value[i_inputoutput]
                        else:
                            time_vect_value = time_arg_value
                        supersamp = SSE4instmodfname.get_supersamp(instmod.get_name(include_prefix=True, code_version=True, recursive=True))
                        if supersamp > 1:
                            exptime = SSE4instmodfname.get_exptime(instmod.get_name(include_prefix=True, code_version=True, recursive=True))
                            kwargs_TransitModel = {"supersample_factor": supersamp, "exp_time": exptime}
                        else:
                            kwargs_TransitModel = {}
                        params_bat = function_builder.get_ldict(function_shortname=function_whole_shortname)[f"params_{planet_name}_{instmod_fullname}"]
                        m_bat = TransitModel(params_bat, time_vect_value, **kwargs_TransitModel)
                        function_builder.add_variable_to_ldict(variable_name=f"m_{planet_name}_{instmod_fullname}_dst{dst.number}",
                                                               variable_content=m_bat, function_shortname=func_shortname, exist_ok=False)
                    else:
                        if multi:
                            time_vect = f"{time_arg_name}[{i_inputoutput}]"
                        else:
                            time_vect = f"{time_arg_name}"
                        supersamp = SSE4instmodfname.get_supersamp(instmod.get_name(include_prefix=True, code_version=True, recursive=True))
                        if supersamp > 1:
                            exptime = SSE4instmodfname.get_exptime(instmod.get_name(include_prefix=True, code_version=True, recursive=True))
                            supersamp_text = f", supersample_factor={supersamp}, exp_time={exptime}"
                        else:
                            supersamp_text = ""
                        function_builder.add_variable_to_ldict(variable_name="TransitModel", variable_content=TransitModel, function_shortname=func_shortname, exist_ok=True)
                        preambules[func_shortname] += f"{tab}m_{planet_name}_{instmod_fullname}_dst{dst.number} = TransitModel(params_{planet_name}_{instmod_fullname}, {time_vect}{supersamp_text})\n"

                    ## writing the returns
                    if returns[func_shortname][i_inputoutput] == "":
                        pre_text = ""
                    else:
                        pre_text = " + "
                    returns[func_shortname][i_inputoutput] += f"{pre_text}m_{planet_name}_{instmod_fullname}_dst{dst.number}.light_curve(params_{planet_name}_{instmod_fullname}) - 1 "
    #################
    # Pytransit model
    #################
    elif transit_imp == "pytransit":
        ## writing the preambule and return (First preambuless after returns)
        for planet in planets.values():
            planet_name = planet.get_name()
            for func_shortname in l_whole_function_shortname + d_l_function_shortname_4_planet[planet.get_name()]:
                ## preambule: planetary parameter conversions
                ecosw = function_builder.get_text_4_parameter(parameter=planet.ecosw, function_shortname=func_shortname)
                esinw = function_builder.get_text_4_parameter(parameter=planet.esinw, function_shortname=func_shortname)
                function_builder.add_variable_to_ldict(variable_name="sqrt", variable_content=sqrt, function_shortname=func_shortname, exist_ok=True)
                preambules[func_shortname] += f"{tab}ecc_{planet_name} = sqrt({ecosw} * {ecosw} + {esinw} * {esinw})\n"
                function_builder.add_variable_to_ldict(variable_name="getomega_fast", variable_content=getomega_fast, function_shortname=func_shortname, exist_ok=True)
                preambules[func_shortname] += f"{tab}omega_{planet_name} = getomega_fast({esinw}, {ecosw})\n"
                cosinc = function_builder.get_text_4_parameter(parameter=planet.cosinc, function_shortname=func_shortname)
                function_builder.add_variable_to_ldict(variable_name="acos", variable_content=acos, function_shortname=func_shortname, exist_ok=True)
                preambules[func_shortname] += f"{tab}inc_{planet_name} = acos({cosinc})\n"
                period = function_builder.get_text_4_parameter(parameter=planet.P, function_shortname=func_shortname)
                if parametrisation == "Multis":
                    rhostar = function_builder.get_text_4_parameter(parameter=star.rhostar, function_shortname=func_shortname)
                    function_builder.add_variable_to_ldict(variable_name="getaoverr", variable_content=getaoverr, function_shortname=func_shortname, exist_ok=True)
                    function_builder.add_variable_to_ldict(variable_name="degrees", variable_content=degrees, function_shortname=func_shortname, exist_ok=True)
                    preambules[func_shortname] += f"{tab}aR_{planet_name} = getaoverr({period}, {rhostar}, ecc_{planet_name}, degrees(omega_{planet_name}))\n"
                # Get the text for the remaining planet parameters
                if parametrisation == "Multis":
                    aR = f"aR_{planet_name}\n"
                else:
                    aR = function_builder.get_text_4_parameter(parameter=planet.aR, function_shortname=func_shortname)
                tic = function_builder.get_text_4_parameter(parameter=planet.tic, function_shortname=func_shortname)
                Rrat = function_builder.get_text_4_parameter(parameter=planet.Rrat, function_shortname=func_shortname)
                for i_inputoutput, (instmod, dst) in enumerate(zip(l_inst_model, l_dataset)):
                    # Create the Model and add it the the ldict
                    LD_mod_name = ldmodel4instmodfname[i_instmod.get_name(include_prefix=True, code_version=True, recursive=True)][star.code_name]
                    LD_mod = LDs[star.code_name + "_" + LD_mod_name]
                    supersamp = SSE4instmodfname.get_supersamp(instmod.get_name(include_prefix=True, code_version=True, recursive=True))
                    if supersamp > 1:
                        exptime = SSE4instmodfname.get_exptime(instmod.get_name(include_prefix=True, code_version=True, recursive=True))
                        m_pytransit = MandelAgol(supersampling=supersamp, exptime=exptime, model=LD_mod.ld_type)
                    else:
                        m_pytransit = MandelAgol(supersampling=supersamp, exptime=exptime, model=LD_mod.ld_type)
                    function_builder.add_variable_to_ldict(variable_name=f"m_{instmod_fullname}",
                                                           variable_content=m_pytransit, function_shortname=func_shortname, exist_ok=False)
                    ## Writing the returns
                    if returns[func_shortname][i_inputoutput] == "":
                        pre_text = ""
                    else:
                        pre_text = " + "
                    if multi:
                        time_vect = f"{time_arg_name}[{i_inputoutput}]"
                    else:
                        time_vect = f"{time_arg_name}"
                    ld_param_list = "["
                    for param in LD_mod.get_list_params(main=True):
                        ld_param_list += function_builder.get_text_4_parameter(parameter=param, function_shortname=func_shortname) + ", "
                    ld_param_list += "]"
                    returns[func_shortname][i_inputoutput] += f"m_{instmod_fullname}.evaluate({time_vect}, {Rrat}, {ld_param_list}, {tic}, {period}, {aR}, inc_{planet_name}, ecc_{planet_name}, omega_{planet_name}) - 1 "
    ########################
    # No other model for now
    ########################
    else:
        raise ValueError(f"Transit model {transit_imp} is not recognized.")

    return preambules, returns


def get_phasecurve(multi, l_inst_model, phasecurve_model, dico_l_LD_parcont, dico_l_LD_param_list, parametrisation,
                   key_whole, key_param, SSE4instmodfname, star, planets, ext_plonly, arg_list, param_nb, ldict,
                   tab, did_transit,
                   rhostar, params_planet, params_planet_only, params_whole,
                   time_vec_name=time_vec, l_time_vec_name=l_time_vec,):
    """Provide the text for the phase curve part of the LC model text (preambule and return).

    Arguments
    ---------
    multi                   : bool
        True if the datasim function needs to give multiple outputs.
    l_inst_model            : list_of_Instrument_Model
        List of the instrument models instances for each output of the datasim function.
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
    dico_l_LD_parcont        : dict_of_list_of_LD
        Dictionary providing, for all functions specified by key_arglist, the list of limb darkening models
        (parameter container object) associated with the Instrument_Model instances in l_inst_model.
        Format of the dictionary:
        - key : key or keys specificied by key_arglist
        - value: List = [<LD parameter container for instrument1>, ...]
    dico_l_LD_param_list     : dict_of_list_of_str
        Dictionary providing, for all functions specified by key_arglist, the list of string which themself
        write the list of limb darkening parameters values associated with the Instrument_Model instances
        in l_inst_model.
        Format of the dictionary:
        - key : key or keys specificied by key_arglist
        - value: List = ["[<value for LD param1 for instrument1> , <value for LD param2 for instrument1>, ...]", ...]
    parametrisation          : str
        string refering to the parametrisation to use
    key_whole                : str
        Key used in arg_list for the function simulating the whole system (all planets together)
    key_param                : str
        Key used for the parameters entry of arg_list values
    SSE4instmodfname         : dict of dict of str int and float
        Dictionary giving the supersampling factor and the exposure time to use for each instrument model
        Format: {"instrument model name": {'supersamp': int_supersampling_factor, 'exptime': float_exposure_time}}
    star                     : Star object
        Star instance of the parent star
    planets                  : dict of Planets
        Dictionary of Planet instance providing the planets in the system
        Format: {"planet name": Planet instance}
    ext_plonly               : str
        extension to the planet name used for planet only model (without star, nor instrument)
    arg_list                 : dict_of_dict_of_list_of_str
        dictionary giving the arguments of the functions currently being produced with the following format:
        - key = str designating the function being built and provided by key_arglist.
        - value = dict with three str keys and values
            - <key_param>: empty list that will receive the full names of the parameters of the function (content of the param_vector)
            - <key_mand_kwargs>: empty list that will receive the mandatory keyword arguments (beside the param_vector)
            - <key_opt_kwargs>: empty list that will receive the optional keyword arguments
        If it's not added to ldict instead the arguments provided by arguments are going to be added to the key_mand_kwargs or key_opt_kwargs
        of sub-dictionaries specified by key_arglist.
        THIS DICTIONARY IS MODIFIED EVEN IF NOT RETURNED
    param_nb                 : dict_of_int
        dictionary giving the current number of free parameters in the function being produced.
        key = str key designating part of the system or the whole system
        value = int giving the current number of parameter in the model
        Format: {"name_of_function": int_current_nb_of_model_parameters_of_the_datasimulator}
        THIS DICTIONARY IS MODIFIED EVEN IF NOT RETURNED
    ldict                    : dict_of_dict
        Dictionary giving the dictionaries to be used as local dictionary argument of the exec functions.
        - key = str key designating part of the system or the whole system
        - value = dictionary
        THIS DICTIONARY IS MODIFIED EVEN IF NOT RETURNED
    tab                      : str
        String providing the space to put in front of each new line
    did_transit              : bool
        If True the transit model (pre) was alredy done
    rhostar                  : dict_of_str
        Dictionary providing the str to use in the function for rhostar for all function available in arg_list
        Format:
        - key: str designating the function being built and provided by key_arglist.
        - value: str to use for rhostar for this function
    params_planet            : dict_of_dict_of_str
        Dictionary providing the strs to use for the other orbital parameters and for the planet function (1planet+star+instrument)
        Format:
        - key: planet name
        - value: dict_of_str with the following format
            - key: Parameter full name
            - value: str to use for this parameter for this function
    params_planet_only       : dict_of_dict_of_str
        Dictionary providing the strs to use for the other orbital parameters and for the planet only function (1planet and nothing else)
        Format:
        - key: planet name
        - value: dict_of_str with the following format
            - key: Parameter full name
            - value: str to use for this parameter for this function
    params_whole             : dict_of_dict_of_str
        Dictionary providing the strs to use for the other orbital parameters and for the key_whole function ("whole system with all the planets")
        Format:
        - key: planet name
        - value: dict_of_str with the following format
            - key: Parameter full name
            - value: str to use for this parameter for this function
    time_vec_name       : str
        Str used to designate the time vector
    l_time_vec_name     : str
        Str used to designate the list of time vectors

    Returns
    -------
    preambule_pc_planet         : dict of str
        For each planet this dictionary give the preambule for the phasecurve model to be added to the datasimulator function
        of the planet model
    preambule_pc_planet_only    : dict of str
        For each planet this dictionary give the preambule for the phasecurve model to be added to the datasimulator function
        of the planet only model
    preambule_pc_whole          : str
        Preambule for the phase curve model to be added to the datasimulator function of the whole system model
    d_l_return_pl         : dict of list of str
        For each planet this dictionary give the list of the phasecurve models for each instrument
    d_l_return_pl_only    : dict of list of str
        For each planet this dictionary give the list of the phasecurve models planet only for each instrument
    l_pc_whole_planets  : list of str
        List of phasecurve model for all planets combined for each instrument
    """
    # dico to store_text for stellar params
    star_param_text = {}

    preambule_pl = {}
    preambule_pl_only = {}
    preambule_whole = ""
    d_l_return_pl = {}
    d_l_return_pl_only = {}
    l_return_whole = []

    for jj, planet in enumerate(planets.values()):

        planet_name = planet.get_name()

        preambule_pl[planet_name] = ""
        preambule_pl_only[planet_name] = ""
        d_l_return_pl[planet_name] = []
        d_l_return_pl_only[planet_name] = []

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
                    for ii, instmdl in enumerate(l_inst_model):
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
                            ret_pl = (f"{params_pl_inst}.lightcurve({l_time_vec_name}[{ii}]{lightcurve_kwargs}) - 1 ")
                        else:
                            ret_pl = (f"{params_pl_inst}.lightcurve({time_vec_name}{lightcurve_kwargs}) - 1 ")
                        ##########################################################################################################
                        # Fill the template for phase curve model returns for the different function planet, planet only and whole
                        ##########################################################################################################
                        # No need for case for same reason than above
                        if kk == 0:
                            d_l_return_pl[planet_name].append(ret_pl)
                            d_l_return_pl_only[planet_name].append(ret_pl)
                            if jj == 0:
                                l_return_whole.append(ret_pl)
                        else:
                            d_l_return_pl[planet_name] += "+ " + ret_pl
                            d_l_return_pl_only[planet_name] += "+ " + ret_pl
                            l_return_whole[ii] += "+ " + ret_pl
                else:
                    raise NotImplementedError(f"brightness_model {brightness_model} of spiderman is not implemented.")
            else:
                raise NotImplementedError(f"phasecurve model {pc_model} is not implemented.")
    return (preambule_pl, preambule_pl_only, preambule_whole,
            d_l_return_pl, d_l_return_pl_only, l_return_whole,
            )


def get_planet_inst_dst_ext(planet, inst_model, multi):
    """Return the extension to use for the name of spiderman param instance

    Arguments
    ---------
    planet      : Planet
        Planet instance to which the spiderman param instance will correspond
    inst_model  : Instrument_Model
        Instrument model instance to which the spiderman param instance will correspond
    multi       : bool

    Returns
    -------
    sp_param_ext    : string
        Extension to use for the name of spiderman param instance
    """
    if multi:
        sp_param_ext = f"_{planet.get_name()}_{inst_model.get_name(include_prefix=True, code_version=True, prefix_kwargs={'include_prefix': False, 'code_version': True})}"
    else:
        sp_param_ext = f"_{planet.get_name()}"
    return sp_param_ext


def get_decorrelation(multi, planets, l_inst_model, l_dataset,
                      arguments, decorrelation_config, dataset_db, param_nb, arg_list,
                      key_param, key_mand_kwargs, key_opt_kwargs, key_whole, ldict, ext_plonly, LCcat_model,
                      time_arg_name):
    """Provide the text for the decorrelation of the LC model text (return).

    It should provide the text for decorrelation model for all functions (planet, planet_only, whole)
    and separately for each instrument model and each part of the LC model to decorrelate.

    The output of this methods will be used by combine_lc_models when filling the template of the functions
    in datasim_creator_lc.

    Arguments
    ---------
    multi                   : bool
        True if the datasim function needs to give multiple outputs.
    planets                  : dict of Planets
        Dictionary of Planet instance providing the planets in the system
        Format: {"planet name": Planet instance}
    l_inst_model            : list_of_Instrument_Model
        List of the instrument models instances for each output of the datasim function. Each instrument model
        in this list is the instrument model which has to be used for the corresponding dataset provided in l_dataset.
    l_dataset               : list of Datasets
        List of the Dataset intances for each output of the datasim function. The instrument model to be used for
        use for each dataset is provided in l_inst_model.
    arguments               :
    decorrelation_config    :
    dataset_db              : DatasetDatabase
        Dataset database to access the dataset for the decorrelation.
    param_nb                : dict_of_int
        dictionary giving the current number of free parameters in the function being produced.
        key = str key designating part of the system or the whole system
        value = int giving the current number of parameter in the model
        Format: {"name_of_function": int_current_nb_of_model_parameters_of_the_datasimulator}
        THIS DICTIONARY IS MODIFIED EVEN IF NOT RETURNED
    arg_list                 : dict_of_dict_of_list_of_str
        dictionary giving the arguments of the functions currently being produced with the following format:
        - key = str designating the function being built and provided by key_arglist.
        - value = dict with three str keys and values
            - <key_param>: empty list that will receive the full names of the parameters of the function (content of the param_vector)
            - <key_mand_kwargs>: empty list that will receive the mandatory keyword arguments (beside the param_vector)
            - <key_opt_kwargs>: empty list that will receive the optional keyword arguments
        If it's not added to ldict instead the arguments provided by arguments are going to be added to the key_mand_kwargs or key_opt_kwargs
        of sub-dictionaries specified by key_arglist.
        THIS DICTIONARY IS MODIFIED EVEN IF NOT RETURNED
    key_param                : str
        Key used for the parameters entry of arg_list values
    key_mand_kwargs          : str
        Key used for the mandatory keyword argument entry of arg_list
    key_opt_kwargs           : str
        Key used for the optional keyword argument entry of arg_list
    key_whole                : str
        Key used in arg_list for the function simulating the whole system (all planets together)
    ldict                    : dict_of_dict
        Dictionary giving the dictionaries to be used as local dictionary argument of the exec functions.
        - key = str key designating part of the system or the whole system
        - value = dictionary
        THIS DICTIONARY IS MODIFIED EVEN IF NOT RETURNED
    ext_plonly               : str
        extension to the planet name used for planet only model (without star, nor instrument)
    LCcat_model              : LC_InstCat_Model
        LC_InstCat_Model instance for the current model
    time_arg_name            : str
        Str used to designate the time vector(s)

    Returns
    -------
    d_l_decorr_planet         : dict of list of dict
        dictionary which for each planet give the list which for each instrument gives the dictionary providing the decorrelation model for each part of the LC model
    d_l_decorr_planet_only    : dict of list of dict
        dictionary which for each planet give the list which for each instrument gives the dictionary providing the decorrelation model planet only for each part of the LC model
    l_decorr_whole            : list of dict
        list which for each instrument gives the dictionary providing the decorrelation model of the whole system for each part of the LC model
    """
    # Create the decorrelation models for each planet and planet_only functions
    d_l_decorr_planet = {}
    d_l_decorr_planet_only = {}
    for jj, planet in enumerate(planets.values()):
        d_l_decorr_planet[planet.get_name()] = []
        d_l_decorr_planet_only[planet.get_name()] = []
        for l_decorr, key_func in zip([d_l_decorr_planet[planet.get_name()], d_l_decorr_planet_only[planet.get_name()]],
                                      [f"{planet.get_name(include_prefix=False)}", f"{planet.get_name(include_prefix=False)}{ext_plonly}"]):
            for ii, inst_mod_obj in enumerate(l_inst_model):
                l_decorr.append({})
                l_dataset_name_instmod = [dst.dataset_name for i_dst, dst in enumerate(l_dataset) if l_inst_model[i_dst] == inst_mod_obj]
                if decorrelation_config[inst_mod_obj.full_name]["do"]:
                    for model_part, config_decorr_instmod_modelpart in decorrelation_config[inst_mod_obj.full_name]["what to decorrelate"].items():
                        l_decorr[ii][model_part] = LCcat_model.create_text_decorr(multi=multi, inst_mod_obj=inst_mod_obj, idx_inst_mod_obj=ii, l_dataset_name_instmod=l_dataset_name_instmod,
                                                                                  dataset_db=dataset_db,
                                                                                  decorrelation_config_instmod=config_decorr_instmod_modelpart,
                                                                                  param_nb=param_nb, arg_list=arg_list,
                                                                                  key_param=key_param,
                                                                                  key_mand_kwargs=key_mand_kwargs, key_opt_kwargs=key_opt_kwargs,
                                                                                  key_func=key_func, ldict=ldict, model_part=model_part,
                                                                                  time_arg_name=time_arg_name)
    # Create the decorrelation models for the whole system
    l_decorr_whole = []
    for ii, inst_mod_obj in enumerate(l_inst_model):
        l_decorr_whole.append({})
        if decorrelation_config[inst_mod_obj.full_name]["do"]:
            l_dataset_name_instmod = [dst.dataset_name for i_dst, dst in enumerate(l_dataset) if l_inst_model[i_dst] == inst_mod_obj]
            for model_part, config_decorr_instmod_modelpart in decorrelation_config[inst_mod_obj.full_name]["what to decorrelate"].items():
                l_decorr_whole[ii][model_part] = LCcat_model.create_text_decorr(multi=multi, inst_mod_obj=inst_mod_obj, idx_inst_mod_obj=ii, l_dataset_name_instmod=l_dataset_name_instmod,
                                                                                dataset_db=dataset_db,
                                                                                decorrelation_config_instmod=config_decorr_instmod_modelpart,
                                                                                param_nb=param_nb, arg_list=arg_list,
                                                                                key_param=key_param,
                                                                                key_mand_kwargs=key_mand_kwargs, key_opt_kwargs=key_opt_kwargs,
                                                                                key_func=key_whole, ldict=ldict, model_part=model_part,
                                                                                time_arg_name=time_arg_name)
    # # Create the decorrelation models for the whole system
    # l_decorr_only_whole = []
    # for ii, inst_mod_obj in enumerate(l_inst_model):
    #     l_decorr_only_whole.append({})
    #     if decorrelation_config[inst_mod_obj.full_name]["do"]:
    #         l_dataset_name_instmod = [dst.dataset_name for i_dst, dst in enumerate(l_dataset) if l_inst_model[i_dst] == inst_mod_obj]
    #         for model_part, config_decorr_instmod_modelpart in decorrelation_config[inst_mod_obj.full_name]["what to decorrelate"].items():
    #             key_func_dec_only = f"dec_{model_part}"
    #             param_nb[key_func_dec_only] = 0
    #             arg_list[]
    #             l_decorr_only_whole[ii][model_part] = LCcat_model.create_text_decorr(multi=multi, inst_mod_obj=inst_mod_obj, idx_inst_mod_obj=ii, l_dataset_name_instmod=l_dataset_name_instmod,
    #                                                                                  dataset_db=dataset_db,
    #                                                                                  decorrelation_config_instmod=config_decorr_instmod_modelpart,
    #                                                                                  param_nb=param_nb, arg_list=arg_list,
    #                                                                                  key_param=key_param,
    #                                                                                  key_mand_kwargs=key_mand_kwargs, key_opt_kwargs=key_opt_kwargs,
    #                                                                                  key_func=f"dec_{model_part}", ldict=ldict, model_part=model_part,
    #                                                                                  time_arg_name=time_arg_name)
    return d_l_decorr_planet, d_l_decorr_planet_only, l_decorr_whole  # , l_decorr_only_whole


def combine_return_models(which_model, stellar_var, transit, phasecurve, decorrelation):
    """Combine the different component of the lc model including the decorrelation if necessary.

    This function creates the return for one datasimulator only and one instrument model object only

    Arguments
    ---------
    which_model     : str
        String saying which model you want to create. Possibilities are
        'full' -> full model including all components
        'pl_only' -> Only the planetary components (stellar_var and decorrelation are not used)
        'decorrelation' -> Only the decorrelation components (only decorrelation is used)
    stellar_var     : str
        text providing the additive out of transit variations due to the host star (oot_var)
    transit         : str
        text providing the transit model component of the planet(s) contribution to the LC model
    phasecurve      : str
        text providing the phasecurve model component of the planet(s) contribution to the LC model
    decorrelation   : dict_of_str
        Text providing the decorrelation model component. There are different ways to decorrelate the
        LC model and these ways are designed with strings. For now the ways implemented are
        ["stellarflux", ]
        Format:
        - key : str
            Giving which part of the model to apply the decorrelation to
        - value : str
            Giving the text of the decorrelation for this part of the model.
            This text should include several decorrelation variables and several decorrelation types
            (e.g. linear) if there are several.

    Returns
    -------
    text_return : str
        Text of the return for one datasim lc function.
    """
    if which_model == 'full':
        tr_plusornot_pl = "+ " if transit != "" else ""
        pc_plusornot_pl = "+ " if phasecurve != "" else ""
        if "stellarflux" in decorrelation:
            decorrelation_stellar_flux = " + (" + decorrelation["stellarflux"] + ")"
        else:
            decorrelation_stellar_flux = ""
        return_text = f"(1 {stellar_var}) * (1 {decorrelation_stellar_flux} {tr_plusornot_pl + transit}{pc_plusornot_pl + phasecurve}), "
    elif which_model == 'pl_only':
        pc_plusornot_plonly = "+ " if ((transit != "") and (phasecurve != "")) else ""
        return_text = f"{transit}{pc_plusornot_plonly + phasecurve}, "
    elif which_model == 'decorrelation':
        return_text = decorrelation + ", "
    else:
        raise ValueError(f"which_model should be in ['full', 'pl_only', 'decorrelation'] got {which_model}")
    return return_text
