#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Unit tests for the source.tools.name module.
"""
from unittest import TestCase, main
from logging import getLogger, StreamHandler, Formatter
from logging import DEBUG, INFO
from sys import stdout

import source.tools.dico_database as ddb

level_logger = DEBUG
level_handler = DEBUG

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
        self.ndict = ddb.Nesteddict()
        self.ndictwlvl = ddb.Nesteddict_wlvl()
        self.ndictwflvlnb = ddb.Nesteddict_wfixellvlnb(nb_lvl=3)
        # self.dico1level = {"a": 1, "b": 2}
        # self.dico2level = {"a": {"1": 1, "2": 2}, "b": {"1": 1, "2": 2}}
        # self.dico3level = {"a": {"1": {"i": "i", "j": "j"}, "2": {"i": "i", "j": "j"}},
        #                    "b": {"1": {"i": "i", "j": "j"}, "2": {"i": "i", "j": "j"}}}

    def test_Nesteddict_wlvl(self):
        self.assertEqual(self.ndictwlvl.lvl, 0)
        self.assertEqual(self.ndictwlvl["level1"].lvl, 1)
        self.assertEqual(self.ndictwlvl["level1"]["level2"].lvl, 2)

    def test_Nesteddict_wfixellvlnb(self):
        self.assertEqual(self.ndictwflvlnb.lvl, 0)
        self.ndictwflvlnb["level1"]
        self.assertEqual(self.ndictwflvlnb["level1"].lvl, 1)
        self.ndictwflvlnb["level1"]["level2"]
        self.ndictwflvlnb["level1"]["level2"]["level3"]
        with self.assertRaises(TypeError):
            self.ndictwflvlnb["level1"]["level2"]["level3"]["level4"]
        self.ndictwflvlnb.clear()
        self.ndictwflvlnb["level1"]["level2"]["level3"] = 1
        self.assertFalse("level2" in self.ndictwflvlnb)
        self.assertTrue("level2" in self.ndictwflvlnb["level1"])

    def test_Nesteddict_wfixellvlnb_get_lvl2_keys(self):
        d3lvl = ddb.Nesteddict_wfixellvlnb(nb_lvl=3)
        d3lvl["A"]["a"]["i"] = 1
        d3lvl["A"]["b"]["ii"] = 2
        d3lvl["B"]["b"]["ii"] = 2
        d3lvl["C"]["c"]["iii"] = 3
        self.assertCountEqual(d3lvl.get_lvl2_keys(), ["a", "b", "c", "b"])
        self.assertCountEqual(d3lvl.get_lvl2_keys(level1_key="A", sortby_lvl1key=False), ["a", "b"])
        self.assertCountEqual(d3lvl.get_lvl2_keys(level1_key="A", sortby_lvl1key=True),
                              {"A": ["a", "b"]})

    def test_Nesteddict_wfixellvlnb_get_lvl2_values(self):
        d3lvl = ddb.Nesteddict_wfixellvlnb(nb_lvl=3)
        d3lvl["A"]["a"]["i"] = 1
        d3lvl["A"]["b"]["ii"] = 2
        d3lvl["B"]["b"]["ii"] = 2
        d3lvl["C"]["c"]["iii"] = 3
        self.assertCountEqual(d3lvl.get_lvl2_values(), [{"i": 1}, {"ii": 2}, {"ii": 2}, {"iii": 3}])
        self.assertCountEqual(d3lvl.get_lvl2_values(level1_key="A", sortby_lvl1key=True),
                              {"A": [{"i": 1}, {"ii": 2}]})
        self.assertCountEqual(d3lvl.get_lvl2_values(level1_key="A", sortby_lvl2key=True),
                              {"a": [{"i": 1}], "b": [{"ii": 2}]})
        # self.assertCountEqual(d3lvl.get_lvl2_values(level1_key="A", sortby_lvl1key=False), ["a", "b"])
        # self.assertCountEqual(d3lvl.get_lvl2_values(level1_key="A", sortby_lvl1key=True),
        #                       {"A": ["a", "b"]})
    #     res = ddb.get_content_2ndlevel(self.dico1level, level1_key="a")
    #     self.assertEqual(res, 1)
    #     res = ddb.get_content_2ndlevel(self.dico1level)
    #     self.assertEqual(res, self.dico1level)
    #     res = ddb.get_content_2ndlevel(self.dico2level, level1_key="a")
    #     self.assertCountEqual(res, ["1", "2"])
    #     res = ddb.get_content_2ndlevel(self.dico2level)
    #     self.assertCountEqual(res, {"a": ["1", "2"], "b": ["1", "2"]})
    #     res = ddb.get_content_2ndlevel(self.dico3level, level1_key="a")
    #     self.assertCountEqual(res, ["1", "2"])
    #     res = ddb.get_content_2ndlevel(self.dico3level)
    #     self.assertCountEqual(res, {"a": ["1", "2"], "b": ["1", "2"]})

    def test_Nesteddict_wfixellvlnb_get_lvl3_keys(self):
        d3lvl = ddb.Nesteddict_wfixellvlnb(nb_lvl=3)
        d3lvl["A"]["a"]["i"] = 1
        d3lvl["A"]["b"]["ii"] = 2
        d3lvl["B"]["b"]["ii"] = 2
        d3lvl["C"]["c"]["iii"] = 3
        self.assertCountEqual(d3lvl.get_lvl3_keys(), ["i", "ii", "ii", "iii"])
        self.assertCountEqual(d3lvl.get_lvl3_keys(sortby_lvl1key=True),
                              {"A": ["i", "ii"], "B": ["ii"], "C": ["iii"]})
        self.assertCountEqual(d3lvl.get_lvl3_keys(sortby_lvl2key=True),
                              {"a": ["i"], "b": ["ii", "ii"], "c": ["iii"]})
        self.assertCountEqual(d3lvl.get_lvl3_keys(sortby_lvl1key=True, sortby_lvl2key=True),
                              {"A": {"a": ["i"], "b": ["ii"]},
                               "B": {"b": ["ii"]},
                               "C": {"c": ["iii"]}})
        self.assertCountEqual(d3lvl.get_lvl3_keys(level1_key="A"), ["i", "ii"])
        self.assertCountEqual(d3lvl.get_lvl3_keys(level1_key="A", sortby_lvl1key=True),
                              {"A": ["i", "ii"]})
        self.assertCountEqual(d3lvl.get_lvl3_keys(level1_key="A", sortby_lvl2key=True),
                              {"a": ["i"], "b": ["ii"]})
        self.assertCountEqual(d3lvl.get_lvl3_keys(level1_key="A", sortby_lvl1key=True,
                                                  sortby_lvl2key=True),
                              {"A": {"a": ["i"], "b": ["ii"]}})
        self.assertCountEqual(d3lvl.get_lvl3_keys(level2_key="b"), ["ii", "ii"])
        self.assertCountEqual(d3lvl.get_lvl3_keys(level2_key="b", sortby_lvl1key=True),
                              {"A": ["ii"], "B": ["ii"]})
        self.assertCountEqual(d3lvl.get_lvl3_keys(level2_key="b", sortby_lvl2key=True),
                              {"b": ["ii", "ii"]})
        self.assertCountEqual(d3lvl.get_lvl3_keys(level2_key="b", sortby_lvl1key=True,
                                                  sortby_lvl2key=True),
                              {"A": {"b": ["ii"]}, "B": {"b": ["ii"]}})
        self.assertCountEqual(d3lvl.get_lvl3_keys(level1_key="A", level2_key="b"), ["ii"])
        self.assertCountEqual(d3lvl.get_lvl3_keys(level1_key="A", level2_key="b",
                                                  sortby_lvl1key=True),
                              {"A": ["ii"]})
        self.assertCountEqual(d3lvl.get_lvl3_keys(level1_key="A", level2_key="b",
                                                  sortby_lvl2key=True),
                              {"b": ["ii"]})
        self.assertCountEqual(d3lvl.get_lvl3_keys(level1_key="A", level2_key="b",
                                                  sortby_lvl1key=True, sortby_lvl2key=True),
                              {"A": {"b": ["ii"]}})
        self.assertCountEqual(d3lvl.get_lvl3_keys(level1_key="D", sortby_lvl1key=True), {})
        self.assertCountEqual(d3lvl.get_lvl3_keys(level1_key="D", sortby_lvl2key=True), {})
        self.assertCountEqual(d3lvl.get_lvl3_keys(level1_key="D", sortby_lvl1key=True,
                                                  sortby_lvl2key=True), {})
        self.assertCountEqual(d3lvl.get_lvl3_keys(level1_key="D"), [])
        self.assertCountEqual(d3lvl.get_lvl3_keys(level2_key="d", sortby_lvl1key=True), {})

    def test_Nesteddict_wfixellvlnb_get_lvl3_values(self):
        d3lvl = ddb.Nesteddict_wfixellvlnb(nb_lvl=3)
        d3lvl["A"]["a"]["i"] = 1
        d3lvl["A"]["b"]["ii"] = 2
        d3lvl["B"]["b"]["ii"] = 2
        d3lvl["C"]["c"]["iii"] = 3
        self.assertCountEqual(d3lvl.get_lvl3_values(), [1, 2, 2, 3])
        self.assertCountEqual(d3lvl.get_lvl3_values(sortby_lvl1key=True),
                              {"A": [1, 2], "B": [2], "C": [3]})
        self.assertCountEqual(d3lvl.get_lvl3_values(sortby_lvl1key=True)["A"],
                              [1, 2])
        self.assertCountEqual(d3lvl.get_lvl3_values(sortby_lvl1key=True)["B"],
                              [2])
        self.assertCountEqual(d3lvl.get_lvl3_values(sortby_lvl1key=True)["C"],
                              [3])
        self.assertCountEqual(d3lvl.get_lvl3_values(sortby_lvl2key=True),
                              {"a": [1], "b": [2, 2], "c": [3]})
        self.assertCountEqual(d3lvl.get_lvl3_values(sortby_lvl2key=True)['b'],
                              [2, 2])
        self.assertCountEqual(d3lvl.get_lvl3_values(sortby_lvl2key=True)['a'],
                              [1])
        self.assertCountEqual(d3lvl.get_lvl3_values(sortby_lvl3key=True),
                              {"i": [1], "ii": [2, 2], "iii": [3]})
        self.assertCountEqual(d3lvl.get_lvl3_values(sortby_lvl3key=True)["ii"],
                              [2, 2])
        self.assertCountEqual(d3lvl.get_lvl3_values(sortby_lvl3key=True)["iii"],
                              [3])
        self.assertCountEqual(d3lvl.get_lvl3_values(sortby_lvl3key=True)["i"],
                              [1])
        res = d3lvl.get_lvl3_values(sortby_lvl1key=True, sortby_lvl2key=True)
        expec = {"A": {"a": [1], "b": [2]}, "B": {"b": [2]}, "C": {"c": [3]}}
        logger.info("All sort by lvl 1 and lv2:\nres: {}\nexpected: {}".format(res, expec))
        self.assertCountEqual(res, expec)
        self.assertCountEqual(d3lvl.get_lvl3_values(sortby_lvl1key=True, sortby_lvl2key=True)["A"],
                              {"a": [1], "b": [2]})
        self.assertCountEqual(d3lvl.get_lvl3_values(sortby_lvl1key=True, sortby_lvl2key=True)["B"],
                              {"b": [2]})
        self.assertCountEqual(d3lvl.get_lvl3_values(sortby_lvl1key=True, sortby_lvl2key=True)["C"],
                              {"c": [3]})
        res = d3lvl.get_lvl3_values(sortby_lvl1key=True, sortby_lvl3key=True)
        expec = {"A": {"i": [1], "ii": [2]}, "B": {"ii": [2]}, "C": {"iii": [3]}}
        logger.info("All sort by lvl 1 and lv3:\nres: {}\nexpected: {}".format(res, expec))
        self.assertCountEqual(res, expec)
        res = d3lvl.get_lvl3_values(level1_key="A")
        expec = [1, 2]
        logger.info("lvl1 = 'a' no sort:\nres: {}\nexpected: {}".format(res, expec))
        self.assertCountEqual(res, expec)
        res = d3lvl.get_lvl3_values(level1_key="A", sortby_lvl1key=True)
        expec = {"A": [2, 2]}
        logger.info("lvl1 = 'A' sort by lvl 1:\nres: {}\nexpected: {}".format(res, expec))
        self.assertCountEqual(res, expec)
        res = d3lvl.get_lvl3_values(level1_key="A", sortby_lvl2key=True, sortby_lvl3key=True)
        expec = {"a": {"i": [1]}, "b": {"ii": [2]}}
        logger.info("lvl1 = 'A' sort by lvl 2 and lvl 3:\nres: {}\nexpected: {}".format(res, expec))
        self.assertCountEqual(res, expec)
        res = d3lvl.get_lvl3_values(level1_key="A", sortby_lvl1key=True, sortby_lvl2key=True)
        expec = {"A": {"a": [1], "b": [2]}}
        logger.info("lvl1 = 'A' sort by lvl 1 and lvl 2:\nres: {}\nexpected: {}".format(res, expec))
        self.assertCountEqual(res, expec)
        res = d3lvl.get_lvl3_values(level1_key="A", sortby_lvl1key=True, sortby_lvl3key=True)
        expec = {"A": {"i": [1], "ii": [2]}}
        logger.info("lvl1 = 'A' sort by lvl 1 and lvl 3:\nres: {}\nexpected: {}".format(res, expec))
        self.assertCountEqual(res, expec)
        res = d3lvl.get_lvl3_values(level2_key="b")
        expec = [2, 2]
        logger.info("lvl2 = 'b' no sort:\nres: {}\nexpected: {}".format(res, expec))
        self.assertCountEqual(res, expec)
        res = d3lvl.get_lvl3_values(level1_key="A", level2_key="b")
        expec = [2]
        logger.info("lvl2 = 'ii' no sort:\nres: {}\nexpected: {}".format(res, expec))
        self.assertCountEqual(res, expec)
        res = d3lvl.get_lvl3_values(level1_key="A", level2_key="a")
        expec = [1]
        logger.info("lvl2 = 'ii' no sort:\nres: {}\nexpected: {}".format(res, expec))
        self.assertCountEqual(res, expec)


if __name__ == '__main__':
    main()
