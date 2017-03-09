#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Unit tests for the source.posterior.core.model.core_model module.
"""
from logging import getLogger, StreamHandler, Formatter, DEBUG, INFO
from unittest import TestCase, main
from sys import stdout

import source.posterior.core.model.core_model as cmdl
from source.posterior.exoplanet.model.celestial_bodies import Star, Planet
from source.posterior.core.prior.manager_prior import Manager_Prior
from source.posterior.core.dataset_and_instrument.dataset_database import DatasetDatabase
from source.posterior.core.dataset_and_instrument.instrument import instrument_model_category


log_level = DEBUG
ch_level = INFO

logger = getLogger()
if logger.level != log_level:
    logger.setLevel(log_level)
if len(logger.handlers) == 0:
    ch = StreamHandler(stdout)
    ch.setLevel(ch_level)
    formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
else:
    ch = logger.handlers[0]
    if ch.level != ch_level:
        ch.setLevel(ch_level)


class TestMethods(TestCase):

    def setUp(self):
        class FakeModel(cmdl.Core_Model):
            """docstring for FakeModel."""
            __category__ = "FakeModel"

            def __init__(self, model_name, dataset_db):
                super(FakeModel, self).__init__(model_name, dataset_db)
        self.fake_modelsubclass = FakeModel

        manager = Manager_Prior()
        manager.load_setup()
        print(manager.get_available_priors())

    def test_basics(self):
        mdl_instance = self.fake_modelsubclass(model_name="test",
                                               dataset_db=DatasetDatabase("test"))
        self.assertEqual("FakeModel", mdl_instance.category)
        self.assertEqual("FakeModel", self.fake_modelsubclass.category)
        self.assertEqual("test", mdl_instance.name)
        with self.assertRaises(AttributeError):
            mdl_instance.name = "test"
        with self.assertRaises(AttributeError):
            mdl_instance.category = "test"

    def test_manage_paramcontainers(self):
        mdl_instance = self.fake_modelsubclass(model_name="test",
                                               dataset_db=DatasetDatabase("test"))
        mdl_instance.add_a_paramcontainer(Star(name="A"))
        mdl_instance.add_a_paramcontainer(Planet(name="b"))
        mdl_instance.add_a_paramcontainer(Planet(name="c"))
        self.assertTrue(mdl_instance.isavailable_paramcontainer(name="A", category="stars"))
        self.assertTrue(mdl_instance.isavailable_paramcontainer(name="b", category="planets"))
        self.assertTrue(mdl_instance.isavailable_paramcontainer(name="c", category="planets"))
        self.assertDictEqual(mdl_instance.nb_of_paramcontainers, {instrument_model_category: 0,
                                                                  "stars": 1, "planets": 2})
        mdl_instance.rm_paramcontainer(name="c", category="planets")
        self.assertFalse(mdl_instance.isavailable_paramcontainer(name="c", category="planets"))
        self.assertDictEqual(mdl_instance.nb_of_paramcontainers, {instrument_model_category: 0,
                                                                  "stars": 1, "planets": 1})


if __name__ == '__main__':
    main()
