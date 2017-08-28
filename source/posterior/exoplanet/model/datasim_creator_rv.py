#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Datasim creator RV module.
"""
from logging import getLogger
from textwrap import dedent
from collections import OrderedDict
from copy import deepcopy

from ajplanet import pl_rv_array

from ..dataset_and_instrument.rv import RV_inst_cat
from ...core.model.datasim_docfunc import DatasimDocFunc
from ...core.dataset_and_instrument.instrument import Instrument_Model
from ...core.dataset_and_instrument.dataset import Dataset
from ....tools.convert import getecc_fast, getomega_fast, gettp_fast


## Logger object
logger = getLogger()


def create_datasimulator_RV(star, planets, key_whole,
                            RV_globalref_instname=None,
                            RV_instref_modnames=None,
                            RV_inst_db=None,
                            inst_models=None, datasets=None):
    """Return a radial velocity datasimulator functions.

    A datasimualtor function is created for the whole dataset_database and for each instrument
    model individually.

    :param Star star: Star instance corresponding to the star in the planetary system
    :param dict planets: key=planet name, value=Planet instance
    :param string key_whole: Key used for the whole system
    :param string RV_globalref_instname: Instrument name of the instrument used as RV reference
    :param dict RV_instref_modnames: key=instrument name, value=instrument model name (not
        full name) used as reference for the instrument
    :param dict RV_inst_db: key=instrument name, value=dict: key= instrument model name,
        value=instrument model object.
    :param Instrument_Model/list_of_Instrument_Model/None inst_models:
        If None the datasimulator does not include any contribution from the instrument.
        If Instrument_Model, return a datasimulator docfunc for this instrument model
        If list of Instrument_Model, a datasimulator is produced for each instrument model in the
            list
    :param Dataset/list_of_Dataset datasets:
        If Dataset, the datasimulator include the kwargs of the dataset, so provided parameters
            of for the model, it simulates the data in the dataset.
        If None, the datasimulator function requires the time (and eventually the t_ref) on top
            of the parameters of the model.
        If list of Dataset, it has to provide exactly one dataset (no None) for each Instrument
            model in inst_models and the produced datasimulator will include the kwargs of the
            datasets.
    :return dict dico_docf: key=object (planet name or whole_key), value=DatasimDocFunc
    """
    # Check the content of inst_model_fullnames: If not provided or string set multi_inst_model
    # to False, otherwise to True. And set the inst_model_fullnames argument for the Datasim_DocFunc
    # instmod_docf
    instmod_err = False
    if inst_models is None or isinstance(inst_models, Instrument_Model):
        multi_instmodl = False
        if inst_models is None:
            instmod_docf = inst_models
        else:
            instmod_docf = inst_models.full_name
    elif isinstance(inst_models, list):
        if isinstance(inst_models[0], Instrument_Model):
            multi_instmodl = True
            instmod_docf = []
            for instmod in inst_models:
                if instmod is None:
                    instmod_docf.append(instmod)
                else:
                    instmod_docf.append(instmod.full_name)
        else:
            instmod_err = True
    else:
        instmod_err = True
    if instmod_err:
        raise ValueError("inst_models should be None, string or list of strings.")

    # Check the content of datasets: If not provided or string set multi_dataset
    # to False, otherwise to True.  And set the datasets argument for the Datasim_DocFunc dtsts_docf
    dataset_err = False
    if datasets is None or isinstance(datasets, Dataset):
        multi_dataset = False
        if datasets is None:
            dtsts_docf = datasets
        else:
            dtsts_docf = datasets.dataset_name
    elif isinstance(datasets, list):
        if isinstance(datasets[0], Dataset):
            multi_dataset = True
            dtsts_docf = []
            for dtst in datasets:
                if dtst is None:
                    dtsts_docf.append(dtst)
                else:
                    dtsts_docf.append(dtst.dataset_name)
        else:
            dataset_err = True
    else:
        dataset_err = True
    if dataset_err:
        raise ValueError("datasets should be None, string or list of strings.")

    # Produce the list of datasets and list of models (even of 1 element)
    multi = multi_dataset or multi_instmodl
    if multi and (multi_dataset != multi_instmodl):
        if multi_dataset:
            l_dataset = [datasets for instmod in inst_models]
            l_inst_model = inst_models
        else:  # multi_instmodl
            l_inst_model = [inst_models for dtst in datasets]
            l_dataset = datasets
    elif multi:
        l_dataset = datasets
        l_inst_model = inst_models
    else:
        l_dataset = [datasets]
        l_inst_model = [inst_models]

    # Set the inst_model_full_name for the name of the function and the inst_cat input
    # (instcat_docf) for the datasim_docfunc
    if multi:
        inst_model_full_name = "multi"
        instcat_docf = [RV_inst_cat for ii in range(len(l_inst_model))]
    else:
        instcat_docf = RV_inst_cat
        if inst_models is None:
            inst_model_full_name = "woinst"
        else:
            inst_model_full_name = inst_models.full_name

    # text_def_func is a dictionary which will received the text of the datasimulator functions
    # It has several keys for several datasimulator functions:
    #   - "whole" for the whole system with all the planets
    #   - "b", "c", ... ("planet name") for only the contribution of one planet.
    text_def_func = {}

    # param_nb is a dictionary that will keep track of the number of parameter for each
    # function in text_def_func (so the keys are the same).
    param_nb = {}

    # arg_list is a dictionary which will receive the argument list of the datasimulator
    # function in text_def_func (so the keys are the same).
    # The argument list of a function is itself a dictionary (OrderedDict) that get at least two
    # keys:
    #   - "param": list of the free parameters name in order
    #   - "kwargs": list of the additional argument taht you need to provide to simulate the
    #               data. For example the time
    arg_list = {}

    # Initialise the template function text
    function_name = ("RVsim_{{object}}_{instmod_fullname}"
                     "".format(instmod_fullname=inst_model_full_name))
    template_function = """
    def {function_name}({{arguments}}):
    {{tab}}{{preambule}}
    {{tab}}return {{returns}}
    """.format(function_name=function_name)
    tab = "    "
    template_function = dedent(template_function)

    # Initialise the template for each instmodel
    template_returns_instmod = "{delta_inst_rv} {star_mean_rv} {planets_rv}"

    # Create the arguments text
    if multi_dataset:
        if datasets[0] is None:
            arguments = "p, l_t, l_tref"
        else:
            arguments = "p"
    else:
        if datasets is None:
            arguments = "p, t, tref"
        else:
            arguments = "p"

    # Initialise arg_list and param_nb for key "whole"
    arg_list[key_whole] = OrderedDict()
    arg_list[key_whole]["param"] = []
    arg_list[key_whole]["kwargs"] = []
    param_nb[key_whole] = 0

    # Add time in the kwargs entry of the whole system arg_list
    if datasets is None:
        if multi_instmodl:
            arg_list[key_whole]["kwargs"].append("l_t")
        else:
            arg_list[key_whole]["kwargs"].append("t")

    # Create for the instrument Delta RV (delta_inst_rv)
    l_delta_inst_rv = []
    l_star_mean_rv = []
    for ii, instmdl, dst in zip(range(len(l_inst_model)), l_inst_model, l_dataset):
        l_delta_inst_rv.append("")
        if instmdl is not None:
            inst_name = instmdl.instrument.name
            ## RVrefglobal_inst: name of the instrument chosen as global RV reference
            ## (eg: HARPS)
            RVrefglobal_instname = RV_globalref_instname
            ## RVref4inst_modname: name of the instrument model chosen as reference for the
            ## current instrument (eg: default)
            RVref4inst_modname = RV_instref_modnames[inst_name]
            # Add the Delta_RV of the global RV reference instrument model if needed
            if inst_name != RVrefglobal_instname:
                instmod_RVref4inst = RV_inst_db[inst_name][RVref4inst_modname]
                if instmod_RVref4inst.DeltaRV.main:
                    if instmod_RVref4inst.DeltaRV.free:
                        l_delta_inst_rv[ii] += "p[{}] + ".format(param_nb[key_whole])
                        param_nb[key_whole] += 1
                        arg_list[key_whole]["param"].append(instmod_RVref4inst.DeltaRV.full_name)
                    else:
                        l_delta_inst_rv[ii] += "{} + ".format(instmod_RVref4inst.DeltaRV.value)
            # Add the Delta_RV of the model used as RV reference for the current instrument
            if instmdl.name != RVref4inst_modname:
                if instmdl.DeltaRV.main:
                    if instmdl.DeltaRV.free:
                        l_delta_inst_rv[ii] += "p[{}] + ".format(param_nb[key_whole])
                        param_nb[key_whole] += 1
                        arg_list[key_whole]["param"].append(instmdl.DeltaRV.full_name)
                    else:
                        l_delta_inst_rv[ii] += "{} + ".format(instmdl.DeltaRV.value)

        # Create the text for the star mean RV (star_mean_rv)
        l_star_mean_rv.append("")
        if star.v0.free:
            l_star_mean_rv[ii] += "p[{}]".format(param_nb[key_whole])
            param_nb[key_whole] += 1
            arg_list[key_whole]["param"].append(star.v0.full_name)
        else:
            l_star_mean_rv[ii] += "{}".format(star.v0.value)
        if star.with_RVdrift:
            for order in range(1, star.RVdrift_order + 1):
                RVdrift_param_name = star.get_RVdrift_param_name(order)
                RVdrift_param_fullname = star.parameters[RVdrift_param_name].full_name
                if star.parameters[RVdrift_param_name].main:
                    value_not0 = True
                    if star.parameters[RVdrift_param_name].free:
                        l_star_mean_rv[ii] += "+ p[{}]".format(param_nb[key_whole])
                        param_nb[key_whole] += 1
                        arg_list[key_whole]["param"].append(RVdrift_param_fullname)
                    else:
                        if star.parameters[RVdrift_param_name].value != 0.0:
                            l_star_mean_rv[ii] += "+ {}".format(star.
                                                                parameters[RVdrift_param_name].
                                                                value)
                        else:
                            value_not0 = False
                    if value_not0:
                        if ((("tref" not in arg_list[key_whole]["kwargs"]) or
                             ("tref" not in arg_list[key_whole]["kwargs"])) and
                           (dst is None)):
                            if multi_instmodl:
                                arg_list[key_whole]["kwargs"].append("l_tref")
                            else:
                                arg_list[key_whole]["kwargs"].append("tref")
                        if order == 1:
                            if multi_instmodl:
                                l_star_mean_rv[ii] += (" * (l_t[{ii}] - l_tref[{ii}]) "
                                                       "".format(ii=ii))
                            else:
                                l_star_mean_rv[ii] += " * (t - tref) "
                        elif order > 1:
                            if multi_instmodl:
                                l_star_mean_rv[ii] += (" * (l_t[{ii}] - l_tref[{ii}])**{order} "
                                                       "".format(order=order, ii=ii))
                            else:
                                l_star_mean_rv[ii] += (" * (t - tref)**{order}"
                                                       "".format(order=order))

    # Save the param_nb and arg_list for the whole function before iterating over the planets
    # text_def_func_before = text_def_func[self.key_whole]
    param_nb_before = param_nb[key_whole]
    arg_list_before = deepcopy(arg_list[key_whole])

    # Iterate over the planets to create the preambules (preambule_planet and preambule_whole),
    # the planets RV contribution (planet_rv and whole_planets_rv) and finalise the text of
    # planets functions.
    template_preambule = """
    {tab}ecc_{planet} = getecc_fast({secosw}, {sesinw})
    {tab}omega_{planet} = getomega_fast({secosw}, {sesinw})
    {tab}tp_{planet} = gettp_fast({P}, {tc}, ecc_{planet}, omega_{planet})
    """
    if multi_instmodl:
        template_planet_rv = ("+ pl_rv_array(l_t[{ii}], 0., {K}, omega_{planet}, "
                              "ecc_{planet}, tp_{planet}, {P})")
    else:
        template_planet_rv = ("+ pl_rv_array(t, 0., {K}, omega_{planet}, "
                              "ecc_{planet}, tp_{planet}, {P})")

    # Initialise the local dictionary for the creation of the datasim functions by exec
    ldict = locals().copy()
    if datasets is not None:
        if multi_instmodl:
            l_t = []
            l_tref = []
            for instmdl, dst in zip(l_inst_model, l_dataset):
                    l_t.append(dst.get_time())
                    l_tref.append(dst.get_tref())
            ldict["l_t"] = l_t
            ldict["l_tref"] = l_tref
        else:
            ldict["t"] = datasets.get_time()
            ldict["tref"] = datasets.get_tref()

    # Initialise the text for the whole system preambule
    preambule_whole = ""
    l_whole_planets_rv = []
    for instmdl in l_inst_model:
        l_whole_planets_rv.append("")
    for i, planet in enumerate(planets.values()):
        # Initialise arg_list and param_nb for the current planet
        arg_list[planet.name] = deepcopy(arg_list_before)
        param_nb[planet.name] = param_nb_before

        # Create two dictionaries which will contain the text for each planet parameter for the
        # current planet and for the whole system.
        params_planet = {}
        params_whole = {}
        # Create the text for each planet parameter for the current planet and for the whole
        # system.
        for param_name, param in zip(["K", "secosw", "sesinw", "tc", "P"],
                                     [planet.K, planet.secosw, planet.sesinw, planet.tc,
                                      planet.P]):
            if param.free:
                param_text = "p[{}]"
                params_whole[param_name] = param_text.format(param_nb[key_whole])
                param_nb[key_whole] += 1
                arg_list[key_whole]["param"].append(param.full_name)
                params_planet[param_name] = param_text.format(param_nb[planet.name])
                param_nb[planet.name] += 1
                arg_list[planet.name]["param"].append(param.full_name)
            else:
                params_whole[param_name] = "{}".format(param.value)
                params_planet[param_name] = params_whole[param_name]

        # Create the preambule text that compute intermediate variables
        preambule_planet = (dedent(template_preambule).
                            format(planet=planet.name, secosw=params_planet["secosw"],
                                   sesinw=params_planet["sesinw"], P=params_planet["P"],
                                   tc=params_planet["tc"], tab=tab))
        preambule_whole += (dedent(template_preambule).
                            format(planet=planet.name, secosw=params_whole["secosw"],
                                   sesinw=params_whole["sesinw"], P=params_whole["P"],
                                   tc=params_whole["tc"], tab=tab))

        # planets RV contribution (planet_rv and whole_planets_rv)
        l_planet_rv = []
        if multi_instmodl:
            for ii, instmdl in enumerate(l_inst_model):
                l_planet_rv.append(template_planet_rv.format(ii=ii,
                                                             planet=planet.name,
                                                             K=params_planet["K"],
                                                             P=params_planet["P"]))
                l_whole_planets_rv[ii] += template_planet_rv.format(ii=ii,
                                                                    planet=planet.name,
                                                                    K=params_whole["K"],
                                                                    P=params_whole["P"])
        else:
            l_planet_rv.append(template_planet_rv.format(planet=planet.name,
                                                         K=params_whole["K"],
                                                         P=params_whole["P"]))
            l_whole_planets_rv[ii] += template_planet_rv.format(planet=planet.name,
                                                                K=params_whole["K"],
                                                                P=params_whole["P"])

        # Fill returns text for each planet
        returns_pl = ""
        for delta_inst_rv, planet_rv, star_mean_rv in zip(l_delta_inst_rv,
                                                          l_planet_rv,
                                                          l_star_mean_rv):
            returns_pl += template_returns_instmod.format(delta_inst_rv=delta_inst_rv,
                                                          star_mean_rv=star_mean_rv,
                                                          planets_rv=planet_rv)
            returns_pl += ", "
        returns_pl = returns_pl[:-2]

        # Finalise the text of planet RV simulator function
        text_def_func[planet.name] = (template_function.
                                      format(object=planet.name, preambule=preambule_planet,
                                             arguments=arguments, returns=returns_pl,
                                             tab=tab))
        logger.debug("text of {object} RV simulator function :\n{text_func}"
                     "".format(object=planet.name, text_func=text_def_func[planet.name]))

    # Fill returns text for the whole system
    returns_whole = ""
    for delta_inst_rv, whole_planet_rv, star_mean_rv in zip(l_delta_inst_rv,
                                                            l_whole_planets_rv,
                                                            l_star_mean_rv):
        returns_whole += template_returns_instmod.format(delta_inst_rv=delta_inst_rv,
                                                         star_mean_rv=star_mean_rv,
                                                         planets_rv=whole_planet_rv)
        returns_whole += ", "
    returns_whole = returns_whole[:-2]

    # Finalise the  text of whole system RV simulator function
    text_def_func[key_whole] = (template_function.format(object=key_whole,
                                                         preambule=preambule_whole,
                                                         arguments=arguments, returns=returns_whole,
                                                         tab=tab))
    logger.debug("text of {object} RV simulator function :\n{text_func}"
                 "".format(object=key_whole, text_func=text_def_func[key_whole]))

    # Create and fill the output dictionnary containing the datasimulators functions.
    dico_docf = dict.fromkeys(text_def_func.keys(), None)
    for obj_key in dico_docf:
        ldict["getecc_fast"] = getecc_fast
        ldict["getomega_fast"] = getomega_fast
        ldict["gettp_fast"] = gettp_fast
        ldict["pl_rv_array"] = pl_rv_array
        exec(text_def_func[obj_key], ldict)
        params_model = arg_list[obj_key]["param"]
        if len(arg_list[obj_key]["kwargs"]) > 0:
            dataset_kwargs = str(arg_list[obj_key]["kwargs"])
        else:
            dataset_kwargs = None
        dico_docf[obj_key] = DatasimDocFunc(function=ldict[function_name.format(object=obj_key)],
                                            params_model=params_model,
                                            inst_cat=instcat_docf,
                                            dataset_kwargs=dataset_kwargs,
                                            inst_model_fullname=instmod_docf,
                                            dataset=dtsts_docf)
    return dico_docf
