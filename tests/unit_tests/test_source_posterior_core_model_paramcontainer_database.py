#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Unit tests for the source.posterior.core.model.paramcontainer_database module.
"""
from logging import getLogger, StreamHandler, Formatter, DEBUG, INFO
from unittest import TestCase, main
from sys import stdout

from source.posterior.core.model.paramcontainers_database import ParamContainerDatabase
from source.posterior.exoplanet.model.celestial_bodies import Planet, Star
from source.posterior.exoplanet.dataset_and_instrument.rv import HARPS, SOPHIE_HE
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


class TestMethods(TestCase):

    def setUp(self):
        # Check the handler level
        ch = logger.handlers[0]
        if ch.level != ch_level:
            ch.setLevel(ch_level)
        # test set up
        parcont_db = ParamContainerDatabase()
        star_A = Star(name="A")
        planet_b = Planet(name="b")
        planet_c = Planet(name="c")
        parcont_db.add_a_paramcontainer(star_A)
        parcont_db.add_a_paramcontainer(planet_b)
        parcont_db.add_a_paramcontainer(planet_c)
        self.parcont_db = parcont_db
        self.star_A = star_A
        self.planet_b = planet_b

    def test_operations_standardparamcontainers(self):
        self.assertCountEqual(self.parcont_db.paramcont_categories,
                              [instrument_model_category, self.star_A.category,
                               self.planet_b.category])
        self.assertDictEqual(self.parcont_db.nb_of_paramcontainers, {instrument_model_category: 0,
                                                                     self.star_A.category: 1,
                                                                     self.planet_b.category: 2})
        self.parcont_db.rm_paramcontainer(self.star_A.name, self.star_A.category)
        self.assertCountEqual(self.parcont_db.paramcont_categories,
                              [instrument_model_category, self.planet_b.category])
        self.assertDictEqual(self.parcont_db.nb_of_paramcontainers, {instrument_model_category: 0,
                                                                     self.planet_b.category: 2})
        self.assertTrue(self.parcont_db.isavailable_paramcontainer(self.planet_b.name,
                                                                   self.planet_b.category))
        self.assertFalse(self.parcont_db.isavailable_paramcontainer(self.star_A.name,
                                                                    self.star_A.category))

    def test_operations_instrumentparamcontainers(self):
        self.parcont_db.add_an_instrument_model(instrument=HARPS, name="default")
        self.parcont_db.add_an_instrument_model(instrument=HARPS, name="default1")
        self.parcont_db.add_an_instrument_model(instrument=SOPHIE_HE, name="default")
        self.assertCountEqual(self.parcont_db.paramcont_categories,
                              [self.star_A.category, self.planet_b.category,
                               instrument_model_category])
        print(self.parcont_db.nb_of_paramcontainers)
        print(self.parcont_db.instruments)


if __name__ == '__main__':
    main()
