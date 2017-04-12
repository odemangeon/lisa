#!/usr/bin/python
# -*- coding:  utf-8 -*-
import source.posterior.core.likelihood.manager_noise_model as mgr
import source.posterior.core.likelihood.jitter_noise_model as jnm
import source.posterior.exoplanet.likelihood.stellar_activity_noisemodel as sanm

manager = mgr.Manager_NoiseModel()

manager.add_available_noisemodel(jnm.GaussianNoiseModel)
manager.add_available_noisemodel(jnm.GaussianNoiseModel_wdfmjitter)
manager.add_available_noisemodel(jnm.GaussianNoiseModel_wjittermulti)
manager.add_available_noisemodel(jnm.GaussianNoiseModel_wjitteradd)
manager.add_available_noisemodel(jnm.GaussianNoiseModel_wjittermultiBaluev)
manager.add_available_noisemodel(jnm.GaussianNoiseModel_wjitteraddBaluev)
manager.add_available_noisemodel(sanm.StellarActNoiseModel)
