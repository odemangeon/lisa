#!/usr/bin/python
# -*- coding:  utf-8 -*-
from source.posterior.core.prior.core_prior import Manager_Prior
import source.posterior.core.prior.prior_function as pf_stdrd
import source.posterior.exoplanet.prior.prior_function as pf_exop


manager = Manager_Prior()

manager.add_available_prior(pf_stdrd.UniformPrior)
manager.add_available_prior(pf_stdrd.NormalPrior)
manager.add_available_prior(pf_stdrd.LogNormPrior)
manager.add_available_prior(pf_stdrd.JeffreysPrior)
manager.add_available_prior(pf_stdrd.SinePrior)
manager.add_available_prior(pf_stdrd.PolarPrior)
manager.add_available_prior(pf_exop.HKPPrior)
manager.add_available_prior(pf_exop.HKPtPrior)
manager.add_available_prior(pf_exop.Ptphiprior)
manager.add_available_prior(pf_exop.Transitingprior)
manager.add_available_prior(pf_exop.TransitingRhoprior)
