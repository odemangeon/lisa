#!/usr/bin/python
# -*- coding:  utf-8 -*-

# Light-curve parametrisation file of WASP-151
transit_model = 'pytransit-MandelAgol'

# Limb-darkening.
# Associate LC instrument models with LD param containers.
# Available limb-darkening models are:
# ['quadratic', 'linear', 'uniform']
LDs = {'A': {'IAC80_default0': 'LDR',
             'IAC80_default1': 'LDR',
             'EulerCam_default': 'LDNG',
             'K2_default': 'LDKp',
             'TRAPPIST_default': 'LDz',

             'LD_models': {'LDz': 'quadratic',
                           'LDNG': 'quadratic',
                           'LDKp': 'quadratic',
                           'LDR': 'quadratic'}
             }
       }

# Supersampling and exposure_time
SuperSamps = {'IAC80_default0': {'supersamp':  1, 'exptime': 0.02043402778},
              'IAC80_default1': {'supersamp':  1, 'exptime': 0.02043402778},
              'EulerCam_default': {'supersamp': 1, 'exptime': 0.02043402778},
              'K2_default': {'supersamp': 10, 'exptime': 0.02043402778},
              'TRAPPIST_default': {'supersamp': 1, 'exptime': 0.02043402778},
              }
