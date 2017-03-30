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
from collections import OrderedDict


from .manager_noise_model import Manager_NoiseModel
from ..database_func import DatabaseInstLvlDataset
from ....tools.function_w_doc import DocFunction
from ....tools.miscellaneous import interpret_data_filename


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
        l_func = []
        l_params_idx = []
        l_allparams = []
        l_params = []
        for dataset_name in instmodel4dataset:
            instmod_fullname = instmodel4dataset.get_instmod_fullname(dataset_name=dataset_name)
            lnlike_func = lnlike_db[instmod_fullname]["whole"].function
            arg_list = lnlike_db[instmod_fullname]["whole"].arg_list
            fileinfo = interpret_data_filename(dataset_name)
            inst_cat = fileinfo["inst_category"]
            inst_name = fileinfo["inst_name"]
            number = fileinfo["number"]
            dataset = dataset_db[inst_cat][inst_name][number]
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

            l_func.append(db[dataset_name])
            idx_par = []
            for par in arg_list_new["param"]:
                if par not in l_allparams:
                    l_allparams.append(par)
                idx_par.append(l_allparams.index(par))
            l_params_idx.append(idx_par)

        def lnlike_all(p):
            res = 0
            # logger.debug("paramnames like ({}): {}\nparams like ({}): {}"
            #              "".format(len(arg_list_all["param"]), arg_list_all["param"], len(p), p))
            for func, param, idxs in zip(l_func, l_params, l_params_idx):
                # logger.debug("func: {}\nidxs ({}): {}\np[idxs] ({}): {}\nparams names ({}): {}"
                #              "".format(func, len(idxs), idxs, len(p[idxs]), p[idxs],
                #                        len(param), param))
                res += func(p[idxs])
            return res

        arg_list_all = OrderedDict()
        arg_list_all["param"] = l_allparams
        arg_list_all["kwargs"] = []

        db["all"] = DocFunction(function=lnlike_all, arg_list=arg_list_all)

        return db
