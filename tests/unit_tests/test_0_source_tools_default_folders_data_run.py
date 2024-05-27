#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Unit tests for the source.tools.default_folders_data_run
"""
import logging
import unittest
import sys
import os

# from unittest.mock import patch

import lisa.tools.default_folders_data_run as mod
# import lisa.posterior.core.posterior as pst
#
# from lisa.posterior.core.dataset_and_instrument.manager_dataset_instrument import \
#     Manager_Inst_Dataset
# from lisa.posterior.core.model.core_model import Core_Model
# import lisa.posterior.exoplanet.dataset_and_instrument.lc as lc
# import lisa.posterior.exoplanet.dataset_and_instrument.rv as rv
# from lisa.posterior.core.dataset_and_instrument.dataset_database import DatasetDatabase
# from lisa.posterior.core.likelihood.jitter_noise_model import GaussianNoiseModel

logger = logging.getLogger()
if logger.level > logging.DEBUG:
    logger.setLevel(logging.DEBUG)
if len(logger.handlers) == 0:
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)


class TestMethods(unittest.TestCase):

    def setUp(self):

        class ChildRunfolder(mod.RunFolder):
            """docstring for ChildRunfolded."""

            def __init__(self, run_folder=None):
                self.object_name = "testobject"
                mod.RunFolder.__init__(self, run_folder=run_folder)

        class ChildDatafolder(mod.DataFolder):
            """docstring for ChildDatafolded."""

            def __init__(self, data_folder=None):
                self.object_name = "testobject"
                mod.DataFolder.__init__(self, data_folder=data_folder)

        class ChildRunNDatafolder(mod.RunFolder, mod.DataFolder):
            """docstring for ChildRunNDatafolded."""

            def __init__(self, run_folder=None, data_folder=None):
                self.object_name = "testobject"
                mod.RunFolder.__init__(self, run_folder=run_folder)
                mod.DataFolder.__init__(self, data_folder=data_folder)

        self.ChildRunfolder = ChildRunfolder
        self.ChildDatafolder = ChildDatafolder
        self.ChildRunNDatafolder = ChildRunNDatafolder

    def test_posterior_instance_creation_basic(self):
        i_runfolder_no = self.ChildRunfolder()
        i_datafolder_no = self.ChildDatafolder()
        i_rundatafolder_no = self.ChildRunNDatafolder()
        i_runfolder_cwd = self.ChildRunfolder(run_folder=os.getcwd())
        i_datafolder_cwd = self.ChildDatafolder(data_folder=os.getcwd())
        i_rundatafolder_cwd = self.ChildRunNDatafolder(run_folder=os.getcwd(), data_folder=os.getcwd())

    # TODO: Test the run_folder = "default" when the self.object.name

if __name__ == '__main__':
    unittest.main()
