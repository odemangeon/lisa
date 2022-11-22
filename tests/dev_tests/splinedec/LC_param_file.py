#!/usr/bin/python
# -*- coding:  utf-8 -*-

# Light-curve parametrisation file of WASP-76

# Which model do you want to use for the transit ?
transit_model = {'b': {'do': True,
                       'model4instrument': {'LC_CHEOPS_inst0': ''},
                       'model_definitions': {'': {'category': 'batman',
                                                  'param_extensions': {'planet': {'Rrat': ''},
                                                                       'star': {}}}}}}

# Limb-darkening.
# Associate LC instrument models with LD param containers.
# Available limb-darkening models are:
# ['quadratic', 'nonlinear', 'exponential', 'logarithmic', 'squareroot', 'linear', 'uniform', 'custom']
LDs = {'A': {'LC_CHEOPS_inst0': 'default',

             'LD_models': {'default': 'quadratic'}
             }
       }

# Supersampling and exposure_time
SuperSamps = {'LC_CHEOPS_inst0': {'supersamp': 1, 'exptime': 0.02043402778},
              }

# Which model do you want to use for the phase curve ?
phasecurve_model = {'b': {'do': False,
                          'model4instrument': {'LC_CHEOPS_inst0': ['']},
                          'model_definitions': {'': {'args': {'factor_period': 1,
                                                              'flux_offset': 'param',
                                                              'occultation': True,
                                                              'phase_offset': 'param',
                                                              'sincos': 'cos'},
                                                     'category': 'sincos',
                                                     'param_extensions': {'planet': {'A': '',
                                                                                     'Foffset': '',
                                                                                     'Phi': '',
                                                                                     'Rrat': ''},
                                                                          'star': {}}}}}}

# Which model do you want to use for the occultation ?
# WARNING: Some phasecurve models already include the occultation. No need to add it twice in these cases.
occultation_model = {'b': {'do': False,
                           'model4instrument': {'LC_CHEOPS_inst0': ''},
                           'model_definitions': {'': {'category': 'batman',
                                                      'param_extensions': {'planet': {'Frat': '',
                                                                                      'Rrat': ''},
                                                                           'star': {}}}}}}

# Polynomial trends
polynomial_model = {'A': {'do': False, 'order': 0, 'tref': None},
                    'LC_CHEOPS_inst0': {'do': True, 'order': 0, 'tref': None}}

# Decorrelation
#
# Define if you want to include decorrelation models.
# In the dictionary below, each key corresponds to an instrument model and has for value a dictionary with the following structure:
# {"do": True/False,
#  "<decorrelation_model_name>": {"<Indicator instrument model name>": {decorrelation_model_options},  ...}
# If "do" is False no decorrelation is performed for the data taken with the instrument model.
# Otherwise, for each available decorrelation model you need to provide the name of the instrument
# model of the indicators that you want to use and the options for the decorrelation method
#
# The list of datasets for each LC instrument model are:
# {'LC_CHEOPS_inst0': ['LC_WASP-76_CHEOPS_100']}
#
# The list of datasets for each IND instrument model are:
# {'IND-ROLL_CHEOPS_inst': ['IND-ROLL_WASP-76_CHEOPS_100'], 'IND-CX_CHEOPS_inst': ['IND-CX_WASP-76_CHEOPS_100'], 'IND-CY_CHEOPS_inst': ['IND-CY_WASP-76_CHEOPS_100'], 'IND-TF_CHEOPS_inst': ['IND-TF_WASP-76_CHEOPS_100'], 'IND-BKG_CHEOPS_inst': ['IND-BKG_WASP-76_CHEOPS_100']}
#
# The format of decorrelation_model_options dictionary depends on the decorrelation model used
# linear: {'quantity': 'raw'}
# spline: {'category': 'spline', 'spline_type': 'UnivariateSpline' or 'LSQUnivariateSpline', 'spline_kwargs': {'k': 3}, 'match datasets': {<dataset name>: <indicator dataset name>}}
# bispline: {'category': 'bispline', 'spline_type': 'SmoothBivariateSpline' or 'LSQBivariateSpline', 'spline_kwargs': {'kx': 3, 'ky': 3}, 'match datasets': {<dataset name>: {'X': <indicator dataset name>, 'Y':<indicator dataset name>}}


decorrelation_model = {'LC_CHEOPS_inst0': {'do': False,
                                           'what to decorrelate': {'add_2_totalflux': {'linear': {}},
                                                                   'multiply_2_totalflux': {'linear': {}}}}}
decorrelation_likelihood = {'do': False, 'model_definitions': {}, 'order_models': []}