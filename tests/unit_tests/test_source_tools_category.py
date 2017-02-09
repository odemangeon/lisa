#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Unit tests for the source.posterior.core.dataset_and_instrument.dataset module.
"""
from logging import getLogger, StreamHandler, Formatter
from logging import DEBUG
from unittest import TestCase, main
from sys import stdout

import source.tools.metaclasses as meta

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
        class Core_Test(metaclass=meta.CategorisedType):
            pass
        self.Core_Test = Core_Test

        class Test(Core_Test):
            __category__ = "Test"
        self.Test = Test

        class Test2(Core_Test):
            __category__ = "Test2"
        self.Test2 = Test2

        class Core_TestMROA(metaclass=meta.MandatoryReadOnlyAttr):
            __mandatoryattrs__ = ["category", "mandatory_args"]
        self.Core_TestMROA = Core_TestMROA

        class TestMROA(Core_TestMROA):
            __category__ = "Testcat"
            __mandatory_args__ = ["a", "b"]
        self.TestMROA = TestMROA

        class TestMROA2(Core_TestMROA):
            __category__ = "Testcat2"
            __mandatory_args__ = ["c", "d"]
        self.TestMROA2 = TestMROA2

    def test_basics(self):
        t = self.Test()
        t2 = self.Test2()
        self.assertEqual(t.category, "Test")
        self.assertEqual(self.Test.category, "Test")
        self.assertEqual(self.Test2.category, "Test2")
        self.assertEqual(t2.category, "Test2")

    def test_assertion_errors(self):
        with self.assertRaises(AttributeError):
            t = self.Test()
            t.category = "bla"
        with self.assertRaises(AttributeError):
            self.Test.category = "bla"
        with self.assertRaises(AttributeError):
            class Test3(self.Core_Test):
                pass

    def test_MandatoryReadOnlyAttr(self):
        t = self.TestMROA()
        t2 = self.TestMROA2()
        self.assertEqual(t.category, "Testcat")
        self.assertEqual(self.TestMROA.category, "Testcat")
        self.assertEqual(self.TestMROA2.category, "Testcat2")
        self.assertEqual(t2.category, "Testcat2")
        self.assertCountEqual(t.mandatory_args, ["a", "b"])
        self.assertCountEqual(t2.mandatory_args, ["c", "d"])
        self.assertCountEqual(self.TestMROA2.mandatory_args, ["c", "d"])

    def test_assertion_errors2(self):
        with self.assertRaises(AttributeError):
            class Core_TestMROA(metaclass=meta.MandatoryReadOnlyAttr):
                pass
        with self.assertRaises(AttributeError):
            self.TestMROA.category = "bla"
        with self.assertRaises(AttributeError):
            self.TestMROA.mandatory_args = "bla"
        with self.assertRaises(AttributeError):
            class Test3(self.Core_TestMROA):
                pass
        with self.assertRaises(AttributeError):
            class Test4(self.Core_TestMROA):
                __category__ = "Testcat4"


if __name__ == '__main__':
    main()
