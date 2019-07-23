#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Unit tests for the source.posterior.exoplanet.model module.
"""
from unittest import TestCase, main
from logging import getLogger, StreamHandler, Formatter
from logging import DEBUG, INFO
from sys import stdout
# from ipdb import set_trace

import os
import numpy as np

import lisa.posterior.exoplanet.model.gravgroup as exomdl
import lisa.posterior.core.prior.manager_prior as mgrp
from source.posterior.core.dataset_and_instrument.dataset_database import DatasetDatabase
from source.posterior.core.datasetsfile_db import DatasetsFileDb

level_logger = DEBUG
level_handler = DEBUG

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

    def setUp(self):
        self.dataset_db = DatasetDatabase(object_name="K2-19")
        self.dataset_db_RVonly = DatasetDatabase(object_name="K2-19")
        file1 = "LC_K2-29_K2.txt"
        instmod_name = "default"
        noisemod_name = "gaussian"
        line1 = "{}  {}  {}".format(file1, instmod_name, noisemod_name)
        file2 = "RV_K2-29_SOPHIE-HE.txt"
        line2 = "{}  {}  {}".format(file2, instmod_name, noisemod_name)
        file3 = "RV_K2-29_HARPS.txt"
        line3 = "{}  {}  {}".format(file3, instmod_name, noisemod_name)
        dataset_file = "test_datasetfile.txt"
        dataset_file_RVonly = "test_datasetfile_RVonly.txt"
        open(file1, "x").close()
        open(file2, "x").close()
        open(file3, "x").close()
        with open(dataset_file, "x") as f:
            f.write(line1 + "\n")
            f.write(line2 + "\n")
            f.write(line3 + "\n")
        with open(dataset_file_RVonly, "x") as f:
            f.write(line2 + "\n")
            f.write(line3 + "\n")
        self.datasetsfile_db = DatasetsFileDb(object_name="K2-29")
        self.datasetsfile_db_RV_only = DatasetsFileDb(object_name="K2-29")
        self.datasetsfile_db.load(datasetsfile_path=dataset_file)
        self.datasetsfile_db_RV_only.load(datasetsfile_path=dataset_file_RVonly)
        (self.dataset_db.
         _add_datasets_from_listdatasetpath(l_dataset_path=self.datasetsfile_db.dataset_filepaths))
        (self.dataset_db_RVonly.
         _add_datasets_from_listdatasetpath(l_dataset_path=(self.datasetsfile_db_RV_only.
                                                            dataset_filepaths)))
        os.remove(file1)
        os.remove(file2)
        os.remove(file3)
        os.remove(dataset_file)
        os.remove(dataset_file_RVonly)
        noisemod4instmodfullname = self.datasetsfile_db.get_noisemod4instmodfullname()
        self.l_instmod_fullnames = list(noisemod4instmodfullname.keys())
        noisemod4instmodfullname_RVonly = self.datasetsfile_db_RV_only.get_noisemod4instmodfullname()
        self.l_instmod_fullnames_RVonly = list(noisemod4instmodfullname_RVonly.keys())
        self.managerp = mgrp.Manager_Prior()
        self.managerp.load_setup()
        logger.debug("Instrument categories in the dataset_db: {}"
                     "".format(self.dataset_db.inst_categories))

    def test_basics(self):
        logger.info("\n\nStart test_basics")
        gravgroup_model = exomdl.GravGroup(name="K2-19",
                                           dataset_db=self.dataset_db,
                                           l_instmod_fullnames=self.l_instmod_fullnames,
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
        self.assertEqual(gravgroup_model.paramcontainers["stars"]["A"].get_name(), "A")
        self.assertEqual(gravgroup_model.paramcontainers["stars"]["A"].get_name(include_prefix=False, code_version=True), "A")
        self.assertEqual(gravgroup_model.paramcontainers["stars"]["A"].get_name(include_prefix=True), "K2-19_A")
        self.assertEqual(gravgroup_model.paramcontainers["stars"]["A"].get_name(include_prefix=True, code_version=True), "K219_A")
        logger.info("planets: {}".format(gravgroup_model.paramcontainers["planets"]))
        logger.info("Number of planets in the gravgroup: {}"
                    "".format(gravgroup_model.nb_of_paramcontainers["planets"]))
        self.assertEqual(gravgroup_model.nb_of_paramcontainers["planets"], 2)
        self.assertTrue(gravgroup_model.isavailable_paramcontainer("b", "planets"))
        self.assertEqual(gravgroup_model.paramcontainers["planets"]["b"].get_name(), "b")
        self.assertEqual(gravgroup_model.paramcontainers["planets"]["b"].get_name(include_prefix=False, code_version=True), "b")
        self.assertEqual(gravgroup_model.paramcontainers["planets"]["b"].get_name(include_prefix=True), "K2-19_b")
        self.assertEqual(gravgroup_model.paramcontainers["planets"]["b"].get_name(include_prefix=True, code_version=True), "K219_b")
        self.assertTrue(gravgroup_model.isavailable_paramcontainer("c", "planets"))
        self.assertEqual(gravgroup_model.paramcontainers["planets"]["c"].get_name(), "c")
        self.assertEqual(gravgroup_model.paramcontainers["planets"]["c"].get_name(include_prefix=False, code_version=True), "c")
        self.assertEqual(gravgroup_model.paramcontainers["planets"]["c"].get_name(include_prefix=True), "K2-19_c")
        self.assertEqual(gravgroup_model.paramcontainers["planets"]["c"].get_name(include_prefix=True, code_version=True), "K219_c")

    def test_parametrisationfile(self):
        logger.info("\n\nStart test_parmetrisationfile")
        # set_trace()
        gravgroup_model = exomdl.GravGroup(name="K2-19", dataset_db=self.dataset_db_RVonly,
                                           l_instmod_fullnames=self.l_instmod_fullnames_RVonly,
                                           rv_model="ajplanet",
                                           stars=1, planets=2)
        logger.info("Parametrisation : {}"
                    "".format(gravgroup_model.paramcontainers["stars"]["A"].
                              get_list_params(main=True)))
        logger.info("Parametrisation : {}"
                    "".format(gravgroup_model.paramcontainers["planets"]["b"].
                              get_list_params(main=True)))
        logger.info("Parametrisation : {}"
                    "".format(gravgroup_model.paramcontainers["planets"]["c"].
                              get_list_params(main=True)))
        self.assertFalse(gravgroup_model.paramcontainers["stars"]["A"].v0.main)
        gravgroup_model.apply_RV_EXOFAST_param()
        self.assertTrue(gravgroup_model.paramcontainers["stars"]["A"].v0.main)
        self.assertTrue(gravgroup_model.paramcontainers["planets"]["b"].K.main)
        self.assertTrue(gravgroup_model.paramcontainers["planets"]["c"].K.main)
        logger.info("Parametrisation : {}"
                    "".format(gravgroup_model.paramcontainers["stars"]["A"].
                              get_list_params(main=True)))
        logger.info("Parametrisation : {}"
                    "".format(gravgroup_model.paramcontainers["planets"]["b"].
                              get_list_params(main=True)))
        logger.info("Parametrisation : {}"
                    "".format(gravgroup_model.paramcontainers["planets"]["c"].
                              get_list_params(main=True)))
        logger.info("List dataset names in model.instmodel4dataset: {}"
                    "".format(gravgroup_model.instmodel4dataset.list_datasets))
        logger.info("paramfile_section :\n{}".format(gravgroup_model.get_paramfile_section()))

    def test_creation_datasimulator(self):
        logger.info("\n\nStart test_creation_datasimulator")
        logger.handlers[0].setLevel(10)
        gravgroup_model = exomdl.GravGroup(name="K2-19", dataset_db=self.dataset_db_RVonly,
                                           l_instmod_fullnames=self.l_instmod_fullnames_RVonly,
                                           rv_model="ajplanet",
                                           stars=1, planets=2)
        logger.info("gravgroup_model stars name: {}".format(list(gravgroup_model.stars.keys())))
        logger.info("gravgroup_model planets name: {}".format(list(gravgroup_model.
                                                                   planets.keys())))
        gravgroup_model.apply_RV_EXOFAST_param(with_drift=True)  # TODO: the with_drift=True doesn't
        res = gravgroup_model._create_datasimulator_RV(gravgroup_model.  # WORK
                                                       instruments["RV"]["HARPS"]["default"])
        logger.info("Dictionnary containing the datasimulator DocFunction:\n{}".format(res))
        logger.info("arg_list of the system datasimulator:\n{}"
                    "".format(res["whole"].arg_list))
        logger.info("arg_list of planet b datasimulator:\n{}"
                    "".format(res[gravgroup_model.planets["b"].name].arg_list))
        logger.info("function of the system datasimulator:\n{}"
                    "".format(res["whole"].function))
        # ["amp","gamma", "period","tau", "trvsys", "k", "w", "ecc", "t0", "period1", "k2", "w2",
        #  "ecc2", "t02", "period2" ]
        p = [0.0, 0.0, 14.4, 0.119 * np.cos(90.0 * np.pi / 180.),
             0.119 * np.sin(90.0 * np.pi / 180.), 66.8503, 7.92008, 4.8,
             0.095 * np.cos(16.3 * np.pi / 180.), 0.095 * np.sin(16.3 * np.pi / 180.), 67.19487,
             11.9068]
        simu_data = res["whole"].function(p, np.arange(66., 80.))
        logger.info("Simulated data:\n{}".format(simu_data))


if __name__ == '__main__':
    main()
