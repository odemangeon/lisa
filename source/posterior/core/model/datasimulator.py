#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
datasimulator module.

The objective of this module is to define the class DatasimulatorCreator.

@DONE:
    -

@TODO:
    -
"""
from logging import getLogger


## logger object
logger = getLogger()

## Root of all the function for the creation of datasimulators
root_name_func_datsim = "_create_datasimulator"


class DatasimulatorCreator(object):
    """docstring for DatasimulatorCreator."""

    def _create_datasimulator(self, inst_model):
        """Return the datasimulator for a given instrument model."""
        inst_cat = inst_model.instrument.category
        create_datasim_func = getattr(self, root_name_func_datsim + "_" + inst_cat)
        return create_datasim_func(self, inst_model)

    def create_datasimulators(self):
        """Return the datasimulator for each instrument model used."""
        db = self._create_database_func_instlevel(object_name=self.object_name,
                                                  database_name="datasimulator")
