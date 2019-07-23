#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Unit tests for the source.tools.default_folders_data_run module.
"""
from unittest import TestCase, main
from logging import getLogger, StreamHandler, Formatter
from logging import DEBUG, INFO
from sys import stdout
from unittest.mock import patch
from os import mkdir, rmdir, remove
from os.path import join

from lisa.tools.default_folders_data_run import RunFolder, DataFolder
from lisa.software_parameters import input_run_folder
from lisa.software_parameters import input_data_folder

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
        class TestClass(RunFolder, DataFolder):
            """Docstring of class TestClass."""
            def __init__(self, object_name, run_folder=None, data_folder=None):
                self.__object_name = object_name
                RunFolder.__init__(self, run_folder=run_folder)
                DataFolder.__init__(self, data_folder=data_folder)

            @property
            def object_name(self):
                return self.__object_name
        self.TestClass = TestClass

    def test_RunFolder_basics(self):
        logger.info("NEW TEST SUITE\n\nStart test_RunFolder")
        logger.info("Test 1: If you don't provide any run folder and ask for run_folder it returns"
                    "None.")
        instance = self.TestClass(object_name="Test")
        self.assertIsNone(instance.run_folder)
        logger.info("Test 2: Run folder provided has an absolute path and exist. Check that the run"
                    "folder is defined as expected.")
        folder_test = "test_run_folder"
        mkdir(folder_test)
        instance = self.TestClass(object_name="Test", run_folder=folder_test)
        rmdir(folder_test)
        self.assertTrue(instance.hasrun_folder)
        self.assertEqual(instance.run_folder, folder_test)
        logger.info("Test 3: Run folder defined with a file inside. Check that look4runfile manage"
                    " to find it from file name only or file path.")
        name_file = "test_file.txt"
        file_path = join(folder_test, "test_file.txt")
        mkdir(folder_test)
        open(file_path, "x")
        res1 = instance.look4runfile(name_file)
        res2 = instance.look4runfile(file_path)
        remove(file_path)
        rmdir(folder_test)
        self.assertEqual(res1, file_path)
        self.assertEqual(res2, file_path)
        logger.info("Test 4: Run folder defined with a file inside. Check that look4runfile doesn't"
                    " manage to find the file after deletion.")
        res1 = instance.look4runfile(name_file)
        res2 = instance.look4runfile(file_path)
        self.assertIsNone(res1)
        self.assertIsNone(res2)

    @patch("source.tools.miscellaneous.QCM_utilisateur", return_value="n")
    def test_def_absolute_runfolder_doesnt_exist_dont_create(self, input):
        logger.info("NEW TEST SUITE\n\nStart test_def_absolute_runfolder_doesnt_exist_dont_create")
        logger.info("Test: Run folder provided has an absolute path that doesn't exist and user "
                    "doesn't want to create it. Check that the run folder is not defined.")
        instance = self.TestClass(object_name="Test", run_folder="test_runfolder")
        self.assertFalse(instance.hasrun_folder)

    @patch("source.tools.miscellaneous.QCM_utilisateur", return_value="y")
    def test_def_absolute_runfolder_doesnt_exist_create(self, input):
        logger.info("NEW TEST SUITE\n\nStart test_def_absolute_runfolder_doesnt_exist_create")
        logger.info("Test: Run folder provided has an absolute path that doesn't exist and user "
                    " creates it. Check that the run folder is defined as expected.")
        folder_test = "test_runfolder"
        instance = self.TestClass(object_name="Test", run_folder=folder_test)
        rmdir(folder_test)
        self.assertTrue(instance.hasrun_folder)
        self.assertEqual(instance.run_folder, folder_test)

    @patch("source.tools.miscellaneous.QCM_utilisateur", return_value="n")
    def test_def_default_runfolder_doesnt_exist_dont_create(self, input):
        logger.info("NEW TEST SUITE\n\nStart test_def_default_runfolder_doesnt_exist_dont_create")
        logger.info("Test: Run folder provided has as defaults but subfolder doesn't exist and user"
                    " doesn't want to create it. Check that the run folder is not defined.")
        instance = self.TestClass(object_name="Test", run_folder="default")
        self.assertFalse(instance.hasrun_folder)

    @patch("source.tools.miscellaneous.QCM_utilisateur", return_value="y")
    def test_def_default_runfolder_doesnt_exist_create(self, input):
        logger.info("NEW TEST SUITE\n\nStart test_def_default_runfolder_doesnt_exist_create")
        logger.info("Test: Run folder provided has as defaults but subfolder doesn't exist and user"
                    " creates it. Check that the run folder is defined as expected.")
        object_name = "Test"
        instance = self.TestClass(object_name="Test", run_folder="default")
        rmdir(join(input_run_folder, object_name))
        self.assertTrue(instance.hasrun_folder)
        self.assertEqual(instance.run_folder, join(input_run_folder, object_name))

    def test_DataFolder_basics(self):
        logger.info("NEW TEST SUITE\n\nStart test_DataFolder_basics")
        logger.info("Test 1: If you don't provide any data folder and ask for data_folder it "
                    "returns None.")
        instance = self.TestClass(object_name="Test")
        self.assertIsNone(instance.run_folder)
        logger.info("Test 2: Data folder provided has an absolute path and exist. Check that the "
                    "data folder is defined as expected.")
        folder_test = "test_data_folder"
        mkdir(folder_test)
        instance = self.TestClass(object_name="Test", data_folder=folder_test)
        rmdir(folder_test)
        self.assertTrue(instance.hasdata_folder)
        self.assertEqual(instance.data_folder, folder_test)
        logger.info("Test 3: Data folder defined with a file inside. Check that look4datafile "
                    "manage to find it from file name only or file path.")
        name_file = "test_file.txt"
        file_path = join(folder_test, "test_file.txt")
        mkdir(folder_test)
        open(file_path, "x")
        res1 = instance.look4datafile(name_file)
        res2 = instance.look4datafile(file_path)
        remove(file_path)
        rmdir(folder_test)
        self.assertEqual(res1, file_path)
        self.assertEqual(res2, file_path)
        logger.info("Test 4: Data folder defined with a file inside. Check that look4datafile "
                    "doesn't manage to find the file after deletion.")
        res1 = instance.look4datafile(name_file)
        res2 = instance.look4datafile(file_path)
        self.assertIsNone(res1)
        self.assertIsNone(res2)

    @patch("source.tools.miscellaneous.QCM_utilisateur", return_value="n")
    def test_def_absolute_datafolder_doesnt_exist_dont_create(self, input):
        logger.info("NEW TEST SUITE\n\nStart test_def_absolute_datafolder_doesnt_exist_dont_create")
        logger.info("Test: data folder provided has an absolute path that doesn't exist and user "
                    "doesn't want to create it. Check that the data folder is not defined.")
        instance = self.TestClass(object_name="Test", data_folder="test_datafolder")
        self.assertFalse(instance.hasdata_folder)

    @patch("source.tools.miscellaneous.QCM_utilisateur", return_value="y")
    def test_def_absolute_datafolder_doesnt_exist_create(self, input):
        logger.info("NEW TEST SUITE\n\nStart test_def_absolute_datafolder_doesnt_exist_create")
        logger.info("Test: data folder provided has an absolute path that doesn't exist and user "
                    " creates it. Check that the data folder is defined as expected.")
        folder_test = "test_datafolder"
        instance = self.TestClass(object_name="Test", data_folder=folder_test)
        rmdir(folder_test)
        self.assertTrue(instance.hasdata_folder)
        self.assertEqual(instance.data_folder, folder_test)

    @patch("source.tools.miscellaneous.QCM_utilisateur", return_value="n")
    def test_def_default_datafolder_doesnt_exist_dont_create(self, input):
        logger.info("NEW TEST SUITE\n\nStart test_def_default_datafolder_doesnt_exist_dont_create")
        logger.info("Test: data folder provided has as defaults but subfolder doesn't exist and user"
                    " doesn't want to create it. Check that the data folder is not defined.")
        instance = self.TestClass(object_name="Test", data_folder="default")
        self.assertFalse(instance.hasdata_folder)

    @patch("source.tools.miscellaneous.QCM_utilisateur", return_value="y")
    def test_def_default_datafolder_doesnt_exist_create(self, input):
        logger.info("NEW TEST SUITE\n\nStart test_def_default_datafolder_doesnt_exist_create")
        logger.info("Test: data folder provided has as defaults but subfolder doesn't exist and user"
                    " creates it. Check that the data folder is defined as expected.")
        object_name = "Test"
        instance = self.TestClass(object_name="Test", data_folder="default")
        rmdir(join(input_data_folder, object_name))
        self.assertTrue(instance.hasdata_folder)
        self.assertEqual(instance.data_folder, join(input_data_folder, object_name))


if __name__ == '__main__':
    main()
