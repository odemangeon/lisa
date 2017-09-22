#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
datasimulator module.

The objective of this module is to define the class DatasimulatorCreator and provide tools to create
your datasimulator.

@DONE:
    -

@TODO:
    - implement boolean argument used_instmodel_only in create_datasimulators
"""
from logging import getLogger
from collections import defaultdict

from .datasim_docfunc import DatasimDocFunc
from ..database_instlevelsanddataset import DatabaseInstLvlDataset
from ..dataset_and_instrument.instrument import Instrument_Model
from ..dataset_and_instrument.dataset import Dataset


## logger object
logger = getLogger()

## Root of all the function for the creation of datasimulators
root_name_func_datsim = "_create_datasimulator"


class DatasimulatorCreator(object):
    """docstring for DatasimulatorCreator."""

    def _create_datasimulator(self, instmod_obj, dataset=None):
        """Return the datasimulator for a given instrument model.

        :param Instrument_Model instmod_obj: Instrument_Model instance.
        :param Dataset/None dataset: If provided the output datasimulator will simulate the data of
            the provided dataset. The function will include the dataset kwargs (like time or t_ref).
        :return datasim:
        """
        # Get the instrument category of the instrument model which will allow to get the correct
        # datasimulator creator function.
        inst_cat = instmod_obj.instrument.category
        return self.get_datasimcreator(inst_cat)(instmod_obj, dataset)

    def create_datasimulators(self, affectinstmodel4dataset=False, lock_db=False):
        """Return a database with the datasim docfuncs for each instrument model used separatly.

        :param bool affectinstmodel4dataset: True if you want to copy the instmodel4dataset of the
            model into the one of the output database.
        :param bool lock_db: True if you want to lock the output database before returning it
        :return DatabaseInstLvlDataset db: Database containing the datasimulator docfuncs for each
            instrument model used. There is several datasim for each instrument model, because there
            might be several components (e.g. several planets) in the object studied. But there is
            always an entry which correspond to the whole object whose key is self.key_whole .
            Structure is: 1st = inst_cat, 2nd = inst_name, 3nd = inst_model, 4st = component
        """
        # Create the result database (DatabaseInstLvlDataset)
        # If affectinstmodel4dataset=True, copy the instmodel4dataset of the model into the one of
        # this database.
        if affectinstmodel4dataset:
            instmodel4dataset = self.instmodel4dataset.copy()
        else:
            instmodel4dataset = None
        db = DatabaseInstLvlDataset(object_stored="datasimulator", database_name=self.object_name,
                                    instmodel4dataset=instmodel4dataset, ordered=False)
        # Unlock the database to be sure that you can modify it
        db.database_unlock()
        # For each instrument model used, ...
        for instmod_obj in self.get_instmodels_used():
            # ... get the inst_cat, inst_name and inst_model_name for the storage in the database
            inst_model = instmod_obj.name
            inst_name = instmod_obj.instrument.name
            inst_cat = instmod_obj.instrument.category
            # ... create and store the datasimulator docfuncs in the database
            db[inst_cat][inst_name][inst_model] = self._create_datasimulator(instmod_obj)
        # If required lock the database
        if lock_db:
            db.lock()
        return db

    def create_datasimulators_perdataset(self, dataset_db):
        """Return a database with the datasim docfunc for each dataset separatly.

        :param DatasetDatabase dataset_db: Database with all the datasets
        :return dict db: Database with the datasim docfunc for each dataset in dataset_db. There is
            only one datasim for each dataset corresponding to the whole object. The dataset are
            included in the functions.
        """
        # Initialise the output database
        db = {}
        # For each dataset, ...
        for dataset in dataset_db.get_datasets():
            dataset_name = dataset.dataset_name
            db[dataset_name] = {}
            # ... get the associated instrument model object
            instmod_obj = self.get_instmod(dataset_name)
            # ... create and store the datasimulator
            db[dataset_name] = self._create_datasimulator(instmod_obj, dataset)[self.key_whole]
        return db

    def __datasim_alldatasets_creator(self, l_datasim, l_params_idx, params_model, inst_cat,
                                      inst_model_fullname=None, dataset=None):
        """Return the datasimulator for a given instrument model.

        :param list_DatasimDocFunc l_datasim: List of DatasimDocFunc
        :parama list_list_int l_params_idx: List of list of indexes in the param array for each
            datasim function in l_datasim.
        :return function datasim_alldatasets: Function that gather al
        """
        def datasim_alldatasets(p):
            l_res = []
            for datasim, idxs in zip(l_datasim, l_params_idx):
                l_res.extend(datasim(p[idxs]))
            return l_res

        return DatasimDocFunc(function=datasim_alldatasets,
                              params_model=params_model,
                              inst_cat=inst_cat,
                              inst_model_fullname=inst_model_fullname,
                              dataset=dataset)

    def create_datasimulator_alldatasets(self, dataset_db):
        """Return one datasim docfunction that simulates all the datasets at the same time.

        :param DatasetDatabase dataset_db: Database with all the datasets
        :return DocFunction docfunc: Function that simulates all the datasets in dataset_db at the
            same time with the datasets included.
        """
        # Initialise the dictionary datsimC_inputs:
        #   key = datasimcreator_name, v
        #   value = dict :
        #               key: "datasets" and "instmodels"
        #               value: list of datasets and list of corresponding intrument model object
        def defdictfunc():
            return {"datasets": [], "instmodels": []}
        datsimC_inputs = defaultdict(defdictfunc)

        # For each dataset, ...
        for dataset in dataset_db.get_datasets():
            # ... get the associated instrument category, instrument model object and datasimcreator
            # name
            inst_cat = dataset.instrument.category
            datsimC_name = self.get_datasimcreatorname(inst_cat)
            instmod_obj = self.get_instmod(dataset.dataset_name)
            # ... store the dataset and instrument model object in datsimC_inputs
            datsimC_inputs[datsimC_name]["datasets"].append(dataset)
            datsimC_inputs[datsimC_name]["instmodels"].append(instmod_obj)

        # Initialise the list of Datasim list of DatasimDocFunc
        l_datsim = []
        l_allparams = []
        l_params_idx = []
        inst_cats = []
        inst_model_fullnames = []
        datasets = []

        # For each datasimcreator creator name, ...
        for datsimC_name in datsimC_inputs:
            # ... create the datasim function with all the datasets using this datasimcreator
            l_datsim.append(self.datasimcreator
                            [datsimC_name](datsimC_inputs[datsimC_name]["instmodels"],
                                           datsimC_inputs[datsimC_name]["datasets"])
                            [self.key_whole])
            # ... get the ordered list of instrument model full names for this function
            inst_cats = inst_cats + list(l_datsim[-1].inst_cat)
            # ... get the ordered list of instrument model full names for this function
            inst_model_fullnames = (inst_model_fullnames +
                                    list(l_datsim[-1].instmodel_fullname))
            # ... get the ordered list of dataset names for this function
            datasets = datasets + list(l_datsim[-1].dataset)
            # ... create the list of indexes for the function parameters and the list of all the
            # model parameter for the all datasets function
            idx_par = []
            # For each parameter in the list of this function, ...
            for par in l_datsim[-1].params_model:
                # ... if the param is not in the list of all parameters already, add it
                if par not in l_allparams:
                    l_allparams.append(par)
                # ... get the index of this parameter in the list of all the parameters
                idx_par.append(l_allparams.index(par))
            l_params_idx.append(idx_par)

        # Create the datasim_alldatasets
        return self.__datasim_alldatasets_creator(l_datasim=l_datsim, l_params_idx=l_params_idx,
                                                  params_model=l_allparams,
                                                  inst_cat=inst_cats,
                                                  inst_model_fullname=inst_model_fullnames,
                                                  dataset=datasets)


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
            inst_model_full_name = inst_models.full_name

    return (l_dataset, l_inst_model, multi, inst_model_full_name, instcat_docf, instmod_docf,
            dtsts_docf)
