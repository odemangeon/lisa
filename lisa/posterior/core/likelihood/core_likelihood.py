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
from collections import defaultdict
from copy import copy
# import matplotlib.pyplot as pl

from .manager_noise_model import Manager_NoiseModel
from ..likelihood_posterior_docfunc import LikelihoodPosteriorDocFunc
from ..model.datasim_docfunc import DatasimDocFunc
from ..database_func import DatabaseInstLvlDataset
from ....tools.function_from_text_toolbox import FunctionBuilder
from ..model import par_vec_name


## logger object
logger = getLogger()

mgr_noisemodel = Manager_NoiseModel()
mgr_noisemodel.load_setup()

tab = "    "


class LikelihoodCreator(object):
    """LikelihoodCreator is an Interface class for Core_Model.

    It provides methods to create likelihood functions for a model.
    """

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
        db_decorr = {}

        # For each dataset_name and associated datasim in the datasim_db_dtset dictionnary, ...
        for dataset_name, datasim in datasim_db_dtset.items():
            # ..., datasim_db_dtset should contain a "all" entry. This entry requires a specific
            # treatment.
            # if dataset_name == "all":
            #     continue

            # ..., create the corresponding lnlikelihood doc function
            # For IND dataset you might not want to model them. In this case the datasim should be None
            if datasim is not None:
                db[dataset_name], db_decorr[dataset_name] = self._create_lnlikelihood(datasim)
            # db[dataset_name] = self.__lnlike_withdataset_creator(lnlike_doc_func.function,
            #                                                      lnlike_doc_func.arg_list,
            #                                                      data=dataset.get_data(),
            #                                                      data_err=dataset.get_data_err())
        return db, db_decorr

    def _create_lnlikelihood(self, datasim_docfunc):
        """Create the lnlikelihood function.

        This function "only" assemble the likelihood function from the datasimulator function and
        the "raw" lnlikelihood functions built from the noise models associated to the datasim
        function and provided in the dico_noisemodel argument.

        It sums the lnlikelihood for each noise_model involved.
        Each lnlikelihood for each noise model is computed like this:
            lnlike_noisemod(l_sim_data, )

        Arguments
        ---------
        datasim_docfunc : DatasimDocFunc
            DatasimDocFunc specifying the data type (instrument category), the instrument models and
            the datasets simulated by this datasimulator of which you want to get the likelihood function
            of.

        Returns
        -------
        lnlike_docf     : return function
            ln likelihood function. This function can have different set of
            arguments. If the datasim doc function provided in argument does include the dataset
            kwargs, then it takes as arguments only the parameters vector (including the datasim
            parameter and the noise models parameters). Otherwise the datasim doc function provided
            in argument does NOT include the dataset kwargs and in this case if the include_dataset
            argument is True the output lnlike function will include them and take only the
            parameters vector as argument. If the include_dataset argument is False the lnlike
            function will take as arguments the parameters vector and the dataset kwargs.
        decorr_docfs    :
        """

        dataset_included_in_datasim = datasim_docfunc.include_dataset_kwarg

        if not(dataset_included_in_datasim):
            raise NotImplementedError("For now, __likelihood_creator cannot be applied to a data "
                                      "simulator for which the dataset is not included")

        func_shortname_lnlike = "lnlike"
        l_func_shortname = [func_shortname_lnlike, ]

        func_builder = FunctionBuilder()
        parameters = [self.get_parameter(name=param_fullname, notexist_ok=False, return_error=False, kwargs_get_list_params={'main': True, 'free': True, 'no_duplicate': True, 'recursive': True}, kwargs_get_name={'recursive': True, 'include_prefix': True}) for param_fullname in datasim_docfunc.param_model_names_list]
        l_mand_args = copy(datasim_docfunc.mand_kwargs_list)
        if par_vec_name in l_mand_args:
            l_mand_args.remove(par_vec_name)
        func_builder.add_new_function(shortname=func_shortname_lnlike, parameters=parameters,
                                      mandatory_args=l_mand_args,
                                      optional_args=copy(datasim_docfunc.opt_kwargs_dict),
                                      full_function_name=None)

        (l_dataset_obj, d_required_datasetkwargkeys_4_dataset, d_required_datasetkwargkeys_4_inddataset,
         dico_noisemodel, dico_decorr_4_instmod, noisemodel_names_list
         ) = self._get_required_dataset(datasim_docfunc=datasim_docfunc)
        l_dataset_name = [dst.dataset_name for dst in l_dataset_obj]

        # If a likelihood decorrelation is required add a decorr function to the function builder
        func_shortname_decorr = "decorr"
        func_shortname_plotdecorr = "plotdecorr"
        l_func_shortname_decorr = [func_shortname_decorr, func_shortname_plotdecorr]
        if len(dico_decorr_4_instmod) > 0:
            for func_shortname in l_func_shortname_decorr:
                l_func_shortname.append(func_shortname)
                func_builder.add_new_function(shortname=func_shortname, parameters=parameters,
                                              mandatory_args=l_mand_args,
                                              optional_args=copy(datasim_docfunc.opt_kwargs_dict),
                                              full_function_name=None)

        # Create the datasimulator that simulate all the dataset object required
        if l_dataset_name == list(datasim_docfunc.dataset_names_list):
            datasim_all_dst_doc_func = datasim_docfunc
        else:
            datasim_all_dst_doc_func = self.create_datasimulator_4_ldataset(l_dataset_obj=l_dataset_obj)

        l_idx_param_dtsim = list(range(len(datasim_all_dst_doc_func.param_model_names_list)))
        datasim_mand_arg = datasim_all_dst_doc_func.mand_kwargs_list
        datasim_mand_arg.remove(par_vec_name)
        mand_args_text = ", ".join(datasim_mand_arg)
        opt_args_text = ", ".join(datasim_all_dst_doc_func.opt_kwargs_dict.keys())
        if (mand_args_text == '') and (opt_args_text == ''):
            additional_args_text = ''
        elif (mand_args_text != '') and (opt_args_text != ''):
            additional_args_text = f', {mand_args_text}, {opt_args_text}'
        else:
            additional_args_text = f', {mand_args_text+opt_args_text}'
        for func_shortname in l_func_shortname:
            func_builder.add_variable_to_ldict(variable_name="l_idx_param_dtsim", variable_content=l_idx_param_dtsim, function_shortname=func_shortname, exist_ok=False)
            func_builder.add_variable_to_ldict(variable_name="datasim_func_alldst", variable_content=datasim_all_dst_doc_func.function, function_shortname=func_shortname, exist_ok=False)
            func_builder.add_to_body_text(text=f"{tab}sim_data = datasim_func_alldst({par_vec_name}[l_idx_param_dtsim]{additional_args_text})\n", function_shortname=func_shortname)

        # Create the dataset_kwargs dictionary
        dataset_kwargs = defaultdict(dict)

        # Fill the dataset_kwargs dictionary with what is required
        for dataset_name, l_datasetkwarg in d_required_datasetkwargkeys_4_dataset.items():
            dataset_obj = l_dataset_obj[l_dataset_name.index(dataset_name)]
            for datasetkwarg in l_datasetkwarg:
                dataset_kwargs[dataset_name][datasetkwarg] = dataset_obj.get_datasetkwarg(datasetkwarg)
        for func_shortname in l_func_shortname:
            func_builder.add_variable_to_ldict(variable_name="dataset_kwargs", variable_content=dataset_kwargs,
                                               function_shortname=func_shortname, exist_ok=False)

        # Create the dataset_kwargs dictionary
        inddataset_kwargs = defaultdict(dict)

        # Fill the inddataset_kwargs dictionary with what is required
        for inddataset_name, l_datasetkwarg in d_required_datasetkwargkeys_4_inddataset.items():
            dataset_obj = self.dataset_db[inddataset_name]
            for datasetkwarg in l_datasetkwarg:
                inddataset_kwargs[inddataset_name][datasetkwarg] = dataset_obj.get_datasetkwarg(datasetkwarg)

        for func_shortname in l_func_shortname:
            func_builder.add_variable_to_ldict(variable_name="inddataset_kwargs", variable_content=inddataset_kwargs,
                                               function_shortname=func_shortname, exist_ok=False)

        # Initialise the list of parameter for the likelihood computation with the parameter of the
        # datasimulator
        l_paramsfullname_likelihood = datasim_all_dst_doc_func.param_model_names_list.copy()

        # Update the parameters required taking into account the parameter of the noise model
        # Also for each instrument model create the functions of the lnlikelihood and the functions to format
        # the sim_data, the params vector and the dataset_kwargs
        l_instmod_obj = [self.instruments[instmod_fullname] for instmod_fullname in datasim_docfunc.inst_model_fullnames_list]
        for noisemodel_cat, dico in dico_noisemodel.items():
            noise_model_obj = mgr_noisemodel.get_noisemodel_subclass(noisemodel_cat)
            (dico["lnlike_func"], dico["f_format_param"], dico["f_format_simdata"], dico["f_format_datasetkwargs"],
             l_paramsfullname_likelihood
             ) = noise_model_obj.create_lnlikelihood_and_formatinputs(model_instance=self, l_idx_simdata=dico["l_idx_simdata"],
                                                                      l_instmod_obj=[l_instmod_obj[ii] for ii in dico["l_idx_simdata"]],
                                                                      l_dataset_obj=[l_dataset_obj[ii] for ii in dico["l_idx_simdata"]],
                                                                      l_datasetkwargs_req=dico["l_datasetkwargs_req"],
                                                                      l_likelihood_param_fullname=l_paramsfullname_likelihood,
                                                                      datasim_has_multioutputs=datasim_all_dst_doc_func.multi_output,
                                                                      function_builder=func_builder,
                                                                      function_shortname=func_shortname_lnlike,
                                                                      )
            func_builder.add_variable_to_ldict(variable_name=f"lnlike_{noisemodel_cat}", variable_content=dico["lnlike_func"],
                                               function_shortname=func_shortname_lnlike, exist_ok=False)
            func_builder.add_variable_to_ldict(variable_name=f"format_param_{noisemodel_cat}", variable_content=dico["f_format_param"],
                                               function_shortname=func_shortname_lnlike, exist_ok=False)
            func_builder.add_variable_to_ldict(variable_name=f"format_simdata_{noisemodel_cat}", variable_content=dico["f_format_simdata"],
                                               function_shortname=func_shortname_lnlike, exist_ok=False)
            func_builder.add_variable_to_ldict(variable_name=f"format_datasetkwargs_{noisemodel_cat}", variable_content=dico["f_format_datasetkwargs"],
                                               function_shortname=func_shortname_lnlike, exist_ok=False)

        # Update the parameters required taking into account the parameter of the decorrelation model
        # Also for each instrument model create the functions of the decorrelation and the functions to format
        # the sim_data, the params vector, the dataset_kwargs and the inddataset_kwargs
        for inst_mod_fullname, dico in dico_decorr_4_instmod.items():
            instmod_obj = self.instruments[inst_mod_fullname]
            instcat_mod_inst = self.instcat_models[instmod_obj.instrument.category]
            (dico["d_decorrtext_4_dataset"], l_paramsfullname_likelihood
             ) = instcat_mod_inst.create_decorrelation_likelihood(function_builder=func_builder,
                                                                  l_function_shortname=l_func_shortname,
                                                                  inst_model_obj=instmod_obj,
                                                                  dico_decorr_instmod=dico,
                                                                  l_dataset_name=l_dataset_name,
                                                                  l_paramsfullname_likelihood=l_paramsfullname_likelihood,
                                                                  dataset_kwargs=dataset_kwargs,
                                                                  inddataset_kwargs=inddataset_kwargs,
                                                                  datasim_has_multioutputs=datasim_all_dst_doc_func.multi_output,
                                                                  plot_functionshortname=func_shortname_plotdecorr
                                                                  )

        # Text that add the decorrelation to sim data
        # func_builder.add_variable_to_ldict(variable_name="plot", variable_content=pl.plot,
        #                                    function_shortname=func_shortname_lnlike, exist_ok=True)
        # func_builder.add_to_body_text(text=f"{tab}figure()\n", function_shortname=func_shortname_lnlike)
        return_decorr = ""
        for ii, (inst_mod_fullname, dataset_name) in enumerate(zip(datasim_docfunc.inst_model_fullnames_list, datasim_docfunc.dataset_names_list)):
            # func_builder.add_to_body_text(text=f"{tab}plot(dataset_kwargs['{dataset_name}']['data'], '.', label='data')\n", function_shortname=func_shortname_lnlike)
            # func_builder.add_to_body_text(text=f"{tab}plot(sim_data[{ii}], label='simdata_before')\n", function_shortname=func_shortname_lnlike)
            if inst_mod_fullname in dico_decorr_4_instmod:
                decorr_text = dico_decorr_4_instmod[inst_mod_fullname]["d_decorrtext_4_dataset"][dataset_name]
                func_builder.add_to_body_text(text=f"{tab}sim_data[{ii}] += {decorr_text}\n", function_shortname=func_shortname_lnlike)
                if return_decorr == "" and datasim_docfunc.multi_output:
                    return_decorr += "["
                return_decorr += f"{decorr_text}, "
                # func_builder.add_to_body_text(text=f"{tab}plot(sim_data[{ii}], label='simdata_after')\n", function_shortname=func_shortname_lnlike)
                # func_builder.add_to_body_text(text=f"{tab}plot(1 + {decorr_text}, label='decorr')\n", function_shortname=func_shortname_lnlike)
        if return_decorr != "" and datasim_docfunc.multi_output:
            return_decorr += "]"
        else:
            return_decorr = return_decorr[:-2]
        if return_decorr != "":
            func_builder.add_to_body_text(text=f"{tab}return {return_decorr}\n", function_shortname=func_shortname_decorr)
            func_builder.add_to_body_text(text=f"{tab}return None\n", function_shortname=func_shortname_plotdecorr)

        l_noisemodel_cat = list(dico_noisemodel.keys())
        if len(l_noisemodel_cat) > 1:
            func_builder.add_to_body_text(text=f"{tab}res = 0\n", function_shortname=func_shortname_lnlike)
            for noisemodel_cat in l_noisemodel_cat:
                func_builder.add_to_body_text(text=f"{tab}res += lnlike_{noisemodel_cat}(sim_data=format_simdata_{noisemodel_cat}(sim_data), param_noisemodel=format_param_{noisemodel_cat}({par_vec_name}), datasets_kwargs=format_datasetkwargs_{noisemodel_cat}(dataset_kwargs))\n", function_shortname=func_shortname_lnlike)
            func_builder.add_to_body_text(text=f"{tab}return res\n", function_shortname=func_shortname_lnlike)
        else:
            noisemodel_cat = l_noisemodel_cat[0]
            func_builder.add_to_body_text(text=f"{tab}return lnlike_{noisemodel_cat}(sim_data=format_simdata_{noisemodel_cat}(sim_data), param_noisemodel=format_param_{noisemodel_cat}({par_vec_name}), datasets_kwargs=format_datasetkwargs_{noisemodel_cat}(dataset_kwargs))\n", function_shortname=func_shortname_lnlike)

        # Create the lnlike function
        logger.debug(f"text of {func_shortname_lnlike} lnlikelihood function :\n{func_builder.get_full_function_text(shortname=func_shortname_lnlike)}")
        exec(func_builder.get_full_function_text(shortname=func_shortname_lnlike), func_builder._get_ldict(function_shortname=func_shortname_lnlike))
        params_like = [param.full_name for param in func_builder.get_free_parameter_vector(function_shortname=func_shortname_lnlike)]
        dico_param_nb = {nb: param for nb, param in enumerate(params_like)}
        # Check below that it's ok, because of par_vec_name
        if len(func_builder.get_l_mandatory_argument(function_shortname=func_shortname_lnlike)) > 0:
            mand_kwargs = func_builder.get_l_mandatory_argument(function_shortname=func_shortname_lnlike)
        else:
            mand_kwargs = None
        if len(func_builder.get_l_mandatory_argument(function_shortname=func_shortname_lnlike)) > 0:
            opt_kwargs = func_builder.get_l_mandatory_argument(function_shortname=func_shortname_lnlike)
        else:
            opt_kwargs = None
        logger.debug(f"Parameters for {func_shortname_lnlike} function :\n{dico_param_nb}")
        lnlike_docf = LikelihoodPosteriorDocFunc(func_builder._get_ldict(function_shortname=func_shortname_lnlike)[func_builder.get_function_fullname(shortname=func_shortname_lnlike)],
                                                 param_model_names_list=params_like,
                                                 params_model_vect_name=par_vec_name, inst_cats_list=datasim_docfunc.inst_cats_list,
                                                 inst_model_fullnames_list=datasim_docfunc.inst_model_fullnames_list, dataset_names_list=datasim_docfunc.dataset_names_list,
                                                 noisemodel_names_list=noisemodel_names_list, include_dataset_kwarg=datasim_docfunc.include_dataset_kwarg,
                                                 mand_kwargs_list=mand_kwargs,  # datasim.mand_kwargs_list[1:],  # to exclude the params_model_vect_name
                                                 opt_kwargs_dict=opt_kwargs  # datasim.opt_kwargs_dict,
                                                 )

        # Create the decorr function
        decorr_docfs = {}
        for func_shortname in l_func_shortname_decorr:
            if func_shortname in func_builder.l_function_shortname:
                logger.debug(f"text of {func_shortname} likelihood decorrelation simulator function :\n{func_builder.get_full_function_text(shortname=func_shortname)}")
                exec(func_builder.get_full_function_text(shortname=func_shortname), func_builder._get_ldict(function_shortname=func_shortname))
                params_model = [param.full_name for param in func_builder.get_free_parameter_vector(function_shortname=func_shortname)]
                dico_param_nb = {nb: param for nb, param in enumerate(params_model)}
                # Check below that it's ok, because of par_vec_name
                if len(func_builder.get_l_mandatory_argument(function_shortname=func_shortname)) > 0:
                    mand_kwargs = func_builder.get_l_mandatory_argument(function_shortname=func_shortname)
                else:
                    mand_kwargs = None
                if len(func_builder.get_d_optional_argument(function_shortname=func_shortname)) > 0:
                    opt_kwargs = func_builder.get_d_optional_argument(function_shortname=func_shortname)
                else:
                    opt_kwargs = None
                logger.debug(f"Parameters for {func_shortname} function :\n{dico_param_nb}")
                decorr_docfs[func_shortname] = DatasimDocFunc(func_builder._get_ldict(function_shortname=func_shortname)[func_builder.get_function_fullname(shortname=func_shortname)],
                                                              param_model_names_list=params_model,
                                                              params_model_vect_name=par_vec_name, inst_cats_list=datasim_docfunc.inst_cats_list,
                                                              inst_model_fullnames_list=datasim_docfunc.inst_model_fullnames_list, dataset_names_list=datasim_docfunc.dataset_names_list,
                                                              include_dataset_kwarg=datasim_docfunc.include_dataset_kwarg,
                                                              mand_kwargs_list=mand_kwargs,  # datasim.mand_kwargs_list[1:],  # to exclude the params_model_vect_name
                                                              opt_kwargs_dict=opt_kwargs  # datasim.opt_kwargs_dict,
                                                              )

        return lnlike_docf, decorr_docfs

    # WARNING/TODO: Right now this function is not used, because I am not creating likelihoods without dataset
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
        datasim_inst_db.database_unlock()
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
                        (db_lnlike[inst_cat][inst_name][inst_model][obj], decorr_docfs
                         ) = self._create_lnlikelihood(datasim=datasim)
                        for func_shortname in decorr_docfs.keys():
                            datasim_inst_db[inst_cat][inst_name][inst_model][f"{obj}_{func_shortname}_like"] = decorr_docfs[func_shortname]
        datasim_inst_db.lock()
        # If required lock the database
        if lock_db:
            db_lnlike.lock()
        return db_lnlike

    def _get_required_dataset(self, datasim_docfunc):
        """
        """
        ## Deal with the noise_model/likelihood
        # Get list of dataset objects required by datasim_doc_func
        l_dataset_obj = list(set([self.dataset_db[dataset_name] for dataset_name in datasim_docfunc.dataset_names_list]))
        l_dataset_name = [dst.dataset_name for dst in l_dataset_obj]

        noisemodel_names_list = []

        # Create a dictionary that regroups all the info related to the likelihood function of each noise model
        def defdic_noisemod_func():
            return {"l_idx_simdata": [],
                    "l_datasetkwargs_req": [],
                    }

        dico_noisemodel = {}

        # Create d_required_datasetkwargkeys_4_dataset: The list of required kwargs keys for each dataset
        # in l_dataset_obj.
        d_required_datasetkwargkeys_4_dataset = defaultdict(list)

        # Fill dico_noisemodel and d_required_datasetkwargkeys_4_dataset
        for ii in range(datasim_docfunc.noutput):
            instmod_fullname = datasim_docfunc.inst_model_fullnames_list[ii]
            instmod_obj = self.instruments[instmod_fullname]
            noisemod_cat = instmod_obj.noise_model
            noisemodel_names_list.append(noisemod_cat)
            dataset_name = datasim_docfunc.dataset_names_list[ii]
            if noisemod_cat not in dico_noisemodel:
                dico_noisemodel[noisemod_cat] = defdic_noisemod_func()
            # Fill the "l_idx_simdata" entry of dico_noisemodel
            dico_noisemodel[noisemod_cat]["l_idx_simdata"].append(l_dataset_name.index(dataset_name))
            # Fill the "l_datasetkwargs_req" entry of dico_noisemodel
            noise_model_obj = mgr_noisemodel.get_noisemodel_subclass(noisemod_cat)
            dico_noisemodel[noisemod_cat]["l_datasetkwargs_req"].append(noise_model_obj.l_required_datasetkwarg_keys)
            # Fill d_required_datasetkwargkeys_4_dataset
            for datasetkwarg in noise_model_obj.l_required_datasetkwarg_keys:
                if datasetkwarg not in d_required_datasetkwargkeys_4_dataset[dataset_name]:
                    d_required_datasetkwargkeys_4_dataset[dataset_name].append(datasetkwarg)

        ## Deal with the decorrelation
        # Update this list with the list of dataset objects required by the decorrelation and at the same time
        # get the list of dataset object required for the decorrelation of each instrument model
        d_l_dataset_obj_4_instmod_obj_decorr = {}
        l_dataset_obj_decorr = []
        l_instmod_obj = []
        for instmod_obj_fullname in datasim_docfunc.inst_model_fullnames_list:
            if instmod_obj_fullname not in (d_l_dataset_obj_4_instmod_obj_decorr):
                instmod_obj = self.instruments[instmod_obj_fullname]
                instcat_mod_inst = self.instcat_models[instmod_obj.instrument.category]
                if instcat_mod_inst.require_likelihood_decorrelation(instmod_fullname=instmod_obj_fullname):
                    l_instmod_obj.append(instmod_obj)
                    d_l_dataset_obj_4_instmod_obj_decorr[instmod_obj_fullname] = instcat_mod_inst.get_l_dataset_obj_4_decorrelation(instmod_obj=instmod_obj)
                    l_dataset_obj_decorr += d_l_dataset_obj_4_instmod_obj_decorr[instmod_obj_fullname]
        l_dataset_obj = l_dataset_obj + list(set(l_dataset_obj_decorr) - set(l_dataset_obj))
        l_dataset_name = [dst.dataset_name for dst in l_dataset_obj]

        dico_decorr_4_instmod = {}

        # Create d_required_datasetkwargkeys_4_inddataset: The list of required kwargs keys for each
        # indicator dataset
        d_required_datasetkwargkeys_4_inddataset = defaultdict(list)

        for ii in range(datasim_docfunc.noutput):
            instmod_fullname = datasim_docfunc.inst_model_fullnames_list[ii]
            instmod_obj = self.instruments[instmod_fullname]
            instcat_mod_inst = self.instcat_models[instmod_obj.instrument.category]
            dataset_name = datasim_docfunc.dataset_names_list[ii]
            if instcat_mod_inst.require_likelihood_decorrelation(instmod_fullname=instmod_fullname):
                (d_required_datasetkwargkeys_4_dataset, d_required_datasetkwargkeys_4_inddataset, dico_decorr_4_instmod
                 ) = instcat_mod_inst._get_required_dataset(d_required_datasetkwargkeys_4_dataset,
                                                            d_required_datasetkwargkeys_4_inddataset,
                                                            dico_decorr_4_instmod, l_dataset_name, instmod_fullname,
                                                            dataset_name)

        return (l_dataset_obj, d_required_datasetkwargkeys_4_dataset, d_required_datasetkwargkeys_4_inddataset,
                dico_noisemodel, dico_decorr_4_instmod, noisemodel_names_list)
