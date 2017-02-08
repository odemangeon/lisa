#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Unit tests for the source.posterior.core.model.core_model module.
"""
import logging
import unittest
import sys

import source.posterior.core.model.core_model as cmdl

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
        class FakeModel(cmdl.Model):
            """docstring for FakeModel."""
            _model_type = "FakeModel"

            def __init__(self, model_name):
                super(FakeModel, self).__init__(model_name)
        self.fake_modelsubclass = FakeModel

    def test_instrument_and_default_isntrument(self):
        mdl_instance = self.fake_modelsubclass(model_name="test")
        # self.assertEqual("FakeModel", mdl_instance.model_type)
        # self.assertEqual("FakeModel", self.fake_modelsubclass.model_type)
        # self.assertEqual("test", mdl_instance.name)
        # with self.assertRaises(AttributeError):
        #     mdl_instance.name = "test"
        # with self.assertRaises(AttributeError):
        #     mdl_instance.model_type = "test"


if __name__ == '__main__':
    unittest.main()
