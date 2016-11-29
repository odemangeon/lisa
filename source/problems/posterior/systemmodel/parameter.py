#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Parameter module.

The objective of this module is to define the Parameter class.
"""
import logging
from numbers import Number

from source.tools.miscellaneous import spacestring_like

logger = logging.getLogger()


class Parameter(object):
    """docstring for Parameter."""

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

    def __init__(self, name, free=None, main=None, joint_prior=None,
                 prior_type=None, prior_args=None,
                 joint_prior_ref=None, joint_prior_pos=None,
                 value=None):
        """Create a Parameter Instance.

        ----

        Arguments:
            name            : string,
                Name of the parameter
            free            : boolean, optional (default: None),
                True if you want the parameter to be free, False otherwise
            main            : boolean, optional (default: None),
                True if you want the parameter to be a main parameter, False if it's an auxiliary
                parameter. Being a main parameter implies that you belong to the minium set of
                parameter used for the model and that you have the possibility to be jumped or
                fixed (free or not). Being an auxialiary parameter implies that your value is
                defined by the value of the main parameters (so you can be free or not but it
                doesn't depend on you).
            joint_prior     : boolean, optional (default: None),
                True if the prior probability associated to the value of parameter is defined by a
                joint prior probability function that depends on at least another parameter. False
                if this parameter is considered as independant of the other free parameter a priori.
            prior_type      : string, optional (default: None),
                Gives the type of prior probability to use for this parameter, eg: gaussian, uniform
                , ...
            prior_args      : dict, optional (default: None),
                Dictionnary which gives the value of the parameter of the prior probability function
                that you want to use. The number of elements depends on the prior_type.
            joint_prior_ref : reference or function used as joint prior probability function
            joint_prior_pos : Index (or position) of this parameter in the list of parameter of the
                joint prior function
            value           : number (float), optional (default:None)
                Number giving the current value of the parameter, can be used in the initialization
                to define the initial value.
        """
        ## Name of the parameter: string
        self.name = name
        # Set the free attribute
        if isinstance(free, bool) or (free is None):
            ## Indicate if this parameter is free or fixed: Boolean or None
            self.free = free
        else:
            raise ValueError("Free should be a boolean or None.")
        # Set the main attribute
        if isinstance(main, bool) or (main is None):
            ## Indicate if this parameter is main or auxiliary: Boolean or None
            self.main = main
        else:
            raise ValueError("Main should be a boolean or None.")
        # Set the joint_prior attribute
        if isinstance(joint_prior, bool) or (joint_prior is None):
            ## Indicate if the prior of this parameter is a joint prior: Boolean or None
            self.joint_prior = joint_prior
        else:
            raise ValueError("Joint_prior should be a booleanor None.")
        # Set the value of the parameter
        if isinstance(value, Number) or (value is None):
            ## Value of the parameter: float
            self.value = value
        else:
            raise ValueError("Value should be a number or None.")

    def value_isNone(self):
        """Indicate is the value of the parameter is None."""
        return self.value is None

    def ismain(self):
        """Indicate if the paramater is a main parameter."""
        return self.main is True

    def get_value(self):
        """Return the value of the parameter."""
        if self.value is None:
            logger.warning("The current value of parameter {} is not specified. Returned None."
                           "".format(self.name))
        return self.value

    def get_prior_value(self):
        """Return the a priori density probability of parameter to be value."""
        if self.joint_prior:
            raise AttributeError("Currently it is not possible to get the prior value for"
                                 "parameter described by joint prior probability.")
        return self.prior_func(self.value)

    def get_paramfile_section(self, text_tab="", texttab_1tline=True):
        """Return the text to include in the parameter_file for this parameter.

        ----

        Arguments:
            text_tab : string,
                text giving the tabulation that needs to be added to this the text to obtain the
                good alignment in the input file.
        """
        name = self.get_short_name()
        entete_param = "'{0}': {{".format(name)
        space_entete_param = spacestring_like(entete_param)
        text = ""
        # First is the name of the parameter
        if texttab_1tline:
            text += text_tab
        text += entete_param
        # First key of the parameter dictionnary is 'free' for free parameter or fixed.
        text += "'free': True,\n".format(name)
        # Second key is for the priors
        entete_prior = "'prior': {"
        space_entete_prior = spacestring_like(entete_prior)
        text += text_tab + space_entete_param + entete_prior
        # Classical marginal prior keys
        text += "'type': None, 'args': { }\n"
        # Joint prior keys (for later use, not implemented yet in what follows)
        # text += (text_tab + space_entete_param + space_entete_prior +
        #          "'joint_prior': False, 'joint_prior_ref': None,\n")
        text += text_tab + space_entete_param + space_entete_prior + "},\n"
        # Third and last key is the value
        text += text_tab + space_entete_param + "'value': None\n"
        text += text_tab + space_entete_param + "},\n"
        return text

    def get_short_name(self):
        """Return the short name of the parameter."""
        return self.name

    def get_full_name(self):
        """Return the full name of the parameter."""
        return self.name
