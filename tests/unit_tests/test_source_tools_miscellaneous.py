#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Unit tests for the source.tools.function_w_doc module.
"""
from unittest import TestCase, main
from logging import getLogger, StreamHandler, Formatter
from logging import DEBUG, INFO
from sys import stdout

from source.tools.miscellaneous import (interpret_data_filename, get_filename_from_file_path,
                                        spacestring_like, get_filename_woext_from_filename)

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

    def test_spacestring_like(self):
        self.assertEqual(spacestring_like("test"), "    ")

    def test_get_filename_from_filepath(self):
        file_path = "Users/olivier/Softwares/lisa/data/K2-19/EPIC201505350.rdb"
        file_name = get_filename_from_file_path(file_path)
        self.assertEqual(file_name, "EPIC201505350.rdb")

    def test_get_filename_woext_from_filename(self):
        file_name = "EPIC201505350.rdb"
        file_name_woext = get_filename_woext_from_filename(file_name)
        self.assertEqual(file_name_woext, "EPIC201505350")

    def test_interpret_data_filename(self):
        filename_1 = "LC_K2-19_K2.txt"
        filename_2 = "RV_K2-3_HARPS_2.txt"
        dico_1 = interpret_data_filename(filename_1)
        dico_2 = interpret_data_filename(filename_2)
        self.assertDictEqual(dico_1, {"inst_category": "LC",
                                      "inst_name": "K2",
                                      "object": "K2-19",
                                      "number": 0})
        self.assertDictEqual(dico_2, {"inst_category": "RV",
                                      "inst_name": "HARPS",
                                      "object": "K2-3",
                                      "number": 2})


if __name__ == '__main__':
    main()
