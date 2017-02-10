#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Unit tests for the source.tools.name module.
"""
from unittest import TestCase, main
from logging import getLogger, StreamHandler, Formatter
from logging import DEBUG
from sys import stdout

import source.tools.dico_database as ddb

logger = getLogger()
if logger.level > DEBUG:
    logger.setLevel(DEBUG)
if len(logger.handlers) == 0:
    ch = StreamHandler(stdout)
    ch.setLevel(DEBUG)
    formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)


class TestMethods(TestCase):

    def setUp(self):
        self.dico1level = {"a": 1, "b": 2}
        self.dico2level = {"a": {"1": 1, "2": 2}, "b": {"1": 1, "2": 2}}
        self.dico3level = {"a": {"1": {"i": "i", "j": "j"}, "2": {"i": "i", "j": "j"}},
                           "b": {"1": {"i": "i", "j": "j"}, "2": {"i": "i", "j": "j"}}}

    def test_get_nblevels_in_dico(self):
        self.assertEqual(ddb.get_nblevels_in_dico(self.dico1level), 1)
        self.assertEqual(ddb.get_nblevels_in_dico(self.dico2level), 2)
        self.assertEqual(ddb.get_nblevels_in_dico(self.dico3level), 3)

    def test_get_content_2ndlevel(self):
        res = ddb.get_content_2ndlevel(self.dico1level, level1_key="a")
        self.assertEqual(res, 1)
        res = ddb.get_content_2ndlevel(self.dico1level)
        self.assertEqual(res, self.dico1level)
        res = ddb.get_content_2ndlevel(self.dico2level, level1_key="a")
        self.assertCountEqual(res, ["1", "2"])
        res = ddb.get_content_2ndlevel(self.dico2level)
        self.assertCountEqual(res, {"a": ["1", "2"], "b": ["1", "2"]})
        res = ddb.get_content_2ndlevel(self.dico3level, level1_key="a")
        self.assertCountEqual(res, ["1", "2"])
        res = ddb.get_content_2ndlevel(self.dico3level)
        self.assertCountEqual(res, {"a": ["1", "2"], "b": ["1", "2"]})

    def test_get_content_3ndlevel(self):
        self.assertRaises(ValueError, ddb.get_content_3ndlevel, dico_db=self.dico1level)
        res = ddb.get_content_3ndlevel(self.dico2level, level1_key="a", level2_key="1")
        self.assertEqual(res, 1)
        res = ddb.get_content_3ndlevel(self.dico2level, level1_key="a")
        self.assertDictEqual(res, {"1": 1, "2": 2})
        res = ddb.get_content_3ndlevel(self.dico3level, level1_key="a", level2_key="1")
        self.assertCountEqual(res, ["i", "j"])
        res = ddb.get_content_3ndlevel(self.dico3level, level1_key="a")
        self.assertCountEqual(res, {"1": ["i", "j"], "2": ["i", "j"]})
        res = ddb.get_content_3ndlevel(self.dico3level)
        self.assertCountEqual(res, {"a": {"1": ["i", "j"], "2": ["i", "j"]},
                              "b": {"1": ["i", "j"], "2": ["i", "j"]}})


if __name__ == '__main__':
    main()
