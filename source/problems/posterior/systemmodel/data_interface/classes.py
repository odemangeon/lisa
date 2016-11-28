#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Classes module.

The objective of this package is to provides the data classes to store and manipulate radial
velocity and light-curve data sets.

@TODO:
    - plot_LC method of ExoP_datasets
    - plot_RV method of ExoP_datasets
"""
import pandas as pd
import matplotlib.pyplot as plt
# import numpy as np
import os
import os.path
from collections import OrderedDict
import logging
import pdb

from .....software_parameters import input_data_folder

logger = logging.getLogger()


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


class ExoP_datasets():
    """
    Exoplanet data sets.

    Gather all the datasets from the different types:
        - radial velocities
        - light-curves
        - spectral energy distribution
    """

    def __init__(self, target, main_data_folder=input_data_folder, data_folder=None,
                 datasets_file=None):
        """
        Create an ExoP_datasets instance which will contains all the data on the studied target.

        Look at the content of the folder provided as input and load the data file contained in it.
        There is two ways to provide the input folder:
            - main_data_folder: You provide the data_folder which is made to receive the data
            from all the targets. It should contain a folder name after the target you want to
            study and which contain all the data.
            - data_folder: You provide directly the folder where the data are.

        ----

        Arguments:
            target : string,
                Name of the target studied.
            main_data_folder : string, optional,
                path to the data_folder which should contain a folder named after the target and
                contain the data.
            data_folder : string,
                path to the folder which contain the data. If provided the main_data_folder argument
                is ignored.
            datasets_filename: string
                Path to the datasets file. If this file is provided and exists and is not empty.
                Only the datasets files mentioned in this file will be considered.

        Returns:
            ExoP_datasets instance
        """
        self.target_name = target

        self.rv_datasets = OrderedDict()
        self.lc_datasets = OrderedDict()
        self.sed_datasets = OrderedDict()

        if data_folder is not None:
            folder = data_folder
        else:
            folder = os.path.join(main_data_folder, target)
        self.folder = folder

        if datasets_file is not None:
            self.datasets_file = datasets_file
            l_files = read_datasetsfile(self.datasets_file)
            if len(l_files) > 0:
                logger.debug("Datasets file content: {}".format(l_files))
                l_input_files_provided = True
            else:
                logger.debug("Datasets is empty.")
                l_input_files_provided = False
        else:
            l_input_files_provided = False

        if not(os.path.isdir(folder)):
            error_msg = "Folder doesn't exist: {}".format(folder)
            logger.error(error_msg)
            raise ValueError(error_msg)

        folder_content = os.listdir(folder)
        logger.info("List the content of {}:\n{}".format(folder, folder_content))
        for content in folder_content:
            if not(os.path.isfile(os.path.join(folder, content))):
                logger.info("Content is not a file and is ignored: {}".format(content))
            else:
                try:
                    if l_input_files_provided:
                        if content not in l_files:
                            logger.info("Content ignored because not in the datasets files: {}"
                                        "".format(content))
                            continue
                    filename_info = interpret_data_filename(content)
                    if filename_info is None:
                        continue
                    if filename_info["target"] != self.target_name:
                        logger.warning("Content target is not the provided target "
                                       "and is ignored: {}".format(content))
                        continue
                    key = build_dataset_key(filename_info["instrument"],
                                            number=filename_info["number"])
                    if filename_info["type"] == "LC":
                        self.lc_datasets[key] = LightCurve(content, data_folder=folder)
                        logger.info("Content accepted as LC datasets files and as been loaded: {}\n"
                                    "".format(content))
                    elif filename_info["type"] == "RV":
                        self.rv_datasets[key] = RV(content, data_folder=folder)
                        logger.info("Content accepted as RV datasets files and as been loaded: {}\n"
                                    "".format(content))
                    elif filename_info["type"] == "SED":
                        logger.warning("Data file type SED not implemented yet.")
                        continue
                except:
                    raise

    def get_LC_dataset_keys(self):
        """Return the list of light-curve dataset_key available."""
        return list(self.lc_datasets.keys())

    def get_RV_dataset_keys(self):
        """Return the list of light-curve dataset_key available."""
        return list(self.rv_datasets.keys())

    def get_dataset_keys(self):
        """Return a dictionnary with the lists of LC, RV (and SED) dataset_key available."""
        return {"LC": self.get_LC_dataset_keys(),
                "RV": self.get_RV_dataset_keys()}

    def get_LC_dataset_keys_perinstrument(self):
        """Return a dictionnary with the lists of LC dataset_key per isntrument."""
        lc_keys = self.get_LC_dataset_keys()
        result = {}
        for key in lc_keys:
            key_info = interpret_dataset_key(key)
            if key_info["instrument"] in result.keys():
                result[key_info["instrument"]].append(key)
            else:
                result[key_info["instrument"]] = [key]

    def get_RV_dataset_keys_perinstrument(self):
        """Return a dictionnary with the lists of LC dataset_key per isntrument."""
        rv_keys = self.get_RV_dataset_keys()
        result = {}
        for key in rv_keys:
            key_info = interpret_dataset_key(key)
            if key_info["instrument"] in result.keys():
                result[key_info["instrument"]].append(key)
            else:
                result[key_info["instrument"]] = [key]

    def isin_LC_datasets(self, key):
        """Indicate if the LC dataset designed by key is exisiting and loaded."""
        return key in self.lc_datasets

    def isin_RV_datasets(self, key):
        """Indicate if the RV dataset designed by key is exisiting and loaded."""
        return key in self.rv_datasets

    def plot_LC(dataset_key=None):
        """
        Plot a specific light-curve data set or all of them.

        To plot a specific LC dataset one should provide the dataset_key which is name of the
        instrument (followed by _number is several datasets from the same instrument). For example
        "K2".

        ----

        Arguments:
            dataset_key : string, optional,
                Key indicating which dataset you want to plot. If not provided the function plot all
                the LC dataset in different sub-windows.
        """
        raise NotImplementedError

    def plot_RV():
        """
        Plot a specific radial velocity data set or all of them.

        To plot a specific RV dataset one should provide the dataset_key which is name of the
        instrument (followed by _number is several datasets from the same instrument). For example
        "SOPHIE".

        ----

        Arguments:
            dataset_key : string, optional,
                Key indicating which dataset you want to plot. If not provided the function plot all
                the RV dataset in different sub-windows.
        """
        raise NotImplementedError


class ExoP_timeserie():
    """
    Exoplanet time-serie data class.

    This class should not be instanciated directly it's a parent class for the classes LightCurve,
    RV (and SED) to define common attributes and method for example the __init__ method of
    ExoP_timeserie should be called at the beginning of the __init__ method of LightCurve and RV
    classes.
    """

    target_name = None
    file_name = None
    folder = None
    instrument_type = None
    instrument_name = None
    data = None  # Pandas.Dataframe
    flags_list = []
    _mandatory_columns = ["time"]  # Not sure if I should put time here if pandas time serie

    def __init__(self, filename, main_data_folder=input_data_folder, data_folder=None):
        """
        Create an ExoP_timeserie instance.

        This class is not supposed to be instanciate directly. Use the LightCurve or RV classes.

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
        filename_info = interpret_data_filename(filename)

        if filename_info is None:
            raise ValueError("The file name doesn't correspond to the naming convention."
                             "The creation of the instance is not possible.")

        self.file_name = filename
        self.target_name = filename_info["target"]

        if data_folder is not None:
            folder = data_folder
        else:
            folder = os.path.join(main_data_folder, self.target_name)
        self.folder = folder


class LightCurve(ExoP_timeserie):
    """
    Light-curve class.

    Instances will contain the light-curve data of one dataset in the data attribute.
    It also contains functions to visualize (plot) and manipulate the light-curve (cut around the
    transit, detrend)
    """

    instrument_type = "transit"
    ExoP_timeserie._mandatory_columns.extend(["flux", "flux_err"])

    def __init__(self, filename, main_data_folder=input_data_folder, data_folder=None):
        """
        Create a LightCurve instance which contains the content of a LC data file.

        Look at the content of the file given by filename provided as input. There is two ways to
        provide the folder where filename is:
            - main_data_folder and target: You provide the data_folder which is made to receive the
            data from all the targets. It should contain a folder name after the target you want to
            study and which contain all the data. The name of the target is in the filename
            - data_folder: You provide directly the folder where the data are.

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
        ExoP_timeserie.__init__(self, filename, main_data_folder=main_data_folder,
                                data_folder=data_folder)
        self._read()

    def _read(self, skip_rows=1):
        """
        Read light curve into a pandas database.

        path should alwasy be the same...or given by person
        file name should denine the object and the run (type of analysis)
        need to define format of file to know how many rows to skip
        the name of the file is an identification of the filter but if 2 ground based instruments
        with same filter we might need to identified them as diferent
        """
        file_path = os.path.join(self.folder, self.file_name)
        # we can also read the header from the file with
        # lc = pd.read_table('cuttransits.txt', delim_whitespace=True, header=0, index_col=0)
        self.data = pd.read_table(file_path,
                                  delim_whitespace=True,
                                  names=["time", "flux", "flux_err", "inst_flag"],
                                  index_col=0,
                                  skiprows=skip_rows)
        # to acces the colum values lc['time'], lc['flux'], lc['flux_err']
        # they will come indexit to the time but when we transformed them into numpy
        # np.asarray(lc['inst_flag']) it is just the column
        # to have a  quick statistic summary of your data
        # lc.describe()
        self.data["inst_flag"].fillna(0, inplace=True)

    def plot(self):
        """
        Plot function to visualise the data.

        This is not very pretty but it plots the flux versus time and the error bars
        """
        self.data.plot(y="flux", yerr="flux_err")
        plt.show()


class RV(ExoP_timeserie):
    """
    Radial velocities class.

    Instances will contain the radial velocity data of one dataset in the data attribute.
    It also contains functions to visualize (plot) and manipulate the rvs (??)
    """

    instrument_type = "rv"
    ExoP_timeserie._mandatory_columns.extend(["RV", "RV_err"])

    def __init__(self, filename, main_data_folder=input_data_folder, data_folder=None):
        """
        Create a RV instance which contains the content of a Radial velocity data file.

        Look at the content of the file given by filename provided as input. There is two ways to
        provide the folder where filename is:
            - main_data_folder and target: You provide the data_folder which is made to receive the
            data from all the targets. It should contain a folder name after the target you want to
            study and which contain all the data. The name of the target is in the filename
            - data_folder: You provide directly the folder where the data are.
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
        ExoP_timeserie.__init__(self, filename, main_data_folder=main_data_folder,
                                data_folder=data_folder)
        self._read()

    def _read(self, skip_rows=1):
        """
        Read radial velocities into a pandas database.

        path should alwasy be the same...or given by person
        file name should denine the object and the run (type of analysis)
        need to define format of file to know how many rows to skip
        the name of the file is an identification of the filter but if 2 ground based instruments
        with same filter we might need to identified them as diferent
        """
        file_path = os.path.join(self.folder, self.file_name)
        # we can also read the header from the file with
        # lc = pd.read_table('cuttransits.txt', delim_whitespace=True, header=0, index_col=0)
        self.data = pd.read_table(file_path,
                                  delim_whitespace=True,
                                  names=["time", "rv", "rv_err", "inst_flag"],
                                  index_col=0,
                                  skiprows=skip_rows)
        # to acces the colum values lc['time'], lc['flux'], lc['flux_err']
        # they will come indexit to the time but when we transformed them into numpy
        # np.asarray(lc['inst_flag']) it is just the column
        # to have a  quick statistic summary of your data
        # lc.describe()
        self.data["inst_flag"].fillna(0, inplace=True)

    def plot(self):
        """
        Plot function to visualise the data.

        This is not very pretty but it plots the flux versus time and the error bars
        """
        self.data.plot(y="rv", yerr="rv_err")
        plt.show()
