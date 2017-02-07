#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
manager_dataset_instrument module.

The objective of this module is used to manage the subclasses of the Instrument and Dataset classes.

@DONE:
    - get_filename_from_file_path: Doc and UT
    - interpret_data_filename: Doc and UT
    - __Mgr.__init__: UT
    - __Mgr.set_dataset_for_inst_type: UT
    - __Mgr.get_available_inst_type: UT
    - __Mgr._reset_dataset_for_inst_type: Doc and UT
    - __Mgr.load_setup: Doc but No UT because depend on the content of the setup file
    - __Mgr.get_dataset_subclass: Doc an dUT
    - __Mgr._reset_available_inst: Doc and UT
    - __Mgr.get_available_inst_name: Doc and UT
    - __Mgr.add_available_inst: Doc and UT
    - __Mgr.get_instrument_instance: Doc and UT
    - __Mgr.is_available_inst: Doc and UT
    - __Mgr.create_dataset: Doc
    - Manager_Inst_Dataset.__init__: Doc and UT
    - Manager_Inst_Dataset.__gettattr__: Doc and UT

@TODO:
    - UT __Mgr.create_dataset
"""
import logging
import os.path
from ....software_parameters import setupfile_dataset_inst
from .instrument import _Default_Instrument

## Logger
logger = logging.getLogger()


def get_filename_from_file_path(file_path):
    """Return the filename of a dataset given its file_path.
    ----
    Arguments:
        file_path   : string,
            Path to the dataset file.

    Returns:
        file_name   : string,
            Name of the file extracted from the file_path.
    """
    return os.path.basename(file_path)


def interpret_data_filename(data_file_name):
    """
    Interpret data file name.

    If the format of the data file name is recognized the function return a dictionnary (see
    Returns below) otherwise return None.
    ----
    Arguments:
        data_file_name : string,
            Data file name, should be in the format insttype_object_instname(_number).*

    Returns:
        dictionnary with the interpration of the filename which contains the following keys:
            - object : name of the object observed with the data
            - inst_type : type of instrument used to take the data. e.g. "LC", "RV" or "SED"
            - inst_name : instrument name
            - number : give the number of the data file if there is several data files of the
                same object observed with the same instrument
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


class Manager_Inst_Dataset(object):
    """docstring for Manager_Inst_Dataset Singleton class."""

    class __Mgr(object):
        """docstring for __Mgr private class of Singleton class Manager_Inst_Dataset.

        For more information see Manager_Inst_Dataset class.
        """
        def __init__(self):
            """__Mgr init method.

            For more information see Manager_Inst_Dataset init method.
            """
            self.__dataset_for_inst = dict()
            self.__available_inst = dict()

        def _reset_dataset_for_inst_type(self):
            """Reset database giving Dataset subclass associated to instrument type."""
            self.__dataset_for_inst = dict()

        def set_dataset_for_inst_type(self, inst_type, dataset_subclass):
            """Add a Dataset subclass to a given instrument type.
            ----
            Arguments:
                inst_type : string,
                    Type of the instrument.
                dataset_subclass : Subclass of Dataset class,
                    Subclass of Dataset class that you want to associate to the instrument type.
            """
            self.__dataset_for_inst.update({inst_type: dataset_subclass})

        def get_available_inst_type(self):
            """Returns the list of available instrument types.
            ----
            Returns:
                list of string, giving the available instrument types
            """
            return list(self.__dataset_for_inst.keys())

        def load_setup(self):
            """Load the configuration of instruments and datasets define in the setup file.

            Association of instrument types and Dataset subclasses but also available instrument
            instances. The setup file is define in the software_parameters module.
            """
            exec(open(setupfile_dataset_inst).read())

        def get_dataset_subclass(self, inst_type):
            """Return Dataset subclass associated to a given instrument type.
            ----
            Arguments:
                inst_type           : string,
                    Gives the instrument type.
            Returns:
                Dataset_Subclass    : class,
                    Sub-class of Dataset associated with the instrument type provided.
            """
            return self.__dataset_for_inst[inst_type]

        def validate_inst_type(self, inst_type):
            """Check if inst_type refers to an available subclass of Instrument.
            ----
            Returns:
                True if inst_type is an available instrument type. False otherwise.
            """
            return inst_type in self.get_available_inst_type()

        def _reset_available_inst(self):
            """Reset database of available instrument instance."""
            self.__available_inst = dict()

        def get_available_inst_name(self):
            """Returns the list of available instrument instances.
            ----
            Returns:
                list of string, giving the available instrument instance names.
            """
            return list(self.__available_inst.keys())

        def add_available_inst(self, inst_instance):
            """Add an instance of an Instrument subclass to the list of available instrument.

            This method checks that the instrument type provided is a valid one before adding the
            instance.
            ----
            Arguments:
                instrument_instance : Instance of an Instrument Subclass,
                    instance of Instrument subclass of type inst_type
            """
            if not(self.validate_inst_type(inst_instance.inst_type)):
                raise ValueError("Provided inst_type ({}) is not amongst the valid instrument types"
                                 ": {}".format(self.get_available_inst_type()))
            self.__available_inst.update({inst_instance.name: inst_instance})

        def add_available_def_inst(self, inst_type, inst_name):
            """Add an instance of the _Default_Instrument class to the list of available instrument.

            This method checks that the instrument type provided is a valid one before adding the
            instance.
            ----
            Arguments:
                inst_type           : string,
                    Type of instrument
                inst_name           : string,
                    name of the instrument
            """
            self.add_available_inst(_Default_Instrument(inst_type, inst_name))

        def get_instrument_instance(self, inst_name):
            """Return Instrument Subclass instance associated to a given instrument name.
            ----
            Arguments:
                inst_name           : string,
                    Gives the instrument name.
            Returns:
                instrument_instance : class,
                    Instance of a Sub-class of Instrument associated with the instrument name
                    provided.
            """
            if not self.is_available_inst(inst_name):
                raise ValueError("Instrument named {} is not amongst the available instrument"
                                 " instances".format(self.get_available_inst_name()))
            return self.__available_inst[inst_name]

        def is_available_inst(self, inst_name):
            """Check if inst_name refers to an available instance of a subclass of Instrument.
            ----
            Returns:
                True if inst_type is an available instrument instance. False otherwise.
            """
            return inst_name in self.get_available_inst_name()

        def create_dataset(self, file_path):
            """Create the correct Dataset subclass instance from the file path.

            This function does:
                1. Check if the file exist
                2. Extract the file name from the file path
                3. Check and interpret the file name into object name, instrument name and type and
                  eventually number of the dataset
                4. Validate the instrument type
                5. Check if the inst_name correspond to an available instrument and if not create
                    a __Default_Instrument instance.
                6. Get instrument instance
                7. Get the correct subclass of Dataset from the instrument type
                8. Create the instance of this subclass and return it
            ----
            Arguments:
                file_path : string,
                    Path to the datafile.

            Returns:
                Instance of a Dataset Subclass with the instrument instance associated both
                    indicated by the name of the data file.
            """
            # 1
            if not(os.path.exists(file_path)):
                raise ValueError("file doesn't exist: {}".format(file_path))
            # 2
            file_name = get_filename_from_file_path(file_path)
            # 3
            filename_info = interpret_data_filename(file_name)
            if filename_info is None:
                raise ValueError("The file name doesn't correspond to the naming convention."
                                 "The creation of the instance is not possible.")
            # 4
            if not self.validate_inst_type(filename_info["inst_type"]):
                raise ValueError("The instrument type is not recognised: {}\nAvailable types: {}"
                                 "".format(filename_info["inst_type"],
                                           self.get_available_inst_type()))
            # 5
            if not self.is_available_inst(filename_info["inst_name"]):
                self.add_available_def_inst(filename_info["inst_type"], filename_info["inst_name"])
            # 6.
            inst_instance = self.get_instrument_instance(filename_info["inst_name"])
            # 7
            Dataset_SubClass = self.get_dataset_subclass(filename_info["inst_type"])
            # 8
            return Dataset_SubClass(file_path, inst_instance)

    instance = None

    def __init__(self):
        """Manager_Inst_Dataset init method (check if singleton exists and creates it if needed).

        The init method of the inside class does:
            1. Initialise the database giving Dataset subclass associated to instrument type
            2. Initialise the database of available instrument instances
        """
        if Manager_Inst_Dataset.instance is None:
            Manager_Inst_Dataset.instance = Manager_Inst_Dataset.__Mgr()

    def __getattr__(self, name):
        """Delegate every method or attribute call to the Singleton."""
        return getattr(self.instance, name)
