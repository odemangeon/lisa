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
    - __Mgr.get_inst: Doc and UT
    - __Mgr.is_available_inst: Doc and UT
    - __Mgr.create_dataset: Doc
    - Manager_Inst_Dataset.__init__: Doc and UT
    - Manager_Inst_Dataset.__gettattr__: Doc and UT

@TODO:
    - UT __Mgr.create_dataset
"""
from logging import getLogger
from os.path import exists
from numpy import logical_xor
from ....software_parameters import setupfile_dataset_inst
from ....tools.miscellaneous import get_filename_from_file_path

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

        def _reset_inst_cat(self):
            """Reset database giving Dataset subclass associated to instrument category.
            """
            self.__dataset_for_inst = dict()
            self.__available_inst_subclass = dict()

        def _reset_available_inst(self):
            """Reset database of available instrument instance.
            """
            self.__available_inst = dict()

        def _reset_manager(self):
            """Reset database of available instrument instance.
            """
            self.__init__()

        def add_available_inst_cat(self, inst_subclass, dataset_subclass):
            """Add a Dataset subclass to a given instrument category.

            Arguments
            ---------
            inst_subclass : Instrument subclass
            dataset_subclass : Subclass of Dataset class,
                Subclass of Dataset class that you want to associate to the instrument category.
            """
            self.__available_inst_subclass.update({inst_subclass.category: inst_subclass})
            self.__dataset_for_inst.update({inst_subclass.category: dataset_subclass})

        def add_available_inst(self, inst_instance):
            """Add an instance of a Core_Instrument subclass to the list of available instrument.

            This method checks that the instrument category provided is a valid one before adding
            the instance.

            Arguments
            ---------
            instrument_instance : Instance of a Core_Instrument Subclass,
                instance of Core_Instrument subclass of category inst_category
            """
            inst_cat = inst_instance.category
            if not(self.validate_inst_cat(inst_cat)):
                raise ValueError("Provided inst_category ({}) is not amongst the valid instrument "
                                 "categories: {}".format(self.get_available_inst_cat()))
            if inst_cat not in self.__available_inst.keys():
                self.__available_inst[inst_cat] = {}
            if inst_instance.has_subcategories:
                inst_subcat = getattr(inst_instance, inst_instance.sub_category)
                if inst_subcat not in self.__available_inst[inst_cat]:
                    self.__available_inst[inst_cat][inst_subcat] = {}
                inst_name = inst_instance.get_name()
                if inst_name in self.__available_inst[inst_cat][inst_subcat]:
                    logger.debug(f"Instrument {inst_name} of category {inst_cat} already exists.")
                else:
                    self.__available_inst[inst_cat][inst_subcat].update({inst_name: inst_instance})
            else:
                inst_name = inst_instance.get_name()
                if inst_name in self.__available_inst[inst_cat]:
                    logger.debug(f"Instrument {inst_name} of category {inst_cat} already exists.")
                else:
                    self.__available_inst[inst_cat].update({inst_name: inst_instance})

        def define_def_instrument_class(self, Default_Inst_class):
            """Define the class to be used for default instruments.

            TODO: Check is this is actually used

            Arguments
            ---------
            Default_Inst_class
            """
            self._Default_Instrument = Default_Inst_class

        def add_available_def_inst(self, inst_fullcat, inst_name):
            """Add an instance of the Default_Instrument class to the list of available instrument.

            This method checks that the instrument category provided is a valid one before adding
            the instance.

            Arguments
            ---------
            inst_fullcat : string,
                Full category of the Instrument
            name              : string,
                Name of the instrument
            """
            valid, inst_subclass = self.validate_inst_fullcat(inst_fullcat=inst_fullcat)
            if valid:
                inst_cat, inst_subcat = inst_subclass.interpret_inst_fullcat(inst_fullcat=inst_fullcat, raise_error=True)
            else:
                raise ValueError(f"{inst_fullcat} is not a valid instrument full category")
            new_inst = inst_subclass(name=inst_name, subcat=inst_subcat)
            self.add_available_inst(new_inst)

        def load_setup(self):
            """Load the configuration of instruments and datasets define in the setup file.

            Association of instrument categories and Dataset subclasses but also available
            instrument instances. The setup file is define in the software_parameters module.
            """
            f = open(setupfile_dataset_inst)
            exec(f.read())
            f.close()
            logger.debug("Setup of Manager_Inst_Dataset Loaded")

        def get_available_inst_cat(self):
            """Returns the list of available instrument categories.
            ----
            Returns:
                list of string, giving the available instrument categories
            """
            return list(self.__available_inst_subclass.keys())

        def get_available_inst_name(self, inst_cat=None, inst_subcat=None, inst_fullcat=None):
            """Returns the list of available instrument instances.

            You should provide inst_cat (and inst_subcat if needed) or inst_fullcat, not both.

            Parameters
            ----------
            inst_cat : string,
                Gives the category of the instrument.
            inst_subcat : string
                Gives the sub category of the instrument if needed.
            inst_fullcat : string
                Gives the full category of the instrument.

            Returns
            -------
                list of string, giving the available instrument instance names.
            """
            if (inst_cat is not None) and (inst_fullcat is not None):
                raise ValueError("You should provide inst_cat (and inst_subcat if needed) or inst_fullcat, not both.")
            if inst_fullcat is not None:
                valid, inst_subclass = self.validate_inst_fullcat(inst_fullcat=inst_fullcat)
                if valid:
                    inst_cat, inst_subcat = inst_subclass.interpret_inst_fullcat(inst_fullcat=inst_fullcat, raise_error=True)
                else:
                    raise ValueError(f"{inst_fullcat} is not a valid instrument full category")
            if (inst_cat is None) and (inst_subcat is not None):
                raise ValueError("It doesn't make sense to provide inst_subcat but not inst_cat.")
            if inst_cat is None:
                res = {}
                for inst_cat in self.get_available_inst_cat():
                    inst_subclass = self.get_inst_subclass(inst_cat=inst_cat)
                    if inst_subclass.has_subcategories:
                        res[inst_cat] = {}
                        for inst_subcat in self.__available_inst[inst_cat].keys():
                            res[inst_cat][inst_subcat] = list(self.__available_inst[inst_cat][inst_subcat])
                    else:
                        res[inst_cat] = list(self.__available_inst[inst_cat])
            else:
                inst_subclass = self.get_inst_subclass(inst_cat=inst_cat)
                if inst_subclass.has_subcategories:
                    if inst_subcat is None:
                        res = {}
                        for inst_subcat in self.__available_inst[inst_cat].keys():
                            res[inst_subcat] = list(self.__available_inst[inst_cat][inst_subcat])
                    else:
                        res = list(self.__available_inst[inst_cat][inst_subcat])
                else:
                    if inst_subcat is not None:
                        raise ValueError(f"Instrument category {inst_cat} doesn't have sub categories (got ({inst_subcat}))")
                    else:
                        res = list(self.__available_inst[inst_cat])
            return res

        def get_available_inst_subclass(self):
            """Returns the dictionary of available instrument subclasses.
            ----
            Returns:
                dictionary with keys being instrument category and values the instrument subclass.
            """
            return self.__available_inst_subclass.copy()

        def validate_inst_cat(self, inst_cat):
            """Validate an instrument category.

            An instrument category is valid if the manager possess an Instrument subclass of this same category.

            Parameters
            ----------
            inst_cat : str
                Instrument category that you want to validate

            Returns
            -------
            valid : bool
                True is inst_cat is a valid instrument category
            """
            return inst_cat in self.get_available_inst_cat()

        def validate_dataset_filename(self, file_name):
            """Check if the provided file name is a valid filename for the available dataset subclasses.

            Arguments
            ---------
            file_name : str
                Dataset file name.

            Returns
            -------
            valid            : bool
                if True then the file name is valid
            dataset_subclass : Dataset subclass
                If valid is True, gives the Dataset subclass of which the filename belong, else None.
            """
            for inst_cat in self.get_available_inst_cat():
                dataset_subclass = self.get_dataset_subclass(inst_cat)
                valid = dataset_subclass.validate_dataset_filename(file_name)
                if valid:
                    break
                else:
                    dataset_subclass = None
            return valid, dataset_subclass

        def validate_inst_fullcat(self, inst_fullcat):
            """Check if the provided instrument full category

            Arguments
            ---------
            inst_fullcat : str
                Instrument full category

            Returns
            -------
            valid            : bool
                if True then the instrument full category is valid
            inst_subclass : Instrument subclass
                If valid is True, gives the Instrument subclass of which the inst_fullcat refers to.
            """
            for inst_cat in self.get_available_inst_cat():
                inst_subclass = self.get_inst_subclass(inst_cat)
                valid = inst_subclass.validate_inst_fullcat(inst_fullcat)
                if valid:
                    break
                else:
                    inst_subclass = None
            return valid, inst_subclass

        def interpret_data_filename(self, data_file_name, raise_error=True):
            """Interpret data file name.

            If the format of the data file name is recognized the function return a dictionnary (see
            Returns below) otherwise return None.

            Arguments
            ---------
            data_file_name : string
                Data file name. The format depends on wheter or not the instrument class associated to the
                dataset has sub categories or not.
            raise_error    : Boolean
                If True the function will raise an error if the format is not correct

            Returns
            -------
            result: dictionnary with the interpration of the filename which contains the following keys:
                - object : name of the object observed with the data
                - inst_cat : category of instrument used to take the data. e.g. "LC", "RV", ...
                - inst_subcat : sub category of instrument used to take the data. e.g. "FWHM", None is this instrument category doesn't have subcategories
                - inst_fullcat : full category of instrument used to take the data including or not the
                    instrument sub category when needed.
                - inst_name : Name of the instrument used to take the data.
                - number : give the number of the data file if there is several data files of the
                    same object observed with the same instrument
            """
            valid, dataset_subclass = self.validate_dataset_filename(file_name=data_file_name)
            if valid:
                return dataset_subclass.interpret_data_filename(data_file_name=data_file_name, raise_error=True)
            else:
                raise ValueError(f"{data_file_name} is not a valid data file name")

        def dataset_name_from_file_name(self, file_name):
            """Return the dataset_name associated to the filename of a dataset."""
            valid, dataset_subclass = self.validate_dataset_filename(file_name=file_name)
            if valid:
                filename_info = dataset_subclass.interpret_data_filename(data_file_name=file_name, raise_error=True)
                if filename_info["inst_subcat"] is None:
                    return "{}_{}_{}_{}".format(filename_info["inst_cat"], filename_info["object"],
                                                filename_info["inst_name"], filename_info["number"])
                else:
                    return "{}-{}_{}_{}_{}".format(filename_info["inst_cat"], filename_info["inst_subcat"],
                                                   filename_info["object"], filename_info["inst_name"], filename_info["number"])
            else:
                raise ValueError(f"{file_name} is not a valid data file name")

        def validate_instmod_fullname(self, instmod_fullname):
            """Check if the provided instrument model full name is a valid instrument model name for the available instrument subclasses.

            Arguments
            ---------
            instmod_fullname : str
                Instrument model full name.

            Returns
            -------
            valid: bool
                if True then the file name is valid
            inst_subclass: Instrument subclass
                If valid is True, gives the Instrument subclass of which the filename belong, else None.
            """
            for inst_cat in self.get_available_inst_cat():
                inst_subclass = self.get_inst_subclass(inst_cat)
                valid = inst_subclass.validate_instmod_fullname(instmod_fullname)
                if valid:
                    break
                else:
                    inst_subclass = None
            return valid, inst_subclass

        def interpret_instmod_fullname(self, instmod_fullname, raise_error=True):
            """Interpret instrument model full name.

            If the format of the data file name is recognized the function return a dictionnary (see
            Returns below) otherwise return None.

            Arguments
            ---------
            instmod_fullname : string
                Instrument model full name. The format depends on wheter or not the instrument class associated to the instrument model has sub categories or not.
            raise_error    : Boolean
                If True the function will raise an error if the format is not correct

            Returns
            -------
            result: dictionnary with the interpration of the filename which contains the following keys:
                - inst_cat : category of instrument used to take the data. e.g. "LC", "RV", ...
                - inst_subcat : sub category of instrument used to take the data. e.g. "FWHM", None is this instrument category doesn't have subcategories
                - inst_fullcat : full category of instrument used to take the data including or not the
                    instrument sub category when needed.
                - inst_name : give the number of the data file if there is several data files of the
                    same object observed with the same instrument
                - inst_model : give the number of the data file if there is several data files of the
                    same object observed with the same instrument
            """
            valid, instrument_subclass = self.validate_instmod_fullname(instmod_fullname=instmod_fullname)
            if valid:
                return instrument_subclass.interpret_instmod_fullname(instmod_fullname=instmod_fullname, raise_error=True)
            else:
                raise ValueError(f"{instmod_fullname} is not a valid instrument model full name")

        def interpret_inst_fullcat(self, inst_fullcat, raise_error=True):
            """Interpret instrument full category.

            If the format of the instrument full category is recognized the function return the instrument category and instrument subcategory.

            Arguments
            ---------
            inst_fullcat : string
                Instrument full category. The format depends on wheter or not the instrument class associated to the instrument model has sub categories or not.
            raise_error  : Boolean
                If True the function will raise an error if the format is not correct

            Returns
            -------
            inst_cat    : str
                Instrument category
            inst_subcat : str
                Instrument sub category. It is None if the instrument category has no subcategories.
            """
            valid, instrument_subclass = self.validate_inst_fullcat(inst_fullcat=inst_fullcat)
            if valid:
                return instrument_subclass.interpret_inst_fullcat(inst_fullcat=inst_fullcat, raise_error=True)
            else:
                raise ValueError(f"{inst_fullcat} is not a valid instrument full category")

        def get_inst_fullcat_code(self, inst_fullcat, raise_error=True):
            """Return the instrument full category for codes

            If the format of the instrument full category is recognized the function return the instrument category and instrument subcategory.

            Arguments
            ---------
            inst_fullcat : string
                Instrument full category. The format depends on wheter or not the instrument class associated to the instrument model has sub categories or not.
            raise_error  : Boolean
                If True the function will raise an error if the format is not correct

            Returns
            -------
            inst_fullcat_code : str
                Instrument full category for use in codes and scripts
            """
            valid, instrument_subclass = self.validate_inst_fullcat(inst_fullcat=inst_fullcat)
            if valid:
                return instrument_subclass.inst_fullcat_to_code(inst_fullcat=inst_fullcat, raise_error=raise_error)
            else:
                raise ValueError(f"{inst_fullcat} is not a valid instrument full category")

        def is_available_inst(self, inst_name, inst_cat=None, inst_subcat=None, inst_fullcat=None):
            """Check if inst_name refers to an available instance of a subclass of Core_Instrument.

            Parameters
            ----------
            inst_name    : string,
                Gives the instrument name.
            inst_cat     : string,
                Gives the category of the instrument.
            inst_subcat  : string
                Gives the instrument subcategory of the instrument
            inst_fullcat : string
                Gives the isntrument full category of the instrument

            Returns
            -------
                True if inst_category is an available instrument instance. False otherwise.
            """
            if not logical_xor(inst_fullcat is None, inst_cat is None):
                raise ValueError("You should provide inst_cat (and inst_subcat if needed) or inst_fullcat , not both or none.")
            if inst_fullcat is not None:
                valid, inst_subclass = self.validate_inst_fullcat(inst_fullcat=inst_fullcat)
                if valid:
                    inst_cat, inst_subcat = inst_subclass.interpret_inst_fullcat(inst_fullcat=inst_fullcat, raise_error=True)
                else:
                    raise ValueError(f"{inst_fullcat} is not a valid instrument full category")
            inst_subclass = self.get_inst_subclass(inst_cat=inst_cat)
            if inst_subclass.has_subcategories:
                if inst_subcat is None:
                    raise ValueError(f"Instrument category {inst_cat} requires a sub category")
                else:
                    return inst_name in self.get_available_inst_name(inst_cat=inst_cat, inst_subcat=inst_subcat)
            else:
                return inst_name in self.get_available_inst_name(inst_cat=inst_cat)

        def get_dataset_subclass(self, inst_cat):
            """Return Dataset subclass associated to a given instrument category.

            Arguments
            ---------
            inst_cat : string,
                Gives the instrument category

            Returns
            -------
            Dataset_Subclass : class,
                Sub-class of Dataset associated with the instrument category provided.
            """
            return self.__dataset_for_inst[inst_cat]

        def get_inst(self, inst_name, inst_cat=None, inst_subcat=None, inst_fullcat=None):
            """Return Core_Instrument Subclass instance associated to a given instrument name.

            Parameters
            ----------
            inst_name    : string,
                Gives the instrument name.
            inst_cat     : string,
                Gives the category of the instrument.
            inst_subcat  : string
                Gives the instrument subcategory of the instrument
            inst_fullcat : string
                Gives the isntrument full category of the instrument

            Returns
            -------
            instrument_instance : class,
                Instance of a Sub-class of Core_Instrument associated with the instrument name
                provided.
            """
            if not logical_xor(inst_fullcat is None, inst_cat is None):
                raise ValueError("You should provide inst_cat (and inst_subcat if needed) or inst_fullcat , not both or none.")
            if inst_fullcat is not None:
                valid, inst_subclass = self.validate_inst_fullcat(inst_fullcat=inst_fullcat)
                if valid:
                    inst_cat, inst_subcat = inst_subclass.interpret_inst_fullcat(inst_fullcat=inst_fullcat, raise_error=True)
                else:
                    raise ValueError(f"{inst_fullcat} is not a valid instrument full category")
            if not self.is_available_inst(inst_name=inst_name, inst_cat=inst_cat, inst_subcat=inst_subcat):
                raise ValueError("Instrument named '{}' is not amongst the available instrument"
                                 " instances for the category {}".format(inst_name, inst_cat))
            inst_subclass = self.get_inst_subclass(inst_cat=inst_cat)
            if inst_subclass.has_subcategories:
                return self.__available_inst[inst_cat][inst_subcat][inst_name]
            else:
                return self.__available_inst[inst_cat][inst_name]

        def get_inst_subclass(self, inst_cat):
            """Return Core_Instrument Subclass associated to a given instrument category.
            ----
            Arguments:
                inst_cat : string,
                    Gives the category of instrument.
            Returns:
                instrument_subclass: Subclass of Core_Instrument,
                    Sub-class of Core_Instrument associated with the instrument category provided.
            """
            if not self.validate_inst_cat(inst_cat):
                raise ValueError("Instrument category '{}' is not amongst the available instrument"
                                 " categories {}".format(inst_cat,
                                                         self.get_available_inst_cat()))
            return self.__available_inst_subclass[inst_cat]

        def create_dataset(self, file_path):
            """Create the correct Dataset subclass instance from the file path.

            This function does:
                1. Check if the file exist
                2. Extract the file name from the file path
                3. Check the file name and if valid return the inst_cat, instrument subclass and dataset subclass
                4. Check if the inst_name correspond to an available instrument and if not create
                    a _Default_Instrument instance.
                5. Get instrument instance
                6. Create the instance of this subclass and return it
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
            valid, dataset_subclass = self.validate_dataset_filename(file_name)
            if valid is False:
                raise ValueError(f"The file name {file_name} doesn't correspond to the naming convention of any dataset type."
                                 "The creation of the instance is not possible.")
            filename_info = dataset_subclass.interpret_data_filename(file_name)
            # 4
            # print(filename_info)
            if not self.is_available_inst(inst_name=filename_info["inst_name"], inst_cat=filename_info["inst_cat"], inst_subcat=filename_info["inst_subcat"]):
                self.add_available_def_inst(inst_fullcat=filename_info["inst_fullcat"],
                                            inst_name=filename_info["inst_name"],
                                            )
            # 5.
            inst_instance = self.get_inst(inst_name=filename_info["inst_name"], inst_cat=filename_info["inst_cat"], inst_subcat=filename_info["inst_subcat"])
            # 6
            return dataset_subclass(file_path, inst_instance)

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
