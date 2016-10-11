#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Parameter module.

The objective of this module is to define the Parameter class.
"""
import logging
from numbers import Number

logger = logging.getLogger()


class Parameter(object):
    """docstring for Parameter."""

    ## Name of the parameter: string
    name = None

    ## Indicate if this parameter is free or fixed: Boolean
    free = None

    ## Prior function: function
    prior_func = None
    ## Give the type of prior: string, for example Gaussian, Uniform
    prior_type = None
    ## Arguments of the prior function: dictionnary, for example for a gaussian {"mean": 0, "std":0}
    prior_args = None
    ## Indicate if the prior function is a joint prior with another parameter: Boolean
    joint_prior = None
    ## Position of this parameter value in the list of parameter of the joint prior fucntion: int
    joint_prior_pos = None

    ## Value of the parameter: float
    value = None

    def __init__(self, name, free, joint,
                 prior_type=None, prior_args=None,
                 joint_prior=None, joint_prior_pos=None,
                 value=None):
        """Create a Parameter Instance."""
        # Set the free attribute
        if isinstance(free, bool):
            self.free = free
        else:
            raise ValueError("Free should be a boolean.")
        # Set the joint attribute
        if isinstance(joint, bool):
            self.joint = joint
        else:
            raise ValueError("Joint should be a boolean.")
        # Set the value of the parameter
        if isinstance(value, Number) or (value is None):
            self.value = value
        else:
            raise ValueError("Value should be a number or None.")
        # Set name
        self.name = name

    def value_isNone(self):
        """Indicate is the value of the parameter is None."""
        return self.value is None

    def get_value(self):
        """Return the value of the parameter."""
        if self.value is None:
            logger.warning("The current value of parameter {} is not specified. Returned None."
                           "".format(self.name))
        return self.value

    def get_prior_value(self):
        """Return the a priori density probability of parameter to be value."""
        if self.joint:
            raise AttributeError("Correctly it is not possible to get the prior value for"
                                 "parameter described by joint prior probability.")
        return self.prior_func(self.value)

    def get_paramfile_section(self, text_tab=""):
        """Return the text to include in the parameter_file for this parameter."""
        name = self.get_short_name()
        text = text_tab + "{0} = {{'free': True,\n".format(name)
        text += (text_tab + self._spacestring_like("{0} = {{".format(name)) +
                 "'prior': {{'joint': False, 'joint_prior_ref': None,\n".format(name))
        text += (text_tab + self._spacestring_like("{0} = {{".format(name)) +
                 self._spacestring_like("'prior': {") + "'type': None, 'args': {}\n")
        text += (text_tab + self._spacestring_like("{0} = {{".format(name)) +
                 self._spacestring_like("'prior': {") + "}\n")
        text += (text_tab + self._spacestring_like("{0} = {{".format(name)) +
                 "'value': None\n")
        text += (text_tab + self._spacestring_like("{0} = {{".format(name)) +
                 "}\n")
        return text

    def _spacestring_like(self, string):
        """Return an empty string with the same size than string."""
        return " " * len(string)

    def get_short_name(self):
        """Return the short name of the parameter."""
        return self.name

    def get_full_name(self):
        """Return the full name of the parameter."""
        return self.name
