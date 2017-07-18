#!/usr/bin/python
# -*- coding:  utf-8 -*-

# Light-curve parametrisation file of HD106315
transit_model = 'pytransit-MandelAgol'

# Limb-darkening.
# Associate LC instrument models with LD param containers.
# Available limb-darkening models are:
# ['quadratic', 'linear', 'uniform']
LDs = {'A': {'K2_def': 'default',

             'LD_models': {'default': 'quadratic'}
             }
       }

# Supersampling and exposure_time
SuperSamps = {'K2_def': {'supersamp': 7, 'exptime': 0.02043402778},
              }
