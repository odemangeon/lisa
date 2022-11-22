#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Unit tests for the source.posterior.core.dataset_and_instrument.manager_dataset_instrument module.
"""
from unittest import TestCase, main
from logging import getLogger, StreamHandler, Formatter
from logging import DEBUG, INFO
from sys import stdout
import os
import shutil
import importlib
from pprint import pformat

from lisa.posterior.exoplanet.model.gravgroup.model import GravGroup
from lisa.posterior.core.dataset_and_instrument.dataset_database import DatasetDatabase
from lisa.posterior.core.instmodel4dataset import Instmodel4Dataset
from lisa.posterior.core.datasetsfile_db import DatasetsFileDb
from lisa.posterior.core.posterior import Posterior


# from lisa.posterior.exoplanet.model.celestial_bodies import Planet, Star
import lisa.posterior.core.likelihood.core_decorrelation_likelihood
import lisa.posterior.core.model.core_instcat_model
import lisa.posterior.exoplanet.model.gravgroup.LC_instcat_model
import lisa.posterior.exoplanet.likelihood.decorrelation.spline_decorrelation
import lisa.posterior.exoplanet.likelihood.decorrelation.bispline_decorrelation

# import lisa.posterior.exoplanet.model.gravgroup.planetstarmodel_parametrisation

# from lisa.posterior.exoplanet.model.gravgroup.planetstarmodel_parametrisation import OrbitalModels, RVKeplerianModels, TransitModels, OccultationModels, PhaseCurveModels
# from lisa.posterior.exoplanet.model.gravgroup.planetstarmodel import OrbitalModelBatman, RVKeplerianModelRadvel, TransitModelBatman, OccultationModelBatman, PhaseCurveModelSinCos, PhaseCurveModelBeaming, PhaseCurveModelEllipsoidal, PhaseCurveModelLambertian, PhaseCurveModelKelpThermal, PhaseCurveModelSpidermanZhang
# import lisa.posterior.core.dataset_and_instrument.instrument as inst
# from lisa.posterior.exoplanet.dataset_and_instrument.lc import LC_Instrument

# from kelp import Filter, StellarSpectrum

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


def delete_content_folder(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


class TestMethods(TestCase):

    def setUp(self):
        object_name = "WASP-76"
        self.run_folder = "./run_folder_tmp"
        self.post_instance = Posterior(object_name=object_name)
        self.post_instance.dataset_db.data_folder = "./input_files"
        self.post_instance.dataset_db.run_folder = self.run_folder
        self.post_instance.load_datasetsfile(path_datasets_file="./input_files/dataset_decorrelation.txt")
        self.post_instance.define_model(category="GravitionalGroups", stars=1, planets=1)

    def test_get_text_decorrelation_likelihood_model(self):
        delete_content_folder(self.run_folder)
        logger.info("\n\nSTART get_text_4_instcat_param_file")
        self.assertTrue(self.post_instance.model.instcat_models['LC'].decorrelation_likelihood_config == {'do': False, 'order_models': [], 'model_definitions': {}})
        logger.info("Test initialise decorrelation_likelihood_config Done")
        import pdb; pdb.set_trace()
        self.post_instance.model.create_instcat_paramfiles(paramfile_path=None, answer_overwrite="y", answer_create=True)


if __name__ == '__main__':
    # importlib.reload(lisa.posterior.core.likelihood.core_decorrelation_likelihood)
    # importlib.reload(lisa.posterior.core.model.core_instcat_model)
    # importlib.reload(lisa.posterior.exoplanet.model.gravgroup.LC_instcat_model)
    # importlib.reload(lisa.posterior.exoplanet.likelihood.decorrelation.spline_decorrelation)
    # importlib.reload(lisa.posterior.exoplanet.likelihood.decorrelation.bispline_decorrelation)

    main()
