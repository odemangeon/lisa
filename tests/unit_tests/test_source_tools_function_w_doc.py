#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Unit tests for the source.tools.function_w_doc module.
"""
from unittest import TestCase, main
from logging import getLogger, StreamHandler, Formatter
from logging import DEBUG, INFO
from sys import stdout

from lisa.tools.function_w_doc import DocFunction

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
        def func(x, y):
            return x + y
        self.func = func

    def test_basics(self):
        docfunc = DocFunction(self.func, ["x", "y"])
        self.assertListEqual(docfunc.arg_list, ["x", "y"])
        self.assertEqual(docfunc.function, self.func)
        self.assertEqual(docfunc.function(1, 1), 2)
        self.assertEqual(docfunc(1, 1), 2)
        with self.assertRaises(AttributeError):
            docfunc.function = 1
        with self.assertRaises(AttributeError):
            docfunc.arg_list = "a"


if __name__ == '__main__':
    main()
