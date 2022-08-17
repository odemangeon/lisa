#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Datasim creator IND module.
"""
from logging import getLogger

from ..datasimulator_toolbox import check_datasets_and_instmodels
from .. import par_vec_name
from ..datasim_docfunc import DatasimDocFunc
from ..datasimulator_timeseries_toolbox import time_vec, l_time_vec  # , add_time_argument, time_ref
from ... import function_whole_shortname
# from ...dataset_and_instrument.indicator import IND_Instrumenst
from .....tools.function_from_text_toolbox import FunctionBuilder


## Logger object
logger = getLogger()

tab = "    "

template_function_whole_shortname_ind_cat = "{indicator_category}_{function_whole_shortname}"


def create_datasimulator_IND(model_instance, indicator_models, dataset_db, INDcat_model, indicator_category,
                             inst_models, datasets, get_times_from_datasets):
    """Return indicators datasimulator functions.

    A datasimualtor function is created for the whole dataset_database and for each instrument
    model individually.

    Arguments
    ---------
    model_instance          : Star
        Star instance corresponding to the star in the planetary system
    indicator_models        : list_of_Core_Indicator_Model

    dataset_db              : DatasetDatabase
        Dataset database, this will be used by the function to access the dataset for the decorrelation,
        not to access the IND datasets to be simulated.
    INDcat_model            : IND_InstCat_Model
        Instance of the IND_InstCat_Model
    indicator_category      : str
        Indicator category of the instrument models (all instrument models needs to have the same indicator
        category)
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
        If True the times at which the IND model is computed is taken from the datasets.
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

    function_whole_shortname_ind_cat = template_function_whole_shortname_ind_cat.format(indicator_category=indicator_category,
                                                                                        function_whole_shortname=function_whole_shortname)

    func_builder.add_new_function(shortname=function_whole_shortname_ind_cat)
    if multi:
        func_full_name_MultiOrDst_ext = "_multi"
    else:
        func_full_name_MultiOrDst_ext = f"{l_dataset[0].dataset_code_name}"
    func_builder.set_function_fullname(full_name=f"IND_sim_{function_whole_shortname_ind_cat}_{func_full_name_MultiOrDst_ext}", shortname=function_whole_shortname_ind_cat)

    ####################################
    # Produce different indicator models
    ####################################
    d_d_l_components = {}
    for model in indicator_models:
        d_d_l_components.update(model.create_datasimulator(model_instance=model_instance, multi=multi,
                                                           l_inst_model=l_inst_model, l_dataset=l_dataset,
                                                           get_times_from_datasets=get_times_from_datasets,
                                                           tab=tab, time_vec_name=time_vec, l_time_vec_name=l_time_vec,
                                                           INDcat_model=INDcat_model, indicator_category=indicator_category,
                                                           dataset_db=dataset_db,
                                                           function_builder=func_builder, l_function_shortname=[function_whole_shortname_ind_cat, ],
                                                           ext_func_fullname=func_full_name_MultiOrDst_ext
                                                           )
                                )

    #######################################################################
    # Finalise the functions combining different outputs (whole and planet)
    #######################################################################
    # Function of the whole system
    for func_shortname in [function_whole_shortname_ind_cat, ]:
        d_l_components = {}
        for component_name in d_d_l_components.keys():
            if function_whole_shortname_ind_cat in d_d_l_components[component_name]:
                d_l_components[component_name] = d_d_l_components[component_name][function_whole_shortname_ind_cat]
        combine_return_models(l_inst_model=l_inst_model, tab=tab, function_builder=func_builder, function_shortname=func_shortname,
                              d_l_components=d_l_components
                              )

    ###################################
    # Execute the text of all functions
    ###################################
    # Create and fill the output dictionnary containing the datasimulators functions.
    # dico_docf = dict.fromkeys(text_def_func.keys(), None)
    dico_docf = {}
    for func_shortname in func_builder.l_function_shortname:
        # Create the function (if there is a function to create)
        if func_builder.get_body_text(function_shortname=func_shortname) != "":
            logger.debug(f"text of {func_shortname} IND-{indicator_category} simulator function :\n{func_builder.get_full_function_text(shortname=func_shortname)}")
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
            logger.debug(f"Parameters for {func_shortname} IND-{indicator_category} simulator function :\n{dico_param_nb}")
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


def combine_return_models(l_inst_model, tab, function_builder, function_shortname, d_l_components):
    """
    """
    return_text = []
    for i_inputoutput, instmod in enumerate(l_inst_model):
        return_text.append("")

        for component_name, component in d_l_components.items():
            if (component is not None) and (component[i_inputoutput] != ""):
                if return_text[i_inputoutput] == "":
                    pretext = ""
                else:
                    pretext = " + "
                return_text[i_inputoutput] += pretext + component[i_inputoutput]

    if any([return_text_i != "" for return_text_i in return_text]):
        function_builder.add_to_body_text(text=f"{tab}return {', '.join(return_text)}", function_shortname=function_shortname)
