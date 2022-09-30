#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Unit tests for the source.posterior.core.dataset_and_instrument.manager_dataset_instrument module.
"""
from unittest import TestCase, main
from logging import getLogger, StreamHandler, Formatter
from logging import DEBUG, INFO
from sys import stdout
import importlib

from lisa.posterior.exoplanet.model.celestial_bodies import Planet, Star

import lisa.posterior.exoplanet.model.gravgroup.planetstarmodel
import lisa.posterior.exoplanet.model.gravgroup.planetstarmodel_parametrisation

from lisa.posterior.exoplanet.model.gravgroup.planetstarmodel_parametrisation import OrbitalModels, RVKeplerianModels, TransitModels, OccultationModels, PhaseCurveModels
from lisa.posterior.exoplanet.model.gravgroup.planetstarmodel import OrbitalModelBatman, RVKeplerianModelRadvel, TransitModelBatman, OccultationModelBatman, PhaseCurveModelSinCos, PhaseCurveModelBeaming, PhaseCurveModelEllipsoidal, PhaseCurveModelLambertian, PhaseCurveModelKelpThermal, PhaseCurveModelSpidermanZhang
# import lisa.posterior.core.dataset_and_instrument.instrument as inst
# from lisa.posterior.exoplanet.dataset_and_instrument.lc import LC_Instrument

from kelp import Filter, StellarSpectrum


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
        self.l_planet = [Planet(name="b"), Planet(name="c")]
        self.host_star = Star(name="A")
        self.l_inst_model_fullname = ['LC_CHEOPS_inst0', 'LC_CHEOPS_inst1', 'RV_ESPRESSO_inst', 'RV_ESPRESSO_inst1']
        self.l_inst_model_fullname_rv = ['RV_ESPRESSO_inst', 'RV_ESPRESSO_inst1', ]
        self.l_inst_model_fullname_tr = ['LC_CHEOPS_inst0', 'LC_CHEOPS_inst1', ]
        self.dico_config_orbital_models = {'b': {'do': True,
                                                 'model4instrument': {'LC_CHEOPS_inst0': '',
                                                                      'LC_CHEOPS_inst1': '1',
                                                                      'RV_ESPRESSO_inst': '',
                                                                      'RV_ESPRESSO_inst1': '1'
                                                                      },
                                                 'model_definitions': {'': {'category': 'batman',
                                                                            'param_extensions': {'planet': {'P': '',
                                                                                                            'cosinc': '',
                                                                                                            'ecosw': '',
                                                                                                            'esinw': '',
                                                                                                            'tic': ''},
                                                                                                 'star': {'rho': ''}},
                                                                            'parametrisation': {'ew_format': 'ecosw-esinw',
                                                                                                'inc_format': 'cosinc',
                                                                                                'use_aR': False,
                                                                                                'use_tic': True}},
                                                                       '1': {'category': 'batman',
                                                                             'param_extensions': {'planet': {'P': '',
                                                                                                             'cosinc': '',
                                                                                                             'ecosw': '',
                                                                                                             'esinw': '',
                                                                                                             'tic': '1',
                                                                                                             'aR': ''},
                                                                                                  'star': {}},
                                                                             'parametrisation': {'ew_format': 'ecosw-esinw',
                                                                                                 'inc_format': 'cosinc',
                                                                                                 'use_aR': True,
                                                                                                 'use_tic': True}},
                                                                       }
                                                 },
                                           'c': {'do': True,
                                                 'model4instrument': {'LC_CHEOPS_inst0': '',
                                                                      'LC_CHEOPS_inst1': '',
                                                                      'RV_ESPRESSO_inst': '',
                                                                      'RV_ESPRESSO_inst1': ''},
                                                 'model_definitions': {'': {'category': 'batman',
                                                                            'param_extensions': {'planet': {'P': '',
                                                                                                            'cosinc': '',
                                                                                                            'ecosw': '',
                                                                                                            'esinw': '',
                                                                                                            'tic': ''},
                                                                                                 'star': {'rho': ''}},
                                                                            'parametrisation': {'ew_format': 'ecosw-esinw',
                                                                                                'inc_format': 'cosinc',
                                                                                                'use_aR': False,
                                                                                                'use_tic': True}}}}}

        self.dico_config_rvkeplerian_models = {'b': {'do': True,
                                                     'model': {'category': 'radvel',
                                                               'param_extensions': {'planet': {'K': '1'}, 'star': {}}}},
                                               'c': {'do': True,
                                                     'model': {'category': 'radvel',
                                                               'param_extensions': {'planet': {'K': ''}, 'star': {}}}}}

        self.dico_config_transit_models = {'b': {'do': True,
                                                 'model4instrument': {'LC_CHEOPS_inst0': '', 'LC_CHEOPS_inst1': '1'},
                                                 'model_definitions': {'': {'category': 'batman',
                                                                            'param_extensions': {'planet': {'Rrat': ''},
                                                                                                 'star': {}
                                                                                                 }
                                                                            },
                                                                       '1': {'category': 'batman',
                                                                             'param_extensions': {'planet': {'Rrat': '1'},
                                                                                                  'star': {}
                                                                                                  }
                                                                             }
                                                                       }
                                                 },
                                           'c': {'do': True,
                                                 'model4instrument': {'LC_CHEOPS_inst0': '', 'LC_CHEOPS_inst1': ''},
                                                 'model_definitions': {'': {'category': 'batman',
                                                                            'param_extensions': {'planet': {'Rrat': ''},
                                                                                                 'star': {}}}}}}

        self.dico_config_occultation_models = {'b': {'do': True,
                                                     'model4instrument': {'LC_CHEOPS_inst0': '', 'LC_CHEOPS_inst1': '1'},
                                                     'model_definitions': {'': {'category': 'batman',
                                                                                'param_extensions': {'planet': {'Frat': '', 'Rrat': ''},
                                                                                                     'star': {}
                                                                                                     }
                                                                                },
                                                                           '1': {'category': 'batman',
                                                                                 'param_extensions': {'planet': {'Frat': '1', 'Rrat': '1'},
                                                                                                      'star': {}
                                                                                                      }
                                                                                 }
                                                                           }
                                                     },
                                               'c': {'do': True,
                                                     'model4instrument': {'LC_CHEOPS_inst0': '', 'LC_CHEOPS_inst1': ''},
                                                     'model_definitions': {'': {'category': 'batman',
                                                                                'param_extensions': {'planet': {'Rrat': ''},
                                                                                                     'star': {}}}}}}

        filt = Filter.from_name("IRAC 2")
        filt.bin_down(10)  # this speeds up the integration
        T_s = 6331
        stellar_spectrum = StellarSpectrum.from_phoenix(T_s=T_s, log_g=4.5, cache=True)
        self.dico_config_phasecurve_models = {'b': {'do': True,
                                                    'model4instrument': {'LC_CHEOPS_inst0': ['', '1'], 'LC_CHEOPS_inst1': ['']},
                                                    'model_definitions': {'': {'category': 'lambertian',
                                                                               'param_extensions': {'planet': {'A': ''},
                                                                                                    'star': {}
                                                                                                    }
                                                                               },
                                                                          '1': {'category': 'kelp-thermal',
                                                                                'args': {'Model_kwargs': {'lmax': 1, 'filt': filt, 'stellar_spectrum': stellar_spectrum, 'T_s': 6331},
                                                                                         'brightness_model_kwargs': {'n_theta': 20, 'n_phi': 200, 'cython': True, 'quad': False, 'check_sorted': True},
                                                                                         },
                                                                                'param_extensions': {'planet': {'Rrat': '1', },
                                                                                                     'star': {}
                                                                                                     }
                                                                                },
                                                                          }
                                                    },
                                              'c': {'do': True,
                                                    'model4instrument': {'LC_CHEOPS_inst0': ['', '1'], 'LC_CHEOPS_inst1': ['']},
                                                    'model_definitions': {'': {'args': {'factor_period': 1,
                                                                                        'flux_offset': 'param',
                                                                                        'occultation': True,
                                                                                        'phase_offset': 'param',
                                                                                        'sincos': 'cos'},
                                                                               'category': 'sincos',
                                                                               'param_extensions': {'planet': {'A': '',
                                                                                                               'Foffset': '',
                                                                                                               'Phi': ''},
                                                                                                    'star': {}
                                                                                                    }
                                                                               },
                                                                          '1': {'args': {'factor_period': 1 / 2,
                                                                                         'flux_offset': 'param',
                                                                                         'occultation': True,
                                                                                         'phase_offset': 'param',
                                                                                         'sincos': 'sin'},
                                                                                'category': 'sincos',
                                                                                'param_extensions': {'planet': {'A': '1',
                                                                                                                'Foffset': '',
                                                                                                                'Phi': ''},
                                                                                                     'star': {}
                                                                                                     }
                                                                                }
                                                                          }
                                                    }
                                              }

    def test_orbital_model(self):
        logger.info("\n\nSTART test_orbital_models")
        orbital_models = OrbitalModels(l_planet=self.l_planet, host_star=self.host_star,
                                       l_inst_model_fullname=self.l_inst_model_fullname
                                       )
        logger.info("test_creation_done")
        print(f"orbital_models.__repr__ = {orbital_models!r}")
        print(f"orbital_models = {orbital_models}")
        logger.info("Check of the __repr__ and __str__ done")
        self.assertTrue(orbital_models.get_do(planet_name="b"))
        self.assertTrue(orbital_models.get_do(planet_name="c"))
        logger.info("Check of the get_do done.")
        self.assertTrue(isinstance(orbital_models.get_model(planet_name="b", inst_model_fullname='LC_CHEOPS_inst0'), OrbitalModelBatman))
        self.assertTrue(isinstance(orbital_models.get_model(planet_name="c", inst_model_fullname='RV_ESPRESSO_inst1'), OrbitalModelBatman))
        logger.info("Check of the get_models done.")
        orbital_model_planetb = orbital_models.get_model(planet_name="b", inst_model_fullname='LC_CHEOPS_inst0')
        orbital_model_planetb.create_parameters_and_set_main(inst_model_fullname='LC_CHEOPS_inst0')
        orbital_model_planetc = orbital_models.get_model(planet_name="c", inst_model_fullname='LC_CHEOPS_inst0')
        orbital_model_planetc.create_parameters_and_set_main(inst_model_fullname='LC_CHEOPS_inst0')
        logger.info("Check of that create_parameters_and_set_main runs without error done.")
        self.assertTrue(self.host_star.rho.main)
        logger.info("Check that the param are main for the star model OrbitalModelBatman param use_aR False Done.")
        for i_planet in range(len(self.l_planet)):
            self.assertTrue(self.l_planet[i_planet].P.main)
            self.assertTrue(self.l_planet[i_planet].tic.main)
            self.assertTrue(self.l_planet[i_planet].ecosw.main)
            self.assertTrue(self.l_planet[i_planet].esinw.main)
            self.assertTrue(self.l_planet[i_planet].cosinc.main)
            logger.info(f"Check that the param are main for the planet {i_planet} model OrbitalModelBatman param use_aR False Done.")
        orbital_models.load_config(dico_config=self.dico_config_orbital_models)
        logger.info("Check the load_config function runs without error Done.")
        orbital_model_planetb1 = orbital_models.get_model(planet_name="b", inst_model_fullname='LC_CHEOPS_inst1')
        orbital_model_planetb1.create_parameters_and_set_main(inst_model_fullname='LC_CHEOPS_inst1')
        orbital_model_planetc1 = orbital_models.get_model(planet_name="c", inst_model_fullname='LC_CHEOPS_inst1')
        orbital_model_planetc1.create_parameters_and_set_main(inst_model_fullname='LC_CHEOPS_inst1')
        self.assertTrue(self.l_planet[0].P.main)
        self.assertTrue(self.l_planet[0].tic1.main)
        self.assertTrue(self.l_planet[0].ecosw.main)
        self.assertTrue(self.l_planet[0].esinw.main)
        self.assertTrue(self.l_planet[0].cosinc.main)
        self.assertTrue(self.l_planet[0].aR.main)
        logger.info(f"Check that the param are main for the planet {i_planet} model OrbitalModelBatman param use_aR True Done.")

    def test_keplerian_models(self):
        logger.info("\n\nSTART test_keplerian_models")
        orbital_models = OrbitalModels(l_planet=self.l_planet, host_star=self.host_star,
                                       l_inst_model_fullname=self.l_inst_model_fullname
                                       )
        orbital_models.load_config(dico_config=self.dico_config_orbital_models)
        keplerian_models = RVKeplerianModels(l_planet=self.l_planet, host_star=self.host_star, orbital_models=orbital_models)
        logger.info("test_creation_done")
        print(f"keplerian_models.__repr__ = {keplerian_models!r}")
        print(f"keplerian_models = {keplerian_models}")
        logger.info("Check of the __repr__ and __str__ done")
        self.assertTrue(keplerian_models.get_do(planet_name="b"))
        self.assertTrue(keplerian_models.get_do(planet_name="c"))
        logger.info("Check of the get_do done.")
        self.assertTrue(isinstance(keplerian_models.get_model(planet_name="b"), RVKeplerianModelRadvel))
        self.assertTrue(isinstance(keplerian_models.get_model(planet_name="c"), RVKeplerianModelRadvel))
        self.assertNotEqual(keplerian_models.get_model(planet_name="b"), keplerian_models.get_model(planet_name="c"))
        logger.info("Check of the get_models done.")
        keplerian_model_planetb = keplerian_models.get_model(planet_name="b")
        keplerian_model_planetb.create_parameters_and_set_main(inst_model_fullname='RV_ESPRESSO_inst')
        keplerian_model_planetb.create_parameters_and_set_main(inst_model_fullname='RV_ESPRESSO_inst1')
        keplerian_model_planetc = keplerian_models.get_model(planet_name="c")
        keplerian_model_planetc.create_parameters_and_set_main(inst_model_fullname='RV_ESPRESSO_inst')
        keplerian_model_planetc.create_parameters_and_set_main(inst_model_fullname='RV_ESPRESSO_inst1')
        logger.info("Check of that create_parameters_and_set_main runs without error done.")
        self.assertFalse(self.host_star.rho.main)  # aR or rho is not required by RV
        logger.info("Check that the param are main for the star model RVKeplerianModelRadvel Done.")
        self.assertTrue(self.l_planet[0].K.main)
        self.assertTrue(self.l_planet[0].P.main)
        self.assertTrue(self.l_planet[0].tic.main)
        self.assertTrue(self.l_planet[0].tic1.main)
        self.assertTrue(self.l_planet[0].ecosw.main)
        self.assertTrue(self.l_planet[0].esinw.main)
        self.assertFalse(self.l_planet[0].cosinc.main)
        logger.info(f"Check that the param are main for the planet {0} model RVKeplerianModelRadvel Done.")
        self.assertTrue(self.l_planet[1].K.main)
        self.assertTrue(self.l_planet[1].P.main)
        self.assertTrue(self.l_planet[1].tic.main)
        self.assertTrue(self.l_planet[1].ecosw.main)
        self.assertTrue(self.l_planet[1].esinw.main)
        self.assertFalse(self.l_planet[1].cosinc.main)
        logger.info(f"Check that the param are main for the planet {1} model RVKeplerianModelRadvel Done.")
        keplerian_models.load_config(dico_config=self.dico_config_rvkeplerian_models)
        keplerian_model_planetb = keplerian_models.get_model(planet_name="b")
        keplerian_model_planetb.create_parameters_and_set_main(inst_model_fullname='RV_ESPRESSO_inst')
        keplerian_model_planetb.create_parameters_and_set_main(inst_model_fullname='RV_ESPRESSO_inst1')
        keplerian_model_planetc = keplerian_models.get_model(planet_name="c")
        keplerian_model_planetc.create_parameters_and_set_main(inst_model_fullname='RV_ESPRESSO_inst')
        keplerian_model_planetc.create_parameters_and_set_main(inst_model_fullname='RV_ESPRESSO_inst1')
        logger.info("Check the load_config function runs without error Done.")
        self.assertTrue(self.l_planet[0].K1.main)
        self.assertTrue(self.l_planet[0].P.main)
        self.assertTrue(self.l_planet[0].tic.main)
        self.assertTrue(self.l_planet[0].tic1.main)
        self.assertTrue(self.l_planet[0].ecosw.main)
        self.assertTrue(self.l_planet[0].esinw.main)
        self.assertFalse(self.l_planet[0].cosinc.main)
        logger.info(f"Check that the param are main for the planet {0} model RVKeplerianModelRadvel after load_config Done.")
        self.assertTrue(self.l_planet[1].K.main)
        self.assertTrue(self.l_planet[1].P.main)
        self.assertTrue(self.l_planet[1].tic.main)
        self.assertTrue(self.l_planet[1].ecosw.main)
        self.assertTrue(self.l_planet[1].esinw.main)
        self.assertFalse(self.l_planet[1].cosinc.main)
        logger.info(f"Check that the param are main for the planet {1} model RVKeplerianModelRadvel after load_config Done.")

    def test_transit_models(self):
        logger.info("\n\nSTART test_transit_models")
        orbital_models = OrbitalModels(l_planet=self.l_planet, host_star=self.host_star,
                                       l_inst_model_fullname=self.l_inst_model_fullname
                                       )
        orbital_models.load_config(dico_config=self.dico_config_orbital_models)
        transit_models = TransitModels(l_planet=self.l_planet, host_star=self.host_star, l_inst_model_fullname=self.l_inst_model_fullname_tr,
                                       orbital_models=orbital_models
                                       )
        logger.info("test_creation_done")
        print(f"transit_models.__repr__ = {transit_models!r}")
        print(f"transit_models = {transit_models}")
        logger.info("Check of the __repr__ and __str__ done")
        self.assertTrue(transit_models.get_do(planet_name="b"))
        self.assertTrue(transit_models.get_do(planet_name="c"))
        logger.info("Check of the get_do done.")
        self.assertTrue(isinstance(transit_models.get_model(planet_name="b", inst_model_fullname="LC_CHEOPS_inst0"), TransitModelBatman))
        self.assertTrue(isinstance(transit_models.get_model(planet_name="c", inst_model_fullname="LC_CHEOPS_inst1"), TransitModelBatman))
        self.assertEqual(transit_models.get_model(planet_name="b", inst_model_fullname="LC_CHEOPS_inst0"), transit_models.get_model(planet_name="b", inst_model_fullname="LC_CHEOPS_inst1"))
        self.assertEqual(transit_models.get_model(planet_name="c", inst_model_fullname="LC_CHEOPS_inst0"), transit_models.get_model(planet_name="c", inst_model_fullname="LC_CHEOPS_inst1"))
        self.assertNotEqual(transit_models.get_model(planet_name="b", inst_model_fullname="LC_CHEOPS_inst0"), transit_models.get_model(planet_name="c", inst_model_fullname="LC_CHEOPS_inst0"))
        logger.info("Check of the get_models done.")
        model_planetb = transit_models.get_model(planet_name="b", inst_model_fullname="LC_CHEOPS_inst0")
        model_planetb.create_parameters_and_set_main(inst_model_fullname='LC_CHEOPS_inst0')
        model_planetb.create_parameters_and_set_main(inst_model_fullname='LC_CHEOPS_inst1')
        model_planetc = transit_models.get_model(planet_name="c", inst_model_fullname="LC_CHEOPS_inst0")
        model_planetc.create_parameters_and_set_main(inst_model_fullname='LC_CHEOPS_inst0')
        model_planetc.create_parameters_and_set_main(inst_model_fullname='LC_CHEOPS_inst1')
        logger.info("Check of that create_parameters_and_set_main runs without error done.")
        self.assertTrue(self.host_star.rho.main)
        logger.info("Check that the param are main for the star model TransitModelBatman Done.")
        self.assertTrue(self.l_planet[0].Rrat.main)
        self.assertTrue(self.l_planet[0].P.main)
        self.assertTrue(self.l_planet[0].tic.main)
        self.assertTrue(self.l_planet[0].tic1.main)
        self.assertTrue(self.l_planet[0].ecosw.main)
        self.assertTrue(self.l_planet[0].esinw.main)
        self.assertTrue(self.l_planet[0].cosinc.main)
        logger.info(f"Check that the param are main for the planet {0} model TransitModelBatman Done.")
        self.assertTrue(self.l_planet[1].Rrat.main)
        self.assertTrue(self.l_planet[1].P.main)
        self.assertTrue(self.l_planet[1].tic.main)
        self.assertTrue(self.l_planet[1].ecosw.main)
        self.assertTrue(self.l_planet[1].esinw.main)
        self.assertTrue(self.l_planet[1].cosinc.main)
        logger.info(f"Check that the param are main for the planet {1} model TransitModelBatman Done.")
        transit_models.load_config(dico_config=self.dico_config_transit_models)
        self.assertNotEqual(transit_models.get_model(planet_name="b", inst_model_fullname="LC_CHEOPS_inst0"), transit_models.get_model(planet_name="b", inst_model_fullname="LC_CHEOPS_inst1"))
        self.assertEqual(transit_models.get_model(planet_name="c", inst_model_fullname="LC_CHEOPS_inst0"), transit_models.get_model(planet_name="c", inst_model_fullname="LC_CHEOPS_inst1"))
        model_planetb0 = transit_models.get_model(planet_name="b", inst_model_fullname='LC_CHEOPS_inst0')
        model_planetb0.create_parameters_and_set_main(inst_model_fullname='LC_CHEOPS_inst0')
        model_planetb1 = transit_models.get_model(planet_name="b", inst_model_fullname='LC_CHEOPS_inst1')
        model_planetb1.create_parameters_and_set_main(inst_model_fullname='LC_CHEOPS_inst1')
        model_planetc = transit_models.get_model(planet_name="c", inst_model_fullname="LC_CHEOPS_inst0")
        model_planetc.create_parameters_and_set_main(inst_model_fullname='LC_CHEOPS_inst0')
        model_planetc.create_parameters_and_set_main(inst_model_fullname='LC_CHEOPS_inst1')
        logger.info("Check the load_config function runs without error Done.")
        self.assertTrue(self.l_planet[0].Rrat1.main)
        self.assertTrue(self.l_planet[0].P.main)
        self.assertTrue(self.l_planet[0].tic.main)
        self.assertTrue(self.l_planet[0].tic1.main)
        self.assertTrue(self.l_planet[0].ecosw.main)
        self.assertTrue(self.l_planet[0].esinw.main)
        self.assertTrue(self.l_planet[0].cosinc.main)
        logger.info(f"Check that the param are main for the planet {0} model TransitModelBatman after load_config Done.")
        self.assertTrue(self.l_planet[1].Rrat.main)
        self.assertTrue(self.l_planet[1].P.main)
        self.assertTrue(self.l_planet[1].tic.main)
        self.assertTrue(self.l_planet[1].ecosw.main)
        self.assertTrue(self.l_planet[1].esinw.main)
        self.assertTrue(self.l_planet[1].cosinc.main)
        logger.info(f"Check that the param are main for the planet {1} model TransitModelBatman after load_config Done.")

    def test_occultation_models(self):
        logger.info("\n\nSTART test_occultation_model")
        orbital_models = OrbitalModels(l_planet=self.l_planet, host_star=self.host_star,
                                       l_inst_model_fullname=self.l_inst_model_fullname
                                       )
        orbital_models.load_config(dico_config=self.dico_config_orbital_models)
        occultation_models = OccultationModels(l_planet=self.l_planet, host_star=self.host_star, l_inst_model_fullname=self.l_inst_model_fullname_tr,
                                               orbital_models=orbital_models
                                               )
        logger.info("test_creation_done")
        print(f"occultation_models.__repr__ = {occultation_models!r}")
        print(f"occultation_models = {occultation_models}")
        logger.info("Check of the __repr__ and __str__ done")
        self.assertFalse(occultation_models.get_do(planet_name="b"))
        self.assertFalse(occultation_models.get_do(planet_name="c"))
        logger.info("Check of the get_do done.")
        self.assertTrue(isinstance(occultation_models.get_model(planet_name="b", inst_model_fullname="LC_CHEOPS_inst0"), OccultationModelBatman))
        self.assertTrue(isinstance(occultation_models.get_model(planet_name="c", inst_model_fullname="LC_CHEOPS_inst1"), OccultationModelBatman))
        self.assertEqual(occultation_models.get_model(planet_name="b", inst_model_fullname="LC_CHEOPS_inst0"), occultation_models.get_model(planet_name="b", inst_model_fullname="LC_CHEOPS_inst1"))
        self.assertEqual(occultation_models.get_model(planet_name="c", inst_model_fullname="LC_CHEOPS_inst0"), occultation_models.get_model(planet_name="c", inst_model_fullname="LC_CHEOPS_inst1"))
        self.assertNotEqual(occultation_models.get_model(planet_name="b", inst_model_fullname="LC_CHEOPS_inst0"), occultation_models.get_model(planet_name="c", inst_model_fullname="LC_CHEOPS_inst0"))
        logger.info("Check of the get_models done.")
        model_planetb = occultation_models.get_model(planet_name="b", inst_model_fullname="LC_CHEOPS_inst0")
        model_planetb.create_parameters_and_set_main(inst_model_fullname='LC_CHEOPS_inst0')
        model_planetb.create_parameters_and_set_main(inst_model_fullname='LC_CHEOPS_inst1')
        model_planetc = occultation_models.get_model(planet_name="c", inst_model_fullname="LC_CHEOPS_inst0")
        model_planetc.create_parameters_and_set_main(inst_model_fullname='LC_CHEOPS_inst0')
        model_planetc.create_parameters_and_set_main(inst_model_fullname='LC_CHEOPS_inst1')
        logger.info("Check of that create_parameters_and_set_main runs without error done.")
        self.assertTrue(self.host_star.rho.main)
        logger.info("Check that the param are main for the star model occultationModelBatman Done.")
        self.assertTrue(self.l_planet[0].Rrat.main)
        self.assertTrue(self.l_planet[0].Frat.main)
        self.assertTrue(self.l_planet[0].P.main)
        self.assertTrue(self.l_planet[0].tic.main)
        self.assertTrue(self.l_planet[0].tic1.main)
        self.assertTrue(self.l_planet[0].ecosw.main)
        self.assertTrue(self.l_planet[0].esinw.main)
        self.assertTrue(self.l_planet[0].cosinc.main)
        logger.info(f"Check that the param are main for the planet {0} model occultationModelBatman Done.")
        self.assertTrue(self.l_planet[1].Rrat.main)
        self.assertTrue(self.l_planet[1].Frat.main)
        self.assertTrue(self.l_planet[1].P.main)
        self.assertTrue(self.l_planet[1].tic.main)
        self.assertTrue(self.l_planet[1].ecosw.main)
        self.assertTrue(self.l_planet[1].esinw.main)
        self.assertTrue(self.l_planet[1].cosinc.main)
        logger.info(f"Check that the param are main for the planet {1} model occultationModelBatman Done.")
        occultation_models.load_config(dico_config=self.dico_config_occultation_models)
        self.assertNotEqual(occultation_models.get_model(planet_name="b", inst_model_fullname="LC_CHEOPS_inst0"), occultation_models.get_model(planet_name="b", inst_model_fullname="LC_CHEOPS_inst1"))
        self.assertEqual(occultation_models.get_model(planet_name="c", inst_model_fullname="LC_CHEOPS_inst0"), occultation_models.get_model(planet_name="c", inst_model_fullname="LC_CHEOPS_inst1"))
        self.assertTrue(occultation_models.get_do(planet_name="b"))
        self.assertTrue(occultation_models.get_do(planet_name="c"))
        model_planetb0 = occultation_models.get_model(planet_name="b", inst_model_fullname='LC_CHEOPS_inst0')
        model_planetb0.create_parameters_and_set_main(inst_model_fullname='LC_CHEOPS_inst0')
        model_planetb1 = occultation_models.get_model(planet_name="b", inst_model_fullname='LC_CHEOPS_inst1')
        model_planetb1.create_parameters_and_set_main(inst_model_fullname='LC_CHEOPS_inst1')
        model_planetc = occultation_models.get_model(planet_name="c", inst_model_fullname="LC_CHEOPS_inst0")
        model_planetc.create_parameters_and_set_main(inst_model_fullname='LC_CHEOPS_inst0')
        model_planetc.create_parameters_and_set_main(inst_model_fullname='LC_CHEOPS_inst1')
        logger.info("Check the load_config function runs without error Done.")
        self.assertTrue(self.l_planet[0].Rrat1.main)
        self.assertTrue(self.l_planet[0].Frat1.main)
        self.assertTrue(self.l_planet[0].P.main)
        self.assertTrue(self.l_planet[0].tic.main)
        self.assertTrue(self.l_planet[0].tic1.main)
        self.assertTrue(self.l_planet[0].ecosw.main)
        self.assertTrue(self.l_planet[0].esinw.main)
        self.assertTrue(self.l_planet[0].cosinc.main)
        logger.info(f"Check that the param are main for the planet {0} model occultationModelBatman after load_config Done.")
        self.assertTrue(self.l_planet[1].Rrat.main)
        self.assertTrue(self.l_planet[1].Frat.main)
        self.assertTrue(self.l_planet[1].P.main)
        self.assertTrue(self.l_planet[1].tic.main)
        self.assertTrue(self.l_planet[1].ecosw.main)
        self.assertTrue(self.l_planet[1].esinw.main)
        self.assertTrue(self.l_planet[1].cosinc.main)
        logger.info(f"Check that the param are main for the planet {1} model occultationModelBatman after load_config Done.")

    def test_phasecurve_models(self):
        logger.info("\n\nSTART test_phasecurve_model")
        orbital_models = OrbitalModels(l_planet=self.l_planet, host_star=self.host_star,
                                       l_inst_model_fullname=self.l_inst_model_fullname
                                       )
        orbital_models.load_config(dico_config=self.dico_config_orbital_models)
        phasecurve_models = PhaseCurveModels(l_planet=self.l_planet, host_star=self.host_star, l_inst_model_fullname=self.l_inst_model_fullname_tr,
                                             orbital_models=orbital_models
                                             )
        logger.info("test_creation_done")
        print(f"phasecurve_models.__repr__ = {phasecurve_models!r}")
        print(f"phasecurve_models = {phasecurve_models}")
        logger.info("Check of the __repr__ and __str__ done")
        self.assertFalse(phasecurve_models.get_do(planet_name="b"))
        self.assertFalse(phasecurve_models.get_do(planet_name="c"))
        logger.info("Check of the get_do done.")
        self.assertTrue(isinstance(phasecurve_models.get_l_model(planet_name="b", inst_model_fullname="LC_CHEOPS_inst0")[0], PhaseCurveModelSinCos))
        self.assertTrue(isinstance(phasecurve_models.get_l_model(planet_name="c", inst_model_fullname="LC_CHEOPS_inst1")[0], PhaseCurveModelSinCos))
        self.assertEqual(phasecurve_models.get_l_model(planet_name="b", inst_model_fullname="LC_CHEOPS_inst0")[0], phasecurve_models.get_l_model(planet_name="b", inst_model_fullname="LC_CHEOPS_inst1")[0])
        self.assertEqual(phasecurve_models.get_l_model(planet_name="c", inst_model_fullname="LC_CHEOPS_inst0")[0], phasecurve_models.get_l_model(planet_name="c", inst_model_fullname="LC_CHEOPS_inst1")[0])
        self.assertNotEqual(phasecurve_models.get_l_model(planet_name="b", inst_model_fullname="LC_CHEOPS_inst0")[0], phasecurve_models.get_l_model(planet_name="c", inst_model_fullname="LC_CHEOPS_inst0")[0])
        logger.info("Check of the get_models done.")
        model_planetb = phasecurve_models.get_l_model(planet_name="b", inst_model_fullname="LC_CHEOPS_inst0")[0]
        model_planetb.create_parameters_and_set_main(inst_model_fullname='LC_CHEOPS_inst0')
        model_planetb.create_parameters_and_set_main(inst_model_fullname='LC_CHEOPS_inst1')
        model_planetc = phasecurve_models.get_l_model(planet_name="c", inst_model_fullname="LC_CHEOPS_inst0")[0]
        model_planetc.create_parameters_and_set_main(inst_model_fullname='LC_CHEOPS_inst0')
        model_planetc.create_parameters_and_set_main(inst_model_fullname='LC_CHEOPS_inst1')
        logger.info("Check of that create_parameters_and_set_main runs without error done.")
        self.assertTrue(self.host_star.rho.main)
        logger.info("Check that the param are main for the star model PhaseCurveModelSinCos Done.")
        self.assertTrue(self.l_planet[0].A.main)
        self.assertTrue(self.l_planet[0].Foffset.main)
        self.assertTrue(self.l_planet[0].Phi.main)
        self.assertTrue(self.l_planet[0].P.main)
        self.assertTrue(self.l_planet[0].tic.main)
        self.assertTrue(self.l_planet[0].tic1.main)
        self.assertTrue(self.l_planet[0].ecosw.main)
        self.assertTrue(self.l_planet[0].esinw.main)
        self.assertTrue(self.l_planet[0].cosinc.main)
        logger.info(f"Check that the param are main for the planet {0} model PhaseCurveModelSinCos Done.")
        self.assertTrue(self.l_planet[1].A.main)
        self.assertTrue(self.l_planet[1].Foffset.main)
        self.assertTrue(self.l_planet[1].Phi.main)
        self.assertTrue(self.l_planet[1].P.main)
        self.assertTrue(self.l_planet[1].tic.main)
        self.assertTrue(self.l_planet[1].ecosw.main)
        self.assertTrue(self.l_planet[1].esinw.main)
        self.assertTrue(self.l_planet[1].cosinc.main)
        logger.info(f"Check that the param are main for the planet {1} model phasecurveModelBatman Done.")
        phasecurve_models.load_config(dico_config=self.dico_config_phasecurve_models)
        self.assertEqual(phasecurve_models.get_l_model(planet_name="b", inst_model_fullname="LC_CHEOPS_inst0")[0], phasecurve_models.get_l_model(planet_name="b", inst_model_fullname="LC_CHEOPS_inst1")[0])
        self.assertNotEqual(phasecurve_models.get_l_model(planet_name="b", inst_model_fullname="LC_CHEOPS_inst0")[1], phasecurve_models.get_l_model(planet_name="b", inst_model_fullname="LC_CHEOPS_inst1")[0])
        self.assertEqual(phasecurve_models.get_l_model(planet_name="c", inst_model_fullname="LC_CHEOPS_inst0")[0], phasecurve_models.get_l_model(planet_name="c", inst_model_fullname="LC_CHEOPS_inst1")[0])
        self.assertTrue(phasecurve_models.get_do(planet_name="b"))
        self.assertTrue(phasecurve_models.get_do(planet_name="c"))
        l_model_planetb0 = phasecurve_models.get_l_model(planet_name="b", inst_model_fullname='LC_CHEOPS_inst0')
        for model in l_model_planetb0:
            model.create_parameters_and_set_main(inst_model_fullname='LC_CHEOPS_inst0')
        l_model_planetb1 = phasecurve_models.get_l_model(planet_name="b", inst_model_fullname='LC_CHEOPS_inst1')
        for model in l_model_planetb1:
            model.create_parameters_and_set_main(inst_model_fullname='LC_CHEOPS_inst1')
        l_model_planetc0 = phasecurve_models.get_l_model(planet_name="c", inst_model_fullname="LC_CHEOPS_inst0")
        for model in l_model_planetc0:
            model.create_parameters_and_set_main(inst_model_fullname='LC_CHEOPS_inst0')
        l_model_planetc1 = phasecurve_models.get_l_model(planet_name="c", inst_model_fullname='LC_CHEOPS_inst1')
        for model in l_model_planetc1:
            model.create_parameters_and_set_main(inst_model_fullname='LC_CHEOPS_inst1')
        logger.info("Check the load_config function runs without error Done.")
        self.assertTrue(self.l_planet[0].Rrat1.main)
        self.assertTrue(self.l_planet[0].A.main)
        self.assertTrue(self.l_planet[0].P.main)
        self.assertTrue(self.l_planet[0].tic.main)
        self.assertTrue(self.l_planet[0].tic1.main)
        self.assertTrue(self.l_planet[0].ecosw.main)
        self.assertTrue(self.l_planet[0].esinw.main)
        self.assertTrue(self.l_planet[0].cosinc.main)
        logger.info(f"Check that the param are main for the planet {0} model phasecurveModelBatman after load_config Done.")
        self.assertFalse(self.l_planet[1].Rrat.main)
        self.assertTrue(self.l_planet[1].A.main)
        self.assertTrue(self.l_planet[1].A1.main)
        self.assertTrue(self.l_planet[1].Foffset.main)
        self.assertTrue(self.l_planet[1].Phi.main)
        self.assertTrue(self.l_planet[1].P.main)
        self.assertTrue(self.l_planet[1].tic.main)
        self.assertTrue(self.l_planet[1].ecosw.main)
        self.assertTrue(self.l_planet[1].esinw.main)
        self.assertTrue(self.l_planet[1].cosinc.main)
        logger.info(f"Check that the param are main for the planet {1} model phasecurveModelBatman after load_config Done.")
    #     logger.info("test_phasecurve_model")
    #     orbital_model = OrbitalModel(l_planet=self.l_planet, host_star=self.host_star,
    #                                  l_inst_model_fullname=self.l_inst_model_fullname
    #                                  )
    #     orbital_model.define_model(planet_name='b', model_name='1', model_category='batman',
    #                                new_parameter={'planet': {'P': '', 'tic': True, 'ecosw': '', 'esinw': '', 'aR': ''},
    #                                               'star': {'rho': True},
    #                                               },
    #                                overwrite=False
    #                                )
    #     orbital_model.set_model_name_4_inst_model(planet_name='b', inst_model_fullname='LC_CHEOPS_inst1', model_name='1')
    #     phasecurve_model = PhaseCurveModel(l_planet=self.l_planet, host_star=self.host_star, l_inst_model_fullname=self.l_inst_model_fullname_tr,
    #                                        orbitalmodel_instance=orbital_model
    #                                        )
    #     phasecurve_model.define_model(planet_name='b', model_name='1', model_category='kelp-thermal', new_parameter={'planet': {'Rrat': '', }, 'star': {'Teff': ''}, },
    #                                   overwrite=False
    #                                   )
    #     phasecurve_model.define_model(planet_name='c', model_name='', model_category='spiderman-zhang', new_parameter={'planet': {'Rrat': '', }, 'star': {'Teff': ''}, },
    #                                   overwrite=True
    #                                   )
    #     phasecurve_model.define_model(planet_name='c', model_name='2', model_category='lambertian', new_parameter=None,
    #                                   overwrite=False
    #                                   )
    #     phasecurve_model.set_l_model_name_4_inst_model(planet_name='b', inst_model_fullname='LC_CHEOPS_inst1', l_model_name=['', '1'])
    #     phasecurve_model.set_l_model_name_4_inst_model(planet_name='c', inst_model_fullname='LC_CHEOPS_inst0', l_model_name=[''])
    #     phasecurve_model.set_l_model_name_4_inst_model(planet_name='c', inst_model_fullname='LC_CHEOPS_inst1', l_model_name=['2', ''])
    #     phasecurve_model.set_do(do=True, planet_name='b')
    #     phasecurve_model.set_do(do=True, planet_name='c')
    #     logger.info("test_creation_done")
    #     logger.info("test_creation_done")
    #     print(f"phasecurve_model.__repr__ = {phasecurve_model!r}")
    #     print(f"phasecurve_model = {phasecurve_model}")
    #     logger.info("Check of the __repr__ and __str__ done")
    #     self.assertEqual(phasecurve_model.get_parameter_name(planet_name='b', param_basename='A', inst_model_fullname='LC_CHEOPS_inst0'), 'A')
    #     self.assertEqual(phasecurve_model.get_parameter_name(planet_name='b', param_basename='Rrat', inst_model_fullname='LC_CHEOPS_inst1'), 'Rrat')
    #     self.assertEqual(phasecurve_model.get_parameter_name(planet_name='b', param_basename='P', model_name='', inst_model_fullname='LC_CHEOPS_inst0'), 'P')
    #     self.assertEqual(phasecurve_model.get_parameter_name(planet_name='b', param_basename='P', model_name='1', inst_model_fullname='LC_CHEOPS_inst1'), 'P')
    #     self.assertEqual(phasecurve_model.get_parameter_name(planet_name='b', param_basename='P', model_name='', inst_model_fullname='LC_CHEOPS_inst1'), 'P')
    #     self.assertEqual(phasecurve_model.get_parameter_name(planet_name='b', param_basename='tic', inst_model_fullname='LC_CHEOPS_inst0'), 'tic')
    #     self.assertEqual(phasecurve_model.get_parameter_name(planet_name='b', param_basename='tic', model_name='1', inst_model_fullname='LC_CHEOPS_inst1'), 'tic1')
    #     logger.info("test_content_after_creation_done")


if __name__ == '__main__':

    importlib.reload(lisa.posterior.exoplanet.model.gravgroup.planetstarmodel)
    importlib.reload(lisa.posterior.exoplanet.model.gravgroup.planetstarmodel_parametrisation)
    from lisa.posterior.exoplanet.model.gravgroup.planetstarmodel_parametrisation import OrbitalModels, RVKeplerianModels, TransitModels, OccultationModels, PhaseCurveModels
    from lisa.posterior.exoplanet.model.gravgroup.planetstarmodel import OrbitalModelBatman, RVKeplerianModelRadvel, TransitModelBatman, OccultationModelBatman, PhaseCurveModelSinCos, PhaseCurveModelBeaming, PhaseCurveModelEllipsoidal, PhaseCurveModelLambertian, PhaseCurveModelKelpThermal, PhaseCurveModelSpidermanZhang

    main()
