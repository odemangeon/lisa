#!/usr/bin/python
# -*- coding:  utf-8 -*-

# Light-curve parametrisation file of WASP-76

# Which model do you want to use for the transit ?
transit_model = {'b': {'do': True,
                       'model4instrument': {'LC_CHEOPS_inst0': '',
                                            'LC_CHEOPS_inst1': '1',
                                            'LC_CHEOPS_inst2': '2',
                                            'LC_CHEOPS_inst3': '3',
                                            'LC_CHEOPS_inst4': '4'
                                            },
                       'model_definitions': {'': {'model': 'batman',
                                                  'new_parameter': {'Rrat': True},
                                                  'orbital_model': '0'
                                                  },
                                             '1': {'model': 'batman',
                                                   'new_parameter': {'Rrat': ''},
                                                   'orbital_model': '1'
                                                   },
                                             '2': {'model': 'batman',
                                                   'new_parameter': {'Rrat': ''},
                                                   'orbital_model': '2'
                                                   },
                                             '3': {'model': 'batman',
                                                   'new_parameter': {'Rrat': ''},
                                                   'orbital_model': '3'
                                                   },
                                             '4': {'model': 'batman',
                                                   'new_parameter': {'Rrat': ''},
                                                   'orbital_model': '4'
                                                   },
                                             }
                       }
                 }

# Limb-darkening.
# Associate LC instrument models with LD param containers.
# Available limb-darkening models are:
# ['quadratic', 'nonlinear', 'exponential', 'logarithmic', 'squareroot', 'linear', 'uniform', 'custom']
LDs = {'A': {'LC_CHEOPS_inst0': 'LD',
             'LC_CHEOPS_inst1': 'LD',
             'LC_CHEOPS_inst2': 'LD',
             'LC_CHEOPS_inst3': 'LD',
             'LC_CHEOPS_inst4': 'LD',

             'LD_models': {'LD': 'nonlinear'}
             }
       }

# Supersampling and exposure_time
SuperSamps = {'LC_CHEOPS_inst0': {'supersamp': 1, 'exptime': 0.02043402778},
              'LC_CHEOPS_inst1': {'supersamp': 1, 'exptime': 0.02043402778},
              'LC_CHEOPS_inst2': {'supersamp': 1, 'exptime': 0.02043402778},
              'LC_CHEOPS_inst3': {'supersamp': 1, 'exptime': 0.02043402778},
              'LC_CHEOPS_inst4': {'supersamp': 1, 'exptime': 0.02043402778},
              }

# Which model do you want to use for the phase curve ?
phasecurve_model = {'b': {'do': False,
                          'model4instrument': {'LC_CHEOPS_inst0': '',
                                               'LC_CHEOPS_inst1': '',
                                               'LC_CHEOPS_inst2': '',
                                               'LC_CHEOPS_inst3': '',
                                               'LC_CHEOPS_inst4': ''
                                               },
                          'model_definitions': {'': {'args': {'factor_period': 1,
                                                              'flux_offset': 'param',
                                                              'occultation': True,
                                                              'phase_offset': 'param',
                                                              'sincos': 'cos'},
                                                     'model': 'sincos',
                                                     'new_parameter': {'amp': True,
                                                                       'flux_offset': True,
                                                                       'phase_offset': True},
                                                     'orbital_model': ''}}}}

# Which model do you want to use for the occultation ?
# WARNING: Some phasecurve models already include the occultation. No need to add it twice in these cases.
occultation_model = {'b': {'do': False,
                           'model4instrument': {'LC_CHEOPS_inst0': '',
                                                'LC_CHEOPS_inst1': '',
                                                'LC_CHEOPS_inst2': '',
                                                'LC_CHEOPS_inst3': '',
                                                'LC_CHEOPS_inst4': ''},
                           'model_definitions': {'': {'model': 'batman', 'orbital_model': ''}}}}

# Polynomial trends
polynomial_model = {'A': {'do': False, 'order': 0, 'tref': None},
                    'LC_CHEOPS_inst0': {'do': True, 'order': 0, 'tref': None},
                    'LC_CHEOPS_inst1': {'do': True, 'order': 0, 'tref': None},
                    'LC_CHEOPS_inst2': {'do': True, 'order': 0, 'tref': None},
                    'LC_CHEOPS_inst3': {'do': True, 'order': 0, 'tref': None},
                    'LC_CHEOPS_inst4': {'do': True, 'order': 0, 'tref': None}}

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
# {'LC_CHEOPS_inst0': ['LC_WASP-76_CHEOPS_10'], 'LC_CHEOPS_inst1': ['LC_WASP-76_CHEOPS_11'], 'LC_CHEOPS_inst2': ['LC_WASP-76_CHEOPS_12'], 'LC_CHEOPS_inst3': ['LC_WASP-76_CHEOPS_13'], 'LC_CHEOPS_inst4': ['LC_WASP-76_CHEOPS_14']}
#
# The list of datasets for each IND instrument model are:
# {'IND-ROLL_CHEOPS_inst': ['IND-ROLL_WASP-76_CHEOPS_10', 'IND-ROLL_WASP-76_CHEOPS_11', 'IND-ROLL_WASP-76_CHEOPS_12', 'IND-ROLL_WASP-76_CHEOPS_13', 'IND-ROLL_WASP-76_CHEOPS_14'], 'IND-CX_CHEOPS_inst': ['IND-CX_WASP-76_CHEOPS_10', 'IND-CX_WASP-76_CHEOPS_11', 'IND-CX_WASP-76_CHEOPS_12', 'IND-CX_WASP-76_CHEOPS_13', 'IND-CX_WASP-76_CHEOPS_14'], 'IND-CY_CHEOPS_inst': ['IND-CY_WASP-76_CHEOPS_10', 'IND-CY_WASP-76_CHEOPS_11', 'IND-CY_WASP-76_CHEOPS_12', 'IND-CY_WASP-76_CHEOPS_13', 'IND-CY_WASP-76_CHEOPS_14'], 'IND-SMEAR_CHEOPS_inst': ['IND-SMEAR_WASP-76_CHEOPS_10', 'IND-SMEAR_WASP-76_CHEOPS_11', 'IND-SMEAR_WASP-76_CHEOPS_12', 'IND-SMEAR_WASP-76_CHEOPS_13', 'IND-SMEAR_WASP-76_CHEOPS_14'], 'IND-TF_CHEOPS_inst': ['IND-TF_WASP-76_CHEOPS_10', 'IND-TF_WASP-76_CHEOPS_11', 'IND-TF_WASP-76_CHEOPS_12', 'IND-TF_WASP-76_CHEOPS_13', 'IND-TF_WASP-76_CHEOPS_14'], 'IND-BKG_CHEOPS_inst': ['IND-BKG_WASP-76_CHEOPS_10', 'IND-BKG_WASP-76_CHEOPS_11', 'IND-BKG_WASP-76_CHEOPS_12', 'IND-BKG_WASP-76_CHEOPS_13', 'IND-BKG_WASP-76_CHEOPS_14'], 'IND-DARK_CHEOPS_inst': ['IND-DARK_WASP-76_CHEOPS_10', 'IND-DARK_WASP-76_CHEOPS_11', 'IND-DARK_WASP-76_CHEOPS_12', 'IND-DARK_WASP-76_CHEOPS_13', 'IND-DARK_WASP-76_CHEOPS_14'], 'IND-CONTA_CHEOPS_inst': ['IND-CONTA_WASP-76_CHEOPS_10', 'IND-CONTA_WASP-76_CHEOPS_11', 'IND-CONTA_WASP-76_CHEOPS_12', 'IND-CONTA_WASP-76_CHEOPS_13', 'IND-CONTA_WASP-76_CHEOPS_14']}
#
# The format of decorrelation_model_options dictionary depends on the decorrelation model used
# linear: {'quantity': 'raw'}
# spline: {'quantity': 'raw', 'spline_type': 'UnivariateSpline', 'spline_kwargs': {}}
# bispline: {'IND instument models': [], 'quantity': 'raw', 'spline_type': 'SmoothBivariateSpline', 'spline_kwargs': {'k': 3}, 'match datasets': {}, }


decorrelation_model = {'LC_CHEOPS_inst0': {'do': False,
                                           'what to decorrelate': {'add_2_totalflux': {'linear': {}},
                                                                   'multiply_2_totalflux': {'linear': {}}}},
                       'LC_CHEOPS_inst1': {'do': False,
                                           'what to decorrelate': {'add_2_totalflux': {'linear': {}},
                                                                   'multiply_2_totalflux': {'linear': {}}}},
                       'LC_CHEOPS_inst2': {'do': False,
                                           'what to decorrelate': {'add_2_totalflux': {'linear': {}},
                                                                   'multiply_2_totalflux': {'linear': {}}}},
                       'LC_CHEOPS_inst3': {'do': False,
                                           'what to decorrelate': {'add_2_totalflux': {'linear': {}},
                                                                   'multiply_2_totalflux': {'linear': {}}}},
                       'LC_CHEOPS_inst4': {'do': False,
                                           'what to decorrelate': {'add_2_totalflux': {'linear': {}},
                                                                   'multiply_2_totalflux': {'linear': {}}}}}
decorrelation_likelihood = {'LC_CHEOPS_inst0': {'do': True,
                                                'order': [('bispline', 'XY0'), ('spline', 'IND-BKG_CHEOPS_inst'), ('spline', 'IND-TF_CHEOPS_inst'), ('spline', 'IND-ROLL_CHEOPS_inst'), ],
                                                'bispline': {'XY0': {'IND instument models': ['IND-CX_CHEOPS_inst', 'IND-CY_CHEOPS_inst'],
                                                                     'quantity': 'raw',
                                                                     'spline_type': 'SmoothBivariateSpline',
                                                                     'spline_kwargs': {'kx': 3, 'ky': 3},
                                                                     'match datasets': {'LC_WASP-76_CHEOPS_10': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_10',
                                                                                                                 'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_10'
                                                                                                                 },
                                                                                        'LC_WASP-76_CHEOPS_11': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_11',
                                                                                                                 'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_11'
                                                                                                                 },
                                                                                        }
                                                                     },
                                                             },
                                                'spline': {'IND-ROLL_CHEOPS_inst': {'quantity': 'raw',
                                                                                    'spline_type': 'UnivariateSpline',
                                                                                    'spline_kwargs': {'k': 3, },
                                                                                    'match datasets': {'LC_WASP-76_CHEOPS_10': 'IND-ROLL_WASP-76_CHEOPS_10',
                                                                                                       'LC_WASP-76_CHEOPS_11': 'IND-ROLL_WASP-76_CHEOPS_11',
                                                                                                       'LC_WASP-76_CHEOPS_12': 'IND-ROLL_WASP-76_CHEOPS_12',
                                                                                                       'LC_WASP-76_CHEOPS_13': 'IND-ROLL_WASP-76_CHEOPS_13',
                                                                                                       'LC_WASP-76_CHEOPS_14': 'IND-ROLL_WASP-76_CHEOPS_14',
                                                                                                       }
                                                                                    },
                                                           'IND-BKG_CHEOPS_inst': {'quantity': 'raw',
                                                                                   'spline_type': 'UnivariateSpline',
                                                                                   'spline_kwargs': {'k': 3, },
                                                                                   'match datasets': {'LC_WASP-76_CHEOPS_10': 'IND-BKG_WASP-76_CHEOPS_10', }
                                                                                   },
                                                           'IND-TF_CHEOPS_inst': {'quantity': 'raw',
                                                                                  'spline_type': 'UnivariateSpline',
                                                                                  'spline_kwargs': {'k': 3, },
                                                                                  'match datasets': {'LC_WASP-76_CHEOPS_10': 'IND-TF_WASP-76_CHEOPS_10', }
                                                                                  },
                                                           }
                                                },
                            'LC_CHEOPS_inst1': {'do': True,
                                                'order': [('bispline', 'XY0'), ('spline', 'IND-BKG_CHEOPS_inst'), ('spline', 'IND-TF_CHEOPS_inst'), ('spline', 'IND-ROLL_CHEOPS_inst'), ],
                                                'bispline': {'XY0': {'IND instument models': ['IND-CX_CHEOPS_inst', 'IND-CY_CHEOPS_inst'],
                                                                     'quantity': 'raw',
                                                                     'spline_type': 'SmoothBivariateSpline',
                                                                     'spline_kwargs': {'kx': 3, 'ky': 3},
                                                                     'match datasets': {'LC_WASP-76_CHEOPS_10': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_10',
                                                                                                                 'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_10'
                                                                                                                 },
                                                                                        'LC_WASP-76_CHEOPS_11': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_11',
                                                                                                                 'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_11'
                                                                                                                 },
                                                                                        }
                                                                     },
                                                             },
                                                'spline': {'IND-ROLL_CHEOPS_inst': {'quantity': 'raw',
                                                                                    'spline_type': 'UnivariateSpline',
                                                                                    'spline_kwargs': {'k': 3, },
                                                                                    'match datasets': {'LC_WASP-76_CHEOPS_10': 'IND-ROLL_WASP-76_CHEOPS_10',
                                                                                                       'LC_WASP-76_CHEOPS_11': 'IND-ROLL_WASP-76_CHEOPS_11',
                                                                                                       'LC_WASP-76_CHEOPS_12': 'IND-ROLL_WASP-76_CHEOPS_12',
                                                                                                       'LC_WASP-76_CHEOPS_13': 'IND-ROLL_WASP-76_CHEOPS_13',
                                                                                                       'LC_WASP-76_CHEOPS_14': 'IND-ROLL_WASP-76_CHEOPS_14',
                                                                                                       }
                                                                                    },
                                                           'IND-BKG_CHEOPS_inst': {'quantity': 'raw',
                                                                                   'spline_type': 'UnivariateSpline',
                                                                                   'spline_kwargs': {'k': 3, },
                                                                                   'match datasets': {'LC_WASP-76_CHEOPS_11': 'IND-BKG_WASP-76_CHEOPS_11', }
                                                                                   },
                                                           'IND-TF_CHEOPS_inst': {'quantity': 'raw',
                                                                                  'spline_type': 'UnivariateSpline',
                                                                                  'spline_kwargs': {'k': 3, },
                                                                                  'match datasets': {'LC_WASP-76_CHEOPS_11': 'IND-TF_WASP-76_CHEOPS_11', }
                                                                                  },
                                                           }
                                                },
                            'LC_CHEOPS_inst2': {'do': True,
                                                'order': [('bispline', 'XY2'), ('spline', 'IND-BKG_CHEOPS_inst'), ('spline', 'IND-TF_CHEOPS_inst'), ('spline', 'IND-ROLL_CHEOPS_inst'), ],
                                                'bispline': {'XY2': {'IND instument models': ['IND-CX_CHEOPS_inst', 'IND-CY_CHEOPS_inst'],
                                                                     'quantity': 'raw',
                                                                     'spline_type': 'SmoothBivariateSpline',
                                                                     'spline_kwargs': {'kx': 3, 'ky': 3},
                                                                     'match datasets': {'LC_WASP-76_CHEOPS_12': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_12',
                                                                                                                 'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_12'
                                                                                                                 },
                                                                                        'LC_WASP-76_CHEOPS_13': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_13',
                                                                                                                 'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_13'
                                                                                                                 },
                                                                                        'LC_WASP-76_CHEOPS_14': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_14',
                                                                                                                 'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_14'
                                                                                                                 },
                                                                                        }
                                                                     },
                                                             },
                                                'spline': {'IND-ROLL_CHEOPS_inst': {'quantity': 'raw',
                                                                                    'spline_type': 'UnivariateSpline',
                                                                                    'spline_kwargs': {'k': 3, },
                                                                                    'match datasets': {'LC_WASP-76_CHEOPS_10': 'IND-ROLL_WASP-76_CHEOPS_10',
                                                                                                       'LC_WASP-76_CHEOPS_11': 'IND-ROLL_WASP-76_CHEOPS_11',
                                                                                                       'LC_WASP-76_CHEOPS_12': 'IND-ROLL_WASP-76_CHEOPS_12',
                                                                                                       'LC_WASP-76_CHEOPS_13': 'IND-ROLL_WASP-76_CHEOPS_13',
                                                                                                       'LC_WASP-76_CHEOPS_14': 'IND-ROLL_WASP-76_CHEOPS_14',
                                                                                                       }
                                                                                    },
                                                           'IND-BKG_CHEOPS_inst': {'quantity': 'raw',
                                                                                   'spline_type': 'UnivariateSpline',
                                                                                   'spline_kwargs': {'k': 3, },
                                                                                   'match datasets': {'LC_WASP-76_CHEOPS_12': 'IND-BKG_WASP-76_CHEOPS_12', }
                                                                                   },
                                                           'IND-TF_CHEOPS_inst': {'quantity': 'raw',
                                                                                  'spline_type': 'UnivariateSpline',
                                                                                  'spline_kwargs': {'k': 3, },
                                                                                  'match datasets': {'LC_WASP-76_CHEOPS_12': 'IND-TF_WASP-76_CHEOPS_12', }
                                                                                  },
                                                           }
                                                },
                            'LC_CHEOPS_inst3': {'do': True,
                                                'order': [('bispline', 'XY2'), ('spline', 'IND-BKG_CHEOPS_inst'), ('spline', 'IND-TF_CHEOPS_inst'), ('spline', 'IND-ROLL_CHEOPS_inst'), ],
                                                'bispline': {'XY2': {'IND instument models': ['IND-CX_CHEOPS_inst', 'IND-CY_CHEOPS_inst'],
                                                                     'quantity': 'raw',
                                                                     'spline_type': 'SmoothBivariateSpline',
                                                                     'spline_kwargs': {'kx': 3, 'ky': 3},
                                                                     'match datasets': {'LC_WASP-76_CHEOPS_12': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_12',
                                                                                                                 'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_12'
                                                                                                                 },
                                                                                        'LC_WASP-76_CHEOPS_13': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_13',
                                                                                                                 'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_13'
                                                                                                                 },
                                                                                        'LC_WASP-76_CHEOPS_14': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_14',
                                                                                                                 'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_14'
                                                                                                                 },
                                                                                        }
                                                                     },
                                                             },
                                                'spline': {'IND-ROLL_CHEOPS_inst': {'quantity': 'raw',
                                                                                    'spline_type': 'UnivariateSpline',
                                                                                    'spline_kwargs': {'k': 3, },
                                                                                    'match datasets': {'LC_WASP-76_CHEOPS_10': 'IND-ROLL_WASP-76_CHEOPS_10',
                                                                                                       'LC_WASP-76_CHEOPS_11': 'IND-ROLL_WASP-76_CHEOPS_11',
                                                                                                       'LC_WASP-76_CHEOPS_12': 'IND-ROLL_WASP-76_CHEOPS_12',
                                                                                                       'LC_WASP-76_CHEOPS_13': 'IND-ROLL_WASP-76_CHEOPS_13',
                                                                                                       'LC_WASP-76_CHEOPS_14': 'IND-ROLL_WASP-76_CHEOPS_14',
                                                                                                       }
                                                                                    },
                                                           'IND-BKG_CHEOPS_inst': {'quantity': 'raw',
                                                                                   'spline_type': 'UnivariateSpline',
                                                                                   'spline_kwargs': {'k': 3, },
                                                                                   'match datasets': {'LC_WASP-76_CHEOPS_13': 'IND-BKG_WASP-76_CHEOPS_13', }
                                                                                   },
                                                           'IND-TF_CHEOPS_inst': {'quantity': 'raw',
                                                                                  'spline_type': 'UnivariateSpline',
                                                                                  'spline_kwargs': {'k': 3, },
                                                                                  'match datasets': {'LC_WASP-76_CHEOPS_13': 'IND-TF_WASP-76_CHEOPS_13', }
                                                                                  },
                                                           }
                                                },
                            'LC_CHEOPS_inst4': {'do': True,
                                                'order': [('bispline', 'XY2'), ('spline', 'IND-BKG_CHEOPS_inst'), ('spline', 'IND-TF_CHEOPS_inst'), ('spline', 'IND-ROLL_CHEOPS_inst'), ],
                                                'bispline': {'XY2': {'IND instument models': ['IND-CX_CHEOPS_inst', 'IND-CY_CHEOPS_inst'],
                                                                     'quantity': 'raw',
                                                                     'spline_type': 'SmoothBivariateSpline',
                                                                     'spline_kwargs': {'kx': 3, 'ky': 3},
                                                                     'match datasets': {'LC_WASP-76_CHEOPS_12': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_12',
                                                                                                                 'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_12'
                                                                                                                 },
                                                                                        'LC_WASP-76_CHEOPS_13': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_13',
                                                                                                                 'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_13'
                                                                                                                 },
                                                                                        'LC_WASP-76_CHEOPS_14': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_14',
                                                                                                                 'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_14'
                                                                                                                 },
                                                                                        }
                                                                     },
                                                             },
                                                'spline': {'IND-ROLL_CHEOPS_inst': {'quantity': 'raw',
                                                                                    'spline_type': 'UnivariateSpline',
                                                                                    'spline_kwargs': {'k': 3, },
                                                                                    'match datasets': {'LC_WASP-76_CHEOPS_10': 'IND-ROLL_WASP-76_CHEOPS_10',
                                                                                                       'LC_WASP-76_CHEOPS_11': 'IND-ROLL_WASP-76_CHEOPS_11',
                                                                                                       'LC_WASP-76_CHEOPS_12': 'IND-ROLL_WASP-76_CHEOPS_12',
                                                                                                       'LC_WASP-76_CHEOPS_13': 'IND-ROLL_WASP-76_CHEOPS_13',
                                                                                                       'LC_WASP-76_CHEOPS_14': 'IND-ROLL_WASP-76_CHEOPS_14',
                                                                                                       }
                                                                                    },
                                                           'IND-BKG_CHEOPS_inst': {'quantity': 'raw',
                                                                                   'spline_type': 'UnivariateSpline',
                                                                                   'spline_kwargs': {'k': 3, },
                                                                                   'match datasets': {'LC_WASP-76_CHEOPS_14': 'IND-BKG_WASP-76_CHEOPS_14', }
                                                                                   },
                                                           'IND-TF_CHEOPS_inst': {'quantity': 'raw',
                                                                                  'spline_type': 'UnivariateSpline',
                                                                                  'spline_kwargs': {'k': 3, },
                                                                                  'match datasets': {'LC_WASP-76_CHEOPS_14': 'IND-TF_WASP-76_CHEOPS_14', }
                                                                                  },
                                                           }
                                                },
                            }
