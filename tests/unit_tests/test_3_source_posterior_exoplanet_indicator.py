#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Unit tests for the source.posterior.core.dataset_and_instrument.manager_dataset_instrument module.
"""
import pathlib

from unittest import TestCase, main
from logging import getLogger, StreamHandler, Formatter
from logging import DEBUG, INFO
from sys import stdout
from os.path import join

from lisa.posterior.core.posterior import Posterior
# from lisa.posterior.exoplanet.model.indicator_model import Posterior

# import lisa.posterior.core.dataset_and_instrument.instrument as inst
# from lisa.posterior.exoplanet.dataset_and_instrument.lc import LC_Instrument

level_logger = DEBUG
level_handler = INFO

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
        self.obj_name = "TESTOBJ"
        self.input_files_folder = "input_files"
        self.cwd = pathlib.Path(__file__).parent.absolute()
        self.post_instance = Posterior(object_name=self.obj_name)
        self.post_instance.dataset_db.data_folder = join(self.cwd, self.input_files_folder)
        self.post_instance.load_datasetsfile(join(self.cwd, join(self.input_files_folder, "dataset_indicators.txt")))
        self.post_instance.define_model(category="GravitionalGroups", name=self.obj_name, stars=1, planets=1)

    def test_default_properties(self):
        logger.info("Beginning of test default_properties")
        self.assertDictEqual(self.post_instance.model.model_4_indicator, {"FWHM": "polynomial"})
        self.assertFalse(self.post_instance.model.isdefined_INDparamfile)
        self.assertSequenceEqual(self.post_instance.model.indicator_fullcategories, ["IND-FWHM", ])
        self.assertSequenceEqual(self.post_instance.model.indicator_subcategories, ["FWHM", ])
        self.assertFalse(self.post_instance.model.is_valid_indicator_model("bla"))
        self.assertTrue(self.post_instance.model.is_valid_indicator_model("polynomial"))
        self.assertSequenceEqual(self.post_instance.model.available_models_4_indicators, ["polynomial", ])
        self.assertDictEqual(self.post_instance.model.indicator_subcategories_4_model_used, {"polynomial": ["FWHM", ]})
        self.assertSequenceEqual(self.post_instance.model.indicator_models_used, ["polynomial", ])
        self.assertDictEqual(self.post_instance.model.params_indicator_models, {"polynomial": {"FWHM": {"order": 0}}})


if __name__ == '__main__':
    main()
