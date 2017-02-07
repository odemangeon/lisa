#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Unit tests for the source.posterior.core.dataset_and_instrument.instrument module.
"""
import logging
import unittest
import sys

import source.posterior.core.dataset_and_instrument.instrument as inst

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

    def test_instrument_and_default_isntrument(self):
        inst_instance = inst._Default_Instrument(inst_type="LC", inst_name="K2")
        self.assertEqual("LC", inst_instance.inst_type)
        self.assertEqual("K2", inst_instance.name)


if __name__ == '__main__':
    unittest.main()
