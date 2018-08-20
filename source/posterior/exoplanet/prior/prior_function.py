"""
Prior functions module.
"""
from __future__ import division
from logging import getLogger
from textwrap import dedent

from numpy import pi, inf

from ...core.prior.core_prior import Core_Prior_Function, Core_JointPriorFunction
from ...core.prior.manager_prior import Manager_Prior
from ....tools.convert import getecc_plb_4_handk_fast, getecc_plc_4_handk_fast, getomega_plb_4_handk_fast, getomega_plc_4_handk_fast
from ....tools.convert import gethplus, gethminus, getkplus, getkminus
from ....tools.function_w_doc import DocFunction
from ....tools.function_from_text_toolbox import init_arglist_paramnb_arguments_ldict, add_param_argument, par_vec_name, key_param, get_function_arglist



## logger object
logger = getLogger()
## manager object
manager = Manager_Prior()
# manager.load_setup() ## Cannot be done otherwise there is an import loop


# TODO: SeomegaPrior


# TODO: b and c planets are differentiated by their period. b usually have a smaller period than c.
# But it's not always the case. It would be good to have a way to specify which planet has the smaller
# period and then put to -inf the log period when this is not respected.
class HKPPrior(Core_JointPriorFunction):

    __category__ = "hkP"
    __mandatory_args__ = []
    __extra_args__ = ['Pb_prior', 'Pc_prior', 'eb_prior', 'ec_prior', 'omegab_prior', 'omegac_prior']
    __params__ = ['hplus', 'hminus', 'kplus', 'kminus', 'Pb', 'Pc']

    def __init__(self, Pb_prior=None, Pc_prior=None, eb_prior=None, ec_prior=None,
                 omegab_prior=None, omegac_prior=None):
        self.dico_priors_arg = {}
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
        for param, prior_args in self.dico_priors_arg.items():
            if manager.is_available_priortype(prior_args["category"]):
                priorfunction_subclass = manager.get_priorfunc_subclass(prior_args["category"])
                priorfunction_subclass.check_args(list(prior_args["args"].keys()))
            else:
                raise ValueError("prior_category {} is not in the list of available prior types: {}"
                                 "".format(prior_args["category"], manager.get_available_priors()))
            self.dico_priors_arg[param]["priorfunc_instance"] = priorfunction_subclass(**prior_args["args"])

    @property
    def dico_priorfunction(self):
        """Dictionary containing the prior function instances for each physical parameters.

        The physical parameter keys are Pb, Pc, eb, ec, omegab, omegac
        """
        return {param: self.dico_priors_arg[param]["priorfunc_instance"] for param in self.dico_priors_arg.keys()}

    def create_logpdf(self, params):
        """Create the log pdf.

        :param dict params: Dictionnary which contains the Parameter instances required by the prior.
            The keys are parameter keys in the self.params list and the values are the parameter instances
        :return function logpdf: log pdf
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
            dico_text_params[param_key] = add_param_argument(param=params[param_key], arg_list=arg_list,
                                                             key_param=key_param, param_nb=param_nb,
                                                             param_vector_name=par_vec_name)
        function_name = "logpdf_{}".format(self.category)
        text_function = """
        def {function_name}({param_vector_name}):
            if {Pc}/{Pb} < 0:
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
        exec(text_function, ldict)
        return DocFunction(ldict[function_name], get_function_arglist(arg_list))

    def logpdf(self, hplus, hminus, kplus, kminus, Pb, Pc):

        dico_logpdf = self.dico_priorfunction

        eb = getecc_plb_4_handk_fast(hplus, hminus, kplus, kminus, Pc/Pb)
        ec = getecc_plc_4_handk_fast(hplus, hminus, kplus, kminus)
        omegab = getomega_plb_4_handk_fast(hplus, hminus, kplus, kminus)
        omegac = getomega_plc_4_handk_fast(hplus, hminus, kplus, kminus)
        return (dico_logpdf["Pb"](Pb) + dico_logpdf["Pc"](Pc) + dico_logpdf["eb"](eb) + dico_logpdf["ec"](ec) +
                dico_logpdf["omegab"](omegab) + dico_logpdf["omegac"](omegac))

    def ravs(self, nb_values=1):
        dico_ravs = {}
        for param, dico in self.dico_priors_arg.items():
            value = dico.get("value", None)
            if value is None:
                dico_ravs[param] = dico["priorfunc_instance"].ravs(nb_values=nb_values)
            else:
                dico_ravs[param] = np.ones(nb_values) * value
            if dico_ravs[param].size == 1:
                dico_ravs[param] = dico_ravs[param][0]
        hplus = gethplus(dico_ravs["Pb"]/dico_ravs["Pc"], dico_ravs["eb"], dico_ravs["ec"], dico_ravs["omegab"], dico_ravs["omegac"])
        hminus = gethminus(dico_ravs["Pb"]/dico_ravs["Pc"], dico_ravs["eb"], dico_ravs["ec"], dico_ravs["omegab"], dico_ravs["omegac"])
        kplus = getkplus(dico_ravs["Pb"]/dico_ravs["Pc"], dico_ravs["eb"], dico_ravs["ec"], dico_ravs["omegab"], dico_ravs["omegac"])
        kminus = getkminus(dico_ravs["Pb"]/dico_ravs["Pc"], dico_ravs["eb"], dico_ravs["ec"], dico_ravs["omegab"], dico_ravs["omegac"])
        return hplus, hminus, kplus, kminus, dico_ravs["Pb"], dico_ravs["Pc"]
