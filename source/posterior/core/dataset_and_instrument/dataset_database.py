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
from collections import defaultdict
from os.path import join, isfile

from .manager_dataset_instrument import Manager_Inst_Dataset
from .dataset import Dataset
from ....tools.name import Name
from ....tools.dico_database import Nesteddict_wfixellvlnb, init_result, add_obj_in_result
from ....tools.database_with_instrument_level import check_instcat
from ....tools.default_folders_data_run import RunFolder, DataFolder
from ....tools.miscellaneous import interpret_data_filename

## Logger object
logger = getLogger()

manager_inst = Manager_Inst_Dataset()
manager_inst.load_setup()


class Nesteddict_defgetitem(Nesteddict_wfixellvlnb):

    def __getitem__(self, key):
        if ((len(self) == 1) and (key == ".")) or (key == "1st"):
            return self[list(self.keys())[0]]
        else:
            if isinstance(key, int):
                return self[str(key)]
            else:
                return super(Nesteddict_defgetitem, self).__getitem__(key)

    def __missing__(self, key, cls=None):
        if key == ".":
            raise KeyError("'.' can only be used when the len of the dictionnary is 1.")
        else:
            return super(Nesteddict_defgetitem, self).__missing__(key, cls)


class DatasetDatabase(Nesteddict_defgetitem, Name, RunFolder, DataFolder):
    """docstring for DatasetDatabase."""
    def __init__(self, object_name):
        # 1.
        Name.__init__(self, name=object_name)
        # 2.
        RunFolder.__init__(self, run_folder=None)
        # 3.
        DataFolder.__init__(self, data_folder=None)
        # 4.
        Nesteddict_wfixellvlnb.__init__(self, nb_lvl=3, ordered=True)
        # 5.
        self.freeze = False

    def __missing__(self, key, cls=None):
        return super(DatasetDatabase, self).__missing__(key, cls=Nesteddict_defgetitem)

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
        if str(number) in self[inst_category][inst_name]:
            if not(force):
                logger.error("Dataset {} already exist in the database, it will not be added."
                             "".format(inst_category + '_' + inst_name + '_' + str(number)))
                raise ValueError("The number of the dataset is {}. This number correspond to an "
                                 "alredy added dataset".format(number))
            else:
                logger.error("Dataset {} already exist in the database, it will be replaced."
                             "".format(inst_category + '_' + inst_name + '_' + str(number)))
        self[inst_category][inst_name][str(number)] = dataset

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
        if inst_category in self:
            if inst_name in self[inst_category]:
                if number in self[inst_category][inst_name]:
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
        self[inst_category][inst_name].pop(str(number))
        if len(self[inst_category][inst_name]) == 0:
            self[inst_category].pop(inst_name)
            if len(self[inst_category]) == 0:
                self.pop(inst_category)

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
            if self.hasdata_folder:
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
        file_path = self.look4runfile(file_path=path_datasets_file)
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

    def get_datasets(self, inst_name=None, inst_cat=None, sortby_instcat=False,
                     sortby_instname=False, sortby_nb=False):
        """Return datasets from the dataset database."""
        return self.get_lvl3_values(level1_key=inst_cat, level2_key=inst_name,
                                    sortby_lvl1key=sortby_instcat, sortby_lvl2key=sortby_instname,
                                    sortby_lvl3key=sortby_nb)

    @property
    def inst_categories(self):
        """Return the list of the types of instruments associated to the dataset in the database."""
        return list(self.keys())

    def get_instnames(self, inst_cat=None, sortby_instcat=False):
        """Return the names of instruments.

        If inst_category provided return only the name of the instrument for this category.
        Otherwise return a dict which associate the list of instrument names to each instrument
        category available in the database.
        """
        return self.get_lvl2_keys(level1_key=inst_cat, sortby_lvl1key=sortby_instcat)

    def get_instruments(self, inst_name=None, inst_cat=None,
                        sortby_instname=False, sortby_instcat=False):
        """Return the dict of instruments used by the dataset in the database"""
        inst_cat, inst_name = check_instcat(self, inst_name=inst_name, inst_cat=inst_cat)
        result = init_result(sortby_lvl1key=sortby_instcat, sortby_lvl2key=sortby_instname,
                             default_value=[])
        if inst_name is None:
            iter_instnames = self.get_instnames(inst_cat=inst_cat, sortby_instcat=True)
        else:
            iter_instnames = {inst_cat: [inst_name]}
        # instnames_bycat = self.get_instnames(inst_cat=inst_cat, sortby_instcat)
        for inst_cat, l_instname in iter_instnames.items():
            for inst_name in l_instname:
                instrument = self[inst_cat][inst_name]["1st"].instrument
                add_obj_in_result(result, instrument, lvl1_key=inst_cat, lvl2_key=inst_name,
                                  type_finallvl=list)
        if not(sortby_instname or sortby_instcat):
            if len(result) == 1:
                return result[0]
        return result

    def get_datasetnbs(self, inst_name=None, inst_cat=None,
                       sortby_instcat=False, sortby_instname=False):
        """Return the numbers of the datasets."""
        inst_cat, inst_name = check_instcat(self, inst_name=inst_name, inst_cat=inst_cat)
        return self.get_lvl3_keys(level1_key=inst_cat, level2_key=inst_name,
                                  sortby_lvl1key=sortby_instcat, sortby_lvl2key=sortby_instname)

    def get_datasetnames(self, inst_name=None, inst_cat=None,
                         sortby_instcat=False, sortby_instname=False):
        """Return the dict of instruments used by the dataset in the database"""
        inst_cat, inst_name = check_instcat(self, inst_name=inst_name, inst_cat=inst_cat)
        result = init_result(sortby_lvl1key=sortby_instcat, sortby_lvl2key=sortby_instname,
                             default_value=[])
        list_dataset = self.get_datasets(inst_name=inst_name, inst_cat=inst_cat,
                                         sortby_instcat=False, sortby_instname=False,
                                         sortby_nb=False)
        for dataset in list_dataset:
            instrument = dataset.instrument
            add_obj_in_result(result, dataset.dataset_name, lvl1_key=instrument.category,
                              lvl2_key=instrument.name, type_finallvl=list)
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
