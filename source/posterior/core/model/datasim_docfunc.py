#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
datasimulator documented function module.
"""
from ....tools.function_w_doc import DocFunction


class DatasimDocFunc(DocFunction):
    """docstring for DatasimDocFunc."""

    _instmod_key = "inst_model_fullnames"
    _dtst_key = "datasets"

    def __init__(self, function, params_model, dataset_kwargs=None,
                 inst_model_fullnames=None, datasets=None):
        """Initialise the datasim doc function.

        :param function function: function of the datasimulator
        :param list_of_string params_model: List giving the ordered list of the model parameters
            as they should be provided to the function.
        :param string/None dataset_kwargs: String giving the way the dataset_kwargs (like the time
            vector or a time reference) should be given to function. If None it means that the
            dataset kwargs are already included in function and should not be provided.
        :param list/string/None inst_model_fullnames:
            If None, the datasimulator doesn't include instrumental effect
            If string, the datasimulator simulate only one instrument model and this is its full
                name
            If list, give the list of full names of the instrument models simulated (some might be
                None). This list will be matched to the list of datasets if provided.
        :param list/string/None datasets:
            If None, the datasimulator doesn't include dataset kwargs
            If string, the datasimulator simulate only one dataset and this is its name
            If list, give the list of names of the datasets simualted. This list will be matched to
                the list of inst_model_fullnames if provided.
        """
        # Check the content of dataset_kwargs: If provided set include_dataset_kwarg to False,
        # otherwise to True. Also define the arg_list parameter for __init__ method of DocFunction
        if dataset_kwargs is None:
            self.__include_dataset_kwarg = True
            arg_list = str(params_model)
        else:
            self.__include_dataset_kwarg = False
            arg_list = str(params_model) + dataset_kwargs

        # Initialise the params_model property
        self.__params_models = params_model

        # Check the content of inst_model_fullnames: If not provided or string set multi_inst_model
        # to False, otherwise to True.
        instmod_err = False
        if inst_model_fullnames is None or isinstance(inst_model_fullnames, str):
            self.__multi_inst_model = False
        elif isinstance(inst_model_fullnames, list):
            if isinstance(inst_model_fullnames[0], str):
                self.__multi_inst_model = True
            else:
                instmod_err = True
        else:
            instmod_err = True
        if instmod_err:
            raise ValueError("inst_model_fullnames should be None, string or list of strings.")

        # Check the content of datasets: If not provided or string set multi_dataset
        # to False, otherwise to True.
        dataset_err = False
        if datasets is None or isinstance(datasets, str):
            self.__multi_dataset = False
        elif isinstance(datasets, list):
            if isinstance(datasets[0], str):
                self.__multi_dataset = True
            else:
                dataset_err = True
        else:
            dataset_err = True
        if dataset_err:
            raise ValueError("datasets should be None, string or list of strings.")

        # Initialise inst_dataset_dic: dict with key = instrument model full name or "woinst" if no
        # instrument model, value = list of dataset names for this instrument model
        self.__inst_dataset_dic = {}
        if self.multi_inst_model != self.multi_dataset:
            if self.multi_dataset:
                self.__inst_dataset_dic[self._dtst_key] = datasets
                self.__inst_dataset_dic[self._instmod_key] = [inst_model_fullnames
                                                              for dtst in datasets]
            else:  # self.multi_inst_model
                self.__inst_dataset_dic[self._instmod_key] = inst_model_fullnames
                self.__inst_dataset_dic[self._dtst_key] = [datasets
                                                           for inst in inst_model_fullnames]
        else:
            # Check that if multi_inst_model and multi_dataset, datasets and inst_model_fullnames
            # have the same length
            if self.multi_inst_model:  # self.multi_inst_model and self.multi_dataset
                if len(inst_model_fullnames) != len(datasets):
                    raise ValueError("If inst_model_fullnames and datasets are lists they must have"
                                     "the same length.")
            self.__inst_dataset_dic[self._dtst_key] = datasets
            self.__inst_dataset_dic[self._instmod_key] = inst_model_fullnames
        super(DatasimDocFunc, self).__init__(function=function, arg_list=arg_list)

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
    def inst_dataset_dic(self):
        """Return a dictionary giving the instrument model and datasets used for the outputs."""
        return self.__inst_dataset_dic

    @property
    def instmodel_fullnames(self):
        """Return the ordered list of instrument model full names used for the ouputs."""
        return self.inst_dataset_dic[self._instmod_key]

    @property
    def datasets(self):
        """Return the ordered list of dataset names used for the ouputs."""
        return self.inst_dataset_dic[self._dtst_key]

    @property
    def params_model(self):
        """Return the ordered list of model of the function."""
        return self.__params_models
