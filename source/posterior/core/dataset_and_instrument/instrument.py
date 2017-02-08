#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
instrument module.

The objective of this package is to provides the core Isntrument and Default_Instrument classes
to store information about the isntrument used to measurement the data stored in the Dataset class.

@DONE:
    - Instrument.__init__: Doc and UT
    - Instrument.inst_type: Doc and UT
    - Instrument.name: Doc and UT
    - _Default_Instrument: Doc and UT

@TODO:
"""
from logging import getLogger

from source.tools.name import Name
from ..paramcontainer import ParamContainer
from ..parameter import Parameter


## Logger object
logger = getLogger()


class Metaclass_Instrument(type):
    @property
    def inst_type(cls):
        """Return the name of the instrument."""
        return cls._inst_type

    @property
    def params_model(cls):
        """Return the informations regarding the parameters of the instrument model."""
        return cls._params_model

    def __init__(cls, name, bases, attrs):
        if cls.__name__ not in ["Instrument", "_Default_Instrument"]:
            missing_attrs = ["{}".format(attr) for attr in ["inst_type",
                                                            "params"]
                             if not hasattr(cls, attr)]
            if len(missing_attrs) > 0:
                raise AttributeError("class '{}' requires attribute {}".format(name, missing_attrs))


class Instrument(Name, metaclass=Metaclass_Instrument):
    """docstring for Instrument abstract class."""

    def __init__(self, name):
        """Instrument init method FOR INHERITANCE PURPOSES (as Instrument is an abstract class).

        This __init__ does:
            1. Set name of the instrument
        ----
        Arguments:
            name : string,
                Name of the Instrument
        """
        super(Instrument, self).__init__(name=name)
        # self._params_name = params_name
        # self._params_unit = params_unit

        class Instrument_Model(ParamContainer):
            """Docstring of Instrument_Model class."""
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
        if type(self) is Instrument:
            raise NotImplementedError("Dataset should not be instanciated!")

    @property
    def inst_type(self):
        """Return the instrument type."""
        return self.__class__.inst_type

    @property
    def params_model(self):
        """Return the informations regarding the parameters of the instrument model."""
        return self.__class__._params_model

    def create_model_instance(self, name):
        """Return the instrument type."""
        return self.Instrument_Model(instrument=self, name=name)


class _Default_Instrument(Instrument):
    """docstring for _Default_Instrument class (not abstract contrary to Instrument)."""
    def __init__(self, inst_type, name, params_model={}):
        """Instrument init method FOR INHERITANCE PURPOSES (as Instrument is an abstract class).

        This __init__ does:
            1. Set type of the instrument
            2. Set name of the instrument
        ----
        Arguments:
            inst_type : string,
                Type of the Instrument
            name : string,
                Name of the Instrument
        """
        super(_Default_Instrument, self).__init__(name)
        self._inst_type = inst_type
        self._params_model = params_model

    @property
    def inst_type(self):
        """Return the instrument type."""
        return self._inst_type

    @property
    def params_model(self):
        """Return the informations regarding the parameters of the instrument model."""
        return self._params_model

    # def create_model_instance(self, name):
    #     """Return the instrument type."""
    #     return self.Instrument_Model(instrument=self, name=name)
