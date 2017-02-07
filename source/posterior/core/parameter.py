#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Parameter module.

The objective of this module is to define the Parameter class.

TODO:
    - Change the value.setter to check if value is within the prior
"""
import logging
from numbers import Number

from source.tools.miscellaneous import spacestring_like, check_name_code

## Logger Object
logger = logging.getLogger()


class Parameter(object):
    """docstring for Parameter."""

    ## Prior function: function
    prior_func = None

    ## Arguments of the prior function: dictionnary, for example for a gaussian {"mean": 0, "std":0}
    prior_args = None
    ## Position of this parameter value in the list of parameter of the joint prior fucntion: int
    joint_prior_pos = None

    def __init__(self, name, name_prefix=None,
                 free=True, main=True, joint_prior=False,
                 prior_type=None, prior_args=None,
                 joint_prior_ref=None, joint_prior_pos=None,
                 value=None
                 ):
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
        if not isinstance(name, str):
            raise ValueError("Name should be a string")
        self.__name = name
        ## Name of the parameter: string
        if not isinstance(name_prefix, str) and (name_prefix is not None):
            raise ValueError("Name_prefix should be a string")
        self.__name_prefix = name_prefix
        # Set the free attribute
        self.free = free
        # Set the main attribute
        self.main = main
        # Set the joint_prior attribute
        self.joint_prior = joint_prior
        # Set the prior_type attribute
        self.prior_type = prior_type
        # Set the value of the parameter
        self.value = value
        ## Initialise the info regarding the content of the parametrisation file
        self.__paramfile_info = {"caracteristics": ["free", "value"],
                                 "prior": ["type", "args"]}

    @property
    def name(self):
        """Indicate if the paramater is a main parameter."""
        return self.__name

    @property
    def name_code(self):
        """Return the name of the ParamContainer that can be used in code."""
        return check_name_code(self.name)

    @property
    def full_name(self):
        """Indicate if the paramater is a main parameter."""
        if self.__name_prefix is not None:
            return self.__name_prefix + "_" + self.__name
        else:
            return self.__name

    @property
    def free(self):
        """Indicate if the paramater is a free parameter."""
        return self.__free

    @free.setter
    def free(self, boolean):
        """Indicate if the paramater is a free parameter."""
        if isinstance(boolean, bool):
            ## Indicate if this parameter is main or auxiliary: Boolean
            self.__free = boolean
        else:
            raise AssertionError("free should be a boolean.")

    @property
    def main(self):
        """Indicate if the paramater is a main parameter."""
        return self.__main

    @main.setter
    def main(self, boolean):
        """Indicate if the paramater is a main parameter."""
        if isinstance(boolean, bool):
            ## Indicate if this parameter is main or auxiliary: Boolean
            self.__main = boolean
        else:
            raise AssertionError("Main should be a boolean.")

    @property
    def value(self):
        """Return the value of the parameter."""
        return self.__value

    @value.setter
    def value(self, val):
        """Set the value of the parameter."""
        if isinstance(val, Number) or (val is None):
            self.__value = val
        else:
            raise AssertionError("value should be a number or None.")

    @property
    def joint_prior(self):
        """Indicate if the prior of the parameter is described by a joint prior."""
        return self.__joint_prior

    @joint_prior.setter
    def joint_prior(self, boolean):
        """Set the joint_prior attribute."""
        if isinstance(boolean, bool):
            self.__joint_prior = boolean
        else:
            raise AssertionError("joint_prior should be a boolean.")

    @property
    def prior_type(self):
        """Type of prior associated to the parameter (str)."""
        return self.__prior_type

    @prior_type.setter
    def prior_type(self, prior_str):
        """Set the prior_type attribute."""
        if isinstance(prior_str, str) or (prior_str is None):
            ## Give the type of prior: string, for example Gaussian, Uniform
            self.__prior_type = prior_str
        else:
            raise AssertionError("prior_type should be a str or None.")

    def get_prior_value(self):
        """Return the a priori density probability of parameter to be value."""
        if self.joint_prior:
            raise AttributeError("Currently it is not possible to get the prior value for"
                                 "parameter described by joint prior probability.")
        return self.prior_func(self.value)

    @property
    def paramfile_info(self):
        """Information about the content of the param file"""
        return self.__paramfile_info

    def get_paramfile_section(self, text_tab="", texttab_1tline=True,
                              entete_symb=" = ", quote_name=False):
        """Return the text to include in the parameter_file for this parameter.

        ----

        Arguments:
            text_tab : string,
                text giving the tabulation that needs to be added to this the text to obtain the
                good alignment in the input file.
        """
        if quote_name:
            entete = "'{}'{}{{".format(self.name_code, entete_symb)
        else:
            entete = "{}{}{{".format(self.name_code, entete_symb)
        space_entete_param = spacestring_like(entete)
        text = ""
        # First is the name of the parameter
        if texttab_1tline:
            text += text_tab
        text += entete
        # First key of the parameter dictionnary is 'free' for free parameter or fixed.
        text += "'free': True,\n".format(self.name)
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

    def load_config(self, dico_config):
        """Load the configuration specified by the parameter dictionnary.

        ----

        Arguments:
            dico : dict,
                dictionnary giving the configuration.
        """
        for carac in self.paramfile_info["caracteristics"]:
            if carac in dico_config:
                if getattr(self, carac) != dico_config[carac]:
                    logger.debug("{} attribute of param {} changed from {} to {}"
                                 "".format(carac,
                                           self.full_name,
                                           getattr(self, carac),
                                           dico_config[carac]))
                    setattr(self, carac, dico_config[carac])
