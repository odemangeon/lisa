#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Unit tests for the source.posterior.exoplanet.model module.
"""
import logging
import unittest
import sys

import source.posterior.exoplanet.model.gravgroup as exomdl
import source.posterior.core.prior.manager_prior as mgrp

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
        self.instruments = {"LC": {"K2": "inst_K2", }, "RV": {"HARPS": "inst_HARPS"}}
        self.instruments_RVonly = {"RV": {"HARPS": "inst_HARPS", "SOPHIE": "inst_SOPHIE"}}
        self.managerp = mgrp.Manager_Prior()
        self.managerp.load_setup()

    def test_basics(self):
        gravgroup_model = exomdl.GravGroup(name="K2-19", instruments=self.instruments,
                                           transit_model="batman", ld_model=None,
                                           rv_model="ajplanet",
                                           stars=1, planets=2)
        logger.info("GravGroup Instance created !")
        logger.info("name: {}".format(gravgroup_model.name))
        self.assertEqual(gravgroup_model.name, "K2-19")
        logger.info("transit_model: {}".format(gravgroup_model.transit_model))
        self.assertEqual(gravgroup_model.transit_model, "batman")
        logger.info("ld_model: {}".format(gravgroup_model.ld_model))
        self.assertEqual(gravgroup_model.ld_model, "quadratic")
        logger.info("rv_model: {}".format(gravgroup_model.rv_model))
        self.assertEqual(gravgroup_model.rv_model, "ajplanet")
        logger.info("Stars: {}".format(gravgroup_model.stars))
        logger.info("Number of stars in the gravgroup: {}".format(gravgroup_model.nb_of_stars))
        self.assertEqual(gravgroup_model.nb_of_stars, 1)
        self.assertTrue(gravgroup_model.is_star("A"))
        self.assertEqual(gravgroup_model.stars["A"].name, "A")
        self.assertEqual(gravgroup_model.stars["A"].name_code, "A")
        self.assertEqual(gravgroup_model.stars["A"].full_name, "K2-19_A")
        self.assertEqual(gravgroup_model.stars["A"].full_name_code, "K219_A")
        logger.info("planets: {}".format(gravgroup_model.planets))
        logger.info("Number of planets in the gravgroup: {}".format(gravgroup_model.nb_of_planets))
        self.assertEqual(gravgroup_model.nb_of_planets, 2)
        self.assertTrue(gravgroup_model.is_planet("b"))
        self.assertEqual(gravgroup_model.planets["b"].name, "b")
        self.assertEqual(gravgroup_model.planets["b"].name_code, "b")
        self.assertEqual(gravgroup_model.planets["b"].full_name, "K2-19_b")
        self.assertEqual(gravgroup_model.planets["b"].full_name_code, "K219_b")
        self.assertTrue(gravgroup_model.is_planet("c"))
        self.assertEqual(gravgroup_model.planets["c"].name, "c")
        self.assertEqual(gravgroup_model.planets["c"].name_code, "c")
        self.assertEqual(gravgroup_model.planets["c"].full_name, "K2-19_c")
        self.assertEqual(gravgroup_model.planets["c"].full_name_code, "K219_c")

    def test_parmetrisationfile(self):
        gravgroup_model = exomdl.GravGroup(name="K2-19", instruments=self.instruments_RVonly,
                                           rv_model="ajplanet",
                                           stars=1, planets=2)
        logger.info("Parametrisation : {}"
                    "".format(gravgroup_model.stars["A"].get_list_main_params()))
        logger.info("Parametrisation : {}"
                    "".format(gravgroup_model.planets["b"].get_list_main_params()))
        logger.info("Parametrisation : {}"
                    "".format(gravgroup_model.planets["c"].get_list_main_params()))
        self.assertFalse(gravgroup_model.stars["A"].v0.main)
        gravgroup_model.apply_RV_EXOFAST_param()
        self.assertTrue(gravgroup_model.stars["A"].v0.main)
        self.assertTrue(gravgroup_model.planets["b"].K.main)
        self.assertTrue(gravgroup_model.planets["c"].K.main)
        logger.info("Parametrisation : {}"
                    "".format(gravgroup_model.stars["A"].get_list_main_params()))
        logger.info("Parametrisation : {}"
                    "".format(gravgroup_model.planets["b"].get_list_main_params()))
        logger.info("Parametrisation : {}"
                    "".format(gravgroup_model.planets["c"].get_list_main_params()))
        logger.info("paramfile_section :\n{}".format(gravgroup_model.get_paramfile_section()))


if __name__ == '__main__':
    unittest.main()
