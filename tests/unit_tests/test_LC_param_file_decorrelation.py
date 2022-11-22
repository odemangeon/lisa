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
        os.makedirs(self.run_folder, exist_ok=True)
        delete_content_folder(self.run_folder)
        self.post_instance = Posterior(object_name=object_name)
        self.post_instance.dataset_db.data_folder = "./input_files"
        self.post_instance.run_folder = self.run_folder
        self.post_instance.load_datasetsfile(path_datasets_file="./input_files/dataset_decorrelation.txt")
        self.post_instance.define_model(category="GravitionalGroups", stars=1, planets=1)
        self.LC_instcat_model = self.post_instance.model.instcat_models['LC']
        print(self.post_instance.model.dataset_db)

    def test_get_and_set_decorrelation_likelihood_model_config(self):
        logger.info("\n\nSTART test_get_and_set_decorrelation_likelihood_model_config")
        self.assertTrue(self.LC_instcat_model.decorrelation_likelihood_config == {'do': False, 'order_models': [], 'model_definitions': {}})
        logger.info("Initialise decorrelation_likelihood_config Done")
        self.post_instance.model.create_instcat_paramfiles(paramfile_path=None, answer_overwrite='y', answer_create='create')
        logger.info("Create LC_param_file (and IND_param_file) Done")
        dico_config_decorr_like = {self.LC_instcat_model._decorr_likelihood_dict_name: {'do': True,
                                                                                        'order_models': ['ROLL', 'XY'],
                                                                                        'model_definitions': {'ROLL': {'category': 'spline',
                                                                                                                       'spline_type': 'UnivariateSpline',
                                                                                                                       'spline_kwargs': {'k': 3},
                                                                                                                       'match datasets': {'LC_WASP-76_CHEOPS_100': 'IND-ROLL_WASP-76_CHEOPS_100'}
                                                                                                                       },
                                                                                                              'XY': {'category': 'bispline',
                                                                                                                     'spline_type': 'SmoothBivariateSpline',
                                                                                                                     'spline_kwargs': {'kx': 3, 'ky': 3},
                                                                                                                     'match datasets': {'LC_WASP-76_CHEOPS_100': {'X': 'IND-CX_WASP-76_CHEOPS_100',
                                                                                                                                                                  'Y': 'IND-CY_WASP-76_CHEOPS_100',
                                                                                                                                                                  }
                                                                                                                                        }
                                                                                                                     }
                                                                                                              }
                                                                                        }
                                   }
        self.LC_instcat_model.load_config_decorrelation_likelihood(dico_config=dico_config_decorr_like)
        logger.info("Run load_config_decorrelation_likelihood without error Done")
        self.assertTrue(self.LC_instcat_model.decorrelation_likelihood_config == dico_config_decorr_like[self.LC_instcat_model._decorr_likelihood_dict_name])
        logger.info("Run load_config_decorrelation_likelihood successfully Done")
        logger.info("\n\nFINISHED test_get_and_set_decorrelation_likelihood_model_config")


if __name__ == '__main__':
    # importlib.reload(lisa.posterior.core.likelihood.core_decorrelation_likelihood)
    # importlib.reload(lisa.posterior.core.model.core_instcat_model)
    # importlib.reload(lisa.posterior.exoplanet.model.gravgroup.LC_instcat_model)
    # importlib.reload(lisa.posterior.exoplanet.likelihood.decorrelation.spline_decorrelation)
    # importlib.reload(lisa.posterior.exoplanet.likelihood.decorrelation.bispline_decorrelation)

    main()
