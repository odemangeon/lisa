#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Unit tests for the source.posterior.core.prior.core_prior module.
"""
from unittest import TestCase, main
from logging import getLogger, StreamHandler, Formatter
from logging import DEBUG
from sys import stdout
from os import remove
# from ipdb import set_trace
from numpy import zeros

from source.posterior.core.prior.core_prior import Manager_Prior
from source.posterior.exoplanet.model.gravgroup import GravGroup
from source.posterior.core.dataset_and_instrument.dataset_database import DatasetDatabase
from source.posterior.core.datasetsfile_db import DatasetsFileDb


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
        self.dataset_db = DatasetDatabase(object_name="K2-19")
        self.dataset_db_RVonly = DatasetDatabase(object_name="K2-19")
        file1 = "LC_K2-29_K2.txt"
        file2 = "RV_K2-29_SOPHIE-HE.txt"
        file3 = "RV_K2-29_HARPS.txt"
        instmod_name = "default"
        noisemod_name = "gaussian"
        line1 = "{}  {}  {}".format(file1, instmod_name, noisemod_name)
        line2 = "{}  {}  {}".format(file2, instmod_name, noisemod_name)
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
        noisemod4instmodfullname = self.datasetsfile_db.get_noisemod4instmodfullname()
        self.l_instmod_fullnames = list(noisemod4instmodfullname.keys())
        noisemod4instmodfullname_RVonly = self.datasetsfile_db_RV_only.get_noisemod4instmodfullname()
        self.l_instmod_fullnames_RVonly = list(noisemod4instmodfullname_RVonly.keys())
        remove(file1)
        remove(file2)
        remove(file3)
        remove(dataset_file)
        remove(dataset_file_RVonly)
        self.managerp = Manager_Prior()
        self.managerp.load_setup()
        print(self.dataset_db.inst_categories)

    def test_class_Name(self):
        # set_trace()
        gravgroup_model = GravGroup(name="K2-19",
                                    dataset_db=self.dataset_db_RVonly,
                                    l_instmod_fullnames=self.l_instmod_fullnames_RVonly,
                                    transit_model="batman", ld_model=None,
                                    rv_model="ajplanet",
                                    stars=1, planets=2)
        logger.info("GravGroup Instance created !")
        logger.info("name: {}".format(gravgroup_model.get_name()))
        gravgroup_model.apply_RV_EXOFAST_param()
        logger.info("All params: {}".format(gravgroup_model.get_list_paramnames(full_name=True)))
        logger.info("Main params: {}".format(gravgroup_model.
                                             get_list_paramnames(main=True, full_name=True)))
        logger.info("Main free params: {}".format(gravgroup_model.
                                                  get_list_paramnames(main=True, free=True,
                                                                      full_name=True)))
        priors = gravgroup_model.create_individual_lnpriors()
        logger.info("priors['marginal'].keys(): {}".format(list(priors['marginal'].keys())))
        joint_prior = (gravgroup_model.
                       create_joint_lnprior(gravgroup_model.
                                            get_list_paramnames(main=True, free=True,
                                                                full_name=True)))
        param_val = zeros(len(gravgroup_model.get_list_paramnames(main=True, full_name=True)))
        logger.info("param_val: {}".format(param_val))
        logger.info("joint prior for param_val: {}".format(joint_prior(param_val)))


if __name__ == '__main__':
    main()
