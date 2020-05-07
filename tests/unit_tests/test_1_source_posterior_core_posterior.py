#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Unit tests for the source.posterior.core.posterior
"""
import logging
import unittest
import sys
import os

# from unittest.mock import patch

import lisa.posterior.core.posterior as pst


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

    def test_posterior_instance_creation_basic(self):
        post_instance = pst.Posterior(object_name="TEST")
        post_instance = pst.Posterior(object_name="TEST", run_folder=os.getcwd())


if __name__ == '__main__':
    unittest.main()
