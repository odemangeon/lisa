#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
likelihood documented function module.
"""

from ..model.datasim_docfunc import DatasimDocFunc, instcat_key, instmodfullname_key, dtst_key
from ....tools.function_w_doc import DocFunction

## String used for the noise model column in ouput_info of LikelihoodDocFunc
noisemod_key = "noise model"


class LikelihoodDocFunc(DatasimDocFunc, DocFunction):
    """docstring for LikelihoodDocFunc."""
    def __init__(self, function, params_model, dataset_kwargs=None, output_info=None):
        """Initialise the likelihood doc function.

        :param function function: function of the likelihood
        :param Iterable_of_string params_model: Iterable giving the ordered list of the model
            parameters as they should be provided to the function.
        :param string/None dataset_kwargs: String giving the way the dataset_kwargs (like the time
            vector or a time reference) should be given to function. If None it means that the
            dataset kwargs are already included in function and should not be provided.
        :param pandas.DataFrame output_info: Table which provide the instrument category, model,
            and noise models used for the output
        """
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
    def noutput(self):
        """Return the number of outputs of the LikelihoodDocFunc.

        For now Likelihood function cannot be multi_ouput
        """
        return 1

    @property
    def multi_output(self):
        """If True the datasim function simulates several outputs."""
        return self.__multi_output
