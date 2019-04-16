#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
parametrisation module

The Objective of this module is to provide the Core_Parametrisation class.
"""
from logging import getLogger

## Logger Object
logger = getLogger()


class Core_Parametrisation(object):
    """docstring for the interface class Core_Parametrisation."""

    def init_available_parametrisation(self):
        """
        """
        # Initialise available_parametrisations list should be filled in the Child Class
        # Define name of the parametrisation available (list of string)
        self.__available_parametrisations = []
        self.__parametrisation = None

    def set_parametrisation(self, parametrisation, **kwargs):
        """Choose the parametrisation to use and apply it.

        :param str parametrisation: Name of the parametrisation to use
        keyword arguments associated to the parametrisation chosen
        """
        self.parametrisation = parametrisation
        self.apply_parametrisation(**kwargs)

    @property
    def available_parametrisations(self):
        """List of the available parametrisation."""
        return self.__available_parametrisations

    @property
    def parametrisation(self):
        """Dictionary defining the available parametrisation and their apply functions."""
        return self.__parametrisation

    # TODO: If I do a Core_Parametrisation Class, this should go there
    @parametrisation.setter
    def parametrisation(self, value=None):
        """Set the parametrisation to use."""
        # If no parametrisation is provided I chose what I think is best.
        if value is None:
            self.__parametrisation = self._choose_default_parametrisation()
            logger.info("No parametrisation provided. The automatically selected parametrisation is"
                        ": {}".format(self.__parametrisation))
        # If a parametrisation is provided, I check that it's an available one and a valid one given
        # the circumstances (number of planets).
        else:
            self._check_availability_parametrisation(value)
            self._check_validity_parametrisation(value)
            self.__parametrisation = value
        logger.info("The parametrisation has been set: {}".format(self.__parametrisation))

    def _choose_default_parametrisation(self):
        """Return the best parametrisation when no choice is made by the user."""
        raise NotImplementedError("This function needs to be overloaded in the child Class.")

    def _check_availability_parametrisation(self, parametrisation):
        """Check that the parametrisation requested is in the list of available parametrisations.

        If not raise ValueError

        :param str parametrisation: String which designate the parametrisation. Should be in
            self.available_parametrisations
        """
        if parametrisation not in self.available_parametrisations:
            raise ValueError("{} is not in the list of available parametrisation ({})"
                             "".format(parametrisation, self.available_parametrisations))

    def _check_validity_parametrisation(self, parametrisation):
        """Check that the parametrisation requested is valid for the current model.

        If not raise ValueError. For now there is no validity concern for model given the existing
        parametrisations.

        :param str parametrisation: String which designate the parametrisation. Should be in
            self.available_parametrisations
        """
        raise NotImplementedError("This function needs to be overloaded in the child Class.")

    @property
    def parametrisation_kwargs(self):
        """Dictionary giving the keyword arguments of the apply_parametrisation method."""
        try:
            return self.__parametrisation_kwargs
        except:
            self.__parametrisation_kwargs = {}
            return self.__parametrisation_kwargs

    def apply_parametrisation(self, **kwargs):
        """Apply the parametrisation pointed by the parametrisation property."""
        raise NotImplementedError("This function needs to be overloaded in the child Class.")

    def save_parametrisation_kwargs(self, **kwargs):
        """Save the keyword arguments of the parmetrisation function in parametrisation_kwargs."""
        for key, value in kwargs.items():
            self.parametrisation_kwargs[key] = value
