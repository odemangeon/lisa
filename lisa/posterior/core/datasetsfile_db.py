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
from logging import getLogger
from re import split
from collections import OrderedDict

from .dataset_and_instrument.manager_dataset_instrument import Manager_Inst_Dataset
from .database_instlevelsanddataset import DatabaseInstLvlDataset
from ...tools.miscellaneous import get_filename_from_file_path
from ...tools.lockable_dict import LockableDict
from .likelihood.manager_noise_model import Manager_NoiseModel

## Logger object
logger = getLogger()

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

    result = OrderedDict()
    with open(datasetsfile_path, 'r') as f:
        for line in f.readlines():
            line_striped = line.strip(" \n")
            logger.debug("raw line: {}striped line: {}".format(line, line_striped))
            if not(line_striped.startswith("#")) and (len(line_striped) > 0):
                logger.debug("Valid line ?: {}".format(True))
                dataset_path, inst_mod, noise_mod = split("\s+", line_striped)[:3]
                result[dataset_path] = {"inst_mod": inst_mod,
                                        "noise_mod": noise_mod}
            else:
                logger.debug("Valid line ?: {}".format(False))
    return result


class DatasetsFileDb(DatabaseInstLvlDataset):
    """docstring for DatasetsFile.

    Database with three levels inst_fullcat, inst_name, inst_model which contains the noise model subclass
    to be used for each instrument model.

    Attributes
    ----------
    instmodel4dataset : dictionary
        Provide the instrument model (values) to use for each dataset provided by their name (keys).

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

    def __init__(self, object_name, instmodel4dataset=None, lock=None):
        object_stored = "dataset, inst_model and noise model subclass"
        super(DatasetsFileDb, self).__init__(object_stored=object_stored, database_name=object_name,
                                             instmodel4dataset=instmodel4dataset, ordered=False,
                                             use_samelock=True, lock_dataset=lock, default=None)
        self.__path4name = LockableDict(lock=self.get_Lock_instance())

    @property
    def datasetsfile_path(self):
        """Return the path to the datasets_file."""
        return self.__datasetsfile_path

    @property
    def path4name(self):
        """Dictionnary giving the dataset file path for the dataset name"""
        return self.__path4name

    @property
    def dataset_filepaths(self):
        """Return the list of the paths to the datasets."""
        return list(self.path4name.values())

    def load(self, datasetsfile_path, load_setup=False):
        """Load the datasets provided in the datasets file into the dataset database.

        Also update the datasetsfile_content.
        """
        # Load the noise_model_setup_file.py to get all the available noise models
        if load_setup:
            mgr_noisemodel.load_setup()

        # Read the dataset file and load its content in dictionary dico_df.
        # Each keys is the path to a dataset file and contain a dictionary with two keys:
        # "inst_mod" giving the instrument model's name and "noise_mod" giving the noise model's
        # name
        dico_df = read_datasets_file(datasetsfile_path)
        logger.debug("Content of the datasets file: {}".format(dico_df))

        # For each dataset file
        for dataset_filepath in dico_df:
            # Extract the dataset name and filename from its path and file the path4name dictionary
            # giving the dataset path associated to its name
            dataset_filename = get_filename_from_file_path(dataset_filepath)
            dataset_name = mgr_inst_dst.dataset_name_from_file_name(dataset_filename)
            logger.debug("load info regarding dataset {} at path: {}".format(dataset_name,
                                                                             dataset_filepath))
            self.path4name[dataset_name] = dataset_filepath

            # Extract, instrument category, instrument name, ... from the dataset filename
            dataset_info = mgr_inst_dst.interpret_data_filename(dataset_filename)
            inst_fullcat = dataset_info["inst_fullcat"]
            inst_name = dataset_info["inst_name"]
            inst_model = dico_df[dataset_filepath]["inst_mod"]
            noise_model = dico_df[dataset_filepath]["noise_mod"]

            # Store the instrument model name associated to a dataset name in instmodel4dataset
            self.instmodel4dataset[dataset_name] = inst_model

            # Store the noise model subclass associated to an instrument model into datasetfile_db
            # (self)
            self[inst_fullcat][inst_name][inst_model] = (mgr_noisemodel.
                                                         get_noisemodel_subclass(noise_model))

        # Store the datasetsfile path into the read only datasetsfile_path property
        self.__datasetsfile_path = datasetsfile_path

    def get_noisemod4instmodfullname(self):
        """Return the dictionary giving the noise model name for each instrument model full_name."""
        res = OrderedDict()
        for inst_fullcat in self:
            for inst_name in self[inst_fullcat]:
                for inst_model in self[inst_fullcat][inst_name]:
                    valid, inst_subclass = mgr_inst_dst.validate_inst_fullcat(inst_fullcat)
                    instmod_fullname = inst_subclass.build_instmod_fullname(inst_model=inst_model, inst_name=inst_name, inst_fullcat=inst_fullcat)
                    res[instmod_fullname] = self[inst_fullcat][inst_name][inst_model].category
        return res

    # @property
    # def noisemodel_categories(self):
    #     """Return the list of noise model categories used."""
    #     return [noisemod.category for noisemod in set(self.get_objects())]  # Comes from DatabaseInstLevel


class DatasetsFileDbAttr(object):
    """docstring for DataSets."""
    def __init__(self, object_name, instmodel4dataset):
        self.__datasetsfile_db = DatasetsFileDb(object_name=object_name,
                                                instmodel4dataset=instmodel4dataset,
                                                lock=instmodel4dataset.get_Lock_instance())

    @property
    def datasetsfile_db(self):
        """Return the datasetsfile database"""
        return self.__datasetsfile_db
