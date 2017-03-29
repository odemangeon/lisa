#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Unit tests for the source.posterior.core.datafile_tools module.
"""
from unittest import TestCase, main
from logging import getLogger, StreamHandler, Formatter
from logging import DEBUG, INFO
from sys import stdout
from os import remove

import source.posterior.core.datafile_tools as dt

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
        pass

    def test_read_datafile(self):
        filepath = "test_read_datafile.txt"
        with open(filepath, "w") as f:
            f.write("RV_K2-19_HARPS.txt default\tgaussian\n")
            f.write("RV_K2-19_SOPHIE.txt   \t  default1\tstellar_activity\n")
        dico_res = dt.read_datafile(filepath)
        remove(filepath)
        logger.debug("Result of the reading process: {}".format(dico_res))
        expected_dict = {"RV_K2-19_HARPS.txt": {dt.dico_df_k["instmod"]: "default",
                                                dt.dico_df_k["noisemod"]: "gaussian"},
                         "RV_K2-19_SOPHIE.txt": {dt.dico_df_k["instmod"]: "default1",
                                                 dt.dico_df_k["noisemod"]: "stellar_activity"}
                         }
        logger.debug("Expected result of the reading process: {}".format(expected_dict))
        self.assertDictEqual(dico_res, expected_dict)


if __name__ == '__main__':
    main()
