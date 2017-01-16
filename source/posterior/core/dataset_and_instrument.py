#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
dataset_and_instrument module.

The objective of this package is to provides the core dataset and isntrument classes to store
and manipulate thedata.

@TODO:
    - Implement Flagged time-series
    - Implement spectral_transmission ?
"""
import os
import logging

from .paramcontainer import ParamContainer


## Logger
logger = logging.getLogger()


class Dataset(object):
    """docstring for the Dataset abstract class."""
    def __init__(self, file_path):
        """Dataset init method FOR INHERITANCE PURPOSES (as Dataset is an abstract class).
        ----
        Arguments:
            file_path : string
                Path of file which contains the data
        """
        super(Dataset, self).__init__()
        # Check if the file exists at filepath
        if not(os.path.exists(file_path)):
            raise ValueError("file doesn't exist: {}".format(file_path))
        # Extract the filename from the file_path
        filename = self.get_filename(file_path)
        # Interpret and validate the filename
        filename_info = self.interpret_data_filename(filename)
        if filename_info is None:
            raise ValueError("The file name doesn't correspond to the naming convention."
                             "The creation of the instance is not possible.")
        # Create and validate the instrument instance
        self.__set_instrument(filename_info['inst_type'], filename_info['inst_name'])
        # Set the file_path and object_name attributes
        self.__set_filepath(file_path)
        self.__set_objectname(filename_info["object"])

        # Create abstract attribute data
        self.data = None

        # Make Dataset an abstract class
        if type(self) is Dataset:
            raise NotImplementedError("Dataset should not be instanciated!")

    def __set_filepath(self):
        """Define the path of the data file."""
        return self.__file_path

    def get_filepath(self):
        """Get the path of the data file."""
        return self.__file_path

    def get_filename(self, file_path=None):
        """Get the name of the data file."""
        if file_path is None:
            return os.path.basename(self.__file_path)
        else:
            return os.path.basename(file_path)

    def interpret_data_filename(data_file_name):
        """
        Interpret data file name.
        ----
        Arguments:
            data_file_name : string,
                Data file name
        Returns:
            dictionnary with the interpration of the filename which contains the following keys:
                - object : name of the target
                - inst_type : data type "LC", "RV" or "SED"
                - inst_name : instrument name
                - number : give the number of the data file if there is several data files from the
                same instrument
        """
        cuts = data_file_name.split("_")   # List of fields that were separated by "_"
        cuts[-1] = cuts[-1].split(".")[0]  # Remove the extension
        if len(cuts) < 3 or len(cuts) > 4:
            logging.warning("Data file name not recognized. Should be in the format "
                            "type_target_instrument(_number).txt. Got: {}".format(data_file_name))
            return None
        result = {"object": cuts[1],
                  "inst_type": cuts[0],
                  "inst_name": cuts[2]}
        if len(cuts) == 3:
            result["number"] = None
        elif len(cuts) == 4:
            result["number"] = cuts[3]
        return result

    def __set_instrument(self, inst_type, inst_name):
        """Define the instrument instance and attribute."""
        self.__instrument = Instrument(inst_type, inst_name)

    def _get_instrument(self):
        """Return the instrument instance."""
        return self.__instrument

    def __set_objectname(self, object_name):
        """Define the name of the object the data are about."""
        self.__object_name = object_name

    def get_objectname(self):
        """Return the name of the object the data are about."""
        return self.__object_name

    def load_data(self):
        """Load the content of the data file."""
        raise NotImplementedError("The function load_data is an abstract method in class Dataset !")

    def data_loaded(self):
        """Return True is data has been loaded, False otherwise."""
        return self.data is not None

    def __set_data(self, data):
        """Set the data attribute."""
        self.__data = data

    def get_data(self):
        """Return the data attribute."""
        if not(self.data_loaded):
            logger.warning("No data loaded for {}".format(self.get_name()))
        return self.__data

    def __rm_data(self):
        """Remove data previously loaded."""
        self.data = None
        logger.info("Data has been removed from {}.".format(self.get_name()))


class Timeserie_dataset(Dataset):
    """
    Time-serie dataset class.

    This class defines time-series datasets as generally as possible.
    """

    __mandatory_columns = ["time"]  # Not sure if I should put time here if pandas time serie

    def load_data(self, filepath):
        """Load the content of the data file."""
        raise NotImplementedError


class Instrument(ParamContainer):
    """docstring for Instrument."""

    __available_inst_types = []

    def __init__(self, inst_type, inst_name):
        """docstring for Instrument init method."""
        type_validated = self.validate_inst_type(inst_type)
        if type_validated:
            super(Instrument, self).__init__(inst_name)
        else:
            raise ValueError("Instrument type is not recognised: {}".format(inst_type))
        # Add Jitter parameter
        self.append_param(name='jitter')

    def validate_inst_type(self, inst_type):
        """Return True if inst_type is a know instrument type, False otherwise."""
        return inst_type in self.__available_inst_types

    def __set_inst_type(self, inst_type):
        """Define instrument type."""
        self.__inst_type = inst_type

    def get_inst_type(self):
        """Return isntrument type."""
        return self.__inst_type


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
