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

from ..database_func import DatabaseInstLvlDataset


## logger object
logger = getLogger()

## Root of all the function for the creation of datasimulators
root_name_func_datsim = "_create_datasimulator"


class DatasimulatorCreator(object):
    """docstring for DatasimulatorCreator."""

    def _create_datasimulator(self, instmod_obj):
        """Return the datasimulator for a given instrument model."""
        inst_cat = instmod_obj.instrument.category
        create_datasim_func = getattr(self, root_name_func_datsim + "_" + inst_cat)
        return create_datasim_func(instmod_obj)

    def create_datasimulators(self, affectinstmodel4dataset=False, lock_db=False):
        """Return the datasimulator for each instrument model used."""
        if affectinstmodel4dataset:
            instmodel4dataset = self.instmodel4dataset.copy()
        else:
            instmodel4dataset = None
        db = DatabaseInstLvlDataset(object_stored="datasimulator",
                                    database_name=self.object_name,
                                    instmodel4dataset=instmodel4dataset,
                                    ordered=False)

        db.database_unlock()
        # Get the list of used instrument model
        for instmod_obj in self.get_instmodels_used():
            inst_model = instmod_obj.name
            inst_name = instmod_obj.instrument.name
            inst_cat = instmod_obj.instrument.category
            db[inst_cat][inst_name][inst_model] = self._create_datasimulator(instmod_obj)
        if lock_db:
            db.lock()
        return db
