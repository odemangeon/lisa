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
from logging import getLogger

from ....tools.name import Name
from ....tools.metaclasses import MandatoryReadOnlyAttr
from ..paramcontainer import Core_ParamContainer
from ..parameter import Parameter


## Logger object
logger = getLogger()

instrument_model_category = "instruments"


class Core_Instrument(Name, metaclass=MandatoryReadOnlyAttr):
    """docstring for Core_Instrument abstract class."""

    __mandatoryattrs__ = ["category", "params_model"]

    def __init__(self, name):
        """Core_Instrument init method FOR INHERITANCE PURPOSES (as Core_Instrument is an abstract class).

        This __init__ does:
            1. Set name of the instrument
        ----
        Arguments:
            name : string,
                Name of the Instrument
        """
        super(Core_Instrument, self).__init__(name=name)

        class Instrument_Model(Core_ParamContainer):
            """Docstring of Instrument_Model class."""

            __category__ = instrument_model_category

            def __init__(self, instrument, name):
                """Docstring of the Instrument_Model init method."""
                # name_prefix is set to None because it will be set when the gravgroup is set.
                super(Instrument_Model, self).__init__(name=name, name_prefix=instrument.name)
                self.__instrument = instrument
                for name, dico in instrument.params_model.items():
                    self.add_parameter(Parameter(name=name, name_prefix=self.full_name,
                                                 **dico))

            @property
            def instrument(self):
                return self.__instrument

        self.Instrument_Model = Instrument_Model
        # IMPORTANT: THE INSTRUMENT TYPE IS NOT DEFINED HERE BECAUSE IT HAS TO BE DEFINED AT THE
        # SUBCLASS LEVEL
        # Make Dataset an abstract class
        if type(self) is Core_Instrument:
            raise NotImplementedError("Dataset should not be instanciated!")

    def create_model_instance(self, name):
        """Return the instrument type."""
        return self.Instrument_Model(instrument=self, name=name)


class Default_Instrument(Core_Instrument):
    """docstring for Default_Instrument class (not abstract contrary to Core_Instrument)."""
    def __init__(self, category, name, params_model={}):
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
        super(Default_Instrument, self).__init__(name)
        self.__category__ = category
        self.__params_model__ = params_model
