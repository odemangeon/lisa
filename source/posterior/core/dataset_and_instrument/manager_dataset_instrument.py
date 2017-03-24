#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
manager_dataset_instrument module.

The objective of this module is used to manage the subclasses of the Core_Instrument and Dataset
classes.

@DONE:
    - get_filename_from_file_path: Doc and UT
    - interpret_data_filename: Doc and UT
    - __Mgr.__init__: UT
    - __Mgr.add_available_inst_category: UT
    - __Mgr.get_available_inst_category: UT
    - __Mgr._reset_inst_categories: Doc and UT
    - __Mgr.load_setup: Doc but No UT because depend on the content of the setup file
    - __Mgr.get_dataset_subclass: Doc an dUT
    - __Mgr._reset_available_inst: Doc and UT
    - __Mgr.get_available_inst_name: Doc and UT
    - __Mgr.add_available_inst: Doc and UT
    - __Mgr.get_instrument: Doc and UT
    - __Mgr.is_available_inst: Doc and UT
    - __Mgr.create_dataset: Doc
    - Manager_Inst_Dataset.__init__: Doc and UT
    - Manager_Inst_Dataset.__gettattr__: Doc and UT

@TODO:
    - UT __Mgr.create_dataset
"""
from logging import getLogger
from os.path import exists
from ....software_parameters import setupfile_dataset_inst
from ....tools.miscellaneous import interpret_data_filename, get_filename_from_file_path

## Logger
logger = getLogger()


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
            self.__available_inst_subclass = dict()
            self._Default_Instrument = None

        def _reset_inst_categories(self):
            """Reset database giving Dataset subclass associated to instrument category."""
            self.__dataset_for_inst = dict()
            self.__available_inst_subclass = dict()

        def _reset_available_inst(self):
            """Reset database of available instrument instance."""
            self.__available_inst = dict()

        def add_available_inst_category(self, inst_subclass, dataset_subclass):
            """Add a Dataset subclass to a given instrument category.
            ----
            Arguments:
                inst_category : string,
                    Type of the instrument.
                dataset_subclass : Subclass of Dataset class,
                    Subclass of Dataset class that you want to associate to the instrument category.
            """
            self.__available_inst_subclass.update({inst_subclass.category: inst_subclass})
            self.__dataset_for_inst.update({inst_subclass.category: dataset_subclass})

        def add_available_inst(self, inst_instance):
            """Add an instance of a Core_Instrument subclass to the list of available instrument.

            This method checks that the instrument category provided is a valid one before adding
            the instance.
            ----
            Arguments:
                instrument_instance : Instance of a Core_Instrument Subclass,
                    instance of Core_Instrument subclass of category inst_category
            """
            if not(self.validate_inst_category(inst_instance.category)):
                raise ValueError("Provided inst_category ({}) is not amongst the valid instrument "
                                 "categories: {}".format(self.get_available_inst_category()))
            self.__available_inst.update({inst_instance.name: inst_instance})

        def define_def_instrument_class(self, Default_Inst_class):
            """Define the class to be used for default instruments.
            """
            self._Default_Instrument = Default_Inst_class

        def add_available_def_inst(self, inst_category, name):
            """Add an instance of the Default_Instrument class to the list of available instrument.

            This method checks that the instrument category provided is a valid one before adding
            the instance.
            ----
            Arguments:
                inst_category           : string,
                    Type of instrument
                name           : string,
                    name of the instrument
            """
            params_model = self.get_inst_subclass(inst_category).params_model
            self.add_available_inst(self._Default_Instrument(category=inst_category,
                                                             name=name,
                                                             params_model=params_model))

        def load_setup(self):
            """Load the configuration of instruments and datasets define in the setup file.

            Association of instrument categories and Dataset subclasses but also available
            instrument instances. The setup file is define in the software_parameters module.
            """
            f = open(setupfile_dataset_inst)
            exec(f.read())
            f.close()
            logger.debug("Setup of Manager_Inst_Dataset Loaded")

        def get_available_inst_category(self):
            """Returns the list of available instrument categories.
            ----
            Returns:
                list of string, giving the available instrument categories
            """
            return list(self.__available_inst_subclass.keys())

        def get_available_inst_name(self):
            """Returns the list of available instrument instances.
            ----
            Returns:
                list of string, giving the available instrument instance names.
            """
            return list(self.__available_inst.keys())

        def validate_inst_category(self, inst_category):
            """Check if inst_category refers to an available subclass of Core_Instrument.
            ----
            Returns:
                True if inst_category is an available instrument category. False otherwise.
            """
            return inst_category in self.get_available_inst_category()

        def is_available_inst(self, inst_name):
            """Check if inst_name refers to an available instance of a subclass of Core_Instrument.
            ----
            Returns:
                True if inst_category is an available instrument instance. False otherwise.
            """
            return inst_name in self.get_available_inst_name()

        def get_dataset_subclass(self, inst_category):
            """Return Dataset subclass associated to a given instrument category.
            ----
            Arguments:
                inst_category           : string,
                    Gives the instrument category.
            Returns:
                Dataset_Subclass    : class,
                    Sub-class of Dataset associated with the instrument category provided.
            """
            return self.__dataset_for_inst[inst_category]

        def get_instrument(self, inst_name):
            """Return Core_Instrument Subclass instance associated to a given instrument name.
            ----
            Arguments:
                inst_name           : string,
                    Gives the instrument name.
            Returns:
                instrument_instance : class,
                    Instance of a Sub-class of Core_Instrument associated with the instrument name
                    provided.
            """
            if not self.is_available_inst(inst_name):
                raise ValueError("Instrument named '{}' is not amongst the available instrument"
                                 " instances {}".format(inst_name, self.get_available_inst_name()))
            return self.__available_inst[inst_name]

        def get_inst_subclass(self, inst_category):
            """Return Core_Instrument Subclass associated to a given instrument category.
            ----
            Arguments:
                inst_category           : string,
                    Gives the category of instrument.
            Returns:
                instrument_subclass: Subclass of Core_Instrument,
                    Sub-class of Core_Instrument associated with the instrument category provided.
            """
            if not self.validate_inst_category(inst_category):
                raise ValueError("Instrument category '{}' is not amongst the available instrument"
                                 " categories {}".format(inst_category,
                                                         self.get_available_inst_category()))
            return self.__available_inst_subclass[inst_category]

        def get_inst_category(self, inst_name):
            """Return instrument category of the instrument designated by inst_name.
            ----
            Arguments:
            """
            instrument = self.get_instrument(inst_name=inst_name)
            return instrument.category

        def create_dataset(self, file_path):
            """Create the correct Dataset subclass instance from the file path.

            This function does:
                1. Check if the file exist
                2. Extract the file name from the file path
                3. Check and interpret the file name into object name, instrument name and category
                  and eventually number of the dataset
                4. Validate the instrument category
                5. Check if the inst_name correspond to an available instrument and if not create
                    a _Default_Instrument instance.
                6. Get instrument instance
                7. Get the correct subclass of Dataset from the instrument category
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
            if not(exists(file_path)):
                raise ValueError("file doesn't exist: {}".format(file_path))
            # 2
            file_name = get_filename_from_file_path(file_path)
            # 3
            filename_info = interpret_data_filename(file_name)
            if filename_info is None:
                raise ValueError("The file name doesn't correspond to the naming convention."
                                 "The creation of the instance is not possible.")
            # 4
            if not self.validate_inst_category(filename_info["inst_category"]):
                raise ValueError("The instrument category is not recognised: {}\nAvailable "
                                 "categories: {}".format(filename_info["inst_category"],
                                                         self.get_available_inst_category()))
            # 5
            if not self.is_available_inst(filename_info["inst_name"]):
                self.add_available_def_inst(filename_info["inst_category"],
                                            filename_info["inst_name"])
            # 6.
            inst_instance = self.get_instrument(filename_info["inst_name"])
            # 7
            Dataset_SubClass = self.get_dataset_subclass(filename_info["inst_category"])
            # 8
            return Dataset_SubClass(file_path, inst_instance)

    instance = None

    def __init__(self):
        """Manager_Inst_Dataset init method (check if singleton exists and creates it if needed).

        The init method of the inside class does:
            1. Initialise the database giving Dataset subclass associated to instrument category
            2. Initialise the database of available instrument instances
        """
        if Manager_Inst_Dataset.instance is None:
            Manager_Inst_Dataset.instance = Manager_Inst_Dataset.__Mgr()

    def __getattr__(self, name):
        """Delegate every method or attribute call to the Singleton."""
        return getattr(self.instance, name)
