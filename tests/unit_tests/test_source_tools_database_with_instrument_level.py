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
        pass

    def test_creation(self):
        DatabaseInstLevel(object_name="K2-19", database_name="datasimulator")

    def test_add_rm_get_instcatlevel(self):
        db = DatabaseInstLevel(object_name="K2-19", database_name="datasimulator")
        db.add_instcat(inst_cat="RV")
        db.add_instcat(inst_cat="LC")
        self.assertCountEqual(db.inst_categories, ["RV", "LC"])
        db.rm_instcat("RV")
        self.assertCountEqual(db.inst_categories, ["LC"])

    def test_add_rm_get_instnamelevel(self):
        db = DatabaseInstLevel(object_name="K2-19", database_name="datasimulator")
        db.add_instcat(inst_cat="RV")
        db.add_instcat(inst_cat="LC")
        db.add_instname(inst_cat="RV", inst_name="HARPS")
        db.add_instname(inst_cat="RV", inst_name="SOPHIE")
        db.add_instname(inst_cat="LC", inst_name="CoRoT")
        db.add_instname(inst_cat="LC", inst_name="Kepler")
        self.assertCountEqual(db.get_instnames(inst_cat="RV"), ["HARPS", "SOPHIE"])
        self.assertCountEqual(db.get_instnames(inst_cat="LC"), ["CoRoT", "Kepler"])
        db.rm_instname("RV", "HARPS")
        self.assertCountEqual(db.get_instnames(inst_cat="RV"), ["SOPHIE"])

    def test_add_rm_get_instmodellevel(self):
        db = DatabaseInstLevel(object_name="K2-19", database_name="datasimulator")
        db.add_instcat(inst_cat="RV")
        db.add_instcat(inst_cat="LC")
        db.add_instname(inst_cat="RV", inst_name="HARPS")
        db.add_instname(inst_cat="RV", inst_name="SOPHIE")
        db.add_instname(inst_cat="LC", inst_name="CoRoT")
        db.add_instname(inst_cat="LC", inst_name="Kepler")
        db.add_instmodel(inst_cat="RV", inst_name="HARPS", inst_model="default")
        db.add_instmodel(inst_cat="RV", inst_name="HARPS", inst_model="test")
        db.add_instmodel(inst_cat="LC", inst_name="CoRoT", inst_model="default")
        db.add_instmodel(inst_cat="LC", inst_name="Kepler", inst_model="default")
        db.add_instmodel(inst_cat="LC", inst_name="Kepler", inst_model="test")
        self.assertCountEqual(db.get_instmodels(inst_cat="RV", inst_name="HARPS"),
                              ["default", "test"])
        self.assertCountEqual(db.get_instmodels(inst_cat="RV", inst_name="SOPHIE"), [])
        self.assertCountEqual(db.get_instmodels(inst_cat="LC", inst_name="CoRoT"), ["default"])
        db.rm_instmodel("RV", "HARPS", "test")
        self.assertCountEqual(db.get_instmodels(inst_cat="RV", inst_name="HARPS"),
                              ["default"])

    def test_add_object(self):
        db = DatabaseInstLevel(object_name="K2-19", database_name="datasimulator")
        db.add_object(inst_cat="RV", inst_name="HARPS", inst_model="default", object="test")
        self.assertEqual(db["RV"]["HARPS"]["default"], "test")


if __name__ == '__main__':
    main()
