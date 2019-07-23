#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Unit tests for the source.tools.lockable_dict module.
"""
from unittest import TestCase, main
from logging import getLogger, StreamHandler, Formatter
from logging import DEBUG, INFO
from sys import stdout
from copy import copy

from lisa.tools.lockable_dict import LockableDict, Lock

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
        self.dico = LockableDict()
        self.lck = Lock()
        self.dico_wlock = LockableDict(lock=self.lck)

    def test_basics(self):
        self.dico.lock()
        with self.assertRaises(KeyError):
            self.dico["test"] = 4
        self.dico.unlock()
        self.dico["a"] = 1
        self.assertEqual(self.dico["a"], 1)
        self.dico.pop("a")

    def test_basics_lock(self):
        self.lck.unlock()
        a = self.lck
        self.assertFalse(a())
        self.assertFalse(self.lck())
        self.lck.lock()
        self.assertTrue(a())
        self.assertTrue(self.lck())

    def test_basics_copy(self):
        self.dico["a"] = 1
        self.dico["b"] = 2
        # print(self.dico)
        res = self.dico.copy()
        # print(res)
        self.assertFalse(self.dico is res)
        self.assertFalse(self.dico.get_Lock_instance() is res.get_Lock_instance())
        self.assertTrue(res.get_Lock_instance() is res.get_Lock_instance())


if __name__ == '__main__':
    main()
