#!/usr/bin/python
# -*- coding:  utf-8 -*-
import lisa.posterior.core.likelihood.manager_noise_model as mgr
import lisa.posterior.core.likelihood.gaussian_noisemodel as gauss
import lisa.posterior.exoplanet.likelihood.GP1D_noisemodel as gp1d

manager = mgr.Manager_NoiseModel()

manager.add_available_noisemodel(gauss.GaussianNoiseModel)
manager.add_available_noisemodel(gp1d.GP1DNoiseModel)
