#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
manager_noise_model module.

The objective of this module is to manage the noise models.

@DONE:
    -

@TODO:
    -
"""
from logging import getLogger
from ....software_parameters import setupfile_noise_model
from .noise_model import Core_Noise_Model

## Logger
logger = getLogger()


class Manager_NoiseModel(object):
    """docstring for Manager_NoiseModel Singleton class."""

    class __Mgr(object):
        """docstring for __Mgr private class of Singleton class Manager_NoiseModel.

        For more information see Manager_NoiseModel class.
        """
        def __init__(self):
            """__Mgr init method.

            For more information see Manager_NoiseModel init method.
            """
            self.__noise_models = dict()

        def _reset_noisemodels_database(self):
            """Reset database of available noise models."""
            self.__noise_models = dict()

        def load_setup(self):
            """Load the configuration of noise models defined in the setup file.

            Association noise model name and NoiseModel subclass.
            """
            f = open(setupfile_noise_model)
            exec(f.read())
            f.close()
            logger.debug("Setup of Manager_NoiseModel Loaded. Available noise models: {}"
                         "".format(self.get_available_noisemodels()))

        def get_available_noisemodels(self):
            """Returns the list of available noise model names.
            ----
            Returns:
                list of string, giving the available noise model names.
            """
            return list(self.__noise_models.keys())

        def add_available_noisemodel(self, noisemodel_subclass):
            """Add a Core_Noise_Model subclass to database.

            This method checks that the noisemodel_subclass is indeed a Core_Noise_Model subclass
            before adding it to the database.
            ----
            Arguments:
                noisemodel_subclass : Subclass of Core_Noise_Model,
                    Custom subclass of the Core_Noise_Model Class that you want to add to the
                    database.
            """
            logger.debug("noisemodel_subclass type: {}".format(type(noisemodel_subclass)))
            if not(issubclass(noisemodel_subclass, Core_Noise_Model)):
                raise ValueError("The provided class is not a subclass of the Core_Noise_Model"
                                 " class.")
            self.__noise_models.update({noisemodel_subclass.category: noisemodel_subclass})

        def get_noisemodel_subclass(self, category):
            """Return Core_Noise_Model Subclass associated to a given noise model category.
            ----
            Arguments:
                category : string,
                    Type of nooise model.
            Returns:
                noisemodel_subclass : Subclass of Core_Noise_Model,
                    Sub-class of Core_Noise_Model associated with the noise model category.
            """
            if not self.is_available_noisemodeltype(category):
                raise ValueError("The noise model type {} is not amongst the available noise models"
                                 " {}".format(category, self.get_available_noisemodels()))
            return self.__noise_models[category]

        def is_available_noisemodeltype(self, category):
            """Check if category refers to an available subclass of Core_Noise_Model.
            ----
            Arguments:
                category : string,
                    Type of the noise model.
            Returns:
                True if category is an available Core_Noise_Model subclass. False otherwise.
            """
            return category in self.get_available_noisemodels()

    instance = None

    def __init__(self):
        """Manager_NoiseModel init method (check if singleton exists and creates it if needed).

        The init method of the inside class does:
            1. Initialise the database of available noise models
        """
        if Manager_NoiseModel.instance is None:
            Manager_NoiseModel.instance = Manager_NoiseModel.__Mgr()

    def __getattr__(self, name):
        """Delegate every method or attribute call to the Singleton."""
        return getattr(self.instance, name)
