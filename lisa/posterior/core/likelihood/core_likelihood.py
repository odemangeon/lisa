#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
likelihood module.

The objective of this module is to define the class LikelihoodCreator.

@DONE:
    -

@TODO:
    -
"""
from logging import getLogger
from collections import defaultdict  # , OrderedDict
# import numpy as np
# from copy import deepcopy

from .manager_noise_model import Manager_NoiseModel
from .likelihood_docfunc import LikelihoodDocFunc, noisemod_key
from ..model.datasim_docfunc import instmodfullname_key
from ..database_func import DatabaseInstLvlDataset
# from ....tools.function_w_doc import DocFunction
# from ..model.datasim_docfunc import instmodfullname_key, dtst_key
# from ....tools.miscellaneous import interpret_data_filename


## logger object
logger = getLogger()

mgr_noisemodel = Manager_NoiseModel()
mgr_noisemodel.load_setup()

## Keys of the dico_noisemodel dict for the LikelihoodCreator.__likelihood_creator and
## LikelihoodCreator._create_lnlikelihood methods
key_noisemod_likefunc = "lnlike"
key_lparnoisemod = "idx_param_noisemod"
key_dtst = "datasets"
key_idxsim = "idx_simdata"
key_dtkwarg = "datakwargs"


class LikelihoodCreator(object):
    """LikelihoodCreator is an Interface class for Core_Model.

    It provides methods to create likelihood functions for a model.
    """

    def __likelihood_creator(self, datasim, l_idx_param_dtsim, dico_noisemodel,
                             include_dataset=True):
        """Create the lnlikelihood function.

        This function "only" assemble the likelihood function from the datasimulator function and
        the "raw" lnlikelihood functions built from the noise models associated to the datasim
        function and provided in the dico_noisemodel argument.

        :param DatasimDocFunc datasim: Datasimulator doc function, the ouput of this is the
            simulated data called sim_data which can be a 2 dimensional array if the datasim
            simulates multiple dataset and/or instrument models.
        :param list_of_int l_idx_param_dtsim: List of indexes giving the indexes of the datasim
            parameters in the full list of model parameters.
        :param dict dico_noisemodel: Dictionary giving the required inputs for each noise model.
            key = noise model name, value = dictionary:
                key= "lnlike", value: lnlike function for this noise model. This function take as
                    arguments the modeled data, the parameters for the noise model, and eventually
                    the dataset kwargs necessary for the noise model.
                key= "idx_param_noisemod", value: list of indexes corresponding to the noise model
                    parameters in the parameter vector
                key= "datasets", value: dictionary:
                    key= "idx_simdata", value: list of int giving the indexes of dataset affected by
                        the noise model in the simulated data list (sim_data)
                    key= "datakwargs", value: list of dataset_kwargs (dict: key=datakwarg type, eg.
                        "t" for time; value= datakwarg of this type for the corresponding dataset
                        simulated at the corresponding index of sim_data
        :param bool include_dataset: If True the output ln likelihood function will include
            the dataset kwargs, otherwise not. This argument is only used if the
            datasim doc function provided in argument does not included the dataset kwargs.
            Otherwise it is ignored and the dataset are automatically included in the output
            likelihood, that adds the noise model contribution, because it would not make sense to
            include them in the simulated data but not in the noise model.
        :return function lnlike: ln likelihood function. This function can have different set of
            arguments. If the datasim doc function provided in argument does include the dataset
            kwargs, then it takes as arguments only the parameters vector (including the datasim
            parameter and the noise models parameters). Otherwise the datasim doc function provided
            in argument does NOT include the dataset kwargs and in this case if the include_dataset
            argument is True the output lnlike function will include them and take only the
            parameters vector as argument. If the include_dataset argument is False the lnlike
            function will take as arguments the parameters vector and the dataset kwargs.
        """
        datasim_func = datasim.function
        dataset_included_in_datasim = datasim.include_dataset_kwarg

        if dataset_included_in_datasim:
            if not(include_dataset):
                logger.warning("Include_dataset is False but the datasim doc function provided in "
                               "argument includes already the dataset kwargs. Include_dataset=False"
                               "is thus ignored.")

            if datasim.multi_output:
                def lnlike(p, *arg, **kwargs):
                    sim_data = datasim_func(p[l_idx_param_dtsim], *arg, **kwargs)
                    res = 0
                    for noisemod_name in dico_noisemodel:
                        res += (dico_noisemodel[noisemod_name][key_noisemod_likefunc]
                                ([sim_data[ii] for ii in
                                  dico_noisemodel[noisemod_name][key_dtst][key_idxsim]],
                                 p[dico_noisemodel[noisemod_name][key_lparnoisemod]],
                                 dico_noisemodel[noisemod_name][key_dtst][key_dtkwarg]))
                    return res
            else:
                noisemod_name = list(dico_noisemodel.keys())[0]
                noisemod_dict = dico_noisemodel[noisemod_name]

                def lnlike(p, *arg, **kwargs):
                    sim_data = datasim_func(p[l_idx_param_dtsim], *arg, **kwargs)
                    return noisemod_dict[key_noisemod_likefunc]([sim_data], p[noisemod_dict[key_lparnoisemod]],
                                                                noisemod_dict[key_dtst][key_dtkwarg])
        else:
            raise NotImplementedError("For now, __likelihood_creator cannot be applied to a data "
                                      "simulator for which the dataset is not included")

        return lnlike

    def _create_lnlikelihood(self, datasim):
        """Return the log likelihood doc function corresponding to a datasim doc function.

        This function prepares the inputs for __likelihood_creator function and then use it.
        These inputs included the noise_model ln likelihood function, the indexes of the parameters
        of the noise model (if any) and the dataset information required by the noise model.
        __likelihood_creator just assembles all these to create the full ln likelihood.

        :param DatasimDocFunc datasim: DatasimDocFunc specifying the data type (instrument category)
            and at least instrument model you want to get the likelyhood function of. The datasim
            function thus need to specify all the instrument models for the function to be able to
            infer the noise models to use.
        :return LikelihoodDocFunc lnlike: LikelihoodDocFunc giving the lnlikelihood asssociated to
            the datasim DatasimDocFunc provided as argument. If the datasim function provided in
            argument includes the datasets then the lnlikelihood function will also include them.
            Otherwise not
        """
        if not(datasim.include_dataset_kwarg):
            raise NotImplementedError("For now _create_lnlikelihood doesn't handle datasim function"
                                      "which do not include the dataset kwargs.")

        # Construct the input dictionnary, dico_noisemodel for the __likelihood_creator function:
        # See description of this dictionary in the docstring of __likelihood_creator
        # Define a function for defaultdict class to match the structure for dico_noisemodel
        def defdic_func():
            return {key_noisemod_likefunc: None, key_lparnoisemod: [],
                    key_dtst: {key_idxsim: [],
                               key_dtkwarg: []
                               }
                    }

        dico_noisemodel = defaultdict(defdic_func)

        # Get the list of instrument model objects from the list of instrument model full name in
        # the datasim function and the list of dataset object from the list of datasets in the
        # datasim function
        l_instmod = []
        l_dataset = []
        for ii in range(datasim.noutput):
            if datasim.instmodel_fullname[ii] is None:
                raise ValueError("To create a likelihood your datasim function cannot have an "
                                 "output that is not associated with an instrument model, because "
                                 "the instrument model give the noise model to use.")
            l_instmod.append(self.instruments[datasim.instmodel_fullname[ii]])
            if datasim.dataset[ii] is None:
                l_dataset.append(None)
            else:
                l_dataset.append(self.dataset_db[datasim.dataset[ii]])
            #     raise ValueError("For now to create a likelihood your datasim function cannot "
            #                      "have an output that is not associated with a dataset.")

        # Initialise instmod4noisemod dictionary giving the the list of instrument model object for
        # each noise model: key = noise model name, value: list of instrument model objects.
        instmod4noisemod = defaultdict(list)

        # Initialise the output_info DataFrame for the LikelihoodDocFunc
        output_info_like = datasim.output_info.copy()
        output_info_like[noisemod_key] = None

        # For each instrument model and dataset in the lists produced above, ...
        for ii, instmod, dtst in zip(range(datasim.noutput), l_instmod, l_dataset):
            # ... Set the associate noise model name in output_info_like
            (output_info_like[noisemod_key]
             [output_info_like[instmodfullname_key] == instmod.get_name(include_prefix=True, recursive=True)]) = instmod.noise_model
            # ... add the index corresponding to these dataset and instmod in the output of the
            # datasim function output in the "datasets" and "idx_simdata" section of the
            # corresponding noise model in dico_noisemodel
            dico_noisemodel[instmod.noise_model][key_dtst][key_idxsim].append(ii)
            # ... add the dataset kwargs of the dataset in the "datasets" and "datakwargs" section
            # of the corresponding noise model in dico_noisemodel
            if dtst is None:
                dico_noisemodel[instmod.noise_model][key_dtst][key_dtkwarg].append(None)
            else:
                noise_model = mgr_noisemodel.get_noisemodel_subclass(instmod.noise_model)
                (dico_noisemodel[instmod.noise_model][key_dtst][key_dtkwarg].
                 append(noise_model.get_necessary_datakwargs(dtst)))
            # ... add the instrument model obj to the list of instrument mod for the noise model
            instmod4noisemod[instmod.noise_model].append(instmod)

        # Create the list of indexes for the datasim function in the full list of params of the lnlike
        # function
        params_likelihood = datasim.params_model.copy()
        l_idx_param_dtsim = range(len(params_likelihood))
        # For each noise model, ...
        for noisemod_name in instmod4noisemod:
            # ... get the noise model subclass
            noise_model = mgr_noisemodel.get_noisemodel_subclass(noisemod_name)
            # ... create the prefilled lnlike function thanks to the instruments model
            # object and the ndatasim_param and also the list of indexes for the noise model
            # parameters in the lnlike function parameter add them to dico_noisemodel
            (dico_noisemodel[noisemod_name][key_noisemod_likefunc],
             params_likelihood,
             dico_noisemodel[noisemod_name][key_lparnoisemod]
             ) = noise_model.get_prefilledlnlike(l_params=params_likelihood,
                                                 l_instmod_obj=instmod4noisemod[noisemod_name],
                                                 model_instance=self
                                                 )

        logger.debug("Creation of a likelihood for datasim function:\n {}\nList of the indexes for the datasim"
                     " function:\n{}\nAssociated dictionary of noise models:\n{}\nList of parameters"
                     "for the likelihood function:\n{}"
                     "".format(datasim._info, l_idx_param_dtsim, dico_noisemodel,
                               params_likelihood))

        return LikelihoodDocFunc(self.__likelihood_creator(datasim, l_idx_param_dtsim,
                                                           dico_noisemodel),
                                 params_model=params_likelihood,
                                 include_dataset_kwarg=datasim.include_dataset_kwarg,
                                 mand_kwargs=None, opt_kwargs=None,
                                 output_info=output_info_like)

    # TODO: Right now this function is not used, because I am not creating likelihoods without dataset
    # But actually, I think that _create_lnlikelihood might be able to do this case too (To Be Checked)
    def create_lnlikelihoods(self, datasim_inst_db,
                             affectinstmodel4dataset=False, lock_db=False, pickleable=False):
        """Return the likelihood for each instrument model used (without dataset harcoded).

        This function will create a lnlikelihood function for each datasimulator in datasim_inst_db.

        :param DatabaseInstLvlDataset datasim_inst_db: DatabaseInstLvlDataset which gives the
            datasim doc function for each instrument model used and each component in the object
            studied.
        :param bool affectinstmodel4dataset: True if you want to copy the instmodel4dataset of the
            model into the one of the output database.
        :param bool lock_db: True if you want to lock the output database before returning it
        :param bool pickleable: Use the pickleable function.
        :return DatabaseInstLvlDataset db_lnlike: Database containing the datasimulator docfuncs for
            each instrument model used. There is several datasim for each instrument model, because
            there might be several components (e.g. several planets) in the object studied. But
            there is always an entry which correspond to the whole object whose key is
            self.key_whole.
            Structure is: 1st = inst_cat, 2nd = inst_name, 3nd = inst_model, 4st = component
        """
        # Create the result databases (DatabaseInstLvlDataset)
        # If affectinstmodel4dataset=True, copy the instmodel4dataset of the model into the one of
        # this database.
        if affectinstmodel4dataset:
            instmodel4dataset = self.instmodel4dataset.copy()
        else:
            instmodel4dataset = None
        # Create the likelihood function database
        db_lnlike = DatabaseInstLvlDataset(object_stored="lnlikelihoods",
                                           database_name=self.object_name,
                                           instmodel4dataset=instmodel4dataset, ordered=False)
        # Unlock the database to be sure that you can modify it
        db_lnlike.database_unlock()
        # For each instrument category, ...
        for inst_cat in datasim_inst_db:
            # For each instrument name, ...
            for inst_name in datasim_inst_db[inst_cat]:
                # For each instrument model, ...
                for inst_model in datasim_inst_db[inst_cat][inst_name]:
                    # Init the 4th level (component) of db_lnlike
                    db_lnlike[inst_cat][inst_name][inst_model] = {}
                    # Get the instrument model instance
                    instmod_obj = self.instruments[inst_cat][inst_name][inst_model]
                    logger.info("Creating likelihoods for instrument model {}"
                                "".format(instmod_obj.get_name(include_prefix=True, recursive=True)))
                    # For each component in the model, ...
                    for obj in datasim_inst_db[inst_cat][inst_name][inst_model]:
                        logger.info("Creating likelihood for instrument model {} and obj {}"
                                    "".format(instmod_obj.get_name(include_prefix=True, recursive=True), obj))
                        # ... get the datasim doc func
                        datasim = datasim_inst_db[inst_cat][inst_name][inst_model][obj]
                        # ... create the likelihood function
                        (db_lnlike[inst_cat][inst_name][inst_model][obj]
                         ) = self._create_lnlikelihood(datasim=datasim)
        # If required lock the database
        if lock_db:
            db_lnlike.lock()
        return db_lnlike

    # def __lnlike_withdataset_creator(self, func, arg_list, data, data_err):
    #     arg_list_withdtset = deepcopy(arg_list)
    #     for kwar in ["data", "data_err"]:
    #         arg_list_withdtset["kwargs"].remove(kwar)
    #
    #     def lnlike_withdataset(p):
    #         # logger.debug("paramnames likewdst ({}): {}\nparams likewdst ({}): {}"
    #         #              "".format(len(arg_list["param"]), arg_list["param"], len(p), p))
    #         return func(p, data, data_err)
    #     return DocFunction(function=lnlike_withdataset, arg_list=arg_list_withdtset)

    # def __lnlike_withdataset_creator(self, func, arg_list, kwargs):
    #     def lnlike_withdataset(p):
    #         # logger.debug("paramnames likewdst ({}): {}\nparams likewdst ({}): {}"
    #         #              "".format(len(arg_list["param"]), arg_list["param"], len(p), p))
    #         return func(p, **kwargs)
    #     return DocFunction(function=lnlike_withdataset, arg_list=arg_list)

    def create_lnlikelihoods_perdataset(self, datasim_db_dtset):
        """Return a dictionnary giving the lnlikehood doc function for each dataset.

        :param dict datasim_db_dtset: Dictionnary giving the datasimulator doc function for each
            dataset. key = dataset full name, value = DatasimDocFunc for this dataset. These should
            include the dataset kwargs.
        :return dict db: Dictionary giving the lnlikehood doc function for each dataset.
            key = dataset full name, value = LikelihoodDocFunc for this dataset.
        """
        # Initialise the output dictionary
        db = {}

        # For each dataset_name and associated datasim in the datasim_db_dtset dictionnary, ...
        for dataset_name, datasim in datasim_db_dtset.items():
            # ..., datasim_db_dtset should contain a "all" entry. This entry requires a specific
            # treatment.
            # if dataset_name == "all":
            #     continue

            # ..., create the corresponding lnlikelihood doc function
            db[dataset_name] = self._create_lnlikelihood(datasim)
            # db[dataset_name] = self.__lnlike_withdataset_creator(lnlike_doc_func.function,
            #                                                      lnlike_doc_func.arg_list,
            #                                                      data=dataset.get_data(),
            #                                                      data_err=dataset.get_data_err())
        return db

    # Commented for test of initialisation with batman
    # def create_lnlikelihoods_perdataset(self, lnlike_db, dataset_db, instmodel4dataset):
    #     """Create the log likelihood function with the data hardcoded."""
    #     db = {}
    #     # l_func = []
    #     # l_params_idx = []
    #     # l_allparams = []
    #     l_params = []
    #     for dataset_name in instmodel4dataset:
    #         instmod_fullname = instmodel4dataset.get_instmod_fullname(dataset_name=dataset_name)
    #         lnlike_func = lnlike_db[instmod_fullname]["whole"].function
    #         arg_list = lnlike_db[instmod_fullname]["whole"].arg_list
    #         dataset = dataset_db[dataset_name]
    #         kwargs = dataset.get_kwargs()
    #         arg_list_new = OrderedDict()
    #         arg_list_new["param"] = arg_list["param"]
    #         l_params.append(arg_list["param"])
    #         arg_list_new["kwargs"] = []
    #
    #         # The creator is needed for enclosure on func, arg_list and kwargs and avoid issue
    #         # with the late binding enclosure
    #         # def lnlike_withdataset_creator(func, arg_list, kwargs):
    #         #     def lnlike_withdataset(p):
    #         #         # logger.debug("paramnames likewdst ({}): {}\nparams likewdst ({}): {}"
    #         #         #              "".format(len(arg_list["param"]), arg_list["param"], len(p),
    #         #         #                        p))
    #         #         return func(p, **kwargs)
    #         #     return DocFunction(function=lnlike_withdataset, arg_list=arg_list)
    #
    #         db[dataset_name] = self.__lnlike_withdataset_creator(func=lnlike_func,
    #                                                              arg_list=arg_list_new,
    #                                                              kwargs=kwargs)
    #         # db[dataset_name] = lnlike_withdataset_creator(func=lnlike_func,
    #         #                                               arg_list=arg_list_new,
    #         #                                               kwargs=kwargs)
    #
    #         # l_func.append(db[dataset_name])
    #         # idx_par = []
    #         # for par in arg_list_new["param"]:
    #         #     if par not in l_allparams:
    #         #         l_allparams.append(par)
    #         #     idx_par.append(l_allparams.index(par))
    #         # l_params_idx.append(idx_par)
    #
    #     # def lnlike_all(p):
    #     #     res = 0
    #     #     # logger.debug("paramnames like ({}): {}\nparams like ({}): {}"
    #     #     #              "".format(len(arg_list_all["param"]), arg_list_all["param"], len(p),
    #     #                              p))
    #     #     for func, param, idxs in zip(l_func, l_params, l_params_idx):
    #     #         # logger.debug("func: {}\nidxs ({}): {}\np[idxs] ({}): {}\nparams names ({}): "
    #     #         #              "{}".format(func, len(idxs), idxs, len(p[idxs]), p[idxs],
    #     #         #                        len(param), param))
    #     #         res += func(p[idxs])
    #     #     return res
    #
    #     # arg_list_all = OrderedDict()
    #     # arg_list_all["param"] = l_allparams
    #     # arg_list_all["kwargs"] = []
    #
    #     # db["all"] = DocFunction(function=lnlike_all, arg_list=arg_list_all)
    #     # db["all"] = self.create_lnlikelihoods_alldataset(datasim_db=datasim_db,
    #     #                                                  dataset_db=dataset_db,
    #     #                                                  instmodel4dataset=instmodel4dataset)
    #     return db

    # def __lnlike_withalldataset_creator(self, l_func, l_params_idx, arg_list, l_allkwargs=None):
    #
    #     def lnlike_all_wkwargs(p):
    #         res = 0
    #         # logger.debug("paramnames like ({}): {}\nparams like ({}): {}"
    #         #              "".format(len(arg_list_all["param"]), arg_list_all["param"],
    #         #                        len(p), p))
    #         for func, idxs, kwargs in zip(l_func, l_params_idx, l_allkwargs):
    #             # logger.debug("func: {}\nidxs ({}): {}\np[idxs] ({}): {}\nparams names ({}): "
    #             #              "{}".format(func, len(idxs), idxs, len(p[idxs]), p[idxs],
    #             #                        len(param), param))
    #             res += func(p[idxs], **kwargs)
    #         return res
    #
    #     def lnlike_all_wokwargs(p):
    #         res = 0
    #         # logger.debug("paramnames like ({}): {}\nparams like ({}): {}"
    #         #              "".format(len(arg_list_all["param"]), arg_list_all["param"],
    #         #                        len(p), p))
    #         for func, idxs in zip(l_func, l_params_idx):
    #             # logger.debug("func: {}\nidxs ({}): {}\np[idxs] ({}): {}\nparams names ({}): "
    #             #              "{}".format(func, len(idxs), idxs, len(p[idxs]), p[idxs],
    #             #                        len(param), param))
    #             res += func(p[idxs])
    #         return res
    #
    #     if l_allkwargs is None:
    #         return DocFunction(function=lnlike_all_wokwargs, arg_list=arg_list)
    #     else:
    #         return DocFunction(function=lnlike_all_wkwargs, arg_list=arg_list)

    # def create_lnlikelihood_alldataset(self, datasim_db_dtset, dataset_db, instmodel4dataset):
    #
    #     # Create a dict dico_noisemodel which for each noise model give the dataset names using
    #     # this noise model and their associated instrument models and datasimulators
    #     def dicts_factory():
    #         return deepcopy({"datasim_docfunc": OrderedDict(), "instmodel_obj": OrderedDict()})
    #
    #     dico_noisemodel = defaultdict(dicts_factory)
    #     for dataset_name in instmodel4dataset:
    #         instmod_fullname = instmodel4dataset.get_instmod_fullname(dataset_name=dataset_name)
    #         instmod_obj = self.instruments[instmod_fullname]
    #         noisemodel_name = instmod_obj.noise_model
    #         (dico_noisemodel[noisemodel_name]["datasim_docfunc"]
    #          [dataset_name]) = datasim_db_dtset[dataset_name]
    #         (dico_noisemodel[noisemodel_name]["instmodel_obj"]
    #          [dataset_name]) = instmod_obj
    #
    #     # Create and fill the list of likelihood function (one for each noise model)
    #     l_func = []
    #     # The list of list with the associated param indexes
    #     l_params_idx = []
    #     # The list of dictionnary giving the associated kwargs (data, data_err, ...)
    #     l_allkwargs = []
    #     # The list of all the parameters names (all noise model param in one list)
    #     l_allparams = []
    #     # Create and fill the dictionary giving the noise model instances for each dataset_name in
    #     # in the all datasets likelihood
    #     dico_noisemodel_instance = OrderedDict()
    #     # dico_params_idx_all = OrderedDict()
    #     for noise_model in dico_noisemodel:
    #         noisemodel_subclass = mgr_noisemodel.get_noisemodel_subclass(noise_model)  # Create a
    #         datasim_docfuncs = dico_noisemodel[noisemodel_name]["datasim_docfunc"]  # noise model
    #         instmodel_objs = dico_noisemodel[noisemodel_name]["instmodel_obj"]  # instance.
    #         noisemodel_instance = noisemodel_subclass(datasim_docfunc=datasim_docfuncs,
    #                                                   model_instance=self,
    #                                                   instmodel_obj=instmodel_objs)
    #         # Get the lnlike doc function
    #         # doc_func, dico_params_idx_all[noise_model] = noisemodel_instance.lnlike_creator()
    #         doc_func = noisemodel_instance.lnlike_creator()
    #         l_func.append(doc_func.function)
    #         all_kwargs = defaultdict(list)  # Get the kwargs (data, data_err, and the rest)
    #         for dataset_name in noisemodel_instance.l_dataset:
    #             dico_noisemodel_instance[dataset_name] = noisemodel_instance
    #             dataset = dataset_db[dataset_name]
    #             all_kwargs["data"].append(dataset.get_data())
    #             all_kwargs["data_err"].append(dataset.get_data_err())
    #             # kwargs = dataset.get_kwargs()
    #             # for karg_type, kwarg_value in kwargs.items():
    #             #     all_kwargs[karg_type].append(kwarg_value)
    #         l_allkwargs.append(all_kwargs)
    #         idx_par = []  # Get the l_params_idx
    #         for par in doc_func.arg_list["param"]:
    #             if par not in l_allparams:
    #                 l_allparams.append(par)
    #             idx_par.append(l_allparams.index(par))
    #         l_params_idx.append(idx_par)
    #         # for dataset in noisemodel_instance.l_dataset:
    #         #     dico_params_idx[noise_model]["dataset"] = l_p

    # def create_lnlikelihood_alldataset(self, datasim_db_dtset, dataset_db, instmodel4dataset):
    #
    #     # Create a dict dico_noisemodel which for each noise model give the datasimcreator
    #     # And then all the inst_mod_obj and dataset using this
    #     # noise model and this datasimcreator
    #     dico_noisemdl_datasim = defaultdict(dict)  # defaultdict(dicts_factory)
    #     for dataset_name in instmodel4dataset:
    #         instmod_fullname = instmodel4dataset.get_instmod_fullname(dataset_name=dataset_name)
    #         instmod_obj = self.instruments[instmod_fullname]
    #         datasimcreator_name = self.get_datasimcreatorname(instmod_obj.instrument.category)
    #         noisemodel_name = instmod_obj.noise_model
    #         if datasimcreator_name not in dico_noisemdl_datasim[noisemodel_name]:
    #             (dico_noisemdl_datasim[noisemodel_name]
    #              [datasimcreator_name]) = deepcopy({"inst_mod_obj": OrderedDict(),
    #                                                 "dataset": OrderedDict(),
    #                                                 "datasim": None})
    #         (dico_noisemdl_datasim[noisemodel_name][datasimcreator_name]["inst_mod_obj"]
    #          [instmod_fullname]) = instmod_obj
    #         (dico_noisemdl_datasim[noisemodel_name][datasimcreator_name]["dataset"]
    #          [dataset_name]) = dataset_db[dataset_name]
    #
    #     # Create the datasim functions of each noise model
    #     for noise_mdl in dico_noisemdl_datasim:
    #         for datasimcreator_name in dico_noisemdl_datasim[noise_mdl]:
    #             dic = dico_noisemdl_datasim[noise_mdl][datasimcreator_name]
    #             datasets = []
    #             for dst in dic["dataset"]:
    #                 datasets.append(dic["dataset"][dst])
    #             inst_models = []
    #             for instmdl in dic["inst_mod_obj"]:
    #                 inst_models.append(dic["inst_mod_obj"][instmdl])
    #             dic["datasim"] = self._create_datasimulator(inst_models, datasets)
    #
    #     # Create and fill the list of likelihood function (one for each noise model)
    #     l_func = []
    #     # The list of list with the associated param indexes
    #     l_params_idx = []
    #     # The list of dictionnary giving the associated kwargs (data, data_err, ...)
    #     l_allkwargs = []
    #     # The list of all the parameters names (all noise model param in one list)
    #     l_allparams = []
    #     # Create and fill the dictionary giving the noise model instances for each dataset_name in
    #     # in the all datasets likelihood
    #     dico_noisemodel_instance = OrderedDict()
    #     # dico_params_idx_all = OrderedDict()
    #     for noise_model in dico_noisemdl_datasim:
    #         dic = dico_noisemdl_datasim[noise_model]
    #         noisemodel_subclass = mgr_noisemodel.get_noisemodel_subclass(noise_model)  # Create a
    #         datasim_docfuncs = OrderedDict()
    #         for datasimcreator_name in dic:
    #             datasim_docfuncs[datasimcreator_name] = dic[datasimcreator_name]["datasim"]
    #         instmodel_objs = OrderedDict()
    #         for datasimcreator_name in dic:
    #             instmodel_objs[datasimcreator_name] = []
    #             for instmdl in dic[datasimcreator_name]["inst_mod_obj"]:
    #                 (instmodel_objs[datasimcreator_name].
    #                  append(dic[datasimcreator_name]["inst_mod_obj"][instmdl]))
    #         noisemodel_instance = noisemodel_subclass(datasim_docfunc=datasim_docfuncs,
    #                                                   model_instance=self,
    #                                                   instmodel_obj=instmodel_objs)
    #         # Get the lnlike doc function
    #         # doc_func, dico_params_idx_all[noise_model] = noisemodel_instance.lnlike_creator()
    #         doc_func = noisemodel_instance.lnlike_creator()
    #         l_func.append(doc_func.function)
    #
    #         idx_par = []  # Get the l_params_idx
    #         for par in doc_func.arg_list["param"]:
    #             if par not in l_allparams:
    #                 l_allparams.append(par)
    #             idx_par.append(l_allparams.index(par))
    #         l_params_idx.append(idx_par)
    #
    #     arg_list_all = OrderedDict()
    #     arg_list_all["param"] = l_allparams
    #     arg_list_all["kwargs"] = []
    #     doc_f = self.__lnlike_withalldataset_creator(l_func=l_func, l_params_idx=l_params_idx,
    #                                                  l_allkwargs=l_allkwargs,
    #                                                  arg_list=arg_list_all)
    #     return doc_f, dico_noisemodel_instance  # , dico_params_idx_all

        # Then create the lnlike filling the kwargs and final sum them

    # def create_lnlikelihood_alldataset(self, datasim_db, dataset_db, instmodel4dataset):
    #
    #     # Create a dict dico_noisemodel which for each noise model give the dataset_name using
    #     # this noise model and the associated instrument model and datasimulator
    #     def dicts_factory():
    #         return deepcopy({"datasim_docfunc": OrderedDict(), "instmodel_obj": OrderedDict()})
    #
    #     dico_noisemodel = defaultdict(dicts_factory)
    #     for dataset_name in instmodel4dataset:
    #         instmod_fullname = instmodel4dataset.get_instmod_fullname(dataset_name=dataset_name)
    #         instmod_obj = self.instruments[instmod_fullname]
    #         noisemodel_name = instmod_obj.noise_model
    #         # dico_noisemodel[noisemodel_name]["datasim_docfunc"]
    #         (dico_noisemodel[noisemodel_name]["datasim_docfunc"]
    #          [dataset_name]) = datasim_db[instmod_fullname]["whole"]
    #         (dico_noisemodel[noisemodel_name]["instmodel_obj"]
    #          [dataset_name]) = instmod_obj
    #
    #     # Create and fill the list of likelihood function (one for each noise model)
    #     l_func = []
    #     # The list of list with the associated param indexes
    #     l_params_idx = []
    #     # The list of dictionnary giving the associated kwargs (data, data_err, ...)
    #     l_allkwargs = []
    #     # The list of all the parameters names (all noise model param in one list)
    #     l_allparams = []
    #     # Create and fill the dictionary giving the noise model instances for each dataset_name in
    #     # in the all datasets likelihood
    #     dico_noisemodel_instance = OrderedDict()
    #     # dico_params_idx_all = OrderedDict()
    #     for noise_model in dico_noisemodel:
    #         noisemodel_subclass = mgr_noisemodel.get_noisemodel_subclass(noise_model)  # Create a
    #         datasim_docfuncs = dico_noisemodel[noisemodel_name]["datasim_docfunc"]  # noise model
    #         instmodel_objs = dico_noisemodel[noisemodel_name]["instmodel_obj"]  # instance.
    #         noisemodel_instance = noisemodel_subclass(datasim_docfunc=datasim_docfuncs,
    #                                                   model_instance=self,
    #                                                   instmodel_obj=instmodel_objs)
    #         # Get the lnlike doc function
    #         # doc_func, dico_params_idx_all[noise_model] = noisemodel_instance.lnlike_creator()
    #         doc_func = noisemodel_instance.lnlike_creator()
    #         l_func.append(doc_func.function)
    #         all_kwargs = defaultdict(list)  # Get the kwargs (data, data_err, and the rest)
    #         for dataset_name in noisemodel_instance.l_dataset:
    #             dico_noisemodel_instance[dataset_name] = noisemodel_instance
    #             dataset = dataset_db[dataset_name]
    #             kwargs = dataset.get_kwargs()
    #             for karg_type, kwarg_value in kwargs.items():
    #                 all_kwargs[karg_type].append(kwarg_value)
    #         l_allkwargs.append(all_kwargs)
    #         idx_par = []  # Get the l_params_idx
    #         for par in doc_func.arg_list["param"]:
    #             if par not in l_allparams:
    #                 l_allparams.append(par)
    #             idx_par.append(l_allparams.index(par))
    #         l_params_idx.append(idx_par)
    #         # for dataset in noisemodel_instance.l_dataset:
    #         #     dico_params_idx[noise_model]["dataset"] = l_p
    #
    #     # def lnlike_withalldataset_creator(l_func, l_params_idx, l_allkwargs, arg_list):
    #     #     def lnlike_all(p):
    #     #         res = 0
    #     #         # logger.debug("paramnames like ({}): {}\nparams like ({}): {}"
    #     #         #              "".format(len(arg_list_all["param"]), arg_list_all["param"],
    #     #         #                        len(p), p))
    #     #         for func, idxs, kwargs in zip(l_func, l_params_idx, l_allkwargs):
    #     #             # logger.debug("func: {}\nidxs ({}): {}\np[idxs] ({}): {}\nparams names "
    #     #             #              "({}): {}".format(func, len(idxs), idxs, len(p[idxs]),
    #     #             #                                p[idxs], len(param), param))
    #     #             res += func(p[idxs], **kwargs)
    #     #         return res
    #     #
    #     #     return DocFunction(function=lnlike_all, arg_list=arg_list)
    #
    #     arg_list_all = OrderedDict()
    #     arg_list_all["param"] = l_allparams
    #     arg_list_all["kwargs"] = []
    #     doc_f = self.__lnlike_withalldataset_creator(l_func=l_func, l_params_idx=l_params_idx,
    #                                                  l_allkwargs=l_allkwargs,
    #                                                  arg_list=arg_list_all)
    #     return doc_f, dico_noisemodel_instance  # , dico_params_idx_all
    #
    #     # Then create the lnlike filling the kwargs and final sum them
