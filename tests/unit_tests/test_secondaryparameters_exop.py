#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Unit tests for the source.posterior.core.dataset_and_instrument.manager_dataset_instrument module.
"""
from unittest import TestCase, main
from logging import getLogger, StreamHandler, Formatter
from logging import DEBUG, INFO
import sys
from sys import stdout
import importlib
from pprint import pformat
from numpy.random import random

from lisa.tools.chain_interpreter import ChainsInterpret

import lisa.posterior.exoplanet.exploration_analysis_tools.secondary_parameters

sys.path.append("input_files")

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
        n_walker = 10
        n_iteration = 1000
        n_dim = 2
        param_names = ['b_P', 'b_Rrat']

        self.chainI = ChainsInterpret(input_array=random(size=(n_walker, n_iteration, n_dim)), param_names=param_names)

    def test_get_secondary_chains(self):
        logger.info("\n\nSTART test_get_secondary_chains")
        chainIsec = get_secondary_chains(chainI_main=self.chainI, sec_params=sp, star_kwargs=None, planet_kwargs=None)
        print(f"list of secondary paramters computed: {chainIsec.param_names}\nchainIsec.shape = {chainIsec.shape}\nchainIsec = {chainIsec}")
        logger.info("test run without error. Done")





if __name__ == '__main__':
    import secondary_parameters
    importlib.reload(secondary_parameters)
    importlib.reload(lisa.posterior.exoplanet.exploration_analysis_tools.secondary_parameters)
    from lisa.posterior.exoplanet.exploration_analysis_tools.secondary_parameters import get_secondary_chains
    from secondary_parameters import sp

    main()
