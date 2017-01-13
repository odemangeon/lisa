#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
dataset module.

The objective of this package is to provides the core dataset class to store and manipulate
data.

@TODO:
    - Implement Flagged time-series
"""
import os
import logging

from ...software_parameters import input_data_folder

## Logger
logger = logging.getLogger()


class Dataset(object):
    """docstring for the Dataset abstract class."""
    def __init__(self, filename, main_data_folder=input_data_folder, data_folder=None):
        """Dataset init method FOR INHERITANCE PURPOSES (as Dataset is an abstract class).

        ----

        Arguments:
            filename : string
                Name of file which contains the data
            main_data_folder : string, optional,
                path to the data_folder which should contain a folder named after the target and
                contain the data. The name of the target is in the filename.
            data_folder : string,
                path to the folder which contain the data. If provided the data_folder argument is
                ignored.
        """
        super(Dataset, self).__init__()

        # Interpret filename
        filename_info = interpret_data_filename(filename)
        if filename_info is None:
            raise ValueError("The file name doesn't correspond to the naming convention."
                             "The creation of the instance is not possible.")

        self.file_name = filename
        self.target_name = filename_info["target"]
        self.instrument_type = filename_info["type"]
        self.instrument_name = filename_info["instrument"]

        # Check folder in which the file should be
        if data_folder is not None:
            folder = data_folder
        else:
            folder = os.path.join(main_data_folder, self.target_name)
        self.folder = folder

        # Make Dataset an abstract class
        if type(self) is Dataset:
            raise NotImplementedError("Dataset should not be instanciated!")


class Timeserie_dataset(Dataset):
    """
    Time-serie dataset class.

    This class defines time-series datasets as generally as possible.
    """

    _mandatory_columns = ["time"]  # Not sure if I should put time here if pandas time serie


def read_datasetsfile(filepath):
    """
    Read the datasets input file and return a list of dataset files to be used.

    ----

    Arguments:
        filepath: string,
            path to the datasets file.
    """
    if os.path.exists(filepath):
        logger.debug("file exists: {}".format(filepath))
        list_files = []
        with open(filepath, 'r') as f:
            for line in f.readlines():
                line_striped = line.strip(" \n")
                logger.debug("raw line: {}striped line: {}".format(line, line_striped))
                if not(line_striped.startswith("#")) and (len(line_striped) > 0):
                    logger.debug("line accepted as filename: {}".format(True))
                    list_files.append(line_striped)
                else:
                    logger.debug("line accepted as filename: {}".format(False))
    else:
        error_msg = "file doesn't exist: {}".format(filepath)
        raise ValueError(error_msg)
    logger.debug("List of files to use: {}".format(list_files))
    return list_files


def interpret_data_filename(data_file_name):
    """
    Interpret data file name.

    ----

    Arguments:
        data_file_name : string,
            Data file name
    Returns:
        dictionnary with the interpration of the filename which contains the following keys:
            - target : name of the target
            - type : data type "LC", "RV" or "SED"
            - instrument : instrument name
            - number : give the number of the data file if there is several data files from the same
            instrument
    """
    cuts = data_file_name.split("_")
    cuts[-1] = cuts[-1].split(".")[0]
    if len(cuts) < 3 or len(cuts) > 4:
        logging.warning("Data file name not recognized. Should be in the format "
                        "type_target_instrument(_number).txt. Got: {}".format(data_file_name))
        return None
    result = {"target": cuts[1],
              "type": cuts[0],
              "instrument": cuts[2]}
    if result["type"] not in ["LC", "RV", "SED"]:
        logging.warning("Data type from file name not recognized. Should be in  "
                        "['LC', 'RV', 'SED']. Got: {}".format(result["type"]))
        return None
    if len(cuts) == 3:
        result["number"] = None
    elif len(cuts) == 4:
        result["number"] = cuts[3]
    return result


def interpret_dataset_key(dataset_key):
    """
    Interpret dataset key.

    ----

    Arguments:
        dataset_key : string,
            dataset_key
    Returns:
        dictionnary with the interpration of the dataset key which contains the following keys:
            - instrument : instrument name
            - number : give the number of the data file if there is several data files from the same
            instrument
    """
    cuts = dataset_key.split("_")
    if len(cuts) > 2:
        logging.warning("dataset_key not recognized. Should be in the format "
                        "instrument_number. Got: {}".format(dataset_key))
        return None
    result = {"instrument": cuts[0]}
    if len(cuts) == 2:
        result["number"] = cuts[1]
    elif len(cuts) == 1:
        result["number"] = None
    return result


def build_dataset_key(instrument, number=None):
    """
    build dataset key.

    ----

    Arguments:
        instrument : string,
            instrument name
        number : string, optional,
            number of the dataset for this instrument
    Returns:
        dataset_key
    """
    separator = "_"
    dataset_key = instrument
    if number is not None:
        dataset_key += separator + number
    return dataset_key
