#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
likelihood documented function module.
"""

from ..model.datasim_docfunc import DatasimDocFunc
from ...tools.function_w_doc import DocFunction


class LikelihoodDocFunc(DatasimDocFunc, DocFunction):
    """docstring for LikelihoodDocFunc."""
    def __init__(self, function, params_model, dataset_kwargs=None, output_info=None):
        # Initialise the params_model property
        self._init_params_model(params_model)

        # Get the arg_list input for DocFunction and initialise the include_dataset_kwarg property
        arg_list = self._init_arg_list_and_include_dataset_kwarg(params_model, dataset_kwargs)

        # Intialise output_info property
        self.__output_info = output_info

        # For now Likelihood function cannot be multi_ouput
        self.__multi_output = False

        DocFunction.__init__(self, function=function, arg_list=arg_list)

    def _init_params(self, params):
        self.__params = params

    @property
    def output_info(self):
        """Return a table with the instrument category, model and datasets used."""
        return self.__output_info

    @property
    def multi_output(self):
        """If True the datasim function simulates several outputs."""
        return self.__multi_output
