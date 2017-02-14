#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Unit tests for the source.posterior.exoplanet.model module.
"""
import logging
import unittest
import sys
import os

import source.posterior.exoplanet.model.gravgroup as exomdl
import source.posterior.core.prior.manager_prior as mgrp
from source.posterior.core.dataset_and_instrument.dataset_database import DatasetDatabase

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
        self.dataset_db = DatasetDatabase(object_name="K2-19")
        self.dataset_db_RVonly = DatasetDatabase(object_name="K2-19")
        file1 = "LC_K2-29_K2.txt"
        file2 = "RV_K2-29_SOPHIE-HE.txt"
        file3 = "RV_K2-29_HARPS.txt"
        dataset_file = "test_datasetfile.txt"
        dataset_file_RVonly = "test_datasetfile_RVonly.txt"
        open(file1, "x").close()
        open(file2, "x").close()
        open(file3, "x").close()
        with open(dataset_file, "x") as f:
            f.write(file1 + "\n")
            f.write(file2 + "\n")
            f.write(file3 + "\n")
        with open(dataset_file_RVonly, "x") as f:
            f.write(file2 + "\n")
            f.write(file3 + "\n")
        self.dataset_db.add_datasets_from_datasetfile(path_datasets_file=dataset_file)
        self.dataset_db_RVonly.add_datasets_from_datasetfile(path_datasets_file=dataset_file_RVonly)
        os.remove(file1)
        os.remove(file2)
        os.remove(file3)
        os.remove(dataset_file)
        os.remove(dataset_file_RVonly)
        self.managerp = mgrp.Manager_Prior()
        self.managerp.load_setup()
        print(self.dataset_db.inst_categories)

    def test_basics(self):
        gravgroup_model = exomdl.GravGroup(name="K2-19",
                                           dataset_db=self.dataset_db,
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
        logger.info("Stars: {}".format(gravgroup_model.paramcontainers["stars"]))
        logger.info("Number of stars in the gravgroup: {}"
                    "".format(gravgroup_model.nb_of_paramcontainers["stars"]))
        self.assertEqual(gravgroup_model.nb_of_paramcontainers["stars"], 1)
        self.assertTrue(gravgroup_model.isavailable_paramcontainer("A", "stars"))
        self.assertEqual(gravgroup_model.paramcontainers["stars"]["A"].name, "A")
        self.assertEqual(gravgroup_model.paramcontainers["stars"]["A"].name_code, "A")
        self.assertEqual(gravgroup_model.paramcontainers["stars"]["A"].full_name, "K2-19_A")
        self.assertEqual(gravgroup_model.paramcontainers["stars"]["A"].full_name_code, "K219_A")
        logger.info("planets: {}".format(gravgroup_model.paramcontainers["planets"]))
        logger.info("Number of planets in the gravgroup: {}"
                    "".format(gravgroup_model.nb_of_paramcontainers["planets"]))
        self.assertEqual(gravgroup_model.nb_of_paramcontainers["planets"], 2)
        self.assertTrue(gravgroup_model.isavailable_paramcontainer("b", "planets"))
        self.assertEqual(gravgroup_model.paramcontainers["planets"]["b"].name, "b")
        self.assertEqual(gravgroup_model.paramcontainers["planets"]["b"].name_code, "b")
        self.assertEqual(gravgroup_model.paramcontainers["planets"]["b"].full_name, "K2-19_b")
        self.assertEqual(gravgroup_model.paramcontainers["planets"]["b"].full_name_code, "K219_b")
        self.assertTrue(gravgroup_model.isavailable_paramcontainer("c", "planets"))
        self.assertEqual(gravgroup_model.paramcontainers["planets"]["c"].name, "c")
        self.assertEqual(gravgroup_model.paramcontainers["planets"]["c"].name_code, "c")
        self.assertEqual(gravgroup_model.paramcontainers["planets"]["c"].full_name, "K2-19_c")
        self.assertEqual(gravgroup_model.paramcontainers["planets"]["c"].full_name_code, "K219_c")

    def test_parmetrisationfile(self):
        gravgroup_model = exomdl.GravGroup(name="K2-19", dataset_db=self.dataset_db_RVonly,
                                           rv_model="ajplanet",
                                           stars=1, planets=2)
        logger.info("Parametrisation : {}"
                    "".format(gravgroup_model.paramcontainers["stars"]["A"].get_list_main_params()))
        logger.info("Parametrisation : {}"
                    "".format(gravgroup_model.paramcontainers["planets"]["b"].get_list_main_params()))
        logger.info("Parametrisation : {}"
                    "".format(gravgroup_model.paramcontainers["planets"]["c"].get_list_main_params()))
        self.assertFalse(gravgroup_model.paramcontainers["stars"]["A"].v0.main)
        gravgroup_model.apply_RV_EXOFAST_param()
        self.assertTrue(gravgroup_model.paramcontainers["stars"]["A"].v0.main)
        self.assertTrue(gravgroup_model.paramcontainers["planets"]["b"].K.main)
        self.assertTrue(gravgroup_model.paramcontainers["planets"]["c"].K.main)
        logger.info("Parametrisation : {}"
                    "".format(gravgroup_model.paramcontainers["stars"]["A"].get_list_main_params()))
        logger.info("Parametrisation : {}"
                    "".format(gravgroup_model.paramcontainers["planets"]["b"].get_list_main_params()))
        logger.info("Parametrisation : {}"
                    "".format(gravgroup_model.paramcontainers["planets"]["c"].get_list_main_params()))
        logger.info("paramfile_section :\n{}".format(gravgroup_model.get_paramfile_section()))


if __name__ == '__main__':
    unittest.main()
