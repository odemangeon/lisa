#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Unit tests for source.posterior.core.model
"""
import logging
import unittest
import sys
# import os

# from unittest.mock import patch

import lisa.posterior.core.model.manager_model as mgr

from lisa.posterior.core.model.core_model import Core_Model

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
        class FakeModel(Core_Model):
            """docstring for FakeModel."""
            __category__ = "FakeModel"

            def __init__(self, model_name="default"):
                super(FakeModel, self).__init__(model_name)
        self.fake_modelsubclass = FakeModel

    def test_manage_model_database(self):
        manager = mgr.Manager_Model()
        manager._reset_models_database()
        list_res = manager.get_available_models()
        logger.info("Available model types: {}".format(list_res))
        self.assertSequenceEqual(list_res, [])
        manager.add_available_model(self.fake_modelsubclass)
        list_res = manager.get_available_models()
        logger.info("Available model types: {}".format(list_res))
        self.assertSequenceEqual(list_res, ["FakeModel", ])
        self.assertTrue(manager.is_available_modeltype(category="FakeModel"))
        model_subclass = manager.get_model_subclass(category="FakeModel")
        self.assertEqual(model_subclass, self.fake_modelsubclass)
        self.assertFalse(manager.is_available_modeltype(category="Truc"))
        manager._reset_models_database()
        list_res = manager.get_available_models()
        logger.info("Available model types: {}".format(list_res))
        self.assertSequenceEqual(list_res, [])


if __name__ == '__main__':
    unittest.main()
