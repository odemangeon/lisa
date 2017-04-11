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
from collections import OrderedDict, defaultdict
from copy import deepcopy


from .manager_noise_model import Manager_NoiseModel
from ..database_func import DatabaseInstLvlDataset
from ....tools.function_w_doc import DocFunction
# from ....tools.miscellaneous import interpret_data_filename


## logger object
logger = getLogger()

mgr_noisemodel = Manager_NoiseModel()
mgr_noisemodel.load_setup()


class LikelihoodCreator(object):
    """docstring for LikelihoodCreator."""

    def _create_lnlikelihood(self, datasim_docfunc, inst_model_obj, pickleable=False):
                            # **kwarg_data):
        """Return the log likelihood function."""
        noise_model_subclass = mgr_noisemodel.get_noisemodel_subclass(inst_model_obj.noise_model)
        noise_model_instance = noise_model_subclass(datasim_docfunc=datasim_docfunc,
                                                    model_instance=self,
                                                    instmodel_obj=inst_model_obj)
        if pickleable:
            return DocFunction(function=noise_model_instance.lnlike,
                               arg_list=noise_model_instance.arg_list)
        else:
            # docf, _ = noise_model_instance.lnlike_creator()
            return noise_model_instance.lnlike_creator()

    def create_lnlikelihoods(self, datasim_db,
                             affectinstmodel4dataset=False, lock_db=False, pickleable=False):
        """Return the likelihood for each instrument model used.

        datasim_db : DatabaseInstLvlDataset or DatabaseInstLevel instance
        """
        if affectinstmodel4dataset:
            instmodel4dataset = self.instmodel4dataset.copy()
        else:
            instmodel4dataset = None
        db = DatabaseInstLvlDataset(object_stored="lnlikelihoods", database_name=self.object_name,
                                    instmodel4dataset=instmodel4dataset, ordered=False)
        db.database_unlock()
        # Create the instrument_db entries
        for inst_cat in datasim_db:
            for inst_name in datasim_db[inst_cat]:
                for inst_model in datasim_db[inst_cat][inst_name]:
                    db[inst_cat][inst_name][inst_model] = {}
                    instmod_obj = self.instruments[inst_cat][inst_name][inst_model]
                    logger.info("Creating likelihoods for instrument model {}"
                                "".format(instmod_obj.full_name))
                    for obj in datasim_db[inst_cat][inst_name][inst_model]:
                        logger.info("Creating likelihood for instrument model {} and obj {}"
                                    "".format(instmod_obj.full_name, obj))
                        datasim = datasim_db[inst_cat][inst_name][inst_model][obj]
                        (db[inst_cat][inst_name][inst_model][obj]
                         ) = self._create_lnlikelihood(datasim_docfunc=datasim,
                                                       inst_model_obj=instmod_obj,
                                                       pickleable=pickleable)
        if lock_db:
            db.lock()
        return db

    def create_lnlikelihoods_perdataset(self, lnlike_db, dataset_db, instmodel4dataset):
        """Create the log likelihood function with the data hardcoded."""
        db = {}
        # l_func = []
        # l_params_idx = []
        # l_allparams = []
        l_params = []
        for dataset_name in instmodel4dataset:
            instmod_fullname = instmodel4dataset.get_instmod_fullname(dataset_name=dataset_name)
            lnlike_func = lnlike_db[instmod_fullname]["whole"].function
            arg_list = lnlike_db[instmod_fullname]["whole"].arg_list
            dataset = dataset_db[dataset_name]
            kwargs = dataset.get_kwargs()
            arg_list_new = OrderedDict()
            arg_list_new["param"] = arg_list["param"]
            l_params.append(arg_list["param"])
            arg_list_new["kwargs"] = []

            # The creator is needed for enclosure on func, arg_list and kwargs and avoid issue with
            # the late binding enclosure
            def lnlike_withdataset_creator(func, arg_list, kwargs):
                def lnlike_withdataset(p):
                    # logger.debug("paramnames likewdst ({}): {}\nparams likewdst ({}): {}"
                    #              "".format(len(arg_list["param"]), arg_list["param"], len(p), p))
                    return func(p, **kwargs)
                return DocFunction(function=lnlike_withdataset, arg_list=arg_list)

            db[dataset_name] = lnlike_withdataset_creator(func=lnlike_func, arg_list=arg_list_new,
                                                          kwargs=kwargs)

            # l_func.append(db[dataset_name])
            # idx_par = []
            # for par in arg_list_new["param"]:
            #     if par not in l_allparams:
            #         l_allparams.append(par)
            #     idx_par.append(l_allparams.index(par))
            # l_params_idx.append(idx_par)

        # def lnlike_all(p):
        #     res = 0
        #     # logger.debug("paramnames like ({}): {}\nparams like ({}): {}"
        #     #              "".format(len(arg_list_all["param"]), arg_list_all["param"], len(p),
        #                              p))
        #     for func, param, idxs in zip(l_func, l_params, l_params_idx):
        #         # logger.debug("func: {}\nidxs ({}): {}\np[idxs] ({}): {}\nparams names ({}): {}"
        #         #              "".format(func, len(idxs), idxs, len(p[idxs]), p[idxs],
        #         #                        len(param), param))
        #         res += func(p[idxs])
        #     return res

        # arg_list_all = OrderedDict()
        # arg_list_all["param"] = l_allparams
        # arg_list_all["kwargs"] = []

        # db["all"] = DocFunction(function=lnlike_all, arg_list=arg_list_all)
        # db["all"] = self.create_lnlikelihoods_alldataset(datasim_db=datasim_db,
        #                                                  dataset_db=dataset_db,
        #                                                  instmodel4dataset=instmodel4dataset)
        return db

    def create_lnlikelihood_alldataset(self, datasim_db, dataset_db, instmodel4dataset):

        # Create a dict dico_noisemodel which for each noise model give the dataset_name using this
        # noise model and the associated instrument model and datasimulator
        def dicts_factory():
            return deepcopy({"datasim_docfunc": OrderedDict(), "instmodel_obj": OrderedDict()})

        dico_noisemodel = defaultdict(dicts_factory)
        for dataset_name in instmodel4dataset:
            instmod_fullname = instmodel4dataset.get_instmod_fullname(dataset_name=dataset_name)
            instmod_obj = self.instruments[instmod_fullname]
            noisemodel_name = instmod_obj.noise_model
            # dico_noisemodel[noisemodel_name]["datasim_docfunc"]
            (dico_noisemodel[noisemodel_name]["datasim_docfunc"]
             [dataset_name]) = datasim_db[instmod_fullname]["whole"]
            (dico_noisemodel[noisemodel_name]["instmodel_obj"]
             [dataset_name]) = instmod_obj

        # Create and fill the list of likelihood function (one for each noise model)
        l_func = []
        # The list of list with the associated param indexes
        l_params_idx = []
        # The list of dictionnary giving the associated kwargs (data, data_err, ...)
        l_allkwargs = []
        # The list of all the parameters names (all noise model param in one list)
        l_allparams = []
        # Create and fill the dictionary giving the noise model instances for each dataset_name in
        # in the all datasets likelihood
        dico_noisemodel_instance = OrderedDict()
        # dico_params_idx_all = OrderedDict()
        for noise_model in dico_noisemodel:
            noisemodel_subclass = mgr_noisemodel.get_noisemodel_subclass(noise_model)  # Create a
            datasim_docfuncs = dico_noisemodel[noisemodel_name]["datasim_docfunc"]  # noise model
            instmodel_objs = dico_noisemodel[noisemodel_name]["instmodel_obj"]  # instance.
            noisemodel_instance = noisemodel_subclass(datasim_docfunc=datasim_docfuncs,
                                                      model_instance=self,
                                                      instmodel_obj=instmodel_objs)
            # doc_func, dico_params_idx_all[noise_model] = noisemodel_instance.lnlike_creator()  # Get the lnlike doc function
            doc_func = noisemodel_instance.lnlike_creator()
            l_func.append(doc_func.function)
            all_kwargs = defaultdict(list)  # Get the kwargs (data, data_err, and the rest)
            for dataset_name in noisemodel_instance.l_dataset:
                dico_noisemodel_instance[dataset_name] = noisemodel_instance
                dataset = dataset_db[dataset_name]
                kwargs = dataset.get_kwargs()
                for karg_type, kwarg_value in kwargs.items():
                    all_kwargs[karg_type].append(kwarg_value)
            l_allkwargs.append(all_kwargs)
            idx_par = []  # Get the l_params_idx
            for par in doc_func.arg_list["param"]:
                if par not in l_allparams:
                    l_allparams.append(par)
                idx_par.append(l_allparams.index(par))
            l_params_idx.append(idx_par)
            # for dataset in noisemodel_instance.l_dataset:
            #     dico_params_idx[noise_model]["dataset"] = l_p

        def lnlike_withalldataset_creator(l_func, l_params_idx, l_allkwargs, arg_list):
            def lnlike_all(p):
                res = 0
                # logger.debug("paramnames like ({}): {}\nparams like ({}): {}"
                #              "".format(len(arg_list_all["param"]), arg_list_all["param"], len(p), p))
                for func, idxs, kwargs in zip(l_func, l_params_idx, l_allkwargs):
                    # logger.debug("func: {}\nidxs ({}): {}\np[idxs] ({}): {}\nparams names ({}): {}"
                    #              "".format(func, len(idxs), idxs, len(p[idxs]), p[idxs],
                    #                        len(param), param))
                    res += func(p[idxs], **kwargs)
                return res

            return DocFunction(function=lnlike_all, arg_list=arg_list)

        arg_list_all = OrderedDict()
        arg_list_all["param"] = l_allparams
        arg_list_all["kwargs"] = []
        doc_f = lnlike_withalldataset_creator(l_func=l_func, l_params_idx=l_params_idx,
                                              l_allkwargs=l_allkwargs, arg_list=arg_list_all)
        return doc_f, dico_noisemodel_instance # , dico_params_idx_all

        # Then create the lnlike filling the kwargs and final sum them
