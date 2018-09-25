#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Unit tests for the source.tools.name module.
"""
from unittest import TestCase, main
from logging import getLogger, StreamHandler, Formatter
from logging import DEBUG
from sys import stdout

from source.tools.name import Name, check_name_for_prohibitedchar, check_name, check_name_code

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
        class TestClass(Name):
            """Docstring of class TestClass."""
            def __init__(self, name, prefix=None):
                super(TestClass, self).__init__(name, name_prefix)
        self.TestClass = TestClass

    def test_check_name_functions(self):
        result = check_name_for_prohibitedchar(name="blablabla", prohibitedchars="bl")
        self.assertEqual(result, "aaa")
        result = check_name_for_prohibitedchar(name="blablabla", prohibitedchars="la")
        self.assertEqual(result, "bbb")
        result = check_name("test")
        self.assertEqual(result, "test")
        result = check_name("test_2")
        self.assertEqual(result, "test2")
        result = check_name_code("test")
        self.assertEqual(result, "test")
        result = check_name_code("test-2")
        self.assertEqual(result, "test2")

    def test_class_Name(self):
        testinst = self.TestClass(name="test")
        self.assertEqual(testinst.name, "test")
        testinst2 = self.TestClass(name="test", prefix="M.")
        self.assertEqual(testinst2.name, "test")
        with self.assertRaises(AttributeError):
            testinst.name = "redefinition_of_name"
        self.assertEqual(testinst.full_name, "test")
        self.assertEqual(testinst2.full_name, "M._test")
        testinst2.name_prefix = "Mr"
        self.assertEqual(testinst2.full_name, "M._test")
        testinst3 = self.TestClass(name="test-code")
        self.assertEqual(testinst3.name_code, "testcode")


if __name__ == '__main__':
    main()
