#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
datasimulator module.

The objective of this module is to define the class DatasimulatorCreator.

@DONE:
    -

@TODO:
    - implement boolean argument used_instmodel_only in create_datasimulators
"""
from logging import getLogger

from ..database_instlevelsanddataset import DatabaseInstLvlDataset
from ....tools.miscellaneous import interpret_data_filename


## logger object
logger = getLogger()

## Root of all the function for the creation of datasimulators
root_name_func_datsim = "_create_datasimulator"


class DatasimulatorCreator(object):
    """docstring for DatasimulatorCreator."""

    def _create_datasimulator(self, instmod_obj, dataset=None):
        """Return the datasimulator for a given instrument model."""
        inst_cat = instmod_obj.instrument.category
        # create_datasim_func = getattr(self, root_name_func_datsim + "_" + inst_cat)
        return self.get_datasimcreator(inst_cat)(instmod_obj, dataset)

    def create_datasimulators(self, affectinstmodel4dataset=False, lock_db=False):
        """Return the datasimulator for each instrument model used."""
        if affectinstmodel4dataset:
            instmodel4dataset = self.instmodel4dataset.copy()
        else:
            instmodel4dataset = None
        db = DatabaseInstLvlDataset(object_stored="datasimulator", database_name=self.object_name,
                                    instmodel4dataset=instmodel4dataset, ordered=False)
        db.database_unlock()
        # Get the list of used instrument model
        for instmod_obj in self.get_instmodels_used():
            inst_model = instmod_obj.name
            inst_name = instmod_obj.instrument.name
            inst_cat = instmod_obj.instrument.category
            db[inst_cat][inst_name][inst_model] = self._create_datasimulator(instmod_obj)
            # print(list(db[inst_cat][inst_name][inst_model].keys()))
        if lock_db:
            db.lock()
        return db

    def create_datasimulators_perdataset(self, datasim_db, dataset_db, instmodel4dataset):
        """Create the datasimulator function for each dataset."""
        db = {}
        for dataset_name in instmodel4dataset:
            # instmod_fullname = instmodel4dataset.get_instmod_fullname(dataset_name=dataset_name)
            fileinfo = interpret_data_filename(dataset_name)
            inst_cat = fileinfo["inst_category"]
            inst_name = fileinfo["inst_name"]
            number = fileinfo["number"]
            dataset = dataset_db[inst_cat][inst_name][number]
            db[dataset_name] = {}
            instmod_obj = self.get_instmod(dataset_name)
            # for obj in datasim_db[instmod_fullname]:
            #     instmod_obj = self.get_instmod(dataset_name)
            #     # datasim_func = datasim_db[instmod_fullname][obj]
            #     # db[dataset_name][obj] = dataset.create_datasimulator_for_dataset(datasim_func)
            db[dataset_name] = self._create_datasimulator(instmod_obj, dataset)["whole"]
        return db

    def create_datasimulator_alldatasets(self, datasim_dbf, inser):
        """Create a function that gather the datasimulators for all the datasets."""
