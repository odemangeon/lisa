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
from ..dataset_and_instrument.dataset import Dataset


def check_datasets_and_instmodels(datasets, inst_models):
    """Check the content of datasets and inst_models argument for the datasim creator functions.

    Set the inst_model_fullnames argument for the Datasim_DocFunc (instmod_docf).
    Set the dataset_names argument for the Datasim_DocFunc (dtsts_docf).

    :param list_of_Dataset/Dataset/None datasets: instance of Dataset
        or list of Dataset instances or None
    :param list_of_Instrument_Model/Instrument_Model/None inst_models: instance of Instrument_Model
        or list of Instrument_Model instances or None
    :return list_of_Dataset l_dataset: Checked list of Dataset instance(s).
    :return list_of_Dataset l_inst_model: Checked list of Instrument_Model instance(s).
    :return bool multi: True if the datasim function needs multiple outputs.
    :return string inst_model_full_name: Instrument model full name for the name of the
        datasimulator function
    :return list_of_string instcat_docf: List of instrument categories corresponding to the list of
        instrument model (l_inst_model).
    :return list_of_string/string/None dtsts_docf: Dataset name, or list of
        dataset names or None, matching datasets.
    :return list_of_string/string/None instmod_docf: Instrument Model full name, or list of
        Instrument Model full names or None, matching inst_models.
    """
    # Check the content of datasets argument for the datasim creator functions.
    # Set multi_dataset to True if several datasets are provided, to False otherwise.
    # Finally set the dataset_names argument for the Datasim_DocFunc (dtsts_docf).
    instmod_err = False
    if inst_models is None or isinstance(inst_models, Instrument_Model):
        multi_instmodl = False
        if inst_models is None:
            instmod_docf = inst_models
        else:
            instmod_docf = inst_models.get_name(include_prefix=True, recursive=True)
    elif isinstance(inst_models, Iterable):
        if isinstance(inst_models[0], Instrument_Model):
            multi_instmodl = True
            instmod_docf = []
            for instmod in inst_models:
                if instmod is None:
                    instmod_docf.append(instmod)
                else:
                    instmod_docf.append(instmod.get_name(include_prefix=True, recursive=True))
        else:
            instmod_err = True
    else:
        instmod_err = True
    if instmod_err:
        raise ValueError("inst_models should be None, string or list of strings.")

    # Check the content of datasets argument: Set multi_dataset to True if several datasets
    # are provided, to False otherwise. Finally set the datasets argument for the
    # Datasim_DocFunc (dtsts_docf)
    dataset_err = False
    if datasets is None or isinstance(datasets, Dataset):
        multi_dataset = False
        if datasets is None:
            dtsts_docf = datasets
        else:
            dtsts_docf = datasets.dataset_name
    elif isinstance(datasets, Iterable):
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

    # Produce the list of instrument categories corresponding to l_inst_model for the datasim
    # docfunction
    instcat_docf = [instmdl.instrument.category for instmdl in l_inst_model]

    # Produce the inst_model_full_name value for the name of the datasimulator function
    if multi:
        inst_model_full_name = "multi"
    else:
        if inst_models is None:
            inst_model_full_name = "woinst"
        else:
            inst_model_full_name = inst_models.get_name(include_prefix=True, recursive=True)

    return (l_dataset, l_inst_model, multi, inst_model_full_name, instcat_docf, instmod_docf,
            dtsts_docf)


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


def get_has_datasets(l_dataset):
    """Return True if datasets provides Dataset(s).

    This function should be called after check_datasets_and_instmodels since it uses its output.

    :param list_of_Dataset l_dataset: Checked list of Dataset instance(s) or None.
    :return bool res: True if datasets provides Dataset(s).
    """
    return l_dataset[0] is not None
