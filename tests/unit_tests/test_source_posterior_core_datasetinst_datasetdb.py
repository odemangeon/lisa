#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Unit tests for the source.posterior.core.dataset_and_instrument.dataset_database module.
"""
from unittest import TestCase, main
from logging import getLogger, StreamHandler, Formatter
from logging import DEBUG
from sys import stdout

import lisa.posterior.core.dataset_and_instrument.dataset_database as ddb

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

    def test_Nesteddict_defgetitem(self):
        db = ddb.Nesteddict_defgetitem(nb_lvl=3)
        dataset_HARPS = "dataset_RV_HARPS_0"
        db["RV"]["HARPS"]["0"] = dataset_HARPS
        self.assertEqual(db["."]["."]["."], dataset_HARPS)
        dataset_SOPHIE = "dataset_RV_SOPHIE_0"
        db["RV"]["SOPHIE"]["0"] = dataset_SOPHIE
        logger.info("Db: {}".format(db))
        self.assertEqual(db["RV"]["SOPHIE"][0], dataset_SOPHIE)
        self.assertEqual(db["RV"]["SOPHIE"]["1st"], dataset_SOPHIE)
        self.assertEqual(db["RV_K2-19_SOPHIE_0"], dataset_SOPHIE)
        self.assertEqual(db["RV_K2-19_SOPHIE"], dataset_SOPHIE)
        with self.assertRaises(KeyError):
            db["."]["."]["."]


if __name__ == '__main__':
    main()
