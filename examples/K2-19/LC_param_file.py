#!/usr/bin/python
# -*- coding:  utf-8 -*-

# Light-curve parametrisation file of K2-19
transit_model = 'batman'

# Limb-darkening.
# Associate LC instrument models with LD param containers.
# Available limb-darkening models are:
# ['quadratic', 'nonlinear', 'exponential', 'logarithmic', 'squareroot', 'linear', 'uniform', 'custom']
LDs = {'A': {'LC_Balesta_def': 'LDKp',
             'LC_C2PU_def': 'LDC2PU',
             'LC_K2_def': 'LDBalesta',
             'LC_NITES_def': 'LDNITES',

             'LD_models': {'LDKp': 'quadratic', 'LDC2PU': 'quadratic', 'LDBalesta': 'quadratic', 'LDNITES': 'quadratic'}
             }
       }

# Supersampling and exposure_time
SuperSamps = {'LC_Balesta_def': {'supersamp': 1, 'exptime': 0.02043402778},
              'LC_C2PU_def': {'supersamp': 1, 'exptime': 0.02043402778},
              'LC_K2_def': {'supersamp': 10, 'exptime': 0.02043402778},
              'LC_NITES_def': {'supersamp': 1, 'exptime': 0.02043402778},
              }
