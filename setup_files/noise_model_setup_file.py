#!/usr/bin/python
# -*- coding:  utf-8 -*-
import source.posterior.core.likelihood.manager_noise_model as mgr
import source.posterior.core.likelihood.noise_model as nm
import source.posterior.exoplanet.likelihood.stellar_activity_noisemodel as sanm

manager = mgr.Manager_NoiseModel()

manager.add_available_noisemodel(nm.GaussianNoiseModel)
manager.add_available_noisemodel(nm.GaussianNoiseModel_wdfmjitter)
manager.add_available_noisemodel(nm.GaussianNoiseModel_wjittermulti)
manager.add_available_noisemodel(nm.GaussianNoiseModel_wjitteradd)
manager.add_available_noisemodel(nm.GaussianNoiseModel_wjittermultiBaluev)
manager.add_available_noisemodel(nm.GaussianNoiseModel_wjitteraddBaluev)
manager.add_available_noisemodel(sanm.StellarActNoiseModel)
