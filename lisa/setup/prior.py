#!/usr/bin/python
# -*- coding:  utf-8 -*-
from ..posterior.core.prior.core_prior import Manager_Prior
from ..posterior.core.prior.prior_function import UniformPrior, NormalPrior, LogNormPrior, JeffreysPrior, SinePrior, PolarPrior, BetaPrior, SupInfprior, Sumprior 
from ..posterior.exoplanet.prior.prior_function import HKPPrior, HKPtPrior, Ptphiprior, Transitingprior, TransitingRhoprior, BetaEccPrior, SupInfLogPtauprior, kelp_loaded, KelpInhomegeousReflectionprior


manager = Manager_Prior()

manager.add_available_prior(UniformPrior)
manager.add_available_prior(NormalPrior)
manager.add_available_prior(LogNormPrior)
manager.add_available_prior(JeffreysPrior)
manager.add_available_prior(SinePrior)
manager.add_available_prior(PolarPrior)
manager.add_available_prior(HKPPrior)
manager.add_available_prior(HKPtPrior)
manager.add_available_prior(Ptphiprior)
manager.add_available_prior(Transitingprior)
manager.add_available_prior(TransitingRhoprior)
manager.add_available_prior(BetaPrior)
manager.add_available_prior(BetaEccPrior)
manager.add_available_prior(SupInfprior)
manager.add_available_prior(SupInfLogPtauprior)
manager.add_available_prior(Sumprior)
if kelp_loaded:
    manager.add_available_prior(KelpInhomegeousReflectionprior)
