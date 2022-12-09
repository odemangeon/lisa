#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Datasim creator RV module.
"""
from logging import getLogger
from math import sqrt

from radvel.kepler import rv_drive

from . import get_function_planet_shortname
from ...dataset_and_instrument.rv import RV_Instrument
from ....core import function_whole_shortname
from ....core.model import par_vec_name
from ....core.model.datasim_docfunc import DatasimDocFunc
from ....core.model.datasimulator_toolbox import check_datasets_and_instmodels
from ....core.model.datasimulator_timeseries_toolbox import add_time_argument, time_vec, l_time_vec  # , time_ref
from ....core.model.polynomial_model import get_polymodel
from .....tools.function_from_text_toolbox import FunctionBuilder
from .....posterior.exoplanet.model.convert import gettp_fast, getomega_fast


## Logger object
logger = getLogger()

# RVdrift_tref_name = f"{time_ref}_RVdrift"

tab = "    "


def create_datasimulator_RV(star, planets, keplerian_rv_model, dataset_db, RVcat_model, inst_models, datasets,
                            get_times_from_datasets
                            ):
    """Return a radial velocity datasimulator functions.

    A datasimualtor function is created for the whole dataset_database and for each instrument
    model individually.

    Arguments
    ---------
    star                    : Star
        Star instance corresponding to the star in the planetary system
    planets                 : dict_of_Planet
        key=planet name, value=Planet instance
    rv_model                : str
        Package used for the radial velocity model ("ajplanet" or "radvel")
    dataset_db              : DatasetDatabase
        Dataset database, this will be used by the function to access the dataset for the decorrelation,
        not to access the RV datasets to be simulated.
    RVcat_model             : RV_InstCat_Model
        Instance of the RV_InstCat_Model
    inst_models             : Instrument_Model/list_of_Instrument_Model
        If None the datasimulator does not include any contribution from the instrument.
        If Instrument_Model, return a datasimulator docfunc for this instrument model
        If list of Instrument_Model, a datasimulator is produced for each instrument model in the
            list
    datasets                : Dataset/list_of_Dataset
        If Dataset, the datasimulator include the kwargs of the dataset, so provided parameters
            of for the model, it simulates the data in the dataset.
        If None, the datasimulator function requires the time (and eventually the t_ref) on top
            of the parameters of the model.
        If list of Dataset, it has to provide exactly one dataset (no None) for each Instrument
            model in inst_models and the produced datasimulator will include the kwargs of the
            datasets.
    get_times_from_datasets : bool
        If True the times at which the RV model is computed is taken from the datasets.
        Else it is an input of the datasimulator function produced.

    Returns
    -------
    dico_docf   : dict_of_DatasimDocFunc
        key=object (planet name or whole_key), value=DatasimDocFunc
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

    func_builder.add_new_function(shortname=function_whole_shortname)
    if multi:
        func_full_name_MultiOrDst_ext = "_multi"
    else:
        func_full_name_MultiOrDst_ext = f"{l_dataset[0].dataset_code_name}"
    func_builder.set_function_fullname(full_name=f"RV_sim_{function_whole_shortname}_{func_full_name_MultiOrDst_ext}", shortname=function_whole_shortname)
    l_function_planet_shortname = [get_function_planet_shortname(planet) for planet in planets.values()]
    for function_shortname in l_function_planet_shortname:
        func_builder.add_new_function(shortname=function_shortname)
        func_builder.set_function_fullname(full_name=f"RV_sim_{function_shortname}_{func_full_name_MultiOrDst_ext}", shortname=function_shortname)

    ##########################
    # Produce Keplerian models
    ##########################
    returns_keplerian = get_RV_keplerian(multi=multi, l_inst_model=l_inst_model, l_dataset=l_dataset,
                                         get_times_from_datasets=get_times_from_datasets, keplerian_rv_model=keplerian_rv_model,
                                         planets=planets, time_vec_name=time_vec, l_time_vec_name=l_time_vec,
                                         function_builder=func_builder, ext_func_fullname=func_full_name_MultiOrDst_ext)

    ###################################################################
    # Produce instrumental variations models (Including the RV offsets)
    ###################################################################
    d_l_inst_var = get_instvar(multi=multi, l_inst_model=l_inst_model, l_dataset=l_dataset, get_times_from_datasets=get_times_from_datasets,
                               tab=tab, time_vec_name=time_vec, l_time_vec_name=l_time_vec,
                               RVcat_model=RVcat_model, dataset_db=dataset_db,
                               function_builder=func_builder, l_function_shortname=[function_whole_shortname, ],
                               ext_func_fullname=func_full_name_MultiOrDst_ext)

    #################################################
    # Produce stellar_var models (analytical, not GP)
    #################################################
    d_l_stellar_var = get_stellarvar(multi=multi, l_inst_model=l_inst_model, l_dataset=l_dataset, get_times_from_datasets=get_times_from_datasets,
                                     tab=tab, time_vec_name=time_vec, l_time_vec_name=l_time_vec, star=star,
                                     RVcat_model=RVcat_model, dataset_db=dataset_db,
                                     function_builder=func_builder, l_function_shortname=[function_whole_shortname, ],
                                     ext_func_fullname=func_full_name_MultiOrDst_ext)

    ###########################
    # Produce the decorrelation
    ###########################
    d_l_d_decorr = get_decorrelation(multi=multi, planets=planets, l_inst_model=l_inst_model, l_dataset=l_dataset,
                                     get_times_from_datasets=get_times_from_datasets,
                                     dataset_db=dataset_db, RVcat_model=RVcat_model, tab=tab, time_vec_name=time_vec,
                                     l_time_vec_name=l_time_vec, function_builder=func_builder, l_function_shortname=[function_whole_shortname, ],
                                     ext_func_fullname=func_full_name_MultiOrDst_ext)

    #######################################################################
    # Finalise the functions combining different outputs (whole and planet)
    #######################################################################
    # Function of the whole system
    for func_shortname in [function_whole_shortname, ]:
        combine_return_models(l_inst_model=l_inst_model, tab=tab, function_builder=func_builder, function_shortname=func_shortname,
                              inst_var=d_l_inst_var.get(func_shortname, None), stellar_var=d_l_stellar_var.get(func_shortname, None),
                              keplerian=returns_keplerian.get(func_shortname, None), decorrelation=d_l_d_decorr.get(func_shortname, None))

    # Function of the planets only
    for func_shortname in l_function_planet_shortname:
        combine_return_models(l_inst_model=l_inst_model, tab=tab, function_builder=func_builder, function_shortname=func_shortname,
                              inst_var=None, stellar_var=None, keplerian=returns_keplerian.get(func_shortname, None),
                              decorrelation=None)

    ###################################
    # Execute the text of all functions
    ###################################
    # Create and fill the output dictionnary containing the datasimulators functions.
    # dico_docf = dict.fromkeys(text_def_func.keys(), None)
    dico_docf = {}
    for func_shortname in func_builder.l_function_shortname:
        logger.debug(f"text of {func_shortname} RV simulator function :\n{func_builder.get_full_function_text(shortname=func_shortname)}")
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
        logger.debug(f"Parameters for {func_shortname} RV simulator function :\n{dico_param_nb}")
        dico_docf[func_shortname] = DatasimDocFunc(function=func_builder._get_ldict(function_shortname=func_shortname)[func_builder.get_function_fullname(shortname=func_shortname)],
                                                   param_model_names_list=params_model,
                                                   params_model_vect_name=par_vec_name,
                                                   inst_cats_list=instcat_docf,
                                                   inst_model_fullnames_list=instmod_docf,
                                                   dataset_names_list=dtsts_docf,
                                                   include_dataset_kwarg=get_times_from_datasets,
                                                   mand_kwargs_list=mand_kwargs,
                                                   opt_kwargs_dict=opt_kwargs,
                                                   )
    return dico_docf

    # # Iterate over the planets to create the preambules (preambule_planet and preambule_whole),
    # # the planets RV contribution (planet_rv and whole_planets_rv) and finalise the text of
    # # planets functions.
    # template_preambule = """
    # {tab}ecc_{planet} = sqrt({ecosw} * {ecosw} + {esinw} * {esinw})
    # {tab}omega_{planet} = atan2({esinw}, {ecosw})
    # {tab}tp_{planet} = gettp_fast({P}, {tic}, ecc_{planet}, omega_{planet})
    # """
    # if rv_model == "ajplanet":
    #     template_planet_rv = "pl_rv_array({time}, 0., {K}, omega_{planet}, ecc_{planet}, tp_{planet}, {P})"
    # else:
    #     template_planet_rv = "rv_drive({time}, [{P},  tp_{planet}, ecc_{planet}, omega_{planet}, {K}], use_c_kepler_solver=True)"
    #
    # # Initialise the text for the whole system preambule
    # preambule_whole = ""
    # l_whole_planets_rv = []
    # for instmdl in l_inst_model:
    #     l_whole_planets_rv.append("")
    # for i, planet in enumerate(planets.values()):
    #     # Initialise arg_list and param_nb for the current planet
    #     arg_list[planet.get_name()] = deepcopy(arg_list_before)
    #     param_nb[planet.get_name()] = param_nb_before
    #
    #     # Create two dictionaries which will contain the text for each planet parameter for the
    #     # current planet and for the whole system.
    #     params_planet = {}
    #     params_planet_only = {}
    #     params_whole = {}
    #     # Create the text for each planet parameter for the current planet and for the whole
    #     # system.
    #     l_param = [planet.K, planet.ecosw, planet.esinw, planet.tic, planet.P]
    #     for param in l_param:
    #         param_text = add_param_argument(param=param, arg_list=arg_list, key_param=key_param, param_nb=param_nb,
    #                                         key_arglist=[key_whole, planet.get_name(), planet.get_name() + ext_plonly],
    #                                         param_vector_name=par_vec_name)
    #         params_whole[param.get_name()] = param_text[key_whole]
    #         params_planet[param.get_name()] = param_text[planet.get_name()]
    #         params_planet_only[param.get_name()] = param_text[planet.get_name() + ext_plonly]
    #
    #     # Create the preambule text that compute intermediate variables
    #     preambule_planet = (dedent(template_preambule).
    #                         format(planet=planet.get_name(), ecosw=params_planet["ecosw"],
    #                                esinw=params_planet["esinw"], P=params_planet["P"],
    #                                tic=params_planet["tic"], tab=tab))
    #     preambule_planet_only = (dedent(template_preambule).
    #                              format(planet=planet.get_name(), ecosw=params_planet_only["ecosw"],
    #                                     esinw=params_planet_only["esinw"], P=params_planet_only["P"],
    #                                     tic=params_planet_only["tic"], tab=tab))
    #     preambule_whole += (dedent(template_preambule).
    #                         format(planet=planet.get_name(), ecosw=params_whole["ecosw"],
    #                                esinw=params_whole["esinw"], P=params_whole["P"],
    #                                tic=params_whole["tic"], tab=tab))
    #
    #     # planets RV contribution (planet_rv and whole_planets_rv)
    #     l_planet_rv = []
    #     l_planet_only_rv = []
    #     for ii, instmdl in enumerate(l_inst_model):
    #         if multi:
    #             time = "{ltime_vec}[{ii}]".format(ltime_vec=l_time_vec, ii=ii)
    #         else:
    #             time = time_vec
    #         l_planet_rv.append(template_planet_rv.format(planet=planet.get_name(),
    #                                                      time=time,
    #                                                      K=params_planet["K"],
    #                                                      P=params_planet["P"]))
    #         l_planet_only_rv.append(template_planet_rv.format(planet=planet.get_name(),
    #                                                           time=time,
    #                                                           K=params_planet_only["K"],
    #                                                           P=params_planet_only["P"]))
    #         l_whole_planets_rv[ii] += "+ " + template_planet_rv.format(planet=planet.get_name(),
    #                                                                    time=time,
    #                                                                    K=params_whole["K"],
    #                                                                    P=params_whole["P"])
    #
    #     # Fill returns text for each planet
    #     returns_pl = ""
    #     returns_pl_only = ""
    #     for delta_inst_rv, planet_rv, planet_only_rv, star_mean_rv in zip(l_delta_inst_rv, l_planet_rv,
    #                                                                       l_planet_only_rv, l_star_mean_rv):
    #         returns_pl += template_returns_instmod.format(delta_inst_rv=delta_inst_rv,
    #                                                       star_mean_rv=star_mean_rv,
    #                                                       planets_rv="+ " + planet_rv)
    #         returns_pl_only += template_returns_pl_only.format(planets_rv=planet_only_rv)
    #         returns_pl += ", "
    #         returns_pl_only += ", "
    #     if not(multi):  # If multi, the coma in the end ensure that the output is always a tuple (even there is actually just one dataset). This is very important for output of datasim_all_datasets.
    #         returns_pl = returns_pl[:-2]
    #         returns_pl_only = returns_pl_only[:-2]
    #
    #     # Finalise the text of planet RV simulator function
    #     # add *args, **kwargs to the function arguments if not already there
    #     if argskwargs not in arguments:
    #         arguments = add_argskwargs_argument(arguments)
    #     text_def_func[planet.get_name()] = (template_function.format(object=planet.get_name(), preambule=preambule_planet,
    #                                                                  arguments=arguments, returns=returns_pl,
    #                                                                  tab=tab))
    #     text_def_func[planet.get_name() + ext_plonly] = (template_function.format(object=planet.get_name() + ext_plonly,
    #                                                                               preambule=preambule_planet_only,
    #                                                                               arguments=arguments,
    #                                                                               returns=returns_pl_only,
    #                                                                               tab=tab))
    #
    # # Fill returns text for the whole system
    # returns_whole = ""
    # for delta_inst_rv, whole_planet_rv, star_mean_rv in zip(l_delta_inst_rv,
    #                                                         l_whole_planets_rv,
    #                                                         l_star_mean_rv):
    #     returns_whole += template_returns_instmod.format(delta_inst_rv=delta_inst_rv,
    #                                                      star_mean_rv=star_mean_rv,
    #                                                      planets_rv=whole_planet_rv)
    #     returns_whole += ", "
    # if not(multi):  # If multi, the coma in the end ensure that the output is always a tuple (even there is actually just one dataset). This is very important for output of datasim_all_datasets.
    #     returns_whole = returns_whole[:-2]
    #
    # # Finalise the  text of whole system RV simulator function
    # text_def_func[key_whole] = (template_function.format(object=key_whole,
    #                                                      preambule=preambule_whole,
    #                                                      arguments=arguments, returns=returns_whole,
    #                                                      tab=tab))
    #
    # # Create and fill the output dictionnary containing the datasimulators functions.
    # dico_docf = dict.fromkeys(text_def_func.keys(), None)
    # for obj_key in dico_docf:
    #     ldict["sqrt"] = mt.sqrt
    #     ldict["atan2"] = mt.atan2
    #     ldict["gettp_fast"] = gettp_fast
    #     if rv_model == "ajplanet":
    #         ldict["pl_rv_array"] = pl_rv_array
    #     else:
    #         ldict["rv_drive"] = rv_drive
    #     logger.debug("text of {object} RV simulator function :\n{text_func}"
    #                  "".format(object=obj_key, text_func=text_def_func[obj_key]))
    #     exec(text_def_func[obj_key], ldict)
    #     params_model = arg_list[obj_key][key_param]
    #     if len(arg_list[obj_key][key_mand_kwargs]) > 0:
    #         mand_kwargs = str(arg_list[obj_key][key_mand_kwargs])
    #     else:
    #         mand_kwargs = None
    #     if len(arg_list[obj_key][key_opt_kwargs]) > 0:
    #         opt_kwargs = str(arg_list[obj_key][key_opt_kwargs])
    #     else:
    #         opt_kwargs = None
    #     logger.debug("Parameters for {object} RV simulator function :\n{dico_param}"
    #                  "".format(object=obj_key, dico_param={nb: param for nb, param in enumerate(params_model)}))
    #     dico_docf[obj_key] = DatasimDocFunc(function=ldict[function_name.format(object=obj_key)],
    #                                         params_model=params_model,
    #                                         inst_cat=instcat_docf,
    #                                         include_dataset_kwarg=get_times_from_datasets,
    #                                         mand_kwargs=mand_kwargs,
    #                                         opt_kwargs=opt_kwargs,
    #                                         inst_model_fullname=instmod_docf,
    #                                         dataset=dtsts_docf)
    # return dico_docf


def get_instvar(multi, l_inst_model, l_dataset, get_times_from_datasets, tab, time_vec_name, l_time_vec_name,
                RVcat_model, dataset_db,
                function_builder, l_function_shortname, ext_func_fullname):
    """Get the instrumental variation contribution to the RVs including the RV offsets

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
    RVcat_model                 : RV_InstCat_Model
        Instance of the RV_InstCat_Model
        Not used right now but there to be able to produce instrumental drift in the future
    dataset_db                  : DatasetDatabase
        Dataset database, this will be used by the function to access the all the RV dataset,
        not only the datasets to be simulated.
        Not used right now but there to be able to produce instrumental drift in the future
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
        Dictionary of list of str giving the return for instvar for each function and each output
    """
    return get_polymodel(multi=multi, l_inst_model=l_inst_model, l_dataset=l_dataset, get_times_from_datasets=get_times_from_datasets,
                         tab=tab, time_vec_name=time_vec_name, l_time_vec_name=l_time_vec_name, inst_cat_model=RVcat_model,
                         dataset_db=dataset_db, function_builder=function_builder, l_function_shortname=l_function_shortname,
                         polyonly_func_shortname="inst_var", ext_func_fullname=ext_func_fullname, name_coeff_const="DeltaRV",
                         func_param_name=lambda order: RV_Instrument.get_polymodel_param_name(inst_model=None, order=order),
                         instrument_per_instrument_model=True, param_container=None, prefix_config=None,
                         )
    # ########################
    # # Initialise the outputs
    # ########################
    # returns = {}
    #
    # #############################################################################
    # # Check if any of the instrument model needs an inst var model
    # #############################################################################
    # # If there there is more than one instrument models there will be a detlaRV in between them, so inst_var is required
    # if len(set(l_inst_model)) > 1:
    #     requires_instvar = True
    # else:
    #     instmdl = l_inst_model[0]
    #     if instmdl.get_with_inst_var():
    #         requires_instvar = True
    #     else:
    #         inst_name = instmdl.instrument.get_name()
    #         instmdl_name = instmdl.get_name()
    #         ## RVref4inst_modname: name of the instrument model chosen as reference for the
    #         ## current instrument (eg: default)
    #         RVref4inst_modname = RV_instref_modnames[inst_name]
    #         if (RV_globalref_instname == inst_name) and (RVref4inst_modname == instmdl_name):
    #             requires_instvar = False
    #         else:
    #             requires_instvar = True
    #
    # if requires_instvar:
    #     #################################################
    #     # Initialise the new function in function_builder
    #     #################################################
    #     # Extension for the shortname of the function that do the decorrelation only model
    #     inst_var_func_shortname = "inst_var"
    #     function_builder.add_new_function(shortname=inst_var_func_shortname)
    #     function_builder.set_function_fullname(full_name=f"RV_sim_{inst_var_func_shortname}{ext_func_fullname}", shortname=inst_var_func_shortname)
    #
    #     ########################################
    #     # Update the list of function to address
    #     ########################################
    #     l_function_shortname += [inst_var_func_shortname, ]
    #
    #     ################################
    #     # Do the Model for each function
    #     ################################
    #     for function_shortname in l_function_shortname:
    #         returns[function_shortname] = []
    #
    #         # Add the time argument
    #         # Even if the model is a constant you want to generate a vector of constant values that can
    #         # compared with the data (for the likelihood computation) or plotted without issue
    #         time_arg_name = add_time_argument(function_builder=function_builder, function_shortname=function_shortname,
    #                                           multi=multi, get_times_from_datasets=get_times_from_datasets,
    #                                           l_dataset=l_dataset, time_vec_name=time_vec_name, l_time_vec_name=l_time_vec_name,
    #                                           exist_ok=True)
    #
    #         # For each instrument model and dataset, ...
    #         for ii, instmdl in enumerate(l_inst_model):
    #             returns[function_shortname].append("")
    #             inst_name = instmdl.instrument.get_name()
    #             ## RVref4inst_modname: name of the instrument model chosen as reference for the
    #             ## current instrument (eg: default)
    #             RVref4inst_modname = RV_instref_modnames[inst_name]
    #             # Get the Delta_RV of the global RV reference instrument model if needed
    #             if inst_name != RV_globalref_instname:
    #                 instmod_RVref4inst = RV_inst_db[inst_name][RVref4inst_modname]
    #                 if instmod_RVref4inst.DeltaRV.main:
    #                     function_builder.add_parameter(parameter=instmod_RVref4inst.DeltaRV, function_shortname=function_shortname)
    #                     DeltaRV_instmod_RVref4inst = function_builder.get_text_4_parameter(parameter=instmod_RVref4inst.DeltaRV, function_shortname=function_shortname)
    #             else:
    #                 DeltaRV_instmod_RVref4inst = 0.
    #             # Get the Delta_RV of the model used as RV reference for the current instrument
    #             if instmdl.get_name() != RVref4inst_modname:
    #                 if instmdl.DeltaRV.main:
    #                     function_builder.add_parameter(parameter=instmdl.DeltaRV, function_shortname=function_shortname)
    #                     DeltaRV_instmod = function_builder.get_text_4_parameter(parameter=instmdl.DeltaRV, function_shortname=function_shortname)
    #             else:
    #                 DeltaRV_instmod = 0.
    #             # Write the RV offset contribution (from global RV reference and/or the the model used as RV reference for the current instrument)
    #             DeltaRV = ""
    #             if (DeltaRV_instmod_RVref4inst != 0.0) and (DeltaRV_instmod != 0.0):
    #                 DeltaRV = f"({DeltaRV_instmod_RVref4inst} + {DeltaRV_instmod})"
    #             elif DeltaRV_instmod_RVref4inst != 0.0:
    #                 DeltaRV = f"{DeltaRV_instmod_RVref4inst}"
    #             elif DeltaRV_instmod != 0.0:
    #                 DeltaRV = f"{DeltaRV_instmod}"
    #             if DeltaRV != "":
    #                 if not(instmdl.get_with_inst_var()) or (instmdl.get_inst_var_order() == 0):
    #                     function_builder.add_variable_to_ldict(variable_name="ones_like", variable_content=ones_like,
    #                                                            function_shortname=function_shortname,
    #                                                            exist_ok=True)
    #                     if multi:
    #                         returns[function_shortname][ii] += f"{DeltaRV} * ones_like({time_arg_name}[{ii}])"
    #                     else:
    #                         returns[function_shortname][ii] += f"{DeltaRV} * ones_like({time_arg_name})"
    #                 else:
    #                     if returns[function_shortname][ii] == "":
    #                         pretext = ""
    #                     else:
    #                         pretext = " + "
    #                     returns[function_shortname][ii] += f"{pretext}{DeltaRV_instmod}"
    #             # ..., if instrument variations have been asked, ...
    #             if instmdl.get_with_inst_var() and (instmdl.get_inst_var_order() > 0):
    #                 # ..., For each order in the required polynomial model, ...
    #                 for order in range(1, instmdl.get_inst_var_order() + 1):
    #                     # ..., get the name and full name of the parameter for this order
    #                     instvar_param_name = instmdl.get_inst_var_param_name(order)
    #                     # ..., If this parameter is a main parameter (it should be), ...
    #                     if instmdl.parameters[instvar_param_name].main:
    #                         function_builder.add_parameter(parameter=instmdl.parameters[instvar_param_name], function_shortname=function_shortname)
    #                         text_instvar_param = function_builder.get_text_4_parameter(parameter=instmdl.parameters[instvar_param_name], function_shortname=function_shortname)
    #                         # ..., if the parameter is free or the fixed value is not zero, ...
    #                         if text_instvar_param != 0.0:
    #                             if returns[function_shortname][ii] == "":
    #                                 pretext = ""
    #                             else:
    #                                 pretext = " + "
    #                             returns[function_shortname][ii] += f"{pretext}{text_instvar_param}"
    #                             # ..., and you need a time reference. There is one time reference per instrument
    #                             # model, which is automatically set to the time of the first measurement
    #                             # among the datasets associated with this instrument model.
    #                             # So start be creating the name of the instrument model
    #                             timeref_instmod = f"timeref_instvar_{instmdl.full_code_name}"
    #                             # if this time_reference is not already in the ldict of the function ...
    #                             if timeref_instmod not in function_builder.get_ldict(function_shortname=function_shortname):
    #                                 # we have to compute its value and add it to the ldict
    #                                 l_dataset_name_instmod = RVcat_model.get_l_datasetname(instmod_fullnames=instmdl.full_name)
    #                                 timeref_instmod_value = min([min(dataset_db[dataset_name].get_time()) for dataset_name in l_dataset_name_instmod])
    #                                 function_builder.add_variable_to_ldict(variable_name=timeref_instmod, variable_content=timeref_instmod_value, function_shortname=function_shortname)
    #                             # ..., add the end of this order's contribution to the text of the instruments variations, ...
    #                             if order == 1:
    #                                 if multi:
    #                                     returns[function_shortname][ii] += f" * ({time_arg_name}[{ii}] - {timeref_instmod})"
    #                                 else:
    #                                     returns[function_shortname][ii] += f" * ({time_arg_name} - {timeref_instmod})"
    #                             elif order > 1:
    #                                 if multi:
    #                                     returns[function_shortname][ii] += (f" * ({time_arg_name}[{ii}] - {timeref_instmod})**{order}")
    #                                 else:
    #                                     returns[function_shortname][ii] += (f" * ({time_arg_name} - {timeref_instmod})**{order}")
    #
    #     #####################################
    #     # Finalize the inst_var only function
    #     #####################################
    #     for func_shortname in [inst_var_func_shortname, ]:
    #         l_return = [output_i if output_i != "" else 'None' for output_i in returns.pop(func_shortname)]
    #         function_builder.add_to_body_text(text=f"{tab}return {', '.join(l_return)}", function_shortname=func_shortname)
    #
    # return returns


def get_stellarvar(multi, l_inst_model, l_dataset, get_times_from_datasets,
                   tab, time_vec_name, l_time_vec_name,
                   star, RVcat_model, dataset_db,
                   function_builder, l_function_shortname, ext_func_fullname):
    """Get the stellar variation contribution to the RVs including the systemic velocity

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
    RVcat_model                 : RV_InstCat_Model
        Instance of the RV_InstCat_Model
    dataset_db                  : DatasetDatabase
        Dataset database, this will be used by the function to access the all the RV dataset,
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
                         tab=tab, time_vec_name=time_vec_name, l_time_vec_name=l_time_vec_name, inst_cat_model=RVcat_model,
                         dataset_db=dataset_db, function_builder=function_builder, l_function_shortname=l_function_shortname,
                         polyonly_func_shortname="stellar_var", ext_func_fullname=ext_func_fullname, name_coeff_const=star.__name_coeff_const_RV__,
                         func_param_name=lambda order: star.get_polymodel_param_name(order=order, inst_cat=RVcat_model.inst_cat),
                         instrument_per_instrument_model=False, param_container=star, prefix_config=RVcat_model.inst_cat,
                         )
    # ########################
    # # Initialise the outputs
    # ########################
    # returns = {}
    #
    # #################################################
    # # Initialise the new function in function_builder
    # #################################################
    # # Extension for the shortname of the function that do the decorrelation only model
    # stellar_var_func_shortname = "stellar_var"
    # function_builder.add_new_function(shortname=stellar_var_func_shortname)
    # function_builder.set_function_fullname(full_name=f"RV_sim_{stellar_var_func_shortname}{ext_func_fullname}", shortname=stellar_var_func_shortname)
    #
    # ########################################
    # # Update the list of function to address
    # ########################################
    # l_function_shortname += [stellar_var_func_shortname, ]
    #
    # ################################
    # # Do the Model for each function
    # ################################
    # for function_shortname in l_function_shortname:
    #     returns[function_shortname] = []
    #
    #     # Add the time argument
    #     # Even if the model is a constant you want to generate a vector of constant values that can
    #     # compared with the data (for the likelihood computation) or plotted without issue
    #     time_arg_name = add_time_argument(function_builder=function_builder, function_shortname=function_shortname,
    #                                       multi=multi, get_times_from_datasets=get_times_from_datasets,
    #                                       l_dataset=l_dataset, time_vec_name=time_vec_name, l_time_vec_name=l_time_vec_name,
    #                                       exist_ok=True)
    #
    #     # For each instrument model and dataset, ...
    #     for ii, instmdl in enumerate(l_inst_model):
    #         returns[function_shortname].append("")
    #         # Add the systemic velocity
    #         if star.v0.main:
    #             function_builder.add_parameter(parameter=star.v0, function_shortname=function_shortname)
    #             star_v0 = function_builder.get_text_4_parameter(parameter=star.v0, function_shortname=function_shortname)
    #             if star_v0 != 0.0:
    #                 if not(star.with_RVdrift) or (star.RVdrift_order == 0):
    #                     function_builder.add_variable_to_ldict(variable_name="ones_like", variable_content=ones_like,
    #                                                            function_shortname=function_shortname,
    #                                                            exist_ok=True)
    #                     if multi:
    #                         returns[function_shortname][ii] += f"{star_v0} * ones_like({time_arg_name}[{ii}])"
    #                     else:
    #                         returns[function_shortname][ii] += f"{star_v0} * ones_like({time_arg_name})"
    #                 else:
    #                     if returns[function_shortname][ii] == "":
    #                         pretext = ""
    #                     else:
    #                         pretext = " + "
    #                     returns[function_shortname][ii] += f"{pretext}{star_v0}"
    #         # Add the drift components
    #         if star.with_RVdrift:
    #             # ..., For each order in the required polynomial model, ...
    #             for order in range(1, star.RVdrift_order + 1):
    #                 # ..., get the name and full name of the parameter for this order
    #                 RVdrift_param_name = star.get_RVdrift_param_name(order)
    #                 # ..., If this parameter is a main parameter (it should be), ...
    #                 if star.parameters[RVdrift_param_name].main:
    #                     function_builder.add_parameter(parameter=star.parameters[RVdrift_param_name], function_shortname=function_shortname)
    #                     text_stellarvar_param = function_builder.get_text_4_parameter(parameter=star.parameters[RVdrift_param_name], function_shortname=function_shortname)
    #                     # ..., if the parameter is free or the fixed value is not zero, ...
    #                     if text_stellarvar_param != 0.0:
    #                         if returns[function_shortname][ii] == "":
    #                             pretext = ""
    #                         else:
    #                             pretext = " + "
    #                         returns[function_shortname][ii] += f"{pretext}{text_stellarvar_param}"
    #                         # ..., and you need a time reference. There is one time reference
    #                         # which is automatically set to the time of the first RV measurement
    #                         timeref_stellarvar = "timeref_stellarvar"
    #                         # if this time_reference is not already in the ldict of the function ...
    #                         if timeref_stellarvar not in function_builder.get_ldict(function_shortname=function_shortname):
    #                             # we have to compute its value and add it to the ldict
    #                             l_dataset_name_RV = RVcat_model.get_l_datasetname()
    #                             timeref_instmod_value = min([min(dataset_db[dataset_name].get_time()) for dataset_name in l_dataset_name_RV])
    #                             function_builder.add_variable_to_ldict(variable_name=timeref_stellarvar, variable_content=timeref_instmod_value, function_shortname=function_shortname)
    #                         if order == 1:
    #                             if multi:
    #                                 returns[function_shortname][ii] += f" * ({time_arg_name}[{ii}] - {timeref_stellarvar})"
    #                             else:
    #                                 returns[function_shortname][ii] += f" * ({time_arg_name} - {timeref_stellarvar})"
    #                         elif order > 1:
    #                             if multi:
    #                                 returns[function_shortname][ii] += (f" * ({time_arg_name}[{ii}] - {timeref_stellarvar})**{order}")
    #                             else:
    #                                 returns[function_shortname][ii] += (f" * ({time_arg_name} - {timeref_stellarvar})**{order}")
    #
    # #####################################
    # # Finalize the inst_var only function
    # #####################################
    # for func_shortname in [stellar_var_func_shortname, ]:
    #     l_return = [output_i if output_i != "" else 'None' for output_i in returns.pop(func_shortname)]
    #     function_builder.add_to_body_text(text=f"{tab}return {', '.join(l_return)}", function_shortname=func_shortname)
    #
    # return returns


def get_RV_keplerian(multi, l_inst_model, l_dataset, get_times_from_datasets, keplerian_rv_model, planets,
                     time_vec_name, l_time_vec_name, function_builder, ext_func_fullname):
    """Provide the text for the rv keplerian part of the RV model text (preambule and return).

    This function should generate the text for the "<function_whole_shortname>" function, the "<planet>"
    functions.

    Arguments
    ---------

    Returns
    -------
    """
    ########################
    # Initialise the outputs
    ########################
    returns = {}

    # Extension for the shortname of the function that do the radial velocity keplerian only model
    ext_func_keprv_only = "_keprv"

    ##############################
    # Do the Model for each planet
    ##############################
    for planet in planets.values():
        planet_name = planet.get_name()
        if keplerian_rv_model.get_do(planet_name=planet_name):
            ########################################################################
            # Define the functions to populate and initialise entries in the outputs
            ########################################################################
            # Defines the lists of function shortnames and add the new transit only function into the function builder
            l_whole_function_shortname = [function_whole_shortname, ]
            l_planet_function_shortname_ext = ["", ext_func_keprv_only]
            l_planet_function_shortname = []
            for planet_func_shortname_ext in l_planet_function_shortname_ext:
                l_planet_function_shortname.append(f"{get_function_planet_shortname(planet)}{planet_func_shortname_ext}")
            l_function_shortname_4_planet = l_whole_function_shortname + l_planet_function_shortname

            ##################################################
            # Initialise the new functions in function_builder
            ##################################################
            l_func_shortname_ext_to_create = [ext_func_keprv_only, ]
            for func_shortname_ext in l_func_shortname_ext_to_create:
                func_shortname_tr_pl_only = f"{get_function_planet_shortname(planet)}{ext_func_keprv_only}"
                function_builder.add_new_function(shortname=func_shortname_tr_pl_only)
                function_builder.set_function_fullname(full_name=f"RV_sim_{func_shortname_tr_pl_only}_{ext_func_fullname}", shortname=func_shortname_tr_pl_only)

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

            ###########################################
            # Get the keplerian RV model
            ###########################################
            rv_model = keplerian_rv_model.get_model(planet_name=planet_name)

            ####################################################################
            # Do the Model for each planet and each instrument and each function
            ####################################################################
            for func_shortname in l_function_shortname_4_planet:

                for i_inputoutput, (instmod, dst) in enumerate(zip(l_inst_model, l_dataset)):
                    instmod_fullname = instmod.full_name

                    ###########################################
                    # Add the parameters required for the model
                    ###########################################
                    # make sure that all the required parameters are added to the function in the function_builder
                    parameters = rv_model.get_parameters(inst_model_fullname=instmod_fullname, object_category=None)
                    for object_category in parameters:
                        for param in parameters[object_category].values():
                            function_builder.add_parameter(parameter=param, function_shortname=func_shortname, exist_ok=True)

                    ##############
                    # Radvel model
                    ##############
                    if rv_model.category == "radvel":
                        ## writing the preambule and return (First preambules after returns)
                        ## preambule: Get the parameter values
                        period = function_builder.get_text_4_parameter(parameter=parameters['orbit']['P'], function_shortname=func_shortname)
                        ecosw = function_builder.get_text_4_parameter(parameter=parameters['orbit']['ecosw'], function_shortname=func_shortname)
                        esinw = function_builder.get_text_4_parameter(parameter=parameters['orbit']['esinw'], function_shortname=func_shortname)
                        tic = function_builder.get_text_4_parameter(parameter=parameters['orbit']['tic'], function_shortname=func_shortname)
                        K = function_builder.get_text_4_parameter(parameter=parameters['planet']['K'], function_shortname=func_shortname)
                        if not(function_builder.is_done_in_text(name=f"ecc_{planet_name}", function_shortname=func_shortname)):
                            function_builder.add_variable_to_ldict(variable_name="sqrt", variable_content=sqrt, function_shortname=func_shortname, exist_ok=True)
                            function_builder.add_to_body_text(text=f"{tab}ecc_{planet_name} = sqrt({ecosw} * {ecosw} + {esinw} * {esinw})\n", function_shortname=func_shortname)
                            function_builder.add_to_done_in_text(name=f"ecc_{planet_name}", function_shortname=func_shortname)
                        if not(function_builder.is_done_in_text(name=f"omega_{planet_name}", function_shortname=func_shortname)):
                            function_builder.add_variable_to_ldict(variable_name="getomega_fast", variable_content=getomega_fast, function_shortname=func_shortname, exist_ok=True)
                            function_builder.add_to_body_text(text=f"{tab}omega_{planet_name} = getomega_fast({esinw}, {ecosw})\n", function_shortname=func_shortname)
                            function_builder.add_to_done_in_text(name=f"omega_{planet_name}", function_shortname=func_shortname)
                        if not(function_builder.is_done_in_text(name=f"tp_{planet_name}", function_shortname=func_shortname)):
                            function_builder.add_variable_to_ldict(variable_name="gettp_fast", variable_content=gettp_fast, function_shortname=func_shortname, exist_ok=True)
                            function_builder.add_to_body_text(text=f"{tab}tp_{planet_name} = gettp_fast({period}, {tic}, ecc_{planet_name}, omega_{planet_name})\n", function_shortname=func_shortname)
                            function_builder.add_to_done_in_text(name=f"tp_{planet_name}", function_shortname=func_shortname)
                        ## writing the returns
                        if returns[func_shortname][i_inputoutput] == "":
                            pre_text = ""
                        else:
                            pre_text = " + "
                        if multi:
                            time_vect = f"{time_arg_name}[{i_inputoutput}]"
                        else:
                            time_vect = f"{time_arg_name}"
                        function_builder.add_variable_to_ldict(variable_name="rv_drive", variable_content=rv_drive, function_shortname=func_shortname, exist_ok=True)
                        returns[func_shortname][i_inputoutput] += f"{pre_text}rv_drive({time_vect}, [{period},  tp_{planet_name}, ecc_{planet_name}, omega_{planet_name}, {K}], use_c_kepler_solver=True)"

                    ########################
                    # No other model for now
                    ########################
                    else:
                        raise ValueError(f"RV keplerian model {rv_model} is not recognized.")

    ############################################
    # Finalize the planets radial velocity keplerian only function
    ############################################
    for planet in planets.values():
        planet_name = planet.get_name()
        if keplerian_rv_model.get_do(planet_name=planet_name):
            func_shortname = f"{get_function_planet_shortname(planet)}{ext_func_keprv_only}"
            function_builder.add_to_body_text(text=f"{tab}return {', '.join(returns.pop(func_shortname))}",
                                              function_shortname=func_shortname)

    return returns


def get_decorrelation(multi, planets, l_inst_model, l_dataset, get_times_from_datasets, dataset_db,
                      RVcat_model, tab, time_vec_name, l_time_vec_name, function_builder, l_function_shortname,
                      ext_func_fullname):
    """Provide the text for the decorrelation of the RV model text (return).

    It should provide the text for decorrelation model for all functions requested (l_function_shortname)
    ands separately for each instrument model and each part of the RV model to decorrelate.

    The output of this methods will be used by combine_return_models when filling the template of the functions
    in datasim_creator_rv.

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
    RVcat_model              : RV_InstCat_Model
        RV_InstCat_Model instance for the current model
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
        if RVcat_model.require_model_decorrelation(instmod_fullname=instmod_obj.full_name):
            requires_decorr = True
            break

    if requires_decorr:
        decorrelation_config = RVcat_model.decorrelation_model_config
        #################################################
        # Initialise the new function in function_builder
        #################################################
        # Extension for the shortname of the function that do the decorrelation only model
        decorr_func_shortname = "decorr"
        function_builder.add_new_function(shortname=decorr_func_shortname)
        function_builder.set_function_fullname(full_name=f"RV_sim_{decorr_func_shortname}{ext_func_fullname}", shortname=decorr_func_shortname)

        ########################################
        # Update the list of function to address
        ########################################
        l_function_shortname += [decorr_func_shortname, ]

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
                    l_dataset_name_instmod = RVcat_model.get_l_datasetname(instmod_fullnames=instmod.full_name)
                    for model_part, config_decorr_instmod_modelpart in decorrelation_config[instmod.full_name]["what to decorrelate"].items():
                        text_decorr = RVcat_model.create_text_decorr(multi=multi, inst_mod_obj=instmod, idx_inst_mod_obj=i_inputoutput,
                                                                     l_dataset_name_instmod=l_dataset_name_instmod,
                                                                     dataset_db=dataset_db, decorrelation_config_instmod=config_decorr_instmod_modelpart,
                                                                     model_part=model_part, time_arg_name=time_arg_name,
                                                                     function_builder=function_builder, function_shortname=func_shortname)
                        if text_decorr != "":
                            returns[func_shortname][i_inputoutput][model_part] = text_decorr

        ##########################################
        # Finalize the decorrelation only function
        ##########################################
        for func_shortname in [decorr_func_shortname, ]:
            return_text = ""
            for dico_config_return_instmodel in returns.pop(func_shortname):
                return_text += '{'
                for model_part, text in dico_config_return_instmodel.items():
                    return_text += f"'{model_part}': {text}, "
                return_text += '}, '
            return_text = return_text[:-2]

            function_builder.add_to_body_text(text=f"{tab}return {return_text}", function_shortname=func_shortname)

    return returns


def combine_return_models(l_inst_model, tab, function_builder, function_shortname, keplerian=None,
                          inst_var=None, stellar_var=None, decorrelation=None):
    """
    """
    return_text = []
    for i_inputoutput, instmod in enumerate(l_inst_model):
        return_text.append("")

        for component in [keplerian, inst_var, stellar_var]:
            if (component is not None) and (component[i_inputoutput] != ""):
                if return_text[i_inputoutput] == "":
                    pretext = ""
                else:
                    pretext = " + "
                return_text[i_inputoutput] += pretext + component[i_inputoutput]

        if decorrelation is not None:
            if return_text[i_inputoutput] == "":
                pretext = ""
            else:
                pretext = " + "
            if "multiply_2_totalrv" in decorrelation[i_inputoutput]:
                return_text[i_inputoutput] = "(" + return_text[i_inputoutput] + ")"
                return_text[i_inputoutput] += f" * ({decorrelation[i_inputoutput]['multiply_2_totalrv']})"
            if "add_2_totalrv" in decorrelation[i_inputoutput]:
                return_text[i_inputoutput] += f" + ({decorrelation[i_inputoutput]['add_2_totalrv']})"

    function_builder.add_to_body_text(text=f"{tab}return {', '.join(return_text)}", function_shortname=function_shortname)

# def get_starmeanrv_and_deltarv(l_inst_model, l_dataset, star, multi, RV_globalref_instname, RV_instref_modnames,
#                                RV_inst_db, ldict, arguments, param_nb, arg_list, key_whole, key_param,
#                                key_mand_kwargs, key_opt_kwargs, time_vec_name=time_vec, l_time_vec_name=l_time_vec,
#                                timeref_name=RVdrift_tref_name, use_dataset_4_tref=False, time_ref_val=None):
#     """Get the contribution of the systemic/star rv contribution and the instrumental delta RV.
#
#     Arguments:
#     ----------
#     l_inst_model          : list of Instrument Models
#         Checked list of Instrument_Model instance(s).
#     l_dataset             : list_of_Dataset
#         Checked list of Dataset instance(s).
#     star                  : Star
#         Star instance corresponding to the star in the planetary system
#     multi                 : bool
#         True if the datasim function needs multiple outputs.
#     RV_globalref_instname : string
#         Instrument name of the instrument used as RV reference
#     RV_instref_modnames   : dict
#         key=instrument name, value=instrument model name (not full name) used as reference for the instrument
#     RV_inst_db            : dict
#         key=instrument name, value=dict: key= instrument model name, value=instrument model object.
#     ldict                 : dict
#         dictionary to be used as local dictionary argument of the exec function.
#         THIS DICTIONARY IS MODIFIED EVEN IF NOT RETURNED
#     arguments             : str
#         string giving the current text of arguments
#     param_nb              : dict_of_int
#         dictionary with key = key_whole, value = current number of free parameters in the model
#         THIS DICTIONARY IS MODIFIED EVEN IF NOT RETURNED
#     arg_list              : dict
#         dictionary with key = key_whole, value = dict with key = key_param, value = list of parameter
#         full names THIS DICTIONARY IS MODIFIED EVEN IF NOT RETURNED
#     key_whole             : string
#         Key used for the whole system
#     key_param             : string
#         Key used for the parameters entry of arg_list
#     key_mand_kwargs       : str
#         Key used for the mandatory keyword argument entry of arg_list
#     key_opt_kwargs        : str
#         Key used for the optional keyword argument entry of arg_list
#     time_vec_name         : str
#         Str used to design the time vector
#     l_time_vec_name       : str
#         Str used to design the list of time vector
#     timeref_name          : str
#         Str used to design the time reference for the RV drift
#     use_dataset_4_tref    : bool
#         If True, then the dataset will be used to compute the reference time for the RV drift
#     time_ref_val          :
#         Value of the time reference if not computed from the datasets
#
#     Returns
#     -------
#     l_delta_inst_rv       : list_of_string
#         list give the string representation of the contributions of the instrumental delta_rv for each
#         couple instrument model - dataset in l_inst_model and l_dataset.
#     l_star_mean_rv        : list_of_string
#         list give the string representation of the contribution of the systemic/star rv  for each couple
#         instrument model - dataset in l_inst_model and l_dataset.
#     arguments             : str
#         Updated string giving the new text of arguments
#     """
#     # Check if datasets are provided
#     has_dataset = get_has_datasets(l_dataset)
#     # Create list for the text of each instrument Delta RV (delta_inst_rv)
#     l_delta_inst_rv = []
#     # Create list for the text of each instrument star_mean_rv (delta_inst_rv)
#     l_star_mean_rv = []
#     for ii, instmdl, dst in zip(range(len(l_inst_model)), l_inst_model, l_dataset):
#         l_delta_inst_rv.append("")
#         if instmdl is not None:
#             inst_name = instmdl.instrument.get_name()
#             ## RVrefglobal_inst: name of the instrument chosen as global RV reference
#             ## (eg: HARPS)
#             RVrefglobal_instname = RV_globalref_instname
#             ## RVref4inst_modname: name of the instrument model chosen as reference for the
#             ## current instrument (eg: default)
#             RVref4inst_modname = RV_instref_modnames[inst_name]
#             # Add the Delta_RV of the global RV reference instrument model if needed
#             if inst_name != RVrefglobal_instname:
#                 instmod_RVref4inst = RV_inst_db[inst_name][RVref4inst_modname]
#                 if instmod_RVref4inst.DeltaRV.main:
#                     l_delta_inst_rv[ii] += (add_param_argument(param=instmod_RVref4inst.DeltaRV, arg_list=arg_list,
#                                                                key_param=key_param, param_nb=param_nb,
#                                                                key_arglist=key_whole, param_vector_name=par_vec_name)[key_whole] +
#                                             " + ")
#             # Add the Delta_RV of the model used as RV reference for the current instrument
#             if instmdl.get_name() != RVref4inst_modname:
#                 if instmdl.DeltaRV.main:
#                     l_delta_inst_rv[ii] += (add_param_argument(param=instmdl.DeltaRV, arg_list=arg_list,
#                                                                key_param=key_param, param_nb=param_nb,
#                                                                key_arglist=key_whole, param_vector_name=par_vec_name)[key_whole] +
#                                             " + ")
#         # Create the text for the star mean RV (star_mean_rv)
#         l_star_mean_rv.append("")
#         l_star_mean_rv[ii] += add_param_argument(param=star.v0, arg_list=arg_list, key_param=key_param,
#                                                  param_nb=param_nb, key_arglist=key_whole, param_vector_name=par_vec_name)[key_whole]
#
#         # If stellar RV drift has been asked, create the text for stellar RV drift, ...
#         if star.with_RVdrift:
#             # ..., if neither "tref" nor "l_tref" are in the list of kwargs and
#             # no dataset is provided, ...
#             if timeref_name not in arg_list[key_whole][key_mand_kwargs] + arg_list[key_whole][key_opt_kwargs]:
#                 if multi:
#                     def get_time_ref(l_time):
#                         return floor(min(concatenate[l_time]))
#                 else:
#                     def get_time_ref(time):
#                         return min(time)
#                 (arguments, timeref_arg_name, timeref_arg, timeref_arg_in_arguments
#                  ) = add_timeref_arguments(arguments=arguments, multi=multi, vect_for_multi=False,
#                                            use_dataset=use_dataset_4_tref, arg_list=arg_list, key_arglist=key_whole,
#                                            key_mand_kwargs=key_mand_kwargs, key_opt_kwargs=key_opt_kwargs,
#                                            ldict=ldict, has_dataset=has_dataset, get_time_ref=get_time_ref,
#                                            time_ref_val=time_ref_val, l_dataset=l_dataset,
#                                            timeref_name=timeref_name, time_vec_name=time_vec_name,
#                                            l_time_vec_name=l_time_vec_name)
#                 if timeref_arg is None:
#                     # The value has been added to ldict and you nned to use timeref_arg_name in the text of the function
#                     timeref = timeref_arg_name
#                 else:
#                     # The value to use in the text is timeref_arg
#                     timeref = timeref_arg
#             # ..., For each order in the required polynomial model (zero is the system mean
#             # velocity, so the orders starts at 1), ...
#             for order in range(1, star.RVdrift_order + 1):
#                 # ..., get the name and full name of the parameter for this order
#                 RVdrift_param_name = star.get_RVdrift_param_name(order)
#                 # ..., If this parameter is a main parameter (it should be), ...
#                 if star.parameters[RVdrift_param_name].main:
#                     value_not0 = True
#                     text_RV_drift_param = add_param_argument(param=star.parameters[RVdrift_param_name],
#                                                              arg_list=arg_list, key_param=key_param,
#                                                              param_nb=param_nb, key_arglist=key_whole,
#                                                              param_vector_name=par_vec_name)[key_whole]
#                     # ..., if the parameter is free or the fixed value is not zero, ...
#                     if text_RV_drift_param != str(0.0):
#                         l_star_mean_rv[ii] += "+ {}".format(text_RV_drift_param)
#                     # ..., else, since the fixed value is zero, this order doesn't have any
#                     # contribution
#                     else:
#                         value_not0 = False
#                     # ..., if the order has a contribution to the RV drift, ...
#                     if value_not0:
#                         # ..., add the end of this order's contribution to the text of the RV drift.
#                         if order == 1:
#                             if multi:
#                                 l_star_mean_rv[ii] += (f" * ({l_time_vec_name}[{ii}] - {timeref}) ")
#                             else:
#                                 l_star_mean_rv[ii] += (f" * ({time_vec_name} - {timeref}) ")
#                         elif order > 1:
#                             if multi:
#                                 l_star_mean_rv[ii] += (f" * ({l_time_vec_name}[{ii}] - {timeref})**{order}")
#                             else:
#                                 l_star_mean_rv[ii] += (f" * ({time_vec_name} - {timeref})**{order}")
#     return l_star_mean_rv, l_delta_inst_rv, arguments
