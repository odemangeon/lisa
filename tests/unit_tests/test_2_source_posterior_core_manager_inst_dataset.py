#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Unit tests for the source.posterior.core.dataset_and_instrument.manager_dataset_instrument module.
"""
from unittest import TestCase, main
from logging import getLogger, StreamHandler, Formatter
from logging import DEBUG, INFO
from sys import stdout


import lisa.posterior.core.dataset_and_instrument.manager_dataset_instrument as mgr
import lisa.posterior.core.dataset_and_instrument.instrument as inst
from lisa.posterior.exoplanet.dataset_and_instrument.lc import LC_Instrument

level_logger = DEBUG
level_handler = INFO

logger = getLogger()
if logger.level != level_logger:
    logger.setLevel(level_logger)
if len(logger.handlers) == 0:
    ch = StreamHandler(stdout)
    ch.setLevel(level_handler)
    formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
else:
    ch = logger.handlers[0]
    if ch.level != level_handler:
        ch.setLevel(level_handler)


class TestMethods(TestCase):

    def test_manage_dataset_associated_to_inst_category_database(self):
        logger.info("Beginning of test test_manage_dataset_associated_to_inst_category_database")
        manager = mgr.Manager_Inst_Dataset()
        manager._reset_inst_cat()
        list_res = manager.get_available_inst_cat()
        logger.info("Available instrument categories: {}".format(list_res))
        self.assertSequenceEqual(manager.get_available_inst_cat(), [])
        manager.add_available_inst_cat(LC_Instrument, "DatasetSubclass")
        list_res = manager.get_available_inst_cat()
        logger.info("Available instrument categories: {}".format(list_res))
        self.assertSequenceEqual(manager.get_available_inst_cat(), ["LC"])
        dataset_subclass = manager.get_dataset_subclass(inst_cat="LC")
        self.assertEqual(dataset_subclass, "DatasetSubclass")
        self.assertTrue(manager.validate_inst_cat(inst_cat="LC"))
        self.assertFalse(manager.validate_inst_cat(inst_cat="Truc"))
        manager._reset_inst_cat()
        list_res = manager.get_available_inst_cat()
        logger.info("Available instrument categories: {}".format(list_res))
        self.assertSequenceEqual(list_res, [])

    def test_manage_instrument_instance_associated_to_inst_name_database(self):
        logger.info("Beginning of test test_manage_instrument_instance_associated_to_inst_name_database")
        manager = mgr.Manager_Inst_Dataset()
        manager._reset_manager()
        list_res = manager.get_available_inst_name()
        logger.info("Available instruments: {}".format(list_res))
        self.assertSequenceEqual(manager.get_available_inst_name(), [])
        manager.add_available_inst_cat(LC_Instrument, "DatasetSubclass")
        K2_inst = LC_Instrument(name="K2", subcat=None)
        manager.add_available_inst(K2_inst)
        list_res = manager.get_available_inst_name()
        logger.info("Available instruments: {}".format(list_res))
        self.assertSequenceEqual(manager.get_available_inst_name(), {'LC': ["K2"]})
        instrument_instance = manager.get_inst(inst_name="K2", inst_cat="LC")
        self.assertEqual(instrument_instance, K2_inst)
        self.assertTrue(manager.is_available_inst(inst_name="K2", inst_cat="LC"))
        self.assertFalse(manager.is_available_inst(inst_name="Truc", inst_cat="LC"))
        manager._reset_manager()
        list_res = manager.get_available_inst_name()
        logger.info("Available instrument: {}".format(list_res))
        self.assertSequenceEqual(list_res, [])

    def test_manage_default_instrument_instance(self):
        logger.info("Beginning of test test_manage_default_instrument_instance")
        manager = mgr.Manager_Inst_Dataset()
        manager._reset_manager()
        list_res = manager.get_available_inst_name()
        logger.info("Available instruments: {}".format(list_res))
        self.assertSequenceEqual(manager.get_available_inst_name(), [])
        manager.add_available_inst_cat(LC_Instrument, "DatasetSubclass")
        manager.add_available_def_inst("LC", "K2")
        list_res = manager.get_available_inst_name()
        logger.info("Available instruments: {}".format(list_res))
        self.assertSequenceEqual(manager.get_available_inst_name(), {"LC": ["K2"]})


if __name__ == '__main__':
    main()
