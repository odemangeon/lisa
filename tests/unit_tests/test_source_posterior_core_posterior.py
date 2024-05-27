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

import lisa.posterior.core.posterior as pst

from lisa.setup import input_data_folder
from lisa.posterior.core.dataset_and_instrument.manager_dataset_instrument import \
    Manager_Inst_Dataset
from lisa.posterior.core.model.core_model import Core_Model
import lisa.posterior.exoplanet.dataset_and_instrument.lc as lc
import lisa.posterior.exoplanet.dataset_and_instrument.rv as rv
from lisa.posterior.core.dataset_and_instrument.dataset_database import DatasetDatabase
from lisa.posterior.core.likelihood.gaussian_noisemodelconfiguration import GaussianNoiseModel

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
        self.manager_dataset = Manager_Inst_Dataset()
        self.manager_dataset.add_available_inst_category(lc.LC_Instrument, lc.LC_Dataset)
        self.manager_dataset.add_available_inst(lc.K2)
        self.manager_dataset.add_available_inst_category(rv.RV_Instrument, rv.RV_Dataset)
        self.manager_dataset.add_available_inst(rv.SOPHIE_HE)
        self.test_datafile = "LC_K2-19_K2.txt"

        class FakeModel(Core_Model):
            """docstring for FakeModel."""
            __category__ = "FakeModel"

            def __init__(self, name="default", dataset_db=None, run_folder=None,
                         instmodel4dataset=None, l_instmod_fullnames=None, lock=None):
                super(FakeModel, self).__init__(name, dataset_db, run_folder,
                                                instmodel4dataset=instmodel4dataset)

    def test_object_name(self):
        self.assertEqual(self.posterior_instance.object_name, "K2-29")
        with self.assertRaises(AttributeError):
            self.posterior_instance.object_name = "K2-28"

    def test_datafolder_isset(self):
        self.assertFalse(self.posterior_instance.dataset_db.hasdata_folder)

    @patch('source.tools.miscellaneous.QCM_utilisateur', return_value="y")
    def test_set_custom_datafolder_answer_yes(self, input):
        path = "testposteriordatafolder"
        self.posterior_instance.dataset_db.data_folder = path
        self.assertEqual(self.posterior_instance.dataset_db.data_folder, path)
        os.rmdir(path)

    @patch('source.tools.miscellaneous.QCM_utilisateur', return_value="n")
    def test_set_custom_datafolder_answer_no(self, input):
        path = "testposteriordatafolder"
        self.posterior_instance.dataset_db.data_folder = path
        self.assertFalse(self.posterior_instance.dataset_db.hasdata_folder)

    def test_set_custom_datafolder_alreadyexists(self):
        path = "testposteriordatafolder"
        os.makedirs(path)
        self.posterior_instance.dataset_db.data_folder = path
        self.assertEqual(self.posterior_instance.dataset_db.data_folder, path)
        os.rmdir(path)

    @patch('source.tools.miscellaneous.QCM_utilisateur', return_value="y")
    def test_set_default_datafolder_answer_yes(self, input):
        path = os.path.join(input_data_folder, "test")
        self.posterior_instance_test.dataset_db.data_folder = "default"
        self.assertEqual(self.posterior_instance_test.dataset_db.data_folder, path)
        os.rmdir(path)

    @patch('source.tools.miscellaneous.QCM_utilisateur', return_value="n")
    def test_set_default_datafolder_answer_no(self, input):
        self.posterior_instance_test.data_folder = "default"
        self.assertFalse(self.posterior_instance_test.dataset_db.hasdata_folder)

    def test_set_default_datafolder_alreadyexists(self):
        path = os.path.join(input_data_folder, "test")
        os.makedirs(path)
        self.posterior_instance_test.data_folder = path
        self.assertEqual(self.posterior_instance_test.data_folder, path)
        os.rmdir(path)

    def test_manage_basic_operation_of_dataset_database(self):
        self.assertTrue(isinstance(self.posterior_instance.dataset_db, DatasetDatabase))
        self.assertCountEqual(self.posterior_instance.dataset_db, {})
        with self.assertRaises(Warning):
            self.posterior_instance.dataset_db = {"a": {}}
        if os.path.isfile(self.test_datafile):
            raise ValueError("The file {} already exists. the unit test can't be performed or it "
                             "will damage it. Change current directory.".format(self.test_datafile))
        open(self.test_datafile, "x").close()
        dataset = self.manager_dataset.create_dataset(self.test_datafile)
        os.remove(self.test_datafile)
        self.posterior_instance.dataset_db._add_a_dataset(dataset)
        dataset_returned = self.posterior_instance.dataset_db["LC"]["K2"][0]
        self.assertEqual(dataset, dataset_returned)
        self.posterior_instance.dataset_db.rm_dataset("LC", "K2")
        self.assertCountEqual(self.posterior_instance.dataset_db, {})

    def test_add_a_dataset_from_path(self):
        open(self.test_datafile, "x").close()
        (self.posterior_instance.dataset_db.
         _add_a_dataset_from_path(datafile_path=self.test_datafile))
        os.remove(self.test_datafile)
        inst_category = self.posterior_instance.dataset_db["LC"]["K2"]["0"].instrument.category
        inst_name = self.posterior_instance.dataset_db["LC"]["K2"]["0"].instrument.get_name()
        number = self.posterior_instance.dataset_db["LC"]["K2"]["0"].number
        path = self.posterior_instance.dataset_db["LC"]["K2"]["0"].filepath
        self.assertEqual("LC", inst_category)
        self.assertEqual("K2", inst_name)
        self.assertEqual(0, number)
        self.assertEqual(self.test_datafile, path)

    def test_add_a_dataset_from_datasetsfile_and_get_instrument_categories(self):
        file1 = "LC_K2-29_K2.txt"
        line1 = "{}  default  {}".format(file1, GaussianNoiseModel.category)
        file2 = "RV_K2-29_SOPHIE-HE.txt"
        line2 = "{}  default  {}".format(file2, GaussianNoiseModel.category)
        dataset_file = "test_datasetfile.txt"
        open(file1, "x").close()
        open(file2, "x").close()
        with open(dataset_file, "x") as f:
            f.write(line1 + "\n")
            f.write(line2 + "\n")
        self.posterior_instance.load_datasetsfile(path_datasets_file=dataset_file)
        os.remove(file1)
        os.remove(file2)
        os.remove(dataset_file)
        inst_category = self.posterior_instance.dataset_db["LC"]["K2"]["0"].instrument.category
        inst_name = self.posterior_instance.dataset_db["LC"]["K2"]["0"].instrument.get_name()
        number = self.posterior_instance.dataset_db["LC"]["K2"]["0"].number
        path = self.posterior_instance.dataset_db["LC"]["K2"]["0"].filepath
        self.assertEqual("LC", inst_category)
        self.assertEqual("K2", inst_name)
        self.assertEqual(0, number)
        self.assertEqual(file1, path)
        inst_category = (self.posterior_instance.dataset_db["RV"]["SOPHIE-HE"]["0"]
                         .instrument.category)
        inst_name = self.posterior_instance.dataset_db["RV"]["SOPHIE-HE"]["0"].instrument.get_name()
        number = self.posterior_instance.dataset_db["RV"]["SOPHIE-HE"]["0"].number
        path = self.posterior_instance.dataset_db["RV"]["SOPHIE-HE"]["0"].filepath
        self.assertEqual("RV", inst_category)
        self.assertEqual("SOPHIE-HE", inst_name)
        self.assertEqual(0, number)
        self.assertEqual(file2, path)
        self.assertCountEqual(["LC", "RV"],
                              self.posterior_instance.dataset_db.inst_categories)

    def test_model_operations(self):
        with self.assertRaises(AttributeError):
            self.posterior_instance.model = "K2-28"
        self.posterior_instance.rm_model()
        self.assertFalse(self.posterior_instance.isdefined_model)
        self.posterior_instance.define_model(category="FakeModel", name="test")
        self.assertTrue(self.posterior_instance.isdefined_model)
        self.posterior_instance.rm_model()
        self.assertFalse(self.posterior_instance.isdefined_model)


if __name__ == '__main__':
    unittest.main()
