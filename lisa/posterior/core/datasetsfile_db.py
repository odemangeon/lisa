#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
datafile_tools module.

The objective of this package is to provide tools to read the datafile.

@ DONE:
    -
@TODO:
    -
"""
from loguru import logger
from re import split
from collections import OrderedDict

from .dataset_and_instrument.manager_dataset_instrument import Manager_Inst_Dataset
from ...tools.miscellaneous import get_filename_from_file_path
from ...tools.lockable_dict import LockableDict
from ...tools.database_with_instrument_level import DatabaseDatasetLevel
from .likelihood.manager_noise_model import Manager_NoiseModel

mgr_noisemodel = Manager_NoiseModel()
mgr_noisemodel.load_setup()

mgr_inst_dst = Manager_Inst_Dataset()
mgr_inst_dst.load_setup()


def read_datasets_file(datasetsfile_path):
    """Read a dataset file and return its content.
    ----
    Arguments:
        datafile_path: string, Path to the the dataset file
    Returns:
        dict with as key the path to the datasets and as value a dict with two keys:
            - "inst_mod" giving the name of the instrument model to use
            - "noise_mod" giving the category of the noise model to use
    """
    result = []
    with open(datasetsfile_path, 'r') as f:
        for line in f.readlines():
            line_striped = line.strip(" \n")
            logger.debug("raw line: {}striped line: {}".format(line, line_striped))
            if not(line_striped.startswith("#")) and (len(line_striped) > 0):
                logger.debug("Valid line ?: {}".format(True))
                result.append(line_striped)
            else:
                logger.debug("Valid line ?: {}".format(False))
    return result


class DatasetsFileDb(DatabaseDatasetLevel):
    """docstring for DatasetsFile.

    Database with three levels inst_fullcat, inst_name, dst_number which contains the dataset file path
    for each dataset to use.

    Properties
    ----------
    path4name         : dictionary
        Provide the dataset path (values) where the datasets designed by their name (keys) can be found.
    datasetsfile_path : string
        Path to the dataset.txt file.
    dataset_filepaths : list of string
        List of the paths to all the dataset files

    Methods
    -------
    load :
        Load the content of the dataset.txt file into this database
    get_noisemod4instmodfullname :
        Return a dictionary which provides the noise model category for each instrument model designated
        by their full name
    """

    def __init__(self, object_name, lock=None):
        object_stored = "dataset file path"
        super(DatasetsFileDb, self).__init__(object_stored=object_stored, database_name=object_name, 
                                             ordered=False, lock=lock, default=None)
        
    @property
    def datasetsfile_path(self):
        """Return the path to the datasets_file."""
        return self.__datasetsfile_path

    @property
    def l_dataset_file_path(self):
        """Return the list of the paths to the datasets."""
        return list(self.get_datasetfilepaths())
    
    @property
    def l_dataset_fullname(self):
        """Return the list of the paths to the datasets."""
        return [mgr_inst_dst.dataset_name_from_file_name(get_filename_from_file_path(dataset_file_path)) for dataset_file_path in self.get_datasetfilepaths()]

    def load(self, datasetsfile_path):
        """Load the datasets provided in the datasets file into the dataset database.

        Also update the datasetsfile_content.
        """
        l_dataset_files = read_datasets_file(datasetsfile_path)
        logger.debug("List of datasets in the datasets file: {}".format(l_dataset_files))

        # For each dataset file
        for dataset_filepath in l_dataset_files:
            # Extract the dataset name and filename from its path and file the path4name dictionary
            # giving the dataset path associated to its name
            dataset_filename = get_filename_from_file_path(dataset_filepath)
            dataset_name = mgr_inst_dst.dataset_name_from_file_name(dataset_filename)
            logger.debug("load info regarding dataset {} at path: {}".format(dataset_name, dataset_filepath))

            # Extract, instrument category, instrument name, ... from the dataset filename
            dataset_info = mgr_inst_dst.interpret_data_filename(dataset_filename)
            inst_fullcat = dataset_info["inst_fullcat"]
            inst_name = dataset_info["inst_name"]
            dst_nb = dataset_info["number"]

            self[inst_fullcat][inst_name][dst_nb] = dataset_filepath

        # Store the datasetsfile path into the read only datasetsfile_path property
        self.__datasetsfile_path = datasetsfile_path

class DatasetsFileDbAttr(object):
    """docstring for DataSets."""
    def __init__(self, object_name, lock=None):
        self.__datasetsfile_db = DatasetsFileDb(object_name=object_name, lock=lock)

    @property
    def datasetsfile_db(self):
        """Return the datasetsfile database"""
        return self.__datasetsfile_db
