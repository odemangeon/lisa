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
from loguru import logger
from textwrap import dedent
# from copy import deepcopy, copy
from math import acos, degrees, sqrt
from numpy import ones_like, inf, mean, pi, sin, cos, abs, argsort, exp
from collections import defaultdict
from numbers import Number


try:
    from batman import TransitModel, TransitParams
    batman_imported = True
except (ModuleNotFoundError, ImportError):
    batman_imported = False
try:
    from pytransit import MandelAgol
    pytransit_imported = True
except (ModuleNotFoundError, ImportError):
    pytransit_imported = False
try:
    from spiderman import ModelParams
    spiderman_imported = True
except (ModuleNotFoundError, ImportError):
    spiderman_imported = False
try:
    from kelp import Model
    from kelp.jax import reflected_phase_curve_inhomogeneous
    kelp_imported = True
except (ModuleNotFoundError, ImportError):
    kelp_imported = False
from PyAstronomy.pyasl import foldAt

from . import get_function_planet_shortname
from ...dataset_and_instrument.lc import LC_Instrument
from ....core import function_whole_shortname
from ....core.model import par_vec_name
from ....core.model.datasim_docfunc import DatasimDocFunc
from ....core.model.datasimulator_toolbox import check_datasets_and_instmodels
from ....core.model.datasimulator_timeseries_toolbox import add_time_argument, time_vec, l_time_vec
from ....core.model.polynomial_model import get_polymodel
from .....tools.function_from_text_toolbox import FunctionBuilder  # , argskwargs
from .....posterior.exoplanet.model.convert import getaoverr, getomega_fast, getomega_deg_fast


template_return = """
{tab}try:
{tab}    return {returns}
{tab}except RuntimeError:
{tab}    return {returns_except}
"""
tab = "    "
template_return = dedent(template_return)


def create_datasimulator_LC(star, planets, ldmodel4instmodfname, LDs, transit_model, SSE4instmodfname,
                            phasecurve_model, occultation_model,
                            dataset_db, LCcat_model,
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
    ldmodel4instmodfname        : dict of dict of str
        Dictionary giving Limd darkening model to use for each instrument model and for each star
        Format: {"<instrument_model_name>: {"<star_name>": "<LD_model_name>"}
    LDs                         : dict of CoreLD
        Dictionary of subclasses of CoreLD instances providing the different limb-darkening models
        Format: {f"<star_name>_<LD model name>"": CoreLD_subclass instance, }
    transit_model               : dict
        Dictionary describing the transit model to use. The format of this disctionary is:
        {"do": True,  # Should we model the transit
         'model4instrument': {'<instrument_full_name>': '<name_given_to_a_model>', ...},  # For each instrument provide a model name, same name means same model
         'model_definitions': {'<name_given_to_a_model>': {'model': 'batman'}, ...},
         }
    SSE4instmodfname            : dict of dict of str int and float
        Dictionary giving the supersampling factor and the exposure time to use for each instrument model
        Format: {"instrument model name": {'supersamp': int_supersampling_factor, 'exptime': float_exposure_time}}
    phasecurve_model            : dict
        Dictionary describing the phasecurve model to use. The format of this disctionary is:
        {"do": True,  # Should we model the phasecurve
         'model4instrument': {'<instrument_full_name>': '<name_given_to_a_model>', ...},  # For each instrument provide a model name, same name means same model
         'model_definitions': {'<name_given_to_a_model>': {'args': {'Model_kwargs': {'lmax': lmax, 'filt': filt, 'stellar_spectrum': stellar_spectrum, 'T_s': T_s},
                                                                    'brightness_model_kwargs': {'n_theta': 20, 'n_phi': 200, 'cython': True, 'quad': False, 'check_sorted': True},
                                                                    'brightness_model': 'thermal'},
                                                           'model': 'kelp'}
                                                           }, ...
                               },
         }
    occultation_model            : dict
        Dictionary describing the occultation model to use. The format of this disctionary is:
        {"do": True,  # Should we do a specific model for the eclipse
         'model4instrument': {'<instrument_full_name>': '<name_given_to_a_model>', ...},  # For each instrument provide a model name, same name means same model
         'model_definitions': {'default_model': {'model': 'batman', 'modulate_pc': True}}}}
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
    # - Check the content of inst_models and datasets argument and transform them into two list l_inst_model
    # and l_dataset which provide the couple (inst_model_obj, dataset) for each output of the datasimulator
    # - Set multi True if the datasimulator has several outputs (several datasets to be simulated)
    # - Set the inst_model_fullnames argument for the Datasim_DocFunc (instmod_docf)
    # - Set the dst_ext extension to be used for the name of the datasimulator function
    # - Set the instcat_docf, instmod_docf, dtsts_docf to be used as arguments inst_cat, inst_model_fullname,
    # datasets in the Datasim_DocFunc.
    (l_dataset, l_inst_model, multi, inst_model_full_name, dst_ext, instcat_docf, instmod_docf,
     dtsts_docf) = check_datasets_and_instmodels(datasets, inst_models)

    #####################################################################################################
    ## Initialise the function in the function builder for the whole system and the planet and planet only functions
    #####################################################################################################
    # Create the FunctionBuilder
    func_builder = FunctionBuilder(parameter_vector_name=par_vec_name)
    # Initialise the whole function
    func_builder.add_new_function(shortname=function_whole_shortname)
    if multi:
        func_full_name_MultiOrDst_ext = "_multi"
    else:
        func_full_name_MultiOrDst_ext = f"{l_dataset[0].dataset_code_name}"
    func_builder.set_function_fullname(full_name=f"LC_sim_{function_whole_shortname}_{func_full_name_MultiOrDst_ext}", shortname=function_whole_shortname)
    # Initialise the planet function
    l_function_planet_shortname = [get_function_planet_shortname(planet) for planet in planets.values()]
    for function_shortname in l_function_planet_shortname:
        func_builder.add_new_function(shortname=function_shortname)
        func_builder.set_function_fullname(full_name=f"LC_sim_{function_shortname}_{func_full_name_MultiOrDst_ext}", shortname=function_shortname)

    ########################
    # Produce Transit models
    ########################
    returns_tr = get_transit(multi=multi, l_inst_model=l_inst_model, l_dataset=l_dataset, get_times_from_datasets=get_times_from_datasets,
                             transit_model=transit_model, ldmodel4instmodfname=ldmodel4instmodfname, LDs=LDs,
                             SSE4instmodfname=SSE4instmodfname, star=star, planets=planets,
                             tab=tab, time_vec_name=time_vec, l_time_vec_name=l_time_vec, function_builder=func_builder,
                             ext_func_fullname=func_full_name_MultiOrDst_ext,
                             )

    ############################
    # Produce phase curve models
    ############################
    returns_pc = get_phasecurve(multi=multi, l_inst_model=l_inst_model, l_dataset=l_dataset, get_times_from_datasets=get_times_from_datasets,
                                phasecurve_model=phasecurve_model, SSE4instmodfname=SSE4instmodfname,
                                star=star, planets=planets,
                                tab=tab, time_vec_name=time_vec, l_time_vec_name=l_time_vec, function_builder=func_builder,
                                ext_func_fullname=func_full_name_MultiOrDst_ext,
                                )

    ############################
    # Produce phase curve models
    ############################
    returns_occ = get_occultation(multi=multi, l_inst_model=l_inst_model, l_dataset=l_dataset, get_times_from_datasets=get_times_from_datasets,
                                  occultation_model=occultation_model, SSE4instmodfname=SSE4instmodfname,
                                  star=star, planets=planets,
                                  tab=tab, time_vec_name=time_vec, l_time_vec_name=l_time_vec, function_builder=func_builder,
                                  ext_func_fullname=func_full_name_MultiOrDst_ext,
                                  )

    ##############################
    # Produce contamination models
    ##############################
    returns_contam = get_contamination(l_inst_model=l_inst_model, l_dataset=l_dataset, tab=tab, function_builder=func_builder,
                                       l_function_shortname=[function_whole_shortname, ], ext_func_fullname=func_full_name_MultiOrDst_ext)

    #####################################################################
    # Get the condition text for the whole system function and the planet
    #####################################################################
    # the transit and phase curve only function already receive the conditions in the get_transit and get_phasecurve functions
    for func_shortname in [function_whole_shortname, ]:
        l_planet = list(planets.values())
        get_condition(multi=multi, l_inst_model=l_inst_model, l_planet=l_planet, tab=tab, time_vec_name=time_vec,
                      l_time_vec_name=l_time_vec, function_builder=func_builder, function_shortname=func_shortname,
                      transit_model=transit_model, occultation_model=occultation_model,
                      phasecurve_model=phasecurve_model,
                      )

    for planet in planets.values():
        func_shortname = f"{get_function_planet_shortname(planet)}"
        get_condition(multi=multi, l_inst_model=l_inst_model, l_planet=[planet, ], tab=tab, time_vec_name=time_vec,
                      l_time_vec_name=l_time_vec, function_builder=func_builder, function_shortname=func_shortname,
                      transit_model=transit_model, occultation_model=occultation_model,
                      phasecurve_model=phasecurve_model,
                      )

    ###########################
    # Produce the decorrelation
    ###########################
    d_l_d_decorr = get_decorrelation(multi=multi, planets=planets, l_inst_model=l_inst_model, l_dataset=l_dataset,
                                     get_times_from_datasets=get_times_from_datasets, dataset_db=dataset_db,
                                     LCcat_model=LCcat_model, tab=tab, time_vec_name=time_vec,
                                     l_time_vec_name=l_time_vec, function_builder=func_builder, l_function_shortname=[function_whole_shortname, ],
                                     ext_func_fullname=func_full_name_MultiOrDst_ext)

    ########################################
    # Produce instrumental variations models
    ########################################
    ## Get the d_l_inst_var and add the t_ref(s) to the list of arguments for the functions
    # d_l_inst_var is the list of strings giving the string representation of the out of transit variation model
    # for each couple instrument model - dataset in l_inst_model and l_dataset.
    # Format: ["oot model", ]
    d_l_inst_var = get_instvar(l_inst_model=l_inst_model, l_dataset=l_dataset, multi=multi,
                               function_builder=func_builder, l_function_shortname=[function_whole_shortname, ], ext_func_fullname=func_full_name_MultiOrDst_ext,
                               get_times_from_datasets=get_times_from_datasets, tab=tab, time_vec_name=time_vec, l_time_vec_name=l_time_vec,
                               LCcat_model=LCcat_model, dataset_db=dataset_db)

    #################################################
    # Produce stellar_var models (analytical, not GP)
    #################################################
    d_l_stellar_var = get_stellarvar(multi=multi, l_inst_model=l_inst_model, l_dataset=l_dataset, get_times_from_datasets=get_times_from_datasets,
                                     tab=tab, time_vec_name=time_vec, l_time_vec_name=l_time_vec, star=star,
                                     LCcat_model=LCcat_model, dataset_db=dataset_db,
                                     function_builder=func_builder, l_function_shortname=[function_whole_shortname, ],
                                     ext_func_fullname=func_full_name_MultiOrDst_ext)

    #######################################################################
    # Finalise the functions combining different outputs (whole and planet)
    #######################################################################
    # Function of the whole system
    for func_shortname in [function_whole_shortname, ]:
        combine_return_models(multi=multi, l_inst_model=l_inst_model, time_vec_name=time_vec, l_time_vec_name=l_time_vec,
                              reference_flux_level=1, tab=tab, function_builder=func_builder, function_shortname=func_shortname,
                              inst_var=d_l_inst_var.get(func_shortname, None), stellar_var=d_l_stellar_var.get(func_shortname, None),
                              transit=returns_tr.get(func_shortname, None), phasecurve=returns_pc.get(func_shortname, None),
                              occultation=returns_occ.get(func_shortname, None), contamination=returns_contam.get(func_shortname, None),
                              decorrelation=d_l_d_decorr.get(func_shortname, None)
                              )

    # Function of the planets only
    for func_shortname in l_function_planet_shortname:
        combine_return_models(multi=multi, l_inst_model=l_inst_model, time_vec_name=time_vec, l_time_vec_name=l_time_vec,
                              reference_flux_level=0, tab=tab, function_builder=func_builder, function_shortname=func_shortname,
                              inst_var=None, stellar_var=None, transit=returns_tr.get(func_shortname, None),
                              phasecurve=returns_pc.get(func_shortname, None), occultation=returns_occ.get(func_shortname, None),
                              contamination=None, decorrelation=None
                              )

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
            mand_kwargs = func_builder.get_l_mandatory_argument(function_shortname=func_shortname)
        else:
            mand_kwargs = None
        if len(func_builder.get_d_optional_argument(function_shortname=func_shortname)) > 0:
            opt_kwargs = func_builder.get_d_optional_argument(function_shortname=func_shortname)
        else:
            opt_kwargs = None
        logger.debug(f"Parameters for {func_shortname} LC simulator function :\n{dico_param_nb}")
        dico_docf[func_shortname] = DatasimDocFunc(function=func_builder._get_ldict(function_shortname=func_shortname)[func_builder.get_function_fullname(shortname=func_shortname)],
                                                   param_model_names_list=params_model,
                                                   params_model_vect_name=par_vec_name,
                                                   inst_cats_list=instcat_docf,
                                                   inst_model_fullnames_list=instmod_docf,
                                                   dataset_names_list=dtsts_docf,
                                                   include_dataset_kwarg=get_times_from_datasets,
                                                   mand_kwargs_list=mand_kwargs,
                                                   opt_kwargs_dict=opt_kwargs
                                                   )
    return dico_docf


def get_contamination(l_inst_model, l_dataset, tab, function_builder, l_function_shortname, ext_func_fullname):
    """Get the contamination contribution to the light-curve model

    Arguments
    ---------
    l_inst_model            : list_of_Instrument_Model
        Checked list of Instrument_Model instance(s).
    l_dataset               : list_of_Dataset
        Checked list of Dataset instance(s).
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
        of the contamination model for each couple instrument model - dataset in l_inst_model and l_dataset.
        Format of the dictionary:
        - key : key or keys specificied by l_function_shortname
        - value: List = ["<inst variation model for instrument1 and dataset1>", ...]
    """
    ########################
    # Initialise the outputs
    ########################
    returns = {}

    #############################################################################
    # Check if any of the instrument model needs a contamination model
    #############################################################################
    requires_contam = False
    for instmod in l_inst_model:
        if instmod.contam.main:
            if instmod.contam.free or float(instmod.contam.value) != 0.0:
                requires_contam = True
                break

    if requires_contam:
        #################################################
        # Initialise the new function in function_builder
        #################################################
        # Extension for the shortname of the function that do the decorrelation only model
        contam_func_shortname = "contam"
        function_builder.add_new_function(shortname=contam_func_shortname)
        function_builder.set_function_fullname(full_name=f"LC_sim_{contam_func_shortname}{ext_func_fullname}", shortname=contam_func_shortname)

        ########################################
        # Update the list of function to address
        ########################################
        l_function_shortname += [contam_func_shortname, ]

        ################################
        # Do the Model for each function
        ################################
        for function_shortname in l_function_shortname:
            returns[function_shortname] = []
            # For each instrument model and dataset, ...
            for ii, instmdl in enumerate(l_inst_model):
                returns[function_shortname].append("")
                # Add the contam parameter
                function_builder.add_parameter(parameter=instmdl.contam, function_shortname=function_shortname)
                text_contam_param = function_builder.get_text_4_parameter(parameter=instmdl.contam, function_shortname=function_shortname)
                if text_contam_param != 0.0:
                    returns[function_shortname][ii] += f"(1 - {text_contam_param})"

        #####################################
        # Finalize the inst_var only function
        #####################################
        for func_shortname in [contam_func_shortname, ]:
            l_return = [output_i if output_i != "" else 'None' for output_i in returns.pop(func_shortname)]
            function_builder.add_to_body_text(text=f"{tab}return {', '.join(l_return)}", function_shortname=func_shortname)

    return returns


def get_instvar(l_inst_model, l_dataset, multi, get_times_from_datasets, tab, time_vec_name, l_time_vec_name,
                LCcat_model, dataset_db, function_builder, l_function_shortname, ext_func_fullname):
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
    LCcat_model                 : LC_InstCat_Model
        Instance of the LC_InstCat_Model
    dataset_db                  : DatasetDatabase
        Dataset database, this will be used by the function to access the all the dataset of a given instrument model,
        not only the datasets to be simulated.
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
    return get_polymodel(multi=multi, l_inst_model=l_inst_model, l_dataset=l_dataset, get_times_from_datasets=get_times_from_datasets,
                         tab=tab, time_vec_name=time_vec_name, l_time_vec_name=l_time_vec_name, inst_cat_model=LCcat_model,
                         dataset_db=dataset_db, function_builder=function_builder, l_function_shortname=l_function_shortname,
                         polyonly_func_shortname="inst_var", ext_func_fullname=ext_func_fullname, name_coeff_const="DeltaF",
                         func_param_name=lambda order: LC_Instrument.get_polymodel_param_name(inst_model=None, order=order),
                         instrument_per_instrument_model=True, param_container=None, prefix_config=None,
                         )


def get_stellarvar(multi, l_inst_model, l_dataset, get_times_from_datasets,
                   tab, time_vec_name, l_time_vec_name,
                   star, LCcat_model, dataset_db,
                   function_builder, l_function_shortname, ext_func_fullname):
    """Get the stellar variation contribution to the LCs including the systemic velocity

    Arguments
    ---------
    multi                   : bool
        True if the datasim function needs to give multiple outputs.
        Not used right now but there to be able to produce instrumental drift in the future
    l_inst_model            : list_of_Instrument_Model
        Checked list of Instrument_Model instance(s).
    l_dataset               : list_of_Dataset
        Checked list of Dataset instance(s).
    get_times_from_datasets : bool
        True the datasets should be used to extract the time vectors
        Not used right now but there to be able to produce instrumental drift in the future
    tab                     : str
        String providing the space to put in front of each new line
    time_vec_name           : str
        Str used to design the time vector
        Not used right now but there to be able to produce instrumental drift in the future
    l_time_vec_name         : str
        Str used to design the list of time vector
        Not used right now but there to be able to produce instrumental drift in the future
    star                        : Star
        Star object
    LCcat_model                 : LC_InstCat_Model
        Instance of the LC_InstCat_Model
    dataset_db                  : DatasetDatabase
        Dataset database, this will be used by the function to access the all the LC dataset,
        not only the datasets to be simulated.
    function_builder        : FunctionBuilder
        Function builder instance
    l_function_shortname    : list of str
        List of the short name of the functions for which you want to add the instrument variation component
    ext_func_fullname       : str
        Extension to add and the end of the full name of the function simulating the instrumental variation only
        which is defined by this function in the function_builder

    Returns
    -------
    returns     : dict of list of str
        Dictionary of list of str giving the return for stellarvar for each function and each output
    """
    return get_polymodel(multi=multi, l_inst_model=l_inst_model, l_dataset=l_dataset, get_times_from_datasets=get_times_from_datasets,
                         tab=tab, time_vec_name=time_vec_name, l_time_vec_name=l_time_vec_name, inst_cat_model=LCcat_model,
                         dataset_db=dataset_db, function_builder=function_builder, l_function_shortname=l_function_shortname,
                         polyonly_func_shortname="stellar_var", ext_func_fullname=ext_func_fullname, name_coeff_const=star.__name_coeff_const_LC__,
                         func_param_name=lambda order: star.get_polymodel_param_name(order=order, inst_cat=LCcat_model.inst_cat),
                         instrument_per_instrument_model=False, param_container=star, prefix_config=LCcat_model.inst_cat,
                         )


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


def get_condition(multi, l_inst_model, l_planet, tab, time_vec_name, l_time_vec_name, function_builder,
                  function_shortname, transit_model=None, occultation_model=None, phasecurve_model=None
                  ):
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
    transit_model        :
    occultation_model    :
    """
    error_return = get_catchederror_return(multi=multi, l_inst_model=l_inst_model, time_vec_name=time_vec_name,
                                           l_time_vec_name=l_time_vec_name, function_builder=function_builder,
                                           function_shortname=function_shortname)
    l_orbital_model = []
    l_Rrat = []
    l_model_name = []
    l_planet_name = []
    for models in [transit_model, occultation_model, phasecurve_model]:
        for planet in l_planet:
            planet_name = planet.get_name()
            if (models is not None) and models.get_do(planet_name=planet_name):
                for inst_model_obj in l_inst_model:
                    instmod_fullname = inst_model_obj.full_name
                    if models == phasecurve_model:
                        l_model_definition = models.get_l_model(planet_name=planet_name, inst_model_fullname=instmod_fullname)
                    else:
                        l_model_definition = [models.get_model(planet_name=planet_name, inst_model_fullname=instmod_fullname), ]
                    for model_definition in l_model_definition:
                        orbital_model = model_definition.get_orbital_model(inst_model_fullname=instmod_fullname)
                        parameters = model_definition.get_parameters(inst_model_fullname=instmod_fullname, object_category=None)
                        add = orbital_model not in l_orbital_model
                        if not(add):
                            add = True
                            for idx, orb_mod in enumerate(l_orbital_model):
                                if orb_mod is orbital_model:
                                    if parameters['planet']['Rrat'] is l_Rrat[idx]:
                                        add = False
                                        break
                        if add:
                            l_orbital_model.append(orbital_model)
                            l_Rrat.append(parameters['planet']['Rrat'])
                            l_model_name.append(model_definition.model_name)
                            l_planet_name.append(planet_name)
    l_condition = []
    for orbital_model, Rrat, model_name, planet_name in zip(l_orbital_model, l_Rrat, l_model_name, l_planet_name):
        if not(orbital_model.use_aR):
            if not(function_builder.is_done_in_text(name=f"aR_{planet_name}", function_shortname=function_shortname)):
                rhostar = function_builder.get_text_4_parameter(parameter=parameters['star']['rho'], function_shortname=function_shortname)
                period = function_builder.get_text_4_parameter(parameter=parameters['star']['rho'], function_shortname=function_shortname)
                function_builder.add_variable_to_ldict(variable_name="getaoverr", variable_content=getaoverr, function_shortname=function_shortname, exist_ok=True)
                if not(function_builder.is_done_in_text(name=f"ecc_{planet_name}", function_shortname=function_shortname)) or not(function_builder.is_done_in_text(name=f"omega_{planet_name}_deg", function_shortname=function_shortname)):
                    ecosw = function_builder.get_text_4_parameter(parameter=parameters['planet']['ecosw'], function_shortname=function_shortname)
                    esinw = function_builder.get_text_4_parameter(parameter=parameters['planet']['esinw'], function_shortname=function_shortname)
                    if not(function_builder.is_done_in_text(name=f"ecc_{planet_name}", function_shortname=function_shortname)):
                        function_builder.add_variable_to_ldict(variable_name="sqrt", variable_content=sqrt, function_shortname=function_shortname, exist_ok=True)
                        function_builder.add_to_body_text(text=f"{tab}ecc_{planet_name} = sqrt({ecosw} * {ecosw} + {esinw} * {esinw})\n", function_shortname=function_shortname)
                        function_builder.add_to_done_in_text(name=f"ecc_{planet_name}", function_shortname=function_shortname)
                    if not(function_builder.is_done_in_text(name=f"omega_{planet_name}_deg", function_shortname=function_shortname)):
                        function_builder.add_variable_to_ldict(variable_name="getomega_deg_fast", variable_content=getomega_deg_fast, function_shortname=function_shortname, exist_ok=True)
                        function_builder.add_to_body_text(text=f"{tab}omega_{planet_name}_deg = getomega_deg_fast({ecosw}, {esinw})\n", function_shortname=function_shortname)
                        function_builder.add_to_done_in_text(name=f"omega_{planet_name}_deg", function_shortname=function_shortname)
                function_builder.add_to_body_text(text=f"{tab}aR_{planet_name} = getaoverr({period}, {rhostar}, ecc_{planet_name}, omega_{planet_name}_deg)\n", function_shortname=function_shortname)
                function_builder.add_to_done_in_text(name=f"aR_{planet_name}", function_shortname=function_shortname)
            aR = f"aR_{planet_name}"
        else:
            aR = function_builder.get_text_4_parameter(parameter=parameters['planet']['aR'], function_shortname=function_shortname)
        # if function_builder.is_parameter(parameter=parameters['planet']['Rrat'], function_shortname=function_shortname):
        #     Rrat = function_builder.get_text_4_parameter(parameter=planet.Rrat, function_shortname=function_shortname)
        #     function_builder.add_to_body_text(text=f"{tab}condition_{planet_name} = ({aR} < ((1.5 / (1 - ecc_{planet_name})) + {Rrat}))\n", function_shortname=function_shortname)
        # else:
        #     function_builder.add_to_body_text(text=f"{tab}condition_{planet_name} = ({aR} < (1.5 / (1 - ecc_{planet_name})))\n", function_shortname=function_shortname)
        Rrat_text = function_builder.get_text_4_parameter(parameter=Rrat, function_shortname=function_shortname)
        condition_name = f"condition_{planet_name}"
        if model_name != '':
            condition_name += f"_{model_name}"
        function_builder.add_to_body_text(text=f"{tab}{condition_name} = ({aR} < ((1.5 / (1 - ecc_{planet_name})) + {Rrat_text}))\n", function_shortname=function_shortname)
        l_condition.append(condition_name)
    if len(l_condition) > 1:
        condition_text = " or ".join(l_condition)
    elif len(l_condition) == 1:
        condition_text = l_condition[0]
    else:
        condition_text = None
    if condition_text is not None:
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
    function_builder.add_variable_to_ldict(variable_name="ones_like", variable_content=ones_like, function_shortname=function_shortname, exist_ok=True)
    function_builder.add_variable_to_ldict(variable_name="inf", variable_content=inf, function_shortname=function_shortname, exist_ok=True)

    l_returns = []
    for i_instmodel in range(len(l_inst_model)):
        if multi:
            l_returns.append(f"ones_like({l_time_vec_name}[{i_instmodel}]) * (- inf)")
        else:
            l_returns.append(f"ones_like({time_vec_name}) * (- inf)")

    return ", ".join(l_returns)


def get_transit(multi, l_inst_model, l_dataset, get_times_from_datasets, transit_model,
                ldmodel4instmodfname, LDs, SSE4instmodfname, star, planets, tab,
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

    ##########################################################################################
    # Initialise the list to keep track of the updates of the TransitParams instance of Batman
    ##########################################################################################
    # Init the list that will indicate that rp has been updated in the batman TransitParams instances used for the occultation
    rp_updates = defaultdict(list)
    # Init the list that will indicate that LD has been updated in the batman TransitParams instances used for the occultation
    ld_updates = defaultdict(list)

    ##############################
    # Do the Model for each planet
    ##############################
    for planet in planets.values():
        planet_name = planet.get_name()
        if transit_model.get_do(planet_name=planet_name):
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
            # if parametrisation == "Multis":
            #     for func_shortname in l_function_shortname_4_planet:
            #         function_builder.add_parameter(parameter=star.rho, function_shortname=func_shortname, exist_ok=True)
            #
            # # Add the planet parameters: Rrat, ecosw, esinw, cosinc, P, tic and aR if needed
            # l_param = [planet.Rrat, planet.ecosw, planet.esinw, planet.cosinc, planet.P, planet.tic]
            # if parametrisation != "Multis":
            #     l_param.append(planet.aR)
            # for param in l_param:
            #     for func_shortname in l_function_shortname_4_planet:
            #         function_builder.add_parameter(parameter=param, function_shortname=func_shortname, exist_ok=True)

            ####################################################################
            # Do the Model for each planet and each instrument and each function
            ####################################################################
            for func_shortname in l_function_shortname_4_planet:

                for i_inputoutput, (instmod, dst) in enumerate(zip(l_inst_model, l_dataset)):
                    instmod_fullname = instmod.full_code_name

                    ####################################################################################
                    # Get the transit model implementation definition for the planet and the instrument
                    ####################################################################################
                    model_definition = transit_model.get_model(planet_name=planet_name, inst_model_fullname=instmod.full_name)

                    ##############
                    # Batman model
                    ##############
                    if model_definition.category == "batman":
                        if not(batman_imported):
                            raise ValueError("Batman doesn't seems to be installed. The import failed.")

                        ## Add the limb darkening parameters
                        LD_mod_name = ldmodel4instmodfname[instmod_fullname][star.code_name]
                        LD_mod = LDs[star.code_name + "_" + LD_mod_name]
                        for param in LD_mod.get_list_params(main=True):
                            if not(function_builder.is_parameter(parameter=param, function_shortname=func_shortname)):
                                function_builder.add_parameter(parameter=param, function_shortname=func_shortname, exist_ok=True)

                        text_transit, _ = do_batman_transit_occultation_models(function_builder=function_builder,
                                                                               function_shortname=func_shortname,
                                                                               model_definition=model_definition,
                                                                               planet=planet, star=star,
                                                                               inst_model_obj=instmod, dataset=dst,
                                                                               get_times_from_datasets=get_times_from_datasets,
                                                                               time_arg_name=time_arg_name,
                                                                               SSE4instmodfname=SSE4instmodfname,
                                                                               do_transit=True,
                                                                               do_occultation=False,
                                                                               l_dataset=l_dataset, multi=multi,
                                                                               i_inputoutput=i_inputoutput,
                                                                               ldmodel4instmodfname=ldmodel4instmodfname,
                                                                               LDs=LDs, rp_updates=rp_updates,
                                                                               ld_updates=ld_updates,
                                                                               )

                        ## writing the returns
                        if returns[func_shortname][i_inputoutput] == "":
                            pre_text = ""
                        else:
                            pre_text = " + "
                        returns[func_shortname][i_inputoutput] += f"{pre_text}m_batman_{planet_name}_{instmod_fullname}_dst{dst.number}.light_curve(params_{planet_name}_{instmod_fullname}) - 1 "

                    #################
                    # Pytransit model
                    #################
                    elif model_definition.category == "pytransit":
                        orbital_model = model_definition.get_orbital_model(inst_model_fullname=instmod_fullname)
                        if not(pytransit_imported):
                            raise ValueError("pytransit doesn't seems to be installed. The import failed.")
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
                        if not(function_builder.is_done_in_text(name=f"ecc_{planet_name}", function_shortname=func_shortname)):
                            function_builder.add_variable_to_ldict(variable_name="sqrt", variable_content=sqrt, function_shortname=func_shortname, exist_ok=True)
                            function_builder.add_to_body_text(text=f"{tab}ecc_{planet_name} = sqrt({ecosw} * {ecosw} + {esinw} * {esinw})\n", function_shortname=func_shortname)
                            function_builder.add_to_done_in_text(name=f"ecc_{planet_name}", function_shortname=func_shortname)
                        if not(function_builder.is_done_in_text(name=f"omega_{planet_name}", function_shortname=func_shortname)):
                            function_builder.add_variable_to_ldict(variable_name="getomega_fast", variable_content=getomega_fast, function_shortname=func_shortname, exist_ok=True)
                            function_builder.add_to_body_text(text=f"{tab}omega_{planet_name} = getomega_fast({esinw}, {ecosw})\n", function_shortname=func_shortname)
                            function_builder.add_to_done_in_text(name=f"omega_{planet_name}", function_shortname=func_shortname)
                        cosinc = function_builder.get_text_4_parameter(parameter=planet.cosinc, function_shortname=func_shortname)
                        if not(function_builder.is_done_in_text(name=f"inc_{planet_name}", function_shortname=func_shortname)):
                            function_builder.add_variable_to_ldict(variable_name="acos", variable_content=acos, function_shortname=func_shortname, exist_ok=True)
                            function_builder.add_to_body_text(text=f"{tab}inc_{planet_name} = acos({cosinc})\n", function_shortname=func_shortname)
                            function_builder.add_to_done_in_text(name=f"inc_{planet_name}", function_shortname=func_shortname)
                        period = function_builder.get_text_4_parameter(parameter=planet.P, function_shortname=func_shortname)
                        if not(orbital_model.use_aR):
                            if not(function_builder.is_done_in_text(name=f"aR_{planet_name}", function_shortname=func_shortname)):
                                rhostar = function_builder.get_text_4_parameter(parameter=star.rhostar, function_shortname=func_shortname)
                                function_builder.add_variable_to_ldict(variable_name="getaoverr", variable_content=getaoverr, function_shortname=func_shortname, exist_ok=True)
                                function_builder.add_variable_to_ldict(variable_name="degrees", variable_content=degrees, function_shortname=func_shortname, exist_ok=True)
                                function_builder.add_to_body_text(text=f"{tab}aR_{planet_name} = getaoverr({period}, {rhostar}, ecc_{planet_name}, degrees(omega_{planet_name}))\n", function_shortname=func_shortname)
                                function_builder.add_to_done_in_text(name=f"aR_{planet_name}", function_shortname=func_shortname)
                        # Get the text for the remaining planet parameters
                        if not(orbital_model.use_aR):
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
                        raise ValueError(f"Transit model {model_definition.category} is not recognized.")

    ############################################
    # Finalize the planets transit only function
    ############################################
    for planet in planets.values():
        planet_name = planet.get_name()
        if transit_model.get_do(planet_name=planet_name):
            func_shortname = f"{get_function_planet_shortname(planet)}{ext_func_tr_only}"
            get_condition(multi=multi, l_inst_model=l_inst_model, l_planet=[planet, ], tab=tab, time_vec_name=time_vec_name,
                          l_time_vec_name=l_time_vec_name, function_builder=function_builder, function_shortname=func_shortname,
                          transit_model=transit_model, occultation_model=None,
                          phasecurve_model=None,
                          )
            function_builder.add_to_body_text(text=template_return.format(tab=tab, returns=f"{', '.join(returns.pop(func_shortname))}",
                                                                          returns_except=get_catchederror_return(multi=multi,
                                                                                                                 l_inst_model=l_inst_model,
                                                                                                                 time_vec_name=time_vec_name,
                                                                                                                 l_time_vec_name=l_time_vec_name,
                                                                                                                 function_builder=function_builder,
                                                                                                                 function_shortname=func_shortname)),
                                              function_shortname=func_shortname)

    return returns


def get_phasecurve(multi, l_inst_model, l_dataset, get_times_from_datasets, phasecurve_model,
                   SSE4instmodfname, star, planets, tab,
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

    ##########################################################################################
    # Initialise the list to keep track of the updates of the TransitParams instance of Batman
    ##########################################################################################
    # Init the list that will indicate that t_secondary has been updated in the batman TransitParams instances used for the occultation
    t_sec_updates = defaultdict(list)
    # Init the list that will indicate that fp has been set to 1 in the batman TransitParams instances used for the occultation
    fp_updates = defaultdict(list)
    rp_updates = defaultdict(list)

    ##############################
    # Do the Model for each planet
    ##############################
    for planet in planets.values():
        planet_name = planet.get_name()
        if phasecurve_model.get_do(planet_name=planet_name):
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
                    l_model_def = phasecurve_model.get_l_model(planet_name=planet_name, inst_model_fullname=instmod.full_name)
                    orbital_model = phasecurve_model.orbital_models.get_model(planet_name=planet_name, inst_model_fullname=instmod.full_name)

                    # For each component of the phasec curve model
                    for pc_component_model in l_model_def:
                        component_name = pc_component_model.model_name

                        ###########################################
                        # Add the parameters required for the model
                        ###########################################
                        # make sure that all the required parameters are added to the function in the function_builder
                        parameters = pc_component_model.get_parameters(inst_model_fullname=instmod_fullname, object_category=None)
                        for object_category in parameters:
                            for param in parameters[object_category].values():
                                function_builder.add_parameter(parameter=param, function_shortname=func_shortname, exist_ok=True)

                        ########################################
                        # Spiderman model with Zhang Thermal map
                        ########################################
                        if pc_component_model.category == "spiderman-zhang":
                            if not(spiderman_imported):
                                raise ValueError("spiderman doesn't seems to be installed. The import failed.")

                            # Add the lightcurve_kwargs to ldict
                            if len(pc_component_model.pc_component_model) > 0:
                                if not(function_builder.is_in_ldict(variable_name=f"{component_name}_lightcurve_kwargs", function_shortname=func_shortname)):
                                    function_builder.add_variable_to_ldict(variable_name=f"{component_name}_lightcurve_kwargs", variable_content=pc_component_model.pc_component_model.copy(),
                                                                           function_shortname=func_shortname, exist_ok=True)
                                lightcurve_kwargs = f", **{component_name}_lightcurve_kwargs"
                            else:
                                lightcurve_kwargs = ""

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
                                period = function_builder.get_text_4_parameter(parameter=parameters['orbit']['P'], function_shortname=func_shortname)
                                ecosw = function_builder.get_text_4_parameter(parameter=parameters['orbit']['ecosw'], function_shortname=func_shortname)
                                esinw = function_builder.get_text_4_parameter(parameter=parameters['orbit']['esinw'], function_shortname=func_shortname)
                                cosinc = function_builder.get_text_4_parameter(parameter=parameters['orbit']['cosinc'], function_shortname=func_shortname)
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
                                if not(orbital_model.use_aR):
                                    if not(function_builder.is_done_in_text(name=f"aR_{planet_name}", function_shortname=func_shortname)):
                                        rhostar = function_builder.get_text_4_parameter(parameter=parameters['orbit']['rho'], function_shortname=func_shortname)
                                        function_builder.add_variable_to_ldict(variable_name="getaoverr", variable_content=getaoverr, function_shortname=func_shortname, exist_ok=True)
                                        function_builder.add_to_body_text(text=f"{tab}aR_{planet_name} = getaoverr({period}, {rhostar}, ecc_{planet_name}, omega_{planet_name})\n", function_shortname=func_shortname)
                                        function_builder.add_to_done_in_text(name=f"aR_{planet_name}", function_shortname=func_shortname)
                                ## preambule: Update the parameter values in the TransitParams object
                                tic = function_builder.get_text_4_parameter(parameter=parameters['orbit']['tic'], function_shortname=func_shortname)
                                Rrat = function_builder.get_text_4_parameter(parameter=parameters['planet']['Rrat'], function_shortname=func_shortname)
                                a_au = function_builder.get_text_4_parameter(parameter=parameters['planet']['a'], function_shortname=func_shortname)
                                u1 = function_builder.get_text_4_parameter(parameter=parameters['planet']['u1'], function_shortname=func_shortname)
                                u2 = function_builder.get_text_4_parameter(parameter=parameters['planet']['u2'], function_shortname=func_shortname)
                                xi = function_builder.get_text_4_parameter(parameter=parameters['planet']['xi'], function_shortname=func_shortname)
                                Tn = function_builder.get_text_4_parameter(parameter=parameters['planet']['Tn'], function_shortname=func_shortname)
                                deltaT = function_builder.get_text_4_parameter(parameter=parameters['planet']['delta_T'], function_shortname=func_shortname)
                                Teff = function_builder.get_text_4_parameter(parameter=parameters['star']['Teff'], function_shortname=func_shortname)
                                if not(orbital_model.use_aR):
                                    aR = f"aR_{planet_name}\n"
                                else:
                                    aR = function_builder.get_text_4_parameter(parameter=parameters['orbit']['aR'], function_shortname=func_shortname)
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

                        #########################
                        # Lambertian sphere model
                        #########################
                        elif pc_component_model.category == "lambertian":
                            #########################
                            # Get text for parameters
                            #########################
                            # Orbital Period
                            period = function_builder.get_text_4_parameter(parameter=parameters['orbit']['P'], function_shortname=func_shortname)
                            # Time of inferior conjunction
                            tic = function_builder.get_text_4_parameter(parameter=parameters['orbit']['tic'], function_shortname=func_shortname)
                            # Amplitude
                            amp = function_builder.get_text_4_parameter(parameter=parameters['orbit']['A'], function_shortname=func_shortname)
                            ###################################
                            # Add sin, cos, pi and abs to ldict
                            ###################################
                            function_builder.add_variable_to_ldict(variable_name="pi", variable_content=pi,
                                                                   function_shortname=func_shortname, exist_ok=True)
                            function_builder.add_variable_to_ldict(variable_name="sin", variable_content=sin,
                                                                   function_shortname=func_shortname, exist_ok=True)
                            function_builder.add_variable_to_ldict(variable_name="cos", variable_content=cos,
                                                                   function_shortname=func_shortname, exist_ok=True)
                            function_builder.add_variable_to_ldict(variable_name="abs", variable_content=abs,
                                                                   function_shortname=func_shortname, exist_ok=True)
                            ###########################
                            # Add phase_angle computation
                            ###########################
                            # Be careful the orbital phase is define to be 0 during superior conjunction here
                            if not(function_builder.is_done_in_text(name="phase_angle", function_shortname=func_shortname)):
                                function_builder.add_to_body_text(text=f"{tab}phase_angle = (({time_arg_name} - {tic}) / {period} + pi) % (2 * pi)\n", function_shortname=func_shortname)
                                function_builder.add_to_done_in_text(name="phase_angle", function_shortname=func_shortname)
                            ###################
                            # Compute the model
                            ###################
                            # Reference: Sara Seager, 2010, Book: Exoplanet atmosphere, page 45, equation 3.58
                            # Warning: The absolute value of the phase function is not written in Seager
                            # but it's are necessary for the equation to be valid
                            # outside of the range [0, pi] in phase angle.
                            if multi:
                                phase_angle_vect = f"phase_angle[{i_inputoutput}]"  # WARNING: Does take into account the orbital eccentricity
                            else:
                                phase_angle_vect = "phase_angle"
                            if get_times_from_datasets:
                                supersamp = SSE4instmodfname.get_supersamp(instmod.get_name(include_prefix=True, code_version=True, recursive=True))
                                if supersamp > 1:
                                    logger.warning("Currently the lambertian sphere model doesn't include supersampling !")
                            if returns[func_shortname][i_inputoutput] == "":
                                pre_text = ""
                            else:
                                pre_text = " + "
                            returns[func_shortname][i_inputoutput] += f"{pre_text}{amp} / pi * abs(sin({phase_angle_vect}) + (pi - {phase_angle_vect}) * cos({phase_angle_vect}))"

                        #######################
                        # Sine and Cosine model
                        #######################
                        elif (pc_component_model.category == "sincos") or (pc_component_model.category == "ellipsoidal") or (pc_component_model.category == "beaming"):
                            if pc_component_model.occultation:
                                _, text_occ = do_batman_transit_occultation_models(function_builder=function_builder,
                                                                                   function_shortname=func_shortname,
                                                                                   model_definition=pc_component_model,
                                                                                   planet=planet, star=star, inst_model_obj=instmod,
                                                                                   dataset=dst,
                                                                                   get_times_from_datasets=get_times_from_datasets,
                                                                                   time_arg_name=time_arg_name, SSE4instmodfname=SSE4instmodfname,
                                                                                   do_transit=False, do_occultation=True,
                                                                                   l_dataset=l_dataset, multi=multi,
                                                                                   i_inputoutput=i_inputoutput,
                                                                                   normalize_occultation=True,
                                                                                   rp_updates=rp_updates,
                                                                                   fp_updates=fp_updates, t_sec_updates=t_sec_updates
                                                                                   )
                                text_occ = f" * ({text_occ})"
                            else:
                                text_occ = ""

                            if pc_component_model.sincos is None:
                                ################
                                # Add parameters
                                ################
                                constant = function_builder.get_text_4_parameter(parameter=parameters['planet']['C'], function_shortname=func_shortname)
                                if returns[func_shortname][i_inputoutput] == "":
                                    pre_text = ""
                                else:
                                    pre_text = " + "
                                returns[func_shortname][i_inputoutput] += f"{pre_text}{constant}{text_occ}"
                            else:
                                ################
                                # Add parameters
                                ################
                                # Orbital Period
                                period = function_builder.get_text_4_parameter(parameter=parameters['orbit']['P'], function_shortname=func_shortname)
                                # Time of inferior conjunction
                                tic = function_builder.get_text_4_parameter(parameter=parameters['orbit']['tic'], function_shortname=func_shortname)
                                # Amplitude
                                amp = function_builder.get_text_4_parameter(parameter=parameters['planet']['A'], function_shortname=func_shortname)
                                # Phase Offset
                                if pc_component_model.phase_offset == "param":
                                    phi = function_builder.get_text_4_parameter(parameter=parameters['planet']['Phi'], function_shortname=func_shortname)
                                else:
                                    phi = f"{pc_component_model.phase_offset}"
                                # flux offset
                                if pc_component_model.flux_offset == "param":
                                    flux_offset = function_builder.get_text_4_parameter(parameter=parameters['planet']['Foffset'], function_shortname=func_shortname)
                                elif isinstance(pc_component_model.flux_offset, Number):
                                    flux_offset = f"{pc_component_model.flux_offset}"
                                # Add sin or cos and pi to ldict
                                function_builder.add_variable_to_ldict(variable_name="pi", variable_content=pi,
                                                                       function_shortname=func_shortname, exist_ok=True)
                                if pc_component_model.sincos == 'sin':
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
                                        logger.warning("Currently the sincos model doesn't include supersampling !")
                                if returns[func_shortname][i_inputoutput] == "":
                                    pre_text = ""
                                else:
                                    pre_text = " + "
                                if pc_component_model.flux_offset == "zero":
                                    returns[func_shortname][i_inputoutput] += f"{pre_text}{amp} / 2 * {pc_component_model.sincos}(2 * pi / {period} / {pc_component_model.factor_period} * ({time_vect} - {tic}) + {phi}){text_occ}"
                                elif pc_component_model.flux_offset == "semi-amplitude":
                                    returns[func_shortname][i_inputoutput] += f"{pre_text}{amp} / 2 * (1 + {pc_component_model.sincos}(2 * pi / {period} / {pc_component_model.factor_period} * ({time_vect} - {tic}) + {phi})){text_occ}"
                                else:  # it has to be 'param'
                                    returns[func_shortname][i_inputoutput] += f"{pre_text}({amp} / 2 * (1 + {pc_component_model.sincos}(2 * pi / {period} / {pc_component_model.factor_period} * ({time_vect} - {tic}) + {phi})) + {flux_offset}){text_occ}"

                        ##########################
                        # Kelp thermal phase curve
                        ##########################
                        elif pc_component_model.category == "kelp-thermal":
                            if not(kelp_imported):
                                raise ValueError("Kelp doesn't seems to be installed. The import failed.")

                            #######################
                            # Create the Kelp Model
                            #######################
                            ## Create the kelp Model object model_kelp_{planet_name}_{instmod_fullname} and put in ldict
                            if not(function_builder.is_in_ldict(variable_name=f"model_kelp_{planet_name}_{instmod_fullname}", function_shortname=func_shortname)):
                                stellar_spectrum = pc_component_model.Model_kwargs.get('stellar_spectrum', None)
                                l_max = pc_component_model.Model_kwargs.get('l_max', 1)
                                if l_max == 1:
                                    C_ml = [[0],
                                            [0, 0.1, 0]]
                                else:
                                    raise ValueError("For now only lmax = 1 is implemented in Kelp model")
                                if stellar_spectrum is None:
                                    model_kelp_pl_inst = Model(hotspot_offset=0, alpha=0.6, omega_drag=4.5,
                                                               A_B=0, C_ml=C_ml, lmax=1, a_rs=5, rp_a=0.02,
                                                               T_s=5777, filt=pc_component_model.Model_kwargs.get('filt', None)
                                                               )
                                else:
                                    model_kelp_pl_inst = Model(hotspot_offset=0, alpha=0.6, omega_drag=4.5,
                                                               A_B=0, C_ml=C_ml, lmax=1, a_rs=5, rp_a=0.02,
                                                               T_s=pc_component_model.Model_kwargs['T_s'],
                                                               filt=pc_component_model.Model_kwargs.get('filt', None),
                                                               stellar_spectrum=stellar_spectrum
                                                               )
                                function_builder.add_variable_to_ldict(variable_name=f"model_kelp_{planet_name}_{instmod_fullname}",
                                                                       variable_content=model_kelp_pl_inst, function_shortname=func_shortname, exist_ok=False)

                            ## Create the brightness_model_kwargs dictionary which contains the non-physical parameters for the computation of the phase curve 
                            # that will be passed to model_kelp_{planet_name}_{instmod_fullname}.thermal_phase_curve and put in ldict
                            if not(function_builder.is_in_ldict(variable_name=f"kelp_pc_kwargs_{planet_name}_{instmod_fullname}", function_shortname=func_shortname)):
                                kelp_pc_kwargs_pl_inst = pc_component_model.pc_kwargs.copy()
                                function_builder.add_variable_to_ldict(variable_name=f"kelp_pc_kwargs_{planet_name}_{instmod_fullname}",
                                                                       variable_content=kelp_pc_kwargs_pl_inst, function_shortname=func_shortname, exist_ok=False)
                            ## Do the text for the occultation
                            _, text_occ = do_batman_transit_occultation_models(function_builder=function_builder,
                                                                               function_shortname=func_shortname,
                                                                               model_definition=pc_component_model,
                                                                               planet=planet, star=star, inst_model_obj=instmod,
                                                                               dataset=dst,
                                                                               get_times_from_datasets=get_times_from_datasets,
                                                                               time_arg_name=time_arg_name, SSE4instmodfname=SSE4instmodfname,
                                                                               do_transit=False, do_occultation=True,
                                                                               l_dataset=l_dataset, multi=multi,
                                                                               i_inputoutput=i_inputoutput,
                                                                               normalize_occultation=True,
                                                                               rp_updates=rp_updates,
                                                                               fp_updates=fp_updates, t_sec_updates=t_sec_updates,
                                                                               )

                            ## preambule: define rpa the ratio of the planetary radius over the semi-major axis
                            if not(orbital_model.use_aR):
                                aR = f"aR_{planet_name}\n"
                            else:
                                aR = function_builder.get_text_4_parameter(parameter=parameters['orbit']['aR'], function_shortname=func_shortname)
                            if not(function_builder.is_done_in_text(name=f"rpa_{planet_name}", function_shortname=func_shortname)):
                                Rrat = function_builder.get_text_4_parameter(parameter=parameters['planet']['Rrat'], function_shortname=func_shortname)
                                function_builder.add_to_body_text(text=f"{tab}rpa_{planet_name} = {Rrat} / {aR}\n", function_shortname=func_shortname)
                                function_builder.add_to_done_in_text(name=f"rpa_{planet_name}", function_shortname=func_shortname)
                            c11 = function_builder.get_text_4_parameter(parameter=parameters['planet']['c11'], function_shortname=func_shortname)
                            hotspotoffset = function_builder.get_text_4_parameter(parameter=parameters['planet']['hotspotoffset'], function_shortname=func_shortname)
                            alpha = function_builder.get_text_4_parameter(parameter=parameters['planet']['alpha'], function_shortname=func_shortname)
                            omegadrag = function_builder.get_text_4_parameter(parameter=parameters['planet']['omegadrag'], function_shortname=func_shortname)
                            AB = function_builder.get_text_4_parameter(parameter=parameters['planet']['AB'], function_shortname=func_shortname)
                            if stellar_spectrum is None:
                                Teff = function_builder.get_text_4_parameter(parameter=parameters['star']['Teff'], function_shortname=func_shortname)

                            ## Update the parameters of the kelp model and planet
                            if not(function_builder.is_done_in_text(name=f"model_kelp_{planet_name}_{instmod_fullname}", function_shortname=func_shortname)):
                                if stellar_spectrum is None:
                                    function_builder.add_to_body_text(text=f"{tab}model_kelp_{planet_name}_{instmod_fullname}.T_s = {Teff}\n", function_shortname=func_shortname)
                                function_builder.add_to_body_text(text=f"{tab}model_kelp_{planet_name}_{instmod_fullname}.A_B = {AB}\n", function_shortname=func_shortname)
                                function_builder.add_to_body_text(text=f"{tab}model_kelp_{planet_name}_{instmod_fullname}.omega_drag = {omegadrag}\n", function_shortname=func_shortname)
                                function_builder.add_to_body_text(text=f"{tab}model_kelp_{planet_name}_{instmod_fullname}.alpha = {alpha}\n", function_shortname=func_shortname)
                                function_builder.add_to_body_text(text=f"{tab}model_kelp_{planet_name}_{instmod_fullname}.hotspot_offset = {hotspotoffset}\n", function_shortname=func_shortname)
                                function_builder.add_to_body_text(text=f"{tab}model_kelp_{planet_name}_{instmod_fullname}.C_ml[1][1] = {c11}\n", function_shortname=func_shortname)
                                function_builder.add_to_body_text(text=f"{tab}model_kelp_{planet_name}_{instmod_fullname}.rp_a = rpa_{planet_name}\n", function_shortname=func_shortname)
                                function_builder.add_to_body_text(text=f"{tab}model_kelp_{planet_name}_{instmod_fullname}.a_rs = {aR}\n", function_shortname=func_shortname)
                                function_builder.add_to_done_in_text(name=f"model_kelp_{planet_name}_{instmod_fullname}", function_shortname=func_shortname)

                            ####################################################
                            # Produce the text for the phase curve model returns
                            ####################################################
                            ## Compute the orbital phase and idx_sort (orbital phase 0 means secondary eclipse)
                            if not(function_builder.is_done_in_text(name=f"orbphase_{planet_name}_{instmod_fullname}_dst{dst.number}", function_shortname=func_shortname)):
                                if multi:
                                    time_vect = f"{time_arg_name}[{i_inputoutput}]"
                                else:
                                    time_vect = f"{time_arg_name}"
                                if get_times_from_datasets:
                                    supersamp = SSE4instmodfname.get_supersamp(instmod.get_name(include_prefix=True, code_version=True, recursive=True))
                                    if supersamp > 1:
                                        logger.warning("Currently the kelp model doesn't include supersampling !")
                                period = function_builder.get_text_4_parameter(parameter=parameters['orbit']['P'], function_shortname=func_shortname)
                                tic = function_builder.get_text_4_parameter(parameter=parameters['orbit']['tic'], function_shortname=func_shortname)
                                function_builder.add_variable_to_ldict(variable_name="pi", variable_content=pi, function_shortname=func_shortname, exist_ok=True)
                                function_builder.add_variable_to_ldict(variable_name="foldAt", variable_content=foldAt, function_shortname=func_shortname, exist_ok=True)
                                function_builder.add_to_body_text(text=f"{tab}orbphase_{planet_name}_{instmod_fullname}_dst{dst.number} = (foldAt({time_vect}, {period}, T0={tic}, getEpoch=False) - 0.5) * 2 * pi\n", function_shortname=func_shortname)
                                function_builder.add_to_done_in_text(name=f"orbphase_{planet_name}_{instmod_fullname}_dst{dst.number}", function_shortname=func_shortname)
                            if not(function_builder.is_done_in_text(name=f"idxsortphase_{planet_name}_{instmod_fullname}_dst{dst.number}", function_shortname=func_shortname)):
                                function_builder.add_variable_to_ldict(variable_name="argsort", variable_content=argsort, function_shortname=func_shortname, exist_ok=True)
                                function_builder.add_to_body_text(text=f"{tab}idxsortphase_{planet_name}_{instmod_fullname}_dst{dst.number} = argsort(orbphase_{planet_name}_{instmod_fullname}_dst{dst.number})\n", function_shortname=func_shortname)
                                function_builder.add_to_done_in_text(name=f"idxsortphase_{planet_name}_{instmod_fullname}_dst{dst.number}", function_shortname=func_shortname)
                            if not(function_builder.is_done_in_text(name=f"idxdesortphase_{planet_name}_{instmod_fullname}_dst{dst.number}", function_shortname=func_shortname)):
                                function_builder.add_variable_to_ldict(variable_name="argsort", variable_content=argsort, function_shortname=func_shortname, exist_ok=True)
                                function_builder.add_to_body_text(text=f"{tab}idxdesort_{planet_name}_{instmod_fullname}_dst{dst.number} = argsort(idxsortphase_{planet_name}_{instmod_fullname}_dst{dst.number})\n", function_shortname=func_shortname)
                                function_builder.add_to_done_in_text(name=f"idxdesort_{planet_name}_{instmod_fullname}_dst{dst.number}", function_shortname=func_shortname)

                            if returns[func_shortname][i_inputoutput] == "":
                                pre_text = ""
                            else:
                                pre_text = " + "
                            f = function_builder.get_text_4_parameter(parameter=parameters['planet']['f'], function_shortname=func_shortname)
                            returns[func_shortname][i_inputoutput] = f"{pre_text}model_kelp_{planet_name}_{instmod_fullname}.thermal_phase_curve(orbphase_{planet_name}_{instmod_fullname}_dst{dst.number}[idxsortphase_{planet_name}_{instmod_fullname}_dst{dst.number}], f={f}, **kelp_pc_kwargs_{planet_name}_{instmod_fullname}).flux[idxdesort_{planet_name}_{instmod_fullname}_dst{dst.number}] * 1e-6 * ({text_occ})"

                        #################
                        # Gaussian models
                        #################
                        elif pc_component_model.category == "gaussian":
                            if pc_component_model.occultation:
                                _, text_occ = do_batman_transit_occultation_models(function_builder=function_builder,
                                                                                   function_shortname=func_shortname,
                                                                                   model_definition=pc_component_model,
                                                                                   planet=planet, star=star, inst_model_obj=instmod,
                                                                                   dataset=dst,
                                                                                   get_times_from_datasets=get_times_from_datasets,
                                                                                   time_arg_name=time_arg_name, SSE4instmodfname=SSE4instmodfname,
                                                                                   do_transit=False, do_occultation=True,
                                                                                   l_dataset=l_dataset, multi=multi,
                                                                                   i_inputoutput=i_inputoutput,
                                                                                   normalize_occultation=True,
                                                                                   rp_updates=rp_updates,
                                                                                   fp_updates=fp_updates, t_sec_updates=t_sec_updates
                                                                                   )
                                text_occ = f" * ({text_occ})"
                            else:
                                text_occ = ""

                            ################
                            # Add parameters
                            ################
                            # Orbital Period
                            period = function_builder.get_text_4_parameter(parameter=parameters['orbit']['P'], function_shortname=func_shortname)
                            # Time of inferior conjunction
                            tic = function_builder.get_text_4_parameter(parameter=parameters['orbit']['tic'], function_shortname=func_shortname)
                            # Amplitude
                            amp = function_builder.get_text_4_parameter(parameter=parameters['planet']['A'], function_shortname=func_shortname)
                            # Width
                            sigma_phi = function_builder.get_text_4_parameter(parameter=parameters['planet']['sigmaPhi'], function_shortname=func_shortname)
                            # Phase Offset
                            if pc_component_model.phase_offset == "param":
                                phi = function_builder.get_text_4_parameter(parameter=parameters['planet']['Phi'], function_shortname=func_shortname)
                            else:
                                phi = f"{pc_component_model.phase_offset}"

                            # flux offset
                            if pc_component_model.flux_offset == "param":
                                flux_offset = function_builder.get_text_4_parameter(parameter=parameters['planet']['Foffset'], function_shortname=func_shortname)
                            elif isinstance(pc_component_model.flux_offset, Number):
                                flux_offset = f"{pc_component_model.flux_offset}"
                            elif pc_component_model.flux_offset == "zero":
                                flux_offset = 0
                            # Add gauss to ldict
                            def gauss(x, Foffset, A, phi, sigmaphi):
                                return Foffset + A * exp(-(x - phi)** 2 / (2 * sigmaphi ** 2))
                            function_builder.add_variable_to_ldict(variable_name="gauss", variable_content=gauss, function_shortname=func_shortname, exist_ok=True)
                            ####################################################
                            # Produce the text for the phase curve model returns
                            ####################################################
                            ### TODO: This is only a copy paste from sin-cos
                            if not(function_builder.is_done_in_text(name=f"orbphase_{planet_name}_{instmod_fullname}_dst{dst.number}", function_shortname=func_shortname)):
                                if multi:
                                    time_vect = f"{time_arg_name}[{i_inputoutput}]"
                                else:
                                    time_vect = f"{time_arg_name}"
                                if get_times_from_datasets:
                                    supersamp = SSE4instmodfname.get_supersamp(instmod.get_name(include_prefix=True, code_version=True, recursive=True))
                                    if supersamp > 1:
                                        logger.warning("Currently the gaussian model doesn't include supersampling !")
                                period = function_builder.get_text_4_parameter(parameter=parameters['orbit']['P'], function_shortname=func_shortname)
                                tic = function_builder.get_text_4_parameter(parameter=parameters['orbit']['tic'], function_shortname=func_shortname)
                                function_builder.add_variable_to_ldict(variable_name="pi", variable_content=pi, function_shortname=func_shortname, exist_ok=True)
                                function_builder.add_variable_to_ldict(variable_name="foldAt", variable_content=foldAt, function_shortname=func_shortname, exist_ok=True)
                                function_builder.add_to_body_text(text=f"{tab}orbphase_{planet_name}_{instmod_fullname}_dst{dst.number} = (foldAt({time_vect}, {period}, T0={tic}, getEpoch=False) - 0.5) * 2 * pi\n", function_shortname=func_shortname)
                                function_builder.add_to_done_in_text(name=f"orbphase_{planet_name}_{instmod_fullname}_dst{dst.number}", function_shortname=func_shortname)
                            if returns[func_shortname][i_inputoutput] == "":
                                pre_text = ""
                            else:
                                pre_text = " + "
                            returns[func_shortname][i_inputoutput] += f"{pre_text}gauss(x=orbphase_{planet_name}_{instmod_fullname}_dst{dst.number}, Foffset={flux_offset}, A={amp}, phi={phi}, sigmaphi={sigma_phi}){text_occ}"

                        ##################################
                        # Kelp reflected light homogeneous
                        ##################################
                        elif pc_component_model.category == "kelp-reflect-hom":
                            raise NotImplementedError
                        
                        ####################################
                        # Kelp reflected light inhomogeneous
                        ####################################
                        elif pc_component_model.category == "kelp-reflect-inhom":
                            ## Do the text for the occultation
                            _, text_occ = do_batman_transit_occultation_models(function_builder=function_builder,
                                                                               function_shortname=func_shortname,
                                                                               model_definition=pc_component_model,
                                                                               planet=planet, star=star, inst_model_obj=instmod,
                                                                               dataset=dst,
                                                                               get_times_from_datasets=get_times_from_datasets,
                                                                               time_arg_name=time_arg_name, SSE4instmodfname=SSE4instmodfname,
                                                                               do_transit=False, do_occultation=True,
                                                                               l_dataset=l_dataset, multi=multi,
                                                                               i_inputoutput=i_inputoutput,
                                                                               normalize_occultation=True,
                                                                               rp_updates=rp_updates,
                                                                               fp_updates=fp_updates, t_sec_updates=t_sec_updates,
                                                                               )

                            ## preambule: define rpa the ratio of the planetary radius over the semi-major axis
                            if not(orbital_model.use_aR):
                                aR = f"aR_{planet_name}\n"
                            else:
                                aR = function_builder.get_text_4_parameter(parameter=parameters['orbit']['aR'], function_shortname=func_shortname)
                            if not(function_builder.is_done_in_text(name=f"rpa_{planet_name}", function_shortname=func_shortname)):
                                Rrat = function_builder.get_text_4_parameter(parameter=parameters['planet']['Rrat'], function_shortname=func_shortname)
                                function_builder.add_to_body_text(text=f"{tab}rpa_{planet_name} = {Rrat} / {aR}\n", function_shortname=func_shortname)
                                function_builder.add_to_done_in_text(name=f"rpa_{planet_name}", function_shortname=func_shortname)
                            omega_0 = function_builder.get_text_4_parameter(parameter=parameters['planet']['omega0'], function_shortname=func_shortname)
                            omega_prime = function_builder.get_text_4_parameter(parameter=parameters['planet']['omegaprime'], function_shortname=func_shortname)
                            x1 = function_builder.get_text_4_parameter(parameter=parameters['planet']['x1'], function_shortname=func_shortname)
                            x2 = function_builder.get_text_4_parameter(parameter=parameters['planet']['x2'], function_shortname=func_shortname)
                            A_g = function_builder.get_text_4_parameter(parameter=parameters['planet']['Ag'], function_shortname=func_shortname)
                            
                            ####################################################
                            # Produce the text for the phase curve model returns
                            ####################################################
                            ## Compute the orbital phase and idx_sort (orbital phase 0 means secondary eclipse)
                            if not(function_builder.is_done_in_text(name=f"orbphase_{planet_name}_{instmod_fullname}_dst{dst.number}", function_shortname=func_shortname)):
                                if multi:
                                    time_vect = f"{time_arg_name}[{i_inputoutput}]"
                                else:
                                    time_vect = f"{time_arg_name}"
                                if get_times_from_datasets:
                                    supersamp = SSE4instmodfname.get_supersamp(instmod.get_name(include_prefix=True, code_version=True, recursive=True))
                                    if supersamp > 1:
                                        logger.warning("Currently the kelp model doesn't include supersampling !")
                                period = function_builder.get_text_4_parameter(parameter=parameters['orbit']['P'], function_shortname=func_shortname)
                                tic = function_builder.get_text_4_parameter(parameter=parameters['orbit']['tic'], function_shortname=func_shortname)
                                function_builder.add_variable_to_ldict(variable_name="pi", variable_content=pi, function_shortname=func_shortname, exist_ok=True)
                                function_builder.add_variable_to_ldict(variable_name="foldAt", variable_content=foldAt, function_shortname=func_shortname, exist_ok=True)
                                function_builder.add_to_body_text(text=f"{tab}orbphase_{planet_name}_{instmod_fullname}_dst{dst.number} = (foldAt({time_vect}, {period}, T0={tic}, getEpoch=False) - 0.5) * 2 * pi\n", function_shortname=func_shortname)
                                function_builder.add_to_done_in_text(name=f"orbphase_{planet_name}_{instmod_fullname}_dst{dst.number}", function_shortname=func_shortname)
                            if not(function_builder.is_done_in_text(name=f"idxsortphase_{planet_name}_{instmod_fullname}_dst{dst.number}", function_shortname=func_shortname)):
                                function_builder.add_variable_to_ldict(variable_name="argsort", variable_content=argsort, function_shortname=func_shortname, exist_ok=True)
                                function_builder.add_to_body_text(text=f"{tab}idxsortphase_{planet_name}_{instmod_fullname}_dst{dst.number} = argsort(orbphase_{planet_name}_{instmod_fullname}_dst{dst.number})\n", function_shortname=func_shortname)
                                function_builder.add_to_done_in_text(name=f"idxsortphase_{planet_name}_{instmod_fullname}_dst{dst.number}", function_shortname=func_shortname)
                            if not(function_builder.is_done_in_text(name=f"idxdesortphase_{planet_name}_{instmod_fullname}_dst{dst.number}", function_shortname=func_shortname)):
                                function_builder.add_variable_to_ldict(variable_name="argsort", variable_content=argsort, function_shortname=func_shortname, exist_ok=True)
                                function_builder.add_to_body_text(text=f"{tab}idxdesort_{planet_name}_{instmod_fullname}_dst{dst.number} = argsort(idxsortphase_{planet_name}_{instmod_fullname}_dst{dst.number})\n", function_shortname=func_shortname)
                                function_builder.add_to_done_in_text(name=f"idxdesort_{planet_name}_{instmod_fullname}_dst{dst.number}", function_shortname=func_shortname)
                            
                            if returns[func_shortname][i_inputoutput] == "":
                                pre_text = ""
                            else:
                                pre_text = " + "
                            returns[func_shortname][i_inputoutput] = f"{pre_text}reflected_phase_curve_inhomogeneous(orbphase_{planet_name}_{instmod_fullname}_dst{dst.number}[idxsortphase_{planet_name}_{instmod_fullname}_dst{dst.number}], omega_0={omega_0}, omega_prime={omega_prime}, x1={x1}, x2={x2}, A_g={A_g}, a_rp=1/rpa_{planet_name})[0][idxdesort_{planet_name}_{instmod_fullname}_dst{dst.number}] * 1e-6 * ({text_occ})"
                            function_builder.add_variable_to_ldict(variable_name="reflected_phase_curve_inhomogeneous", variable_content=reflected_phase_curve_inhomogeneous, function_shortname=func_shortname, exist_ok=True)

                        ########################
                        # No other model for now
                        ########################
                        else:
                            raise NotImplementedError(f"phasecurve model {pc_component_model.category} is not implemented.")

        ###############################################
        # Finalize the planets phasecurve only function
        ###############################################
    for planet in planets.values():
        planet_name = planet.get_name()
        if phasecurve_model.get_do(planet_name=planet_name):
            func_shortname = f"{get_function_planet_shortname(planet)}{ext_func_pc_only}"
            get_condition(multi=multi, l_inst_model=l_inst_model, l_planet=[planet, ], tab=tab, time_vec_name=time_vec_name,
                          l_time_vec_name=l_time_vec_name, function_builder=function_builder, function_shortname=func_shortname,
                          transit_model=None, occultation_model=None, phasecurve_model=phasecurve_model,
                          )
            function_builder.add_to_body_text(text=f"{tab}return {', '.join(returns.pop(func_shortname))}", function_shortname=func_shortname)

    return returns


def get_occultation(multi, l_inst_model, l_dataset, get_times_from_datasets, occultation_model,
                    SSE4instmodfname, star, planets, tab,
                    time_vec_name, l_time_vec_name, function_builder, ext_func_fullname
                    ):
    """Provide the text for the occultation curve part of the LC model text (preambule and return).

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
    occultation_model        : dict
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
    ext_func_occ_only = "_occ"

    # Init the list that will indicate that t_secondary has been updated in the batman TransitParams instances used for the occultation
    t_sec_updates = defaultdict(list)
    # Init the list that will indicate that fp and rp has been set to 1 in the batman TransitParams instances used for the occultation
    fp_updates = defaultdict(list)
    rp_updates = defaultdict(list)

    ##############################
    # Do the Model for each planet
    ##############################
    for planet in planets.values():
        planet_name = planet.get_name()
        if occultation_model.get_do(planet_name=planet_name):
            ########################################################################
            # Define the functions to populate and initialise entries in the outputs
            ########################################################################
            # Defines the lists of function shortnames and add the new transit only function into the function builder
            l_whole_function_shortname = [function_whole_shortname, ]
            l_planet_function_shortname_ext = ["", ext_func_occ_only]
            l_planet_function_shortname = []
            for planet_func_shortname_ext in l_planet_function_shortname_ext:
                l_planet_function_shortname.append(f"{get_function_planet_shortname(planet)}{planet_func_shortname_ext}")
            l_function_shortname_4_planet = l_whole_function_shortname + l_planet_function_shortname

            ##################################################
            # Initialise the new functions in function_builder
            ##################################################
            l_func_shortname_ext_to_create = [ext_func_occ_only, ]
            for func_shortname_ext in l_func_shortname_ext_to_create:
                func_shortname_tr_pl_only = f"{get_function_planet_shortname(planet)}{ext_func_occ_only}"
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
            # if parametrisation == "Multis":
            #     for func_shortname in l_function_shortname_4_planet:
            #         function_builder.add_parameter(parameter=star.rho, function_shortname=func_shortname, exist_ok=True)
            #
            # # Add the planet parameters: Rrat, ecosw, esinw, cosinc, P, tic and aR if needed
            # l_param = [planet.ecosw, planet.esinw, planet.cosinc, planet.P, planet.tic, planet.Frat]
            # if parametrisation != "Multis":
            #     l_param.append(planet.aR)
            # for param in l_param:
            #     for func_shortname in l_function_shortname_4_planet:
            #         function_builder.add_parameter(parameter=param, function_shortname=func_shortname, exist_ok=True)

            ####################################################################
            # Do the Model for each planet and each instrument and each function
            ####################################################################
            for func_shortname in l_function_shortname_4_planet:

                for i_inputoutput, (instmod, dst) in enumerate(zip(l_inst_model, l_dataset)):
                    ####################################################################################
                    # Get the transit model implementation definition for the planet and the instrument
                    ####################################################################################
                    model_definition = occultation_model.get_model(planet_name=planet_name, inst_model_fullname=instmod.full_name)

                    ##############
                    # Batman model
                    ##############
                    if model_definition.category == "batman":
                        if not(batman_imported):
                            raise ValueError("Batman doesn't seems to be installed. The import failed.")

                        _, text_occ = do_batman_transit_occultation_models(function_builder=function_builder,
                                                                           function_shortname=func_shortname,
                                                                           model_definition=model_definition,
                                                                           planet=planet, star=star, inst_model_obj=instmod,
                                                                           dataset=dst,
                                                                           get_times_from_datasets=get_times_from_datasets,
                                                                           time_arg_name=time_arg_name, SSE4instmodfname=SSE4instmodfname,
                                                                           do_transit=False, do_occultation=True,
                                                                           l_dataset=l_dataset, multi=multi,
                                                                           i_inputoutput=i_inputoutput,
                                                                           normalize_occultation=False,
                                                                           fp_updates=fp_updates, rp_updates=rp_updates,
                                                                           t_sec_updates=t_sec_updates
                                                                           )

                        ## writing the returns
                        if returns[func_shortname][i_inputoutput] == "":
                            pre_text = ""
                        else:
                            pre_text = " + "
                        returns[func_shortname][i_inputoutput] += f"{pre_text}{text_occ}"

                    ########################
                    # No other model for now
                    ########################
                    else:
                        raise ValueError(f"Occulation model {model_definition.category} is not recognized.")

    ############################################
    # Finalize the planets transit only function
    ############################################
    for planet in planets.values():
        planet_name = planet.get_name()
        if occultation_model.get_do(planet_name=planet_name):
            func_shortname = f"{get_function_planet_shortname(planet)}{ext_func_occ_only}"
            get_condition(multi=multi, l_inst_model=l_inst_model, l_planet=[planet, ], tab=tab, time_vec_name=time_vec_name,
                          l_time_vec_name=l_time_vec_name, function_builder=function_builder, function_shortname=func_shortname,
                          transit_model=None, occultation_model=occultation_model,
                          phasecurve_model=None
                          )
            function_builder.add_to_body_text(text=template_return.format(tab=tab, returns=f"{', '.join(returns.pop(func_shortname))}",
                                                                          returns_except=get_catchederror_return(multi=multi,
                                                                                                                 l_inst_model=l_inst_model,
                                                                                                                 time_vec_name=time_vec_name,
                                                                                                                 l_time_vec_name=l_time_vec_name,
                                                                                                                 function_builder=function_builder,
                                                                                                                 function_shortname=func_shortname
                                                                                                                 )
                                                                          ),
                                              function_shortname=func_shortname)

    return returns


def get_decorrelation(multi, planets, l_inst_model, l_dataset, get_times_from_datasets, dataset_db,
                      LCcat_model, tab, time_vec_name, l_time_vec_name, function_builder, l_function_shortname,
                      ext_func_fullname):
    """Provide the text for the decorrelation of the LC model text (return).

    It should provide the text for decorrelation model for all functions requested (l_function_shortname)
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

    #############################################################################
    # Check if any of the instrument model is associated to a decorrelation model
    #############################################################################
    requires_decorr = False
    for instmod_obj in l_inst_model:
        if LCcat_model.require_model_decorrelation(instmod_fullname=instmod_obj.full_name):
            requires_decorr = True
            break

    if requires_decorr:
        decorrelation_config = LCcat_model.decorrelation_model_config
        #################################################
        # Initialise the new function in function_builder
        #################################################
        # Extension for the shortname of the function that do the decorrelation only model
        l_decorr_func_shortname = []
        for i_inputoutput, (instmod, dst) in enumerate(zip(l_inst_model, l_dataset)):
            if decorrelation_config[instmod.full_name]["do"]:
                for model_part, config_decorr_instmod_modelpart in decorrelation_config[instmod.full_name]["what to decorrelate"].items():
                    decorr_func_shortname = f"decorr_{model_part}"
                    if not(function_builder.is_function(shortname=decorr_func_shortname)):
                        function_builder.add_new_function(shortname=decorr_func_shortname)
                        function_builder.set_function_fullname(full_name=f"LC_sim_{decorr_func_shortname}{ext_func_fullname}", shortname=decorr_func_shortname)
                        l_decorr_func_shortname.append(decorr_func_shortname)
        # decorr_func_shortname = "decorr"
        # function_builder.add_new_function(shortname=decorr_func_shortname)
        # function_builder.set_function_fullname(full_name=f"LC_sim_{decorr_func_shortname}{ext_func_fullname}", shortname=decorr_func_shortname)

        ########################################
        # Update the list of function to address
        ########################################
        l_function_shortname += l_decorr_func_shortname
        # l_function_shortname += [decorr_func_shortname, ]

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
                if func_shortname in l_decorr_func_shortname:
                    returns[func_shortname].append("")
                else:
                    returns[func_shortname].append({})
                if decorrelation_config[instmod.full_name]["do"]:
                    # List of the datasets associated with the instrument model
                    l_dataset_name_instmod = LCcat_model.get_l_datasetname(instmod_fullnames=instmod.full_name)
                    for model_part, config_decorr_instmod_modelpart in decorrelation_config[instmod.full_name]["what to decorrelate"].items():
                        text_decorr = LCcat_model.create_text_decorr(multi=multi, inst_mod_obj=instmod, idx_inst_mod_obj=i_inputoutput,
                                                                     l_dataset_name_instmod=l_dataset_name_instmod,
                                                                     dataset_db=dataset_db, decorrelation_config_instmod=config_decorr_instmod_modelpart,
                                                                     model_part=model_part, time_arg_name=time_arg_name,
                                                                     function_builder=function_builder, function_shortname=func_shortname)
                        if text_decorr != "":
                            if func_shortname in l_decorr_func_shortname:
                                returns[func_shortname][i_inputoutput] = text_decorr
                            else:
                                returns[func_shortname][i_inputoutput][model_part] = text_decorr

        ##########################################
        # Finalize the decorrelation only function
        ##########################################
        for func_shortname in l_decorr_func_shortname:
            l_return = [output_i if output_i != "" else 'None' for output_i in returns.pop(func_shortname)]
            function_builder.add_to_body_text(text=f"{tab}return {', '.join(l_return)}", function_shortname=func_shortname)

    return returns


def combine_return_models(multi, l_inst_model, time_vec_name, l_time_vec_name, reference_flux_level,
                          tab, function_builder, function_shortname, transit=None, phasecurve=None,
                          occultation=None, inst_var=None, stellar_var=None, decorrelation=None, contamination=None):
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
        Reference_flux_level for the photometry (in principle 1 or 0). This argument is ignored if stellar_var
        is provided (as it provides the reference level)
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
    occultation             : list of str
        text providing the occultation model component of the planet(s) contribution to the LC model (independantly of the phase curve)
    inst_var                : list of str
        text providing the additive out of transit variations due to the instrument (inst_var)
    stellar_var             : list of str
        text providing the additive out of transit variations due to the star (stellar_var)
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
    contamination           : list of str
        Text providing the multiplication factor to account for contamination by third light (contam)

    Returns
    -------
    text_return : str
        Text of the return for one datasim lc function.
    """
    return_text = []
    for i_inputoutput, instmod in enumerate(l_inst_model):
        return_text.append("")
        planet_contribution = ""
        nb_non_none_model = 0
        for model in [transit, phasecurve, occultation]:
            if model is not None:
                if nb_non_none_model == 0:
                    planet_contribution += f"{model[i_inputoutput]}"
                else:
                    planet_contribution += f" + {model[i_inputoutput]}"
                nb_non_none_model += 1
        # Combine the planetary and stellar contribution
        if reference_flux_level == 0:
            if stellar_var is None or stellar_var[i_inputoutput] == "":
                return_text[i_inputoutput] += f"{planet_contribution}"
            else:
                return_text[i_inputoutput] += f"({stellar_var}) * (1 + {planet_contribution}) - 1"
        else:
            if stellar_var is None or stellar_var[i_inputoutput] == "":
                return_text[i_inputoutput] += f"{reference_flux_level} * (1 + {planet_contribution})"
            else:
                return_text[i_inputoutput] += f"({stellar_var}) * (1 + {planet_contribution})"

        # Apply the contamination correction
        if (contamination is not None) and (contamination[i_inputoutput] != ""):
            return_text[i_inputoutput] = "(" + return_text[i_inputoutput] + f") * {contamination[i_inputoutput]}"

        # Add the instrumental variation
        if (inst_var is not None) and (inst_var[i_inputoutput] != "") and (inst_var[i_inputoutput] != "None"):
            return_text[i_inputoutput] += " + " + inst_var[i_inputoutput]

        if decorrelation is not None:
            if "multiply_2_totalflux" in decorrelation[i_inputoutput]:
                return_text[i_inputoutput] = "(" + return_text[i_inputoutput] + ")"
                return_text[i_inputoutput] += f" * ({decorrelation[i_inputoutput]['multiply_2_totalflux']})"
            if "add_2_totalflux" in decorrelation[i_inputoutput]:
                return_text[i_inputoutput] += f" + ({decorrelation[i_inputoutput]['add_2_totalflux']})"

    function_builder.add_to_body_text(text=template_return.format(tab=tab, returns=", ".join(return_text),
                                                                  returns_except=get_catchederror_return(multi=multi,
                                                                                                         l_inst_model=l_inst_model,
                                                                                                         time_vec_name=time_vec_name,
                                                                                                         l_time_vec_name=l_time_vec_name,
                                                                                                         function_builder=function_builder,
                                                                                                         function_shortname=function_shortname)),
                                      function_shortname=function_shortname)


def do_batman_transit_occultation_models(function_builder, function_shortname, planet, star, model_definition,
                                         inst_model_obj, dataset,
                                         get_times_from_datasets, time_arg_name, SSE4instmodfname,
                                         do_transit, do_occultation,
                                         l_dataset, multi, i_inputoutput=None,
                                         ldmodel4instmodfname=None, LDs=None,
                                         normalize_occultation=True, fp_updates=None, t_sec_updates=None,
                                         rp_updates=None, ld_updates=None,
                                         ):
    if not(do_transit or do_occultation):
        return None, None

    planet_name = planet.get_name()
    instmod_fullname = inst_model_obj.full_name

    # make sure that all the required parameters are added to the function in the function_builder
    parameters = model_definition.get_parameters(inst_model_fullname=instmod_fullname, object_category=None)
    for object_category in parameters:
        for param in parameters[object_category].values():
            function_builder.add_parameter(parameter=param, function_shortname=function_shortname, exist_ok=True)

    # get the orbital_model
    orbital_model = model_definition.get_orbital_model(inst_model_fullname=instmod_fullname)

    ## If it doesn't already exists, create a batman TransitParams instance for the occultation
    if not(function_builder.is_in_ldict(variable_name=f"params_{planet_name}_{instmod_fullname}", function_shortname=function_shortname)):
        params_bat = TransitParams()
        params_bat.per = 1.   # orbital period
        params_bat.rp = 0.1   # planet radius(in stel radii)
        params_bat.a = 15.    # semi-major axis(in stel radii)
        params_bat.inc = 90.  # orbital inclination (in degrees)
        params_bat.ecc = 0.   # eccentricity
        params_bat.w = 90.    # long. of periastron (in deg.)
        if get_times_from_datasets:
            time_arg_value = function_builder.get_ldict(function_shortname=function_shortname)[time_arg_name]  # Time is the same for all function
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
        params_bat.limb_dark = 'linear'  # LD model
        params_bat.u = [0., ]  # LDC init val
        if do_occultation:
            params_bat.t_secondary = params_bat.t0 + params_bat.per / 2
        function_builder.add_variable_to_ldict(variable_name=f"params_{planet_name}_{instmod_fullname}",
                                               variable_content=params_bat, function_shortname=function_shortname, exist_ok=False)

    ## Need to set fp to 1 in the batman parameter instance for the occultation
    if do_occultation and (f"params_{planet_name}_{instmod_fullname}" not in fp_updates[function_shortname]):
        params_bat = function_builder.get_ldict(function_shortname=function_shortname)[f"params_{planet_name}_{instmod_fullname}"]
        if normalize_occultation:
            params_bat.fp = 1.
        else:
            params_bat.fp = 1e-3
        function_builder.add_variable_to_ldict(variable_name=f"params_{planet_name}_{instmod_fullname}",
                                               variable_content=params_bat, function_shortname=function_shortname,
                                               exist_ok=True, overwrite=True)

    if do_transit and (f"params_{planet_name}_{instmod_fullname}" not in ld_updates[function_shortname]):
        params_bat = function_builder.get_ldict(function_shortname=function_shortname)[f"params_{planet_name}_{instmod_fullname}"]
        LD_mod_name = ldmodel4instmodfname[instmod_fullname][star.code_name]
        LD_mod = LDs[star.code_name + "_" + LD_mod_name]
        params_bat.limb_dark = LD_mod.ld_type  # LD model
        params_bat.u = LD_mod.init_LD_values  # LDC init val
        function_builder.add_variable_to_ldict(variable_name=f"params_{planet_name}_{instmod_fullname}",
                                               variable_content=params_bat, function_shortname=function_shortname,
                                               exist_ok=True, overwrite=True)

    ## preambule: Update the parameter values in the TransitParams object
    if not(function_builder.is_done_in_text(name=f"params_{planet_name}_{instmod_fullname}", function_shortname=function_shortname)):
        period = function_builder.get_text_4_parameter(parameter=parameters['orbit']['P'], function_shortname=function_shortname)
        tic = function_builder.get_text_4_parameter(parameter=parameters['orbit']['tic'], function_shortname=function_shortname)
        ## preambule: define ecc, omega, inc if needed
        # WARNING eccentricity is just taken into account in the timing of the occulation, not the shape of the PC.
        ecosw = function_builder.get_text_4_parameter(parameter=parameters['orbit']['ecosw'], function_shortname=function_shortname)
        esinw = function_builder.get_text_4_parameter(parameter=parameters['orbit']['esinw'], function_shortname=function_shortname)
        cosinc = function_builder.get_text_4_parameter(parameter=parameters['orbit']['cosinc'], function_shortname=function_shortname)
        if not(function_builder.is_done_in_text(name=f"ecc_{planet_name}", function_shortname=function_shortname)):
            function_builder.add_variable_to_ldict(variable_name="sqrt", variable_content=sqrt, function_shortname=function_shortname, exist_ok=True)
            function_builder.add_to_body_text(text=f"{tab}ecc_{planet_name} = sqrt({ecosw} * {ecosw} + {esinw} * {esinw})\n", function_shortname=function_shortname)
            function_builder.add_to_done_in_text(name=f"ecc_{planet_name}", function_shortname=function_shortname)
        if not(function_builder.is_done_in_text(name=f"omega_{planet_name}_deg", function_shortname=function_shortname)):
            function_builder.add_variable_to_ldict(variable_name="getomega_deg_fast", variable_content=getomega_deg_fast, function_shortname=function_shortname, exist_ok=True)
            function_builder.add_to_body_text(text=f"{tab}omega_{planet_name}_deg = getomega_deg_fast({ecosw}, {esinw})\n", function_shortname=function_shortname)
            function_builder.add_to_done_in_text(name=f"omega_{planet_name}_deg", function_shortname=function_shortname)
        if not(function_builder.is_done_in_text(name=f"inc_{planet_name}_deg", function_shortname=function_shortname)):
            function_builder.add_variable_to_ldict(variable_name="degrees", variable_content=degrees, function_shortname=function_shortname, exist_ok=True)
            function_builder.add_variable_to_ldict(variable_name="acos", variable_content=acos, function_shortname=function_shortname, exist_ok=True)
            function_builder.add_to_body_text(text=f"{tab}inc_{planet_name}_deg = degrees(acos({cosinc}))\n", function_shortname=function_shortname)
            function_builder.add_to_done_in_text(name=f"inc_{planet_name}_deg", function_shortname=function_shortname)
        ## preambule: define aR if needed in the preambule and get the text
        if not(orbital_model.use_aR):
            if not(function_builder.is_done_in_text(name=f"aR_{planet_name}", function_shortname=function_shortname)):
                rhostar = function_builder.get_text_4_parameter(parameter=parameters['orbit']['rho'], function_shortname=function_shortname)
                function_builder.add_variable_to_ldict(variable_name="getaoverr", variable_content=getaoverr, function_shortname=function_shortname, exist_ok=True)
                function_builder.add_to_body_text(text=f"{tab}aR_{planet_name} = getaoverr({period}, {rhostar}, ecc_{planet_name}, omega_{planet_name}_deg)\n", function_shortname=function_shortname)
                function_builder.add_to_done_in_text(name=f"aR_{planet_name}", function_shortname=function_shortname)
            aR = f"aR_{planet_name}\n"
        else:
            aR = function_builder.get_text_4_parameter(parameter=parameters['orbit']['aR'], function_shortname=function_shortname)

        # Update the transit params instance if it's not already done
        function_builder.add_to_body_text(text=f"{tab}params_{planet_name}_{instmod_fullname}.t0 = {tic}\n", function_shortname=function_shortname)
        function_builder.add_to_body_text(text=f"{tab}params_{planet_name}_{instmod_fullname}.per = {period}\n", function_shortname=function_shortname)
        function_builder.add_to_body_text(text=f"{tab}params_{planet_name}_{instmod_fullname}.inc = inc_{planet_name}_deg\n", function_shortname=function_shortname)
        function_builder.add_to_body_text(text=f"{tab}params_{planet_name}_{instmod_fullname}.ecc = ecc_{planet_name}\n", function_shortname=function_shortname)
        function_builder.add_to_body_text(text=f"{tab}params_{planet_name}_{instmod_fullname}.w = omega_{planet_name}_deg\n", function_shortname=function_shortname)
        function_builder.add_to_body_text(text=f"{tab}params_{planet_name}_{instmod_fullname}.a = {aR}\n", function_shortname=function_shortname)
        function_builder.add_to_done_in_text(name=f"params_{planet_name}_{instmod_fullname}", function_shortname=function_shortname)

    if (f"params_{planet_name}_{instmod_fullname}" not in rp_updates[function_shortname]):
        Rrat = function_builder.get_text_4_parameter(parameter=parameters['planet']['Rrat'], function_shortname=function_shortname)
        function_builder.add_to_body_text(text=f"{tab}params_{planet_name}_{instmod_fullname}.rp = {Rrat}\n", function_shortname=function_shortname)
        rp_updates[function_shortname].append(f"params_{planet_name}_{instmod_fullname}")

    if do_transit and (f"params_{planet_name}_{instmod_fullname}" not in ld_updates[function_shortname]):
        ld_param_list = "["
        for param in LD_mod.get_list_params(main=True):
            ld_param_list += function_builder.get_text_4_parameter(parameter=param, function_shortname=function_shortname) + ", "
        ld_param_list += "]"
        function_builder.add_to_body_text(text=f"{tab}params_{planet_name}_{instmod_fullname}.u = {ld_param_list}\n", function_shortname=function_shortname)
        ld_updates[function_shortname].append(f"params_{planet_name}_{instmod_fullname}")

    ## preambule: Create the TransitModel object
    if do_transit:
        if get_times_from_datasets:
            if not(function_builder.is_in_ldict(variable_name=f"m_batman_{planet_name}_{instmod_fullname}_dst{dataset.number}", function_shortname=function_shortname)):
                time_arg_value = function_builder.get_ldict(function_shortname=function_shortname)[time_arg_name]
                if multi:
                    time_vect_value = time_arg_value[i_inputoutput]
                else:
                    time_vect_value = time_arg_value
                supersamp = SSE4instmodfname.get_supersamp(instmod_fullname)
                if supersamp > 1:
                    exptime = SSE4instmodfname.get_exptime(instmod_fullname)
                    kwargs_TransitModel = {"supersample_factor": supersamp, "exp_time": exptime}
                else:
                    kwargs_TransitModel = {}
                params_bat = function_builder.get_ldict(function_shortname=function_shortname)[f"params_{planet_name}_{instmod_fullname}"]
                m_bat = TransitModel(params_bat, time_vect_value, **kwargs_TransitModel)
                function_builder.add_variable_to_ldict(variable_name=f"m_batman_{planet_name}_{instmod_fullname}_dst{dataset.number}",
                                                       variable_content=m_bat, function_shortname=function_shortname, exist_ok=False)
        else:
            if not(function_builder.is_done_in_text(name=f"m_batman_{planet_name}_{instmod_fullname}_dst{dataset.number}", function_shortname=function_shortname)):
                if multi:
                    time_vect = f"{time_arg_name}[{i_inputoutput}]"
                else:
                    time_vect = f"{time_arg_name}"
                supersamp = SSE4instmodfname.get_supersamp(instmod_fullname)
                if supersamp > 1:
                    exptime = SSE4instmodfname.get_exptime(instmod_fullname)
                    supersamp_text = f", supersample_factor={supersamp}, exp_time={exptime}"
                else:
                    supersamp_text = ""
                function_builder.add_variable_to_ldict(variable_name="TransitModel", variable_content=TransitModel, function_shortname=function_shortname, exist_ok=True)
                function_builder.add_to_body_text(text=f"{tab}m_batman_{planet_name}_{instmod_fullname}_dst{dataset.number} = TransitModel(params_{planet_name}_{instmod_fullname}, {time_vect}{supersamp_text})\n", function_shortname=function_shortname)
                function_builder.add_to_done_in_text(name=f"m_batman_{planet_name}_{instmod_fullname}_dst{dataset.number}", function_shortname=function_shortname)

    ## preambule: Create the TransitModel object for the occulation
    if do_occultation:
        if get_times_from_datasets:
            if not(function_builder.is_in_ldict(variable_name=f"m_bat_occ_pc_{planet_name}_{instmod_fullname}_dst{dataset.number}", function_shortname=function_shortname)):
                time_arg_value = function_builder.get_ldict(function_shortname=function_shortname)[time_arg_name]
                if multi:
                    time_vect_value = time_arg_value[i_inputoutput]
                else:
                    time_vect_value = time_arg_value
                supersamp = SSE4instmodfname.get_supersamp(instmod_fullname)
                if supersamp > 1:
                    exptime = SSE4instmodfname.get_exptime(instmod_fullname)
                    kwargs_TransitModel = {"supersample_factor": supersamp, "exp_time": exptime}
                else:
                    kwargs_TransitModel = {}
                params_bat = function_builder.get_ldict(function_shortname=function_shortname)[f"params_{planet_name}_{instmod_fullname}"]
                if params_bat.t_secondary is None:  # You need params_bat.t_secondary to be different than None for the TransitModel creation
                    params_bat.t_secondary = params_bat.t0 + params_bat.per / 2
                m_bat = TransitModel(params=params_bat, t=time_vect_value, transittype="secondary", **kwargs_TransitModel)
                function_builder.add_variable_to_ldict(variable_name=f"m_bat_occ_pc_{planet_name}_{instmod_fullname}_dst{dataset.number}",
                                                       variable_content=m_bat, function_shortname=function_shortname, exist_ok=False)
        else:
            if not(function_builder.is_done_in_text(name=f"m_bat_occ_pc_{planet_name}_{instmod_fullname}_dst{dataset.number}", function_shortname=function_shortname)):
                if multi:
                    time_vect = f"{time_arg_name}[{i_inputoutput}]"
                else:
                    time_vect = f"{time_arg_name}"
                supersamp = SSE4instmodfname.get_supersamp(instmod_fullname)
                if supersamp > 1:
                    exptime = SSE4instmodfname.get_exptime(instmod_fullname)
                    supersamp_text = f", supersample_factor={supersamp}, exp_time={exptime}"
                else:
                    supersamp_text = ""
                function_builder.add_variable_to_ldict(variable_name="TransitModel", variable_content=TransitModel, function_shortname=function_shortname, exist_ok=True)
                params_bat = function_builder.get_ldict(function_shortname=function_shortname)[f"params_{planet_name}_{instmod_fullname}"]
                if params_bat.t_secondary is None:  # You need params_bat.t_secondary to be different than None for the TransitModel creation
                    params_bat.t_secondary = params_bat.t0 + params_bat.per / 2  # Doing this here will change the content of the variable in ldict. So that's fine.
                function_builder.add_to_body_text(text=f"{tab}m_bat_occ_pc_{planet_name}_{instmod_fullname}_dst{dataset.number} = TransitModel(params=params_{planet_name}_{instmod_fullname}, t={time_vect}, transittype='secondary'{supersamp_text})\n", function_shortname=function_shortname)
                tic = function_builder.get_text_4_parameter(parameter=parameters['orbit']['tic'], function_shortname=function_shortname)
                function_builder.add_to_body_text(text=f"{tab}params_{planet_name}_{instmod_fullname}.t0 = {tic}\n", function_shortname=function_shortname)  # This is necessary, because the init of TransitModel modifies the params instance (which is not a good idea in my opinion, but batman is not my code)
                function_builder.add_to_done_in_text(name=f"m_bat_occ_pc_{planet_name}_{instmod_fullname}_dst{dataset.number}", function_shortname=function_shortname)

    ## Need to updata the t_secondary of a batman parameter instance for the occultation
    if do_occultation and (f"params_{planet_name}_{instmod_fullname}" not in t_sec_updates[function_shortname]):
        function_builder.add_to_body_text(text=f"{tab}params_{planet_name}_{instmod_fullname}.t_secondary = m_bat_occ_pc_{planet_name}_{instmod_fullname}_dst{dataset.number}.get_t_secondary(params_{planet_name}_{instmod_fullname})\n", function_shortname=function_shortname)
        t_sec_updates[function_shortname].append(f"params_{planet_name}_{instmod_fullname}")

    if do_occultation and (f"params_{planet_name}_{instmod_fullname}" not in fp_updates[function_shortname]):
        if not(normalize_occultation):
            Frat = function_builder.get_text_4_parameter(parameter=parameters['planet']['Frat'], function_shortname=function_shortname)
            function_builder.add_to_body_text(text=f"{tab}params_{planet_name}_{instmod_fullname}.fp = {Frat}\n", function_shortname=function_shortname)
        fp_updates[function_shortname].append(f"params_{planet_name}_{instmod_fullname}")

    if do_transit:
        return_transit = f"m_batman_{planet_name}_{instmod_fullname}_dst{dataset.number}.light_curve(params_{planet_name}_{instmod_fullname}) - 1"
    else:
        return_transit = None

    if do_occultation:
        if normalize_occultation:
            return_occultation = f"m_bat_occ_pc_{planet_name}_{instmod_fullname}_dst{dataset.number}.light_curve(params_{planet_name}_{instmod_fullname}) - 1"
        else:
            return_occultation = f"m_bat_occ_pc_{planet_name}_{instmod_fullname}_dst{dataset.number}.light_curve(params_{planet_name}_{instmod_fullname}) - 1 - {Frat}"
    else:
        return_occultation = None

    return return_transit, return_occultation
