#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
gp_lnlike module.

The objective of this module is to define the log likelihood in case you want to use a GP to
model the residuals.

@DONE:
    -

@TODO:
    -
"""
from loguru import logger
from george.kernels import ExpSquaredKernel, ExpSine2Kernel
from george import GP
from numpy import concatenate, sqrt
import numpy as np
from collections import defaultdict, Counter, OrderedDict
import os
from os.path import basename
# from collections import OrderedDict

# from ..model.celestial_bodies import Star
from ..dataset_and_instrument.rv import RV_inst_cat
from ..dataset_and_instrument.lc import LC_inst_cat
from ...core.parameter import Parameter
from ...core.likelihood.jitter_noise_model import jitter_name, GaussianNoiseModel_wjitteradd
from ...core.dataset_and_instrument.indicator import IND_inst_cat
from ....tools.miscellaneous import spacestring_like
from ....tools.human_machine_interface.QCM import QCM_utilisateur
from ....tools.function_from_text_toolbox import FunctionBuilder
# from ....tools.function_w_doc import DocFunction


stelact_GP_noisemodel = "stellar_activity"

amp = "amp"
tau = "tau"
gamma = "gamma"
logperiod = "lnperiod"

param_noisemod_name = "param_noisemod"


def get_stelact_GP_param_name(param_GP_name, stelact_mod_name):
    """Return a Name and Named instance of the GP hyper parameter.

    Arguments
    ---------
    param_GP_name : String
        Name of the GP parameter (amp, tau, etc.)
    stelact_mod_name : String
        Name of the stellar activity model as provided in the stellar activity noise model parameter file

    Returns
    -------
    name : String
        String for the name argument of the parameter __init__ method
    """
    return f"{param_GP_name}{stelact_mod_name}"


class StellarActNoiseModel(GaussianNoiseModel_wjitteradd):
    """docstring for StellarActNoiseModel."""

    __category__ = stelact_GP_noisemodel
    __has_GP__ = True
    __has_jitter__ = True

    l_required_datasetkwarg_keys = ["data", "data_err", "time"]

    kernel_text = ("{amp}**2 * ExpSquaredKernel(metric={tau}) * "
                   "ExpSine2Kernel(gamma=1/(2 * {gamma}**2), log_period={log_period})")
    # The parametrisation of the quasi-periodic Kernel is taken from Grunblatt, Howard & Haywood 2015 The Astrophysical Journal. 808:127

    # Comment: There is no need to sort the times because George does it automicatically.
    # Before the version 0.3.1 of george, there was a sort argument (which was True by default) which need to
    # Be True to sort the x values
    # This function if for 1 stellar activity model.
    # The expected format for the inputs are
    # sim_data : List of arrays containing the simulated dataset for each dataset associated with the stellar activity model corresponding to this function
    # param_noisemod : array of parameter values
    # l_datakwargs :  list of dictionaries giving the dataset kwargs for of each dataset associated with the stellar activity model corresponding to this function. Keys are "data", "data_err", "t" and values are arrays extracted from the datasets.
    lnlikefunc_text = """def {func_name}(sim_data, {param_noisemod_name}, l_datakwargs):
        dict_datakwargs = defaultdict(list)
        for datakwargs, jitter in zip(l_datakwargs, {text_l_jitter}):
            dict_datakwargs["time"].append(datakwargs["time"])
            dict_datakwargs["data"].append(datakwargs["data"])
            # print((sqrt(datakwargs["data_err"]**2 + jitter**2)).shape)
            dict_datakwargs["data_err"].append(sqrt(datakwargs["data_err"]**2 + jitter**2))
        gp = GP({kernel})
        # import pdb; pdb.set_trace()
        # print("t: len(dict_datakwargs['t']):", len(dict_datakwargs['t']), "concatenate(dict_datakwargs['t']):", concatenate(dict_datakwargs['t']))
        gp.compute(concatenate(dict_datakwargs["time"]), concatenate(dict_datakwargs["data_err"]))
        # print(type(dict_datakwargs["data"]), len(dict_datakwargs["data"]), dict_datakwargs["data"][0].shape)
        # print(type(sim_data), len(sim_data), type(sim_data[0]))
        # print((concatenate(dict_datakwargs["data"]) - concatenate(sim_data)).shape)
        res = gp.log_likelihood((concatenate(dict_datakwargs["data"]) - concatenate(sim_data)).reshape((-1)))
        # print(res)
        return res
        # return gp.log_likelihood((concatenate(dict_datakwargs["data"]) - concatenate(sim_data)).reshape((-1)))
        """

    function_name = "lnlike_{stelact_mod_name}_SA"

    gpsim_func_text = """def {func_name}(sim_data, {param_noisemod_name}, l_datakwargs, tsim):
        dict_datakwargs = defaultdict(list)
        for datakwargs, jitter in zip(l_datakwargs, {text_l_jitter}):
            dict_datakwargs["time"].append(datakwargs["time"])
            dict_datakwargs["data"].append(datakwargs["data"])
            #print(f"jitter: {{jitter}}")
            dict_datakwargs["data_err"].append(sqrt(datakwargs["data_err"]**2 + jitter**2))
        gp = GP({kernel})
        gp.compute(concatenate(dict_datakwargs["time"]), concatenate(dict_datakwargs["data_err"]))
        #print(f"std(resi):{{np.std((concatenate(dict_datakwargs['data']) - concatenate(sim_data)).reshape((-1)))}}")
        pred, pred_var = gp.predict((concatenate(dict_datakwargs["data"]) - concatenate(sim_data)).reshape((-1)), tsim, return_var=True)
        #print(f"std(pred): {{np.std(pred)}}")
        #print(f"pred(var): {{pred_var}}")
        return pred, pred_var
        # return gp.sample_conditional((concatenate(dict_datakwargs["data"]) - concatenate(sim_data)).reshape((-1)),
        #                             tsim)
        """

    gpsim_function_name = "gp_sim"

    _star_param_GP_names = [amp, tau, gamma, logperiod]

    _allowed_inst_cat = [RV_inst_cat, LC_inst_cat, IND_inst_cat]

    # This is now done in the StellarActivityNoiseModelInterface.apply_parametrisation_stelact_noisemod
    # @classmethod
    # def apply_parametrisation(cls, model_instance, instmod_fullname):
    #     """Add in the model the necessary main parameters for the noise model.
    #
    #     This function is called by Core_Model.set_noisemodels for each instrument model.
    #
    #     :param Core_Model model_instance: Instance of Core_Model or a subclass of it. Mandatory for
    #         noise model which requires parameter of the object studied (like GP and stellar
    #         activity)
    #     :param string instmod_fullname: Full name of the instrument involved in the noise model and
    #         for which you want to apply the parametrisation for the noise modelling.
    #     """
    #     # Load the star and inst_model object
    #     star = model_instance.stars[list(model_instance.stars.keys())[0]]
    #     inst_model_obj = model_instance.instruments[instmod_fullname]
    #     inst = inst_model_obj.instrument
    #     inst_cat = inst.category
    #     if inst_cat not in cls._allowed_inst_cat:
    #         raise ValueError(f"Stellar activity noise model can only be used for instrument category "
    #                          f"{cls._allowed_inst_cat}, got {inst_cat}."
    #                          )
    #     # Set the star parameters (tau, gamma, logperiod, amp)
    #     for param_name in cls._star_param_GP_names:
    #         if star.has_parameter(name=param_name):
    #             param = star.get_parameter(name=param_name)
    #             if not param.main:
    #                 param.main = True
    #         else:
    #             star.add_parameter(Parameter(name=param_name, name_prefix=star.name, main=True))
    #     # Set the instrument models parameters (jitter)
    #     super(StellarActNoiseModel, cls).apply_parametrisation(model_instance=model_instance, instmod_fullname=instmod_fullname)

    @classmethod
    def create_lnlikelihood_and_formatinputs(cls, model_instance, l_idx_simdata, l_instmod_obj, l_dataset_obj,
                                             l_datasetkwargs_req, l_likelihood_param_fullname, datasim_has_multioutputs,
                                             function_builder, function_shortname):
        """Create the prefilled lnlikehood function (without the datasim) for the noise model and provide the function to format the inputs and provide the dataset_kwargs

        For a detailed docstring look at Core_NoiseModel.create_lnlikelihood_and_formatinputs
        """
        (lnlike_jitter, l_params_new, dico_params_noisemod, dico_idx_param_noisemod, dico_idx_datasim, dico_idx_l_dataset_obj
         ) = cls.get_prefilledlnlike(l_params=l_likelihood_param_fullname, model_instance=model_instance,
                                     l_instmod_obj=l_instmod_obj, l_idx_simdata=l_idx_simdata, function_builder=function_builder,
                                     function_shortname=function_shortname)

        def f_format_param(param_likelihood):
            return {stelact_mod_name: param_likelihood[idx_param_stelact_mod] for stelact_mod_name, idx_param_stelact_mod in dico_idx_param_noisemod.items()}

        if datasim_has_multioutputs:
            def f_format_simdata(sim_data):
                return {stelact_mod_name: [sim_data[ii] for ii in idx_simdata_stelact_mod] for stelact_mod_name, idx_simdata_stelact_mod in dico_idx_datasim.items()}
        else:
            def f_format_simdata(sim_data):
                return {stelact_mod_name: [sim_data, ] for stelact_mod_name, idx_simdata_stelact_mod in dico_idx_datasim.items()}

        def f_format_dataset_kwargs(dataset_kwargs):
            return {stelact_mod_name: [{datasetkwarg: dataset_kwargs[l_dataset_obj[jj].dataset_name][datasetkwarg] for datasetkwarg in l_datasetkwargs_req[jj]} for jj in idexes_l_dataset_obj_stelact_mod] for stelact_mod_name, idexes_l_dataset_obj_stelact_mod in dico_idx_l_dataset_obj.items()}

        # dataset_kwargs = {stelact_mod_name: [cls.get_necessary_datakwargs(l_dataset_obj[jj]) for jj in idexes_l_dataset_obj_stelact_mod] for stelact_mod_name, idexes_l_dataset_obj_stelact_mod in dico_idx_l_dataset_obj.items()}

        return lnlike_jitter, f_format_param, f_format_simdata, f_format_dataset_kwargs, l_params_new

    @classmethod
    def get_prefilledlnlike(cls, l_params, model_instance, l_instmod_obj, l_idx_simdata, function_builder, function_shortname):
        """Return a ln likelihood function prefilled with the fixed parameters for all stellar activity model.

        Arguments
        ---------
        l_params         : list of String
            Current list of parameters full names.
        model_instance   : Core_Model
            Instance of Core_Model or a subclass of it. Mandatory for noise model which requires parameter of the object studied (like GP and stellar activity)
        l_instmod_obj    : list_of_InstrumentModel
            list of instrument model for the ln likelihood to produce.
        l_idx_simdata            : list of Integers
            List of indexes in the sim_data list (output of the datasimulator function this likelihood function is associated with) which correspond to dataset that should be modeled with this noise model

        Returns
        -------
        prefilled_lnlike        : function
            Prefilled ln likelohood function with as input parameters
            model the simulated data (array), param_noisemod the free parameters value for the noise
            model, the list of dataset kwargs and returns the ln posterior value
        l_params_new            : list_of_string
            Updated list of parameters full names.
        dico_params_noisemod    : Dictionary of list of String
            Dictionary giving the list of parameter full names for each stellar activity noise model
            keys : Stellar activity model names (as defined in the stellar activity parameter file)
            values : List of the full names of the parameters for each stellar activity noise model.
        dico_idx_param_noisemod :  Dictionary of list of Integer
            Dictionary giving the indexes of the noise model parameters in the updated list of parameters of the likelihood function (l_params_new) for each stellar activity noise model
            keys : Stellar activity model names (as defined in the stellar activity parameter file)
            values : List of the indexes of the noise model parameters in the updated list of parameters of the likelihood function (l_params_new) for each stellar activity noise model.
        dico_idx_datasim        :  Dictionary of list of Integer
            Dictionary giving the indexes of the simulated data in the full sim_data (output of the datasimulator associated with this likelihood) for stellar activity noise model
            keys : Stellar activity model names (as defined in the stellar activity parameter file)
            values : List of the indexes of the simulated data in the full sim_data (output of the datasimulator associated with this likelihood) for stellar activity noise model\
        dico_idx_l_dataset_obj  :  Dictionary of list of Integer
            Dictionary giving the indexes of the dataset_obj in the list of dataset object (l_dataset_obj) for stellar activity noise model
            keys : Stellar activity model names (as defined in the stellar activity parameter file)
            values : List of the indexes of the dataset_obj in the list of dataset object.
        """
        l_params_new = l_params.copy()
        # Go through the instrument models and sort them into stellar activity models
        dico_linstmodobj4stelactmodname = OrderedDict()
        dico_idx_datasim = {}
        dico_idx_l_dataset_obj = {}
        for jj, (ii, instmod_obj) in enumerate(zip(l_idx_simdata, l_instmod_obj)):
            stelact_mod_name = model_instance.modelstelactname_4_instmodfullname[instmod_obj.full_name]  # modelstelactname_4_instmodfullname is defined in StellarActivityNoiseModelInterface
            if stelact_mod_name in dico_linstmodobj4stelactmodname:
                dico_linstmodobj4stelactmodname[stelact_mod_name].append(instmod_obj)
                dico_idx_datasim[stelact_mod_name].append(ii)
                dico_idx_l_dataset_obj[stelact_mod_name].append(jj)
            else:
                dico_linstmodobj4stelactmodname[stelact_mod_name] = [instmod_obj, ]
                dico_idx_datasim[stelact_mod_name] = [ii, ]
                dico_idx_l_dataset_obj[stelact_mod_name] = [jj, ]

        dico_func = {}
        dico_params_noisemod = {}
        dico_idx_param_noisemod = {}
        # Produce a prefilled likelihood for each stellar activity noise model
        for stelact_mod_name, l_instmod_obj_stelact_mod in dico_linstmodobj4stelactmodname.items():
            (dico_func[stelact_mod_name], l_params_new, dico_params_noisemod[stelact_mod_name], dico_idx_param_noisemod[stelact_mod_name]
             ) = cls.get_prefilledlnlike_1SANM(l_params=l_params_new, l_params_noisemod=[], l_idx_param_noisemod=[],
                                               model_instance=model_instance, l_instmod_obj=l_instmod_obj_stelact_mod,
                                               stelact_mod_name=stelact_mod_name, function_builder=function_builder,
                                               function_shortname=function_shortname
                                               )

        l_stelact_mod_name = list(dico_linstmodobj4stelactmodname.keys())

        def lnlike_allSANM(sim_data, param_noisemodel, datasets_kwargs):
            """Ln likelihood including all stellar activity models provided

            The provided stellar activity model provided are: {l_stelact_mod_name}

            Arguments
            ---------
            sim_data                : Dictionary of list of np.array
                dictionary of list of arrays giving the sim_data (simulated data) for each stellar activity noise model
                keys : Stellar activity model names (as defined in the stellar activity parameter file)
                values : list of simulated data array of each datasets simulated by each stellar activity noise model
            param_noisemodel  : Dictionary of np.array
                dictionary of array giving the parameters values for the parameters of each stellar activity noise model
                keys : Stellar activity model names (as defined in the stellar activity parameter file)
                values : array of parameter values for each stellar activity noise model
            datasets_kwargs : dictionary of list of dictionaries
                dictionary of list of dictionaries giving the dataset keyword arguments of the dataset associated with each stellar activity noise model.
                keys : Stellar activity model names (as defined in the stellar activity parameter file)
                values : list of dictionaries of datasets values.
                    keys: "data", "data_err", "t"
                    values: list of array giving these values for each datasets associated with each stellar activity noise model
            """.format(l_stelact_mod_name=list(dico_linstmodobj4stelactmodname.keys()))
            res = 0
            for stelact_mod_name in l_stelact_mod_name:
                res += dico_func[stelact_mod_name](sim_data[stelact_mod_name], param_noisemodel[stelact_mod_name], datasets_kwargs[stelact_mod_name])
            return res

        return lnlike_allSANM, l_params_new, dico_params_noisemod, dico_idx_param_noisemod, dico_idx_datasim, dico_idx_l_dataset_obj

    @classmethod
    def get_prefilledlnlike_1SANM(cls, l_params, l_params_noisemod, l_idx_param_noisemod, model_instance,
                                  l_instmod_obj, stelact_mod_name, function_builder, function_shortname):
        """Return a ln likelihood function prefilled with the fixed parameters for a given stellar activity model.

        This function is used by LikelihoodCreator.Core_model._create_lnlikelihood()

        Arguments
        ---------
        l_params          : list of String
            Current list of parameters full names.
        l_params_noisemod :  list of String
            Current list of parameters full names.
        model_instance    : Core_Model
            Instance of Core_Model or a subclass of it. Mandatory for noise model which requires parameter of the object studied (like GP and stellar activity)
        l_instmod_obj    : list_of_InstrumentModel
            list of instrument model for the ln likelihood to produce. Here all instrument model should have the same stellar activity noise model whose name is stelact_mod_name
        stelact_mod_name : String
            Name of the stellar activity model as provided in the stellar activity noise model parameter file

        Returns
        -------
        prefilled_lnlike      : function
            Prefilled ln likelohood function with as input parameters
            model the simulated data (array), param_noisemod the free parameters value for the noise
            model, the list of dataset kwargs and returns the ln posterior value
        l_params_new          : list of String
            Updated list of parameters full names.
        l_params_noisemod_new : list of String
        l_idx_param_noisemod  : list of Integer
            List of the index of the noise model parameters in the updated list of parameters (l_params_new).
        """
        ldict = {}  # TODO: Check if an empty dict would be enough
        l_params_new = l_params.copy()
        l_idx_param_noisemod_new = l_idx_param_noisemod.copy()
        l_params_noisemod_new = l_params_noisemod.copy()
        (ker, l_params_new,
         l_params_noisemod,
         l_idx_param_noisemod) = cls.__get_text_define_GP(model_instance=model_instance, l_params=l_params_new,
                                                          l_params_noisemod=l_params_noisemod_new, l_idx_param_noisemod=l_idx_param_noisemod_new,
                                                          stelact_mod_name=stelact_mod_name, function_builder=function_builder,
                                                          function_shortname=function_shortname,
                                                          )
        (text_l_jitter,
         l_params_new,
         l_params_noisemod,
         l_idx_param_noisemod,
         l_jitter_paramname) = cls.__get_text_l_jitter(l_instmod_obj=l_instmod_obj, l_params=l_params_new,
                                                       l_params_noisemod=l_params_noisemod,
                                                       l_idx_param_noisemod=l_idx_param_noisemod,
                                                       function_builder=function_builder,
                                                       function_shortname=function_shortname,
                                                       )
        func = cls.lnlikefunc_text.format(func_name=cls.function_name.format(stelact_mod_name=stelact_mod_name), param_noisemod_name=param_noisemod_name, kernel=ker, text_l_jitter=text_l_jitter)
        ldict["defaultdict"] = defaultdict
        ldict["list"] = list
        ldict["concatenate"] = concatenate
        ldict["logger"] = logger
        ldict["ExpSquaredKernel"] = ExpSquaredKernel
        ldict["ExpSine2Kernel"] = ExpSine2Kernel
        ldict["GP"] = GP
        ldict["sqrt"] = sqrt
        logger.debug(f"Likelihood of the stellar activity model {stelact_mod_name}:\n {func}\nl_params_noisemod: {l_params_noisemod}, l_idx_param_noisemod: {l_idx_param_noisemod}")
        exec(func, ldict)
        return ldict[cls.function_name.format(stelact_mod_name=stelact_mod_name)], l_params_new, l_params_noisemod, l_idx_param_noisemod

    @classmethod
    def check_parametrisation(cls, model_instance, instmod_fullname):
        """Check the parameteristion for the noise model.

        :param Core_Model model_instance: Instance of Core_Model or a subclass of it. Mandatory for
            noise model which requires parameter of the object studied (like GP and stellar
            activity)
        :param string instmod_fullname: Full name of the instrument involved in the noise model and
            for which you want to apply the parametrisation for the noise modelling.
        """
        # Check the star parameters
        err_msg = ("The noise model of instrument model {} being {}, it must have a {} "
                   "{} parameter !")
        star = cls.get_star(model_instance)
        for param in cls.get_star_params_GP(model_instance):
            if param.get_name() not in star.parameters:
                raise ValueError(err_msg.format(instmod_fullname, cls.category, param.get_name(include_prefix=True,
                                                                                               recursive=True
                                                                                               ),
                                                "")
                                 )
            if not(param.main):
                raise ValueError(err_msg.format(instmod_fullname, cls.category, param.get_name(include_prefix=True,
                                                                                               recursive=True),
                                                "main")
                                 )
        # Check the jitter parameter
        cls.check_parametrisation(model_instance=model_instance, instmod_fullname=instmod_fullname)

    @classmethod
    def get_necessary_datakwargs(cls, dataset):
        """Return the data kwargs necessary for the computation of the likelihood.

        :param Dataset dataset: Dataset instance.
        :return dict datakwargs: dict with keys= datakwargs type (eg. "data"), value= value(s) of
            this datakwarg for this dataset.
        """
        return {"data": dataset.get_data(), "data_err": dataset.get_data_err(),
                "t": dataset.get_time()}

    @classmethod
    def get_star(cls, model_instance):
        """Return the star object used for this stellar activity noise modelling.

        :param Core_Model model_instance: Instance of Core_Model or a subclass of it. Mandatory for
            noise model which requires parameter of the object studied (like GP and stellar
            activity)
        :return Star star: Star parameter container.
        """
        return list(model_instance.stars.values())[0]

    # @classmethod
    # def get_star_param_GP_names(cls, model_instance, free=False, full_name=False):
    #     """Return the list of the names of the paramaters of the GP model."""
    #     if full_name:
    #         return [param.get_name(include_prefix=True, recursive=True) for param in cls.get_star_params_GP(model_instance, free=free)]
    #     else:
    #         return [param.get_name() for param in cls.get_star_params_GP(model_instance, free=free)]

    @classmethod
    def get_star_params_GP(cls, model_instance, stelact_mod_name, free=False):
        """Return the list of GP parameters.

        Arguments
        ---------
        model_instance   : Core_Model subclass
            Instance of Core_Model or a subclass of it. Mandatory for noise models which requires parameter of the object studied (like GP and stellar activity)
        stelact_mod_name : String
            Name of the stellar activity model as provided in the stellar activity noise model parameter file
        free             : Boolean
            If True returns only the free parameters.

        Returns
        -------
        res : List of Parameter
            List of parameter object for the stellar activity model
        """
        star = cls.get_star(model_instance)
        res = []
        for param_GP_name in cls._star_param_GP_names:
            param_name = get_stelact_GP_param_name(param_GP_name=param_GP_name, stelact_mod_name=stelact_mod_name)
            param_obj = star.get_parameter(name=param_name, notexist_ok=False, return_error=False,
                                           kwargs_get_list_params={"no_duplicate": False},
                                           kwargs_get_name={'recursive': False, 'include_prefix': False, 'force_no_duplicate': True}
                                           )
            if free:
                if param_obj.free:
                    res.append(param_obj)
            else:
                res.append(param_obj)
        return res

    # @classmethod
    # def star_params_GP_isfree(cls, model_instance):
    #     """Return the list of boolean indicating if the GP parameters are free."""
    #     return [param.free for param in cls.get_star_params_GP(model_instance)]

    # @classmethod
    # def nb_params_GP_free(cls, model_instance):
    #     """Return the number of GP parameters that are free."""
    #     return len(cls.get_star_params_GP(free=True))

    @classmethod
    def __get_text_define_GP(cls, model_instance, l_params, l_params_noisemod, l_idx_param_noisemod,
                             stelact_mod_name, function_builder, function_shortname):
        """Return the text of the GP kernel, the list of all parameters and list of the idx of the noise model parameters

        Parameters
        ----------
        model_instance       : Core_Model
            Instance of Core_Model or a subclass of it. Mandatory for noise model which requires parameter of the object studied (like GP and stellar activity).
        l_params             : list_of_string
            Current list of parameters full names.
        l_params_noisemod    : list_of_string
            Current list of parameters full names for the noise model only.
        l_idx_param_noisemod : list_of_int
            List of the index of the noise model parameters in the updated list of parameters (l_params_new).
        stelact_mod_name     : String
            Name of the stellar activity model as provided in the stellar activity noise model parameter file

        Returns
        -------
        ker                   : String
            Text of the kernel. The index in the parameter array p are for the noise model parameter array only.
        l_params_new          : list_of_string
            Updated list of parameters full names.
        l_params_noisemod_new : list_of_string
            Updated list of parameters full names for the noise model
        l_idx_param_noisemod  : list_of_int
            List of the index of the noise model parameters in the updated list of parameters (l_params_new).
        """
        dico = {}
        l_params_new = l_params.copy()
        l_params_noisemod_new = l_params_noisemod.copy()
        l_idx_param_noisemod_new = l_idx_param_noisemod.copy()
        for param in cls.get_star_params_GP(model_instance, stelact_mod_name=stelact_mod_name):
            l_params_new, l_params_noisemod_new, l_idx_param_noisemod_new = cls._update_lists_params(l_params_lnlike=l_params_new, l_params_noisemod=l_params_noisemod_new, l_idx_param_noisemod=l_idx_param_noisemod_new, param_obj=param)
            function_builder.add_parameter(parameter=param, function_shortname=function_shortname, exist_ok=True)
            if param.free:
                idx_param_noisemod = l_params_noisemod_new.index(param.full_name)
                dico[param.get_name(force_no_duplicate=True)] = f"{param_noisemod_name}[{idx_param_noisemod}]"
            else:
                dico[param.get_name(force_no_duplicate=True)] = "{}".format(param.value)

        ker = cls.kernel_text.format(amp=dico[get_stelact_GP_param_name(param_GP_name=amp, stelact_mod_name=stelact_mod_name)],
                                     tau=dico[get_stelact_GP_param_name(param_GP_name=tau, stelact_mod_name=stelact_mod_name)],
                                     gamma=dico[get_stelact_GP_param_name(param_GP_name=gamma, stelact_mod_name=stelact_mod_name)],
                                     log_period=dico[get_stelact_GP_param_name(param_GP_name=logperiod, stelact_mod_name=stelact_mod_name)])

        return ker, l_params_new, l_params_noisemod_new, l_idx_param_noisemod_new

    @classmethod
    def __get_text_l_jitter(cls, l_instmod_obj, l_params, l_params_noisemod, l_idx_param_noisemod,
                            function_builder, function_shortname):
        """Return the text of the white noise array, the list of all parameters.

        Parameters
        ----------
        l_instmod_obj : InstrumentModel/list_of_InstrumentModel
            Instument model or list of instrument model for the ln likelihood to produce.
        l_params : List of string
            Current list of parameters full names for the full function (likelihood or GP simulator)
        l_params_noisemod : List of String
            Current list of parameters full names for the noise model only.
        l_idx_param_noisemod : List of int
            Lis of the indexes of the parameters provided by l_params_noisemod in l_params.

        Returns
        -------
        text_l_jitter : str
            Text giving the list of the indexes of the jitter parameters in the list of the noise model
            parameters for each instrument in the list of instrument models
        l_params_new : list_of_string
            Current list of parameters full names.
        """
        l_params_new = l_params.copy()
        l_params_noisemod_new = l_params_noisemod.copy()
        l_idx_param_noisemod_new = l_idx_param_noisemod.copy()
        l_jitter_paramname = []
        text_l_jitter = "["
        for instmod_obj in l_instmod_obj:
            jitter_param = instmod_obj.parameters[jitter_name]
            l_jitter_paramname.append(jitter_param.get_name(include_prefix=True, recursive=True))
            (l_params_new, l_params_noisemod_new,
             l_idx_param_noisemod_new) = cls._update_lists_params(l_params_new, l_params_noisemod_new,
                                                                  l_idx_param_noisemod_new, jitter_param)
            function_builder.add_parameter(parameter=jitter_param, function_shortname=function_shortname, exist_ok=True)

            # I commented the stuff below because I think that cls._update_lists_params does all that already. If there is no error when I run it it's because it's True.
            # if jitter_param.free:
            #     if jitter_param.get_name(include_prefix=True, recursive=True) not in l_params_new:
            #         (l_params_new, l_params_noisemod_new,
            #          l_idx_param_noisemod_new) = cls._update_lists_params(l_params_new, l_params_noisemod_new,
            #                                                               l_idx_param_noisemod_new, jitter_param)
            #     if jitter_param.get_name(include_prefix=True, recursive=True) not in l_params_noisemod_new:
            #         l_params_noisemod_new.append(jitter_param.get_name(include_prefix=True, recursive=True))
            #         l_idx_param_noisemod_new.append(l_params_new.index(jitter_param.get_name(include_prefix=True, recursive=True)))
            if jitter_param.free:
                text_l_jitter += f"{param_noisemod_name}[{l_params_noisemod_new.index(jitter_param.get_name(include_prefix=True, recursive=True))}], "
            else:
                text_l_jitter += f"{jitter_param.value}, "
        text_l_jitter += "]"
        return text_l_jitter, l_params_new, l_params_noisemod_new, l_idx_param_noisemod_new, l_jitter_paramname

    @classmethod
    def create_gpsimulator_and_formatinputs(cls, model_instance, l_instmod_obj, l_dataset_obj, l_datasim_param_fullname,
                                            l_provided_param_fullname):
        """Create the prefilled gp_simulator function (without the datasim) for the dataset provided and provide the function to format the inputs

        This function might not be convenient for your noise model, in wich case you should overload it.

        The these output are then used by emcee_tools.compute_model function
        to compute the model of the dataset. In this function the gp simulator is used as follow:
        gp_sim_function(sim_data=sim_data,
                        param_noisemod=f_format_param(p),
                        l_datakwargs=datasets_kwargs,
                        tsim=tsim)

        Arguments
        ---------
        model_instance            : Core Model subclass
        l_instmod_obj             : list of Instrument_Model instances
            List of instrument model objects that are used for the sim_data elements using this noise model (whose indexes are given by l_idx_datasim).
        l_dataset_obj             : list of Dataset instances
            List of dataset objects that are simulated by the sim_data elements using this noise model (whose indexes are given by l_idx_datasim).
        l_datasim_param_fullname  : list of String
            Current list of parameter full names for the likelihood.
        l_provided_param_fullname : list of String
            List of the full name of all provided parameters

        Returns
        -------
        gpsimulator_function  : function
            function with the following arguments
                sim_data         : sim_data using this noise model, and only these, the exact format is defined by f_format_simdata
                param_noisemodel : param of the current noise model, and only these, the exact format is defined by f_format_param
                dataset_kwargs   : dataset keyword arguments used by this noise model, and only these, the exact format is defined by this function.
        f_format_param   : function
            Function to extract and format the parameter of this noise model from the vector of all the parameters of the likelihood function
        datasets_kwargs  : ??
            Dataset keyword arguments of the datasets using this noise model
        l_datasim_param_fullname_new : list of String
            New list of parameter full names for the likelihood which the l_likelihood_param_fullname +  the parameters for this noise model
        """
        func_builder = FunctionBuilder()
        func_shortname = "gp_simulator"
        parameters = [model_instance.get_parameter(name=param_fullname, notexist_ok=False, return_error=False,
                                                   kwargs_get_list_params={'main': True, 'free': True, 'no_duplicate': True, 'recursive': True},
                                                   kwargs_get_name={'recursive': True, 'include_prefix': True})
                      for param_fullname in l_datasim_param_fullname]
        func_builder.add_new_function(shortname=func_shortname, parameters=parameters,
                                      mandatory_args=None, optional_args=None, full_function_name=None)
        (gp_simulator, l_params_new, params_noisemod, l_idx_param_noisemod
         ) = cls.get_gp_simulator(l_params=l_datasim_param_fullname, model_instance=model_instance,
                                  l_instmod_obj=l_instmod_obj, function_builder=func_builder, function_shortname=func_shortname)

        l_idx_param_noisemod_in_all_param = [l_provided_param_fullname.index(param_noisemod_name_ii) for param_noisemod_name_ii in params_noisemod]

        def f_format_param(all_param):
            return all_param[l_idx_param_noisemod_in_all_param]

        dataset_kwargs = []
        for dataset in l_dataset_obj:
            dataset_kwargs.append({datasetkwarg: dataset.get_datasetkwarg(datasetkwarg) for datasetkwarg in cls.l_required_datasetkwarg_keys})

        return gp_simulator, f_format_param, dataset_kwargs, l_params_new

    # TODO: Adapt to the possibility of several stellar activity noise model. I DON'T THINK THAT I NEED TO BECAUSE THIS IS ONLY FOR DISPLAY PRUPOSES AND I CAN ASK NOISE MODEL PAR NOISE MODEL
    @classmethod
    def get_gp_simulator(cls, l_params, model_instance, l_instmod_obj, function_builder, function_shortname):
        """Return the simulated values with the GP at given simulated times.

        Arguments
        ---------
        l_params : List of String
            Current list of parameters full names.
        model_instance    : Core_Model subclass
            Instance of Core_Model or a subclass of it. Mandatory for
            noise model which requires parameter of the object studied (like GP and stellar
            activity).
        l_instmod_obj     : List of Instrument_Model
            List of instrument model object corresponding to the datasets simulated with the data simulator this gp simulator is associated with.

        Returns
        -------
        gp_sim : function
            gp simulator function that return the simulated gp contributions.
        l_params_new          : list of String
            Updated list of parameters full names.
        l_params_noisemod_new : list of String
            List of the noise model parameters
        l_idx_param_noisemod  : list of Integer
            List of the index of the noise model parameters in the updated list of parameters (l_params_new).
        """
        l_stelact_mod_name = []
        for instmod_obj in l_instmod_obj:
            l_stelact_mod_name.append(model_instance.modelstelactname_4_instmodfullname[instmod_obj.full_name])
        assert len(set(l_stelact_mod_name)) == 1, "All instrument model object should have the stellar activity noise model"
        stelact_noisemodel_name = set(l_stelact_mod_name).pop()

        ldict = {}
        l_params_new = l_params.copy()
        (ker, l_params_new,
         l_params_noisemod,
         l_idx_param_noisemod) = cls.__get_text_define_GP(model_instance=model_instance, l_params=l_params_new,
                                                          l_params_noisemod=[], l_idx_param_noisemod=[],
                                                          stelact_mod_name=stelact_noisemodel_name,
                                                          function_builder=function_builder, function_shortname=function_shortname)
        (text_l_jitter,
         l_params_new,
         l_params_noisemod,
         l_idx_param_noisemod,
         l_jitter_paramname) = cls.__get_text_l_jitter(l_instmod_obj=l_instmod_obj, l_params=l_params_new,
                                                       l_params_noisemod=l_params_noisemod,
                                                       l_idx_param_noisemod=l_idx_param_noisemod,
                                                       function_builder=function_builder, function_shortname=function_shortname)
        func = cls.gpsim_func_text.format(func_name=cls.gpsim_function_name, param_noisemod_name=param_noisemod_name, kernel=ker, text_l_jitter=text_l_jitter)
        ldict["defaultdict"] = defaultdict
        ldict["list"] = list
        ldict["concatenate"] = concatenate
        ldict["logger"] = logger
        ldict["ExpSquaredKernel"] = ExpSquaredKernel
        ldict["ExpSine2Kernel"] = ExpSine2Kernel
        ldict["GP"] = GP
        ldict["sqrt"] = sqrt
        ldict["np"] = np
        exec(func, ldict)
        return ldict[cls.gpsim_function_name], l_params_new, l_params_noisemod, l_idx_param_noisemod

    # @classmethod
    # def star_param_GP_indexorval(cls, model_instance, l_params):
    #     """Return
    #
    #     :param Core_Model model_instance: Instance of Core_Model or a subclass of it. Mandatory for
    #         noise model which requires parameter of the object studied (like GP and stellar
    #         activity)
    #     :param list_of_string l_params: Current list of parameters full names.
    #     :return list_of_string_or_float l:
    #     """
    #     i = 0
    #     l_params_new = l_params.copy()
    #     for param in cls.get_star_params_GP(model_instance):
    #         if param.free:
    #             if param not in l_params_new:
    #                 l_params_new.append(param.get_name(include_prefix=True, recursive=True))
    #             i += 1
    #         else:
    #             l.append(param.value)
    #     return l

    # @classmethod
    # def __define_GP(cls, p, model_instance):
    #     l_val = [p[idxorval] if free else idxorval
    #              for idxorval, free in zip(cls.star_param_GP_indexorval(model_instance),
    #                                        cls.star_params_GP_isfree(model_instance))]
    #     kernel = (exp(l_val[0])**2.0 * ExpSquaredKernel(l_val[1]**2) *
    #               ExpSine2Kernel(2. / (l_val[2])**2.0, l_val[3]))
    #     return GP(kernel)  # Define the kernel of the GP

    # def lnlike_creator(self):
    #     ldict = locals().copy()
    #     nb_free = self.nb_params_GP_free
    #     ker = self.__get_text_define_GP()
    #     if self.multidataset:
    #         l_idx_param = []
    #         for dataset in self.l_dataset:
    #             l_idx_param.append(self.get_param_idxs_datasim(dataset))
    #         ldict["l_idx_param"] = l_idx_param
    #         ldict["l_func"] = [self.get_datasim_function(dataset) for dataset in self.l_dataset]
    #         ldict["concatenate"] = concatenate
    #         ldict["logger"] = logger
    #         text_func = self.lnlikefunc_text_multidataset
    #     else:
    #         datasim_func = self.get_datasim_function()
    #         ldict["datasim_func"] = datasim_func
    #         text_func = self.lnlikefunc_text
    #     func = text_func.format(func_name=self.function_name, nb_GP_free_param=nb_free, kernel=ker)
    #     ldict["ExpSquaredKernel"] = ExpSquaredKernel
    #     ldict["ExpSine2Kernel"] = ExpSine2Kernel
    #     ldict["exp"] = exp
    #     ldict["GP"] = GP
    #     exec(func, ldict)
    #     return DocFunction(function=ldict[self.function_name], arg_list=self.get_arg_list())

    # def lnlike(self, p, data, data_err, t):
    #     if self.multidataset:
    #         model = []
    #         for dataset_key, t_dataset in zip(self.l_dataset, t):
    #             model.append(self.get_datasim_function(dataset_key)
    #                          (p[self.get_param_idxs_datasim(dataset_key)], t_dataset))
    #         gp = self.__define_GP(p[self.get_param_idxs_GP()])
    #         gp.compute(concatenate(t), concatenate(data_err))
    #         return gp.lnlikelihood(concatenate(data) - concatenate(model))
    #     else:
    #         model = self.get_datasim_function()(p[self.get_param_idxs_datasim()], t)
    #         gp = self.__define_GP(p[self.get_param_idxs_GP()])
    #         gp.compute(t, data_err)  # Pre-compute the factorization of the matrix.
    #         return gp.lnlikelihood(data - model)

    # def _get_arg_list_one_dataset(self, dataset_key=None):
    #     arg_list_new = super(StellarActNoiseModel,
    #                          self)._get_arg_list_one_dataset(dataset_key)
    #     arg_list_new["param"] = (self.get_star_param_GP_names(free=True, full_name=True) +
    #                              arg_list_new["param"])
    #     return arg_list_new

    # def gp_simulator(self, p, tsim, data, data_err, t):
    #     """
    #     """
    #     if self.multidataset:
    #         model = []
    #         for dataset_key, t_dataset in zip(self.l_dataset, t):
    #             model.append(self.get_datasim_function(dataset_key)
    #                          (p[self.get_param_idxs_datasim(dataset_key)], t_dataset))
    #         gp = self.__define_GP(p[self.get_param_idxs_GP()])
    #         gp.compute(concatenate(t), concatenate(data_err))
    #         return gp.sample_conditional(concatenate(data) - concatenate(model), tsim)
    #     else:
    #         model = self.get_datasim_function()(p[self.get_param_idxs_datasim()], t)
    #         gp = self.__define_GP(p[self.get_param_idxs_GP()])
    #         gp.compute(t, data_err)  # Pre-compute the factorization of the matrix.
    #         return gp.sample_conditional(data - model, tsim)

    # def get_param_idxs_datasim(self, dataset_key=None):
    #     """Return the list of param indexes for a datasimulator.
    #
    #     If multidataset dataset_key should not be None, because then you should do it for each
    #     dataset.
    #     """
    #     # Get list of param names for the likelihood then for the datasimulator and final get the
    #     # list of indexes for the datasimulator params
    #     l_param_all = self.get_arg_list()["param"]
    #     l_idx_param = []
    #     for par in self.get_datasim_arg_list(dataset_key)["param"]:
    #         l_idx_param.append(l_param_all.index(par))
    #     return l_idx_param

    # def get_param_idxs_GP(self):
    #     """Return the list of param indexes for the GP model."""
    #     # Get list of param names for the likelihood then for the datasimulator and final get the
    #     # list of indexes for the datasimulator params
    #     l_param_all = self.get_arg_list()["param"]
    #     l_idx_param = []
    #     for par in self.get_star_param_GP_names(free=True, full_name=True):
    #         l_idx_param.append(l_param_all.index(par))
    #     return l_idx_param


class StellarActivityNoiseModelInterface(object):
    """docstring for StellarActivityNoiseModelInterface."""

    # String giving the name of the dictionary used to define the model to use for each indicator in the parameter file
    __name_modelstelact_4_instmodfullname = "model_4_instmodfullname"

    # String for the default model name for stellar activity noise model
    __def_stellar_activity_noisemod_name = "SA"

    def __init__(self):
        self.__modelSAname_4_instmodfullname = {}
        self.__modelSA_def = {}

        # Update the applyparametrisation4noisemodel dictionary
        self.applyparametrisation4noisemodel[stelact_GP_noisemodel] = self.apply_parametrisation_stelact_noisemod  # applyparametrisation4noisemodel is created in Core_Parametrisation

        # Update the _same_GP_kernel_function dictionary
        self._same_GP_kernel_function[stelact_GP_noisemodel] = self._get_same_GP_kernel_instmodel_stelact_noisemodel

    @property
    def modelstelactname_4_instmodfullname(self):
        """Dictionary giving the stellar activity for each instrument model full name using the stellar activity model

        key : instrument model full name
        values : String giving the name of the stellar activity noise model to use.
        """
        for inst_mod_obj in self.inst_model_objects:
            if inst_mod_obj.noise_model == stelact_GP_noisemodel:
                inst_mod_fullname = inst_mod_obj.get_name(include_prefix=True, recursive=True)
                if inst_mod_fullname not in self.__modelSAname_4_instmodfullname:
                    self.__modelSAname_4_instmodfullname[inst_mod_fullname] = self.__def_stellar_activity_noisemod_name
        return self.__modelSAname_4_instmodfullname

    @property
    def modelstelact_def(self):
        """Dictionary giving the definition of the stellar activity noise models

        key : stellar activity noise model name
        values :  Dictionary giving the parameters of the stellar activity models.
        """
        for SA_mod_name in self.model_stelact_names:
            if SA_mod_name not in self.__modelSA_def:
                self.__modelSA_def[SA_mod_name] = {}
        return self.__modelSA_def

    @property
    def model_stelact_names(self):
        """List of the stellar activity model names used.

        key : instrument model full name
        values :  String giving the name of the stellar activity noise model to use.
        """
        return list(set(self.modelstelactname_4_instmodfullname.values()))

    @property
    def isdefined_SANMparamfile(self):
        """Return True is the attribute param_file has been defined."""
        return self.isdefined_paramfile_noisemod(stelact_GP_noisemodel)  # isdefined_paramfile_noisemod is defined in Core_Model

    def create_SANM_param_file(self, paramfile_name=None, answer_overwrite=None, answer_create=None):
        """Create the parameter file for the definition of the stellar activity noise model.

        Arguments
        ---------
        paramfile_name   : str
            Path to the stellar activity noise model parameter file (SANM_param_file).
        answer_overwrite : str
            If the SANM_param_file already exists, do you want to
            overwrite it ? "y" or "n". If this is not provided the program will ask you interactively.
        answer_create    : str
            If the SANM_param_file doesn't exists already, where do you want
            to create it ? "absolute", "run_folder" or "error". If this not provide the program will ask you interactively.
        """
        # Choose the parameter file path _choose_parameter_file_path is from Core_Model
        file_path, reply = self._choose_parameter_file_path(default_paramfile_name='SANM_param_file.py', paramfile_name=paramfile_name, answer_overwrite=answer_overwrite, answer_create=answer_create)
        if reply == "y":
            with open(file_path, 'w') as f:
                # Write the header
                f.write("#!/usr/bin/python\n# -*- coding:  utf-8 -*-\n")
                # Put modelstelactname_4_instmodfullname dictionary
                f.write(self.__create_text_modelstelactname_4_instmodfullname())
                # Put the models definition directories
                f.write(self.__create_text_modelstelact_def_directories())
            logger.info("Parameter file for the stellar activity noise model created at path: {}".format(file_path))
        else:
            logger.info("Parameter file for the stellar activity noise model already existing and not overwritten: {}".format(file_path))
        self.paramfile4noisemodcat[stelact_GP_noisemodel] = basename(file_path)  # paramfile4noisemodcat is from Core_Model

    def read_SANM_param_file(self):
        """Read the content of the Stellar activity noise model parameter file."""
        if self.isdefined_SANMparamfile:
            paramfile_noisemod = self.paramfile4noisemodcat[stelact_GP_noisemodel]
            cwd = os.getcwd()
            os.chdir(self.run_folder)
            dico = {}
            with open(paramfile_noisemod) as f:
                exec(f.read(), dico)
            os.chdir(cwd)
            dico.pop('__builtins__')
            logger.debug(f"SANM parameter file read.\nContent of the parameter file: {dico.keys()}")
            return dico
        else:
            raise IOError("Impossible to read SANM parameter file: {}".format(self.paramfile4instcat[IND_inst_cat]))

    def load_SANM_param_file(self, answer_recreate=None):
        """Load the parameter file specific to the stellar activity noise model.
        """
        assert len(self.model_stelact_names) > 0, "There should be a model used by default."
        missing_usedmodel_dict_name = self.model_stelact_names
        unnecessary_model_dict_name = []
        while (len(missing_usedmodel_dict_name) > 0) or (len(unnecessary_model_dict_name)):
            dico_config = self.read_SANM_param_file()
            missing_usedmodel_dict_name, unnecessary_model_dict_name, dict_valid, error_list = self.__check_SANM_param_file(dico_config)
            if len(error_list) > 0:
                inconsistency = True
                logger.warning(f"The following errors have been spotted in the stellar activity parameter file: {error_list}")
            else:
                inconsistency = False
            if dict_valid[self.__name_modelstelact_4_instmodfullname]:
                self.__load_modelstelactname_4_instmodfullname(dico_config[self.__name_modelstelact_4_instmodfullname])
                # Remove unused stellar activity model name from self.modelstelact_def
                used_stelact_mod_name = {mod_name: mod_name in self.model_stelact_names for mod_name in self.modelstelact_def.keys()}
                for mod_name, used in used_stelact_mod_name.items():
                    if not used:
                        self.modelstelact_def.pop(mod_name)
            dict_valid.pop(self.__name_modelstelact_4_instmodfullname)
            for model, valid in dict_valid.items():
                if valid:
                    self.__load_modelstelact_def(model_stelact_name=model, dict_def_SA_model=dico_config[model])
            if len(missing_usedmodel_dict_name) > 0:
                logger.warning(f"The dictionary to parametrize the following stellar activity models are missing in the stellar activity parameter file: {missing_usedmodel_dict_name}")
                inconsistency = True
            if len(unnecessary_model_dict_name) > 0:
                logger.warning(f"There is unnecessary objects defined in the stellar activity parameter file: {unnecessary_model_dict_name}")
                inconsistency = True
            if inconsistency:
                l_answers = ['y', 'n']
                if answer_recreate is None:
                    rep = QCM_utilisateur(f"There is some inconsistencies in the stellar activity parameter file (see warnings above). Do you want to recreate it from current valid inputs ? {l_answers}. 'n' would mean triggering an error\n", l_answers)
                else:
                    if answer_recreate not in l_answers:
                        raise ValueError(f"The provided answer_recreate is not valid. Should be in {l_answers}, got {answer_recreate}")
                    else:
                        rep = answer_recreate
            else:
                rep = "n"
            if inconsistency and (rep == "n"):
                raise ValueError(f"The content of the stellar activity parameter file is not valid. Here is the list of detected errors: {error_list}")
            elif inconsistency and (rep == "y"):
                self.create_SANM_param_file(paramfile_name=self.paramfile4noisemodcat[stelact_GP_noisemodel], answer_overwrite="y", answer_create=None)
                input("Modify the SANM specific paramerisation file: {}".format(self.paramfile4noisemodcat[stelact_GP_noisemodel]))

    def __create_text_modelstelactname_4_instmodfullname(self, text_tab="", entete_symb=" = "):
        """Create the string giving the model_4_instfullcat dictionary for the parameter file.

        Arguments
        ---------
        text_tab    : str
            Space composed only of spaces to be put at the beginning of each new line
        entete_symb : str
            Entete symbol to put in between the dictionary name and the dictionary definition (typically either ' = ' or ': ')

        Returns
        -------
        text : str
            String giving the text for the model_4_instfullcat dictionary for the stellar activity noise model parameter file.
        """
        text = f"{text_tab}# Define the names of stellar activity model to use for each instrument model.\n# You can use whatever name you want as long as you are not using '_' in the name.\n# The same name implies that a common GP matrix will be used.\n"
        text_entete = f"{text_tab}{self.__name_modelstelact_4_instmodfullname}{entete_symb}{{"
        tab = text_tab + spacestring_like(text_entete)
        text += text_entete
        first = True
        for inst_mod_fullname, SA_mod_name in self.modelstelactname_4_instmodfullname.items():
            if not first:
                text += f"\n{tab}"
            else:
                first = False
            text += f"'{inst_mod_fullname}': '{SA_mod_name}',"
        text += f"\n{tab}}}\n"
        return text

    def __load_modelstelactname_4_instmodfullname(self, modelstelactname_4_instmodfullname):
        """Load the modelstelactname_4_instmodfullname dictionary of the parameter file.

        Arguments
        ---------
        modelstelactname_4_instmodfullname : Dictionary
            Dictionary modelstelactname_4_instmodfullname as read from the indicator parameter file.
        """
        self.__modelSAname_4_instmodfullname = modelstelactname_4_instmodfullname

    def __create_text_modelstelact_def_directories(self, text_tab="", entete_symb=" = ", sep_entries="\n"):
        """Create the string giving the modelstelact_def dictionaries for the parameter file.

        Arguments
        ---------
        text_tab    : str
            Space composed only of spaces to be put at the beginning of each new line
        entete_symb : str
            Entete symbol to put in between the dictionary name and the dictionary definition (typically either ' = ' or ': ')

        Returns
        -------
        text : str
            String giving the text for the dictionaries defining each stellar activity models
        """
        text = f"{text_tab}# Define the parameters of the different stellar activity models whose name have been provided in modelstelactname_4_instmodfullname\n# For now there is no parameters for the stellar activity models (there will be later). So the dictionaries should stay empty.\n"
        for stelact_mod_name, dict_def in self.modelstelact_def.items():
            text += f"{text_tab}{stelact_mod_name}{entete_symb}{dict_def}\n"
        return text

    def __load_modelstelact_def(self, model_stelact_name, dict_def_SA_model):
        """Load the polynomail model

        Arguments
        ---------
        model_stelact_name : String
            Name of the stellar activity model to be loaded
        dic_def_SA_model   : dictionary
            Dictionary parametrizing a stellar activity model as read from the indicator parameter file.
        """
        self.modelstelact_def[model_stelact_name] = dict_def_SA_model

    def __check_SANM_param_file(self, dico_config):
        """Check that the content of the param file for stellar activity noise model.

        Check that all the necessary object are here, that they are properly defined and that all is consistent.
        1. Check that the odelstelactname_4_instmodfullname dictionary is there (if not -> AssertionError)
        2. Check its content (if content not valid -> AssertionError):
        3. Check if all used models have there definition dictionary. If not return in missing_usedmodel_dict the list of missing model directories
        4. Check if there is additional dictionaries or variables that should not be here. If yes return the list in unnecessary_model_dict
        5. Check that each used models dictionary is correctly defined.
            a. For now dict should be empty so check that they are.

        Arguments
        ---------
        dico_config : dictionary
            Dictionary providing the content of the stellar activity parameter file.

        Returns
        -------
        missing_usedmodel_dict_name : list of strings
            Name of the missing dictionary definitions
        unnecessary_model_dict_name : list of strings
            Name of the unnecessary variables defined
        dict_valid            : dictionary of boolean
            keys are model names or self.__name_model_4_indicator_dict and values boolean which indicates is the if the definition is valid.
        error_list                  : list of string
            List of errors detected
        """
        error_list = []
        dict_valid = {}
        # 1.
        if not(self.__name_modelstelact_4_instmodfullname in dico_config):
            error_list.append(f"{self.__name_modelstelact_4_instmodfullname} should be defined in the stellar activity parameter file. Defined objects are {list(dico_config.keys())}.")
        # 2
        dict_valid[self.__name_modelstelact_4_instmodfullname], errors = self.__check_modelstelact_4_instmodfullname(dico_config[self.__name_modelstelact_4_instmodfullname])
        error_list.extend(errors)
        # 3 and 4.
        missing_usedmodel_dict_name = list(set(dico_config[self.__name_modelstelact_4_instmodfullname].values()))
        model_dict_names_defined = list(dico_config.keys())
        model_dict_names_defined.remove(self.__name_modelstelact_4_instmodfullname)
        unnecessary_model_dict_name = []
        nessecary_model_dict_name = []
        for model_dict in model_dict_names_defined:
            if model_dict in missing_usedmodel_dict_name:
                missing_usedmodel_dict_name.remove(model_dict)
                nessecary_model_dict_name.append(model_dict)
            else:
                unnecessary_model_dict_name.append(model_dict)
        # 5.
        for model_dict_name in nessecary_model_dict_name:
            dict_valid[model_dict_name], errors = self.__checker_stelact_model_def_dict(dict_model=dico_config[model_dict_name])
            error_list.extend(errors)
        return missing_usedmodel_dict_name, unnecessary_model_dict_name, dict_valid, error_list

    def __check_modelstelact_4_instmodfullname(self, modelstelact_4_instmodfullname):
        """Validate the modelstelact_4_instmodfullname dictionary of the parameter file.

        1. Check that full names of all instrument model using the stellar activity noise model and only these are keys of this dictionary
        2. Check that the associated values are strings.

        Arguments
        ---------
        modelstelact_4_instmodfullname : Dictionary
            Dictionary modelstelact_4_instmodfullname as read from the indicator parameter file.

        Returns
        -------
        valid      : boolean
            Say if the content of modelstelact_4_instmodfullname is valid
        error_list : list of string
            List of error detected
        """
        error_list = []
        # 1.
        if Counter(list(modelstelact_4_instmodfullname.keys())) != Counter(self.modelstelactname_4_instmodfullname.keys()):
            error_list.append(f"There is an inconsistency in between the list of instrument models using the stellar activity noise model ({self.modelstelactname_4_instmodfullname.keys()}) and the list of keys in the dictionary {self.__name_modelstelact_4_instmodfullname}.")
        # 2.
        for instmod_fullname, model_name in modelstelact_4_instmodfullname.items():
            if not isinstance(model_name, str):
                error_list.append(f"Stellar activity model name ({model_name}) provided for instrument model full name {instmod_fullname} should be a string.")
        return len(error_list) == 0, error_list

    def __checker_stelact_model_def_dict(self, dict_model):
        """Check the content of a stellar activity model definition dictionary.
        """
        error_list = []
        if len(dict_model) != 0:
            error_list.append(f"The stellar activity model definition dictionary should be empty, got {dict_model}.")
        return len(error_list) == 0, error_list

    def apply_parametrisation_stelact_noisemod(self):
        """Create the parameters required by the stellar activity models.
        """
        # Get the star object.
        star = self.stars[list(self.stars.keys())[0]]
        # Create a dictionary to make sure that you don't do the parametrisation of a stellar activity model several times.
        dico_model_SA_done = {SA_mod_name: False for SA_mod_name in self.model_stelact_names}
        for instmod_fullname in self.get_instmodfullnames_using_noisemod(noisemod_cat=StellarActNoiseModel.category):
            inst_model_obj = self.instruments[instmod_fullname]
            inst = inst_model_obj.instrument
            inst_cat = inst.category
            # Check that the instrument is from a category allowed for the noise model
            if inst_cat not in StellarActNoiseModel._allowed_inst_cat:
                raise ValueError(f"Stellar activity noise model can only be used for instrument category "
                                 f"{StellarActNoiseModel._allowed_inst_cat}, got {inst_cat}."
                                 )
            # Do the jitter noise model parametrisation
            GaussianNoiseModel_wjitteradd.apply_parametrisation(model_instance=self, instmod_fullname=instmod_fullname)
            # Get the stellar activity model name for the instruments
            SA_mod_name = self.modelstelactname_4_instmodfullname[instmod_fullname]
            # If not already done, do the parametrisation for this stellar activity model.
            if not(dico_model_SA_done[SA_mod_name]):
                for param_GP_name in StellarActNoiseModel._star_param_GP_names:
                    # Commented because I dont' think that it's needed. TBC
                    # if star.has_parameter(name=param_name):
                    #     param = star.get_parameter(name=param_name)
                    #     if not param.main:
                    #         param.main = True
                    # else:
                    param_name = get_stelact_GP_param_name(param_GP_name=param_GP_name, stelact_mod_name=SA_mod_name)
                    star.add_parameter(Parameter(name=param_name, name_prefix=star.name, main=True))

    def _get_same_GP_kernel_instmodel_stelact_noisemodel(self, instmod_fullname):
        """Get the list of the instrument full names modeled by the same GP kernel than the provided one.

        Arguments
        ---------
        instmod_fullname : String
            Full name of the instrument of interest

        Returns
        -------
        l_instmod_fullname : List of String
            List of instrument model full names using the same stellar activity noise model than instmod_fullname
        """
        stelact_noisemodel = self.modelstelactname_4_instmodfullname[instmod_fullname]
        return self.get_linstmodfullname4stelactname(stelact_noisemod_name=stelact_noisemodel)

    def get_linstmodfullname4stelactname(self, stelact_noisemod_name):
        """Provide the list instrument model using a given stellar activity model

        Arguments
        ---------
        stelact_noisemod_name : String
            Name of the stellar activity noise model of interest

        Returns
        -------
        l_instmod_fullname : List of String
            List of instrument model full names using the stellar activity noise model provided
        """
        res = []
        for instmod_fullname_ii, stelact_noisemodel_ii in self.modelstelactname_4_instmodfullname.items():
            if stelact_noisemodel_ii == stelact_noisemod_name:
                res.append(instmod_fullname_ii)
        return res
