#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Unit tests for the source.posterior.exoplanet.model module.
"""
import logging
import unittest
import sys
# from ipdb import set_trace

import lisa.posterior.exoplanet.model.celestial_bodies as cb

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

    def test_basics(self):
        # set_trace()
        star_instance = cb.Star(name="K2-19")
        star_instance.M
        star_instance.R


if __name__ == '__main__':
    unittest.main()
