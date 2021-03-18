#!/usr/bin/python
# -*- coding:  utf-8 -*-

# Light-curve parametrisation file of WASP-151
transit_model = 'batman'

# Limb-darkening.
# Associate LC instrument models with LD param containers.
# Available limb-darkening models are:
# ['quadratic', 'nonlinear', 'exponential', 'logarithmic', 'squareroot', 'linear', 'uniform', 'custom']
LDs = {'A': {'LC_K2_default': 'LDKp',
             'LC_EulerCam_default': 'LDNG',
             'LC_IAC80_default0': 'LDR',
             'LC_IAC80_default1': 'LDR',
             'LC_TRAPPIST_default': 'LDz',

             'LD_models': {'LDz': 'quadratic',
                           'LDNG': 'quadratic',
                           'LDKp': 'quadratic',
                           'LDR': 'quadratic'}
             }
       }

# Supersampling and exposure_time
SuperSamps = {'LC_K2_default': {'supersamp': 10, 'exptime': 0.02043402778},
              'LC_EulerCam_default': {'supersamp': 1, 'exptime': 0.02043402778},
              'LC_IAC80_default0': {'supersamp': 1, 'exptime': 0.02043402778},
              'LC_IAC80_default1': {'supersamp': 1, 'exptime': 0.02043402778},
              'LC_TRAPPIST_default': {'supersamp': 1, 'exptime': 0.02043402778},
              }
