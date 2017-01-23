#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
instrument module.

The objective of this package is to provides the core Isntrument and Default_Instrument classes
to store information about the isntrument used to measurement the data stored in the Dataset class.

@DONE:
    - Instrument.__init__: Doc and UT
    - Instrument._set_type: Doc and UT
    - Instrument.get_type: Doc and UT
    - Instrument._set_name: Doc and UT
    - Instrument.get_name: Doc and UT
    - _Default_Instrument: Doc and UT

@TODO:
"""


class Metaclass_Instrument(type):
    @property
    def inst_type(cls):
        """Return the name of the instrument."""
        return cls._inst_type

    def __init__(cls, name, bases, attrs):
        if cls.__name__ not in ["Instrument", "_Default_Instrument"]:
            missing_attrs = ["{}".format(attr) for attr in ["inst_type"]
                             if not hasattr(cls, attr)]
            if len(missing_attrs) > 0:
                raise AttributeError("class '{}' requires attribute {}".format(name, missing_attrs))


class Instrument(metaclass=Metaclass_Instrument):
    """docstring for Instrument abstract class."""

    def __init__(self, inst_name):
        """Instrument init method FOR INHERITANCE PURPOSES (as Instrument is an abstract class).

        This __init__ does:
            1. Set name of the instrument
        ----
        Arguments:
            inst_name : string,
                Name of the Instrument
        """
        super(Instrument, self).__init__()
        # 1.
        self.__name = inst_name
        # IMPORTANT NOTE THE INSTRUMENT TYPE IS NOT DEFINED HERE BECAUSE IT HAS TO BE DEFINED AT THE
        # SUBCLASS LEVEL

        # Make Dataset an abstract class
        # if type(self) is Instrument:
        #     raise NotImplementedError("Dataset should not be instanciated!")

    @property
    def name(self):
        """Return the instrument type."""
        return self.__name

    @property
    def inst_type(self):
        """Return the instrument type."""
        return self.__class__.inst_type


class _Default_Instrument(Instrument):
    """docstring for _Default_Instrument class (not abstract contrary to Instrument)."""
    def __init__(self, inst_type, inst_name):
        """Instrument init method FOR INHERITANCE PURPOSES (as Instrument is an abstract class).

        This __init__ does:
            1. Set type of the instrument
            2. Set name of the instrument
        ----
        Arguments:
            inst_type : string,
                Type of the Instrument
            inst_name : string,
                Name of the Instrument
        """
        super(_Default_Instrument, self).__init__(inst_name)
        self._inst_type = inst_type

    @property
    def inst_type(self):
        """Return the instrument type."""
        return self._inst_type
