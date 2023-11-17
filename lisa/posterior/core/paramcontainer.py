#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Core_ParamContainer module.

The objective of this module is to define the Core_ParamContainer class wich is an object defined by
a set of parameters. It could be a Planet or a Star for exoplanet models
"""
from loguru import logger
from collections import OrderedDict

from ...tools.metaclasses import MandatoryReadOnlyAttr
from ...tools.name import Named  # , check_getname_kwargs
from .parameter import Parameter


key_params_fileinfo = "Param names"


class Core_ParamContainer(Named, metaclass=MandatoryReadOnlyAttr):
    """docstring for Core_ParamContainer."""

    __mandatoryattrs__ = ["category"]

    __parameters = None  # This is needed to be able to pickle the object. UnPickle doesn't call __init__ but call __getattr__ and self._parameters was only defined by __init__

    def __init__(self, name, name_prefix=None, **kwargs):
        """docstring Core_ParamContainer init method.

        :param str name: Name of the parameter container instance.
        :param str/Name/None name_prefix: Prefix for the parameter container instance.

        Keyword arguments are passed to Named.__init__ (see docstring for more info)
        """
        ## Parameters WARNING, BECAUSE OF THE __GETATTR__ METHOD THIS HAS TO BE THE FIRST LINE !
        self.__parameters = OrderedDict()
        ## Do the Name class init
        super(Core_ParamContainer, self).__init__(name=name, prefix=name_prefix, **kwargs)
        ## This class is not meant to be instanciated but subclassed and then instanciated.
        if type(self) is Core_ParamContainer:
            raise NotImplementedError("Core_ParamContainer should not be instanciated !")

    def __getattr__(self, attr=""):
        """Intercept attribute call to look in the parameter list."""
        l_param_store_names = [param.store_name for param in Core_ParamContainer.__get_list_all_params(self)]
        l_param_code_names = [param.code_name for param in Core_ParamContainer.__get_list_all_params(self)]
        if attr in l_param_store_names:
            return self.parameters[attr]
        elif attr in l_param_code_names:
            return self.parameters[l_param_store_names[l_param_code_names.index(attr)]]
        else:
            # Default behaviour
            raise AttributeError("{}".format(attr))

    @property
    def parameters(self):
        """Parameters contained in the Core_ParamContainer."""
        return self.__parameters

    def add_parameter(self, parameter):
        """Add a parameter to the Core_ParamContainer."""
        if isinstance(parameter, Parameter):
            self.parameters[parameter.store_name] = parameter
        else:
            raise ValueError("parameter should be an instance of the Parameter class")

    def __get_list_all_params(self):
        """Return the list of all parameters."""
        return list(self.parameters.values())

    def __get_list_all_paramnames_storenames(self):
        """Return the list of all parameters."""
        return list(self.parameters.keys())

    def get_list_params(self, main=False, free=False, no_duplicate=True, only_duplicates=False):
        """Return the list of all parameters.

        Arguments
        ---------
        main            : bool
            If true (default false) returns only the main parameters. If False all parameters are returned.
        free            : bool
            If true (default false) returns only the free parameters. If False, wether or the parameter
            is not free is not used to return it or not. the free argument only makes sense for main parameters,
            so it's ignored if main is not True.
        no_duplicate    : bool
            If True, the output list will not include the duplicate parameters, only the orignals
            no_duplicate and only_duplicates cannot be True at the same time
        only_duplicates : bool
            If True, the output list will only include duplicate parameters (not the original of these duplicates)
            no_duplicate and only_duplicates cannot be True at the same time

        Returns
        -------
        result : list of Parameter
            list of Parameter instances
        """
        if no_duplicate and only_duplicates:
            raise ValueError("no_duplicate and only_duplicates cannot be True at the same time")
        result = []
        for param in Core_ParamContainer.__get_list_all_params(self):
            add_param = False
            if only_duplicates:
                if param.duplicate is not None:
                    add_param = True
            else:
                if main:
                    if free and param.main and param.free:
                        add_param = True
                    elif not(free) and param.main:
                        add_param = True
                else:
                    add_param = True
            if add_param:
                if no_duplicate:
                    if param.get_name(include_prefix=True, recursive=True, force_no_duplicate=False) not in [param_in_res.get_name(include_prefix=True, recursive=True, force_no_duplicate=False) for param_in_res in result]:
                        result.append(param)
                else:
                    result.append(param)
        return result

    def get_list_paramnames(self, main=False, free=False, no_duplicate=True, only_duplicates=False, **kwargs):
        """Return the list of all parameters.

        Arguments
        ---------
        main            : bool
            If true (default false) returns only the main parameters. If False all parameters are returned.
        free            : bool
            If true (default false) returns only the free parameters. If False, wether or the parameter
            is not free is not used to return it or not. the free argument only makes sense for main parameters,
            so it's ignored if main is not True.
        no_duplicate    : bool
            If True, the output list will not include the duplicate parameters, only the orignals
            no_duplicate and only_duplicates cannot be True at the same time
        only_duplicates : bool
            If True, the output list will only include duplicate parameters (not the original of these duplicates)
            no_duplicate and only_duplicates cannot be True at the same time

        Keyword arguments are passed directly to the Named.get_name method (see docstring of
        for exhaustive information).

        Returns
        -------
        result  : list of Parameter instances
        """
        result = []
        for param in Core_ParamContainer.get_list_params(self, main=main, free=free, no_duplicate=no_duplicate, only_duplicates=only_duplicates):
            result.append(param.get_name(**kwargs))
        return result

    def _get_parameter_4_naming_kwargs(self, name, return_l_param_name=False, kwargs_get_name=None, kwargs_get_list_params=None):
        """Return parameter instance designated by it's name.

        :param str name: Name of the Parameter looked for.
        :param bool return_l_param_name: if True, return the list of existing parameter names
        :param dict kwargs_get_name: Keyword arguments dictionary for the Paremeter.get_name method.

        Keyword arguments are passed directly to the self.get_list_params method (see docstring of
        for exhaustive information).

        :return Parameter/None result: Parameter instance if uniquely found, None otherwise.
        :return str error_msg: If the parameter has been found "". If not, "unknown" if no parameter
            with this name exists or "duplicates" if several parameters with this name exists
        :return list_of_str l_paramnames: If return_l_param_name is True, the list of existing parameter
            names is returned.
        """
        if kwargs_get_list_params is None:
            kwargs_get_list_params = {}
        l_param = self.get_list_params(**kwargs_get_list_params)
        if kwargs_get_name is None:
            kwargs_get_name = {}
        l_param_names = [param.get_name(**kwargs_get_name) for param in l_param]
        if l_param_names.count(name) == 0:
            result = None
            error_msg = "unknown"
        elif l_param_names.count(name) == 1:
            result = l_param[l_param_names.index(name)]
            error_msg = ""
        else:
            result = None
            error_msg = "duplicates"
        if return_l_param_name:
            return result, error_msg, l_param_names
        else:
            return result, error_msg

    def get_parameter(self, name, notexist_ok=False, return_error=False, kwargs_get_list_params=None, kwargs_get_name=None):
        """Return the parameter instance designated by the name provided if possible.

        :param str name: Name of the Parameter looked for.
        :param bool return_error: If true return also the error message (error_msg)

        Keyword arguments are passed to the self.get_list_params method (see docstring of
        for exhaustive information).

        :return Parameter/None result: Parameter instance if found, None otherwise.
        :return str error_msg: If the parameter has been found "". If not, "unknown" if no parameter
            with this name exists or "duplicates" if several parameters with this name exists. Returned
            only if return_error is True
        """
        result, error_msg, l_paramnames = self._get_parameter_4_naming_kwargs(name, return_l_param_name=True,
                                                                              kwargs_get_name=kwargs_get_name,
                                                                              kwargs_get_list_params=kwargs_get_list_params)

        if notexist_ok:
            if return_error:
                return result, error_msg
            else:
                return result
        else:
            if result is None:
                raise ValueError(f"Parameter {name} not found. Error message = {error_msg}")
            else:
                if return_error:
                    return result, error_msg
                else:
                    return result

    def has_parameter(self, name, return_error=False, kwargs_get_list_params=None, kwargs_get_name=None):
        """Return True in the parameter designated by the name provided exists.

        :param str name: Name of the Parameter looked for.
        :param bool return_error: If true return also the error message (error_msg)

        Keyword arguments are passed to the self.get_list_params method (see docstring of
        for exhaustive information).

        :return bool has: True if the parameter as specified exists, False otherwise.
        :return str error_msg: If the parameter has been found "". If not, "unknown" if no parameter
            with this name exists or "duplicates" if several parameters with this name exists
        """
        result, error_msg = self.get_parameter(name, notexist_ok=True, return_error=True, kwargs_get_list_params=kwargs_get_list_params, kwargs_get_name=kwargs_get_name)
        has = (result is not None)
        if return_error:
            return has, error_msg
        else:
            return has

    @property
    def priors_dict(self):
        """
        """
        res = {}
        for param in self.get_list_params(main=True, free=True, no_duplicate=True):
            if not(param.is_a_duplicate):
                res[param.get_name()] = param.priors_dict
        return res

    def load_priors_config(self, dico_priors_config, available_joint_priors={}, load_setup=False):
        """load the configuration specified by the dictionnary

        :param dict dico_config: Dictionnary containing the new configuration for the main Parameters
            read from the parameter file.
        """
        for param in self.get_list_params(main=True, free=True, no_duplicate=False):
            if param.is_a_duplicate:
                continue
            if param.get_name() in dico_priors_config:
                param.load_prior_config(dico_prior_config=dico_priors_config[param.get_name()],
                                        available_joint_priors=available_joint_priors,
                                        load_setup=load_setup)
            else:
                raise ValueError(f"Parameter {param.full_name} not found in priors dictionary of the configuration file.")
