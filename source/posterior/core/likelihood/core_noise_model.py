#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
core_noise_model module.

The objective of this module is to define the Core_NoiseModel Class.

@DONE:
    -

@TODO:
    -
"""
from logging import getLogger
from copy import deepcopy
from collections import OrderedDict

from ....tools.metaclasses import MandatoryReadOnlyAttr
from ....tools.function_w_doc import DocFunction
from ....tools.dico_database import Nesteddict_wfixellvlnb


## Logger
logger = getLogger()


class Metaclass_NoiseModel(MandatoryReadOnlyAttr):

    def __init__(cls, name, bases, attrs):
        super(Metaclass_NoiseModel, cls).__init__(name, bases, attrs)
        l_mandatory_methods = ["_get_arg_list_one_dataset", "lnlike_creator", "lnlike",
                               "_check_parametrisation_dataset", "apply_parametrisation"]
        if cls.__name__ not in ["Core_Noise_Model", ]:
            missing_attrs = ["{}".format(attr) for attr in l_mandatory_methods
                             if not hasattr(cls, attr)]
            if len(missing_attrs) > 0:
                raise AttributeError("class '{}' requires attribute {}".format(name, missing_attrs))


class Core_Noise_Model(object, metaclass=Metaclass_NoiseModel):
    """Docstring for Core_Noise_Model class."""

    __mandatoryattrs__ = ["category", ]

    def __init__(self, datasim_docfunc, model_instance, instmodel_obj):
        """Initialise a Core_Noise_Model subclass instance.

        The model_instance and instmod_full_name arguments are not used in the function below but
        they are here to remind us that datasim_docfunc, model_instance, inst_model_obj are the
        only possible arguments for a init method a Core_Noise_Model subclass.
        """
        err_msg = ("datasim_docfunc should be a DocFunction instance or a dict of DocFunction"
                   "instances ! Got {} {}.")
        if isinstance(datasim_docfunc, DocFunction):  # Check the datasim_docfunc argument
            self.datasim_docfunc = datasim_docfunc
            self.__multidataset = False
        elif isinstance(datasim_docfunc, OrderedDict):
            value = datasim_docfunc[list(datasim_docfunc.keys())[0]]
            if isinstance(value, DocFunction):
                self.datasim_docfunc = datasim_docfunc
                self.__multidataset = True
            else:
                raise ValueError(err_msg.format(type(datasim_docfunc), type(value)))
        else:
            raise ValueError(err_msg.format(type(datasim_docfunc)))
        self.instmodel_obj = instmodel_obj  # Set the instmodel_obj attributes
        self.check_parametrisation(model_instance, instmodel_obj)  # Check correct parametrisation
        # Make Core_NoiseModel an abstract class
        if type(self) is Core_Noise_Model:
            raise NotImplementedError("Core_NoiseModel should not be instanciated!")

    def __call__(self, p, data, data_err, **kwarg_data):
        return self.lnlike(p, data, data_err, **kwarg_data)

    @property
    def multidataset(self):
        """Return true if the noise model is used for multiple datasets."""
        return self.__multidataset

    @property
    def l_dataset(self):
        """Return the list of datasets."""
        if self.multidataset:
            return list(self.datasim_docfunc.keys())
        else:
            return None

    def get_instmodel_obj(self, dataset_key=None):
        if self.multidataset:
            return self.instmodel_obj[dataset_key]
        else:
            return self.instmodel_obj

    def get_datasim_arg_list(self, dataset_key=None):
        """Return the datasim function."""
        if self.multidataset:
            return self.datasim_docfunc[dataset_key].arg_list
        else:
            return self.datasim_docfunc.arg_list

    def get_datasim_function(self, dataset_key=None):
        """Return the datasim function."""
        if self.multidataset:
            return self.datasim_docfunc[dataset_key].function
        else:
            return self.datasim_docfunc.function

    def _get_arg_list_one_dataset(self, dataset_key=None):
        arg_list_new = deepcopy(self.get_datasim_arg_list(dataset_key))
        arg_list_new["kwargs"] = ["data", "data_err"] + arg_list_new["kwargs"]
        return arg_list_new

    def get_arg_list(self, dataset_key=None):
        if self.multidataset:
            if (dataset_key == "all") or (dataset_key is None):
                arg_list_new = OrderedDict()
                arg_list_new["param"] = []
                arg_list_new["kwargs"] = Nesteddict_wfixellvlnb(nb_lvl=1, ordered=True,
                                                                default=list)
                l_allparams = []
                for dataset_key in self.l_dataset:
                    arg_list_dataset = self.get_arg_list(dataset_key)
                    for par in arg_list_dataset["param"]:
                        if par not in l_allparams:
                            l_allparams.append(par)
                    for kwarg_type in arg_list_dataset["kwargs"]:
                        arg_list_new["kwargs"][kwarg_type].append(dataset_key)
                arg_list_new["param"].extend(l_allparams)
                return arg_list_new
            else:
                return self._get_arg_list_one_dataset(dataset_key)
        else:
            return self._get_arg_list_one_dataset()

    # def __get_odico_indexes(self):
    #     res = OrderedDict()
    #     for dataset in self.l_dataset:
    #         idx_par = []
    #         for par in self.datasim_docfunc[dataset].arg_list["param"]:
    #             idx_par.append(self.arg_list["param"].index(par))
    #         res[dataset].append(idx_par)
    #     return res

    def lnlike_creator(self):
        """Return a DocFunction"""
        raise NotImplementedError("You need to implement a lnlike_creator method for your noise "
                                  "model.")

    def lnlike(self, p, data, data_err, **kwarg_data):
        """Return the value of the log likelihood. The arg_list is provided by get_arg_list()"""
        raise NotImplementedError("You need to implement a lnlike method for your noise "
                                  "model.")

    def get_param_idxs(self, dataset_key):
        """Return the list of param indexes."""
        if self.multidataset:
            idx_par = []
            l_param_name_all = self.get_arg_list()["param"]
            for par in self.get_arg_list(dataset_key)["param"]:
                idx_par.append(l_param_name_all.index(par))
            return idx_par
        else:
            raise ValueError("It doesn't make sense to ask for the param idx if you don't have "
                             "multiple dataset. The result is range(nb_param)...")

    def check_parametrisation(self, model_instance, instmod_obj):
        """For this noise model there is no additional parameter required.

        If you create your own noise model and you need additional parameter you should superseed
        this method to create those parameter and make them main parameters.
        """
        if self.multidataset:
            for dataset in self.l_dataset:
                self._check_parametrisation_dataset(model_instance,
                                                    dataset)
        else:
            self._check_parametrisation_dataset(model_instance)

    def _check_parametrisation_dataset(self, model_instance, dataset_key=None):
        """Check the parameterisation for the model associate to 1 dataset only."""
        raise NotImplementedError("You need to implement a _check_parametrisation_dataset method "
                                  "for your noise model.")

    @classmethod
    def apply_parametrisation(cls, model_instance, instmod_fullname):
        """Add in the model the necessary main parameters for the noise model."""
        raise NotImplementedError("You need to implement a apply_parametrisation method for your "
                                  "noise model.")
