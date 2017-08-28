#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
datasimulator documented function module.
"""
from pandas import DataFrame
from collections import Iterable

from ....tools.function_w_doc import DocFunction

## String used for the instrument category column in ouput_info of DatasimDocFunc
instcat_key = "inst_cat"

## String used for the instrument model full name column in ouput_info of DatasimDocFunc
instmodfullname_key = "inst_mod_fullname"

## String used for the dataset column in ouput_info of DatasimDocFunc
dtst_key = "dataset_name"


class DatasimDocFunc(DocFunction):
    """docstring for DatasimDocFunc."""

    _instmod_key = "inst_model_fullnames"
    _dtst_key = "datasets"

    def __init__(self, function, params_model, inst_cat, dataset_kwargs=None,
                 inst_model_fullname=None, dataset=None):
        """Initialise the datasim doc function.

        :param function function: function of the datasimulator
        :param Iterable_of_string params_model: Iterable giving the ordered list of the model
            parameters as they should be provided to the function.
        :param Iterable_of_string/string inst_cat: Iterable giving the ordered list of the outputs
            instrument categories.
        :param string/None dataset_kwargs: String giving the way the dataset_kwargs (like the time
            vector or a time reference) should be given to function. If None it means that the
            dataset kwargs are already included in function and should not be provided.
        :param Iterable_of_string/string/None inst_model_fullname:
            If None, the datasimulator doesn't include instrumental effect
            If string, the datasimulator simulate only one instrument model and this is its full
                name
            If Iterable, give the list of full names of the instrument models simulated (some might
                be None). This list will be matched to the list of datasets if provided.
        :param Iterable_of_string/string/None dataset:
            If None, the datasimulator doesn't include dataset kwargs
            If string, the datasimulator simulate only one dataset and this is its name
            If Iterable, give the list of names of the datasets simualted. This list will be matched
                to the list of inst_model_fullnames if provided.
        """
        # Initialise the params_model property
        self._init_params_model(params_model)

        # Get the arg_list input for DocFunction and initialise the include_dataset_kwarg property
        arg_list = self._init_arg_list_and_include_dataset_kwarg(params_model, dataset_kwargs)

        # Check inst_model_fullname input and tell if multi instrument models are provided
        multi_inst_model = self._check_inst_model_fullname(inst_model_fullname)

        # Check dataset input and tell if multi datasets are provided
        multi_dataset = self._check_dataset(dataset)

        # Check inst_cat input and tell if there is multi_outputs
        multi_outputs = self._check_inst_cat(inst_cat)

        # Init the output_info property
        self._init_output_info(multi_outputs, inst_cat, multi_inst_model, inst_model_fullname,
                               multi_dataset, dataset)

        super(DatasimDocFunc, self).__init__(function=function, arg_list=arg_list)

    def _init_params_model(self, params_model):
        self.__params_models = list(params_model)

    def _init_arg_list_and_include_dataset_kwarg(self, params_model, dataset_kwargs):
        # Check the content of dataset_kwargs: If provided set include_dataset_kwarg to False,
        # otherwise to True. Also define the arg_list parameter for __init__ method of DocFunction
        if dataset_kwargs is None:
            self.__include_dataset_kwarg = True
            arg_list = str(params_model)
        else:
            self.__include_dataset_kwarg = False
            arg_list = str(params_model) + dataset_kwargs

        return arg_list

    def _check_inst_model_fullname(self, inst_model_fullname):
        # Check the content of inst_model_fullname: If not provided or string set multi_inst_model
        # to False, otherwise to True.
        instmod_err = False
        if inst_model_fullname is None or isinstance(inst_model_fullname, str):
            multi_inst_model = False
        elif isinstance(inst_model_fullname, Iterable):
            if isinstance(inst_model_fullname[0], str):
                multi_inst_model = True
            else:
                instmod_err = True
        else:
            instmod_err = True
        if instmod_err:
            raise ValueError("inst_model_fullnames should be None, string or list of strings.")
        return multi_inst_model

    def _check_dataset(self, dataset):
        # Check the content of dataset: If not provided or string set multi_dataset
        # to False, otherwise to True.
        dataset_err = False
        if dataset is None or isinstance(dataset, str):
            multi_dataset = False
        elif isinstance(dataset, Iterable):
            if isinstance(dataset[0], str):
                multi_dataset = True
            else:
                dataset_err = True
        else:
            dataset_err = True
        if dataset_err:
            raise ValueError("datasets should be None, string or list of strings.")
        return multi_dataset

    def _check_inst_cat(self, inst_cat):
        # Check the content of inst_cat: If string set multi_dataset to False, otherwise to True.
        instcat_err = False
        if isinstance(inst_cat, str):
            multi_outputs = False
        elif isinstance(inst_cat, Iterable):
            if isinstance(inst_cat[0], str):
                multi_outputs = True
            else:
                instcat_err = True
        else:
            instcat_err = True
        if instcat_err:
            raise ValueError("inst_cats should a string or a list of strings.")
        return multi_outputs

    def _init_output_info(self, multi_outputs, inst_cat, multi_inst_model, inst_model_fullname,
                          multi_dataset, dataset):
        # Fill output_info giving the instrument category, the instrument model full name and the
        # dataset name for each ouput of the datasimulator function.
        if multi_outputs:
            noutput = len(inst_cat)
            l_instcat = list(inst_cat)
            if multi_inst_model:
                if len(inst_model_fullname) != noutput:
                    raise ValueError("inst_model_fullnames should have the same length as inst_cats"
                                     " or a string (meaning that all the ouputs have the same "
                                     "instrument model).")
                else:
                    l_instmod = list(inst_model_fullname)
            else:
                l_instmod = [inst_model_fullname for ii in range(noutput)]
            if multi_dataset:
                if len(dataset) != noutput:
                    raise ValueError("datasets should have the same length as inst_cats or a string"
                                     " (meaning that all the ouputs have the same dataset).")
                else:
                    l_dataset = list(dataset)
            else:
                l_dataset = [dataset for ii in range(noutput)]
        else:
            if multi_inst_model or multi_dataset:
                raise ValueError("You can't provide multiple datasets or instrument models if there"
                                 "only one output (len(inst_cats) = 1)")
            else:
                l_instcat = [inst_cat]
                l_instmod = [inst_model_fullname]
                l_dataset = [dataset]
        self.__output_info = DataFrame({instcat_key: l_instcat, instmodfullname_key: l_instmod,
                                        dtst_key: l_dataset})

    @property
    def include_dataset_kwarg(self):
        """If True the function include the dataset(s) kwarg(s) already."""
        return self.__include_dataset_kwarg

    @property
    def multi_dataset(self):
        """If True the datasim function simulates several datasets."""
        raise NotImplementedError

    @property
    def multi_inst_model(self):
        """If True the datasim function simulates several instrument models."""
        raise NotImplementedError

    @property
    def multi_output(self):
        """If True the datasim function simulates several outputs."""
        return self.__output_info.index.count() > 1

    @property
    def output_info(self):
        """Return a table with the instrument category, model and datasets used for the outputs."""
        return self.__output_info

    @property
    def inst_cat(self):
        """Return the Serie of instrument category used for the ouputs."""
        return self.output_info[instcat_key]

    @property
    def instmodel_fullname(self):
        """Return the Serie of instrument model full names used for the ouputs."""
        return self.output_info[instmodfullname_key]

    @property
    def dataset(self):
        """Return the Serie of dataset names used for the ouputs."""
        return self.output_info[dtst_key]

    @property
    def params_model(self):
        """Return the ordered list of model of the function."""
        return self.__params_models
