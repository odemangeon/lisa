"""
Prior functions module.
"""
from __future__ import division
from logging import getLogger
from textwrap import dedent

from numpy import pi, inf, ones, where, any, arange, nan, array, abs  # logical_or

from ...core.prior.core_prior import Core_JointPrior_Function
from ....posterior.exoplanet.model.convert import getecc_plb_4_handk_fast, getecc_plc_4_handk_fast, getomega_plb_4_handk_fast, getomega_plc_4_handk_fast
from ....posterior.exoplanet.model.convert import gethplus, gethminus, getkplus, getkminus, getaoverr
from ....tools.function_w_doc import DocFunction
from ....tools.function_from_text_toolbox import init_arglist_paramnb_arguments_ldict, add_param_argument, par_vec_name, key_param, get_function_arglist


## logger object
logger = getLogger()


class HKPPrior(Core_JointPrior_Function):
    """Prior defined for the h, k and P parameters of the Np parametrisation of the GravgroupsDynam model.
    """

    __category__ = "hkP"
    __mandatory_args__ = []
    __extra_args__ = []
    __default_extra_args__ = {}
    __hidden_param_refs__ = ['Pb', 'Pc', 'eb', 'ec', 'omegab', 'omegac']
    __multiple_hidden_params__ = [False, False, False, False, False, False]
    __default_hidden_priors__ = {"Pb": {"category": "jeffreys", "args": {"vmin": 0.01, "vmax": 1000.}},
                                 "Pc": {"category": "jeffreys", "args": {"vmin": 0.01, "vmax": 1000.}},
                                 "eb": {"category": "uniform", "args": {"vmin": 0., "vmax": 1.}},
                                 "ec": {"category": "uniform", "args": {"vmin": 0., "vmax": 1.}},
                                 "omegab": {"category": "uniform", "args": {"vmin": -pi, "vmax": pi}},
                                 "omegac": {"category": "uniform", "args": {"vmin": -pi, "vmax": pi}}
                                 }
    __param_refs__ = ['hplus', 'hminus', 'kplus', 'kminus', 'Pb', 'Pc']
    __multiple_params__ = [False, False, False, False, False, False]

    def create_logpdf(self, params):
        """Return the logarithmic probability density function for the joint prior.

        :param dict params: Dictionnary which contains the Parameter instances required by the prior.
            The keys are parameter keys in the self.param_refs list and the values are the parameter instances
            as associated in the parameter file.
        :return function logpdf: log pdf the order in which the parameter should be provided is
            provided by self.param_refs
        """
        (param_nb,
         arg_list,
         param_vector_name,
         ldict) = init_arglist_paramnb_arguments_ldict(key_param=key_param, param_vector_name=par_vec_name)
        dico_logpdf = {param: priorfunc.create_logpdf() for param, priorfunc in self.priorinstance_hiddenparams.items()}
        ldict["dico_logpdf"] = dico_logpdf
        ldict["getecc_plb_4_handk_fast"] = getecc_plb_4_handk_fast
        ldict["getecc_plc_4_handk_fast"] = getecc_plc_4_handk_fast
        ldict["getomega_plb_4_handk_fast"] = getomega_plb_4_handk_fast
        ldict["getomega_plc_4_handk_fast"] = getomega_plc_4_handk_fast
        ldict["inf"] = inf
        dico_text_params = {}
        for param_key in self.param_refs:
            dico_text_params[param_key] = add_param_argument(param=params[param_key], arg_list=arg_list, key_param=key_param,
                                                             param_nb=param_nb, param_vector_name=par_vec_name)
        function_name = "logpdf_{}".format(self.category)
        text_function = """
        def {function_name}({param_vector_name}):
            if {Pc}/{Pb} < 1:
                return -inf
            eb = getecc_plb_4_handk_fast({hplus}, {hminus}, {kplus}, {kminus}, {Pc}/{Pb})
            ec = getecc_plc_4_handk_fast({hplus}, {hminus}, {kplus}, {kminus})
            omegab = getomega_plb_4_handk_fast({hplus}, {hminus}, {kplus}, {kminus})
            omegac = getomega_plc_4_handk_fast({hplus}, {hminus}, {kplus}, {kminus})
            return (dico_logpdf["Pb"]({Pb}) + dico_logpdf["Pc"]({Pc}) + dico_logpdf["eb"](eb) + dico_logpdf["ec"](ec) +
                    dico_logpdf["omegab"](omegab) + dico_logpdf["omegac"](omegac))
        """
        text_function = dedent(text_function)
        text_function = text_function.format(function_name=function_name, param_vector_name=par_vec_name,
                                             hplus=dico_text_params["hplus"], hminus=dico_text_params["hminus"],
                                             kplus=dico_text_params["kplus"], kminus=dico_text_params["kminus"],
                                             Pb=dico_text_params["Pb"], Pc=dico_text_params["Pc"])
        logger.debug("text of joint prior {category}:\n{text_func}"
                     "".format(category=self.category, text_func=text_function))
        logger.debug("Parameters for joint prior {category}:\n{dico_param}"
                     "".format(category=self.category, dico_param={nb: param for nb, param in enumerate(get_function_arglist(arg_list)[key_param])}))
        exec(text_function, ldict)
        return DocFunction(ldict[function_name], get_function_arglist(arg_list))

    def logpdf(self, hplus, hminus, kplus, kminus, Pb, Pc):
        dico_logpdf = self.priorinstance_hiddenparams

        eb = getecc_plb_4_handk_fast(hplus, hminus, kplus, kminus, Pc / Pb)
        ec = getecc_plc_4_handk_fast(hplus, hminus, kplus, kminus)
        omegab = getomega_plb_4_handk_fast(hplus, hminus, kplus, kminus)
        omegac = getomega_plc_4_handk_fast(hplus, hminus, kplus, kminus)
        return (dico_logpdf["Pb"](Pb) + dico_logpdf["Pc"](Pc) + dico_logpdf["eb"](eb) + dico_logpdf["ec"](ec) +
                dico_logpdf["omegab"](omegab) + dico_logpdf["omegac"](omegac))

    def ravs(self, nb_values=1):
        """Return values of the parameters drawn from the joint prior.

        :param int nb_values: Number of values to draw for each parameter.
        :return tuple_of_float/ nb_values: Tuple for which each element contains the value(s) drawn
            for each parameter. If nb_values = 1, it's just a float, otherwise it's an np.array.
            The order of the parameters in the tuple is provided by self.param_refs.
        """
        dico_ravs = {}
        for param, dico in self.hiddenparam_defs.items():
            value = dico.get("value", None)
            if value is None:
                dico_ravs[param] = dico["priorfunc_instance"].ravs(nb_values=nb_values)
            else:
                dico_ravs[param] = ones(nb_values) * value
            if dico_ravs[param].size == 1:
                dico_ravs[param] = dico_ravs[param][0]
        hplus = gethplus(dico_ravs["Pb"] / dico_ravs["Pc"], dico_ravs["eb"], dico_ravs["ec"], dico_ravs["omegab"], dico_ravs["omegac"])
        hminus = gethminus(dico_ravs["Pb"] / dico_ravs["Pc"], dico_ravs["eb"], dico_ravs["ec"], dico_ravs["omegab"], dico_ravs["omegac"])
        kplus = getkplus(dico_ravs["Pb"] / dico_ravs["Pc"], dico_ravs["eb"], dico_ravs["ec"], dico_ravs["omegab"], dico_ravs["omegac"])
        kminus = getkminus(dico_ravs["Pb"] / dico_ravs["Pc"], dico_ravs["eb"], dico_ravs["ec"], dico_ravs["omegab"], dico_ravs["omegac"])
        return hplus, hminus, kplus, kminus, dico_ravs["Pb"], dico_ravs["Pc"]


class HKPtPrior(Core_JointPrior_Function):
    """Prior defined for the h, k, P and t parameters of the Np parametrisation of the GravgroupsDynam model.
    """

    __category__ = "hkPt"
    __mandatory_args__ = ['t_ref']
    __extra_args__ = ['Phi_lims']
    __default_extra_args__ = {}
    __hidden_param_refs__ = ['Pb', 'Pc', 'eb', 'ec', 'omegab', 'omegac', 'tb', 'tc', 'Phib', 'Phic']
    __multiple_hidden_params__ = [False, False, False, False, False, False, False, False, False, False]
    __default_hidden_priors__ = {'Pb': {"category": "jeffreys", "args": {"vmin": 0.01, "vmax": 1000.}},
                                 'Pc': {"category": "jeffreys", "args": {"vmin": 0.01, "vmax": 1000.}},
                                 'eb': {"category": "uniform", "args": {"vmin": 0., "vmax": 1.}},
                                 'ec': {"category": "uniform", "args": {"vmin": 0., "vmax": 1.}},
                                 'omegab': {"category": "uniform", "args": {"vmin": -pi, "vmax": pi}},
                                 'omegac': {"category": "uniform", "args": {"vmin": -pi, "vmax": pi}},
                                 'Phib': {"category": "uniform", "args": {"vmin": -0.5, "vmax": 0.5}},
                                 'Phic': {"category": "uniform", "args": {"vmin": -0.5, "vmax": 0.5}},
                                 }
    __param_refs__ = ['hplus', 'hminus', 'kplus', 'kminus', 'Pb', 'Pc', 'tb', 'tc']
    __multiple_params__ = [False, False, False, False, False, False, False, False]

    def __init__(self, params, *args, **kwargs):
        super(HKPtPrior, self).__init__(params, *args, **kwargs)
        self.use_phi = {}
        for tname, t_prior, Phiname, Phi_prior, planet_name in zip(["tb", "tc"],
                                                                   [self.dico_args[self.hiddenparamprior_key].get("tb_prior", None), self.dico_args[self.hiddenparamprior_key].get("tc_prior", None)],
                                                                   ["Phib", "Phib"],
                                                                   [self.dico_args[self.hiddenparamprior_key].get("Phib_prior", None), self.dico_args[self.hiddenparamprior_key].get("Phic_prior", None)],
                                                                   ["b", "c"]):
            if (t_prior is not None) and (Phi_prior is not None):
                raise ValueError("t_prior and Phi_prior cannot be set at the same time. It's one or the other.")
            elif (t_prior is None) and (Phi_prior is None):
                self.use_phi[planet_name] = True
            elif t_prior is not None:
                self.use_phi[planet_name] = False
            else:
                self.use_phi[planet_name] = True
            if self.use_phi[planet_name] and (self.Phi_lims is not None):
                raise ValueError("Phi_lims should not be set when Phi_prior is provided")
        if any([not(use_phi) for use_phi in self.use_phi.values()]):
            if self.Phi_lims is None:
                self.Phi_lims = (-0.5, 0.5)
            self.Phi_min, self.Phi_max = self.Phi_lims

    def create_logpdf(self, params):
        """Return the logarithmic probability density function for the joint prior.

        :param dict params: Dictionnary which contains the Parameter instances required by the prior.
            The keys are parameter keys in the self.param_refs list and the values are the parameter instances
            as associated in the parameter file.
        :return function logpdf: log pdf the order in which the parameter should be provided is
            provided by self.param_refs
        """
        (param_nb,
         arg_list,
         param_vector_name,
         ldict) = init_arglist_paramnb_arguments_ldict(key_param=key_param, param_vector_name=par_vec_name)
        dico_logpdf = {param: priorfunc.create_logpdf() for param, priorfunc in self.priorinstance_hiddenparams.items()}
        ldict["dico_logpdf"] = dico_logpdf
        ldict["getecc_plb_4_handk_fast"] = getecc_plb_4_handk_fast
        ldict["getecc_plc_4_handk_fast"] = getecc_plc_4_handk_fast
        ldict["getomega_plb_4_handk_fast"] = getomega_plb_4_handk_fast
        ldict["getomega_plc_4_handk_fast"] = getomega_plc_4_handk_fast
        ldict["inf"] = inf
        dico_text_params = {}
        for param_key in self.param_refs:
            dico_text_params[param_key] = add_param_argument(param=params[param_key], arg_list=arg_list, key_param=key_param,
                                                             param_nb=param_nb, param_vector_name=par_vec_name)
        logpdf_torPhi = {}
        check_Phi_lims = ""
        for planet_name in ['b', 'c']:
            if self.use_phi[planet_name]:
                logpdf_torPhi[planet_name] = "dico_logpdf['Phi{planet_name}'](Phi{planet_name})".format(planet_name=planet_name)
            else:
                text_Phi_lims = """
                {tab}if (Phi{planet_name} < {Phi_min}) or (Phi{planet_name} > {Phi_max}):
                {tab}    return -inf
                """
                check_Phi_lims += dedent(text_Phi_lims).format(tab="    ", planet_name=planet_name, Phi_min=self.Phi_min, Phi_max=self.Phi_max)
                logpdf_torPhi[planet_name] = "dico_logpdf['t{planet_name}']({{t_planet}})".format(planet_name=planet_name)
                logpdf_torPhi[planet_name] = logpdf_torPhi[planet_name].format(t_planet=dico_text_params["t{}".format(planet_name)])
        function_name = "logpdf_{}".format(self.category)
        text_function = """
        def {function_name}({param_vector_name}):
            if {Pc}/{Pb} < 1:
                return -inf
            Phib = ({tb} - {t_ref}) / {Pb}
            Phic = ({tc} - {t_ref}) / {Pc}
            {check_Phi_lims}
            eb = getecc_plb_4_handk_fast({hplus}, {hminus}, {kplus}, {kminus}, {Pc}/{Pb})
            ec = getecc_plc_4_handk_fast({hplus}, {hminus}, {kplus}, {kminus})
            omegab = getomega_plb_4_handk_fast({hplus}, {hminus}, {kplus}, {kminus})
            omegac = getomega_plc_4_handk_fast({hplus}, {hminus}, {kplus}, {kminus})
            return (dico_logpdf['Pb']({Pb}) + dico_logpdf['Pc']({Pc}) + dico_logpdf['eb'](eb) + dico_logpdf['ec'](ec) +
                    dico_logpdf['omegab'](omegab) + dico_logpdf['omegac'](omegac) + {logpdf_torPhib} + {logpdf_torPhic})
        """
        text_function = dedent(text_function)
        text_function = text_function.format(function_name=function_name, param_vector_name=par_vec_name,
                                             hplus=dico_text_params["hplus"], hminus=dico_text_params["hminus"],
                                             kplus=dico_text_params["kplus"], kminus=dico_text_params["kminus"],
                                             Pb=dico_text_params["Pb"], Pc=dico_text_params["Pc"],
                                             tb=dico_text_params["tb"], tc=dico_text_params["tc"],
                                             check_Phi_lims=check_Phi_lims, t_ref=self.t_ref,
                                             logpdf_torPhib=logpdf_torPhi["b"], logpdf_torPhic=logpdf_torPhi["c"]
                                             )
        logger.debug("text of joint prior {category}:\n{text_func}"
                     "".format(category=self.category, text_func=text_function))
        logger.debug("Parameters for joint prior {category}:\n{dico_param}"
                     "".format(category=self.category, dico_param={nb: param for nb, param in enumerate(get_function_arglist(arg_list)[key_param])}))
        exec(text_function, ldict)
        return DocFunction(ldict[function_name], get_function_arglist(arg_list))

    def logpdf(self, hplus, hminus, kplus, kminus, Pb, Pc, tb, tc):
        if Pc / Pb < 1:
            return -inf
        dico_logpdf = self.priorinstance_hiddenparams
        Phib = (tb - self.t_ref) / Pb
        Phic = (tc - self.t_ref) / Pc
        res_Phiort = {}
        for Phi, tt, planet_name in zip([Phib, Phic], [tb, tc], ["b", "c"]):
            if self.use_phi[planet_name]:
                res_Phiort[planet_name] = dico_logpdf["Phi{}".format(planet_name)](Phi)
            else:
                if (Phi < self.Phi_min) or (Phi > self.Phi_max):
                    return -inf
                res_Phiort[planet_name] = dico_logpdf["t{}".format(planet_name)](tt)
        eb = getecc_plb_4_handk_fast(hplus, hminus, kplus, kminus, Pc / Pb)
        ec = getecc_plc_4_handk_fast(hplus, hminus, kplus, kminus)
        omegab = getomega_plb_4_handk_fast(hplus, hminus, kplus, kminus)
        omegac = getomega_plc_4_handk_fast(hplus, hminus, kplus, kminus)
        return (dico_logpdf["Pb"](Pb) + dico_logpdf["Pc"](Pc) + dico_logpdf["eb"](eb) + dico_logpdf["ec"](ec) +
                dico_logpdf["omegab"](omegab) + dico_logpdf["omegac"](omegac) + res_Phiort["b"] + res_Phiort["c"])

    def ravs(self, nb_values=1):
        """Return values of the parameters drawn from the joint prior.

        :param int nb_values: Number of values to draw for each parameter.
        :return tuple_of_float/ nb_values: Tuple for which each element contains the value(s) drawn
            for each parameter. If nb_values = 1, it's just a float, otherwise it's an np.array.
            The order of the parameters in the tuple is provided by self.param_refs.
        """
        dico_ravs = {}
        for param, dico in self.hiddenparam_defs.items():
            value = dico.get("value", None)
            if value is None:
                dico_ravs[param] = dico["priorfunc_instance"].ravs(nb_values=nb_values)
            else:
                dico_ravs[param] = ones(nb_values) * value
            if dico_ravs[param].size == 1:
                dico_ravs[param] = dico_ravs[param][0]
        hplus = gethplus(dico_ravs["Pb"] / dico_ravs["Pc"], dico_ravs["eb"], dico_ravs["ec"], dico_ravs["omegab"], dico_ravs["omegac"])
        hminus = gethminus(dico_ravs["Pb"] / dico_ravs["Pc"], dico_ravs["eb"], dico_ravs["ec"], dico_ravs["omegab"], dico_ravs["omegac"])
        kplus = getkplus(dico_ravs["Pb"] / dico_ravs["Pc"], dico_ravs["eb"], dico_ravs["ec"], dico_ravs["omegab"], dico_ravs["omegac"])
        kminus = getkminus(dico_ravs["Pb"] / dico_ravs["Pc"], dico_ravs["eb"], dico_ravs["ec"], dico_ravs["omegab"], dico_ravs["omegac"])
        tt = {}
        for planet_name in ["b", "c"]:
            if self.use_phi[planet_name]:
                tt[planet_name] = dico_ravs["Phi{}".format(planet_name)] * dico_ravs["P{}".format(planet_name)] + self.t_ref
            else:
                tt[planet_name] = dico_ravs["t{}".format(planet_name)]
                Phi = (tt[planet_name] - self.t_ref) / dico_ravs["P{}".format(planet_name)]
                indexes = where((Phi > self.Phi_max) | (Phi < self.Phi_min))[0]
                while len(indexes) > 0:
                    tt[planet_name][indexes] = self.hiddenparam_defs["t{}".format(planet_name)]["priorfunc_instance"].ravs(nb_values=len(indexes))
                    indexes = where((Phi > self.Phi_max) | (Phi < self.Phi_min))[0]
        return hplus, hminus, kplus, kminus, dico_ravs["Pb"], dico_ravs["Pc"], tt["b"], tt["c"]


class Ptphiprior(Core_JointPrior_Function):
    """Prior defined for the Period and reference time of the orbit.
    """

    __category__ = "Ptphi"
    __mandatory_args__ = ['t_ref']
    __extra_args__ = ['Phi_lims']
    __default_extra_args__ = {}
    __hidden_param_refs__ = ['P', 't', 'Phi']
    __default_hidden_priors__ = {'P': {"category": "jeffreys", "args": {"vmin": 0.01, "vmax": 1000.}},
                                 'Phi': {"category": "uniform", "args": {"vmin": -0.5, "vmax": 0.5}}
                                 }
    __multiple_hidden_params__ = [False, False, False]
    __param_refs__ = ['P', 't']
    __multiple_params__ = [False, False]

    def __init__(self, params, *args, **kwargs):
        super(Ptphiprior, self).__init__(params, *args, **kwargs)
        t_prior = self.dico_args[self.hiddenparamprior_key].get("t_prior", None)
        Phi_prior = self.dico_args[self.hiddenparamprior_key].get("Phi_prior", None)
        if (t_prior is not None) and (Phi_prior is not None):
            raise ValueError("t_prior and Phi_prior cannot be set at the same time. It's one or the other.")
        elif (t_prior is None) and (Phi_prior is None):
            self.use_phi = True
        elif t_prior is not None:
            self.use_phi = False
        else:
            self.use_phi = True
        if self.use_phi and (self.Phi_lims is not None):
            raise ValueError("Phi_lims should not be set when Phi_prior is provided")
        if not(self.use_phi):
            if self.Phi_lims is None:
                self.Phi_lims = (-0.5, 0.5)
            self.Phi_min, self.Phi_max = self.Phi_lims

    def create_logpdf(self, params):
        """Return the logarithmic probability density function for the joint prior.

        :param dict params: Dictionnary which contains the Parameter instances required by the prior.
            The keys are parameter keys in the self.param_refs list and the values are the parameter instances
            as associated in the parameter file.
        :return function logpdf: log pdf the order in which the parameter should be provided is
            provided by self.param_refs
        """
        (param_nb,
         arg_list,
         param_vector_name,
         ldict) = init_arglist_paramnb_arguments_ldict(key_param=key_param, param_vector_name=par_vec_name)
        dico_logpdf = {param: priorfunc.create_logpdf() for param, priorfunc in self.priorinstance_hiddenparams.items() if priorfunc is not None}
        ldict["dico_logpdf"] = dico_logpdf
        dico_text_params = {}
        for param_key in self.param_refs:
            dico_text_params[param_key] = add_param_argument(param=params[param_key], arg_list=arg_list, key_param=key_param,
                                                             param_nb=param_nb, param_vector_name=par_vec_name)
        function_name = "logpdf_{}".format(self.category)
        if self.use_phi:
            text_function = """
            def {function_name}({param_vector_name}):
                Phi = ({t} - {t_ref}) / {P}
                return dico_logpdf["P"]({P}) + dico_logpdf["Phi"](Phi)
            """
            text_function = dedent(text_function)
            text_function = text_function.format(function_name=function_name, param_vector_name=par_vec_name,
                                                 t=dico_text_params["t"], t_ref=self.t_ref, P=dico_text_params["P"])
        else:
            ldict["inf"] = inf
            text_function = """
            def {function_name}({param_vector_name}):
                Phi = ({t} - {t_ref}) / {P}
                if (Phi < {Phi_min}) or (Phi > {Phi_max}):
                    return -inf
                else:
                    return dico_logpdf["P"]({P}) + dico_logpdf["t"]({t})
            """
            text_function = dedent(text_function)
            text_function = text_function.format(function_name=function_name, param_vector_name=par_vec_name,
                                                 t=dico_text_params["t"], t_ref=self.t_ref, P=dico_text_params["P"],
                                                 Phi_min=self.Phi_min, Phi_max=self.Phi_max)
        logger.debug("text of joint prior {category}:\n{text_func}"
                     "".format(category=self.category, text_func=text_function))
        logger.debug("Parameters for joint prior {category}:\n{dico_param}"
                     "".format(category=self.category, dico_param={nb: param for nb, param in enumerate(get_function_arglist(arg_list)[key_param])}))
        exec(text_function, ldict)
        return DocFunction(ldict[function_name], get_function_arglist(arg_list))

    def logpdf(self, P, t):
        dico_logpdf = self.priorinstance_hiddenparams

        Phi = (t - self.t_ref) / P
        if self.use_phi:
            return dico_logpdf["P"](P) + dico_logpdf["Phi"](Phi)
        else:
            if (Phi < self.Phi_min) or (Phi > self.Phi_max):
                return -inf
            else:
                return dico_logpdf["P"]({P}) + dico_logpdf["t"]({t})

    def ravs(self, nb_values=1):
        """Return values of the parameters drawn from the joint prior.

        :param int nb_values: Number of values to draw for each parameter.
        :return tuple_of_float/ nb_values: Tuple for which each element contains the value(s) drawn
            for each parameter. If nb_values = 1, it's just a float, otherwise it's an np.array.
            The order of the parameters in the tuple is provided by self.param_refs.
        """
        dico_ravs = {}
        for param, dico in self.hiddenparam_defs.items():
            if dico is not None:
                value = dico.get("value", None)
                if value is None:
                    dico_ravs[param] = self.priorinstance_hiddenparams[param].ravs(nb_values=nb_values)
                else:
                    dico_ravs[param] = ones(nb_values) * value
                if dico_ravs[param].size == 1:
                    dico_ravs[param] = dico_ravs[param][0]
        if self.use_phi:
            t = dico_ravs["Phi"] * dico_ravs["P"] + self.t_ref
            return dico_ravs["P"], t
        else:
            Phi = (dico_ravs["t"] - self.t_ref) / dico_ravs["P"]
            indexes = where((Phi > self.Phi_max) | (Phi < self.Phi_min))[0]
            while len(indexes) > 0:
                dico_ravs["t"][indexes] = self.priorinstance_hiddenparams["t"].ravs(nb_values=len(indexes))
                indexes = where((Phi > self.Phi_max) | (Phi < self.Phi_min))[0]
            return dico_ravs["P"], dico_ravs["t"]


class Transitingprior(Core_JointPrior_Function):
    """Prior defined for the a/R, cosinc and Rrat to ensure that a planet is transit (or not).

    IMPORTANT NOTE: This prior is not properly normalized when the transiting and grazing conditions
    are more restrictive than the aR, cosinc Rrat priors

    TODO: Make it multiple

    :param bool transiting: True if you want to force the planet to be transiting, False otherwise
    :param bool allow_grazing: True if you want to allow grazing transits (whatever the value of transiting)
    :param list_like_of_2_floats Phi_lims: Should only be set when t_prior is provided, otherwise it triggers an
        error. Defines the inferior and superior limits and phase (Phi) when t_prior is defined.
    """

    __category__ = "transiting"
    __mandatory_args__ = ['transiting', 'allow_grazing']
    __extra_args__ = []
    __default_extra_args__ = {}
    __param_refs__ = ['aR', 'cosinc', 'Rrat']
    __multiple_params__ = [False, False, False]
    __hidden_param_refs__ = ['Rrat', 'b', 'aR']
    __multiple_hidden_params__ = [False, False, False]
    __default_hidden_priors__ = {'Rrat': {"category": "uniform", "args": {"vmin": 0., "vmax": 1.}},
                                 'b': {"category": "uniform", "args": {"vmin": 0., "vmax": 1.}},
                                 'aR': {"category": "jeffreys", "args": {"vmin": 1., "vmax": 1e3}}
                                 }

    def _get_hidden_param_default_dict(self, dico_default_values=None):
        """Update Core_JointPrior_Function._get_hidden_param_default_dict

        Adapt the default prior for b to the value of transiting and allow_grazing
        """
        dico = super(Transitingprior, self)._get_hidden_param_default_dict(dico_default_values=dico_default_values)
        if self.multiple_hidden_params[1]:  # 1 is for b
            nb_b = self.infer_hiddenparams_nb(hidden_param_ref="b")
            for ii, transiting_ii, allow_grazing_ii in zip(range(nb_b), self.transiting, self.allow_grazing):
                if transiting_ii:
                    if allow_grazing_ii:
                        dico["b"][ii] = {"category": "uniform", "args": {"vmin": 0., "vmax": 2.}}
                else:
                    if allow_grazing_ii:
                        dico["b"][ii] = {"category": "jeffreys", "args": {"vmin": 1., "vmax": 1e3}}
                    else:
                        dico["b"][ii] = {"category": "jeffreys", "args": {"vmin": 0., "vmax": 1e3}}
        else:
            if self.transiting:
                if self.allow_grazing:
                    dico["b"] = {"category": "uniform", "args": {"vmin": 0., "vmax": 2.}}
            else:
                if self.allow_grazing:
                    dico["b"] = {"category": "jeffreys", "args": {"vmin": 1., "vmax": 1e3}}
                else:
                    dico["b"] = {"category": "jeffreys", "args": {"vmin": 0., "vmax": 1e3}}
        return dico

    def create_logpdf(self, params):
        """Return the logarithmic probability density function for the joint prior.

        :param dict params: Dictionnary which contains the Parameter instances required by the prior.
            The keys are parameter keys in the self.param_refs list and the values are the parameter instances
            as associated in the parameter file.
        :return function logpdf: log pdf the order in which the parameter should be provided is
            provided by self.param_refs
        """
        (param_nb,
         arg_list,
         param_vector_name,
         ldict) = init_arglist_paramnb_arguments_ldict(key_param=key_param, param_vector_name=par_vec_name)
        # Create the logpdf function for each hidden parameter
        dico_logpdf = {param: priorfunc.create_logpdf() for param, priorfunc in self.priorinstance_hiddenparams.items()}
        # Put variables that you want to have available when you execute the text of the joint
        # logpdf function in ldict
        ldict["dico_logpdf"] = dico_logpdf
        ldict["inf"] = inf
        # Associate each parameter with value: a number of it's is fixed or a p[i] if it's free.
        dico_text_params = {}
        for param_key in self.param_refs:
            dico_text_params[param_key] = add_param_argument(param=params[param_key], arg_list=arg_list, key_param=key_param,
                                                             param_nb=param_nb, param_vector_name=par_vec_name)
        # Define the joint logpdf function name
        function_name = "logpdf_{}".format(self.category)
        # For the prior you will need to compare the value of b with the condition for transiting and
        # grazind. Make the text that performs this comparison
        if self.transiting:
            if self.allow_grazing:
                text_comp = "b > (1 + {Rrat})".format(Rrat=dico_text_params["Rrat"])
            else:
                text_comp = "b > (1 - {Rrat})".format(Rrat=dico_text_params["Rrat"])
        else:
            if self.allow_grazing:
                text_comp = "b < (1 - {Rrat})".format(Rrat=dico_text_params["Rrat"])
            else:
                text_comp = "b < (1 + {Rrat})".format(Rrat=dico_text_params["Rrat"])
        # Define the full template for the logpdf function text
        text_function = """
        def {function_name}({param_vector_name}):
            b = {aR} * {cosinc}
            if {text_comp}:
                return -inf
            elif abs({cosinc}) > 1:
                return -inf
            else:
                return dico_logpdf['b'](b) + dico_logpdf['Rrat']({Rrat}) + dico_logpdf['aR']({aR})
        """
        text_function = dedent(text_function)
        # Fill the template of the logpdf function
        text_function = text_function.format(function_name=function_name, param_vector_name=par_vec_name,
                                             aR=dico_text_params["aR"], cosinc=dico_text_params["cosinc"],
                                             Rrat=dico_text_params["Rrat"], text_comp=text_comp)

        logger.debug("text of joint prior {category}:\n{text_func}"
                     "".format(category=self.category, text_func=text_function))
        logger.debug("Parameters for joint prior {category}:\n{dico_param}"
                     "".format(category=self.category, dico_param={nb: param for nb, param in enumerate(get_function_arglist(arg_list)[key_param])}))

        exec(text_function, ldict)
        return DocFunction(ldict[function_name], get_function_arglist(arg_list))

    def logpdf(self, aR, cosinc, Rrat):
        dico_logpdf = self.priorinstance_hiddenparams

        b = aR * cosinc
        if self.transiting:
            if self.allow_grazing:
                comp = (b > (1 + Rrat))
            else:
                comp = (b > (1 - Rrat))
        else:
            if self.allow_grazing:
                comp = (b < (1 - Rrat))
            else:
                comp = (b < (1 + Rrat))
        if comp:
            return -inf
        else:
            return dico_logpdf["b"](b) + dico_logpdf["Rrat"](Rrat) + dico_logpdf["aR"](aR)

    def ravs(self, nb_values=1):
        """Return values of the parameters drawn from the joint prior.

        :param int nb_values: Number of values to draw for each parameter.
        :return tuple_of_float/ nb_values: Tuple for which each element contains the value(s) drawn
            for each parameter. If nb_values = 1, it's just a float, otherwise it's an np.array.
            The order of the parameters in the tuple is provided by self.param_refs.
        """
        dico_ravs = {}  # dict containing the randomly drawn values for each hidden parameter
        dico_pick = {}  # dict indicating if you should pick random values (True) or if the value is
        # fixed (False) for each hidden parameter

        # Initialise the dictionary and the arrays which will contain the randomly drawn values. The array
        # already have the good dimension. If the value for a hidden parameter is fixed than the array
        # should be full with this value other, it's full of nans.
        for hiddenparam, dico_prior_def in self.hiddenparam_defs.items():
            value = dico_prior_def.get("value", None)
            if value is None:
                dico_pick[hiddenparam] = True
                dico_ravs[hiddenparam] = ones(nb_values) * nan
            else:
                dico_pick[hiddenparam] = False
                dico_ravs[hiddenparam] = ones(nb_values) * value

        # Indexes is the list of indexes in the arrays for which the random pick should be redrawn
        # (it doesn't satisfy the condition)
        indexes = arange(nb_values)  # We initialise indexes with the list of all element in array
        while len(indexes) > 0:  # While there is at least one drawn that doesn't satisfy the condition, do a new draw.
            # For all hidden parameter redo the drawn for indexes where the condition is not satisfied.
            for hiddenparam_ref in self.hidden_param_refs:
                if dico_pick[hiddenparam_ref]:
                    dico_ravs[hiddenparam_ref][indexes] = self.priorinstance_hiddenparams[hiddenparam_ref].ravs(nb_values=len(indexes))
            # Check if cosinc is below 1
            indexes_cosinc = where(dico_ravs["b"] / dico_ravs["Rrat"] > 1)[0]
            # Check if and where the condition is not satisfy.
            if self.transiting:
                if self.allow_grazing:
                    indexes_tr = where(dico_ravs["b"] > (1 + dico_ravs["Rrat"]))[0]
                else:
                    indexes_tr = where(dico_ravs["b"] > (1 - dico_ravs["Rrat"]))[0]
            else:
                if self.allow_grazing:
                    indexes_tr = where(dico_ravs["b"] < (1 - dico_ravs["Rrat"]))[0]
                else:
                    indexes_tr = where(dico_ravs["b"] < (1 + dico_ravs["Rrat"]))[0]
            indexes = array(list(set(list(indexes_cosinc) + list(indexes_tr))))
        # If you just ask one value, return just one value per parameter instead of an array with only one element.
        if nb_values == 1:
            for param, dico in self.hiddenparam_defs.items():
                dico_ravs[param] = dico_ravs[param][0]

        return dico_ravs['aR'], dico_ravs["b"] / dico_ravs["aR"], dico_ravs["Rrat"]


class TransitingRhoprior(Transitingprior):
    """Prior defined for the a/R, cosinc and Rrat to ensure that a planet is transit (or not).

    IMPORTANT NOTE: This prior is not properly normalized when the transiting and grazing conditions
    are more restrictive than the aR, cosinc Rrat priors

    :param bool transiting: List of bool indicating if you want each planet to be transiting or not transiting.
        True if you want to force the planet to be transiting, False otherwise
    :param bool allow_grazing: List of bool indicating if you want allow each planet to be grazing.
        True if you want to allow grazing transits (whatever the value of transiting)
    """

    __category__ = "transiting_rho"
    __mandatory_args__ = ['transiting', 'allow_grazing']
    __extra_args__ = []
    __default_extra_args__ = []
    __param_refs__ = ['rhostar', 'P', 'cosinc', 'Rrat']
    __multiple_params__ = [False, True, True, True]
    __hidden_param_refs__ = ['rhostar', 'P', 'Rrat', 'b']
    __multiple_hidden_params__ = [False, True, True, True]
    __default_hidden_priors__ = {'rhostar': {'category': 'normal', 'args': {'mu': 1, 'sigma': 0.1, 'lims': [0., None]}},
                                 'P': {'category': 'jeffreys', 'args': {'vmin': 0.1, 'vmax': 1e4}},
                                 'Rrat': {'category': 'uniform', 'args': {'vmin': 0., 'vmax': 1.}},
                                 'b': {'category': 'uniform', 'args': {'vmin': 0., 'vmax': 1.}}
                                 }

    def __init__(self, params, *args, **kwargs):
        super(Transitingprior, self).__init__(params, *args, **kwargs)
        # Check that P, cosinc and Rrat have the same number of parameters.
        if not(self.get_params_nb(param_ref="P") == self.get_params_nb(param_ref="cosinc") == self.get_params_nb(param_ref="Rrat")):
            raise ValueError("You should have the same number of P, cosinc and Rrat parameters. One of each per planet !")
        self.nb_planet = self.get_params_nb(param_ref="P")
        # transiting and allow_grazing are also multiples so check the transiting and allow_grazing have
        # the good dimensions. The user can provide only one value and in this case it's assumed that it applies
        # to all planets.
        for arg in [self.transiting, self.allow_grazing]:
            if isinstance(arg, list) and (len(arg) != self.nb_planet):
                raise ValueError("If you provided transiting or allow_grazing as a list, it should have "
                                 "the same length as params['P']. One per planet.")
            else:
                arg = [arg for i in range(self.nb_planet)]

    def create_logpdf(self, params):
        """Return the logarithmic probability density function for the joint prior.

        :param dict params: Dictionnary which contains the Parameter instances required by the prior.
            The keys are parameter keys in the self.param_refs list and the values are the parameter instances
            as associated in the parameter file.
        :return function logpdf: log pdf the order in which the parameter should be provided is
            provided by self.param_refs
        """
        (param_nb,
         arg_list,
         param_vector_name,
         ldict) = init_arglist_paramnb_arguments_ldict(key_param=key_param, param_vector_name=par_vec_name)
        # Create the logpdf function for each hidden parameter
        dico_logpdf = {}
        for hidden_param_ref, multiple in zip(self.hidden_param_refs, self.multiple_hidden_params):
            if multiple:
                dico_logpdf[hidden_param_ref] = [priorfunc.create_logpdf() for priorfunc in self.priorinstance_hiddenparams[hidden_param_ref]]
            else:
                dico_logpdf[hidden_param_ref] = self.priorinstance_hiddenparams[hidden_param_ref].create_logpdf()
        # Put variables that you want to have available when you execute the text of the joint
        # logpdf function in ldict
        ldict["dico_logpdf"] = dico_logpdf
        ldict["getaoverr"] = getaoverr
        ldict["inf"] = inf
        ldict["array"] = array
        ldict["nb_planet"] = self.nb_planet
        ldict["abs"] = abs
        # Associate each parameter with value: a number of it's is fixed or a p[i] if it's free.
        dico_text_params = {}
        for param_ref, multiple in zip(self.param_refs, self.multiple_params):
            if multiple:
                dico_text_params[param_ref] = [add_param_argument(param=param_ref_ii, arg_list=arg_list, key_param=key_param,
                                                                  param_nb=param_nb, param_vector_name=par_vec_name)
                                               for param_ref_ii in params[param_ref]]
            else:
                dico_text_params[param_ref] = add_param_argument(param=params[param_ref], arg_list=arg_list, key_param=key_param,
                                                                 param_nb=param_nb, param_vector_name=par_vec_name)
        # Define the joint logpdf function name
        function_name = "logpdf_{}".format(self.category)
        # For each planet, you will need to compare the value of b with the condition for transiting and
        # grazind. Make list of texts that performs this comparison (one element of the list per planet)
        list_comp = "["
        for idx_planet in range(self.get_params_nb("P")):
            if self.transiting[idx_planet]:
                if self.allow_grazing[idx_planet]:
                    list_comp += "b[{idx_planet}] > (1 + {Rrat})".format(idx_planet=idx_planet,
                                                                         Rrat=dico_text_params["Rrat"][idx_planet])
                else:
                    list_comp += "b[{idx_planet}] > (1 - {Rrat})".format(idx_planet=idx_planet,
                                                                         Rrat=dico_text_params["Rrat"][idx_planet])
            else:
                if self.allow_grazing:
                    list_comp += "b[{idx_planet}] < (1 - {Rrat})".format(idx_planet=idx_planet,
                                                                         Rrat=dico_text_params["Rrat"][idx_planet])
                else:
                    list_comp += "b[{idx_planet}] < (1 + {Rrat})".format(idx_planet=idx_planet,
                                                                         Rrat=dico_text_params["Rrat"][idx_planet])
            list_comp += ", "
        list_comp += "]"
        # Define the full template for the logpdf function text
        text_function = """
        def {function_name}({param_vector_name}):
            P = array([{P}])
            Rrat = array([{Rrat}])
            b = getaoverr(P, {rhostar}, 0., 90.) * array([{cosinc}])  # WARNING: "0., 90.": Quick fix - ecc and omega are not included in the prior
            if any({list_comp}):
                return -inf
            elif any(abs([{cosinc}]) > 1):
                return -inf
            else:
                return (dico_logpdf['rhostar']({rhostar}) + sum([dico_logpdf['b'][ii](b[ii]) for ii in range(nb_planet)]) +
                        sum([dico_logpdf['Rrat'][ii](Rrat[ii]) for ii in range(nb_planet)]) +
                        sum([dico_logpdf['P'][ii](P[ii]) for ii in range(nb_planet)])
                        )
        """
        text_function = dedent(text_function)
        # Fill the template of the logpdf function
        text_function = text_function.format(function_name=function_name, param_vector_name=par_vec_name,
                                             P=", ".join(dico_text_params["P"]), cosinc=", ".join(dico_text_params["cosinc"]),
                                             Rrat=", ".join(dico_text_params["Rrat"]), rhostar=dico_text_params["rhostar"],
                                             list_comp=list_comp)

        logger.debug("text of joint prior {category}:\n{text_func}"
                     "".format(category=self.category, text_func=text_function))
        logger.debug("Parameters for joint prior {category}:\n{dico_param}"
                     "".format(category=self.category, dico_param={nb: param for nb, param in enumerate(get_function_arglist(arg_list)[key_param])}))

        exec(text_function, ldict)
        return DocFunction(ldict[function_name], get_function_arglist(arg_list))

    def logpdf(self, rhostar, P, cosinc, Rrat):
        """ NOT WORKING because need to take into account the multiple parameter (multiple planetss)
        """
        raise NotImplementedError
        dico_logpdf = self.priorinstance_hiddenparams
        aR = getaoverr(P, rhostar, 0, 90.)  # WARNING: Quick fix - ecc and omega are not included in the prior
        b = aR * cosinc
        if self.transiting:
            if self.allow_grazing:
                comp = (b > (1 + Rrat))
            else:
                comp = (b > (1 - Rrat))
        else:
            if self.allow_grazing:
                comp = (b < (1 - Rrat))
            else:
                comp = (b < (1 + Rrat))
        if comp:
            return -inf
        else:
            return (dico_logpdf['rhostar'](rhostar) + sum([dico_logpdf['b'][ii](b[ii]) for ii in range(self.nb_planet)]) +
                    sum([dico_logpdf['Rrat'][ii]({Rrat}[ii]) for ii in range(self.nb_planet)]) +
                    sum([dico_logpdf['P'][ii]({P}[ii]) for ii in range(self.nb_planet)])
                    )

    def ravs(self, nb_values=1):
        """Return values of the parameters drawn from the joint prior.

        :param int nb_values: Number of values to draw for each parameter.
        :return tuple_of_float/ nb_values: Tuple for which each element contains the value(s) drawn
            for each parameter. If nb_values = 1, it's just a float, otherwise it's an np.array.
            The order of the parameters in the tuple is provided by self.param_refs.
        """
        dico_ravs = {}  # dict containing the randomly drawn values for each hidden parameter
        dico_pick = {}   # dict indicating if you should pick random values (True) or if the value is
        # fixed (False) for each hidden parameter

        # Initialise the dictionary and the arrays which will contain the randomly drawn values. The array
        # already have the good dimension. If the value for a hidden parameter is fixed than the array
        # should be full with this value other, it's full of nans.
        for hiddenparam_ref, multiple in zip(self.hiddenparam_defs, self.multiple_hidden_params):
            if multiple:
                dico_ravs[hiddenparam_ref] = []
                dico_pick[hiddenparam_ref] = []
                for ii in range(self.nb_planet):
                    value = self.hiddenparam_defs[hiddenparam_ref][ii].get("value", None)
                    if value is None:
                        dico_pick[hiddenparam_ref].append(True)
                        dico_ravs[hiddenparam_ref].append(ones(nb_values) * nan)
                    else:
                        dico_pick[hiddenparam_ref].append(False)
                        dico_ravs[hiddenparam_ref].append(ones(nb_values) * value)
            else:
                value = self.hiddenparam_defs[hiddenparam_ref].get("value", None)
                if value is None:
                    dico_pick[hiddenparam_ref] = True
                    dico_ravs[hiddenparam_ref] = ones(nb_values) * nan
                else:
                    dico_pick[hiddenparam_ref] = False
                    dico_ravs[hiddenparam_ref] = ones(nb_values) * value

        # Indexes is the list of indexes in the arrays for which the random pick should be redrawn
        # (it doesn't satisfy the condition)
        indexes = arange(nb_values)  # We initialise indexes with the list of all element in array
        while len(indexes) > 0:   # While there is at least one drawn that doesn't satisfy the condition, do a new draw.
            # For all hidden parameter redo the drawn for indexes where the condition is not satisfied.
            for hiddenparam_ref, multiple in zip(self.hiddenparam_defs, self.multiple_hidden_params):
                if multiple:
                    for ii in range(self.nb_planet):
                        if dico_pick[hiddenparam_ref][ii]:
                            dico_ravs[hiddenparam_ref][ii][indexes] = self.priorinstance_hiddenparams[hiddenparam_ref][ii].ravs(nb_values=len(indexes))
                else:
                    if dico_pick[hiddenparam_ref]:
                        dico_ravs[hiddenparam_ref][indexes] = self.priorinstance_hiddenparams[hiddenparam_ref].ravs(nb_values=len(indexes))

            # Check if and where the condition is not satisfy.
            # The conditions can be statisfied for one planet and not another, so we need a list of indexes.
            # One element correspond to one planet and will give the indexes that don't satisfy the condition
            # for this planet.
            l_indexes = []
            # For each planet, check the condition
            for ii in range(self.nb_planet):
                if self.transiting[ii]:
                    if self.allow_grazing[ii]:
                        l_indexes.append(where(dico_ravs["b"][ii] > (1 + dico_ravs["Rrat"][ii]))[0])
                    else:
                        l_indexes.append(where(dico_ravs["b"][ii] > (1 - dico_ravs["Rrat"][ii]))[0])
                else:
                    if self.allow_grazing[ii]:
                        l_indexes.append(where(dico_ravs["b"][ii] < (1 - dico_ravs["Rrat"][ii]))[0])
                    else:
                        l_indexes.append(where(dico_ravs["b"][ii] < (1 + dico_ravs["Rrat"][ii]))[0])
            # Then we are going to combine these indexes. If at least one planet doesn't satisfy the
            # condition we will redrawn the parameters for all the planets (because rhos star is common
            # to all planets)
            set_indexes = set([])
            for indexes in l_indexes:
                set_indexes = set_indexes.union(indexes)
            indexes = list(set_indexes)

        # If you just ask one value, return just one value per parameter instead of an array with only one element.
        if nb_values == 1:
            for hiddenparam_ref, multiple in zip(self.hiddenparam_defs, self.multiple_hidden_params):
                if multiple:
                    for ii in range(self.nb_planet):
                        dico_ravs[hiddenparam_ref][ii] = dico_ravs[hiddenparam_ref][ii][0]
                else:
                    dico_ravs[hiddenparam_ref] = dico_ravs[hiddenparam_ref][0]
        # Compute the cosinc values from the b, P and rhostar values
        dico_ravs["cosinc"] = []
        for ii in range(self.nb_planet):
            dico_ravs["cosinc"].append(dico_ravs["b"][ii] / getaoverr(dico_ravs["P"][ii], dico_ravs["rhostar"], 0., 90.))  # WARNING: Quick fix - ecc and omega are not included in the prior
        # Format the return which should be a tuple of list of arrays or arrays depending on wether a
        # parameter can be multiple or not.
        # It should be ( np.array(rhostar), [np.array(P) for each planet], [np.array(cosinc) for each planet],
        # , [np.array(aR) for each planet] )
        l_res = []
        for param_ref, multiple in zip(self.param_refs, self.multiple_params):
            l_res.append(dico_ravs[param_ref])
        return tuple(l_res)
