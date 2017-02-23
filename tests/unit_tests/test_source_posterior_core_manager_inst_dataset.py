#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Unit tests for the source.posterior.core.dataset_and_instrument.manager_dataset_instrument module.
"""
import logging
import unittest
import sys

import source.posterior.core.dataset_and_instrument.manager_dataset_instrument as mgr
import source.posterior.core.dataset_and_instrument.instrument as inst
from source.posterior.exoplanet.dataset_and_instrument.lc import LC_Instrument
from source.posterior.exoplanet.dataset_and_instrument.rv import RV_Instrument

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
        self.K2_inst = inst.Default_Instrument("LC", "K2")

    def test_get_filename_from_filepath(self):
        file_path = "Users/olivier/Softwares/lisa/data/K2-19/EPIC201505350.rdb"
        file_name = mgr.get_filename_from_file_path(file_path)
        self.assertEqual(file_name, "EPIC201505350.rdb")

    def test_manage_dataset_associated_to_inst_category_database(self):
        manager = mgr.Manager_Inst_Dataset()
        manager._reset_inst_categories()
        list_res = manager.get_available_inst_category()
        logger.info("Available instrument categories: {}".format(list_res))
        self.assertSequenceEqual(manager.get_available_inst_category(), [])
        manager.add_available_inst_category(LC_Instrument, "DatasetSubclass")
        list_res = manager.get_available_inst_category()
        logger.info("Available instrument categories: {}".format(list_res))
        self.assertSequenceEqual(manager.get_available_inst_category(), ["LC"])
        dataset_subclass = manager.get_dataset_subclass(inst_category="LC")
        self.assertEqual(dataset_subclass, "DatasetSubclass")
        self.assertTrue(manager.validate_inst_category(inst_category="LC"))
        self.assertFalse(manager.validate_inst_category(inst_category="Truc"))
        manager._reset_inst_categories()
        list_res = manager.get_available_inst_category()
        logger.info("Available instrument categories: {}".format(list_res))
        self.assertSequenceEqual(list_res, [])

    def test_manage_instrument_instance_associated_to_inst_name_database(self):
        manager = mgr.Manager_Inst_Dataset()
        manager._reset_available_inst()
        list_res = manager.get_available_inst_name()
        logger.info("Available instruments: {}".format(list_res))
        self.assertSequenceEqual(manager.get_available_inst_name(), [])
        manager.add_available_inst_category(LC_Instrument, "DatasetSubclass")
        manager.add_available_inst(self.K2_inst)
        list_res = manager.get_available_inst_name()
        logger.info("Available instruments: {}".format(list_res))
        self.assertSequenceEqual(manager.get_available_inst_name(), ["K2"])
        instrument_instance = manager.get_instrument(inst_name="K2")
        self.assertEqual(instrument_instance, self.K2_inst)
        self.assertTrue(manager.is_available_inst(inst_name="K2"))
        self.assertFalse(manager.is_available_inst(inst_name="Truc"))
        manager._reset_available_inst()
        list_res = manager.get_available_inst_name()
        logger.info("Available instrument: {}".format(list_res))
        self.assertSequenceEqual(list_res, [])

    def test_manage_default_instrument_instance(self):
        manager = mgr.Manager_Inst_Dataset()
        manager._reset_available_inst()
        list_res = manager.get_available_inst_name()
        logger.info("Available instruments: {}".format(list_res))
        self.assertSequenceEqual(manager.get_available_inst_name(), [])
        manager.add_available_inst_category(LC_Instrument, "DatasetSubclass")
        manager.add_available_def_inst("LC", "K2")
        list_res = manager.get_available_inst_name()
        logger.info("Available instruments: {}".format(list_res))
        self.assertSequenceEqual(manager.get_available_inst_name(), ["K2"])


if __name__ == '__main__':
    unittest.main()
