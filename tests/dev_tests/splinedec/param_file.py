#!/usr/bin/python
# -*- coding:  utf-8 -*-
# Parametrisation file of WASP-76
import numpy as np

# Parameters

# instruments


# instruments LC
LC = {'CHEOPS': {'Dataset': {100: 'inst0'},
                 'inst0': {'DeltaF': {'duplicate': None,
                                      'free': True,
                                      'prior': {'args': {'vmax': 1.0, 'vmin': 0.0},
                                                'category': 'uniform',
                                                'joint_prior_ref': None},
                                      'unit': 'wo unit',
                                      'value': None},
                           'contam': {'duplicate': None,
                                      'free': False,
                                      'prior': {'args': {'vmax': 1.0, 'vmin': 0.0},
                                                'category': 'uniform',
                                                'joint_prior_ref': None},
                                      'unit': 'wo unit',
                                      'value': 0},
                           'jitter': {'duplicate': None,
                                      'free': True,
                                      'prior': {'args': {'vmax': 1.0, 'vmin': 0.0},
                                                'category': 'uniform',
                                                'joint_prior_ref': None},
                                      'unit': None,
                                      'value': None}}}}

# instruments IND-ROLL
INDROLL = {'CHEOPS': {'Dataset': {100: 'inst'}, 'inst': {}}}

# instruments IND-CX
INDCX = {'CHEOPS': {'Dataset': {100: 'inst'}, 'inst': {}}}

# instruments IND-CY
INDCY = {'CHEOPS': {'Dataset': {100: 'inst'}, 'inst': {}}}

# instruments IND-TF
INDTF = {'CHEOPS': {'Dataset': {100: 'inst'}, 'inst': {}}}

# instruments IND-BKG
INDBKG = {'CHEOPS': {'Dataset': {100: 'inst'}, 'inst': {}}}
# stars
A = {'rho': {'duplicate': None,
             'free': True,
             'prior': {'args': {'vmax': 1.0, 'vmin': 0.0},
                       'category': 'uniform',
                       'joint_prior_ref': None},
             'unit': None,
             'value': None}}


# planets
b = {'Frat': {'duplicate': None,
              'free': True,
              'prior': {'args': {'vmax': 1.0, 'vmin': 0.0},
                        'category': 'uniform',
                        'joint_prior_ref': None},
              'unit': None,
              'value': None},
     'P': {'duplicate': None,
           'free': True,
           'prior': {'args': {'vmax': 1.0, 'vmin': 0.0},
                     'category': 'uniform',
                     'joint_prior_ref': None},
           'unit': None,
           'value': None},
     'Rrat': {'duplicate': None,
              'free': True,
              'prior': {'args': {'vmax': 1.0, 'vmin': 0.0},
                        'category': 'uniform',
                        'joint_prior_ref': None},
              'unit': None,
              'value': None},
     'cosinc': {'duplicate': None,
                'free': True,
                'prior': {'args': {'vmax': 1.0, 'vmin': 0.0},
                          'category': 'uniform',
                          'joint_prior_ref': None},
                'unit': 'w/o unit',
                'value': None},
     'ecosw': {'duplicate': None,
               'free': True,
               'prior': {'args': {'vmax': 1.0, 'vmin': 0.0},
                         'category': 'uniform',
                         'joint_prior_ref': None},
               'unit': 'w/o unit',
               'value': None},
     'esinw': {'duplicate': None,
               'free': True,
               'prior': {'args': {'vmax': 1.0, 'vmin': 0.0},
                         'category': 'uniform',
                         'joint_prior_ref': None},
               'unit': 'w/o unit',
               'value': None},
     'tic': {'duplicate': None,
             'free': True,
             'prior': {'args': {'vmax': 1.0, 'vmin': 0.0},
                       'category': 'uniform',
                       'joint_prior_ref': None},
             'unit': None,
             'value': None}}


# LDs
A_default = {}

# GravitionalGroups

WASP76 = {}

# Joint parameters
# Define below the joint parameter distributions.
joint_prior = {# Example:
               # 'priorhkP': {'category': 'hkP', 'args': {'Pb_prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0} } },
               #              'params': {'hplus': 'K219_hplus', 'hminus': 'K219_hminus',
               #                         'kplus': 'K219_kplus', 'kminus': 'K219_kminus',
               #                         'Pb': 'K219_b_P', 'Pc': 'K219_c_P'}
               #              }
               }
