#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Parameter module.

The objective of this module is to define the Parameter class.

TODO:
    - Change the value.setter to check if value is within the prior
"""
from logging import getLogger
from numbers import Number

from astropy.units import NamedUnit

from source.tools.name import Named
from source.tools.miscellaneous import spacestring_like
from .prior.parameter_prior import Parameter_Prior


## Logger Object
logger = getLogger()


# TODO: Add the possibility to add a description of the parameter.


class Parameter(Named, Parameter_Prior):
    """docstring for Parameter."""

    def __init__(self, name, name_prefix=None, unit=None, free=True, main=False, value=None,
                 kwargs_getname_4_storename={}, kwargs_getname_4_codename={},
                 **kwargs_prior):
        """Create a Parameter Instance.

        :param str name: Name of the parameter
        :param str/Name/None name_prefix: (facultative) Prefix for the name (use for the full name)
        :param bool free: (default: None), True if you want the parameter to be free, False otherwise
        :param bool main: (default: None), True if you want the parameter to be a main parameter,
            False if it's an auxiliary parameter. Being a main parameter implies that you belong
            to the minium set of parameter used for the model and that you have the possibility
            to be jumped or fixed (free or not). Being an auxialiary parameter implies that your
            value is defined by the value of the main parameters (so you can be free or not but it
            doesn't depend on you).
        :param number(float) value: (default:None) Number giving the current value of the parameter,
            can be used in the initialization to define the initial value.
        :param dict kwargs_getname_4_storename: Parameters for the Named.get_name method to construct
            the parameter names for storing in a param container database
        :param dict kwargs_getname_4_codename: Parameters for the Named.get_name method to construct
            the parameter names for reference in codes.

        Keyword arguments (kwargs_prior) are provided to Parameter_Prior.__init__ (see its docstring
        for more info). They can be used to change the default prior for a parameter (which is uniform
        between 0 and 1 otherwise.)
        """
        super(Parameter, self).__init__(name=name, prefix=name_prefix, kwargs_getname_4_storename=kwargs_getname_4_storename,
                                        kwargs_getname_4_codename=kwargs_getname_4_codename)
        # Set the free attribute
        self.free = free
        # Set the main attribute
        self.main = main
        # Set the value of the parameter
        self.value = value
        ## Unit of the value
        self.__unit = None
        if unit is not None:
            self.unit = unit
        # Initialise the info regarding the content of the parametrisation file for a Parameter
        self.__paramfile_info = {"caracteristics": ["free", "value"]  # Caracteristics beside the prior info
                                 }
        # Initialisation relative to the Prior.
        Parameter_Prior.__init__(self, self.__paramfile_info, **kwargs_prior)

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
    def unit(self):
        """Return the unit of the value of the parameter."""
        return self.__unit

    @unit.setter
    def unit(self, unt):
        """Set the unit of the parameter.

        :param str/astropy.units.Unit unt:
        """
        if self.__unit is None:
            if isinstance(unt, NamedUnit) or isinstance(unt, str):
                self.__unit = unt
            else:
                raise TypeError("unit should be a string or a astropy.units.Unit")
        else:
            if unt != self.__unit:
                raise AssertionError("unit is already defined to {}. You are not allowed to modify it."
                                     "".format(self.__unit))

    @property
    def paramfile_info(self):
        """Dictionary with contain the name of the information which can be set in the param file.

        It is filled in the __init__ method of this class.
        """
        return self.__paramfile_info

    def get_paramfile_section(self, text_tab="", texttab_1tline=True,
                              entete_symb=" = ", quote_name=False):
        """Return the text to include in the parameter_file for this parameter.

        :param str text_tab : text giving the tabulation that needs to be added to this the text to
            obtain the good alignment in the input file.
        """
        if quote_name:
            entete = "'{}'{}{{"
        else:
            entete = "{}{}{{"
        entete = entete.format(self.get_name(code_version=True), entete_symb)
        space_entete_param = spacestring_like(entete)
        text = ""
        # First is the name of the parameter
        if texttab_1tline:
            text += text_tab
        text += entete
        # First key of the parameter dictionnary is 'free' for free parameter or fixed.
        text += "'free': {},\n".format(self.free)
        # Second key is the value
        text += text_tab + space_entete_param + "'value': {},  # unit: {}\n".format(self.value,
                                                                                    self.unit)
        # Finally the prior info
        text += Parameter_Prior.get_paramfile_section(self, text_tab=text_tab + space_entete_param)
        return text

    def load_config(self, dico_config, **kwargs_prior):
        """Load the configuration specified by the parameter dictionnary.

        :param dict dico_config : Dictionnary giving the configuration.

        Keyword arguments are provided to Parameter_Prior.load_config (see its docstring for more
        info).
        """
        for carac in self.paramfile_info["caracteristics"]:
            if carac in dico_config:
                if getattr(self, carac) != dico_config[carac]:
                    logger.debug("{} attribute of param {} changed from {} to {}"
                                 "".format(carac,
                                           self.get_name(include_prefix=True, recursive=True),
                                           getattr(self, carac),
                                           dico_config[carac]))
                    setattr(self, carac, dico_config[carac])
        if self.free:
            Parameter_Prior.load_config(self, dico_config, **kwargs_prior)
