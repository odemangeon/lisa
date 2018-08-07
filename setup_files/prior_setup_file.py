#!/usr/bin/python
# -*- coding:  utf-8 -*-
import source.posterior.core.prior.manager_prior as mgr
import source.posterior.core.prior.prior_function as pf_stdrd
import source.posterior.exoplanet.prior.prior_function as pf_exop


manager = mgr.Manager_Prior()

manager.add_available_prior(pf_stdrd.UniformPrior)
manager.add_available_prior(pf_stdrd.NormalPrior)
manager.add_available_prior(pf_stdrd.LogNormPrior)
manager.add_available_prior(pf_stdrd.JeffreysPrior)
manager.add_available_prior(pf_stdrd.SinePrior)
manager.add_available_prior(pf_exop.HKPPrior)
