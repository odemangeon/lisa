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
from numpy import sum as npsum
from numpy import log as nplog
from math import exp
from collections import OrderedDict

from .database_func import DatabaseInstLvlDataset
from ...tools.function_w_doc import DocFunction
from ...tools.miscellaneous import interpret_data_filename


## logger object
logger = getLogger()


class LikelihoodCreator(object):
    """docstring for LikelihoodCreator."""

    _lnlikelihoods = {
        "wo jitter": """def {}(p, data, data_err, **kwarg_data):
            model = datasim_func(p, **kwarg_data)
            inv_sigma2 = 1.0 / (data_err**2)
            return -0.5 * (npsum((data - model)**2 * inv_sigma2 + nplog(inv_sigma2)))""",
        "jitter dfm": """def {}(p, data, data_err, **kwarg_data):
            model = datasim_func({}, **kwarg_data)
            inv_sigma2 = 1.0 / (data_err**2 + model**2 * exp(2 * {}))
            return -0.5 * (npsum((data - model)**2 * inv_sigma2 - nplog(inv_sigma2)))""",
        "jitter multiplicative": """def {}(p, data, data_err, **kwarg_data):
            model = datasim_func({}, **kwarg_data)
            inv_sigma2 = 1.0 / (data_err**2 * exp(2 * {}))
            return -0.5 * (npsum((data - model)**2 * inv_sigma2 - nplog(inv_sigma2)))""",
        "jitter multiplicative baluev": """def {}(p, data, data_err, **kwarg_data):
            model = datasim_func({}, **kwarg_data)
            inv_sigma2 = 1.0 / (data_err**2 * exp(2 * {}))
            Bualev_coeff = 1.0 / (1 - len(p)/len(data))
            return -0.5 * (npsum((data - model)**2 * inv_sigma2 * Bualev_coeff -
                                 nplog(inv_sigma2)))""",
        "jitter additive": """def {}(p, data, data_err, **kwarg_data):
            model = datasim_func({}, **kwarg_data)
            inv_sigma2 = 1.0 / (data_err**2 * (1 + exp(2 * {})))
            return -0.5 * (npsum((data - model)**2 * inv_sigma2 - nplog(inv_sigma2)))""",
        "jitter additive baluev": """def {}(p, data, data_err, **kwarg_data):
            model = datasim_func({}, **kwarg_data)
            inv_sigma2 = 1.0 / (data_err**2 * (1 + exp(2 * {})))
            Bualev_coeff = 1.0 / (1 - (len(p) - 1)/len(data))
            return -0.5 * (npsum((data - model)**2 * inv_sigma2 * Bualev_coeff -
                                 nplog(inv_sigma2)))"""}

    def _create_lnlikelihood(self, datasimulator, category="wo jitter", jitter_param=None):
                            # **kwarg_data):
        """Return the log likelihood function."""

        datasim_func = datasimulator.function
        function_name = "lnlikelihood"

        def finalize_and_create_lnlike(datasimulator, text_func, jitter_param=None):
            arg_list = datasimulator.arg_list.copy()
            if jitter_param is not None:
                if jitter_param.free:
                    text = text_func.format(function_name, "p[1:]", "p[0]")
                    arg_list["param"] = [jitter_param.full_name] + arg_list["param"]
                else:
                    text = text_func.format(function_name, "p", jitter_param.value)
            else:
                text = text_func.format(function_name)
            arg_list["kwargs"] = ["data", "data_err"] + arg_list["kwargs"]
            logger.debug("Log likelihood function text: {}".format(text))
            logger.debug("Log likelihood arg_list: {}".format(arg_list))
            ldict = locals().copy()
            ldict["datasim_func"] = datasim_func
            ldict["exp"] = exp
            ldict["nplog"] = nplog
            ldict["npsum"] = npsum
            exec(text, ldict)
            doc_f = DocFunction(function=ldict[function_name], arg_list=arg_list)
            return doc_f

        if category in self._lnlikelihoods.keys():
            text_func = self._lnlikelihoods[category]
            if category == "wo jitter":
                jitter_cat_ok = jitter_param is None
                if not(jitter_cat_ok):
                    jitter_cat_ok = not(jitter_param.main)
                if jitter_cat_ok:
                    return finalize_and_create_lnlike(datasimulator, text_func)
                else:
                    raise ValueError("For likelihood '{}' the jitter parameter should not be a main"
                                     "parameter.".format(category))
            else:
                jitter_cat_ok = jitter_param.main
                if jitter_cat_ok:
                    return finalize_and_create_lnlike(datasimulator, text_func, jitter_param)
                else:
                    raise ValueError("For likelihood '{}' the jitter parameter should be a main"
                                     "parameter.".format(category))
        else:
            raise ValueError("Category {} not recognized. Avalaible categories are {}"
                             "".format(self._ln_categories))

    def create_lnlikelihoods(self, datasim_db, category="wo jitter",
                             affectinstmodel4dataset=False, lock_db=False):
        """Return the likelihood for each instrument model used.

        datasim_db : DatabaseInstLvlDataset or DatabaseInstLevel instance
        """
        if affectinstmodel4dataset:
            instmodel4dataset = self.instmodel4dataset.copy()
        else:
            instmodel4dataset = None
        db = DatabaseInstLvlDataset(object_stored="datasimulator", database_name=self.object_name,
                                    instmodel4dataset=instmodel4dataset, ordered=False)
        db.database_unlock()
        # if datasim_db is None:
        #     datasim_db = self.create_datasimulators()
        # Create the instrument_db entries
        for inst_cat in datasim_db:
            for inst_name in datasim_db[inst_cat]:
                for inst_model in datasim_db[inst_cat][inst_name]:
                    db[inst_cat][inst_name][inst_model] = {}
                    for obj in datasim_db[inst_cat][inst_name][inst_model]:
                        datasim = datasim_db[inst_cat][inst_name][inst_model][obj]
                        instmod_obj = self.instruments[inst_cat][inst_name][inst_model]
                        if instmod_obj.has_parameter(name="jitter", main=True):
                            jitter_param = instmod_obj.jitter
                        else:
                            jitter_param = None
                        (db[inst_cat][inst_name][inst_model][obj]
                         ) = self._create_lnlikelihood(datasim, category=category,
                                                       jitter_param=jitter_param)
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
