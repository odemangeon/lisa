"""
Prior functions module.
"""
from __future__ import division
from logging import getLogger

from numpy import pi, inf

from ...core.prior.core_prior import Core_Prior_Function, Core_JointPriorFunction
from ...core.prior.manager_prior import Manager_Prior
from ....tools.convert import getecc_plc_4_handk_fast, getecc_plc_4_handk_fast, getomega_plb_4_handk_fast, getomega_plc_4_handk_fast
from ....tools.convert import gethplus_fast, gethminus_fast, getkplus_fast, getkminus_fast


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
        dico_priors_arg = {}
        for Pname, P_prior in zip(["Pb", "Pc"], [Pb_prior, Pc_prior]):
            if P_prior is None:
                P_prior = {"category": "jeffreys", "args": {"vmin": 0.01, "vmax": 1000.}}
            dico_priors_arg[Pname] = P_prior
        for ename, e_prior in zip(["eb", "ec"], [eb_prior, ec_prior]):
            if e_prior is None:
                e_prior = {"category": "uniform", "args": {"vmin": 0., "vmax": 1.}}
            dico_priors_arg[ename] = e_prior
        for omeganame, omega_prior in zip(["omegab", "omegac"], [omegab_prior, omegac_prior]):
            if omega_prior is None:
                omega_prior = {"category": "uniform", "args": {"vmin": -pi, "vmax": pi}}
            dico_priors_arg[omeganame] = omega_prior
        self.dico_priorfunction = {}
        for param, prior_args in dico_priors_arg.items():
            if manager.is_available_priortype(prior_args["category"]):
                priorfunction_subclass = manager.get_priorfunc_subclass(prior_args["category"])
                priorfunction_subclass.check_args(list(prior_args["args"].keys()))
            else:
                raise ValueError("prior_category {} is not in the list of available prior types: {}"
                                 "".format(prior_args["category"], manager.get_available_priors()))
            self.dico_priorfunction[param] = priorfunction_subclass(**prior_args["args"])

    def create_logpdf(self):
        dico_logpdf = {param: priorfunc.create_logpdf() for param, priorfunc in self.dico_priorfunction.items()}

        def logpdf(hplus, hminus, kplus, kminus, Pb, Pc):
            eb = getecc_plb_4_handk_fast(hplus, hminus, kplus, kminus, Pc/Pb)
            ec = getecc_plc_4_handk_fast(hplus, hminus, kplus, kminus)
            omegab = getomega_plb_4_handk_fast(hplus, hminus, kplus, kminus)
            omegac = getomega_plc_4_handk_fast(hplus, hminus, kplus, kminus)
            return (dico_logpdf["Pb"](Pb) + dico_logpdf["Pc"](Pc) + dico_logpdf["eb"](eb) + dico_logpdf["ec"](ec) +
                    dico_logpdf["omegab"](omegab) + dico_logpdf["omegac"](omegac))

        return logpdf

    def logpdf(self, hplus, hminus, kplus, kminus, Pb, Pc):

        dico_logpdf = self.dico_priorfunction

        eb = getecc_plb_4_handk_fast(hplus, hminus, kplus, kminus, Pc/Pb)
        ec = getecc_plc_4_handk_fast(hplus, hminus, kplus, kminus)
        omegab = getomega_plb_4_handk_fast(hplus, hminus, kplus, kminus)
        omegac = getomega_plc_4_handk_fast(hplus, hminus, kplus, kminus)
        return (dico_logpdf["Pb"](Pb) + dico_logpdf["Pc"](Pc) + dico_logpdf["eb"](eb) + dico_logpdf["ec"](ec) +
                dico_logpdf["omegab"](omegab) + dico_logpdf["omegac"](omegac))

    def ravs(self):
        dico_ravs = {param: priorfunction.ravs() for param, priorfunction in self.dico_priorfunction.items()}
        hplus = gethplus_fast(dico_ravs["Pb"]/dico_ravs["Pc"], dico_ravs["eb"], dico_ravs["ec"], dico_ravs["omegab"], dico_ravs["omegac"])
        hminus = gethminus_fast(dico_ravs["Pb"]/dico_ravs["Pc"], dico_ravs["eb"], dico_ravs["ec"], dico_ravs["omegab"], dico_ravs["omegac"])
        kplus = getkplus_fast(dico_ravs["Pb"]/dico_ravs["Pc"], dico_ravs["eb"], dico_ravs["ec"], dico_ravs["omegab"], dico_ravs["omegac"])
        kminus = getkminus_fast(dico_ravs["Pb"]/dico_ravs["Pc"], dico_ravs["eb"], dico_ravs["ec"], dico_ravs["omegab"], dico_ravs["omegac"])
        return hplus, hminus, kplus, kminus, dico_ravs["Pb"], dico_ravs["Pc"]
