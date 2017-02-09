#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Unit tests for source.posterior.core.priors
"""
import logging
import unittest
import sys
# import os

# from unittest.mock import patch

import source.posterior.core.prior.manager_prior as mgr
import source.posterior.core.prior.prior_function as pf


# from source.posterior.core.priors.core_priors import priors

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

    def test_manage_priors_database(self):
        manager = mgr.Manager_Prior()
        manager._reset_priors_database()
        list_res = manager.get_available_priors()
        logger.info("Available priors types: {}".format(list_res))
        self.assertSequenceEqual(list_res, [])
        manager.add_available_prior(pf.UniformPrior)
        list_res = manager.get_available_priors()
        logger.info("Available priors types: {}".format(list_res))
        self.assertSequenceEqual(list_res, [pf.UniformPrior.category, ])
        self.assertTrue(manager.is_available_priortype(category=pf.UniformPrior.category))
        prior_subclass = manager.get_priorfunc_subclass(category=pf.UniformPrior.category)
        self.assertEqual(prior_subclass, pf.UniformPrior)
        self.assertFalse(manager.is_available_priortype(category="Truc"))
        manager._reset_priors_database()
        list_res = manager.get_available_priors()
        logger.info("Available prior types: {}".format(list_res))
        self.assertSequenceEqual(list_res, [])


if __name__ == '__main__':
    unittest.main()
