#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Unit tests for the source.tools.name module.
"""
from unittest import TestCase, main
from logging import getLogger, StreamHandler, Formatter
from logging import DEBUG
from sys import stdout

from source.tools.database_with_instrument_level import DatabaseInstLevel

logger = getLogger()
if logger.level > DEBUG:
    logger.setLevel(DEBUG)
if len(logger.handlers) == 0:
    ch = StreamHandler(stdout)
    ch.setLevel(DEBUG)
    formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)


class TestMethods(TestCase):

    def setUp(self):
        self.db = DatabaseInstLevel(object_stored="datasimulator", database_name="K2-19")

    def test_add_rm_get_instcatlevel(self):
        self.db["RV"]
        self.db["LC"]
        self.assertCountEqual(self.db.inst_categories, ["RV", "LC"])
        self.db.pop("RV")
        self.assertCountEqual(self.db.inst_categories, ["LC"])

    def test_add_rm_get_instnamelevel(self):
        self.db["RV"]["HARPS"]
        self.db["RV"]["SOPHIE"]
        self.db["LC"]["CoRoT"]
        self.db["LC"]["Kepler"]
        self.assertCountEqual(self.db.get_instnames(inst_cat="RV"), ["HARPS", "SOPHIE"])
        self.assertCountEqual(self.db.get_instnames(inst_cat="LC"), ["CoRoT", "Kepler"])
        self.db["RV"].pop("HARPS")
        self.assertCountEqual(self.db.get_instnames(inst_cat="RV"), ["SOPHIE"])

    def test_add_rm_get_instmodellevel(self):
        self.db["RV"]["HARPS"]["default"]
        self.db["RV"]["HARPS"]["test"]
        self.db["LC"]["CoRoT"]["default"]
        self.db["LC"]["Kepler"]["default"]
        self.db["LC"]["Kepler"]["test"]
        self.assertCountEqual(self.db.get_instmodels(inst_cat="RV", inst_name="HARPS"),
                              ["default", "test"])
        self.assertCountEqual(self.db.get_instmodels(inst_cat="RV", inst_name="SOPHIE"), [])
        self.assertCountEqual(self.db.get_instmodels(inst_cat="LC", inst_name="CoRoT"), ["default"])
        self.db["RV"]["HARPS"].pop("test")
        self.assertCountEqual(self.db.get_instmodels(inst_cat="RV", inst_name="HARPS"),
                              ["default"])

    def test_addget_object(self):
        self.db["RV"]["HARPS"]["default"] = "test"
        self.assertEqual(self.db["RV"]["HARPS"]["default"], "test")
        self.assertEqual(self.db["HARPS_default"], "test")
        self.assertEqual(self.db["RV"]["HARPS_default"], "test")
        self.assertEqual(self.db["HARPS"]["default"], "test")

    def test_hasatleast1instmod(self):
        self.db["RV"]["HARPS"]["default"] = "test"
        self.db["RV"]["SOPHIE"]
        self.assertTrue(self.db.hasatleast1instmod())
        self.assertTrue(self.db.hasatleast1instmod(inst_name="HARPS", inst_cat="RV"))
        self.assertTrue(self.db.hasatleast1instmod(inst_cat="RV"))
        self.assertTrue(self.db.hasatleast1instmod(inst_name="HARPS"))
        self.assertFalse(self.db.hasatleast1instmod(inst_name="SOPHIE"))
        self.assertFalse(self.db.hasatleast1instmod(inst_name="LC"))


if __name__ == '__main__':
    main()
