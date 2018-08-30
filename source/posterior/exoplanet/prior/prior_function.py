"""
Prior functions module.
"""
from __future__ import division
from logging import getLogger
from textwrap import dedent

from numpy import pi, inf, ones, where, any

from ...core.prior.core_prior import Core_JointPrior_Function
from ....tools.convert import getecc_plb_4_handk_fast, getecc_plc_4_handk_fast, getomega_plb_4_handk_fast, getomega_plc_4_handk_fast
from ....tools.convert import gethplus, gethminus, getkplus, getkminus
from ....tools.function_w_doc import DocFunction
from ....tools.function_from_text_toolbox import init_arglist_paramnb_arguments_ldict, add_param_argument, par_vec_name, key_param, get_function_arglist


## logger object
logger = getLogger()


class HKPPrior(Core_JointPrior_Function):
    """Prior defined for the h, k and P parameters of the Np parametrisation of the GravgroupsDynam model.
    """

    __category__ = "hkP"
    __mandatory_args__ = []
    __extra_args__ = ['Pb_prior', 'Pc_prior', 'eb_prior', 'ec_prior', 'omegab_prior', 'omegac_prior']
    __params__ = ['hplus', 'hminus', 'kplus', 'kminus', 'Pb', 'Pc']

    def set_dico_priors_arg(self, Pb_prior=None, Pc_prior=None, eb_prior=None, ec_prior=None,
                            omegab_prior=None, omegac_prior=None):
        """Fill self.dico_priors_arg.

        The argument defines the marginal prior of the hidden parameters "Pb", "Pc", "eb", "ec", "omegab",
        "omegac". They should follow the following format: {"category": priorcat, "args": {"arg1":0, "arg2":1}}
        like for marginal priors
        """
        for Pname, P_prior in zip(["Pb", "Pc"], [Pb_prior, Pc_prior]):
            if P_prior is None:
                P_prior = {"category": "jeffreys", "args": {"vmin": 0.01, "vmax": 1000.}}
            self.dico_priors_arg[Pname] = P_prior
        for ename, e_prior in zip(["eb", "ec"], [eb_prior, ec_prior]):
            if e_prior is None:
                e_prior = {"category": "uniform", "args": {"vmin": 0., "vmax": 1.}}
            self.dico_priors_arg[ename] = e_prior
        for omeganame, omega_prior in zip(["omegab", "omegac"], [omegab_prior, omegac_prior]):
            if omega_prior is None:
                omega_prior = {"category": "uniform", "args": {"vmin": -pi, "vmax": pi}}
            self.dico_priors_arg[omeganame] = omega_prior

    def create_logpdf(self, params):
        """Return the logarithmic probability density function for the joint prior.

        :param dict params: Dictionnary which contains the Parameter instances required by the prior.
            The keys are parameter keys in the self.params list and the values are the parameter instances
            as associated in the parameter file.
        :return function logpdf: log pdf the order in which the parameter should be provided is
            provided by self.params
        """
        (param_nb,
         arg_list,
         param_vector_name,
         ldict) = init_arglist_paramnb_arguments_ldict(key_param=key_param, param_vector_name=par_vec_name)
        dico_logpdf = {param: priorfunc.create_logpdf() for param, priorfunc in self.dico_priorfunction.items()}
        ldict["dico_logpdf"] = dico_logpdf
        ldict["getecc_plb_4_handk_fast"] = getecc_plb_4_handk_fast
        ldict["getecc_plc_4_handk_fast"] = getecc_plc_4_handk_fast
        ldict["getomega_plb_4_handk_fast"] = getomega_plb_4_handk_fast
        ldict["getomega_plc_4_handk_fast"] = getomega_plc_4_handk_fast
        ldict["inf"] = inf
        dico_text_params = {}
        for param_key in self.params:
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
        dico_logpdf = self.dico_priorfunction

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
            The order of the parameters in the tuple is provided by self.params.
        """
        dico_ravs = {}
        for param, dico in self.dico_priors_arg.items():
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

    __category__ = "hkP"
    __mandatory_args__ = ['t_ref']
    __extra_args__ = ['Pb_prior', 'Pc_prior', 'eb_prior', 'ec_prior', 'omegab_prior', 'omegac_prior',
                      'tb_prior', 'tc_prior', 'Phi_lims', 'Phib_prior', 'Phic_prior']
    __params__ = ['hplus', 'hminus', 'kplus', 'kminus', 'Pb', 'Pc', 'tb', 'tc']

    def set_dico_priors_arg(self, t_ref, Pb_prior=None, Pc_prior=None, eb_prior=None, ec_prior=None,
                            omegab_prior=None, omegac_prior=None, tb_prior=None, tc_prior=None, Phi_lims=None,
                            Phib_prior=None, Phic_prior=None):
        """Fill self.dico_priors_arg.

        The argument defines the marginal prior of the hidden parameters "Pb", "Pc", "eb", "ec", "omegab",
        "omegac". They should follow the following format: {"category": priorcat, "args": {"arg1":0, "arg2":1}}
        like for marginal priors
        You have to choose between the t_prior(s) and Phi_prior(s), you cannot use both for the same planet.

        :param float t_ref: Reference time for the definition of the boundaries of the prior on t.
            outside of the interval [t_ref - P/2, t_ref + P/2] the prior probability is 0.
        :param list_like_of_2_floats Phi_lims: Should only be set when t_prior is provided, otherwise it triggers an
            error. Defines the inferior and superior limits and phase (Phi) when t_prior is defined.
        """
        self.t_ref = t_ref
        for Pname, P_prior in zip(["Pb", "Pc"], [Pb_prior, Pc_prior]):
            if P_prior is None:
                P_prior = {"category": "jeffreys", "args": {"vmin": 0.01, "vmax": 1000.}}
            self.dico_priors_arg[Pname] = P_prior
        for tname, t_prior, Phiname, Phi_prior, planet_name in zip(["tb", "tc"], [tb_prior, tc_prior],
                                                                   ["Phib", "Phib"], [Phib_prior, Phic_prior],
                                                                   ["b", "c"]):
            if (t_prior is not None) and (Phi_prior is not None):
                raise ValueError("t_prior and Phi_prior cannot be set at the same time. It's one or the other.")
            elif (t_prior is None) and (Phi_prior is None):
                self.use_phi[planet_name] = True
                Phi_prior = {"category": "uniform", "args": {"vmin": -0.5, "vmax": 0.5}}
                self.dico_priors_arg["Phi"] = Phi_prior
            elif t_prior is not None:
                self.use_phi[planet_name] = False
                self.dico_priors_arg[tname] = t_prior
            else:
                self.use_phi[planet_name] = True
                self.dico_priors_arg["Phi"] = Phi_prior
                if Phi_lims is not None:
                    raise ValueError("Phi_lims should not be set when Phi_prior is provided")
        if any([use_phi for use_phi in self.use_phi.values()]):
            if Phi_lims is None:
                Phi_lims = (-0.5, 0.5)
            self.Phi_min, self.Phi_max = Phi_lims
        for ename, e_prior in zip(["eb", "ec"], [eb_prior, ec_prior]):
            if e_prior is None:
                e_prior = {"category": "uniform", "args": {"vmin": 0., "vmax": 1.}}
            self.dico_priors_arg[ename] = e_prior
        for omeganame, omega_prior in zip(["omegab", "omegac"], [omegab_prior, omegac_prior]):
            if omega_prior is None:
                omega_prior = {"category": "uniform", "args": {"vmin": -pi, "vmax": pi}}
            self.dico_priors_arg[omeganame] = omega_prior

    def create_logpdf(self, params):
        """Return the logarithmic probability density function for the joint prior.

        :param dict params: Dictionnary which contains the Parameter instances required by the prior.
            The keys are parameter keys in the self.params list and the values are the parameter instances
            as associated in the parameter file.
        :return function logpdf: log pdf the order in which the parameter should be provided is
            provided by self.params
        """
        (param_nb,
         arg_list,
         param_vector_name,
         ldict) = init_arglist_paramnb_arguments_ldict(key_param=key_param, param_vector_name=par_vec_name)
        dico_logpdf = {param: priorfunc.create_logpdf() for param, priorfunc in self.dico_priorfunction.items()}
        ldict["dico_logpdf"] = dico_logpdf
        ldict["getecc_plb_4_handk_fast"] = getecc_plb_4_handk_fast
        ldict["getecc_plc_4_handk_fast"] = getecc_plc_4_handk_fast
        ldict["getomega_plb_4_handk_fast"] = getomega_plb_4_handk_fast
        ldict["getomega_plc_4_handk_fast"] = getomega_plc_4_handk_fast
        ldict["inf"] = inf
        dico_text_params = {}
        for param_key in self.params:
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
                """.format(tab="    ", planet_name=planet_name, Phi_min=self.Phi_min, Phi_max=self.Phi_max, )
                check_Phi_lims += dedent(text_Phi_lims)
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
        dico_logpdf = self.dico_priorfunction
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
            The order of the parameters in the tuple is provided by self.params.
        """
        dico_ravs = {}
        for param, dico in self.dico_priors_arg.items():
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
                Phi = (tt - self.t_ref) / dico_ravs["P{}".format(planet_name)]
                indexes = where((Phi > self.Phi_max) | (Phi < self.Phi_min))[0]
                while len(indexes) > 0:
                    tt[planet_name][indexes] = self.dico_priors_arg["t{}".format(planet_name)]["priorfunc_instance"].ravs(nb_values=len(indexes))
                    indexes = where((Phi > self.Phi_max) | (Phi < self.Phi_min))[0]
        return hplus, hminus, kplus, kminus, dico_ravs["Pb"], dico_ravs["Pc"], tt["b"], tt["c"]


class Ptphiprior(Core_JointPrior_Function):
    """Prior defined for the Period and reference time of the orbit.
    """

    __category__ = "Ptphi"
    __mandatory_args__ = ['t_ref']
    __extra_args__ = ['P_prior', 't_prior', 'Phi_prior', 'Phi_lims']
    __params__ = ['P', 't']

    def set_dico_priors_arg(self, t_ref, P_prior=None, t_prior=None, Phi_prior=None, Phi_lims=None):
        """Fill self.dico_priors_arg and set self.t_ref and self.use_phi.

        The argument defines the marginal prior of the hidden parameters "P", "t" or "P", "Phi".
        They should follow the following format: {"category": priorcat, "args": {"arg1":0, "arg2":1}}
        like for marginal priors.
        You have to choose between t_prior and Phi_prior, you cannot use both.

        :param float t_ref: Reference time for the definition of the boundaries of the prior on t.
            outside of the interval [t_ref - P/2, t_ref + P/2] the prior probability is 0.
        :param list_like_of_2_floats Phi_lims: Should only be set when t_prior is provided, otherwise it triggers an
            error. Defines the inferior and superior limits and phase (Phi) when t_prior is defined.
        """
        self.t_ref = t_ref
        if P_prior is None:
            P_prior = {"category": "jeffreys", "args": {"vmin": 0.01, "vmax": 1000.}}
        self.dico_priors_arg["P"] = P_prior
        if (t_prior is not None) and (Phi_prior is not None):
            raise ValueError("t_prior and Phi_prior cannot be set at the same time. It's one or the other.")
        elif (t_prior is None) and (Phi_prior is None):
            self.use_phi = True
            Phi_prior = {"category": "uniform", "args": {"vmin": -0.5, "vmax": 0.5}}
            self.dico_priors_arg["Phi"] = Phi_prior
        elif t_prior is not None:
            self.use_phi = False
            self.dico_priors_arg["t"] = t_prior
            if Phi_lims is None:
                Phi_lims = (-0.5, 0.5)
            self.Phi_min, self.Phi_max = Phi_lims
        else:
            self.use_phi = True
            self.dico_priors_arg["Phi"] = Phi_prior
            if Phi_lims is not None:
                raise ValueError("Phi_lims should not be set when Phi_prior is provided")

    def create_logpdf(self, params):
        """Return the logarithmic probability density function for the joint prior.

        :param dict params: Dictionnary which contains the Parameter instances required by the prior.
            The keys are parameter keys in the self.params list and the values are the parameter instances
            as associated in the parameter file.
        :return function logpdf: log pdf the order in which the parameter should be provided is
            provided by self.params
        """
        (param_nb,
         arg_list,
         param_vector_name,
         ldict) = init_arglist_paramnb_arguments_ldict(key_param=key_param, param_vector_name=par_vec_name)
        dico_logpdf = {param: priorfunc.create_logpdf() for param, priorfunc in self.dico_priorfunction.items()}
        ldict["dico_logpdf"] = dico_logpdf
        dico_text_params = {}
        for param_key in self.params:
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
        dico_logpdf = self.dico_priorfunction

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
            The order of the parameters in the tuple is provided by self.params.
        """
        dico_ravs = {}
        for param, dico in self.dico_priors_arg.items():
            value = dico.get("value", None)
            if value is None:
                dico_ravs[param] = dico["priorfunc_instance"].ravs(nb_values=nb_values)
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
                dico_ravs["t"][indexes] = self.dico_priors_arg["t"]["priorfunc_instance"].ravs(nb_values=len(indexes))
                indexes = where((Phi > self.Phi_max) | (Phi < self.Phi_min))[0]
            return dico_ravs["P"], dico_ravs["t"]
