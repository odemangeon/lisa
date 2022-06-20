#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
likelihood documented function module.
"""

from .model.datasim_docfunc import DatasimDocFunc

## String used for the noise model column in ouput_info of LikelihoodDocFunc
noisemod_key = "noise_model"


class LikelihoodPosteriorDocFunc(DatasimDocFunc):
    """docstring for LikelihoodPosteriorDocFunc."""

    def __init__(self, function, param_model_names_list, params_model_vect_name, inst_cats_list, inst_model_fullnames_list,
                 dataset_names_list, noisemodel_names_list,
                 include_dataset_kwarg, mand_kwargs_list=None, opt_kwargs_dict=None):
        """Initialise the likelihood doc function.

        Arguments
        ---------
        function                    : function object
            function of the likelihood
        param_model_names_list      : list of str
            List of the name of the model parameters as they should be provided to the function in the
            first argument
        params_model_vect_name      : str
            Name of the argument used for the model parameter vector
        inst_cats_list              : Iterable
            Iterable giving the ordered list of the outputs instrument categories.
            It has to match both inst_model_fullnames_list and dataset_names_list
        inst_model_fullnames_list   : Iterable_of_string/string
            If string, the likelihood simulate only one instrument model and this is its full
            name.
            If Iterable, give the list of full names of the instrument models simulated.
            This list will be matched to dataset_names_list and inst_cats_list and noisemodel_names_list.
        dataset_names_list          : Iterable_of_string/string
            If string, the likelihood simulate only one dataset and this is its name
            If Iterable, give the list of names of the datasets simualted. This list will be matched
            to inst_model_fullnames_list and inst_cats_list and noisemodel_names_list.
        noisemodel_names_list       : Iterable_of_string/string
            If string, the likelihood simulate only one dataset/instrument model and this is the name
            of the noise model associated.
            If Iterable, give the list of names of the noise models. This list will be matched
            to inst_model_fullnames_list and inst_cats_list and dataset_names_list.
        include_dataset_kwarg       : bool
            Boolean saying if the function include the dataset(s) keyword arguments.
        mand_kwargs_list            : List of str
            List of the names of the mandatory arguments besides the name of the model parameter vector
            (like the time vector or a time reference) which should be given to function after the
             model parameter vector.
        opt_kwargs_dict             : dict
            Dictionary whose keys are the name of the optional arguments of the function and the values
            are the default values for these arguments
        """
        super(LikelihoodPosteriorDocFunc, self).__init__(function=function, param_model_names_list=param_model_names_list,
                                                         params_model_vect_name=params_model_vect_name, inst_cats_list=inst_cats_list,
                                                         inst_model_fullnames_list=inst_model_fullnames_list,
                                                         dataset_names_list=dataset_names_list, include_dataset_kwarg=include_dataset_kwarg,
                                                         mand_kwargs_list=mand_kwargs_list, opt_kwargs_dict=opt_kwargs_dict)
        self.output_info[noisemod_key] = noisemodel_names_list

    @property
    def noisemodel_names_list(self):
        """Return the Serie of noise model names  used for the ouputs."""
        return self.output_info[noisemod_key]

    @property
    def noutput(self):
        """Return the number of outputs of the LikelihoodPosteriorDocFunc.

        For now Likelihood function cannot be multi_ouput
        """
        return 1
