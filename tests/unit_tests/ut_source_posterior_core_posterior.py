#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Unit tests for the source.posterior.core.posterior
"""
import logging
import unittest
import sys
import os

from unittest.mock import patch

import source.posterior.core.posterior as pst

from source.software_parameters import input_data_folder
import source.posterior.core.dataset_and_instrument.manager_dataset_instrument as mgr
import source.posterior.exoplanet.dataset_and_instrument.lc as lc
import source.posterior.exoplanet.dataset_and_instrument.rv as rv

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
        self.posterior_instance = pst.Posterior("K2-29")
        self.posterior_instance_test = pst.Posterior("test")
        self.manager = mgr.Manager_Inst_Dataset()
        self.manager.set_dataset_for_inst_type("LC", lc.LC_Dataset)
        self.manager.add_available_inst(lc.K2)
        self.manager.set_dataset_for_inst_type("RV", rv.RV_Dataset)
        self.manager.add_available_inst(rv.SOPHIE_HE)
        self.test_datafile = "LC_K2-19_K2.txt"

    def test_object_name(self):
        self.assertEqual(self.posterior_instance.object_name, "K2-29")
        with self.assertRaises(AttributeError):
            self.posterior_instance.object_name = "K2-28"

    def test_datafolder_isset(self):
        self.assertFalse(self.posterior_instance.isset_datafolder())

    @patch('source.posterior.core.posterior.QCM_utilisateur', return_value="y")
    def test_set_custom_datafolder_answer_yes(self, input):
        path = "testposteriordatafolder"
        self.posterior_instance.data_folder = path
        self.assertEqual(self.posterior_instance.data_folder, path)
        os.rmdir(path)

    @patch('source.posterior.core.posterior.QCM_utilisateur', return_value="n")
    def test_set_custom_datafolder_answer_no(self, input):
        path = "testposteriordatafolder"
        self.posterior_instance.data_folder = path
        self.assertFalse(self.posterior_instance.isset_datafolder())

    def test_set_custom_datafolder_alreadyexists(self):
        path = "testposteriordatafolder"
        os.makedirs(path)
        self.posterior_instance.data_folder = path
        self.assertEqual(self.posterior_instance.data_folder, path)
        os.rmdir(path)

    @patch('source.posterior.core.posterior.QCM_utilisateur', return_value="y")
    def test_set_default_datafolder_answer_yes(self, input):
        path = os.path.join(input_data_folder, "test")
        self.posterior_instance_test.data_folder = "default"
        self.assertEqual(self.posterior_instance_test.data_folder, path)
        os.rmdir(path)

    @patch('source.posterior.core.posterior.QCM_utilisateur', return_value="n")
    def test_set_default_datafolder_answer_no(self, input):
        self.posterior_instance_test.data_folder = "default"
        self.assertFalse(self.posterior_instance_test.isset_datafolder())

    def test_set_default_datafolder_alreadyexists(self):
        path = os.path.join(input_data_folder, "test")
        os.makedirs(path)
        self.posterior_instance_test.data_folder = path
        self.assertEqual(self.posterior_instance_test.data_folder, path)
        os.rmdir(path)

    def test_manage_basic_operation_of_dataset_database(self):
        self.assertDictEqual(self.posterior_instance.dataset_database, {})
        self.posterior_instance.dataset_database = {}
        with self.assertRaises(ValueError):
            self.posterior_instance.dataset_database = {"a": {}}
        if os.path.isfile(self.test_datafile):
            raise ValueError("The file {} already exists. the unit test can't be performed or it "
                             " will damage it. Change current directory.")
        open(self.test_datafile, "x").close()
        dataset = self.manager.create_dataset(self.test_datafile)
        os.remove(self.test_datafile)
        self.posterior_instance._add_a_dataset(dataset)
        self.assertEqual(dataset, self.posterior_instance.dataset_database["LC"]["K2"]["0"])
        self.posterior_instance.rm_dataset("LC", "K2")
        self.assertDictEqual(self.posterior_instance.dataset_database, {})

    def test_add_a_dataset_from_path(self):
        open(self.test_datafile, "x").close()
        self.posterior_instance.add_a_dataset_from_path(datafile_path=self.test_datafile)
        os.remove(self.test_datafile)
        inst_type = self.posterior_instance.dataset_database["LC"]["K2"]["0"].instrument.inst_type
        inst_name = self.posterior_instance.dataset_database["LC"]["K2"]["0"].instrument.name
        number = self.posterior_instance.dataset_database["LC"]["K2"]["0"].number
        path = self.posterior_instance.dataset_database["LC"]["K2"]["0"].filepath
        self.assertEqual("LC", inst_type)
        self.assertEqual("K2", inst_name)
        self.assertEqual(0, number)
        self.assertEqual(self.test_datafile, path)

    def test_add_a_dataset_from_datasetsfile(self):
        file1 = "LC_K2-29_K2.txt"
        file2 = "RV_K2-29_SOPHIE-HE.txt"
        dataset_file = "test_datasetfile.txt"
        open(file1, "x").close()
        open(file2, "x").close()
        with open(dataset_file, "x") as f:
            f.write(file1 + "\n")
            f.write(file2 + "\n")
        self.posterior_instance.add_datasets_from_datasetfile(path_datasets_file=dataset_file)
        os.remove(file1)
        os.remove(file2)
        os.remove(dataset_file)
        inst_type = self.posterior_instance.dataset_database["LC"]["K2"]["0"].instrument.inst_type
        inst_name = self.posterior_instance.dataset_database["LC"]["K2"]["0"].instrument.name
        number = self.posterior_instance.dataset_database["LC"]["K2"]["0"].number
        path = self.posterior_instance.dataset_database["LC"]["K2"]["0"].filepath
        self.assertEqual("LC", inst_type)
        self.assertEqual("K2", inst_name)
        self.assertEqual(0, number)
        self.assertEqual(file1, path)
        inst_type = (self.posterior_instance.dataset_database["RV"]["SOPHIE-HE"]["0"]
                     .instrument.inst_type)
        inst_name = self.posterior_instance.dataset_database["RV"]["SOPHIE-HE"]["0"].instrument.name
        number = self.posterior_instance.dataset_database["RV"]["SOPHIE-HE"]["0"].number
        path = self.posterior_instance.dataset_database["RV"]["SOPHIE-HE"]["0"].filepath
        self.assertEqual("RV", inst_type)
        self.assertEqual("SOPHIE-HE", inst_name)
        self.assertEqual(0, number)
        self.assertEqual(file2, path)



if __name__ == '__main__':
    unittest.main()
