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
        l_mandatory_methods = ["lnlike_creator", "lnlike"]
        if cls.__name__ not in ["Core_Noise_Model", ]:
            missing_attrs = ["{}".format(attr) for attr in l_mandatory_methods
                             if not hasattr(cls, attr)]
            if len(missing_attrs) > 0:
                raise AttributeError("class '{}' requires attribute {}".format(name, missing_attrs))


class Core_Noise_Model(object, metaclass=Metaclass_NoiseModel):
    """Docstring for Core_Noise_Model class."""

    __mandatoryattrs__ = ["category", "allow_multidataset"]

    def __init__(self, datasim_docfunc, model_instance, instmodel_obj):
        """Initialise a Core_Noise_Model subclass instance.

        The model_instance and instmod_full_name arguments are not used in the function below but
        they are here to remind us that datasim_docfunc, model_instance, inst_model_obj are the
        only possible arguments for a init method a Core_Noise_Model subclass.
        """
        if self.allow_multidataset:
            err_msg = ("datasim_docfunc should be a DocFunction instance or a dict of doc instance "
                       "! Got {}.")
        else:
            err_msg = "datasim_docfunc should be a DocFunction instance. Got {}."
        if isinstance(datasim_docfunc, DocFunction):
            self.datasim_docfunc = datasim_docfunc
            self.__multidataset = False
        elif self.allow_multidataset and isinstance(datasim_docfunc, OrderedDict):
            value = datasim_docfunc[list(datasim_docfunc.keys())[0]]
            if isinstance(value, DocFunction):
                self.datasim_docfunc = datasim_docfunc
                self.__multidataset = True
            else:
                ValueError(err_msg.format(type(datasim_docfunc)))
        else:
            raise ValueError(err_msg.format(type(datasim_docfunc)))
        # Make Core_NoiseModel an abstract class
        if type(self) is Core_Noise_Model:
            raise NotImplementedError("Core_NoiseModel should not be instanciated!")

    def __call__(self, p, data, data_err, **kwarg_data):
        return self.lnlike(p, data, data_err, **kwarg_data)

    def get_datasim_function(self, dataset_key=None):
        """Return the datasim function."""
        if self.multidataset:
            return self.datasim_docfunc[dataset_key].function
        else:
            return self.datasim_docfunc.function

    @property
    def multidataset(self):
        """Return true if the noise model is used for multiple datasets."""
        return self.__multidataset

    @property
    def arg_list(self):
        if self.multidataset:
            arg_list_new = {}
            arg_list_new["kwargs"] = Nesteddict_wfixellvlnb(nb_lvl=1, ordered=True, default=list)
            l_set_param = []
            for dataset_key in self.datasim_docfunc:
                l_set_param.append(self.datasim_docfunc[dataset_key].arg_list["param"])
                arg_list_new["kwargs"]["data"].append(dataset_key)
                arg_list_new["kwargs"]["data_err"].append(dataset_key)
                for kwarg in self.datasim_docfunc[dataset_key].arg_list["kwargs"]:
                    arg_list_new["kwargs"][kwarg].append(dataset_key)
            arg_list_new["param"] = set.union(*l_set_param)
            return arg_list_new
        else:
            return deepcopy(self.datasim_docfunc.arg_list)

    @classmethod
    def check_parametrisation(cls, model_instance, instmod_fullname):
        """For this noise model there is no additional parameter required.

        If you create your own noise model and you need additional parameter you should superseed
        this method to create those parameter and make them main parameters.
        """
        pass
