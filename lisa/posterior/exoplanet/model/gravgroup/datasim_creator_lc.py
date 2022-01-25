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
# from copy import deepcopy, copy
from math import acos, degrees, sqrt
from numpy import ones_like, inf, mean, pi, sin, cos
# from collections import Iterable

from batman import TransitModel, TransitParams
# from pytransit import MandelAgol  # Temporarily? remove pytransit from the available rv_models
from spiderman import ModelParams

from . import get_function_planet_shortname
from ....core import function_whole_shortname
from ....core.model import par_vec_name
from ....core.model.datasim_docfunc import DatasimDocFunc
from ....core.model.datasimulator_toolbox import check_datasets_and_instmodels
from ....core.model.datasimulator_timeseries_toolbox import add_time_argument, time_vec, l_time_vec
from .....tools.function_from_text_toolbox import FunctionBuilder  # , argskwargs
from .....posterior.exoplanet.model.convert import getaoverr, getomega_fast, getomega_deg_fast


## Logger object
logger = getLogger()


template_return = """
{tab}try:
{tab}    return {returns}
{tab}except RuntimeError:
{tab}    return {returns_except}
"""
tab = "    "
template_return = dedent(template_return)


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
        func_full_name_MultiOrDst_ext = f"{l_dataset[0].dataset_code_name}"
    func_builder.set_function_fullname(full_name=f"LC_sim_{function_whole_shortname}_{func_full_name_MultiOrDst_ext}", shortname=function_whole_shortname)
    l_function_planet_shortname = [get_function_planet_shortname(planet) for planet in planets.values()]
    for function_shortname in l_function_planet_shortname:
        func_builder.add_new_function(shortname=function_shortname)
        func_builder.set_function_fullname(full_name=f"LC_sim_{function_shortname}_{func_full_name_MultiOrDst_ext}", shortname=function_shortname)

    #####################################
    # Define the templates of the function
    #####################################
    # Initialise function_name and template_function the template function name and the template function text
    # function_name = ("LCsim_{{object}}_{instmod_fullname}{dst_ext}"
    #                  "".format(instmod_fullname=inst_model_full_name, dst_ext=dst_ext))
    # template_return = """
    # {{tab}}try:
    # {{tab}}    return {{returns}}
    # {{tab}}except RuntimeError:
    # {{tab}}    return {{returns_except}}
    # """
    # tab = "    "
    # template_return = dedent(template_return)

    #########################################################################################
    # Create the text of what to return when condition is met or the RuntimeError is catched
    ########################################################################################

    ########################
    # Produce Transit models
    ########################
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

    returns_tr = get_transit(multi=multi, l_inst_model=l_inst_model, l_dataset=l_dataset, get_times_from_datasets=get_times_from_datasets,
                             transit_model=transit_model, ldmodel4instmodfname=ldmodel4instmodfname, LDs=LDs,
                             parametrisation=parametrisation, SSE4instmodfname=SSE4instmodfname, star=star, planets=planets,
                             tab=tab, time_vec_name=time_vec, l_time_vec_name=l_time_vec, function_builder=func_builder,
                             ext_func_fullname=func_full_name_MultiOrDst_ext,
                             )

    ############################
    # Produce phase curve models
    ############################
    returns_pc = get_phasecurve(multi=multi, l_inst_model=l_inst_model, l_dataset=l_dataset, get_times_from_datasets=get_times_from_datasets,
                                phasecurve_model=phasecurve_model, parametrisation=parametrisation, SSE4instmodfname=SSE4instmodfname,
                                star=star, planets=planets,
                                tab=tab, time_vec_name=time_vec, l_time_vec_name=l_time_vec, function_builder=func_builder,
                                ext_func_fullname=func_full_name_MultiOrDst_ext,
                                )

    #####################################################################
    # Get the condition text for the whole system function and the planet
    #####################################################################
    # the transit and phase curve only function already receive the conditions in the get_transit and get_phasecurve functions
    for func_shortname in [function_whole_shortname, ]:
        l_planet = list(planets.values())
        get_condition(multi=multi, l_inst_model=l_inst_model, l_planet=l_planet, parametrisation=parametrisation,
                      tab=tab, time_vec_name=time_vec, l_time_vec_name=l_time_vec, function_builder=func_builder,
                      function_shortname=func_shortname)

    for planet in planets.values():
        func_shortname = f"{get_function_planet_shortname(planet)}"
        get_condition(multi=multi, l_inst_model=l_inst_model, l_planet=[planet, ], parametrisation=parametrisation,
                      tab=tab, time_vec_name=time_vec, l_time_vec_name=l_time_vec, function_builder=func_builder,
                      function_shortname=func_shortname)

    ###########################
    # Produce the decorrelation
    ###########################
    d_l_d_decorr = get_decorrelation(multi=multi, planets=planets, l_inst_model=l_inst_model, l_dataset=l_dataset,
                                     get_times_from_datasets=get_times_from_datasets, decorrelation_config=decorrelation_config,
                                     dataset_db=dataset_db, LCcat_model=LCcat_model, tab=tab, time_vec_name=time_vec,
                                     l_time_vec_name=l_time_vec, function_builder=func_builder, l_function_shortname=[function_whole_shortname, ],
                                     ext_func_fullname=func_full_name_MultiOrDst_ext)

    #####################################
    # Produce instrumental variations models
    #####################################
    ## Get the d_l_inst_var and add the t_ref(s) to the list of arguments for the functions
    # d_l_inst_var is the list of strings giving the string representation of the out of transit variation model
    # for each couple instrument model - dataset in l_inst_model and l_dataset.
    # Format: ["oot model", ]
    d_l_inst_var = get_instvar(l_inst_model=l_inst_model, l_dataset=l_dataset, multi=multi,
                               function_builder=func_builder, l_function_shortname=[function_whole_shortname, ], ext_func_fullname=func_full_name_MultiOrDst_ext,
                               get_times_from_datasets=get_times_from_datasets, tab=tab, time_vec_name=time_vec, l_time_vec_name=l_time_vec)

    #######################################################################
    # Finalise the functions combining different outputs (whole and planet)
    #######################################################################
    # Function of the whole system
    for func_shortname in [function_whole_shortname, ]:
        combine_return_models(multi=multi, l_inst_model=l_inst_model, time_vec_name=time_vec, l_time_vec_name=l_time_vec,
                              reference_flux_level=1, tab=tab, function_builder=func_builder, function_shortname=func_shortname,
                              inst_var=d_l_inst_var.get(func_shortname, None), transit=returns_tr.get(func_shortname, None),
                              phasecurve=returns_pc.get(func_shortname, None), decorrelation=d_l_d_decorr.get(func_shortname, None))

    # Function of the planets only
    for func_shortname in l_function_planet_shortname:
        combine_return_models(multi=multi, l_inst_model=l_inst_model, time_vec_name=time_vec, l_time_vec_name=l_time_vec,
                              reference_flux_level=0, tab=tab, function_builder=func_builder, function_shortname=func_shortname,
                              inst_var=d_l_inst_var.get(func_shortname, None), transit=returns_tr.get(func_shortname, None),
                              phasecurve=returns_pc.get(func_shortname, None), decorrelation=d_l_d_decorr.get(func_shortname, None))

    # #############################################
    # # Fill the functions template for each planet
    # #############################################
    # for jj, planet in enumerate(planets.values()):
    #     # Get the returns text for each planet
    #     returns_pl = ""
    #     returns_pl_only = ""
    #     for (oot_var_planet, oot_var_planet_only, planet_tr, planet_only_tr, planet_pc, planet_only_pc,
    #          decorr_planet, decorr_planet_only
    #          ) in zip(d_l_inst_var[planet.get_name()], d_l_inst_var[planet.get_name() + ext_plonly],
    #                   d_l_tr_ret_planet[planet.get_name()], d_l_tr_ret_planet_only[planet.get_name()],
    #                   d_l_pc_ret_planet[planet.get_name()], d_l_pc_ret_planet_only[planet.get_name()],
    #                   d_l_decorr_planet[planet.get_name()], d_l_decorr_planet_only[planet.get_name()]):
    #
    #         returns_pl += combine_return_models(which_model="full", stellar_var=oot_var_planet, transit=planet_tr, phasecurve=planet_pc,
    #                                             decorrelation=decorr_planet)
    #         returns_pl_only += combine_return_models(which_model="pl_only", stellar_var=oot_var_planet_only, transit=planet_only_tr, phasecurve=planet_only_pc,
    #                                                  decorrelation=decorr_planet_only)
    #     if not(multi):  # If multi, the coma in the end ensure that the output is always a tuple (even there is actually just one dataset). This is very important for output of datasim_all_datasets.
    #         returns_pl = returns_pl[:-2]
    #         returns_pl_only = returns_pl_only[:-2]
    #
    #     # Finalise the text of planet LC simulator functions
    #     if argskwargs not in arguments:
    #         arguments = add_argskwargs_argument(arguments)
    #     text_def_func[planet.get_name()] = (template_function.format(object=planet.get_name(),
    #                                                                  preambule_tr=preambule_tr_planet[planet.get_name()],
    #                                                                  preambule_pc=preambule_pc_planet[planet.get_name()],
    #                                                                  condition=condition_planet,
    #                                                                  arguments=arguments, returns=returns_pl,
    #                                                                  returns_except=error_return,
    #                                                                  tab=tab))
    #     text_def_func[planet.get_name() + ext_plonly] = (template_function.format(object=planet.get_name() + ext_plonly,
    #                                                                               preambule_tr=preambule_tr_planet_only[planet.get_name()],
    #                                                                               preambule_pc=preambule_pc_planet_only[planet.get_name()],
    #                                                                               condition=condition_planet_only,
    #                                                                               arguments=arguments,
    #                                                                               returns=returns_pl_only,
    #                                                                               returns_except=error_return,
    #                                                                               tab=tab))
    #     # logger.debug("text of {object} LC simulator function :\n{text_func}"
    #     #              "".format(object=planet.get_name(), text_func=text_def_func[planet.get_name()]))

    # ##################################################
    # # Fill the functions template for the whole system
    # ##################################################
    # # Get the return text for the whole system
    # returns_whole = ""
    # for oot_var, whole_transit, whole_phasecurve, whole_decorr in zip(d_l_inst_var[key_whole], l_tr_ret_whole_planets, l_pc_ret_whole_planets, l_decorr_whole):
    #     returns_whole += combine_return_models(which_model="full", stellar_var=oot_var, transit=whole_transit, phasecurve=whole_phasecurve,
    #                                            decorrelation=whole_decorr)
    # if not(multi):  # If multi, the coma in the end ensure that the output is always a tuple (even there is actually just one dataset). This is very important for output of datasim_all_datasets.
    #     returns_whole = returns_whole[:-2]
    # # Finalise the text of whole system LC simulator function
    # text_def_func[key_whole] = (template_function.
    #                             format(object=key_whole, preambule_tr=preambule_tr_whole, preambule_pc=preambule_pc_whole, condition=condition_whole,
    #                                    arguments=arguments, returns=returns_whole, returns_except=error_return,
    #                                    tab=tab))

    ###################################
    # Execute the text of all functions
    ###################################
    # Create and fill the output dictionnary containing the datasimulators functions.
    # dico_docf = dict.fromkeys(text_def_func.keys(), None)
    dico_docf = {}
    for func_shortname in func_builder.l_function_shortname:
        logger.debug(f"text of {func_shortname} LC simulator function :\n{func_builder.get_full_function_text(shortname=func_shortname)}")
        exec(func_builder.get_full_function_text(shortname=func_shortname), func_builder._get_ldict(function_shortname=func_shortname))
        params_model = [param.full_name for param in func_builder.get_free_parameter_vector(function_shortname=func_shortname)]
        dico_param_nb = {nb: param for nb, param in enumerate(params_model)}
        if len(func_builder.get_l_mandatory_argument(function_shortname=func_shortname)) > 0:
            mand_kwargs = str(func_builder.get_l_mandatory_argument(function_shortname=func_shortname))
        else:
            mand_kwargs = None
        if len(func_builder.get_l_mandatory_argument(function_shortname=func_shortname)) > 0:
            opt_kwargs = str(func_builder.get_l_mandatory_argument(function_shortname=func_shortname))
        else:
            opt_kwargs = None
        logger.debug(f"Parameters for {func_shortname} LC simulator function :\n{dico_param_nb}")
        dico_docf[func_shortname] = DatasimDocFunc(function=func_builder._get_ldict(function_shortname=func_shortname)[func_builder.get_function_fullname(shortname=func_shortname)],
                                                   params_model=params_model,
                                                   inst_cat=instcat_docf,
                                                   include_dataset_kwarg=get_times_from_datasets,
                                                   mand_kwargs=mand_kwargs,
                                                   opt_kwargs=opt_kwargs,
                                                   inst_model_fullname=instmod_docf,
                                                   dataset=dtsts_docf)
    return dico_docf


def get_instvar(l_inst_model, l_dataset, multi, get_times_from_datasets, tab, time_vec_name, l_time_vec_name,
                function_builder, l_function_shortname, ext_func_fullname):
    """Get the instrumental variation contribution to the light-curve

    Arguments
    ---------
    l_inst_model            : list_of_Instrument_Model
        Checked list of Instrument_Model instance(s).
    l_dataset               : list_of_Dataset
        Checked list of Dataset instance(s).
    multi                   : bool
        True if the datasim function needs to give multiple outputs.
    get_times_from_datasets : bool
        True the datasets should be used to extract the time vectors
    tab                     : str
        String providing the space to put in front of each new line
    time_vec_name           : str
        Str used to design the time vector
    l_time_vec_name         : str
        Str used to design the list of time vector
    function_builder        : FunctionBuilder
        Function builder instance
    l_function_shortname    : list of str
        List of the short name of the functions for which you want to add the instrument variation component
    ext_func_fullname       : str
        Extension to add and the end of the full name of the function simulating the instrumental variation only
        which is defined by this function in the function_builder

    Returns
    -------
    returns : dict of list_of_string
        Dictionary providing, for all functions specified by l_function_shortname, the list of the string representations
        of the instrumental variations model for each couple instrument model - dataset in l_inst_model and l_dataset.
        Format of the dictionary:
        - key : key or keys specificied by l_function_shortname
        - value: List = ["<inst variation model for instrument1 and dataset1>", ...]
    """
    ########################
    # Initialise the outputs
    ########################
    returns = {}

    #################################################
    # Initialise the new function in function_builder
    #################################################
    # Extension for the shortname of the function that do the decorrelation only model
    inst_var_func_shortname = "inst_var"
    function_builder.add_new_function(shortname=inst_var_func_shortname)
    function_builder.set_function_fullname(full_name=f"LC_sim_{inst_var_func_shortname}{ext_func_fullname}", shortname=inst_var_func_shortname)

    ########################################
    # Update the list of function to address
    ########################################
    l_function_shortname += [inst_var_func_shortname, ]

    for function_shortname in l_function_shortname:
        returns[function_shortname] = []
        # For each instrument model and dataset, ...
        for ii, instmdl in enumerate(l_inst_model):
            returns[function_shortname].append("")
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
                            if returns[function_shortname][ii] == "":
                                returns[function_shortname][ii] += f"{text_instvar_param}"
                            else:
                                returns[function_shortname][ii] += f" + {text_instvar_param}"
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
                                function_builder.add_variable_to_ldict(variable_name=timeref_instmod, variable_content=timeref_instmod_value, function_shortname=function_shortname)
                            # ..., add the end of this order's contribution to the text of the instruments variations, ...
                            # add the time argument
                            time_arg_name = add_time_argument(function_builder=function_builder, function_shortname=function_shortname,
                                                              multi=multi, get_times_from_datasets=get_times_from_datasets,
                                                              l_dataset=l_dataset, time_vec_name=time_vec_name, l_time_vec_name=l_time_vec_name,
                                                              exist_ok=True)
                            if order == 1:
                                if multi:
                                    returns[function_shortname][ii] += f" * ({time_arg_name}[{ii}] - {timeref_instmod})"
                                else:
                                    returns[function_shortname][ii] += f" * ({time_arg_name} - {timeref_instmod})"
                            elif order > 1:
                                if multi:
                                    returns[function_shortname][ii] += (f" * ({time_arg_name}[{ii}] - {timeref_instmod})**{order}")
                                else:
                                    returns[function_shortname][ii] += (f" * ({time_arg_name} - {timeref_instmod})**{order}")
                        # # If the is no contribution to the oot of transit variation from this order
                        # # add only a space.
                        # elif value_not0 and order == 0:
                        #     returns[function_shortname][ii] += " "

    #####################################
    # Finalize the inst_var only function
    #####################################
    for func_shortname in [inst_var_func_shortname, ]:
        function_builder.add_to_body_text(text=f"{tab}return {str(returns.pop(func_shortname)).strip('[]')}", function_shortname=func_shortname)

    return returns


def get_LD_parcont_and_param(l_inst_model, ldmodel4instmodfname, star, l_planet_name, LDs, function_builder, l_function_shortname):
    """Return the list of LD param container name, instance and parameter string list for a given star.

    NOT USED HERE BUT STILL IMPORTED IN THE DYNAMICAL (REBOUND) MODEL.

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


# def define_orbital_params(star, planets, parametrisation, function_builder):
#     """Define the orbital parameters as model parameters in the function builder
#
#     Arguments
#     ---------
#     star                        : Star
#         Star object
#     planets                     : dict of Planets
#         Dictionary of Planet instance providing the planets in the system
#         Format: {"planet name": Planet instance}
#     parametrisation             : str
#         string refering to the parametrisation to use
#     function_builder            : FunctionBuilder
#         Object which help building the function
#
#     TBR
#     Returns
#     -------
#     rhostar             : dict_of_str
#         Dictionary providing the str to use in the function for rhostar for all function available in arg_list
#         Format:
#         - key: str designating the function being built and provided by key_arglist.
#         - value: str to use for rhostar for this function
#     params_whole        : dict_of_dict_of_str
#         Dictionary providing the strs to use for the other orbital parameters and for the key_whole function ("whole system with all the planets")
#         Format:
#         - key: planet name
#         - value: dict_of_str with the following format
#             - key: Parameter full name
#             - value: str to use for this parameter for this function
#     params_planet       : dict_of_dict_of_str
#         Dictionary providing the strs to use for the other orbital parameters and for the planet function (1planet+star+instrument)
#         Format:
#         - key: planet name
#         - value: dict_of_str with the following format
#             - key: Parameter full name
#             - value: str to use for this parameter for this function
#     params_planet_only  : dict_of_dict_of_str
#         Dictionary providing the strs to use for the other orbital parameters and for the planet only function (1planet and nothing else)
#         Format:
#         - key: planet name
#         - value: dict_of_str with the following format
#             - key: Parameter full name
#             - value: str to use for this parameter for this function
#     """
#     l_function_shortname_add_rho = [function_whole_shortname, ]
#     for planet in planets.values():
#         l_function_shortname_add_rho.extend([planet.get_name(), planet.get_name() + ext_plonly])
#     # Add the stellar density the model parameter vectors
#     if parametrisation == "Multis":
#         for function_shortname in l_function_shortname_add_rho:
#             function_builder.add_parameter(parameter=star.rho, function_shortname=function_shortname)
#
#     # Create the text for each planet parameter for the current planet model (planet and planet_only) and for the whole system.
#     for planet in planets.values():
#         l_param = [planet.ecosw, planet.esinw, planet.cosinc, planet.tic, planet.P]
#         if parametrisation != "Multis":
#             l_param.append(planet.aR)
#         for function_shortname in [function_whole_shortname, planet.get_name(), planet.get_name() + ext_plonly]:
#             for param in l_param:
#                 function_builder.add_parameter(parameter=param, function_shortname=function_shortname)

# def get_conditions(multi, l_inst_model, planets, parametrisation, tab, time_vec_name, l_time_vec_name, function_builder):
#     """
#     Return the text related to the condition to test if the planet goes into the star
#
#     Arguments
#     ---------
#     multi                   : bool
#         True if the datasim function needs to give multiple outputs.
#     l_inst_model            : list_of_Instrument_Model
#         Checked list of Instrument_Model instance(s).
#     planets                 : dict of Planets
#         Dictionary of Planet instance providing the planets in the system
#         Format: {"planet name": Planet instance}
#     parametrisation         : str
#         string refering to the parametrisation to use
#     tab                     : str
#         String providing the space to put in front of each new line
#     time_vec_name           : str
#         Str used to design the time vector
#     l_time_vec_name         : str
#         Str used to design the list of time vector
#     function_builder        : FunctionBuilder
#         Function builder instance
#     """
#     ##############################
#     # Do the Model for each planet
#     ##############################
#     for planet in planets.values():
#         planet_name = planet.get_name()
#
#         ########################################################################
#         # Define the functions to populate and initialise entries in the outputs
#         ########################################################################
#         # Defines the lists of function shortnames and add the new transit only function into the function builder
#         l_whole_function_shortname = [function_whole_shortname, ]
#         l_planet_function_shortname_ext = ["", "_tr", "_pc"]
#         l_planet_function_shortname = []
#         for planet_func_shortname_ext in l_planet_function_shortname_ext:
#             l_planet_function_shortname.append(f"{get_function_planet_shortname(planet)}{planet_func_shortname_ext}")
#         l_function_shortname_4_planet = l_whole_function_shortname + l_planet_function_shortname
#
#         for func_shortname in l_function_shortname_4_planet:
#
#             if function_builder.is_function(shortname=func_shortname):
#                 error_return = get_catchederror_return(multi=multi, l_inst_model=l_inst_model, time_vec_name=time_vec_name,
#                                                        l_time_vec_name=l_time_vec_name, function_builder=function_builder,
#                                                        function_shortname=func_shortname)
#                 # In all functions currently considered aR should already exists, but the best would be
#                 # to check and only do the condition if it doesn or if there is already the ingredients to
#                 # compute it
#                 if parametrisation == "Multis":
#                     aR = f"aR_{planet_name}"
#                 else:
#                     aR = function_builder.get_text_4_parameter(parameter=planet.aR, function_shortname=func_shortname)
#                 if function_builder.is_parameter(parameter=planet.Rrat, function_shortname=func_shortname):
#                     Rrat = function_builder.get_text_4_parameter(parameter=planet.Rrat, function_shortname=func_shortname)
#                     function_builder.add_to_body_text(text=f"{tab}condition_{planet_name} = ({aR} < ((1.5 / (1 - ecc_{planet_name})) + {Rrat}))\n", function_shortname=func_shortname)
#                 else:
#                     function_builder.add_to_body_text(text=f"condition_{planet_name} = ({aR} < (1.5 / (1 - ecc_{planet_name})))\n", function_shortname=func_shortname)
#                 if func_shortname in l_whole_function_shortname:
#                     function_builder.add_to_body_text(text=f"{tab}condition = condition or condition_{planet_name}\n", function_shortname=func_shortname)
#                 else:
#                     function_builder.add_to_body_text(text=f"{tab}if condition_{planet_name}:\n", function_shortname=func_shortname)
#                     function_builder.add_to_body_text(text=f"{tab}    return {error_return}\n", function_shortname=func_shortname)
#     for func_shortname in l_whole_function_shortname:
#         function_builder.add_to_body_text(text=f"{tab}if condition:\n", function_shortname=func_shortname)
#         function_builder.add_to_body_text(text=f"{tab}    return {error_return}\n", function_shortname=func_shortname)


def get_condition(multi, l_inst_model, l_planet, parametrisation, tab, time_vec_name, l_time_vec_name,
                  function_builder, function_shortname):
    """
    Return the text related to the condition to test if the planet goes into the star

    Arguments
    ---------
    multi                   : bool
        True if the datasim function needs to give multiple outputs.
    l_inst_model            : list_of_Instrument_Model
        Checked list of Instrument_Model instance(s).
    l_planet                : List of Planets
        List of Planet instance providing the planets treated in the function
    parametrisation         : str
        string refering to the parametrisation to use
    tab                     : str
        String providing the space to put in front of each new line
    time_vec_name           : str
        Str used to design the time vector
    l_time_vec_name         : str
        Str used to design the list of time vector
    function_builder        : FunctionBuilder
        Function builder instance
    function_shortname      : str
        Short name of the function being built
    """
    error_return = get_catchederror_return(multi=multi, l_inst_model=l_inst_model, time_vec_name=time_vec_name,
                                           l_time_vec_name=l_time_vec_name, function_builder=function_builder,
                                           function_shortname=function_shortname)
    more_than_1_planet = len(l_planet) > 1
    for planet in l_planet:
        planet_name = planet.get_name()
        # In all functions currently considered aR should already exists, but the best would be
        # to check and only do the condition if it doesn or if there is already the ingredients to
        # compute it
        if parametrisation == "Multis":
            aR = f"aR_{planet_name}"
        else:
            aR = function_builder.get_text_4_parameter(parameter=planet.aR, function_shortname=function_shortname)
        if function_builder.is_parameter(parameter=planet.Rrat, function_shortname=function_shortname):
            Rrat = function_builder.get_text_4_parameter(parameter=planet.Rrat, function_shortname=function_shortname)
            function_builder.add_to_body_text(text=f"{tab}condition_{planet_name} = ({aR} < ((1.5 / (1 - ecc_{planet_name})) + {Rrat}))\n", function_shortname=function_shortname)
        else:
            function_builder.add_to_body_text(text=f"condition_{planet_name} = ({aR} < (1.5 / (1 - ecc_{planet_name})))\n", function_shortname=function_shortname)
    if more_than_1_planet:
        condition_text = [f"condition_{planet.get_name()}" for planet in l_planet].join(" or ")
    else:
        condition_text = f"condition_{planet_name}"
    function_builder.add_to_body_text(text=f"{tab}if {condition_text}:\n", function_shortname=function_shortname)
    function_builder.add_to_body_text(text=f"{tab}    return {error_return}\n", function_shortname=function_shortname)


def get_catchederror_return(multi, l_inst_model, time_vec_name, l_time_vec_name, function_builder, function_shortname):
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
    function_builder    : FunctionBuilder
        Function builder instance
    function_shortname  : str
        Short name of the function being built

    Returns
    -------
    error_return : str
        Text of what to return if an error is catched
    """
    function_builder.add_variable_to_ldict(variable_name="ones_like", variable_content=ones_like, function_shortname=function_shortname, exist_ok=False)
    function_builder.add_variable_to_ldict(variable_name="inf", variable_content=inf, function_shortname=function_shortname, exist_ok=False)

    l_returns = []
    for i_instmodel in range(len(l_inst_model)):
        if multi:
            l_returns.append(f"ones_like({l_time_vec_name}[{i_instmodel}]) * (- inf)")
        else:
            l_returns.append(f"ones_like({time_vec_name}) * (- inf)")

    error_return = ""
    for i_ret, ret in enumerate(l_returns):
        error_return += ret
        if i_ret < (len(l_returns) - 1):
            error_return += ", "

    return error_return


def get_transit(multi, l_inst_model, l_dataset, get_times_from_datasets, transit_model,
                ldmodel4instmodfname, LDs, parametrisation, SSE4instmodfname, star, planets, tab,
                time_vec_name, l_time_vec_name, function_builder, ext_func_fullname
                ):
    """Provide the text for the transit part of the LC model text (preambule and return).

    This function should generate the text for the "<function_whole_shortname>" function, the "<planet>"
    functions and the "tr_<planet>" function.

    Arguments
    ---------
    multi                       : bool
        True if the datasim function needs to give multiple outputs.
    l_inst_model                : list_of_Instrument_Model
        List of the instrument models instances for each output of the datasim function. Each instrument model
        in this list is the instrument model which has to be used for the corresponding dataset provided in l_dataset.
    l_dataset                   : list of Datasets
        List of the Dataset intances for each output of the datasim function. The instrument model to be used for
        each dataset is provided in l_inst_model.
    get_times_from_datasets     : bool
        If True the times at which the model should be computed will be taken from the datasets and
        included into the function. I False the user of the function will have to provide the times.
    transit_model               : dict
        Dictionary describing the transit model to use. The format of this disctionary is:
        {"<planet name >": {"do": <bool>  # Should we model the transit
                            'model_definitions': {"<model name>": {"model": '<name of the model like batman>'}, ...}
                            'model4instrument': {"<instrument model full name>": "<model name in model_definitions>", ...}
                            },
         ...
         }
    ldmodel4instmodfname        : dict of dict of str
        Dictionary giving Limd darkening model to use for each instrument model and for each star
        Format: {"<instrument_model_name>: {"<star_name>": "<LD_model_name>"}
    LDs                         : dict of CoreLD
        Dictionary of subclasses of CoreLD instances providing the different limb-darkening models
        Format: {f"<star_name>_<LD model name>"": CoreLD_subclass instance, }
    parametrisation             : str
        string refering to the parametrisation to use
    SSE4instmodfname            : dict of dict of str int and float
        Dictionary giving the supersampling factor and the exposure time to use for each instrument model
        Format: {"instrument model name": {'supersamp': int_supersampling_factor, 'exptime': float_exposure_time}}
    star                        : Star
        Star object
    planets                     : dict of Planets
        Dictionary of Planet instance providing the planets in the system
        Format: {"planet name": Planet instance}
    tab                         : str
        String providing the space to put in front of each new line
    time_vec_name               : str
        Str used to designate the time vector
    l_time_vec_name             : str
        Str used to designate the list of time vectors
    function_builder            : FunctionBuilder
        FunctionBuilder instance
    ext_func_fullname           : str
        Extension to add and the end of the full name of the function simulating the transit only
        which is defined by this function in the function_builder

    Returns
    -------
    returns     : dict of list of str
        Dictionary of list of str giving the return for transit model for each function and each output
    """
    ########################
    # Initialise the outputs
    ########################
    returns = {}

    # Extension for the shortname of the function that do the transit only model
    ext_func_tr_only = "_tr"

    ##############################
    # Do the Model for each planet
    ##############################
    for planet in planets.values():
        planet_name = planet.get_name()
        if transit_model[planet_name]['do']:
            ########################################################################
            # Define the functions to populate and initialise entries in the outputs
            ########################################################################
            # Defines the lists of function shortnames and add the new transit only function into the function builder
            l_whole_function_shortname = [function_whole_shortname, ]
            l_planet_function_shortname_ext = ["", ext_func_tr_only]
            l_planet_function_shortname = []
            for planet_func_shortname_ext in l_planet_function_shortname_ext:
                l_planet_function_shortname.append(f"{get_function_planet_shortname(planet)}{planet_func_shortname_ext}")
            l_function_shortname_4_planet = l_whole_function_shortname + l_planet_function_shortname

            ##################################################
            # Initialise the new functions in function_builder
            ##################################################
            l_func_shortname_ext_to_create = [ext_func_tr_only, ]
            for func_shortname_ext in l_func_shortname_ext_to_create:
                func_shortname_tr_pl_only = f"{get_function_planet_shortname(planet)}{ext_func_tr_only}"
                function_builder.add_new_function(shortname=func_shortname_tr_pl_only)
                function_builder.set_function_fullname(full_name=f"LC_sim_{func_shortname_tr_pl_only}_{ext_func_fullname}", shortname=func_shortname_tr_pl_only)

            ##############
            # Add the time
            ##############
            for func_shortname in l_function_shortname_4_planet:
                time_arg_name = add_time_argument(function_builder=function_builder, function_shortname=func_shortname,
                                                  multi=multi, get_times_from_datasets=get_times_from_datasets,
                                                  l_dataset=l_dataset, time_vec_name=time_vec_name, l_time_vec_name=l_time_vec_name,
                                                  exist_ok=True)

            ############################################################
            # Initialise the preambule and return text for all functions
            ############################################################
            for func_shortname in l_function_shortname_4_planet:
                if func_shortname not in returns:
                    returns[func_shortname] = []
                    for i_inputoutput in range(len(l_inst_model)):
                        returns[func_shortname].append("")

            ###############################################################
            # Add the parameters required for the model for all instruments
            ###############################################################
            # Add rhostar if needed
            if parametrisation == "Multis":
                for func_shortname in l_function_shortname_4_planet:
                    function_builder.add_parameter(parameter=star.rho, function_shortname=func_shortname, exist_ok=True)

            # Add the planet parameters: Rrat, ecosw, esinw, cosinc, P, tic and aR if needed
            l_param = [planet.Rrat, planet.ecosw, planet.esinw, planet.cosinc, planet.P, planet.tic]
            if parametrisation != "Multis":
                l_param.append(planet.aR)
            for param in l_param:
                for func_shortname in l_function_shortname_4_planet:
                    function_builder.add_parameter(parameter=param, function_shortname=func_shortname, exist_ok=True)

            ####################################################################
            # Do the Model for each planet and each instrument and each function
            ####################################################################
            for func_shortname in l_function_shortname_4_planet:

                for i_inputoutput, (instmod, dst) in enumerate(zip(l_inst_model, l_dataset)):
                    instmod_fullname = instmod.full_code_name

                    ####################################################################################
                    # Get the transit model impletmentation definition for the planet and the instrument
                    ####################################################################################
                    model_definition_name = transit_model[planet_name]['model4instrument'][instmod.full_name]
                    transit_model_pl_inst = transit_model[planet_name]['model_definitions'][model_definition_name]

                    ##############
                    # Batman model
                    ##############
                    if transit_model_pl_inst["model"] == "batman":
                        ## Add the limb darkening parameters
                        LD_mod_name = ldmodel4instmodfname[instmod_fullname][star.code_name]
                        LD_mod = LDs[star.code_name + "_" + LD_mod_name]
                        for param in LD_mod.get_list_params(main=True):
                            if not(function_builder.is_parameter(parameter=param, function_shortname=func_shortname)):
                                function_builder.add_parameter(parameter=param, function_shortname=func_shortname, exist_ok=True)
                        ## Creation of the TransitParams instances and add them to the ldicts
                        if not(function_builder.is_in_ldict(variable_name=f"params_{planet.get_name()}_{instmod.full_code_name}", function_shortname=func_shortname)):
                            params_bat = TransitParams()
                            params_bat.per = 1.   # orbital period
                            params_bat.rp = 0.1   # planet radius(in stel radii)
                            params_bat.a = 15.    # semi-major axis(in stel radii)
                            params_bat.inc = 90.  # orbital inclination (in degrees)
                            params_bat.ecc = 0.   # eccentricity
                            params_bat.w = 90.    # long. of periastron (in deg.)
                            if get_times_from_datasets:
                                time_arg_value = function_builder.get_ldict(function_shortname=function_whole_shortname)[time_arg_name]  # Time is the same for all function
                            else:
                                if multi:
                                    time_arg_value = []
                                    for dst in l_dataset:
                                        time_arg_value.append(dst.get_time())
                                else:
                                    time_arg_value = l_dataset[0].get_time()
                            if multi:
                                t_mean = mean(time_arg_value[0])
                            else:
                                t_mean = mean(time_arg_value)
                            params_bat.t0 = t_mean
                            LD_mod_name = ldmodel4instmodfname[instmod.get_name(include_prefix=True, code_version=True, recursive=True)][star.code_name]
                            LD_mod = LDs[star.code_name + "_" + LD_mod_name]
                            params_bat.limb_dark = LD_mod.ld_type  # LD model
                            params_bat.u = LD_mod.init_LD_values  # LDC init val
                            function_builder.add_variable_to_ldict(variable_name=f"params_{planet_name}_{instmod_fullname}",
                                                                   variable_content=params_bat, function_shortname=func_shortname, exist_ok=False)
                        ## writing the preambule and return (First preambules after returns)
                        ## preambule: Update the parameter values in the TransitParams object
                        if not(function_builder.is_done_in_text(name=f"params_{planet_name}_{instmod_fullname}", function_shortname=func_shortname)):
                            period = function_builder.get_text_4_parameter(parameter=planet.P, function_shortname=func_shortname)
                            ecosw = function_builder.get_text_4_parameter(parameter=planet.ecosw, function_shortname=func_shortname)
                            esinw = function_builder.get_text_4_parameter(parameter=planet.esinw, function_shortname=func_shortname)
                            cosinc = function_builder.get_text_4_parameter(parameter=planet.cosinc, function_shortname=func_shortname)
                            if not(function_builder.is_done_in_text(name=f"ecc_{planet_name}", function_shortname=func_shortname)):
                                function_builder.add_variable_to_ldict(variable_name="sqrt", variable_content=sqrt, function_shortname=func_shortname, exist_ok=True)
                                function_builder.add_to_body_text(text=f"{tab}ecc_{planet_name} = sqrt({ecosw} * {ecosw} + {esinw} * {esinw})\n", function_shortname=func_shortname)
                                function_builder.add_to_done_in_text(name=f"ecc_{planet_name}", function_shortname=func_shortname)
                            if not(function_builder.is_done_in_text(name=f"omega_{planet_name}_deg", function_shortname=func_shortname)):
                                function_builder.add_variable_to_ldict(variable_name="getomega_deg_fast", variable_content=getomega_deg_fast, function_shortname=func_shortname, exist_ok=True)
                                function_builder.add_to_body_text(text=f"{tab}omega_{planet_name}_deg = getomega_deg_fast({ecosw}, {esinw})\n", function_shortname=func_shortname)
                                function_builder.add_to_done_in_text(name=f"omega_{planet_name}_deg", function_shortname=func_shortname)
                            if not(function_builder.is_done_in_text(name=f"inc_{planet_name}_deg", function_shortname=func_shortname)):
                                function_builder.add_variable_to_ldict(variable_name="degrees", variable_content=degrees, function_shortname=func_shortname, exist_ok=True)
                                function_builder.add_variable_to_ldict(variable_name="acos", variable_content=acos, function_shortname=func_shortname, exist_ok=True)
                                function_builder.add_to_body_text(text=f"{tab}inc_{planet_name}_deg = degrees(acos({cosinc}))\n", function_shortname=func_shortname)
                                function_builder.add_to_done_in_text(name=f"inc_{planet_name}_deg", function_shortname=func_shortname)
                            if parametrisation == "Multis":
                                if not(function_builder.is_done_in_text(name=f"aR_{planet_name}", function_shortname=func_shortname)):
                                    rhostar = function_builder.get_text_4_parameter(parameter=star.rho, function_shortname=func_shortname)
                                    function_builder.add_variable_to_ldict(variable_name="getaoverr", variable_content=getaoverr, function_shortname=func_shortname, exist_ok=True)
                                    function_builder.add_to_body_text(text=f"{tab}aR_{planet_name} = getaoverr({period}, {rhostar}, ecc_{planet_name}, omega_{planet_name}_deg)\n", function_shortname=func_shortname)
                                    function_builder.add_to_done_in_text(name=f"aR_{planet_name}", function_shortname=func_shortname)
                            tic = function_builder.get_text_4_parameter(parameter=planet.tic, function_shortname=func_shortname)
                            Rrat = function_builder.get_text_4_parameter(parameter=planet.Rrat, function_shortname=func_shortname)
                            if parametrisation == "Multis":
                                aR = f"aR_{planet_name}\n"
                            else:
                                aR = function_builder.get_text_4_parameter(parameter=planet.aR, function_shortname=func_shortname)
                            function_builder.add_to_body_text(text=f"{tab}params_{planet_name}_{instmod_fullname}.t0 = {tic}\n", function_shortname=func_shortname)
                            function_builder.add_to_body_text(text=f"{tab}params_{planet_name}_{instmod_fullname}.per = {period}\n", function_shortname=func_shortname)
                            function_builder.add_to_body_text(text=f"{tab}params_{planet_name}_{instmod_fullname}.rp = {Rrat}\n", function_shortname=func_shortname)
                            function_builder.add_to_body_text(text=f"{tab}params_{planet_name}_{instmod_fullname}.inc = inc_{planet_name}_deg\n", function_shortname=func_shortname)
                            function_builder.add_to_body_text(text=f"{tab}params_{planet_name}_{instmod_fullname}.ecc = ecc_{planet_name}\n", function_shortname=func_shortname)
                            function_builder.add_to_body_text(text=f"{tab}params_{planet_name}_{instmod_fullname}.w = omega_{planet_name}_deg\n", function_shortname=func_shortname)
                            LD_mod_name = ldmodel4instmodfname[instmod.get_name(include_prefix=True, code_version=True, recursive=True)][star.code_name]
                            LD_mod = LDs[star.code_name + "_" + LD_mod_name]
                            ld_param_list = "["
                            for param in LD_mod.get_list_params(main=True):
                                ld_param_list += function_builder.get_text_4_parameter(parameter=param, function_shortname=func_shortname) + ", "
                            ld_param_list += "]"
                            function_builder.add_to_body_text(text=f"{tab}params_{planet_name}_{instmod_fullname}.u = {ld_param_list}\n", function_shortname=func_shortname)
                            function_builder.add_to_body_text(text=f"{tab}params_{planet_name}_{instmod_fullname}.limb_dark = '{LD_mod.ld_type}'\n", function_shortname=func_shortname)
                            function_builder.add_to_body_text(text=f"{tab}params_{planet_name}_{instmod_fullname}.a = {aR}\n", function_shortname=func_shortname)
                            function_builder.add_to_done_in_text(name=f"params_{planet_name}_{instmod_fullname}", function_shortname=func_shortname)
                        ## preambule: Create the TransitModel object
                        if get_times_from_datasets:
                            if not(function_builder.is_in_ldict(variable_name=f"m_{planet_name}_{instmod_fullname}_dst{dst.number}", function_shortname=func_shortname)):
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
                            if not(function_builder.is_done_in_text(name=f"m_{planet_name}_{instmod_fullname}_dst{dst.number}", function_shortname=func_shortname)):
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
                                function_builder.add_to_body_text(text=f"{tab}m_{planet_name}_{instmod_fullname}_dst{dst.number} = TransitModel(params_{planet_name}_{instmod_fullname}, {time_vect}{supersamp_text})\n", function_shortname=func_shortname)
                                function_builder.add_to_done_in_text(name=f"m_{planet_name}_{instmod_fullname}_dst{dst.number}", function_shortname=func_shortname)
                        ## writing the returns
                        if returns[func_shortname][i_inputoutput] == "":
                            pre_text = ""
                        else:
                            pre_text = " + "
                        returns[func_shortname][i_inputoutput] += f"{pre_text}m_{planet_name}_{instmod_fullname}_dst{dst.number}.light_curve(params_{planet_name}_{instmod_fullname}) - 1 "

                    #################
                    # Pytransit model
                    #################
                    elif transit_model_pl_inst["model"] == "pytransit":
                        ## Add the limb darkening parameters
                        LD_mod_name = ldmodel4instmodfname[instmod_fullname][star.code_name]
                        LD_mod = LDs[star.code_name + "_" + LD_mod_name]
                        for param in LD_mod.get_list_params(main=True):
                            if not(function_builder.is_parameter(parameter=param, function_shortname=func_shortname)):
                                function_builder.add_parameter(parameter=param, function_shortname=func_shortname, exist_ok=False)
                        ## writing the preambule and return (First preambuless after returns)
                        ## preambule: planetary parameter conversions
                        ecosw = function_builder.get_text_4_parameter(parameter=planet.ecosw, function_shortname=func_shortname)
                        esinw = function_builder.get_text_4_parameter(parameter=planet.esinw, function_shortname=func_shortname)
                        function_builder.add_variable_to_ldict(variable_name="sqrt", variable_content=sqrt, function_shortname=func_shortname, exist_ok=True)
                        function_builder.add_to_body_text(text=f"{tab}ecc_{planet_name} = sqrt({ecosw} * {ecosw} + {esinw} * {esinw})\n", function_shortname=func_shortname)
                        function_builder.add_variable_to_ldict(variable_name="getomega_fast", variable_content=getomega_fast, function_shortname=func_shortname, exist_ok=True)
                        function_builder.add_to_body_text(text=f"{tab}omega_{planet_name} = getomega_fast({esinw}, {ecosw})\n", function_shortname=func_shortname)
                        cosinc = function_builder.get_text_4_parameter(parameter=planet.cosinc, function_shortname=func_shortname)
                        function_builder.add_variable_to_ldict(variable_name="acos", variable_content=acos, function_shortname=func_shortname, exist_ok=True)
                        function_builder.add_to_body_text(text=f"{tab}inc_{planet_name} = acos({cosinc})\n", function_shortname=func_shortname)
                        period = function_builder.get_text_4_parameter(parameter=planet.P, function_shortname=func_shortname)
                        if parametrisation == "Multis":
                            rhostar = function_builder.get_text_4_parameter(parameter=star.rhostar, function_shortname=func_shortname)
                            function_builder.add_variable_to_ldict(variable_name="getaoverr", variable_content=getaoverr, function_shortname=func_shortname, exist_ok=True)
                            function_builder.add_variable_to_ldict(variable_name="degrees", variable_content=degrees, function_shortname=func_shortname, exist_ok=True)
                            function_builder.add_to_body_text(text=f"{tab}aR_{planet_name} = getaoverr({period}, {rhostar}, ecc_{planet_name}, degrees(omega_{planet_name}))\n", function_shortname=func_shortname)
                        # Get the text for the remaining planet parameters
                        if parametrisation == "Multis":
                            aR = f"aR_{planet_name}\n"
                        else:
                            aR = function_builder.get_text_4_parameter(parameter=planet.aR, function_shortname=func_shortname)
                        tic = function_builder.get_text_4_parameter(parameter=planet.tic, function_shortname=func_shortname)
                        Rrat = function_builder.get_text_4_parameter(parameter=planet.Rrat, function_shortname=func_shortname)
                        # Create the Model and add it the the ldict
                        LD_mod_name = ldmodel4instmodfname[instmod.get_name(include_prefix=True, code_version=True, recursive=True)][star.code_name]
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
                        raise ValueError(f"Transit model {transit_model_pl_inst['model']} is not recognized.")

        ############################################
        # Finalize the planets transit only function
        ############################################
        for planet in planets.values():
            func_shortname = f"{get_function_planet_shortname(planet)}{ext_func_tr_only}"
            get_condition(multi=multi, l_inst_model=l_inst_model, l_planet=[planet, ], parametrisation=parametrisation,
                          tab=tab, time_vec_name=time_vec_name, l_time_vec_name=l_time_vec_name, function_builder=function_builder,
                          function_shortname=func_shortname)
            function_builder.add_to_body_text(text=template_return.format(tab=tab, returns=f"{str(returns.pop(func_shortname)).strip('[]')}",
                                                                          returns_except=get_catchederror_return(multi=multi,
                                                                                                                 l_inst_model=l_inst_model,
                                                                                                                 time_vec_name=time_vec_name,
                                                                                                                 l_time_vec_name=l_time_vec_name,
                                                                                                                 function_builder=function_builder,
                                                                                                                 function_shortname=func_shortname)),
                                              function_shortname=func_shortname)

    return returns


def get_phasecurve(multi, l_inst_model, l_dataset, get_times_from_datasets, phasecurve_model,
                   parametrisation, SSE4instmodfname, star, planets, tab,
                   time_vec_name, l_time_vec_name, function_builder, ext_func_fullname
                   ):
    """Provide the text for the phase curve part of the LC model text (preambule and return).

    Arguments
    ---------
    multi                   : bool
        True if the datasim function needs to give multiple outputs.
    l_inst_model            : list_of_Instrument_Model
        List of the instrument models instances for each output of the datasim function.
    l_dataset               : list of Datasets
        List of the Dataset intances for each output of the datasim function. The instrument model to be used for
        each dataset is provided in l_inst_model.
    get_times_from_datasets : bool
        If True the times at which the model should be computed will be taken from the datasets and
        included into the function. I False the user of the function will have to provide the times.
    phasecurve_model        : dict
        Dictionary describing the phasecurve model to use. The format of this disctionary is:
        {"<planet name >": {"do": <bool>  # Should we model the transit
                            'model_definitions': {"<model name>": {"model": '<name of the model like spiderman>', "args": {<arguments of the model specific to each model>, ...}}, ...}
                            'model4instrument': {"<instrument model full name>": ["<model name in model_definitions>", ...],  # List of all the components
                                                 ...}
                            },
         ...
         }
    parametrisation          : str
        string refering to the parametrisation to use
    SSE4instmodfname         : dict of dict of str int and float
        Dictionary giving the supersampling factor and the exposure time to use for each instrument model
        Format: {"instrument model name": {'supersamp': int_supersampling_factor, 'exptime': float_exposure_time}}
        WARNING: CURRENTLY NOT USED
    star                     : Star object
        Star instance of the parent star
    planets                  : dict of Planets
        Dictionary of Planet instance providing the planets in the system
        Format: {"planet name": Planet instance}
    tab                      : str
        String providing the space to put in front of each new line
    time_vec_name       : str
        Str used to designate the time vector
    l_time_vec_name     : str
        Str used to designate the list of time vectors
    function_builder            : FunctionBuilder
        FunctionBuilder instance
    ext_func_fullname           : str
        Extension to add and the end of the full name of the function simulating the transit only
        which is defined by this function in the function_builder

    Returns
    -------
    returns     : dict of list of str
        Dictionary of list of str giving the return for transit model for each function and each output
    """
    ########################
    # Initialise the outputs
    ########################
    returns = {}

    # Extension for the shortname of the function that do the transit only model
    ext_func_pc_only = "_pc"

    ##############################
    # Do the Model for each planet
    ##############################
    for planet in planets.values():
        planet_name = planet.get_name()
        if phasecurve_model[planet_name]['do']:
            ########################################################################
            # Define the functions to populate and initialise entries in the outputs
            ########################################################################
            # Defines the lists of function shortnames and add the new transit only function into the function builder
            l_whole_function_shortname = [function_whole_shortname, ]
            l_planet_function_shortname_ext = ["", ext_func_pc_only]
            l_planet_function_shortname = []
            for planet_func_shortname_ext in l_planet_function_shortname_ext:
                l_planet_function_shortname.append(f"{get_function_planet_shortname(planet)}{planet_func_shortname_ext}")
            l_function_shortname_4_planet = l_whole_function_shortname + l_planet_function_shortname

            ##################################################
            # Initialise the new functions in function_builder
            ##################################################
            l_func_shortname_ext_to_create = [ext_func_pc_only, ]
            for func_shortname_ext in l_func_shortname_ext_to_create:
                func_shortname_pc_pl_only = f"{get_function_planet_shortname(planet)}{ext_func_pc_only}"
                function_builder.add_new_function(shortname=func_shortname_pc_pl_only)
                function_builder.set_function_fullname(full_name=f"LC_sim_{func_shortname_pc_pl_only}_{ext_func_fullname}", shortname=func_shortname_pc_pl_only)

            ##############
            # Add the time
            ##############
            for func_shortname in l_function_shortname_4_planet:
                time_arg_name = add_time_argument(function_builder=function_builder, function_shortname=func_shortname,
                                                  multi=multi, get_times_from_datasets=get_times_from_datasets,
                                                  l_dataset=l_dataset, time_vec_name=time_vec_name, l_time_vec_name=l_time_vec_name,
                                                  exist_ok=True)

            ############################################################
            # Initialise the preambule and return text for all functions
            ############################################################
            for func_shortname in l_function_shortname_4_planet:
                if func_shortname not in returns:
                    returns[func_shortname] = []
                    for i_inputoutput in range(len(l_inst_model)):
                        returns[func_shortname].append("")

            ####################################################################
            # Do the Model for each planet and each instrument and each function
            ####################################################################
            for func_shortname in l_function_shortname_4_planet:
                for i_inputoutput, (instmod, dst) in enumerate(zip(l_inst_model, l_dataset)):
                    instmod_fullname = instmod.full_code_name

                    ########################################################################################
                    # Get the phase curve model impletmentation definition for the planet and the instrument
                    ########################################################################################
                    l_pc_model_comp_pl_inst = phasecurve_model[planet_name]['model4instrument'][instmod.full_name]

                    # For each component of the phasec curve model
                    for component_name in l_pc_model_comp_pl_inst:
                        pc_component_model = phasecurve_model[planet_name]['model_definitions'][component_name]

                        ##################
                        # Spiderman models
                        ##################
                        if pc_component_model["model"] == "spiderman":
                            brightness_model = pc_component_model["args"]["ModelParams_kwargs"]["brightness_model"]
                            # Add the lightcurve_kwargs to ldict
                            if ('lightcurve_kwargs' in pc_component_model["args"]) and (len(pc_component_model["args"]['lightcurve_kwargs']) > 0):
                                if not(function_builder.is_in_ldict(variable_name=f"{component_name}_lightcurve_kwargs", function_shortname=func_shortname)):
                                    function_builder.add_variable_to_ldict(variable_name=f"{component_name}_lightcurve_kwargs", variable_content=pc_component_model["args"]['lightcurve_kwargs'],
                                                                           function_shortname=func_shortname, exist_ok=True)
                                lightcurve_kwargs = f", **{component_name}_lightcurve_kwargs"
                            else:
                                lightcurve_kwargs = ""

                            ####################################
                            # Brightness model Zhang Thermal map
                            ####################################
                            if (brightness_model == "zhang"):
                                ###########################################
                                # Add the parameters required for the model
                                ###########################################
                                # Stellar parameters: Teff and rhostar if needed
                                function_builder.add_parameter(parameter=star.Teff, function_shortname=func_shortname, exist_ok=True)
                                if parametrisation == "Multis":
                                    function_builder.add_parameter(parameter=star.rho, function_shortname=func_shortname, exist_ok=True)
                                # Create the planetary model parameters that are model independent
                                l_param = [planet.a, planet.ecosw, planet.esinw, planet.cosinc, planet.P, planet.tic]
                                if parametrisation != "Multis":
                                    l_param.append(planet.aR)
                                for param in l_param:
                                    function_builder.add_parameter(parameter=param, function_shortname=func_shortname, exist_ok=True)
                                # Create the planetary model parameters that are model dependent
                                # TODO: Actually have different parameters for different model components.
                                l_param = [planet.u1, planet.u2, planet.xi, planet.deltaT, planet.Tn, planet.Rrat]
                                for param in l_param:
                                    function_builder.add_parameter(parameter=param, function_shortname=func_shortname, exist_ok=True)

                                ####################################################################
                                # Writing the preambule and return (First preambules, after returns)
                                ####################################################################
                                ## Creation of the TransitParams instances and add them to the ldicts
                                if not(function_builder.is_in_ldict(variable_name=f"param_spiderman_{planet_name}_{instmod_fullname}", function_shortname=func_shortname)):
                                    params_spider = ModelParams(**pc_component_model["args"]["ModelParams_kwargs"])
                                    function_builder.add_variable_to_ldict(variable_name=f"param_spiderman_{planet_name}_{instmod_fullname}",
                                                                           variable_content=params_spider, function_shortname=func_shortname, exist_ok=False)
                                ## preambule: define ecc, omega, inc, aR if needed in the preambule and get text for orbital parameters
                                if not(function_builder.is_done_in_text(name=f"param_spiderman_{planet_name}_{instmod_fullname}", function_shortname=func_shortname)):
                                    period = function_builder.get_text_4_parameter(parameter=planet.P, function_shortname=func_shortname)
                                    ecosw = function_builder.get_text_4_parameter(parameter=planet.ecosw, function_shortname=func_shortname)
                                    esinw = function_builder.get_text_4_parameter(parameter=planet.esinw, function_shortname=func_shortname)
                                    cosinc = function_builder.get_text_4_parameter(parameter=planet.cosinc, function_shortname=func_shortname)
                                    if not(function_builder.is_done_in_text(name=f"ecc_{planet_name}", function_shortname=func_shortname)):
                                        function_builder.add_variable_to_ldict(variable_name="sqrt", variable_content=sqrt, function_shortname=func_shortname, exist_ok=True)
                                        function_builder.add_to_body_text(text=f"{tab}ecc_{planet_name} = sqrt({ecosw} * {ecosw} + {esinw} * {esinw})\n", function_shortname=func_shortname)
                                        function_builder.add_to_done_in_text(name=f"ecc_{planet_name}", function_shortname=func_shortname)
                                    if not(function_builder.is_done_in_text(name=f"omega_{planet_name}_deg", function_shortname=func_shortname)):
                                        function_builder.add_variable_to_ldict(variable_name="getomega_deg_fast", variable_content=getomega_deg_fast, function_shortname=func_shortname, exist_ok=True)
                                        function_builder.add_to_body_text(text=f"{tab}omega_{planet_name} = getomega_deg_fast({ecosw}, {esinw})\n", function_shortname=func_shortname)
                                        function_builder.add_to_done_in_text(name=f"omega_{planet_name}_deg", function_shortname=func_shortname)
                                    if not(function_builder.is_done_in_text(name=f"inc_{planet_name}_deg", function_shortname=func_shortname)):
                                        function_builder.add_variable_to_ldict(variable_name="degrees", variable_content=degrees, function_shortname=func_shortname, exist_ok=True)
                                        function_builder.add_variable_to_ldict(variable_name="acos", variable_content=acos, function_shortname=func_shortname, exist_ok=True)
                                        function_builder.add_to_body_text(text=f"{tab}inc_{planet_name} = degrees(acos({cosinc}))\n", function_shortname=func_shortname)
                                        function_builder.add_to_done_in_text(name=f"inc_{planet_name}_deg", function_shortname=func_shortname)
                                    if parametrisation == "Multis":
                                        if not(function_builder.is_done_in_text(name=f"aR_{planet_name}", function_shortname=func_shortname)):
                                            rhostar = function_builder.get_text_4_parameter(parameter=star.rho, function_shortname=func_shortname)
                                            function_builder.add_variable_to_ldict(variable_name="getaoverr", variable_content=getaoverr, function_shortname=func_shortname, exist_ok=True)
                                            function_builder.add_to_body_text(text=f"{tab}aR_{planet_name} = getaoverr({period}, {rhostar}, ecc_{planet_name}, omega_{planet_name})\n", function_shortname=func_shortname)
                                            function_builder.add_to_done_in_text(name=f"aR_{planet_name}", function_shortname=func_shortname)
                                    ## preambule: Update the parameter values in the TransitParams object
                                    tic = function_builder.get_text_4_parameter(parameter=planet.tic, function_shortname=func_shortname)
                                    Rrat = function_builder.get_text_4_parameter(parameter=planet.Rrat, function_shortname=func_shortname)
                                    a_au = function_builder.get_text_4_parameter(parameter=planet.a, function_shortname=func_shortname)
                                    u1 = function_builder.get_text_4_parameter(parameter=planet.u1, function_shortname=func_shortname)
                                    u2 = function_builder.get_text_4_parameter(parameter=planet.u2, function_shortname=func_shortname)
                                    xi = function_builder.get_text_4_parameter(parameter=planet.xi, function_shortname=func_shortname)
                                    Tn = function_builder.get_text_4_parameter(parameter=planet.Tn, function_shortname=func_shortname)
                                    deltaT = function_builder.get_text_4_parameter(parameter=planet.deltaT, function_shortname=func_shortname)
                                    Teff = function_builder.get_text_4_parameter(parameter=star.Teff, function_shortname=func_shortname)
                                    if parametrisation == "Multis":
                                        aR = f"aR_{planet_name}\n"
                                    else:
                                        aR = function_builder.get_text_4_parameter(parameter=planet.aR, function_shortname=func_shortname)
                                    function_builder.add_to_body_text(text=f"{tab}param_spiderman_{planet_name}_{instmod_fullname}.t0 = {tic}\n", function_shortname=func_shortname)
                                    function_builder.add_to_body_text(text=f"{tab}param_spiderman_{planet_name}_{instmod_fullname}.per = {period}\n", function_shortname=func_shortname)
                                    function_builder.add_to_body_text(text=f"{tab}param_spiderman_{planet_name}_{instmod_fullname}.a_abs = {a_au}\n", function_shortname=func_shortname)
                                    function_builder.add_to_body_text(text=f"{tab}param_spiderman_{planet_name}_{instmod_fullname}.rp = {Rrat}\n", function_shortname=func_shortname)
                                    function_builder.add_to_body_text(text=f"{tab}param_spiderman_{planet_name}_{instmod_fullname}.inc = inc_{planet_name}_deg\n", function_shortname=func_shortname)
                                    function_builder.add_to_body_text(text=f"{tab}param_spiderman_{planet_name}_{instmod_fullname}.ecc = ecc_{planet_name}\n", function_shortname=func_shortname)
                                    function_builder.add_to_body_text(text=f"{tab}param_spiderman_{planet_name}_{instmod_fullname}.w = omega_{planet_name}_deg\n", function_shortname=func_shortname)
                                    function_builder.add_to_body_text(text=f"{tab}param_spiderman_{planet_name}_{instmod_fullname}.p_u1 = {u1}\n", function_shortname=func_shortname)
                                    function_builder.add_to_body_text(text=f"{tab}param_spiderman_{planet_name}_{instmod_fullname}.p_u2 = {u2}\n", function_shortname=func_shortname)
                                    function_builder.add_to_body_text(text=f"{tab}param_spiderman_{planet_name}_{instmod_fullname}.xi = {xi}\n", function_shortname=func_shortname)
                                    function_builder.add_to_body_text(text=f"{tab}param_spiderman_{planet_name}_{instmod_fullname}.T_n = {Tn}\n", function_shortname=func_shortname)
                                    function_builder.add_to_body_text(text=f"{tab}param_spiderman_{planet_name}_{instmod_fullname}.delta_T = {deltaT}\n", function_shortname=func_shortname)
                                    function_builder.add_to_body_text(text=f"{tab}param_spiderman_{planet_name}_{instmod_fullname}.T_s = {Teff}\n", function_shortname=func_shortname)
                                    function_builder.add_to_body_text(text=f"{tab}param_spiderman_{planet_name}_{instmod_fullname}.a = {aR}\n", function_shortname=func_shortname)
                                    function_builder.add_to_body_text(text=f"{tab}param_spiderman_{planet_name}_{instmod_fullname}.l1  = {pc_component_model['args']['attributes']['l1']}\n", function_shortname=func_shortname)
                                    function_builder.add_to_body_text(text=f"{tab}param_spiderman_{planet_name}_{instmod_fullname}.l2 = {pc_component_model['args']['attributes']['l2']}\n", function_shortname=func_shortname)
                                    function_builder.add_to_body_text(text=f"{tab}param_spiderman_{planet_name}_{instmod_fullname}.n_layers = {pc_component_model['args']['attributes'].get('n_layers', 5)}\n", function_shortname=func_shortname)
                                    if "filter" in pc_component_model["args"]["attributes"]:
                                        function_builder.add_to_body_text(text=f"{tab}param_spiderman_{planet_name}_{instmod_fullname}.filter = '{pc_component_model['args']['attributes']['filter']}'\n", function_shortname=func_shortname)
                                    function_builder.add_to_done_in_text(name=f"param_spiderman_{planet_name}_{instmod_fullname}", function_shortname=func_shortname)

                                ####################################################
                                # Produce the text for the phase curve model returns
                                ####################################################
                                if multi:
                                    time_vect = f"{time_arg_name}[{i_inputoutput}]"
                                else:
                                    time_vect = f"{time_arg_name}"
                                if get_times_from_datasets:
                                    supersamp = SSE4instmodfname.get_supersamp(instmod.get_name(include_prefix=True, code_version=True, recursive=True))
                                    if supersamp > 1:
                                        logger.warning("Currently the spiderman model doesn't include supersampling !")
                                if returns[func_shortname][i_inputoutput] == "":
                                    pre_text = ""
                                else:
                                    pre_text = " + "
                                returns[func_shortname][i_inputoutput] = f"{pre_text}param_spiderman_{planet_name}_{instmod_fullname}.lightcurve({time_vect}{lightcurve_kwargs}) - 1 "

                            ##################################
                            # No other brightnee model for now
                            ##################################
                            else:
                                raise NotImplementedError(f"brightness_model {brightness_model} of spiderman is not implemented.")

                        #######################
                        # Sine and Cosine model
                        #######################
                        if (pc_component_model["model"] == "sincos") or (pc_component_model["model"] == "ellipsoidal") or (pc_component_model["model"] == "doppler"):
                            if pc_component_model["model"] in ["ellipsoidal", "beaming"]:
                                if pc_component_model["model"] == "beaming":
                                    sincos_components = {"": {"sincos": "sin", "factor_period": 1, "average": 'zero', 'phase_offset': 0.}}
                                else:  # pc_component_model["model"] == "ellipsoidal"
                                    sincos_components = {"": {"sincos": "cos", "factor_period": 1. / 2., "average": 'zero', 'phase_offset': pi}}
                            else:
                                sincos_components = pc_component_model["args"]
                            for sincos_comp_name, sincos_comp_dict in sincos_components:
                                if sincos_comp_dict["sincos"] is None:
                                    ################
                                    # Add parameters
                                    ################
                                    constant_param = planet.get_parameter(f"C{component_name}{sincos_comp_name}", return_error=False, main=True)
                                    function_builder.add_parameter(parameter=constant_param, function_shortname=func_shortname, exist_ok=True)
                                    constant = function_builder.get_text_4_parameter(parameter=constant_param, function_shortname=func_shortname)
                                    if returns[func_shortname][i_inputoutput] == "":
                                        pre_text = ""
                                    else:
                                        pre_text = " + "
                                    returns[func_shortname][i_inputoutput] += f"{pre_text}{constant}"
                                else:
                                    ################
                                    # Add parameters
                                    ################
                                    # Orbital Period
                                    function_builder.add_parameter(parameter=planet.P, function_shortname=func_shortname, exist_ok=True)
                                    period = function_builder.get_text_4_parameter(parameter=planet.P, function_shortname=func_shortname)
                                    # Time of inferior conjunction
                                    function_builder.add_parameter(parameter=planet.tic, function_shortname=func_shortname, exist_ok=True)
                                    tic = function_builder.get_text_4_parameter(parameter=planet.tic, function_shortname=func_shortname)
                                    # Amplitude
                                    amp_param = planet.get_parameter(f"A{component_name}{sincos_comp_name}", return_error=False, main=True)
                                    function_builder.add_parameter(parameter=amp_param, function_shortname=func_shortname, exist_ok=True)
                                    amp = function_builder.get_text_4_parameter(parameter=amp_param, function_shortname=func_shortname)
                                    # Phase Offset
                                    if sincos_comp_dict.get("phase_offset", 0) == "param":
                                        phi_param = planet.get_parameter(f"Phi{component_name}{sincos_comp_name}", return_error=False, main=True)
                                        function_builder.add_parameter(parameter=phi_param, function_shortname=func_shortname, exist_ok=True)
                                        phi = function_builder.get_text_4_parameter(parameter=phi_param, function_shortname=func_shortname)
                                    else:
                                        phi = f"{sincos_comp_dict.get('phase_offset', 0)}"
                                    # Add sin or cos and pi to ldict
                                    function_builder.add_variable_to_ldict(variable_name="pi", variable_content=pi,
                                                                           function_shortname=func_shortname, exist_ok=True)
                                    if sincos_comp_dict["sincos"] == 'sin':
                                        function_builder.add_variable_to_ldict(variable_name="sin", variable_content=sin,
                                                                               function_shortname=func_shortname, exist_ok=True)
                                    else:  # It has to be cos
                                        function_builder.add_variable_to_ldict(variable_name="cos", variable_content=cos,
                                                                               function_shortname=func_shortname, exist_ok=True)
                                    ####################################################
                                    # Produce the text for the phase curve model returns
                                    ####################################################
                                    if multi:
                                        time_vect = f"{time_arg_name}[{i_inputoutput}]"
                                    else:
                                        time_vect = f"{time_arg_name}"
                                    if get_times_from_datasets:
                                        supersamp = SSE4instmodfname.get_supersamp(instmod.get_name(include_prefix=True, code_version=True, recursive=True))
                                        if supersamp > 1:
                                            logger.warning("Currently the spiderman model doesn't include supersampling !")
                                    if returns[func_shortname][i_inputoutput] == "":
                                        pre_text = ""
                                    else:
                                        pre_text = " + "
                                    if sincos_comp_dict["average"] == "zero":
                                        returns[func_shortname][i_inputoutput] += f"{pre_text}{amp} / 2 * {sincos_comp_dict['sincos']}(2 * pi / {period} / {sincos_comp_dict['factor_period']} * ({time_vect} - {tic}) + {phi})"
                                    else:  # it has to be semi-amplitude
                                        returns[func_shortname][i_inputoutput] += f"{pre_text}{amp} / 2 * (1 + {sincos_comp_dict['sincos']}(2 * pi / {period} / {sincos_comp_dict['factor_period']} * ({time_vect} - {tic}) + {phi}))"
                        ########################
                        # No other model for now
                        ########################
                        else:
                            raise NotImplementedError(f"phasecurve model {pc_component_model['model']} is not implemented.")

        ###############################################
        # Finalize the planets phasecurve only function
        ###############################################
        for planet in planets.values():
            func_shortname = f"{get_function_planet_shortname(planet)}{ext_func_pc_only}"
            get_condition(multi=multi, l_inst_model=l_inst_model, l_planet=[planet, ], parametrisation=parametrisation,
                          tab=tab, time_vec_name=time_vec_name, l_time_vec_name=l_time_vec_name, function_builder=function_builder,
                          function_shortname=func_shortname)
            function_builder.add_to_body_text(text=f"{tab}return {str(returns.pop(func_shortname)).strip('[]')}", function_shortname=func_shortname)

    return returns


def get_decorrelation(multi, planets, l_inst_model, l_dataset, get_times_from_datasets, decorrelation_config,
                      dataset_db, LCcat_model, tab, time_vec_name, l_time_vec_name, function_builder, l_function_shortname,
                      ext_func_fullname):
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
    get_times_from_datasets : bool
        If True the times at which the model should be computed will be taken from the datasets and
        included into the function. I False the user of the function will have to provide the times.
    decorrelation_config    : dict
        Dictionary describing the decorrelation model to use. The format of this disctionary is:
        {}
    dataset_db              : DatasetDatabase
        Dataset database to access the dataset for the decorrelation.
    LCcat_model              : LC_InstCat_Model
        LC_InstCat_Model instance for the current model
    tab                      : str
        String providing the space to put in front of each new line
    time_vec_name       : str
        Str used to designate the time vector
    l_time_vec_name     : str
        Str used to designate the list of time vectors
    function_builder            : FunctionBuilder
        FunctionBuilder instance
    ext_func_fullname           : str
        Extension to add and the end of the full name of the function simulating the transit only
        which is defined by this function in the function_builder

    Returns
    -------
    returns     : dict of list of str
        Dictionary of list of str giving the return for transit model for each function and each output
    """
    ########################
    # Initialise the outputs
    ########################
    returns = {}

    #################################################
    # Initialise the new function in function_builder
    #################################################
    # Extension for the shortname of the function that do the decorrelation only model
    decorr_func_shortname = "decorr"
    function_builder.add_new_function(shortname=decorr_func_shortname)
    function_builder.set_function_fullname(full_name=f"LC_sim_{decorr_func_shortname}{ext_func_fullname}", shortname=decorr_func_shortname)

    ########################################
    # Update the list of function to address
    ########################################
    l_function_shortname += [decorr_func_shortname, ]

    #############################################################################
    # Check if any of the instrument model is associated to a decorrelation model
    #############################################################################
    requires_decorr = False
    for instmod in l_inst_model:
        if decorrelation_config[instmod.full_name]["do"]:
            requires_decorr = True
            break

    if requires_decorr:
        ################################
        # Do the Model for each function
        ################################
        for func_shortname in l_function_shortname:

            ##############
            # Add the time
            ##############
            time_arg_name = add_time_argument(function_builder=function_builder, function_shortname=func_shortname,
                                              multi=multi, get_times_from_datasets=get_times_from_datasets,
                                              l_dataset=l_dataset, time_vec_name=time_vec_name, l_time_vec_name=l_time_vec_name,
                                              exist_ok=True)

            #############################################
            # Initialise the return text for the function
            #############################################
            returns[func_shortname] = []

            ####################################################
            # Do the Model for each function and each instrument
            ####################################################
            for i_inputoutput, (instmod, dst) in enumerate(zip(l_inst_model, l_dataset)):
                returns[func_shortname].append({})
                if decorrelation_config[instmod.full_name]["do"]:
                    # List of the datasets associated with the instrument model
                    l_dataset_name_instmod = [dst.dataset_name for i_dst, dst in enumerate(l_dataset) if l_inst_model[i_dst] == instmod]
                    for model_part, config_decorr_instmod_modelpart in decorrelation_config[instmod.full_name]["what to decorrelate"].items():
                        (returns[func_shortname][i_inputoutput][model_part]
                         ) = LCcat_model.create_text_decorr(multi=multi, inst_mod_obj=instmod, idx_inst_mod_obj=i_inputoutput,
                                                            l_dataset_name_instmod=l_dataset_name_instmod,
                                                            dataset_db=dataset_db, decorrelation_config_instmod=config_decorr_instmod_modelpart,
                                                            model_part=model_part, time_arg_name=time_arg_name,
                                                            function_builder=function_builder, function_shortname=func_shortname)

        ##########################################
        # Finalize the decorrelation only function
        ##########################################
        for func_shortname in [decorr_func_shortname, ]:
            function_builder.add_to_body_text(text=f"{tab}return {str(returns.pop(func_shortname)).strip('[]')}", function_shortname=func_shortname)

    return returns


# def combine_return_models(which_model, stellar_var, transit, phasecurve, decorrelation):
#     """Combine the different component of the lc model including the decorrelation if necessary.
#
#     This function creates the return for one datasimulator only and one instrument model object only
#
#     Arguments
#     ---------
#     which_model     : str
#         String saying which model you want to create. Possibilities are
#         'full' -> full model including all components
#         'pl_only' -> Only the planetary components (stellar_var and decorrelation are not used)
#         'decorrelation' -> Only the decorrelation components (only decorrelation is used)
#     stellar_var     : str
#         text providing the additive out of transit variations due to the host star (oot_var)
#     transit         : str
#         text providing the transit model component of the planet(s) contribution to the LC model
#     phasecurve      : str
#         text providing the phasecurve model component of the planet(s) contribution to the LC model
#     decorrelation   : dict_of_str
#         Text providing the decorrelation model component. There are different ways to decorrelate the
#         LC model and these ways are designed with strings. For now the ways implemented are
#         ["stellarflux", ]
#         Format:
#         - key : str
#             Giving which part of the model to apply the decorrelation to
#         - value : str
#             Giving the text of the decorrelation for this part of the model.
#             This text should include several decorrelation variables and several decorrelation types
#             (e.g. linear) if there are several.
#
#     Returns
#     -------
#     text_return : str
#         Text of the return for one datasim lc function.
#     """
#     if which_model == 'full':
#         tr_plusornot_pl = "+ " if transit != "" else ""
#         pc_plusornot_pl = "+ " if phasecurve != "" else ""
#         if "stellarflux" in decorrelation:
#             decorrelation_stellar_flux = " + (" + decorrelation["stellarflux"] + ")"
#         else:
#             decorrelation_stellar_flux = ""
#         return_text = f"(1 {stellar_var}) * (1 {decorrelation_stellar_flux} {tr_plusornot_pl + transit}{pc_plusornot_pl + phasecurve}), "
#     elif which_model == 'pl_only':
#         pc_plusornot_plonly = "+ " if ((transit != "") and (phasecurve != "")) else ""
#         return_text = f"{transit}{pc_plusornot_plonly + phasecurve}, "
#     elif which_model == 'decorrelation':
#         return_text = decorrelation + ", "
#     else:
#         raise ValueError(f"which_model should be in ['full', 'pl_only', 'decorrelation'] got {which_model}")
#     return return_text


def combine_return_models(multi, l_inst_model, time_vec_name, l_time_vec_name, reference_flux_level, tab, function_builder, function_shortname, transit=None, phasecurve=None,
                          inst_var=None, stellar_var=None, decorrelation=None):
    """Combine the different component of the lc model including the decorrelation if necessary.

    This function creates the return for one datasimulator only and one instrument model object only

    Arguments
    ---------
    multi                   : bool
        True if the datasim function needs to give multiple outputs.
    l_inst_model            : list_of_Instrument_Model
        List of the instrument models instances for each output of the datasim function. Each instrument model
        in this list is the instrument model which has to be used for the corresponding dataset provided in l_dataset.
    time_vec_name           : str
        Str used to designate the time vector
    l_time_vec_name         : str
        Str used to designate the list of time vectors
    reference_flux_level    : float
        Reference_flux_level for the photometry (in principle 1 or 0)
    tab                     : str
        String providing the space to put in front of each new line
    function_builder        : FunctionBuilder
        FunctionBuilder instance
    function_shortname      : str
        Short name of the function being built
    transit                 : list of str
        text providing the transit model component of the planet(s) contribution to the LC model
    phasecurve              : list of str
        text providing the phasecurve model component of the planet(s) contribution to the LC model
    inst_var                : list of str
        text providing the additive out of transit variations due to the host star (oot_var)
    decorrelation           : list of dict_of_str
        Text providing the decorrelation model component. There are different ways to decorrelate the
        LC model and these ways are designed with strings. For now the ways implemented are
        ["multiply_2_totalflux", "add_2_totalflux"]
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
    return_text = ""
    for i_inputoutput, instmod in enumerate(l_inst_model):
        if (stellar_var is not None) or (reference_flux_level != 0) or (inst_var is not None):
            if (stellar_var is None) and (inst_var is None):
                return_text += f"{reference_flux_level} * "
            else:
                if reference_flux_level == 0:
                    if (stellar_var is not None) and (inst_var is not None):
                        return_text += f"({stellar_var} + {inst_var[i_inputoutput]}) * "
                    if stellar_var is not None:
                        return_text += f"({stellar_var}) * "
                    if inst_var is not None:
                        return_text += f"({inst_var[i_inputoutput]}) * "
                else:
                    if (stellar_var is not None) and (inst_var is not None):
                        return_text += f"{reference_flux_level} + ({stellar_var} + {inst_var[i_inputoutput]}) * "
                    if stellar_var is not None:
                        return_text += f"{reference_flux_level} + ({stellar_var}) * "
                    if inst_var is not None:
                        return_text += f"{reference_flux_level} + ({inst_var[i_inputoutput]}) * "

        if (transit is not None) or (phasecurve is not None):
            if (transit is not None) and (phasecurve is not None):
                return_text += f"(1 + {transit[i_inputoutput]} + {phasecurve[i_inputoutput]})"
            elif transit is not None:
                return_text += f"(1 + {transit[i_inputoutput]})"
            elif phasecurve is not None:
                return_text += f"(1 + {phasecurve[i_inputoutput]})"

        if decorrelation is not None:
            if "multiply_2_totalflux" in decorrelation[i_inputoutput]:
                return_text += f" * ({decorrelation[i_inputoutput]['multiply_2_totalflux']})"
            if "add_2_totalflux" in decorrelation[i_inputoutput]:
                return_text += f" + ({decorrelation[i_inputoutput]['add_2_totalflux']})"

        if i_inputoutput < (len(l_inst_model) - 1):
            return_text += ", "

    function_builder.add_to_body_text(text=template_return.format(tab=tab, returns=return_text,
                                                                  returns_except=get_catchederror_return(multi=multi,
                                                                                                         l_inst_model=l_inst_model,
                                                                                                         time_vec_name=time_vec_name,
                                                                                                         l_time_vec_name=l_time_vec_name,
                                                                                                         function_builder=function_builder,
                                                                                                         function_shortname=function_shortname)),
                                      function_shortname=function_shortname)
