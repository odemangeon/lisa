#!/usr/bin/python
# -*- coding:  utf-8 -*-
import lisa.posterior.core.likelihood.manager_noise_model as mgr
import lisa.posterior.core.likelihood.gaussian_noisemodelconfiguration as gauss
import lisa.posterior.core.likelihood.GP1D_noisemodels as gp1d

manager = mgr.Manager_NoiseModel()

manager.add_available_noisemodel(gauss.GaussianNoiseModel)
manager.add_available_noisemodel(gp1d.GP1DNoiseModel)
