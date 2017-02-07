#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
dataset_database module.

The objective of this package is to provides the core DatasetDatabase class.

@ DONE:
    -
@TODO:
    -
"""
from logging import getLogger
from collections import OrderedDict
from os.path import join, isfile

from .manager_dataset_instrument import Manager_Inst_Dataset
from .manager_dataset_instrument import interpret_data_filename
from .dataset import Dataset
from ....software_parameters import input_data_folder
from ....software_parameters import input_run_folder
from ....tools.miscellaneous import define_folder_withdefault, look4file_withdeffolder

logger = getLogger()

manager_dataset = Manager_Inst_Dataset()
manager_dataset.load_setup()


class DatasetDatabase(object):
    """docstring for DatasetDatabase."""
    def __init__(self, object_name):
        super(DatasetDatabase, self).__init__()
        # 1.
        ## Name of the object you are trying to modelize
        self.__object_name = object_name
        # 3.
        ## Folder where the program should look for dataset files by default: Initialise it
        self.__data_folder = None
        #
        ## Folder where the program should look for config files by default: Initialise it
        self.__run_folder = None
        ## Folder where the program should look for config files by default: Initialise it
        self._database = dict()

    def __getitem__(self, key):
        return self._database[key]

    @property
    def object_name(self):
        """Return the name of the object studied."""
        return self.__object_name

    @property
    def data_folder(self):
        """The data_folder is the folder where the program will look for the dataset files.
        It can be provided in two ways:
            - Via the folder defined in software_parameters: In this case the data_folder is
              automatically define as "input_data_folder/object_name". To use this you should assign
              "default"
            - Via the data_folder argument: You can provide any folder here via the data_folder
              argument.
        If not defined, return None.
        """
        return self.__data_folder

    @data_folder.setter
    def data_folder(self, data_folder="default"):
        """Set the data_folder attribute."""
        self.__data_folder = define_folder_withdefault(main_default_folder=input_data_folder,
                                                       object_name=self.object_name,
                                                       folder=data_folder)

    def isset_datafolder(self):
        """Tells if the data_folder attribute is defined."""
        return self.data_folder is not None

    @property
    def run_folder(self):
        """The run_folder is the folder where the program will look for config files and put
        outputs. It can be provided in two ways:
            - Via the folder defined in software_parameters: In this case the run_folder is
              automatically define as "input_run_folder/object_name". To use this you should assign
              "default"
            - Via the run_folder argument: You can provide any folder here via the run_folder
              argument.
        If not defined, return None.
        """
        return self.__run_folder

    @run_folder.setter
    def run_folder(self, run_folder="default"):
        """Set the run_folder attribute."""
        self.__run_folder = define_folder_withdefault(main_default_folder=input_run_folder,
                                                      object_name=self.object_name,
                                                      folder=run_folder)

    def isset_runfolder(self):
        """Tells if the run_folder attribute is defined."""
        return self.run_folder is not None

    def _add_a_dataset(self, dataset, force=False):
        """Add a dataset to the dataset database.
        ----
        Arguments:
            dataset : Subclass of Dataset object,
                Instance of a subclass of Dataset.
            force   : boolean, (default: False),
                True to force the addition of the dataset
        """
        inst_type = dataset.instrument.inst_type
        inst_name = dataset.instrument.name
        number = dataset.number
        if inst_type not in self._database:
            self._database.update({inst_type: {}})
        if inst_name not in self._database[inst_type]:
            self._database[inst_type].update({inst_name: OrderedDict()})
        if str(number) in self._database[inst_type][inst_name]:
            if not(force):
                logger.error("Dataset {} already exist in the database, it will not be added.")
                raise ValueError("The number of the dataset is {}. This number correspond to an "
                                 "alredy added dataset".format(number))
            else:
                logger.error("Dataset {} already exist in the database, it will be replaced.")
        self._database[inst_type][inst_name][str(number)] = dataset

    def isavailable_dataset(self, dataset):
        """Return if filename correspond to a dataset that is in the database.
        ----
        Arguments:
            filename : string,
                filename of the dataset.
        """
        if isinstance(dataset, str):
            filename_info = interpret_data_filename(interpret_data_filename)
            inst_type = filename_info["inst_type"]
            inst_name = filename_info["inst_name"]
            number = filename_info["number"]
        elif isinstance(dataset, Dataset):
            inst_type = dataset.instrument.inst_type
            inst_name = dataset.instrument.name
            number = dataset.number
        else:
            raise ValueError("{} is neither a dataset instance nor a dataset file name."
                             "".format(dataset))
        if inst_type in self._database:
            if inst_name in self._database[inst_type]:
                if number in self._database[inst_type][inst_name]:
                    return True
        else:
            return False

    def rm_dataset(self, inst_type, inst_name, number=0):
        """Remove a dataset from the the dataset database.
        ----
        Arguments:
            inst_type   : string,
                Type of instrument associated to the dataset you want to remove
            inst_name   : string,
                Name of the instrument associated to the dataset you want to remove
            number      : int, (default: 0)
                Number associated to the dataset you want to remove.
        """
        self._database[inst_type][inst_name].pop(str(number))
        if len(self._database[inst_type][inst_name]) == 0:
            self._database[inst_type].pop(inst_name)
            if len(self._database[inst_type]) == 0:
                self._database.pop(inst_type)

    def add_a_dataset_from_path(self, datafile_path, load_setup=False, force=False):
        """Add a dataset designated by its path to the dataset database.
        ----
        Arguments:
            datafile_path   : string,
                path to the data file.
            load_setup      : bool, (default: False)
                tell if you want to manager to laod the inst_and_dataset_setup file.
            force           : boolean, (default: False),
                True to force the addition of the dataset
        """
        found = isfile(datafile_path)
        if found:
            path = datafile_path
        else:
            if self.isset_datafolder:
                path = join(self.data_folder, datafile_path)
                found = isfile(path)
        if found:
            logger.debug("Dataset file found at path: {}".format(path))
        else:
            raise ValueError("File {} not found".format(datafile_path))
        if load_setup:
            manager_dataset.load_setup()
        self._add_a_dataset(manager_dataset.create_dataset(path), force=force)
        logger.info("dataset added to the database: {}".format(datafile_path))

    def add_datasets_from_datasetfile(self, path_datasets_file, load_setup=False, force=False):
        """Add the datasets specified in the datasets_file to the dataset database.
        ----
        Arguments:
            path_datasets_file  : string,
                path to the datasets file.
            load_setup          : bool, (default: False)
                tell if you want to manager to laod the inst_and_dataset_setup file.
            force               : boolean, (default: False),
                True to force the addition of the dataset
        """
        file_path = look4file_withdeffolder(file_path=path_datasets_file,
                                            default_folder=self.run_folder)
        if file_path is not None:
            list_files = []
            with open(file_path, 'r') as f:
                for line in f.readlines():
                    line_striped = line.strip(" \n")
                    logger.debug("raw line: {}striped line: {}".format(line, line_striped))
                    if not(line_striped.startswith("#")) and (len(line_striped) > 0):
                        logger.debug("line accepted as filename: {}".format(True))
                        list_files.append(line_striped)
                    else:
                        logger.debug("line accepted as filename: {}".format(False))
        else:
            error_msg = "file doesn't exist: {}".format(path_datasets_file)
            raise ValueError(error_msg)
        logger.debug("List of files to use: {}".format(list_files))
        if load_setup:
            manager_dataset.load_setup()
        for filepath in list_files:
            self.add_a_dataset_from_path(filepath, force=force)

    def get_dataset(self, inst_type, inst_name, number=None):
        """Return a dataset from the dataset database.

        Giving the caracteristics of the instrument used for the measurement and the number of the
        dataset this function will return the corresponding dataset.

        ----
        inst_type   : string,
            Type of instrument associated to the dataset you want to remove
        inst_name   : string,
            Name of the instrument associated to the dataset you want to remove
        number      : int, (default: 0)
            Number associated to the dataset you want to remove.
        """
        if number is None:
            str_number = list(self._database[inst_type][inst_name].keys())[0]
        else:
            str_number = str(number)
        return self._database[inst_type][inst_name][str_number]

    @property
    def datatypes_tosim(self):
        """Return the list of the types of instruments associated to the dataset in the database."""
        return list(self._database.keys())

    def get_instruments(self):
        """Return the list of the types of instruments associated to the dataset in the database."""
        instruments_dict = {}
        for inst_type in list(self._database.keys()):
            instruments_dict.update({inst_type: []})
            for inst_name in self._database[inst_type].keys():
                first_dataset = self.get_dataset(inst_type=inst_type, inst_name=inst_name)
                instruments_dict[inst_type].append(first_dataset.instrument)
        return instruments_dict


# def interpret_dataset_key(dataset_key):
#     """
#     Interpret dataset key.
#
#     ----
#
#     Arguments:
#         dataset_key : string,
#             dataset_key
#     Returns:
#         dictionnary with the interpration of the dataset key which contains the following keys:
#             - instrument : instrument name
#             - number : give the number of the data file if there is several data files from the
#               same instrument
#     """
#     cuts = dataset_key.split("_")
#     if len(cuts) > 2:
#         logging.warning("dataset_key not recognized. Should be in the format "
#                         "instrument_number. Got: {}".format(dataset_key))
#         return None
#     result = {"instrument": cuts[0]}
#     if len(cuts) == 2:
#         result["number"] = cuts[1]
#     elif len(cuts) == 1:
#         result["number"] = None
#     return result
#
#
# def build_dataset_key(instrument, number=None):
#     """
#     build dataset key.
#
#     ----
#
#     Arguments:
#         instrument : string,
#             instrument name
#         number : string, optional,
#             number of the dataset for this instrument
#     Returns:
#         dataset_key
#     """
#     separator = "_"
#     dataset_key = instrument
#     if number is not None:
#         dataset_key += separator + number
#     return dataset_key
