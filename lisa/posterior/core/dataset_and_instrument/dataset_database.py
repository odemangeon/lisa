#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
dataset_database module.

The objective of this package is to provides the DatasetDatabase and DatasetDbAttr classes.
The DatasetDatabase class define a database to store and query the datasets considered for the analysis.
The DatasetDbAttr class is an interface class created to provide the dataset_db property to the
lisa.posterior.core.posterior.Posterior class. This property is a DatasetDatabase instance.
"""
from logging import getLogger
# from os.path import join, isfile
# from re import split

from .manager_dataset_instrument import Manager_Inst_Dataset
from .dataset import Core_Dataset
from ....tools.name import Named
from ....tools.dico_database import Nesteddict_wfixellvlnb, init_result, add_obj_in_result
from ....tools.database_with_instrument_level import check_instfullcat
from ....tools.default_folders_data_run import RunFolder, DataFolder
# from ....tools.miscellaneous import interpret_data_filename

## Logger object
logger = getLogger()

manager_inst = Manager_Inst_Dataset()
manager_inst.load_setup()


class Nesteddict_defgetitem(Nesteddict_wfixellvlnb):

    def __getitem__(self, key):
        if key in self:
            return super(Nesteddict_defgetitem, self).__getitem__(key)
        else:
            if ((len(self) == 1) and (key == ".")) or (key == "1st"):
                return self[list(self.keys())[0]]
            elif (self.lvl == 2) and isinstance(key, int):
                return self[str(key)]
            else:
                try:
                    if self.lvl == 0:
                        fileinfo = manager_inst.interpret_data_filename(key, raise_error=True)
                        inst_fullcat = fileinfo["inst_fullcat"]
                        inst_name = fileinfo["inst_name"]
                        number = fileinfo["number"]
                        return self[inst_fullcat][inst_name][number]
                    else:
                        raise KeyError
                except (KeyError, ValueError):  # keyError from the self[inst_fullcat][inst_name][number] and ValueError from manager_inst.interpret_data_filename(key, raise_error=True)
                    return super(Nesteddict_defgetitem, self).__getitem__(key)

    def __missing__(self, key, cls=None):
        if key == ".":
            raise KeyError("'.' can only be used when the len of the dictionnary is 1.")
        else:
            return super(Nesteddict_defgetitem, self).__missing__(key, cls)


class DatasetDatabase(Nesteddict_defgetitem, Named, RunFolder, DataFolder):
    """Database which contains all the datasets used for the analysis.

    In standard use you are not supposed to handle this class directly. Datasets should be added
    throught the dataset file, using the lisa.posterior.core.posterior.Posterior.load_datasetsfile
    method.
    """
    def __init__(self, object_name, lock=None):
        # Initialise the name of the datatabase
        Named.__init__(self, name=object_name)
        # Initialise the run folder
        RunFolder.__init__(self, run_folder=None)
        # Initialise the dataset folder
        DataFolder.__init__(self, data_folder=None)
        # Initialise the database (Nesteddict_defgetitem)
        Nesteddict_defgetitem.__init__(self, nb_lvl=3, lock=lock, ordered=True)

    def __missing__(self, key, cls=None):
        return super(DatasetDatabase, self).__missing__(key, cls=Nesteddict_defgetitem)

    @property
    def object_name(self):
        """Return the name of the object studied by the datasets in this database."""
        return self.name.get(include_prefix=False, code_version=False)

    def _add_a_dataset(self, dataset, force=False):
        """Add a dataset to the dataset database.

        See also _add_a_dataset_from_path and _add_datasets_from_listdatasetpath methods

        :param Dataset dataset: Instance of a subclass of Dataset.
        :param bool force: True to force the addition of the dataset
        """
        if self.locked:
            raise ValueError("The dataset dabase has been locked you can not add a new dataset.")
        inst_fullcat = dataset.instrument.full_category
        inst_name = dataset.instrument.get_name()
        number = dataset.number
        if str(number) in self[inst_fullcat][inst_name]:
            if not(force):
                logger.error("Dataset {} already exist in the database, it will not be added."
                             "".format(inst_fullcat + '_' + inst_name + '_' + str(number)))
                raise ValueError("The number of the dataset is {}. This number correspond to an "
                                 "alredy added dataset".format(number))
            else:
                logger.error("Dataset {} already exist in the database, it will be replaced."
                             "".format(inst_fullcat + '_' + inst_name + '_' + str(number)))
        self[inst_fullcat][inst_name][str(number)] = dataset

    def isavailable_dataset(self, dataset):
        """Return True if dataset corresponds to a dataset that is in the database.

        :param str/Dataset dataset: String giving the filename of the dataset or the dataset itself.
        """
        if isinstance(dataset, str):
            filename_info = Core_Dataset.interpret_data_filename(dataset)
            inst_fullcat = filename_info["inst_fullcat"]
            inst_name = filename_info["inst_name"]
            number = filename_info["number"]
        elif isinstance(dataset, Core_Dataset):
            inst_fullcat = dataset.instrument.full_category
            inst_name = dataset.instrument.get_name()
            number = dataset.number
        else:
            raise ValueError("{} is neither a dataset instance nor a dataset file name."
                             "".format(dataset))
        if inst_fullcat in self:
            if inst_name in self[inst_fullcat]:
                if str(number) in self[inst_fullcat][inst_name]:
                    return True
        else:
            return False

    def rm_dataset(self, inst_fullcat, inst_name, number=0):
        """Remove a dataset from the the dataset database.

        :param str inst_fullcat: Full Category of instrument associated to the dataset you want to remove
        :param str inst_name: Name of the instrument associated to the dataset you want to remove
        :param int number: Number associated to the dataset you want to remove.
        """
        if self.locked:
            raise ValueError("The dataset dabase has been locked you can not remove datasets.")
        self[inst_fullcat][inst_name].pop(str(number))
        if len(self[inst_fullcat][inst_name]) == 0:
            self[inst_fullcat].pop(inst_name)
            if len(self[inst_fullcat]) == 0:
                self.pop(inst_fullcat)

    # Now I request the addition of dataset to be done with the dataset file because like that I can
    # specify and pass the information about the name of the instrument model and the noise model
    def _add_a_dataset_from_path(self, datafile_path, load_setup=False, force=False):
        """Add a dataset designated by its path to the dataset database.

        See also _add_a_dataset and _add_datasets_from_listdatasetpath methods

        :param str datafile_path: path to the dataset file.
        :param bool load_setup: True if you want to manager instrument to load the inst_and_dataset_setup
            file.
        :param bool force: True to force the addition of the dataset
        """
        file_path = self.look4datafile(datafile_path)
        if file_path is None:
            raise ValueError("File {} not found".format(datafile_path))
        if load_setup:
            manager_inst.load_setup()
        self._add_a_dataset(manager_inst.create_dataset(file_path), force=force)
        logger.info("dataset added to the database: {}".format(datafile_path))

    def _add_datasets_from_listdatasetpath(self, l_dataset_path, force=False):
        """Add the datasets specified in a list of dataset paths to the database.

        See also _add_a_dataset and _add_a_dataset_from_path methods

        :param list_str l_dataset_path: List of path to dataset files to be added to the database.
        :param bool force: True to force the addition of the datasets
        """
        for filepath in l_dataset_path:
            self._add_a_dataset_from_path(filepath, force=force)

    def get_datasets(self, inst_name=None, inst_fullcat=None, sortby_instcat=False,
                     sortby_instname=False, sortby_nb=False):
        """Return datasets from the database.

        :param str/None inst_name: Name of the instrument associated to the dataset(s) you want. If None,
            all available instrument names are considered.
        :param str/None inst_fullcat: Full Category of instrument(s) associated to the dataset(s) you want. If None,
            all available instrument categories are considered.
        :param bool sortby_instcat: Specify the format of the output. If true, all instrument categories
            matching the request will be merged in the same list. If False, all instrument categories
            matching the request will have there own key in a dictionary.
        :param bool sortby_instname: Specify the format of the output. If true, all instrument names
            matching the request will be merged in the same list. If False, all instrument names
            matching the request will have there own key in a dictionary.
        :param bool sortby_nb: Specify the format of the output. If true, all dataset numbers
            matching the request will be merged in the same list. If False, all dataset numbers
            will have there own key in a dictionary.
        :return list/dictionary_of_Datasets res: All the dataset instances matching the request (inst_name, inst_fullcat).
            The format can be a list or a dictionary depending on the values passed to sortby_instcat,
            sortby_instname, sortby_nb.
        """
        return self.get_lvl3_values(level1_key=inst_fullcat, level2_key=inst_name,
                                    sortby_lvl1key=sortby_instcat, sortby_lvl2key=sortby_instname,
                                    sortby_lvl3key=sortby_nb)

    @property
    def inst_fullcategories(self):
        """Return the list of the categories of instruments associated to the dataset in the database."""
        return list(self.keys())

    @property
    def inst_categories(self):
        """Return the list of the categories of instruments associated to the dataset in the database."""
        res = []
        for inst_fullcat in self.inst_fullcategories:
            inst_cat, inst_subcat = manager_inst.interpret_inst_fullcat(inst_fullcat=inst_fullcat)
            res.append(inst_cat)
        return res

    def get_instnames(self, inst_fullcat=None, sortby_instcat=False):
        """Return the names of instruments used by the datasets in the database.

        :param str/None inst_fullcat:  Full Category of instrument(s) associated to the instrument name(s) you want.
            If None, all available instrument categories are considered.
        :param bool sortby_instcat: Specify the format of the output. If true, all instrument categories
            matching the request will be merged in the same list. If False, all instrument categories
            matching the request will have there own key in a dictionary.
        :return list/dict_of_str res: All the instrument names matching the request (inst_fullcat). The
            format can be a list or a dictionary depending on the values passed to sortby_instcat.
        """
        return self.get_lvl2_keys(level1_key=inst_fullcat, sortby_lvl1key=sortby_instcat)

    def get_instruments(self, inst_name=None, inst_fullcat=None,
                        sortby_instname=False, sortby_instcat=False):
        """Return Core_Instrument subclass instances used by the datasets in the database.

        :param str/None inst_name: Name of the instrument you want. If None, all available instrument
            names are considered.
        :param str/None inst_fullcat: Category of instrument(s) associated to the instrument(s) you want.
            If None, all available instrument categories are considered.
        :param bool sortby_instcat: Specify the format of the output. If true, all instrument categories
            matching the request will be merged in the same list. If False, all instrument categories
            matching the request will have there own key in a dictionary.
        :param bool sortby_instname: Specify the format of the output. If true, all instrument names
            matching the request will be merged in the same list. If False, all instrument names
            matching the request will have there own key in a dictionary.
        :return list/dict_of_Core_Instrument: All the available instruments (Core_Instrument subclass
            instances) matching the request (inst_name, inst_fullcat). The format can be a list or a dictionary
            depending on the values passed to sortby_instcat and sortby_instname.
        """
        inst_fullcat, inst_name = check_instfullcat(self, inst_name=inst_name, inst_fullcat=inst_fullcat)
        result = init_result(sortby_lvl1key=sortby_instcat, sortby_lvl2key=sortby_instname,
                             default_value=[])
        if inst_name is None:
            iter_instnames = self.get_instnames(inst_fullcat=inst_fullcat, sortby_instcat=True)
        else:
            iter_instnames = {inst_fullcat: [inst_name]}
        for inst_fullcat, l_instname in iter_instnames.items():
            for inst_name in l_instname:
                instrument = self[inst_fullcat][inst_name]["1st"].instrument
                add_obj_in_result(result, instrument, lvl1_key=inst_fullcat, lvl2_key=inst_name,
                                  type_finallvl=list)
        if not(sortby_instname or sortby_instcat):
            if len(result) == 1:
                return result[0]
        return result

    def get_datasetnbs(self, inst_name=None, inst_fullcat=None,
                       sortby_instcat=False, sortby_instname=False):
        """Return the number(s) of the datasets int the database.

        :param str/None inst_name: Name of the instrument associated to the datasets of which you want
            the numbers. If None, all available instrument names are considered.
        :param str/None inst_fullcat: Full Category of instrument(s) associated to the dataset(s) of which you want
            the numbers. If None, all available instrument categories are considered.
        :param bool sortby_instcat: Specify the format of the output. If true, all instrument categories
            matching the request will be merged in the same list. If False, all instrument categories
            matching the request will have there own key in a dictionary.
        :param bool sortby_instname: Specify the format of the output. If true, all instrument names
            matching the request will be merged in the same list. If False, all instrument names
            matching the request will have there own key in a dictionary.
        :return list/dict_of_int: All the available dataset numbers matching the request (inst_name,
            inst_fullcat). The format can be a list or a dictionary depending on the values passed to sortby_instcat
            and sortby_instname.
        """
        inst_fullcat, inst_name = check_instfullcat(self, inst_name=inst_name, inst_fullcat=inst_fullcat)
        return self.get_lvl3_keys(level1_key=inst_fullcat, level2_key=inst_name,
                                  sortby_lvl1key=sortby_instcat, sortby_lvl2key=sortby_instname)

    def get_datasetnames(self, inst_name=None, inst_fullcat=None,
                         sortby_instcat=False, sortby_instname=False):
        """Return the name of the datasets in the database.

        :param str/None inst_name: Name of the instrument associated to the datasets of which you want
            the names. If None, all available instrument names are considered.
        :param str/None inst_fullcat: Full Category of instrument(s) associated to the dataset(s) of which you want
            the names. If None, all available instrument categories are considered.
        :param bool sortby_instcat: Specify the format of the output. If true, all instrument categories
            matching the request will be merged in the same list. If False, all instrument categories
            matching the request will have there own key in a dictionary.
        :param bool sortby_instname: Specify the format of the output. If true, all instrument names
            matching the request will be merged in the same list. If False, all instrument names
            matching the request will have there own key in a dictionary.
        :return list/dict_of_int: All the available dataset names matching the request (inst_name,
            inst_fullcat). The format can be a list or a dictionary depending on the values passed to sortby_instcat
            and sortby_instname.
        """
        inst_fullcat, inst_name = check_instfullcat(self, inst_name=inst_name, inst_fullcat=inst_fullcat)
        result = init_result(sortby_lvl1key=sortby_instcat, sortby_lvl2key=sortby_instname,
                             default_value=[])
        list_dataset = self.get_datasets(inst_name=inst_name, inst_fullcat=inst_fullcat,
                                         sortby_instcat=False, sortby_instname=False,
                                         sortby_nb=False)
        for dataset in list_dataset:
            instrument = dataset.instrument
            add_obj_in_result(result, dataset.dataset_name, lvl1_key=instrument.category,
                              lvl2_key=instrument.get_name(), type_finallvl=list)
        return result


class DatasetDbAttr(object):
    """DatasetDbAttr is an Interface class for Posterior.

    It provide a dataset_db property which is a DatasetDatabase instance and the methods to define if.
    See the DatasetDatabase class for more information about the behavior of a DatasetDatabase instance.
    """
    def __init__(self, dataset_db=None):
        # 1. Initialise the dataset_db property
        self.dataset_db = dataset_db
        # 2. Make sure that this class is not used directly
        if type(self) is DatasetDbAttr:
            raise NotImplementedError("DatasetDbAttr should not be instanciated !")

    @property
    def dataset_db(self):
        """The DatasetDatabase instance (see lisa.posterior.core.dataset_and_isntrument.dataset_database)."""
        return self.__dataset_db

    @dataset_db.setter
    def dataset_db(self, dataset_db):
        """Set the dataset_db property."""
        if self.isdefined_datasetdb:
            logger.warning("The dataset database has already been defined for instance {} of "
                           "class {}. One should not redefined it, so set command is ignored."
                           "".format(self.get_name(), self.__class__.__name__))
            raise Warning("The dataset database has already been define set command Ignored")
        else:
            if dataset_db is None:
                logger.debug("No dataset database provided for instance {} of class {}."
                             "".format(self.get_name(), self.__class__.__name__))
            else:
                if isinstance(dataset_db, DatasetDatabase):
                    logger.debug("The dataset database of instance {} of class {} set to {}."
                                 "".format(self.get_name(), self.__class__.__name__, dataset_db))
                    self.__dataset_db = dataset_db
                else:
                    raise ValueError("dataset_db should be a DatasetDatabase instance")

    @property
    def isdefined_datasetdb(self):
        """Return True if a dataset_db is defined."""
        if hasattr(self, "dataset_db"):
            return self.dataset_db is not None
        else:
            return False
