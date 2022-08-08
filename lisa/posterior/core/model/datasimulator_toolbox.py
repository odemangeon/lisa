#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
datasimulator creator toolbox module.

The objective of this module is to provide functions to ease the development of datasimulator
creator function.
@DONE:
    -

@TODO:
    -
"""
from collections import defaultdict, Iterable

from ..dataset_and_instrument.instrument import Instrument_Model
from ..dataset_and_instrument.dataset import Core_Dataset


def check_datasets_and_instmodels(datasets, inst_models):
    """Check the content of datasets and inst_models argument for the datasim creator functions.

    Set the inst_model_fullnames argument for the Datasim_DocFunc (instmod_docf).
    Set the dataset_names argument for the Datasim_DocFunc (dtsts_docf).

    Arguments
    ---------
    datasets    :   list_of_Dataset/Dataset
        instance of Dataset or list of Dataset instances
    inst_models : list_of_Instrument_Model/Instrument_Model
        instance of Instrument_Model or list of Instrument_Model

    Returns
    -------
    l_dataset               : list_of_Dataset
        Checked list of Dataset instance(s).
    l_inst_model            : list_of_Instrument_Model
        Checked list of Instrument_Model instance(s).
    multi                   : bool
        True if the datasim function needs multiple outputs.
    inst_model_full_name    : string
        Instrument model full name for the name of the datasimulator function
    dst_ext                 : string
        String giving the dataset number that will be used as an extension for the name of the datasimulator function
    instcat_docf            : list_of_string
        List of instrument categories corresponding to the list of instrument model (l_inst_model).
    dtsts_docf              : list_of_string/string
        Dataset name, or list of dataset names or None, matching datasets.
    instmod_docf            : list_of_string/string/None
        Instrument Model full name, or list of Instrument Model full names or None, matching inst_models.
    """
    # Check the content of inst_models and datasets argument for the datasim creator functions.
    # Set multi_input for each of these to True if several instances are provided or to False otherwise.
    # Finally set the inputsname4docf for each of these two to list the names of the instances
    # for the Datasim_DocFunc (dtsts_docf).

    # This dictionnary will be filled with two keys "datasets", "inst_models" and the Value
    # will be a boolean state is this inputs has multiple instances or just one
    multi_input = {}

    # This dictionnary will be filled with two keys "datasets", "inst_models" and the Value
    # will be a the name or the list of name of these inputs to be used in the datasimulator docfunc
    inputsname4docf = {}
    for inputs, input_class, input_type in zip([datasets, inst_models], [Core_Dataset, Instrument_Model], ["datasets", "inst_models"]):
        inputs_err = False
        if isinstance(inputs, Iterable):
            if all([isinstance(input, input_class) for input in inputs]):
                if len(inputs) > 1:
                    multi_input[input_type] = True
                else:
                    multi_input[input_type] = False
                    # In practice, it's just one so for the datasim docfunc it is better to make is a non multi
                    if input_type == "datasets":
                        datasets = datasets[0]
                    else:
                        inst_models = inst_models[0]
            else:
                inputs_err = True
        else:
            inputs_err = not(isinstance(inputs, input_class))
            multi_input[input_type] = False
        if inputs_err:
            raise ValueError(f"{input_type} should be an instance of {input_class} or a list of isntances of {input_class}.")
        if multi_input[input_type]:
            inputsname4docf[input_type] = []
            for input in inputs:
                input_name = input.full_name if input_type == "inst_models" else input.dataset_name
                inputsname4docf[input_type].append(input_name)  # instmod.get_name(include_prefix=True, recursive=True)
        else:
            inputsname4docf[input_type] = inst_models.full_name if input_type == "inst_models" else datasets.dataset_name  # inst_models.get_name(include_prefix=True, recursive=True)

    # Produce l_dataset and l_inst_model the list of datasets and list of instrument models (even of 1 element)
    multi = multi_input["datasets"] or multi_input["inst_models"]
    both_multi = multi and (multi_input["datasets"] == multi_input["inst_models"])
    if multi and not(both_multi):
        if (multi_input["datasets"]):
            l_inst_model = [inst_models for dtst in datasets]
            l_dataset = datasets
        else:  # multi_instmodl
            l_dataset = [datasets for instmod in inst_models]
            l_inst_model = inst_models
    elif multi:
        l_dataset = datasets
        l_inst_model = inst_models
    else:
        l_dataset = [datasets]
        l_inst_model = [inst_models]

    # Produce the list of instrument categories corresponding to l_inst_model for the datasim
    # docfunction
    instcat_docf = [instmdl.instrument.category for instmdl in l_inst_model]

    # Produce the inst_model_full_name value for the name of the datasimulator function
    if multi:
        inst_model_full_name = "multi"
        dst_ext = ""
    else:
        inst_model_full_name = inst_models.get_name(include_prefix=True, recursive=True, code_version=True)
        dst_ext = f"_dst{datasets.number}"

    return (l_dataset, l_inst_model, multi, inst_model_full_name, dst_ext, instcat_docf, inputsname4docf["inst_models"],
            inputsname4docf["datasets"])


def __dico_instcat_values_creator():
    return {"l_dataset": [], "l_inst_model": [], "l_index": [], "has": False}


def get_lists_bijection_instcat(l_dataset, l_inst_model, inst_cat=None):
    """Get the list of datasets and the list of instrument models per instrument category.

    This function should be called after check_datasets_and_instmodels since it uses its outputs.

    :param list_of_Dataset l_dataset: list of Dataset instances associated to the Instrument_Model
        instances and instrument categories in l_inst_model and l_inst_cat.
    :param list_of_Instrument_Model l_inst_model: list of Instrument_Model instances associated to
        the Dataset instances and instrument categories in l_dataset and l_inst_cat.
    :param str/list_of_str inst_cat: Intrument category(ies) for which you want the list of Datasets
        and Instrument_Model. If None, we consider that you are interested in all the instrument
        categories.
    :return dict_of_dict_of_lists dico_instcat: dictionary with keys = instrument category of
        interest (specified by inst_cat), values = dictionary with two keys which contain a list:
            "l_dataset" = list of Dataset instance for this instrument category
            "l_inst_model" = list of Dataset instance for this instrument category
            "l_index" = List of indexed in the l_dataset/l_inst_model
            "has" = Boolean indicating if the instrument category used in l_dataset/l_inst_model

    :return list_of_dict l_output_retrieve: list of dictionary giving the information necessary
        to go back to the original l_dataset/l_inst_model from dico_instcat.
            "inst_cat" = string giving the instrument category
            "index" = giving the index in the list related to this instrument category
    """
    # Check the inst_cat parameter
    err = False
    if inst_cat is None:
        l_inst_cat_res = []
    elif isinstance(inst_cat, str):
        l_inst_cat_res = [inst_cat]
    elif isinstance(inst_cat, Iterable):
        if isinstance(inst_cat[0], str):
            l_inst_cat_res = inst_cat
        else:
            err = True
    else:
        err = True
    if err:
        raise ValueError("inst_cat argument should be None, str, or Iterable of str")

    # Construct and fill the output dictionaries res_lists
    dico_instcat = defaultdict(__dico_instcat_values_creator)
    l_output_retrieve = []
    for ii, inst_mod in enumerate(l_inst_model):
        cat = inst_mod.instrument.category
        if (cat in l_inst_cat_res) or (inst_cat is None):
            idx_in_l_cat = len(dico_instcat[cat]["l_dataset"])
            dico_instcat[cat]["l_dataset"].append(l_dataset[ii])
            dico_instcat[cat]["l_inst_model"].append(l_inst_model[ii])
            dico_instcat[cat]["l_index"].append(ii)
            dico_instcat[cat]["has"] = True
            l_output_retrieve.append({"inst_cat": cat, "index": idx_in_l_cat})
    return dico_instcat, l_output_retrieve


# def get_has_datasets(l_dataset):
#     """Return True if datasets provides Dataset(s).
#
#     This function should be called after check_datasets_and_instmodels since it uses its output.
#
#     :param list_of_Dataset l_dataset: Checked list of Dataset instance(s) or None.
#     :return bool res: True if datasets provides Dataset(s).
#     """
#     return l_dataset[0] is not None
