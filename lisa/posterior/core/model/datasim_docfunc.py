#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
datasimulator documented function module.
"""
from pandas import DataFrame
from collections.abc import Iterable

from ....tools.function_w_doc import DocFunction

## String used for the instrument category column in ouput_info of DatasimDocFunc
instcat_key = "inst_cat"

## String used for the instrument model full name column in ouput_info of DatasimDocFunc
instmodfullname_key = "inst_mod_fullname"

## String used for the dataset column in ouput_info of DatasimDocFunc
dtst_key = "dataset_name"


class DatasimDocFunc(DocFunction):
    """docstring for DatasimDocFunc."""

    def __init__(self, function, param_model_names_list, params_model_vect_name, inst_cats_list,
                 inst_model_fullnames_list, dataset_names_list,
                 include_dataset_kwarg, mand_kwargs_list=None, opt_kwargs_dict=None, forced_multioutput=False):
        """Initialise the datasim doc function.

        Arguments
        ---------
        function                    : function object
            function of the datasimulator
        param_model_names_list      : list of str
            List of the name of the model parameters as they should be provided to the function in the
            first argument
        params_model_vect_name      : str
            Name of the argument used for the model parameter vector
        inst_cats_list              : Iterable
            Iterable giving the ordered list of the outputs instrument categories.
            It has to match both inst_model_fullnames_list and dataset_names_list
        include_dataset_kwarg       : bool
            Boolean saying if the function include the dataset(s) keyword arguments.
        mand_kwargs_list            : List of str
            List of the names of the mandatory arguments besides the name of the model parameter vector
            (like the time vector or a time reference) which should be given to function after the
             model parameter vector.
        opt_kwargs_dict             : dict
            Dictionary whose keys are the name of the optional arguments of the function and the values
            are the default values for these arguments
        inst_model_fullnames_list   : Iterable_of_string/string
            If string, the datasimulator simulate only one instrument model and this is its full
            name.
            If Iterable, give the list of full names of the instrument models simulated.
            This list will be matched to dataset_names_list and inst_cats_list.
        dataset_names_list          : Iterable_of_string/string
            If string, the datasimulator simulate only one dataset and this is its name
            If Iterable, give the list of names of the datasets simualted. This list will be matched
            to inst_model_fullnames_list and inst_cats_list.
        """
        # Set param_model_list
        self.__param_model_names_list = list(param_model_names_list)

        # Set param_model_vect_name
        self.__param_model_vect_name = params_model_vect_name
        # add params_model_vect_name at the beginning of the mandatory keyword argument list
        if mand_kwargs_list is None:
            mand_kwargs_list = [params_model_vect_name, ]
        else:
            mand_kwargs_list = [params_model_vect_name, ] + mand_kwargs_list

        # Set include_dataset_kwarg
        self.__include_dataset_kwarg = include_dataset_kwarg

        # Check inst_model_fullname input and tell if multi instrument models are provided
        self.__multi_inst_model = self._check_inst_model_fullname(inst_model_fullnames_list)

        # Check dataset input and tell if multi datasets are provided
        self.__multi_dataset = self._check_dataset(dataset_names_list)

        # Check inst_cat input and tell if there is multi_outputs
        self.__multi_outputs = self._check_inst_cat(inst_cats_list)

        # Set self.__forced_multioutput
        self.__forced_multioutput = forced_multioutput

        # Init the output_info property
        self._init_output_info(self.__multi_outputs, inst_cats_list, self.__multi_inst_model,
                               inst_model_fullnames_list, self.__multi_dataset, dataset_names_list)

        super(DatasimDocFunc, self).__init__(function=function, mand_kwargs_list=mand_kwargs_list, opt_kwargs_dict=opt_kwargs_dict)

    def _check_inst_model_fullname(self, inst_model_fullnames_list):
        # Check the content of inst_model_fullnames_list: If not provided or string set multi_inst_model
        # to False, otherwise to True.
        instmod_err = False
        if isinstance(inst_model_fullnames_list, str):
            multi_inst_model = False
        elif isinstance(inst_model_fullnames_list, Iterable):
            l_isstr = [isinstance(inst_mod, str) for inst_mod in inst_model_fullnames_list]
            if all(l_isstr):
                multi_inst_model = True
            else:
                instmod_err = True
        else:
            instmod_err = True
        if instmod_err:
            raise ValueError("inst_model_fullnames should be a string or list of strings.")
        return multi_inst_model

    def _check_dataset(self, dataset_names_list):
        # Check the content of dataset: If not provided or string set multi_dataset
        # to False, otherwise to True.
        dataset_err = False
        if isinstance(dataset_names_list, str):
            multi_dataset = False
        elif isinstance(dataset_names_list, Iterable):
            l_isstr = [isinstance(dst, str) for dst in dataset_names_list]
            if all(l_isstr):
                multi_dataset = True
            else:
                dataset_err = True
        else:
            dataset_err = True
        if dataset_err:
            raise ValueError("dataset_names_list should be string or list of strings.")
        return multi_dataset

    def _check_inst_cat(self, inst_cats_list):
        # Check the content of inst_cat: If string set multi_dataset to False, otherwise to True.
        instcat_err = False
        if isinstance(inst_cats_list, str):
            multi_outputs = False
        elif isinstance(inst_cats_list, Iterable):
            l_isstr = [isinstance(instcat, str) for instcat in inst_cats_list]
            if all(l_isstr):
                multi_outputs = True
            else:
                instcat_err = True
        else:
            instcat_err = True
        if instcat_err:
            raise ValueError("inst_cats should be a string or a list of strings.")
        return multi_outputs

    def _init_output_info(self, multi_outputs, inst_cats_list, multi_inst_model, inst_model_fullnames_list,
                          multi_dataset, dataset_names_list):
        # Fill output_info giving the instrument category, the instrument model full name and the
        # dataset name for each ouput of the datasimulator function.
        if multi_outputs:
            noutput = len(inst_cats_list)
            l_instcat = list(inst_cats_list)
            if multi_inst_model:
                if len(inst_model_fullnames_list) != noutput:
                    raise ValueError("inst_model_fullnames should have the same length as inst_cats"
                                     " or a string (meaning that all the ouputs have the same "
                                     "instrument model).")
                else:
                    l_instmod = list(inst_model_fullnames_list)
            else:
                l_instmod = [inst_model_fullnames_list for ii in range(noutput)]
            if multi_dataset:
                if len(dataset_names_list) != noutput:
                    raise ValueError("datasets should have the same length as inst_cats or a string"
                                     " (meaning that all the ouputs have the same dataset).")
                else:
                    l_dataset = list(dataset_names_list)
            else:
                l_dataset = [dataset_names_list for ii in range(noutput)]
        else:
            if multi_inst_model or multi_dataset:
                raise ValueError("You can't provide multiple datasets or instrument models if there"
                                 "only one output (len(inst_cats) = 1)")
            else:
                l_instcat = [inst_cats_list]
                l_instmod = [inst_model_fullnames_list]
                l_dataset = [dataset_names_list]
        self.__output_info = DataFrame({instcat_key: l_instcat, instmodfullname_key: l_instmod,
                                        dtst_key: l_dataset})

    @property
    def param_model_vect_name(self):
        """Return the string of the parameter vector of the model (datasimulator)."""
        return self.__param_model_vect_name

    @property
    def include_dataset_kwarg(self):
        """If True the function include the dataset(s) kwarg(s) already."""
        return self.__include_dataset_kwarg

    @property
    def multi_dataset(self):
        """If True the datasim function simulates several datasets."""
        return self.__multi_dataset

    @property
    def multi_inst_model(self):
        """If True the datasim function simulates several instrument models."""
        return self.__multi_inst_model

    @property
    def noutput(self):
        """Return the number of outputs of the DatasimDocFunc."""
        return len(self.__output_info.index)

    @property
    def multi_output(self):
        """If True the output of the datasim function is a list of array, that (can) simulates several outputs."""
        if self.forced_multioutput:
            return True
        else:
            return self.noutput > 1

    @property
    def output_info(self):
        """Return a table with the instrument category, model and datasets used for the outputs."""
        return self.__output_info

    @property
    def inst_cats_list(self):
        """Return the Serie of instrument category used for the ouputs."""
        return list(self.output_info[instcat_key].values)

    @property
    def inst_model_fullnames_list(self):
        """Return the Series of instrument model full names used for the ouputs."""
        return list(self.output_info[instmodfullname_key].values)

    @property
    def dataset_names_list(self):
        """Return the Serie of dataset names used for the ouputs."""
        return list(self.output_info[dtst_key].values)

    @property
    def param_model_names_list(self):
        """Return the ordered list of model parameters name of the function."""
        return self.__param_model_names_list

    @property
    def _info(self):
        """String with information about the function."""
        text = super(DatasimDocFunc, self)._info
        return text + "\noutput_info:\n {output_info}".format(output_info=self.output_info)

    @property
    def forced_multioutput(self):
        """True if the output is a list even if it's a one element list"""
        return self.__forced_multioutput

    def info(self):
        """Provide informations about the function."""
        print(self._info)
