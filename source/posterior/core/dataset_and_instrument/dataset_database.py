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
from ....tools.name import Name
from ....tools.dico_database import get_content_2ndlevel, get_content_3ndlevel

logger = getLogger()

manager_inst = Manager_Inst_Dataset()
manager_inst.load_setup()


class DatasetDatabase(Name):
    """docstring for DatasetDatabase."""
    def __init__(self, object_name):
        super(DatasetDatabase, self).__init__(name=object_name)
        # 3.
        ## Folder where the program should look for dataset files by default: Initialise it
        self.__data_folder = None
        #
        ## Folder where the program should look for config files by default: Initialise it
        self.__run_folder = None
        ## Folder where the program should look for config files by default: Initialise it
        self._database = dict()
        #
        self.freeze = False

    def __getitem__(self, key):
        return self._database[key]

    @property
    def object_name(self):
        """Return the name of the object studied."""
        return self.name

    @property
    def freeze(self):
        """Return True is the database in frozen."""
        return self.__freeze

    @freeze.setter
    def freeze(self, boolean):
        """Return True is the database in frozen."""
        if not(isinstance(boolean, bool)):
            raise ValueError("freeze should be a boolean")
        self.__freeze = boolean

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
                                                       object_name=self.name,
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
                                                      object_name=self.name,
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
        if self.freeze:
            raise ValueError("The dataset dabase has been freezed you can not add a new dataset.")
        inst_category = dataset.instrument.category
        inst_name = dataset.instrument.name
        number = dataset.number
        if inst_category not in self._database:
            self._database.update({inst_category: {}})
        if inst_name not in self._database[inst_category]:
            self._database[inst_category].update({inst_name: OrderedDict()})
        if str(number) in self._database[inst_category][inst_name]:
            if not(force):
                logger.error("Dataset {} already exist in the database, it will not be added."
                             "".format(inst_category + '_' + inst_name + '_' + str(number)))
                raise ValueError("The number of the dataset is {}. This number correspond to an "
                                 "alredy added dataset".format(number))
            else:
                logger.error("Dataset {} already exist in the database, it will be replaced."
                             "".format(inst_category + '_' + inst_name + '_' + str(number)))
        self._database[inst_category][inst_name][str(number)] = dataset

    def isavailable_dataset(self, dataset):
        """Return True sif filename correspond to a dataset that is in the database.
        ----
        Arguments:
            dataset : string or Instance of Dataset Subclass,
                String giving the filename of the dataset or the dataset itself.
        """
        if isinstance(dataset, str):
            filename_info = interpret_data_filename(interpret_data_filename)
            inst_category = filename_info["inst_category"]
            inst_name = filename_info["inst_name"]
            number = filename_info["number"]
        elif isinstance(dataset, Dataset):
            inst_category = dataset.instrument.category
            inst_name = dataset.instrument.name
            number = dataset.number
        else:
            raise ValueError("{} is neither a dataset instance nor a dataset file name."
                             "".format(dataset))
        if inst_category in self._database:
            if inst_name in self._database[inst_category]:
                if number in self._database[inst_category][inst_name]:
                    return True
        else:
            return False

    def rm_dataset(self, inst_category, inst_name, number=0):
        """Remove a dataset from the the dataset database.
        ----
        Arguments:
            inst_category   : string,
                Type of instrument associated to the dataset you want to remove
            inst_name   : string,
                Name of the instrument associated to the dataset you want to remove
            number      : int, (default: 0)
                Number associated to the dataset you want to remove.
        """
        if self.freeze:
            raise ValueError("The dataset dabase has been freezed you can not remove datasets.")
        self._database[inst_category][inst_name].pop(str(number))
        if len(self._database[inst_category][inst_name]) == 0:
            self._database[inst_category].pop(inst_name)
            if len(self._database[inst_category]) == 0:
                self._database.pop(inst_category)

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
            manager_inst.load_setup()
        self._add_a_dataset(manager_inst.create_dataset(path), force=force)
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
            manager_inst.load_setup()
        for filepath in list_files:
            self.add_a_dataset_from_path(filepath, force=force)

    def get_dataset(self, inst_category, inst_name, number=None):
        """Return a dataset from the dataset database.

        Giving the caracteristics of the instrument used for the measurement and the number of the
        dataset this function will return the corresponding dataset.

        ----
        inst_category   : string,
            Type of instrument associated to the dataset you want to remove
        inst_name   : string,
            Name of the instrument associated to the dataset you want to remove
        number      : int, (default: 0)
            Number associated to the dataset you want to remove.
        """
        if number is None:
            str_number = list(self._database[inst_category][inst_name].keys())[0]
        else:
            str_number = str(number)
        return self._database[inst_category][inst_name][str_number]

    @property
    def inst_categories(self):
        """Return the list of the types of instruments associated to the dataset in the database."""
        return list(self._database.keys())

    def get_instnames(self, inst_category=None):
        """Return the names of instruments.

        If inst_category provided return only the name of the instrument for this category.
        Otherwise return a dict which associate the list of instrument names to each instrument
        category available in the database.
        """
        return get_content_2ndlevel(dico_db=self._database, level1_key=inst_category)

    def get_instruments(self):
        """Return the dict of instruments used by the dataset in the database"""
        instruments_dict = {}
        for inst_category in list(self._database.keys()):
            for inst_name in self._database[inst_category].keys():
                first_dataset = self.get_dataset(inst_category=inst_category, inst_name=inst_name)
                instruments_dict[inst_name] = first_dataset.instrument
        return instruments_dict

    def get_datasetnbs(self, inst_name=None, inst_category=None):
        """Return the numbers of the datasets.

        If inst_name provided return only the list of numbers of the datasets for this instrument.
        Else if inst_category provided (and not inst_name) return a dict giving for each instrument
        in this category the list of numbers associated.
        If neither inst_name nor inst_category, returns a 2 level dict giving for each category and
        each instrument in this category the list of numbers associated.
        """
        if (inst_name is not None) and (inst_category is None):
            inst_category = manager_inst.get_inst_category(inst_name=inst_name)
        return get_content_3ndlevel(dico_db=self._database, level1_key=inst_category,
                                    level2_key=inst_name)

    def get_datasetnames(self, inst_name=None, inst_category=None):
        """Return the dict of instruments used by the dataset in the database"""
        if (inst_name is not None) and (inst_category is None):
            inst_category = manager_inst.get_inst_category(inst_name=inst_name)
        result = []
        if inst_category is not None:
            iter_instcat = [inst_category, ]
        else:
            iter_instcat = self.inst_categories
        for cat in iter_instcat:
            if inst_name is not None:
                iter_inst_name = [inst_name, ]
            else:
                iter_inst_name = self.get_instnames(inst_category=cat)
            for name in iter_inst_name:
                nb_list = self.get_datasetnbs(inst_category=cat, inst_name=name)
                for nb in nb_list:
                    result.append("{}_{}_{}_{}".format(cat, self.object_name, name, nb))
        return result


class DatasetDbAttr(object):
    """docstring for ProvideDatasetDbAttr."""
    def __init__(self, dataset_db=None):
        # 1.
        self.dataset_db = dataset_db
        # 2.
        if type(self) is DatasetDbAttr:
            raise NotImplementedError("DatasetDbAttr should not be instanciated !")

    @property
    def dataset_db(self):
        """Return the dataset_datase."""
        return self.__dataset_db

    @dataset_db.setter
    def dataset_db(self, dataset_db):
        """Return the dataset_datase."""
        if self.hasdataset_db:
                logger.warning("The dataset database has already been defined for instance {} of "
                               "class {}. One should not redefined it, so set command is ignored."
                               "".format(self.name, self.__class__.__name__))
                raise Warning("The dataset database has already been define set command Ignored")
        else:
            if dataset_db is None:
                logger.debug("No dataset database provided for instance {} of class {}."
                             "".format(self.name, self.__class__.__name__))
            else:
                if isinstance(dataset_db, DatasetDatabase):
                    logger.debug("The dataset database of instance {} of class {} set to {}."
                                 "".format(self.name, self.__class__.__name__, dataset_db))
                    self.__dataset_db = dataset_db
                else:
                    raise ValueError("dataset_db should be a DatasetDatabase instance")

    @property
    def hasdataset_db(self):
        """Return True if a dataset_db is defined."""
        if hasattr(self, "dataset_db"):
            return self.dataset_db is not None
        else:
            return False

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
