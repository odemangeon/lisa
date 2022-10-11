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

from lisa.tools.name import Named
from .prior.parameter_prior import Parameter_Prior


## Logger Object
logger = getLogger()


# TODO: Add the possibility to add a description of the parameter.
class Named_Parameter(Named):
    """docstring for Named_Parameter(Named):."""

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__, self.get_name(include_prefix=True, recursive=True, force_no_duplicate=True))

    def get_name(self, include_prefix=False, code_version=False, recursive=False, prefix_kwargs=None,
                 force_no_duplicate=False):
        """Return the name of the parameter.

        Parameters
        ----------
        include_prefix : bool
            If True (default False) include the name prefix in the output.
        code_version : bool
            If True (default False) return the code version of the name of the parameter
        recursive : bool
            If True (default False) apply the arguments include_prefix, code_version, and recursive
            itself to the prefix (Superseed the content of prefix_kwargs).
        prefix_kwargs : dict
            Dictionary with the arguments to pass to the get_name method of name_prefix
        force_no_duplicate : bool
            If True the function will not go to the duplicate if the parameter is a duplicate.

        Returns
        -------
        name : str
            String providing the name of the instance
        """
        if (self.duplicate is None) or force_no_duplicate:
            return self.name.get(include_prefix=include_prefix, code_version=code_version, recursive=recursive,
                                 prefix_kwargs=prefix_kwargs)
        else:
            return self.duplicate.name.get(include_prefix=include_prefix, code_version=code_version,
                                           recursive=recursive, prefix_kwargs=prefix_kwargs)


class Parameter(Named_Parameter, Parameter_Prior):
    """docstring for Parameter."""

    def __init__(self, name, name_prefix=None, unit=None, free=True, main=False, value=None,
                 kwargs_getname_4_storename={}, kwargs_getname_4_codename={},
                 **kwargs_prior):
        """Create a Parameter Instance.

        Parameters
        ----------
        name : str
            Name of the parameter
        name_prefix : st or Name or None
            Prefix for the name (use for the full name)
        free : bool
            True if you want the parameter to be free, False otherwise
        main : bool
            True if you want the parameter to be a main parameter,
            False if it's an auxiliary parameter. Being a main parameter implies that you belong
            to the minium set of parameter used for the model and that you have the possibility
            to be jumped or fixed (free or not). Being an auxialiary parameter implies that your
            value is defined by the value of the main parameters (so you can be free or not but it
            doesn't depend on you).
        value : number(float)
            Number giving the current value of the parameter, can be used in the initialization to define
            the initial value.
        kwargs_getname_4_storename : dict
            parameters for the Named.get_name method to construct the parameter names for storing in
            a param container database
        kwargs_getname_4_codename : dict
            parameters for the Named.get_name method to construct the parameter names for reference in
            codes.

        Keyword arguments (kwargs_prior) are provided to Parameter_Prior.__init__ (see its docstring
        for more info). They can be used to change the default prior for a parameter (which is uniform
        between 0 and 1 otherwise.)
        """
        super(Parameter, self).__init__(name=name, prefix=name_prefix, kwargs_getname_4_storename=kwargs_getname_4_storename,
                                        kwargs_getname_4_codename=kwargs_getname_4_codename)
        # Set the duplicate attribute
        self.duplicate = None
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
        self.__paramfile_info = {"caracteristics": ["duplicate", "free", "value"]  # Caracteristics beside the prior info
                                 # duplicate should always be the first one.
                                 }
        # Initialisation relative to the Prior.
        Parameter_Prior.__init__(self, self.__paramfile_info, **kwargs_prior)

    @property
    def duplicate(self):
        """If different from None, then the parameter is a duplicate of the Parameter instance returned."""
        return self.__duplicate

    @duplicate.setter
    def duplicate(self, dup):
        """If different from None, then the parameter is a duplicate of the Parameter instance provided."""
        if (dup is None) or isinstance(dup, Parameter):
            ## Indicate if this parameter is main or auxiliary: Boolean
            self.__duplicate = dup
        else:
            raise AssertionError("duplicate should be a Parameter instance or None.")

    @property
    def free(self):
        """Indicate if the paramater is a free parameter."""
        if self.duplicate is None:
            return self.__free
        else:
            return self.duplicate.free

    @free.setter
    def free(self, boolean):
        """Indicate if the paramater is a free parameter."""
        if self.duplicate is None:
            if isinstance(boolean, bool):
                ## Indicate if this parameter is main or auxiliary: Boolean
                self.__free = boolean
            else:
                raise AssertionError("free should be a boolean.")
        else:
            self.duplicate.free = boolean

    @property
    def main(self):
        """Indicate if the paramater is a main parameter."""
        if self.duplicate is None:
            return self.__main
        else:
            return self.duplicate.main

    @main.setter
    def main(self, boolean):
        """Indicate if the paramater is a main parameter."""
        if self.duplicate is None:
            if isinstance(boolean, bool):
                ## Indicate if this parameter is main or auxiliary: Boolean
                self.__main = boolean
            else:
                raise AssertionError("Main should be a boolean.")
        else:
            self.duplicate.main = boolean

    @property
    def value(self):
        """Return the value of the parameter."""
        if self.duplicate is None:
            return self.__value
        else:
            return self.duplicate.value

    @value.setter
    def value(self, val):
        """Set the value of the parameter."""
        if self.duplicate is None:
            if isinstance(val, Number) or (val is None):
                self.__value = val
            else:
                raise AssertionError("value should be a number or None.")
        else:
            self.duplicate.value = val

    @property
    def unit(self):
        """Return the unit of the value of the parameter."""
        if self.duplicate is None:
            return self.__unit
        else:
            return self.duplicate.unit

    @unit.setter
    def unit(self, unt):
        """Set the unit of the parameter.

        :param str/astropy.units.Unit unt:
        """
        if self.duplicate is None:
            if self.__unit is None:
                if isinstance(unt, NamedUnit) or isinstance(unt, str):
                    self.__unit = unt
                else:
                    raise TypeError("unit should be a string or a astropy.units.Unit")
            else:
                if unt != self.__unit:
                    raise AssertionError("unit is already defined to {}. You are not allowed to modify it."
                                         "".format(self.__unit))
        else:
            self.duplicate.unit = unt

    @property
    def paramfile_info(self):
        """Dictionary with contain the name of the information which can be set in the param file.

        It is filled in the __init__ method of this class.
        """
        if self.duplicate is None:
            return self.__paramfile_info
        else:
            return self.duplicate.paramfile_info

    # def get_paramfile_section(self, text_tab="", texttab_1tline=True,
    #                           entete_symb=" = ", quote_name=False):
    #     """Return the text to include in the parameter_file for this parameter.
    #
    #     :param str text_tab : text giving the tabulation that needs to be added to this the text to
    #         obtain the good alignment in the input file.
    #     """
    #     if quote_name:
    #         entete = f"'{self.get_name(recursive=False, include_prefix=False, code_version=False)}'{entete_symb}" + "{"
    #     else:
    #         entete = f"{self.get_name(recursive=False, include_prefix=False, code_version=False)}{entete_symb}" + "{"
    #     space_entete_param = spacestring_like(entete)
    #     text = ""
    #     # First is the name of the parameter
    #     if texttab_1tline:
    #         text += text_tab
    #     text += entete
    #     # Duplicate key
    #     text += f"'duplicate': {self.duplicate},\n"
    #     # Free key
    #     text += text_tab + space_entete_param + f"'free': {self.free},\n"
    #     # Value key
    #     text += text_tab + space_entete_param + f"'value': {self.value},  # unit: {self.unit}\n"
    #     # Finally the prior info
    #     text += Parameter_Prior.get_paramfile_section(self, text_tab=text_tab + space_entete_param)
    #     return text

    def get_paramfile_dict(self):
        """
        """
        dico_param_file = {}
        dico_param_file['duplicate'] = self.duplicate
        dico_param_file['free'] = self.free
        dico_param_file['value'] = self.value
        dico_param_file['unit'] = self.unit
        dico_param_file['prior'] = Parameter_Prior.get_paramfile_dict(self)
        return dico_param_file

    def load_config(self, dico_config, model_instance, **kwargs_prior):
        """Load the configuration specified by the parameter dictionnary.

        :param dict dico_config : Dictionnary giving the configuration.

        Keyword arguments are provided to Parameter_Prior.load_config (see its docstring for more
        info).
        """
        for carac in self.paramfile_info["caracteristics"]:
            if (carac == "duplicate") or (self.duplicate is None):
                if carac in dico_config:
                    if getattr(self, carac) != dico_config[carac]:
                        logger.debug("{} attribute of param {} changed from {} to {}"
                                     "".format(carac,
                                               self.get_name(include_prefix=True, recursive=True),
                                               getattr(self, carac),
                                               dico_config[carac]))
                        if carac == "duplicate":
                            if dico_config[carac] is None:
                                setattr(self, carac, dico_config[carac])
                            else:
                                param_duplicated = model_instance.get_parameter(dico_config[carac],
                                                                                kwargs_get_list_params={'recursive': True, 'main': True, 'no_duplicate': False},
                                                                                kwargs_get_name={'include_prefix': True, 'recursive': True, 'force_no_duplicate': True, 'code_version': False})
                                setattr(self, carac, param_duplicated)
                        else:
                            setattr(self, carac, dico_config[carac])
                else:
                    raise ValueError(f"key {carac} is missing from the dictionary of parameter {self.get_name(include_prefix=True, recursive=True)}")
        if self.free and (self.duplicate is None):
            Parameter_Prior.load_config(self, dico_config=dico_config, **kwargs_prior)
