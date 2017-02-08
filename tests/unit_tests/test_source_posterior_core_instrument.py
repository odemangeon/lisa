#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Unit tests for the source.posterior.core.dataset_and_instrument.instrument module.
"""
import logging
import unittest
import sys

import source.posterior.core.dataset_and_instrument.instrument as inst

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
        pass

    def test_instrument_and_default_instrument(self):
        inst_instance = inst._Default_Instrument(inst_type="LC", name="K2")
        self.assertEqual("LC", inst_instance.inst_type)
        self.assertEqual("K2", inst_instance.name)

    def test_create_model_instance_without_params(self):
        inst_instance = inst._Default_Instrument(inst_type="LC", name="K2")
        inst_model_def = inst_instance.create_model_instance(name="default")
        self.assertEqual(inst_model_def.instrument, inst_instance)
        self.assertEqual(inst_model_def.name, "default")
        self.assertEqual(inst_model_def.full_name, "K2_default")

    def test_create_model_instance_with_params(self):
        inst_instance = inst._Default_Instrument(inst_type="LC", name="K2",
                                                 params_model={"jitter": {"unit": "wo unit"}})
        inst_model_def = inst_instance.create_model_instance(name="default")
        self.assertEqual(inst_model_def.instrument, inst_instance)
        self.assertEqual(inst_instance.full_name, "K2")
        self.assertEqual(inst_model_def.full_name, "K2_default")
        self.assertEqual(inst_model_def.jitter.name, "jitter")
        self.assertEqual(inst_model_def.jitter.full_name, "K2_default_jitter")
        self.assertEqual(inst_model_def.jitter.unit, "wo unit")


if __name__ == '__main__':
    unittest.main()
