#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
core_model module.

The objective of this package is to provides the core Model class.

@DONE:
    -

@TODO:
    -
"""
import logging

## Logger
logger = logging.getLogger()


class Metaclass_Model(type):
    @property
    def model_type(cls):
        """Return the name of the instrument."""
        return cls._model_type

    def __init__(cls, name, bases, attrs):
        if cls.__name__ not in ["Model", ]:
            missing_attrs = ["{}".format(attr) for attr in ["model_type"]
                             if not hasattr(cls, attr)]
            if len(missing_attrs) > 0:
                raise AttributeError("class '{}' requires attribute {}".format(name, missing_attrs))


class Model(metaclass=Metaclass_Model):
    """docstring for Model abstract class."""
    def __init__(self, model_name, instruments=None):
        """Model init method FOR INHERITANCE PURPOSES (as Model is an abstract class).

        This __init__ does:
            1. Set name of the model
        ----
        Arguments:
            model_name  : string,
                Name of the Model
            instruments : dict, (default: None)
                Dictionnary with keys being the instrument types of the dataset to be modeled and
                each key contain the list of instrument instances associated to the instrument used
                for this type of instrument.
        """
        super(Model, self).__init__()
        # 1.
        self.__name = model_name
        # IMPORTANT NOTE THE MODEL TYPE IS NOT DEFINED HERE BECAUSE IT HAS TO BE DEFINED AT THE
        # SUBCLASS LEVEL

    @property
    def name(self):
        """Return the instrument type."""
        return self.__name

    @property
    def model_type(self):
        """Return the instrument type."""
        return self.__class__._model_type
