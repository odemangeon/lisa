#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
manager_model module.

The objective of this module is to manage the subclasses of the Core_Model classe.

@DONE:
    - __Mgr.__init__: UT
    - __Mgr._reset_models_database: Doc and UT
    - __Mgr.load_setup: Doc but No UT because depend on the content of the setup file
    - __Mgr.get_available_models: Doc and UT
    - __Mgr.add_available_model: Doc and UT
    - __Mgr.get_model_subclass: Doc and UT
    - __Mgr.is_available_modeltype: Doc and UT
    - Manager_Model.__init__: Doc and UT
    - Manager_Model.__gettattr__: Doc and UT

@TODO:
    -
"""
from logging import getLogger
from ....software_parameters import setupfile_model
from .core_model import Core_Model

## Logger
logger = getLogger()


class Manager_Model(object):
    """docstring for Manager_Model Singleton class."""

    class __Mgr(object):
        """docstring for __Mgr private class of Singleton class Manager_Model.

        For more information see Manager_Model class.
        """
        def __init__(self):
            """__Mgr init method.

            For more information see Manager_Model init method.
            """
            self.__models = dict()

        def _reset_models_database(self):
            """Reset database of available models."""
            self.__models = dict()

        def load_setup(self):
            """Load the configuration of models defined in the setup file.

            Association model type name and Core_Model subclass.
            """
            f = open(setupfile_model)
            exec(f.read())
            f.close()
            logger.debug("Setup of Manager_Model Loaded. Available models: {}"
                         "".format(self.get_available_models()))

        def get_available_models(self):
            """Returns the list of available model types.
            ----
            Returns:
                list of string, giving the available model types.
            """
            return list(self.__models.keys())

        def add_available_model(self, model_subclass):
            """Add a Core_Model subclass to database.

            This method checks that the model_sublass is indeed a model subclass before adding it
            to the database.
            ----
            Arguments:
                model_subclass : Subclass of Core_Model,
                    Custom subclass of the Core_Model Class that you want to add to the database.
            """
            logger.debug("model_subclass type: {}".format(type(model_subclass)))
            if not(issubclass(model_subclass, Core_Model)):
                raise ValueError("The provided class is not a subclass of the Core_Model class.")
            self.__models.update({model_subclass.category: model_subclass})

        def get_model_subclass(self, category):
            """Return Core_Model Subclass associated to a given model type.
            ----
            Arguments:
                category : string,
                    Type of the model.
            Returns:
                model_subclass : Subclass of Core_Model,
                    Sub-class of Core_Model associated with the model type.
            """
            if not self.is_available_modeltype(category):
                raise ValueError("The model type {} is not amongst the available models {}"
                                 "".format(category, self.get_available_models()))
            return self.__models[category]

        def is_available_modeltype(self, category):
            """Check if category refers to an available subclass of Core_Model.
            ----
            Arguments:
                category : string,
                    Type of the model.
            Returns:
                True if category is an available Core_Model subclass. False otherwise.
            """
            return category in self.get_available_models()

    instance = None

    def __init__(self):
        """Manager_Model init method (check if singleton exists and creates it if needed).

        The init method of the inside class does:
            1. Initialise the database of available model types
        """
        if Manager_Model.instance is None:
            Manager_Model.instance = Manager_Model.__Mgr()

    def __getattr__(self, name):
        """Delegate every method or attribute call to the Singleton."""
        return getattr(self.instance, name)
