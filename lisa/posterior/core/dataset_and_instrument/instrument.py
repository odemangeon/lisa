#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
instrument module.

The objective of this package is to provides the core Isntrument and Default_Instrument classes
to store information about the isntrument used to measurement the data stored in the Dataset class.

@DONE:
    - Core_Instrument.__init__: Doc and UT
    - Default_Instrument: Doc and UT

@TODO:
"""
from loguru import logger
from numpy import logical_xor

from .manager_dataset_instrument import Manager_Inst_Dataset
# from .dataset import Core_Dataset
from ..paramcontainer import Core_ParamContainer
from ..parameter import Parameter
from ....tools.name import Named
from ....tools.metaclasses import MandatoryReadOnlyAttrAndMethod
# from ....tools.miscellaneous import spacestring_like


instrument_model_category = "instruments"

# string4datasetdico = "Dataset"
#
# key_inst = "inst_dic"
# key_misc = "misc"


class Instrument_Model(Core_ParamContainer):
    """Docstring of Instrument_Model class."""

    __category__ = instrument_model_category

    __instrument = None  # This is needed to be able to pickle the object. UnPickle doesn't call __init__ but call __getattr__ and self._parameters was only defined by __init__

    def __init__(self, instrument, name, noise_model_category=None, **kwargs):
        """Docstring of the Instrument_Model init method.

        :param Core_Instrument instrument: Instrument that is modelled.
        :param string name: Name of the instrument model
        :param string/None noise_model_category: Name of noise model category to use for this instruments data
            likelihood.

        Keyword arguments are passed to Core_Paramcontainer.__init__ (see docstring for more info).
        Only name_prefix should not be provided as arguments, since it set automatically to gravgroup.name
        """
        # Make the initialisation of Core_ParamContainer
        # name_prefix is set to None because it will be set when the gravgroup is set.
        if "name_prefix" in kwargs:
            raise TypeError("'name_prefix' is an invalid keyword argument for this function. "
                            "name_prefix is automatically set as gravgroup.name if gravgroup is"
                            "provided")
        super(Instrument_Model, self).__init__(name=name, name_prefix=instrument.name, **kwargs)
        # Set the instrument attribute
        self.__instrument = instrument
        # Set the noise_model attribute
        if noise_model_category is None:
            self.__noise_model_category = noise_model_category
        else:
            self.noise_model = noise_model_category
        # Set the parameters necessary to model the instrument behavior.
        for name, dico in instrument.params_model.items():
            self.add_parameter(Parameter(name=name, name_prefix=self.name,
                                         **dico))

    def __getattr__(self, name):
        if hasattr(self.instrument, name):
            if hasattr(getattr(self.instrument, name), "__call__"):
                return lambda *args, **kwargs: getattr(self.instrument, name)(inst_model=self,
                                                                              *args, **kwargs)
        # Default behaviour
        return super(Instrument_Model, self).__getattr__(name)

    @property
    def noise_model_category(self):
        """Return the noise model category used for this instrument model."""
        return self.__noise_model_category

    @noise_model_category.setter
    def noise_model_category(self, nm):
        """Set the noise model category to use for this instrument model."""
        self.__noise_model_category = nm

    @property
    def instrument(self):
        return self.__instrument


def _getinsthas_subcategories():
    def _getmethod(self):
        return self.__class__.has_subcategories
    return _getmethod


class Core_Instrument_metaclass(MandatoryReadOnlyAttrAndMethod):

    @property
    def has_subcategories(cls):
        """True if the instrument class has subcategories
        """
        return cls.__sub_category__ is not None

    def __new__(cls, classname, bases, classdict):
        classdict["has_subcategories"] = property(_getinsthas_subcategories())
        return super(Core_Instrument_metaclass, cls).__new__(cls, classname, bases, classdict)


class Core_Instrument(Named, metaclass=Core_Instrument_metaclass):
    """docstring for Core_Instrument abstract class."""

    __mandatoryattrs__ = ["category", "sub_category", "params_model"]
    __mandatorymeths__ = ["set_parametrisation"]

    def __init__(self, name, subcat=None):
        """Core_Instrument init method FOR INHERITANCE PURPOSES (as Core_Instrument is an abstract class).

        This __init__ does:
            1. Set name of the instrument
        ----
        Arguments:
            name : string,
                Name of the Instrument
        """
        if self.sub_category is None:
            name_prefix = f"{self.category}"
        else:
            name_prefix = f"{self.category}-{subcat}"
        # Do the Named initialization
        super(Core_Instrument, self).__init__(name=name, prefix=name_prefix)

        # self.Instrument_Model = Instrument_Model  # To be able to create instrument Models. Probably you can delete this line

        # IMPORTANT: THE INSTRUMENT CATEGORY IS NOT DEFINED HERE BECAUSE IT HAS TO BE DEFINED AT THE
        # SUBCLASS LEVEL

        # Make Core_Instrument an abstract class
        if type(self) is Core_Instrument:
            raise NotImplementedError("Core_Instrument should not be instanciated!")

    @classmethod
    def validate_inst_cat(cls, inst_cat):
        """Validate instrument category

        Parameters
        ----------
        inst_cat : str
            instrument category that you want to validate

        Returns
        -------
        valid : bool
            If true inst_cat is valid for this instrument class
        """
        return inst_cat == cls.category

    @classmethod
    def validate_inst_fullcat(cls, inst_fullcat):
        """Validate instrument full category

        Parameters
        ----------
        inst_fullcat : str
            instrument full category that you want to validate

        Returns
        -------
        valid : bool
            If true inst_fullcat is valid for this instrument full category
        """
        inst_cat, inst_subcat = cls.interpret_inst_fullcat(inst_fullcat=inst_fullcat, raise_error=False)
        return cls.validate_inst_cat(inst_cat)

    @classmethod
    def build_instmod_fullname(cls, inst_model, inst_name, inst_cat=None, inst_subcat=None, inst_fullcat=None):
        """Return the instrument name associated to the instrument model full_name."""
        if not(logical_xor(inst_fullcat is None, inst_cat is None)):
            raise ValueError("You should provide inst_category (and inst_subcategory if necessary) or inst_fullcat, not both.")
        if inst_fullcat is not None:
            inst_cat, inst_subcat = cls.interpret_inst_fullcat(inst_fullcat=inst_fullcat, raise_error=True)
        if cls.has_subcategories:
            if inst_subcat is None:
                raise ValueError(f"Instrument models of intrument class {cls.__name__} require an inst_subcategory.")
            return f"{inst_cat}-{inst_subcat}_{inst_name}_{inst_model}"
        else:
            if inst_subcat is not None:
                raise ValueError(f"Instrument models of intrument class {cls.__name__} do not have  instrument subcategories.")
            return f"{inst_cat}_{inst_name}_{inst_model}"

    @classmethod
    def interpret_instmod_fullname(cls, instmod_fullname, raise_error=True):
        """Interpret data file name.

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
        instmod_info: dictionnary with the interpration of the filename which contains the following keys:
            - inst_category : category of instrument used to take the data. e.g. "LC", "RV", ...
            - inst_subcategory : sub category of instrument used to take the data. e.g. "FWHM", None is this instrument category doesn't have subcategories
            - inst_fullcategory : full category of instrument used to take the data including or not the
                instrument sub category when needed.
            - inst_name : give the number of the data file if there is several data files of the
                same object observed with the same instrument
            - inst_model : give the number of the data file if there is several data files of the
                same object observed with the same instrument
        """
        if cls.has_subcategories:
            filename_format = "instcat-instsubcat_instname_instmodel"
        else:
            filename_format = "instcat_instname_instmodel"
        cuts = instmod_fullname.split("_")   # List of fields that were separated by "_"
        cuts_cat = cuts[0].split("-")
        format_error = False
        if len(cuts) != 3:
            format_error = True
        if cls.has_subcategories:
            if len(cuts_cat) != 2:
                format_error = True
        else:
            if len(cuts_cat) != 1:
                format_error = True
        if format_error:
            if raise_error:
                raise ValueError(f"Instrument model full name not recognized. Should be in the format {filename_format}. Got {instmod_fullname}.")
            else:
                return None
        result = {"inst_category": cuts_cat[0],
                  "inst_name": cuts[1],
                  "inst_model": cuts[2]}
        if cls.has_subcategories:
            result["inst_subcategory"] = cuts_cat[-1]
            result["inst_fullcategory"] = f"{result['inst_category']}-{result['inst_subcategory']}"
        else:
            result["inst_subcategory"] = None
            result["inst_fullcategory"] = result['inst_category']
        return result

    @classmethod
    def validate_instmod_fullname(cls, instmod_fullname):
        """Validate the name of a datafile.

        Arguments
        ---------
        instmod_fullname: string
            Full name of the instrument model.

        Returns
        -------
        valid : bool
            If True the instrument model full name is valid.
        """
        instmod_info = cls.interpret_instmod_fullname(instmod_fullname=instmod_fullname, raise_error=False)
        if instmod_info is None:
            return False
        return cls.validate_inst_cat(instmod_info["inst_category"])

    @classmethod
    def interpret_inst_fullcat(cls, inst_fullcat, raise_error=True):
        """Return the instrument category and sub category from the instrument full category

        Arguments
        ---------
        inst_fullcat : string
            Instrument full category (including the instrument category and subcategory)
        raise_error  : boolean
            If True a ValueError is raised if the inst_fullcat doesn't follow the right format

        Returns
        -------
        inst_cat : string
            Instrument category extracted or None is the format of inst_fullcat is not valid
        inst_subcat : string
            Instrument sub category extracted or None is the format of inst_fullcat is not valid
        """
        cuts = inst_fullcat.split("-")
        error_msg = f"{inst_fullcat} is not a valid instrument full category for instrument class {cls.__name__}"
        valid = False
        if cls.has_subcategories:
            if len(cuts) == 2:
                if cuts[0] == cls.category:
                    valid = True
                    inst_cat, inst_subcat = cuts
        else:
            if len(cuts) == 1:
                if cuts[0] == cls.category:
                    valid = True
                    inst_cat = cuts[0]
                    inst_subcat = None
        if not valid:
            if raise_error:
                raise ValueError(error_msg)
            else:
                return None, None
        else:
            return inst_cat, inst_subcat

    @classmethod
    def inst_fullcat_to_code(cls, inst_fullcat, raise_error=True):
        """Return the instrument category and sub category from the instrument full category

        Arguments
        ---------
        inst_fullcat : string
            Instrument full category (including the instrument category and subcategory)
        raise_error  : boolean
            If True a ValueError is raised if the inst_fullcat doesn't follow the right format

        Returns
        -------
        inst_fullcat_code : str
            Instrument full category for codes
        """
        inst_cat, inst_subcat = cls.interpret_inst_fullcat(inst_fullcat=inst_fullcat, raise_error=raise_error)
        if cls.has_subcategories:
            return f"{inst_cat}{inst_subcat}"
        else:
            return f"{inst_cat}"

    @property
    def full_category(self):
        """Return the instrument full category

        Returns
        -------
        inst_fullcat : str
            Instrument full category
        """
        if self.has_subcategories:
            return f"{self.category}-{getattr(self, self.sub_category)}"
        else:
            return f"{self.category}"

    @property
    def full_category_code(self):
        """Return the instrument full category to use in codes and python script

        Returns
        -------
        inst_fullcat_code : str
            Instrument full category for codes
        """
        if self.has_subcategories:
            return f"{self.category}{getattr(self, self.sub_category)}"
        else:
            return f"{self.category}"

    def create_model_instance(self, name, **kwargs):
        """Return the instrument type.

        Arguments
        ---------
        name : str
            Name of the instrument model

        Keyword arguments are passed to Core_Paramcontainer.__init__ (see docstring for more info).
        Only name_prefix should not be provided as arguments, since it set automatically to gravgroup.name
        """
        return Instrument_Model(instrument=self, name=name, **kwargs)


class Default_Instrument(Core_Instrument):
    """docstring for Default_Instrument class (not abstract contrary to Core_Instrument)."""

    def __init__(self, category, name, params_model={}, sub_category=None):
        """Default_Instrument init method.

        This __init__ does:
            1. Set type of the instrument
            2. Set name of the instrument
        ----
        Arguments:
            category : string,
                Category of the Instrument
            name : string,
                Name of the Instrument
        """
        self.__category__ = category
        self.__sub_category__ = sub_category
        self.__params_model__ = params_model
        super(Default_Instrument, self).__init__(name)

    @classmethod
    def set_parametrisation(cls, inst_model):
        """Set the parametrisation to the instrument model.

        Arguments
        ---------
        inst_model_obj  : Default_Instrument object
            WARNING you cannot change the name of this argument for it to work with the __getattr__
            of lisa.posterior.core.dataset_and_instrument.instrument.Instrument_Model
        """
        # cls.set_polymodel_parametrisation(inst_model=inst_model)
        pass