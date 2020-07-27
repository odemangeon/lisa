#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
datasimulator module.

The objective of this module is to define the class DatasimulatorCreator and provide tools to create
your datasimulator.

@TODO:
    - implement boolean argument used_instmodel_only in create_datasimulators
"""
from logging import getLogger
from collections import defaultdict

from .datasim_docfunc import DatasimDocFunc
from ..database_instlevelsanddataset import DatabaseInstLvlDataset
from ....tools.function_from_text_toolbox import key_param, key_mand_kwargs, key_opt_kwargs


## logger object
logger = getLogger()

## Root of all the function for the creation of datasimulators
root_name_func_datsim = "_create_datasimulator"

## Key for the whole


class DatasimulatorCreator(object):
    """DatasimulatorCreator is an Interface class for Core_Model.

    It provides methods to create datasimulator functions for a model.
    """

    key_param = key_param
    key_mand_kwargs = key_mand_kwargs
    key_opt_kwargs = key_opt_kwargs

    def _create_datasimulator(self, instmod_obj, dataset=None):
        """Return the datasimulator for a given instrument model.

        Arguments
        ---------
        instmod_obj : Instrument_Model
            Instrument_Model instance.
        dataset     : Dataset/None
            If provided the output datasimulator will simulate the data of
            the provided dataset. The function will include the dataset kwargs (like time or t_ref).

        Returns
        -------
        datasim_docfunc : DatasimDocFunc
        """
        # Get the instrument category of the instrument model which will allow to get the correct
        # datasimulator creator function.
        inst_cat = instmod_obj.instrument.category
        return self.get_datasimcreator(inst_cat)(instmod_obj, dataset)  # self.get_datasimcreator is defined in Core_Model

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
            inst_model = instmod_obj.get_name()
            inst_name = instmod_obj.instrument.get_name()
            inst_fullcat = instmod_obj.instrument.full_category
            # ... create and store the datasimulator docfuncs in the database
            db[inst_fullcat][inst_name][inst_model] = self._create_datasimulator(instmod_obj)
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
            instmod_obj = self.get_instmod(dataset_name=dataset_name)
            # ... create and store the datasimulator
            db[dataset_name] = self._create_datasimulator(instmod_obj, dataset)[self.key_whole]
        return db

    def __datasim_multipledatasets_creator(self, l_datasim, l_datasim_has_multi_output, l_params_idx, params_model, mand_kwargs, opt_kwargs,
                                           inst_fullcat, inst_model_fullname=None, dataset=None):
        """Return the datasimulator for all datasets

        WARNING/TODO eventually: For now *args, **kwargs of the datasim_alldatasets are passed to all the datasim function.
        This might not be always desired.

        Arguments
        ---------
        l_datasim           : List of DatasimDocFunc
            list of datasimulators
        l_params_idx        : List of list of int
            List of list of indexes in the param array for each datasim function in l_datasim.
        params_model        : List of string
            Ordered list of parameters full name for the datasimulator being created
        mand_kwargs         : String
            String giving the mandatory keyword arguments for the datasimulator being created
        opt_kwargs          : String
            String giving the optional keyword arguments along with their default values
        inst_fullcat        : String or List of string or None
            Gives instrument full categories of the instrument models used
        inst_model_fullname : String or List of string
            Gives the full name of the instrument models used
        dataset             : String or list of string or None
            Gives the names of the datasets simulated

        Returns
        -------
        datasim_multipledatasets: DatasimDocFunc
            Datasimulator for all datasets
        """
        def datasim_multipledatasets(p, *args, **kwargs):
            l_res = []
            for datasim, multi_output, idxs in zip(l_datasim, l_datasim_has_multi_output, l_params_idx):
                if multi_output:
                    l_res.extend(datasim(p[idxs], *args, **kwargs))
                else:
                    l_res.append(datasim(p[idxs], *args, **kwargs))
            return l_res

        return DatasimDocFunc(function=datasim_multipledatasets,
                              params_model=params_model,
                              inst_cat=inst_fullcat,
                              mand_kwargs=mand_kwargs,
                              opt_kwargs=opt_kwargs,
                              include_dataset_kwarg=l_datasim[0].include_dataset_kwarg,
                              inst_model_fullname=inst_model_fullname,
                              dataset=dataset)

    def create_datasimulator_alldatasets(self, dataset_db):
        """Return one datasim docfunction that simulates all the datasets at the same time.

        :param DatasetDatabase dataset_db: Database with all the datasets
        :return DocFunction docfunc: Function that simulates all the datasets in dataset_db at the
            same time with the datasets included.
        """
        l_dataset_obj = dataset_db.get_datasets()
        return self.create_datasimulator_4_ldataset(l_dataset_obj=l_dataset_obj)[self.key_whole]

    def create_datasimulator_4_ldataset(self, l_dataset_obj):
        """Return one datasim docfunction that simulates all the datasets provided.

        Arguments
        ---------
        l_dataset_obj : List of Dataset

        Returns
        -------
        dico_datastim : Dictionary of DocFunction
            Function that simulates all the datasets provided for each part of the object studied
        """
        # Initialise the dictionary datsimC_inputs:
        #   key = datasimcreator_name,
        #   value = dict :
        #               key: "datasets" and "instmodels"
        #               value: list of datasets and list of corresponding intrument model object
        def defdictfunc():
            return {"datasets": [], "instmodels": []}
        datsimC_inputs = defaultdict(defdictfunc)

        # For each dataset, ...
        for dataset_obj_ii in l_dataset_obj:
            # ... get the associated instrument category, instrument model object and datasimcreator
            # name
            inst_cat = dataset_obj_ii.instrument.category
            datsimC_name = self.get_datasimcreatorname(inst_cat)
            instmod_obj_ii = self.get_instmod(dataset_obj_ii.dataset_name)  # Define in Instmodel4DatasetAttr
            # ... store the dataset and instrument model object in datsimC_inputs
            datsimC_inputs[datsimC_name]["datasets"].append(dataset_obj_ii)
            datsimC_inputs[datsimC_name]["instmodels"].append(instmod_obj_ii)

        datsimC_inputs
        # Initialise the list of Datasim list of DatasimDocFunc
        l_datsim = defaultdict(list)
        l_datsim_has_multi_output = defaultdict(list)
        l_params = defaultdict(list)
        l_allparams = defaultdict(list)
        l_allmand_kwargs = defaultdict(list)
        l_allopt_kwargs = defaultdict(list)
        l_params_idx = defaultdict(list)
        inst_fullcats = defaultdict(list)
        inst_model_fullnames = defaultdict(list)
        datasets = defaultdict(list)

        # output dictionary of DatasimDocFunc
        dico_datasim_4_obj = {}

        # For each datasimcreator creator name, ...
        for datsimC_name in datsimC_inputs:
            # ... create the datasim function with all the datasets using this datasimcreator
            dico_datasim_output = self.datasimcreator[datsimC_name](datsimC_inputs[datsimC_name]["instmodels"],
                                                                    datsimC_inputs[datsimC_name]["datasets"])
            for key_obj in dico_datasim_output:
                l_datsim[key_obj].append(dico_datasim_output[key_obj])
                l_datsim_has_multi_output[key_obj].append(dico_datasim_output[key_obj].multi_output)
                # ... get the ordered list of instrument categories for this function
                inst_fullcats[key_obj] = inst_fullcats[key_obj] + list(l_datsim[key_obj][-1].inst_cat)
                # ... get the ordered list of instrument model full names for this function
                inst_model_fullnames[key_obj] = (inst_model_fullnames[key_obj] +
                                                 list(l_datsim[key_obj][-1].instmodel_fullname))
                # ... get the ordered list of dataset names for this function
                datasets[key_obj] = datasets[key_obj] + list(l_datsim[key_obj][-1].dataset)
                # ... create the list of indexes for the function parameters and the list of all the
                # model parameter for the all datasets function
                idx_par = []
                # For each parameter in the list of this function, ...
                l_params[key_obj].append(l_datsim[key_obj][-1].params_model)
                # WARNING/TODO: This two lines are a quick and very dirty way to pass the mand and opt kwargs to the __datasim_alldatasets_creator
                # and after the DatasimDocFunc init because if several functions use the same kwargs, it will then appear several times
                l_allmand_kwargs[key_obj].append(l_datsim[key_obj][-1].mand_kwargs_list)
                l_allopt_kwargs[key_obj].append(l_datsim[key_obj][-1].opt_kwargs_list)
                for par in l_datsim[key_obj][-1].params_model:
                    # ... if the param is not in the list of all parameters already, add it
                    if par not in l_allparams[key_obj]:
                        l_allparams[key_obj].append(par)
                    # ... get the index of this parameter in the list of all the parameters
                    idx_par.append(l_allparams[key_obj].index(par))
                l_params_idx[key_obj].append(idx_par)

        for key_obj in l_datsim.keys():
            logger.debug(f"Creation of datasimulator for the folling list of datasets {[dataset_obj_ii.dataset_name for dataset_obj_ii in l_dataset_obj]} and for object {key_obj}.\nList of parameters names:\n{l_allparams[key_obj]}\n"
                         f"Input for the creation of the individual datasimulators:\n{datsimC_inputs}\n"
                         f"List of datasim functions obtained: {l_datsim[key_obj]}\n"
                         f"List of datasim has multi_output obtained: {l_datsim_has_multi_output[key_obj]}\n"
                         f"List of parameter names for each individual datasimulator:\n{l_params[key_obj]}\n"
                         f"List of param indexes for each individual datasimulator:\n{l_params_idx[key_obj]}\n"
                         f"List of instrument categories: {inst_fullcats[key_obj]}\n"
                         f"List of instrument instrument model full names: {inst_model_fullnames[key_obj]}\n"
                         f"List of datasets: {datasets[key_obj]}")

        # Create the datasim
            dico_datasim_4_obj[key_obj] = self.__datasim_multipledatasets_creator(l_datasim=l_datsim[key_obj],
                                                                                  l_datasim_has_multi_output=l_datsim_has_multi_output[key_obj],
                                                                                  l_params_idx=l_params_idx[key_obj],
                                                                                  params_model=l_allparams[key_obj], mand_kwargs=str(l_allmand_kwargs[key_obj]), opt_kwargs=str(l_allopt_kwargs[key_obj]),
                                                                                  inst_fullcat=inst_fullcats[key_obj],
                                                                                  inst_model_fullname=inst_model_fullnames[key_obj], dataset=datasets[key_obj])

        return dico_datasim_4_obj
