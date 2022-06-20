#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
datasimulator documented function module.
"""
from pandas import DataFrame
from collections import Iterable

from ....tools.function_w_doc import DocFunction


class PriorDocFunc(DocFunction):
    """docstring for DatasimDocFunc."""

    def __init__(self, function, param_prior_names_list, params_prior_vect_name,
                 mand_kwargs_list=None, opt_kwargs_dict=None):
        """Initialise the datasim doc function.

        Arguments
        ---------
        function                    : function object
            function of the datasimulator
        param_prior_names_list      : list of str
            List of the name of the prior parameters as they should be provided to the function in the
            first argument
        params_prior_vect_name      : str
            Name of the argument used for the prior parameter vector
        mand_kwargs_list            : List of str
            List of the names of the mandatory arguments besides the name of the model parameter vector
            (like the time vector or a time reference) which should be given to function after the
             model parameter vector.
        opt_kwargs_dict             : dict
            Dictionary whose keys are the name of the optional arguments of the function and the values
            are the default values for these arguments
        """
        # Set param_model_list
        self.__param_model_names_list = list(param_prior_names_list)

        # add params_model_vect_name at the beginning of the mandatory keyword argument list
        if mand_kwargs_list is None:
            mand_kwargs_list = [params_prior_vect_name, ]
        else:
            mand_kwargs_list = [params_prior_vect_name, ] + mand_kwargs_list

        super(PriorDocFunc, self).__init__(function=function, mand_kwargs_list=mand_kwargs_list, opt_kwargs_dict=opt_kwargs_dict)

    @property
    def param_model_names_list(self):
        """Return the ordered list of model parameters name of the function."""
        return self.__param_model_names_list
