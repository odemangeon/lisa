#!/usr/bin/python
# -*- coding:  utf-8 -*-
import source.posterior.core.prior.manager_prior as mgr
from source.posterior.core.prior.prior_function import pf

manager = mgr.Manager_Prior()

manager.add_available_prior(pf.UniformPrior)
manager.add_available_prior(pf.NormalPrior)
manager.add_available_prior(pf.LogNormPrior)
manager.add_available_prior(pf.JeffreysPrior)
manager.add_available_prior(pf.SinePrior)
