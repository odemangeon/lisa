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
                                      'prior': {'args': {'mu': 0.0284, 'sigma': np.sqrt(0.001**2 + 0.00030**2)},  # From TS3 Tom Wilson and script_prior
                                                'category': 'normal',
                                                'joint_prior_ref': None},
                                      'unit': 'wo unit',
                                      'value': None},
                           'contam': {'duplicate': None,
                                      'free': False,
                                      'prior': {'args': {'mu': 0.0284, 'sigma': 0.001},  # From TS3 Tom Wilson
                                                'category': 'normal',
                                                'joint_prior_ref': None},
                                      'unit': 'wo unit',
                                      'value': 0},
                           'jitter': {'duplicate': None,
                                      'free': True,
                                      'prior': {'args': {'vmax': 0.0012, 'vmin': 0.0},
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
             'prior': {'args': {'mu': 0.2299499918941955, 'sigma': 0.015254611012997882, 'lims': [0, np.inf]},  # from TS3 M and R estimate (https://docs.google.com/spreadsheets/d/12KA3-A3h5T7IJR5J7T1DE9SYTtjoS8rI6-98HwgQFF4/edit#gid=1232635509)
                       'category': 'normal',
                       'joint_prior_ref': None},
             'unit': None,
             'value': None}}


# planets
b = {'Frat': {'duplicate': None,
              'free': True,
              'prior': {'args': {'vmin': 0.0, 'vmax': 1e-3},  # Arbitrary
                        'category': 'uniform',
                        'joint_prior_ref': None},
              'unit': None,
              'value': None},
     'P': {'duplicate': None,
           'free': True,
           'prior': {'args': {'mu': 1.809881104375426, 'sigma': 2.1e-07, 'lims': [0, np.inf]},
                     'category': 'normal',
                     'joint_prior_ref': None},
           'unit': None,
           'value': None},
     'Rrat': {'duplicate': None,
              'free': True,
              'prior': {'args': {'mu': 0.10921646539374623, 'sigma': 9e-05},
                        'category': 'normal',
                        'joint_prior_ref': None},
              'unit': None,
              'value': None},
     'cosinc': {'duplicate': None,
                'free': True,
                'prior': {'args': {'mu': 0.006609044877456989, 'sigma': 0.0006, 'lims': [0, 1]},  # From Ehrenreich+2020: https://arxiv.org/pdf/2003.05528.pdf
                          'category': 'normal',
                          'joint_prior_ref': None},
                'unit': 'w/o unit',
                'value': None},
     'ecosw': {'duplicate': None,
               'free': True,
               'prior': {'args': {'mu': 0.002297509022196895, 'sigma': 0.0015},
                         'category': 'normal',
                         'joint_prior_ref': None},
               'unit': 'w/o unit',
               'value': None},
     'esinw': {'duplicate': None,
               'free': True,
               'prior': {'args': {'mu': 0.032461706018839964, 'sigma': 0.008},
                         'category': 'normal',
                         'joint_prior_ref': None},
               'unit': 'w/o unit',
               'value': None},
     'tic': {'duplicate': None,
             'free': True,
             'prior': {'args': {'mu': 1080.625326793695, 'sigma': 0.00016},
                       'category': 'normal',
                       'joint_prior_ref': None},
             'unit': None,
             'value': None}}


# LDs
A_default = {}

# GravitionalGroups

WASP76 = {}

# Joint parameters
# Define below the joint parameter distributions.
joint_prior = {}
