#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Unit tests for the source.posterior.core.dataset_and_instrument.dataset module.
"""
import logging
import unittest
import sys

import source.posterior.core.dataset_and_instrument.dataset as dst
from source.posterior.exoplanet.dataset_and_instrument.lc import K2

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
        class _Basic_Dataset(dst.Dataset):
            pass

        self.file_path = "/Users/olivier/Softwares/lisa/data/K2-19/LC_K2-19_K2.txt"
        self.dataset_instance = _Basic_Dataset(self.file_path, K2)

    def test_manage_default_instrument_instance(self):
        filepath = self.dataset_instance.filepath
        self.assertEqual(self.file_path, filepath)
        filename = self.dataset_instance.filename
        self.assertEqual("LC_K2-19_K2.txt", filename)
        objectname = self.dataset_instance.object_name
        self.assertEqual("K2-19", objectname)
        instrument_instance = self.dataset_instance.instrument
        self.assertEqual(K2, instrument_instance)
        self.assertFalse(self.dataset_instance.is_data_stored())
        self.dataset_instance._set_data("some_data")
        dataset_name = self.dataset_instance.dataset_name
        self.assertEqual("LC_K2-19_K2_0", dataset_name)
        data = self.dataset_instance.get_data()
        self.assertTrue(self.dataset_instance.is_data_stored())
        self.assertEqual("some_data", data)
        self.dataset_instance._rm_data()
        self.assertFalse(self.dataset_instance.is_data_stored())
        data = self.dataset_instance.get_data(names=None)
        print(data.info())
        self.assertIsNotNone(data)
        self.assertRaises(NotImplementedError, dst.Dataset, self.file_path, "Instrument_instance")


if __name__ == '__main__':
    unittest.main()
