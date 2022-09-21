#!/usr/bin/python
# -*- coding:  utf-8 -*-

# Light-curve parametrisation file of WASP-76


# Which model do you want to use for the transit ?
transit_model = {'b': {'do': False,
                       'model4instrument': {'LC_CHEOPS_inst0': '',
                                            'LC_CHEOPS_inst1': '',
                                            'LC_CHEOPS_inst2': '',
                                            'LC_CHEOPS_inst3': '',
                                            'LC_CHEOPS_inst4': '',
                                            'LC_CHEOPS_inst5': '',
                                            'LC_CHEOPS_inst6': '',
                                            'LC_CHEOPS_inst7': '',
                                            'LC_CHEOPS_inst8': '',
                                            'LC_CHEOPS_inst9': '',
                                            'LC_CHEOPS_inst10': '',
                                            'LC_CHEOPS_inst11': '',
                                            'LC_CHEOPS_inst12': '',
                                            'LC_CHEOPS_inst13': '',
                                            'LC_CHEOPS_inst14': '',
                                            'LC_CHEOPS_inst15': '',
                                            'LC_CHEOPS_inst16': '',
                                            'LC_CHEOPS_inst17': '',
                                            'LC_CHEOPS_inst18': '',
                                            'LC_CHEOPS_inst19': '',
                                            },
                       'model_definitions': {'': {'model': 'batman'}, }
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
             'LC_CHEOPS_inst5': 'LD',
             'LC_CHEOPS_inst6': 'LD',
             'LC_CHEOPS_inst7': 'LD',
             'LC_CHEOPS_inst8': 'LD',
             'LC_CHEOPS_inst9': 'LD',
             'LC_CHEOPS_inst10': 'LD',
             'LC_CHEOPS_inst11': 'LD',
             'LC_CHEOPS_inst12': 'LD',
             'LC_CHEOPS_inst13': 'LD',
             'LC_CHEOPS_inst14': 'LD',
             'LC_CHEOPS_inst15': 'LD',
             'LC_CHEOPS_inst16': 'LD',
             'LC_CHEOPS_inst17': 'LD',
             'LC_CHEOPS_inst18': 'LD',
             'LC_CHEOPS_inst19': 'LD',
             'LD_models': {'LD': 'nonlinear'}
             }
       }

# Supersampling and exposure_time
SuperSamps = {'LC_CHEOPS_inst0': {'supersamp': 1, 'exptime': 0.02043402778},
              'LC_CHEOPS_inst1': {'supersamp': 1, 'exptime': 0.02043402778},
              'LC_CHEOPS_inst2': {'supersamp': 1, 'exptime': 0.02043402778},
              'LC_CHEOPS_inst3': {'supersamp': 1, 'exptime': 0.02043402778},
              'LC_CHEOPS_inst4': {'supersamp': 1, 'exptime': 0.02043402778},
              'LC_CHEOPS_inst5': {'supersamp': 1, 'exptime': 0.02043402778},
              'LC_CHEOPS_inst6': {'supersamp': 1, 'exptime': 0.02043402778},
              'LC_CHEOPS_inst7': {'supersamp': 1, 'exptime': 0.02043402778},
              'LC_CHEOPS_inst8': {'supersamp': 1, 'exptime': 0.02043402778},
              'LC_CHEOPS_inst9': {'supersamp': 1, 'exptime': 0.02043402778},
              'LC_CHEOPS_inst10': {'supersamp': 1, 'exptime': 0.02043402778},
              'LC_CHEOPS_inst11': {'supersamp': 1, 'exptime': 0.02043402778},
              'LC_CHEOPS_inst12': {'supersamp': 1, 'exptime': 0.02043402778},
              'LC_CHEOPS_inst13': {'supersamp': 1, 'exptime': 0.02043402778},
              'LC_CHEOPS_inst14': {'supersamp': 1, 'exptime': 0.02043402778},
              'LC_CHEOPS_inst15': {'supersamp': 1, 'exptime': 0.02043402778},
              'LC_CHEOPS_inst16': {'supersamp': 1, 'exptime': 0.02043402778},
              'LC_CHEOPS_inst17': {'supersamp': 1, 'exptime': 0.02043402778},
              'LC_CHEOPS_inst18': {'supersamp': 1, 'exptime': 0.02043402778},
              'LC_CHEOPS_inst19': {'supersamp': 1, 'exptime': 0.02043402778},
              }

# Which model do you want to use for the phase curve ?
phasecurve_model = {'b': {'do': True,
                          'model4instrument': {'LC_CHEOPS_inst0': ['0'],
                                               'LC_CHEOPS_inst1': ['1'],
                                               'LC_CHEOPS_inst2': ['2'],
                                               'LC_CHEOPS_inst3': ['3'],
                                               'LC_CHEOPS_inst4': ['4'],
                                               'LC_CHEOPS_inst5': ['5'],
                                               'LC_CHEOPS_inst6': ['6'],
                                               'LC_CHEOPS_inst7': ['7'],
                                               'LC_CHEOPS_inst8': ['8'],
                                               'LC_CHEOPS_inst9': ['9'],
                                               'LC_CHEOPS_inst10': ['10'],
                                               'LC_CHEOPS_inst11': ['11'],
                                               'LC_CHEOPS_inst12': ['12'],
                                               'LC_CHEOPS_inst13': ['13'],
                                               'LC_CHEOPS_inst14': ['14'],
                                               'LC_CHEOPS_inst15': ['15'],
                                               'LC_CHEOPS_inst16': ['16'],
                                               'LC_CHEOPS_inst17': ['16'],
                                               'LC_CHEOPS_inst18': ['18'],
                                               'LC_CHEOPS_inst19': ['19'],
                                               },
                          'model_definitions': {'0': {'args': {"cos1": {"sincos": "cos", "factor_period": 1,
                                                                        'flux_offset': 'param',
                                                                        'phase_offset': 'param',
                                                                        'occultation': True
                                                                        },
                                                               },
                                                      'model': 'sincos'
                                                      },
                                                '1': {'args': {"cos1": {"sincos": "cos", "factor_period": 1,
                                                                        'flux_offset': 'param',
                                                                        'phase_offset': 'param',
                                                                        'occultation': True
                                                                        },
                                                               },
                                                      'model': 'sincos'
                                                      },
                                                '2': {'args': {"cos1": {"sincos": "cos", "factor_period": 1,
                                                                        'flux_offset': 'param',
                                                                        'phase_offset': 'param',
                                                                        'occultation': True
                                                                        },
                                                               },
                                                      'model': 'sincos'
                                                      },
                                                '3': {'args': {"cos1": {"sincos": "cos", "factor_period": 1,
                                                                        'flux_offset': 'param',
                                                                        'phase_offset': 'param',
                                                                        'occultation': True
                                                                        },
                                                               },
                                                      'model': 'sincos'
                                                      },
                                                '4': {'args': {"cos1": {"sincos": "cos", "factor_period": 1,
                                                                        'flux_offset': 'param',
                                                                        'phase_offset': 'param',
                                                                        'occultation': True
                                                                        },
                                                               },
                                                      'model': 'sincos'
                                                      },
                                                '5': {'args': {"cos1": {"sincos": "cos", "factor_period": 1,
                                                                        'flux_offset': 'param',
                                                                        'phase_offset': 'param',
                                                                        'occultation': True
                                                                        },
                                                               },
                                                      'model': 'sincos'
                                                      },
                                                '6': {'args': {"cos1": {"sincos": "cos", "factor_period": 1,
                                                                        'flux_offset': 'param',
                                                                        'phase_offset': 'param',
                                                                        'occultation': True
                                                                        },
                                                               },
                                                      'model': 'sincos'
                                                      },
                                                '7': {'args': {"cos1": {"sincos": "cos", "factor_period": 1,
                                                                        'flux_offset': 'param',
                                                                        'phase_offset': 'param',
                                                                        'occultation': True
                                                                        },
                                                               },
                                                      'model': 'sincos'
                                                      },
                                                '8': {'args': {"cos1": {"sincos": "cos", "factor_period": 1,
                                                                        'flux_offset': 'param',
                                                                        'phase_offset': 'param',
                                                                        'occultation': True
                                                                        },
                                                               },
                                                      'model': 'sincos'
                                                      },
                                                '9': {'args': {"cos1": {"sincos": "cos", "factor_period": 1,
                                                                        'flux_offset': 'param',
                                                                        'phase_offset': 'param',
                                                                        'occultation': True
                                                                        },
                                                               },
                                                      'model': 'sincos'
                                                      },
                                                '10': {'args': {"cos1": {"sincos": "cos", "factor_period": 1,
                                                                         'flux_offset': 'param',
                                                                         'phase_offset': 'param',
                                                                         'occultation': True
                                                                         },
                                                               },
                                                       'model': 'sincos'
                                                       },
                                                }
                          }
                    }

# Which model do you want to use for the occultation ?
# WARNING: Some phasecurve models already include the occultation. No need to add it twice in these cases.
occultation_model = {'b': {'do': False,
                           'model4instrument': {'LC_CHEOPS_inst0': '',
                                                'LC_CHEOPS_inst1': '',
                                                'LC_CHEOPS_inst10': '',
                                                'LC_CHEOPS_inst11': '',
                                                'LC_CHEOPS_inst12': '',
                                                'LC_CHEOPS_inst13': '',
                                                'LC_CHEOPS_inst14': '',
                                                'LC_CHEOPS_inst15': '',
                                                'LC_CHEOPS_inst16': '',
                                                'LC_CHEOPS_inst17': '',
                                                'LC_CHEOPS_inst18': '',
                                                'LC_CHEOPS_inst19': '',
                                                'LC_CHEOPS_inst2': '',
                                                'LC_CHEOPS_inst3': '',
                                                'LC_CHEOPS_inst4': '',
                                                'LC_CHEOPS_inst5': '',
                                                'LC_CHEOPS_inst6': '',
                                                'LC_CHEOPS_inst7': '',
                                                'LC_CHEOPS_inst8': '',
                                                'LC_CHEOPS_inst9': '',
                                                'LC_CHEOPS_instPC0': '',
                                                'LC_CHEOPS_instPC1': '',
                                                'LC_CHEOPS_instPC2': ''},
                           'model_definitions': {'': {'model': 'batman'}, }
                           }
                     }

# Polynomial trends
polynomial_model = {'A': {'do': False, 'order': 0, 'tref': None},
                    'LC_CHEOPS_inst0': {'do': True, 'order': 0, 'tref': None},
                    'LC_CHEOPS_inst1': {'do': True, 'order': 0, 'tref': None},
                    'LC_CHEOPS_inst2': {'do': True, 'order': 0, 'tref': None},
                    'LC_CHEOPS_inst3': {'do': True, 'order': 0, 'tref': None},
                    'LC_CHEOPS_inst4': {'do': True, 'order': 0, 'tref': None},
                    'LC_CHEOPS_inst5': {'do': True, 'order': 0, 'tref': None},
                    'LC_CHEOPS_inst6': {'do': True, 'order': 0, 'tref': None},
                    'LC_CHEOPS_inst7': {'do': True, 'order': 0, 'tref': None},
                    'LC_CHEOPS_inst8': {'do': True, 'order': 0, 'tref': None},
                    'LC_CHEOPS_inst9': {'do': True, 'order': 0, 'tref': None},
                    'LC_CHEOPS_inst10': {'do': True, 'order': 0, 'tref': None},
                    'LC_CHEOPS_inst11': {'do': True, 'order': 0, 'tref': None},
                    'LC_CHEOPS_inst12': {'do': True, 'order': 0, 'tref': None},
                    'LC_CHEOPS_inst13': {'do': True, 'order': 0, 'tref': None},
                    'LC_CHEOPS_inst14': {'do': True, 'order': 0, 'tref': None},
                    'LC_CHEOPS_inst15': {'do': True, 'order': 0, 'tref': None},
                    'LC_CHEOPS_inst16': {'do': True, 'order': 0, 'tref': None},
                    'LC_CHEOPS_inst17': {'do': True, 'order': 0, 'tref': None},
                    'LC_CHEOPS_inst18': {'do': True, 'order': 0, 'tref': None},
                    'LC_CHEOPS_inst19': {'do': True, 'order': 0, 'tref': None},
                    }

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
# {'LC_CHEOPS_instPC0': ['LC_WASP-76_CHEOPS_0'], 'LC_CHEOPS_instPC1': ['LC_WASP-76_CHEOPS_1'], 'LC_CHEOPS_instPC2': ['LC_WASP-76_CHEOPS_2'], 'LC_CHEOPS_inst0': ['LC_WASP-76_CHEOPS_100'], 'LC_CHEOPS_inst1': ['LC_WASP-76_CHEOPS_101'], 'LC_CHEOPS_inst2': ['LC_WASP-76_CHEOPS_102'], 'LC_CHEOPS_inst3': ['LC_WASP-76_CHEOPS_103'], 'LC_CHEOPS_inst4': ['LC_WASP-76_CHEOPS_104'], 'LC_CHEOPS_inst5': ['LC_WASP-76_CHEOPS_105'], 'LC_CHEOPS_inst6': ['LC_WASP-76_CHEOPS_106'], 'LC_CHEOPS_inst7': ['LC_WASP-76_CHEOPS_107'], 'LC_CHEOPS_inst8': ['LC_WASP-76_CHEOPS_108'], 'LC_CHEOPS_inst9': ['LC_WASP-76_CHEOPS_109'], 'LC_CHEOPS_inst10': ['LC_WASP-76_CHEOPS_110'], 'LC_CHEOPS_inst11': ['LC_WASP-76_CHEOPS_111'], 'LC_CHEOPS_inst12': ['LC_WASP-76_CHEOPS_112'], 'LC_CHEOPS_inst13': ['LC_WASP-76_CHEOPS_113'], 'LC_CHEOPS_inst14': ['LC_WASP-76_CHEOPS_114'], 'LC_CHEOPS_inst15': ['LC_WASP-76_CHEOPS_115'], 'LC_CHEOPS_inst16': ['LC_WASP-76_CHEOPS_116'], 'LC_CHEOPS_inst17': ['LC_WASP-76_CHEOPS_117'], 'LC_CHEOPS_inst18': ['LC_WASP-76_CHEOPS_118'], 'LC_CHEOPS_inst19': ['LC_WASP-76_CHEOPS_119']}
#
# The list of datasets for each IND instrument model are:
# {'IND-ROLL_CHEOPS_inst': ['IND-ROLL_WASP-76_CHEOPS_0', 'IND-ROLL_WASP-76_CHEOPS_1', 'IND-ROLL_WASP-76_CHEOPS_2', 'IND-ROLL_WASP-76_CHEOPS_100', 'IND-ROLL_WASP-76_CHEOPS_101', 'IND-ROLL_WASP-76_CHEOPS_102', 'IND-ROLL_WASP-76_CHEOPS_103', 'IND-ROLL_WASP-76_CHEOPS_104', 'IND-ROLL_WASP-76_CHEOPS_105', 'IND-ROLL_WASP-76_CHEOPS_106', 'IND-ROLL_WASP-76_CHEOPS_107', 'IND-ROLL_WASP-76_CHEOPS_108', 'IND-ROLL_WASP-76_CHEOPS_109', 'IND-ROLL_WASP-76_CHEOPS_110', 'IND-ROLL_WASP-76_CHEOPS_111', 'IND-ROLL_WASP-76_CHEOPS_112', 'IND-ROLL_WASP-76_CHEOPS_113', 'IND-ROLL_WASP-76_CHEOPS_114', 'IND-ROLL_WASP-76_CHEOPS_115', 'IND-ROLL_WASP-76_CHEOPS_116', 'IND-ROLL_WASP-76_CHEOPS_117', 'IND-ROLL_WASP-76_CHEOPS_118', 'IND-ROLL_WASP-76_CHEOPS_119'], 'IND-CX_CHEOPS_inst': ['IND-CX_WASP-76_CHEOPS_0', 'IND-CX_WASP-76_CHEOPS_1', 'IND-CX_WASP-76_CHEOPS_2', 'IND-CX_WASP-76_CHEOPS_100', 'IND-CX_WASP-76_CHEOPS_101', 'IND-CX_WASP-76_CHEOPS_102', 'IND-CX_WASP-76_CHEOPS_103', 'IND-CX_WASP-76_CHEOPS_104', 'IND-CX_WASP-76_CHEOPS_105', 'IND-CX_WASP-76_CHEOPS_106', 'IND-CX_WASP-76_CHEOPS_107', 'IND-CX_WASP-76_CHEOPS_108', 'IND-CX_WASP-76_CHEOPS_109', 'IND-CX_WASP-76_CHEOPS_110', 'IND-CX_WASP-76_CHEOPS_111', 'IND-CX_WASP-76_CHEOPS_112', 'IND-CX_WASP-76_CHEOPS_113', 'IND-CX_WASP-76_CHEOPS_114', 'IND-CX_WASP-76_CHEOPS_115', 'IND-CX_WASP-76_CHEOPS_116', 'IND-CX_WASP-76_CHEOPS_117', 'IND-CX_WASP-76_CHEOPS_118', 'IND-CX_WASP-76_CHEOPS_119'], 'IND-CY_CHEOPS_inst': ['IND-CY_WASP-76_CHEOPS_0', 'IND-CY_WASP-76_CHEOPS_1', 'IND-CY_WASP-76_CHEOPS_2', 'IND-CY_WASP-76_CHEOPS_100', 'IND-CY_WASP-76_CHEOPS_101', 'IND-CY_WASP-76_CHEOPS_102', 'IND-CY_WASP-76_CHEOPS_103', 'IND-CY_WASP-76_CHEOPS_104', 'IND-CY_WASP-76_CHEOPS_105', 'IND-CY_WASP-76_CHEOPS_106', 'IND-CY_WASP-76_CHEOPS_107', 'IND-CY_WASP-76_CHEOPS_108', 'IND-CY_WASP-76_CHEOPS_109', 'IND-CY_WASP-76_CHEOPS_110', 'IND-CY_WASP-76_CHEOPS_111', 'IND-CY_WASP-76_CHEOPS_112', 'IND-CY_WASP-76_CHEOPS_113', 'IND-CY_WASP-76_CHEOPS_114', 'IND-CY_WASP-76_CHEOPS_115', 'IND-CY_WASP-76_CHEOPS_116', 'IND-CY_WASP-76_CHEOPS_117', 'IND-CY_WASP-76_CHEOPS_118', 'IND-CY_WASP-76_CHEOPS_119'], 'IND-SMEAR_CHEOPS_inst': ['IND-SMEAR_WASP-76_CHEOPS_0', 'IND-SMEAR_WASP-76_CHEOPS_1', 'IND-SMEAR_WASP-76_CHEOPS_2', 'IND-SMEAR_WASP-76_CHEOPS_100', 'IND-SMEAR_WASP-76_CHEOPS_101', 'IND-SMEAR_WASP-76_CHEOPS_102', 'IND-SMEAR_WASP-76_CHEOPS_103', 'IND-SMEAR_WASP-76_CHEOPS_104', 'IND-SMEAR_WASP-76_CHEOPS_105', 'IND-SMEAR_WASP-76_CHEOPS_106', 'IND-SMEAR_WASP-76_CHEOPS_107', 'IND-SMEAR_WASP-76_CHEOPS_108', 'IND-SMEAR_WASP-76_CHEOPS_109', 'IND-SMEAR_WASP-76_CHEOPS_110', 'IND-SMEAR_WASP-76_CHEOPS_111', 'IND-SMEAR_WASP-76_CHEOPS_112', 'IND-SMEAR_WASP-76_CHEOPS_113', 'IND-SMEAR_WASP-76_CHEOPS_114', 'IND-SMEAR_WASP-76_CHEOPS_115', 'IND-SMEAR_WASP-76_CHEOPS_116', 'IND-SMEAR_WASP-76_CHEOPS_117', 'IND-SMEAR_WASP-76_CHEOPS_118', 'IND-SMEAR_WASP-76_CHEOPS_119'], 'IND-TF_CHEOPS_inst': ['IND-TF_WASP-76_CHEOPS_0', 'IND-TF_WASP-76_CHEOPS_1', 'IND-TF_WASP-76_CHEOPS_2', 'IND-TF_WASP-76_CHEOPS_100', 'IND-TF_WASP-76_CHEOPS_101', 'IND-TF_WASP-76_CHEOPS_102', 'IND-TF_WASP-76_CHEOPS_103', 'IND-TF_WASP-76_CHEOPS_104', 'IND-TF_WASP-76_CHEOPS_105', 'IND-TF_WASP-76_CHEOPS_106', 'IND-TF_WASP-76_CHEOPS_107', 'IND-TF_WASP-76_CHEOPS_108', 'IND-TF_WASP-76_CHEOPS_109', 'IND-TF_WASP-76_CHEOPS_110', 'IND-TF_WASP-76_CHEOPS_111', 'IND-TF_WASP-76_CHEOPS_112', 'IND-TF_WASP-76_CHEOPS_113', 'IND-TF_WASP-76_CHEOPS_114', 'IND-TF_WASP-76_CHEOPS_115', 'IND-TF_WASP-76_CHEOPS_116', 'IND-TF_WASP-76_CHEOPS_117', 'IND-TF_WASP-76_CHEOPS_118', 'IND-TF_WASP-76_CHEOPS_119'], 'IND-BKG_CHEOPS_inst': ['IND-BKG_WASP-76_CHEOPS_0', 'IND-BKG_WASP-76_CHEOPS_1', 'IND-BKG_WASP-76_CHEOPS_2', 'IND-BKG_WASP-76_CHEOPS_100', 'IND-BKG_WASP-76_CHEOPS_101', 'IND-BKG_WASP-76_CHEOPS_102', 'IND-BKG_WASP-76_CHEOPS_103', 'IND-BKG_WASP-76_CHEOPS_104', 'IND-BKG_WASP-76_CHEOPS_105', 'IND-BKG_WASP-76_CHEOPS_106', 'IND-BKG_WASP-76_CHEOPS_107', 'IND-BKG_WASP-76_CHEOPS_108', 'IND-BKG_WASP-76_CHEOPS_109', 'IND-BKG_WASP-76_CHEOPS_110', 'IND-BKG_WASP-76_CHEOPS_111', 'IND-BKG_WASP-76_CHEOPS_112', 'IND-BKG_WASP-76_CHEOPS_113', 'IND-BKG_WASP-76_CHEOPS_114', 'IND-BKG_WASP-76_CHEOPS_115', 'IND-BKG_WASP-76_CHEOPS_116', 'IND-BKG_WASP-76_CHEOPS_117', 'IND-BKG_WASP-76_CHEOPS_118', 'IND-BKG_WASP-76_CHEOPS_119'], 'IND-DARK_CHEOPS_inst': ['IND-DARK_WASP-76_CHEOPS_0', 'IND-DARK_WASP-76_CHEOPS_1', 'IND-DARK_WASP-76_CHEOPS_2', 'IND-DARK_WASP-76_CHEOPS_100', 'IND-DARK_WASP-76_CHEOPS_101', 'IND-DARK_WASP-76_CHEOPS_102', 'IND-DARK_WASP-76_CHEOPS_103', 'IND-DARK_WASP-76_CHEOPS_104', 'IND-DARK_WASP-76_CHEOPS_105', 'IND-DARK_WASP-76_CHEOPS_106', 'IND-DARK_WASP-76_CHEOPS_107', 'IND-DARK_WASP-76_CHEOPS_108', 'IND-DARK_WASP-76_CHEOPS_109', 'IND-DARK_WASP-76_CHEOPS_110', 'IND-DARK_WASP-76_CHEOPS_111', 'IND-DARK_WASP-76_CHEOPS_112', 'IND-DARK_WASP-76_CHEOPS_113', 'IND-DARK_WASP-76_CHEOPS_114', 'IND-DARK_WASP-76_CHEOPS_115', 'IND-DARK_WASP-76_CHEOPS_116', 'IND-DARK_WASP-76_CHEOPS_117', 'IND-DARK_WASP-76_CHEOPS_118', 'IND-DARK_WASP-76_CHEOPS_119'], 'IND-CONTA_CHEOPS_inst': ['IND-CONTA_WASP-76_CHEOPS_0', 'IND-CONTA_WASP-76_CHEOPS_1', 'IND-CONTA_WASP-76_CHEOPS_2', 'IND-CONTA_WASP-76_CHEOPS_100', 'IND-CONTA_WASP-76_CHEOPS_101', 'IND-CONTA_WASP-76_CHEOPS_102', 'IND-CONTA_WASP-76_CHEOPS_103', 'IND-CONTA_WASP-76_CHEOPS_104', 'IND-CONTA_WASP-76_CHEOPS_105', 'IND-CONTA_WASP-76_CHEOPS_106', 'IND-CONTA_WASP-76_CHEOPS_107', 'IND-CONTA_WASP-76_CHEOPS_108', 'IND-CONTA_WASP-76_CHEOPS_109', 'IND-CONTA_WASP-76_CHEOPS_110', 'IND-CONTA_WASP-76_CHEOPS_111', 'IND-CONTA_WASP-76_CHEOPS_112', 'IND-CONTA_WASP-76_CHEOPS_113', 'IND-CONTA_WASP-76_CHEOPS_114', 'IND-CONTA_WASP-76_CHEOPS_115', 'IND-CONTA_WASP-76_CHEOPS_116', 'IND-CONTA_WASP-76_CHEOPS_117', 'IND-CONTA_WASP-76_CHEOPS_118', 'IND-CONTA_WASP-76_CHEOPS_119']}
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
                       'LC_CHEOPS_inst10': {'do': False,
                                            'what to decorrelate': {'add_2_totalflux': {'linear': {}},
                                                                    'multiply_2_totalflux': {'linear': {}}}},
                       'LC_CHEOPS_inst11': {'do': False,
                                            'what to decorrelate': {'add_2_totalflux': {'linear': {}},
                                                                    'multiply_2_totalflux': {'linear': {}}}},
                       'LC_CHEOPS_inst12': {'do': False,
                                            'what to decorrelate': {'add_2_totalflux': {'linear': {}},
                                                                    'multiply_2_totalflux': {'linear': {}}}},
                       'LC_CHEOPS_inst13': {'do': False,
                                            'what to decorrelate': {'add_2_totalflux': {'linear': {}},
                                                                    'multiply_2_totalflux': {'linear': {}}}},
                       'LC_CHEOPS_inst14': {'do': False,
                                            'what to decorrelate': {'add_2_totalflux': {'linear': {}},
                                                                    'multiply_2_totalflux': {'linear': {}}}},
                       'LC_CHEOPS_inst15': {'do': False,
                                            'what to decorrelate': {'add_2_totalflux': {'linear': {}},
                                                                    'multiply_2_totalflux': {'linear': {}}}},
                       'LC_CHEOPS_inst16': {'do': False,
                                            'what to decorrelate': {'add_2_totalflux': {'linear': {}},
                                                                    'multiply_2_totalflux': {'linear': {}}}},
                       'LC_CHEOPS_inst17': {'do': False,
                                            'what to decorrelate': {'add_2_totalflux': {'linear': {}},
                                                                    'multiply_2_totalflux': {'linear': {}}}},
                       'LC_CHEOPS_inst18': {'do': False,
                                            'what to decorrelate': {'add_2_totalflux': {'linear': {}},
                                                                    'multiply_2_totalflux': {'linear': {}}}},
                       'LC_CHEOPS_inst19': {'do': False,
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
                                                                   'multiply_2_totalflux': {'linear': {}}}},
                       'LC_CHEOPS_inst5': {'do': False,
                                           'what to decorrelate': {'add_2_totalflux': {'linear': {}},
                                                                   'multiply_2_totalflux': {'linear': {}}}},
                       'LC_CHEOPS_inst6': {'do': False,
                                           'what to decorrelate': {'add_2_totalflux': {'linear': {}},
                                                                   'multiply_2_totalflux': {'linear': {}}}},
                       'LC_CHEOPS_inst7': {'do': False,
                                           'what to decorrelate': {'add_2_totalflux': {'linear': {}},
                                                                   'multiply_2_totalflux': {'linear': {}}}},
                       'LC_CHEOPS_inst8': {'do': False,
                                           'what to decorrelate': {'add_2_totalflux': {'linear': {}},
                                                                   'multiply_2_totalflux': {'linear': {}}}},
                       'LC_CHEOPS_inst9': {'do': False,
                                           'what to decorrelate': {'add_2_totalflux': {'linear': {}},
                                                                   'multiply_2_totalflux': {'linear': {}}}},
                       'LC_CHEOPS_instPC0': {'do': False,
                                             'what to decorrelate': {'add_2_totalflux': {'linear': {}},
                                                                     'multiply_2_totalflux': {'linear': {}}}},
                       'LC_CHEOPS_instPC1': {'do': False,
                                             'what to decorrelate': {'add_2_totalflux': {'linear': {}},
                                                                     'multiply_2_totalflux': {'linear': {}}}},
                       'LC_CHEOPS_instPC2': {'do': False,
                                             'what to decorrelate': {'add_2_totalflux': {'linear': {}},
                                                                     'multiply_2_totalflux': {'linear': {}}}}}
decorrelation_likelihood = {'LC_CHEOPS_inst0': {'do': True,
                                                'order': [('bispline', 'XY0'), ('spline', 'IND-BKG_CHEOPS_inst'), ('spline', 'IND-TF_CHEOPS_inst'), ('spline', 'IND-ROLL_CHEOPS_inst'), ],
                                                'bispline': {'XY0': {'IND instument models': ['IND-CX_CHEOPS_inst', 'IND-CY_CHEOPS_inst'],
                                                                     'quantity': 'raw',
                                                                     'spline_type': 'SmoothBivariateSpline',
                                                                     'spline_kwargs': {'kx': 3, 'ky': 3},
                                                                     'match datasets': {'LC_WASP-76_CHEOPS_100': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_100',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_100'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_101': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_101',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_101'
                                                                                                                  },
                                                                                        }
                                                                     },
                                                             },
                                                'spline': {'IND-ROLL_CHEOPS_inst': {'quantity': 'raw',
                                                                                    'spline_type': 'UnivariateSpline',
                                                                                    'spline_kwargs': {'k': 3, },
                                                                                    'match datasets': {'LC_WASP-76_CHEOPS_100': 'IND-ROLL_WASP-76_CHEOPS_100',
                                                                                                       'LC_WASP-76_CHEOPS_101': 'IND-ROLL_WASP-76_CHEOPS_101',
                                                                                                       'LC_WASP-76_CHEOPS_102': 'IND-ROLL_WASP-76_CHEOPS_102',
                                                                                                       'LC_WASP-76_CHEOPS_103': 'IND-ROLL_WASP-76_CHEOPS_103',
                                                                                                       'LC_WASP-76_CHEOPS_104': 'IND-ROLL_WASP-76_CHEOPS_104',
                                                                                                       'LC_WASP-76_CHEOPS_105': 'IND-ROLL_WASP-76_CHEOPS_105',
                                                                                                       'LC_WASP-76_CHEOPS_106': 'IND-ROLL_WASP-76_CHEOPS_106',
                                                                                                       'LC_WASP-76_CHEOPS_107': 'IND-ROLL_WASP-76_CHEOPS_107',
                                                                                                       'LC_WASP-76_CHEOPS_108': 'IND-ROLL_WASP-76_CHEOPS_108',
                                                                                                       'LC_WASP-76_CHEOPS_109': 'IND-ROLL_WASP-76_CHEOPS_109',
                                                                                                       'LC_WASP-76_CHEOPS_110': 'IND-ROLL_WASP-76_CHEOPS_110',
                                                                                                       'LC_WASP-76_CHEOPS_111': 'IND-ROLL_WASP-76_CHEOPS_111',
                                                                                                       'LC_WASP-76_CHEOPS_112': 'IND-ROLL_WASP-76_CHEOPS_112',
                                                                                                       'LC_WASP-76_CHEOPS_113': 'IND-ROLL_WASP-76_CHEOPS_113',
                                                                                                       'LC_WASP-76_CHEOPS_114': 'IND-ROLL_WASP-76_CHEOPS_114',
                                                                                                       'LC_WASP-76_CHEOPS_115': 'IND-ROLL_WASP-76_CHEOPS_115',
                                                                                                       'LC_WASP-76_CHEOPS_116': 'IND-ROLL_WASP-76_CHEOPS_116',
                                                                                                       'LC_WASP-76_CHEOPS_117': 'IND-ROLL_WASP-76_CHEOPS_117',
                                                                                                       'LC_WASP-76_CHEOPS_118': 'IND-ROLL_WASP-76_CHEOPS_118',
                                                                                                       'LC_WASP-76_CHEOPS_119': 'IND-ROLL_WASP-76_CHEOPS_119',
                                                                                                       'LC_WASP-76_CHEOPS_0': 'IND-ROLL_WASP-76_CHEOPS_0',
                                                                                                       'LC_WASP-76_CHEOPS_1': 'IND-ROLL_WASP-76_CHEOPS_1',
                                                                                                       'LC_WASP-76_CHEOPS_2': 'IND-ROLL_WASP-76_CHEOPS_2',
                                                                                                       }
                                                                                    },
                                                           'IND-BKG_CHEOPS_inst': {'quantity': 'raw',
                                                                                   'spline_type': 'UnivariateSpline',
                                                                                   'spline_kwargs': {'k': 3, },
                                                                                   'match datasets': {'LC_WASP-76_CHEOPS_100': 'IND-BKG_WASP-76_CHEOPS_100', }
                                                                                   },
                                                           'IND-TF_CHEOPS_inst': {'quantity': 'raw',
                                                                                  'spline_type': 'UnivariateSpline',
                                                                                  'spline_kwargs': {'k': 3, },
                                                                                  'match datasets': {'LC_WASP-76_CHEOPS_100': 'IND-TF_WASP-76_CHEOPS_100', }
                                                                                  },
                                                           }
                                                },
                            'LC_CHEOPS_inst1': {'do': True,
                                                'order': [('bispline', 'XY0'), ('spline', 'IND-BKG_CHEOPS_inst'), ('spline', 'IND-TF_CHEOPS_inst'), ('spline', 'IND-ROLL_CHEOPS_inst'), ],
                                                'bispline': {'XY0': {'IND instument models': ['IND-CX_CHEOPS_inst', 'IND-CY_CHEOPS_inst'],
                                                                     'quantity': 'raw',
                                                                     'spline_type': 'SmoothBivariateSpline',
                                                                     'spline_kwargs': {'kx': 3, 'ky': 3},
                                                                     'match datasets': {'LC_WASP-76_CHEOPS_100': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_100',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_100'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_101': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_101',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_101'
                                                                                                                  },
                                                                                        }
                                                                     },
                                                             },
                                                'spline': {'IND-ROLL_CHEOPS_inst': {'quantity': 'raw',
                                                                                    'spline_type': 'UnivariateSpline',
                                                                                    'spline_kwargs': {'k': 3, },
                                                                                    'match datasets': {'LC_WASP-76_CHEOPS_100': 'IND-ROLL_WASP-76_CHEOPS_100',
                                                                                                       'LC_WASP-76_CHEOPS_101': 'IND-ROLL_WASP-76_CHEOPS_101',
                                                                                                       'LC_WASP-76_CHEOPS_102': 'IND-ROLL_WASP-76_CHEOPS_102',
                                                                                                       'LC_WASP-76_CHEOPS_103': 'IND-ROLL_WASP-76_CHEOPS_103',
                                                                                                       'LC_WASP-76_CHEOPS_104': 'IND-ROLL_WASP-76_CHEOPS_104',
                                                                                                       'LC_WASP-76_CHEOPS_105': 'IND-ROLL_WASP-76_CHEOPS_105',
                                                                                                       'LC_WASP-76_CHEOPS_106': 'IND-ROLL_WASP-76_CHEOPS_106',
                                                                                                       'LC_WASP-76_CHEOPS_107': 'IND-ROLL_WASP-76_CHEOPS_107',
                                                                                                       'LC_WASP-76_CHEOPS_108': 'IND-ROLL_WASP-76_CHEOPS_108',
                                                                                                       'LC_WASP-76_CHEOPS_109': 'IND-ROLL_WASP-76_CHEOPS_109',
                                                                                                       'LC_WASP-76_CHEOPS_110': 'IND-ROLL_WASP-76_CHEOPS_110',
                                                                                                       'LC_WASP-76_CHEOPS_111': 'IND-ROLL_WASP-76_CHEOPS_111',
                                                                                                       'LC_WASP-76_CHEOPS_112': 'IND-ROLL_WASP-76_CHEOPS_112',
                                                                                                       'LC_WASP-76_CHEOPS_113': 'IND-ROLL_WASP-76_CHEOPS_113',
                                                                                                       'LC_WASP-76_CHEOPS_114': 'IND-ROLL_WASP-76_CHEOPS_114',
                                                                                                       'LC_WASP-76_CHEOPS_115': 'IND-ROLL_WASP-76_CHEOPS_115',
                                                                                                       'LC_WASP-76_CHEOPS_116': 'IND-ROLL_WASP-76_CHEOPS_116',
                                                                                                       'LC_WASP-76_CHEOPS_117': 'IND-ROLL_WASP-76_CHEOPS_117',
                                                                                                       'LC_WASP-76_CHEOPS_118': 'IND-ROLL_WASP-76_CHEOPS_118',
                                                                                                       'LC_WASP-76_CHEOPS_119': 'IND-ROLL_WASP-76_CHEOPS_119',
                                                                                                       'LC_WASP-76_CHEOPS_0': 'IND-ROLL_WASP-76_CHEOPS_0',
                                                                                                       'LC_WASP-76_CHEOPS_1': 'IND-ROLL_WASP-76_CHEOPS_1',
                                                                                                       'LC_WASP-76_CHEOPS_2': 'IND-ROLL_WASP-76_CHEOPS_2',
                                                                                                       }
                                                                                    },
                                                           'IND-BKG_CHEOPS_inst': {'quantity': 'raw',
                                                                                   'spline_type': 'UnivariateSpline',
                                                                                   'spline_kwargs': {'k': 3, },
                                                                                   'match datasets': {'LC_WASP-76_CHEOPS_101': 'IND-BKG_WASP-76_CHEOPS_101', }
                                                                                   },
                                                           'IND-TF_CHEOPS_inst': {'quantity': 'raw',
                                                                                  'spline_type': 'UnivariateSpline',
                                                                                  'spline_kwargs': {'k': 3, },
                                                                                  'match datasets': {'LC_WASP-76_CHEOPS_101': 'IND-TF_WASP-76_CHEOPS_101', }
                                                                                  },
                                                           }
                                                },
                            'LC_CHEOPS_inst2': {'do': True,
                                                'order': [('bispline', 'XY2'), ('spline', 'IND-BKG_CHEOPS_inst'), ('spline', 'IND-TF_CHEOPS_inst'), ('spline', 'IND-ROLL_CHEOPS_inst'), ],
                                                'bispline': {'XY2': {'IND instument models': ['IND-CX_CHEOPS_inst', 'IND-CY_CHEOPS_inst'],
                                                                     'quantity': 'raw',
                                                                     'spline_type': 'SmoothBivariateSpline',
                                                                     'spline_kwargs': {'kx': 3, 'ky': 3},
                                                                     'match datasets': {'LC_WASP-76_CHEOPS_102': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_102',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_102'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_103': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_103',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_103'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_104': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_104',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_104'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_105': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_105',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_105'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_106': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_106',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_106'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_107': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_107',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_107'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_108': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_108',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_108'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_109': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_109',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_109'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_110': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_110',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_110'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_111': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_111',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_111'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_112': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_112',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_112'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_113': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_113',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_113'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_114': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_114',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_114'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_0': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_0',
                                                                                                                'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_0'
                                                                                                                },
                                                                                        'LC_WASP-76_CHEOPS_1': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_1',
                                                                                                                'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_1'
                                                                                                                },
                                                                                        }
                                                                     },
                                                             },
                                                'spline': {'IND-ROLL_CHEOPS_inst': {'quantity': 'raw',
                                                                                    'spline_type': 'UnivariateSpline',
                                                                                    'spline_kwargs': {'k': 3, },
                                                                                    'match datasets': {'LC_WASP-76_CHEOPS_100': 'IND-ROLL_WASP-76_CHEOPS_100',
                                                                                                       'LC_WASP-76_CHEOPS_101': 'IND-ROLL_WASP-76_CHEOPS_101',
                                                                                                       'LC_WASP-76_CHEOPS_102': 'IND-ROLL_WASP-76_CHEOPS_102',
                                                                                                       'LC_WASP-76_CHEOPS_103': 'IND-ROLL_WASP-76_CHEOPS_103',
                                                                                                       'LC_WASP-76_CHEOPS_104': 'IND-ROLL_WASP-76_CHEOPS_104',
                                                                                                       'LC_WASP-76_CHEOPS_105': 'IND-ROLL_WASP-76_CHEOPS_105',
                                                                                                       'LC_WASP-76_CHEOPS_106': 'IND-ROLL_WASP-76_CHEOPS_106',
                                                                                                       'LC_WASP-76_CHEOPS_107': 'IND-ROLL_WASP-76_CHEOPS_107',
                                                                                                       'LC_WASP-76_CHEOPS_108': 'IND-ROLL_WASP-76_CHEOPS_108',
                                                                                                       'LC_WASP-76_CHEOPS_109': 'IND-ROLL_WASP-76_CHEOPS_109',
                                                                                                       'LC_WASP-76_CHEOPS_110': 'IND-ROLL_WASP-76_CHEOPS_110',
                                                                                                       'LC_WASP-76_CHEOPS_111': 'IND-ROLL_WASP-76_CHEOPS_111',
                                                                                                       'LC_WASP-76_CHEOPS_112': 'IND-ROLL_WASP-76_CHEOPS_112',
                                                                                                       'LC_WASP-76_CHEOPS_113': 'IND-ROLL_WASP-76_CHEOPS_113',
                                                                                                       'LC_WASP-76_CHEOPS_114': 'IND-ROLL_WASP-76_CHEOPS_114',
                                                                                                       'LC_WASP-76_CHEOPS_115': 'IND-ROLL_WASP-76_CHEOPS_115',
                                                                                                       'LC_WASP-76_CHEOPS_116': 'IND-ROLL_WASP-76_CHEOPS_116',
                                                                                                       'LC_WASP-76_CHEOPS_117': 'IND-ROLL_WASP-76_CHEOPS_117',
                                                                                                       'LC_WASP-76_CHEOPS_118': 'IND-ROLL_WASP-76_CHEOPS_118',
                                                                                                       'LC_WASP-76_CHEOPS_119': 'IND-ROLL_WASP-76_CHEOPS_119',
                                                                                                       'LC_WASP-76_CHEOPS_0': 'IND-ROLL_WASP-76_CHEOPS_0',
                                                                                                       'LC_WASP-76_CHEOPS_1': 'IND-ROLL_WASP-76_CHEOPS_1',
                                                                                                       'LC_WASP-76_CHEOPS_2': 'IND-ROLL_WASP-76_CHEOPS_2',
                                                                                                       }
                                                                                    },
                                                           'IND-BKG_CHEOPS_inst': {'quantity': 'raw',
                                                                                   'spline_type': 'UnivariateSpline',
                                                                                   'spline_kwargs': {'k': 3, },
                                                                                   'match datasets': {'LC_WASP-76_CHEOPS_102': 'IND-BKG_WASP-76_CHEOPS_102', }
                                                                                   },
                                                           'IND-TF_CHEOPS_inst': {'quantity': 'raw',
                                                                                  'spline_type': 'UnivariateSpline',
                                                                                  'spline_kwargs': {'k': 3, },
                                                                                  'match datasets': {'LC_WASP-76_CHEOPS_102': 'IND-TF_WASP-76_CHEOPS_102', }
                                                                                  },
                                                           }
                                                },
                            'LC_CHEOPS_inst3': {'do': True,
                                                'order': [('bispline', 'XY2'), ('spline', 'IND-BKG_CHEOPS_inst'), ('spline', 'IND-TF_CHEOPS_inst'), ('spline', 'IND-ROLL_CHEOPS_inst'), ],
                                                'bispline': {'XY2': {'IND instument models': ['IND-CX_CHEOPS_inst', 'IND-CY_CHEOPS_inst'],
                                                                     'quantity': 'raw',
                                                                     'spline_type': 'SmoothBivariateSpline',
                                                                     'spline_kwargs': {'kx': 3, 'ky': 3},
                                                                     'match datasets': {'LC_WASP-76_CHEOPS_102': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_102',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_102'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_103': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_103',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_103'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_104': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_104',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_104'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_105': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_105',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_105'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_106': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_106',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_106'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_107': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_107',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_107'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_108': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_108',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_108'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_109': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_109',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_109'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_110': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_110',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_110'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_111': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_111',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_111'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_112': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_112',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_112'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_113': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_113',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_113'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_114': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_114',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_114'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_0': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_0',
                                                                                                                'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_0'
                                                                                                                },
                                                                                        'LC_WASP-76_CHEOPS_1': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_1',
                                                                                                                'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_1'
                                                                                                                },
                                                                                        }
                                                                     },
                                                             },
                                                'spline': {'IND-ROLL_CHEOPS_inst': {'quantity': 'raw',
                                                                                    'spline_type': 'UnivariateSpline',
                                                                                    'spline_kwargs': {'k': 3, },
                                                                                    'match datasets': {'LC_WASP-76_CHEOPS_100': 'IND-ROLL_WASP-76_CHEOPS_100',
                                                                                                       'LC_WASP-76_CHEOPS_101': 'IND-ROLL_WASP-76_CHEOPS_101',
                                                                                                       'LC_WASP-76_CHEOPS_102': 'IND-ROLL_WASP-76_CHEOPS_102',
                                                                                                       'LC_WASP-76_CHEOPS_103': 'IND-ROLL_WASP-76_CHEOPS_103',
                                                                                                       'LC_WASP-76_CHEOPS_104': 'IND-ROLL_WASP-76_CHEOPS_104',
                                                                                                       'LC_WASP-76_CHEOPS_105': 'IND-ROLL_WASP-76_CHEOPS_105',
                                                                                                       'LC_WASP-76_CHEOPS_106': 'IND-ROLL_WASP-76_CHEOPS_106',
                                                                                                       'LC_WASP-76_CHEOPS_107': 'IND-ROLL_WASP-76_CHEOPS_107',
                                                                                                       'LC_WASP-76_CHEOPS_108': 'IND-ROLL_WASP-76_CHEOPS_108',
                                                                                                       'LC_WASP-76_CHEOPS_109': 'IND-ROLL_WASP-76_CHEOPS_109',
                                                                                                       'LC_WASP-76_CHEOPS_110': 'IND-ROLL_WASP-76_CHEOPS_110',
                                                                                                       'LC_WASP-76_CHEOPS_111': 'IND-ROLL_WASP-76_CHEOPS_111',
                                                                                                       'LC_WASP-76_CHEOPS_112': 'IND-ROLL_WASP-76_CHEOPS_112',
                                                                                                       'LC_WASP-76_CHEOPS_113': 'IND-ROLL_WASP-76_CHEOPS_113',
                                                                                                       'LC_WASP-76_CHEOPS_114': 'IND-ROLL_WASP-76_CHEOPS_114',
                                                                                                       'LC_WASP-76_CHEOPS_115': 'IND-ROLL_WASP-76_CHEOPS_115',
                                                                                                       'LC_WASP-76_CHEOPS_116': 'IND-ROLL_WASP-76_CHEOPS_116',
                                                                                                       'LC_WASP-76_CHEOPS_117': 'IND-ROLL_WASP-76_CHEOPS_117',
                                                                                                       'LC_WASP-76_CHEOPS_118': 'IND-ROLL_WASP-76_CHEOPS_118',
                                                                                                       'LC_WASP-76_CHEOPS_119': 'IND-ROLL_WASP-76_CHEOPS_119',
                                                                                                       'LC_WASP-76_CHEOPS_0': 'IND-ROLL_WASP-76_CHEOPS_0',
                                                                                                       'LC_WASP-76_CHEOPS_1': 'IND-ROLL_WASP-76_CHEOPS_1',
                                                                                                       'LC_WASP-76_CHEOPS_2': 'IND-ROLL_WASP-76_CHEOPS_2',
                                                                                                       }
                                                                                    },
                                                           'IND-BKG_CHEOPS_inst': {'quantity': 'raw',
                                                                                   'spline_type': 'UnivariateSpline',
                                                                                   'spline_kwargs': {'k': 3, },
                                                                                   'match datasets': {'LC_WASP-76_CHEOPS_103': 'IND-BKG_WASP-76_CHEOPS_103', }
                                                                                   },
                                                           'IND-TF_CHEOPS_inst': {'quantity': 'raw',
                                                                                  'spline_type': 'UnivariateSpline',
                                                                                  'spline_kwargs': {'k': 3, },
                                                                                  'match datasets': {'LC_WASP-76_CHEOPS_103': 'IND-TF_WASP-76_CHEOPS_103', }
                                                                                  },
                                                           }
                                                },
                            'LC_CHEOPS_inst4': {'do': True,
                                                'order': [('bispline', 'XY2'), ('spline', 'IND-BKG_CHEOPS_inst'), ('spline', 'IND-TF_CHEOPS_inst'), ('spline', 'IND-ROLL_CHEOPS_inst'), ],
                                                'bispline': {'XY2': {'IND instument models': ['IND-CX_CHEOPS_inst', 'IND-CY_CHEOPS_inst'],
                                                                     'quantity': 'raw',
                                                                     'spline_type': 'SmoothBivariateSpline',
                                                                     'spline_kwargs': {'kx': 3, 'ky': 3},
                                                                     'match datasets': {'LC_WASP-76_CHEOPS_102': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_102',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_102'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_103': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_103',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_103'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_104': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_104',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_104'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_105': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_105',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_105'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_106': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_106',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_106'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_107': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_107',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_107'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_108': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_108',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_108'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_109': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_109',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_109'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_110': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_110',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_110'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_111': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_111',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_111'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_112': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_112',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_112'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_113': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_113',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_113'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_114': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_114',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_114'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_0': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_0',
                                                                                                                'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_0'
                                                                                                                },
                                                                                        'LC_WASP-76_CHEOPS_1': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_1',
                                                                                                                'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_1'
                                                                                                                },
                                                                                        }
                                                                     },
                                                             },
                                                'spline': {'IND-ROLL_CHEOPS_inst': {'quantity': 'raw',
                                                                                    'spline_type': 'UnivariateSpline',
                                                                                    'spline_kwargs': {'k': 3, },
                                                                                    'match datasets': {'LC_WASP-76_CHEOPS_100': 'IND-ROLL_WASP-76_CHEOPS_100',
                                                                                                       'LC_WASP-76_CHEOPS_101': 'IND-ROLL_WASP-76_CHEOPS_101',
                                                                                                       'LC_WASP-76_CHEOPS_102': 'IND-ROLL_WASP-76_CHEOPS_102',
                                                                                                       'LC_WASP-76_CHEOPS_103': 'IND-ROLL_WASP-76_CHEOPS_103',
                                                                                                       'LC_WASP-76_CHEOPS_104': 'IND-ROLL_WASP-76_CHEOPS_104',
                                                                                                       'LC_WASP-76_CHEOPS_105': 'IND-ROLL_WASP-76_CHEOPS_105',
                                                                                                       'LC_WASP-76_CHEOPS_106': 'IND-ROLL_WASP-76_CHEOPS_106',
                                                                                                       'LC_WASP-76_CHEOPS_107': 'IND-ROLL_WASP-76_CHEOPS_107',
                                                                                                       'LC_WASP-76_CHEOPS_108': 'IND-ROLL_WASP-76_CHEOPS_108',
                                                                                                       'LC_WASP-76_CHEOPS_109': 'IND-ROLL_WASP-76_CHEOPS_109',
                                                                                                       'LC_WASP-76_CHEOPS_110': 'IND-ROLL_WASP-76_CHEOPS_110',
                                                                                                       'LC_WASP-76_CHEOPS_111': 'IND-ROLL_WASP-76_CHEOPS_111',
                                                                                                       'LC_WASP-76_CHEOPS_112': 'IND-ROLL_WASP-76_CHEOPS_112',
                                                                                                       'LC_WASP-76_CHEOPS_113': 'IND-ROLL_WASP-76_CHEOPS_113',
                                                                                                       'LC_WASP-76_CHEOPS_114': 'IND-ROLL_WASP-76_CHEOPS_114',
                                                                                                       'LC_WASP-76_CHEOPS_115': 'IND-ROLL_WASP-76_CHEOPS_115',
                                                                                                       'LC_WASP-76_CHEOPS_116': 'IND-ROLL_WASP-76_CHEOPS_116',
                                                                                                       'LC_WASP-76_CHEOPS_117': 'IND-ROLL_WASP-76_CHEOPS_117',
                                                                                                       'LC_WASP-76_CHEOPS_118': 'IND-ROLL_WASP-76_CHEOPS_118',
                                                                                                       'LC_WASP-76_CHEOPS_119': 'IND-ROLL_WASP-76_CHEOPS_119',
                                                                                                       'LC_WASP-76_CHEOPS_0': 'IND-ROLL_WASP-76_CHEOPS_0',
                                                                                                       'LC_WASP-76_CHEOPS_1': 'IND-ROLL_WASP-76_CHEOPS_1',
                                                                                                       'LC_WASP-76_CHEOPS_2': 'IND-ROLL_WASP-76_CHEOPS_2',
                                                                                                       }
                                                                                    },
                                                           'IND-BKG_CHEOPS_inst': {'quantity': 'raw',
                                                                                   'spline_type': 'UnivariateSpline',
                                                                                   'spline_kwargs': {'k': 3, },
                                                                                   'match datasets': {'LC_WASP-76_CHEOPS_104': 'IND-BKG_WASP-76_CHEOPS_104', }
                                                                                   },
                                                           'IND-TF_CHEOPS_inst': {'quantity': 'raw',
                                                                                  'spline_type': 'UnivariateSpline',
                                                                                  'spline_kwargs': {'k': 3, },
                                                                                  'match datasets': {'LC_WASP-76_CHEOPS_104': 'IND-TF_WASP-76_CHEOPS_104', }
                                                                                  },
                                                           }
                                                },
                            'LC_CHEOPS_inst5': {'do': True,
                                                'order': [('bispline', 'XY2'), ('spline', 'IND-BKG_CHEOPS_inst'), ('spline', 'IND-TF_CHEOPS_inst'), ('spline', 'IND-ROLL_CHEOPS_inst'), ],
                                                'bispline': {'XY2': {'IND instument models': ['IND-CX_CHEOPS_inst', 'IND-CY_CHEOPS_inst'],
                                                                     'quantity': 'raw',
                                                                     'spline_type': 'SmoothBivariateSpline',
                                                                     'spline_kwargs': {'kx': 3, 'ky': 3},
                                                                     'match datasets': {'LC_WASP-76_CHEOPS_102': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_102',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_102'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_103': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_103',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_103'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_104': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_104',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_104'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_105': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_105',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_105'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_106': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_106',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_106'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_107': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_107',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_107'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_108': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_108',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_108'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_109': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_109',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_109'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_110': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_110',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_110'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_111': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_111',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_111'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_112': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_112',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_112'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_113': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_113',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_113'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_114': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_114',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_114'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_0': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_0',
                                                                                                                'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_0'
                                                                                                                },
                                                                                        'LC_WASP-76_CHEOPS_1': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_1',
                                                                                                                'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_1'
                                                                                                                },
                                                                                        }
                                                                     },
                                                             },
                                                'spline': {'IND-ROLL_CHEOPS_inst': {'quantity': 'raw',
                                                                                    'spline_type': 'UnivariateSpline',
                                                                                    'spline_kwargs': {'k': 3, },
                                                                                    'match datasets': {'LC_WASP-76_CHEOPS_100': 'IND-ROLL_WASP-76_CHEOPS_100',
                                                                                                       'LC_WASP-76_CHEOPS_101': 'IND-ROLL_WASP-76_CHEOPS_101',
                                                                                                       'LC_WASP-76_CHEOPS_102': 'IND-ROLL_WASP-76_CHEOPS_102',
                                                                                                       'LC_WASP-76_CHEOPS_103': 'IND-ROLL_WASP-76_CHEOPS_103',
                                                                                                       'LC_WASP-76_CHEOPS_104': 'IND-ROLL_WASP-76_CHEOPS_104',
                                                                                                       'LC_WASP-76_CHEOPS_105': 'IND-ROLL_WASP-76_CHEOPS_105',
                                                                                                       'LC_WASP-76_CHEOPS_106': 'IND-ROLL_WASP-76_CHEOPS_106',
                                                                                                       'LC_WASP-76_CHEOPS_107': 'IND-ROLL_WASP-76_CHEOPS_107',
                                                                                                       'LC_WASP-76_CHEOPS_108': 'IND-ROLL_WASP-76_CHEOPS_108',
                                                                                                       'LC_WASP-76_CHEOPS_109': 'IND-ROLL_WASP-76_CHEOPS_109',
                                                                                                       'LC_WASP-76_CHEOPS_110': 'IND-ROLL_WASP-76_CHEOPS_110',
                                                                                                       'LC_WASP-76_CHEOPS_111': 'IND-ROLL_WASP-76_CHEOPS_111',
                                                                                                       'LC_WASP-76_CHEOPS_112': 'IND-ROLL_WASP-76_CHEOPS_112',
                                                                                                       'LC_WASP-76_CHEOPS_113': 'IND-ROLL_WASP-76_CHEOPS_113',
                                                                                                       'LC_WASP-76_CHEOPS_114': 'IND-ROLL_WASP-76_CHEOPS_114',
                                                                                                       'LC_WASP-76_CHEOPS_115': 'IND-ROLL_WASP-76_CHEOPS_115',
                                                                                                       'LC_WASP-76_CHEOPS_116': 'IND-ROLL_WASP-76_CHEOPS_116',
                                                                                                       'LC_WASP-76_CHEOPS_117': 'IND-ROLL_WASP-76_CHEOPS_117',
                                                                                                       'LC_WASP-76_CHEOPS_118': 'IND-ROLL_WASP-76_CHEOPS_118',
                                                                                                       'LC_WASP-76_CHEOPS_119': 'IND-ROLL_WASP-76_CHEOPS_119',
                                                                                                       'LC_WASP-76_CHEOPS_0': 'IND-ROLL_WASP-76_CHEOPS_0',
                                                                                                       'LC_WASP-76_CHEOPS_1': 'IND-ROLL_WASP-76_CHEOPS_1',
                                                                                                       'LC_WASP-76_CHEOPS_2': 'IND-ROLL_WASP-76_CHEOPS_2',
                                                                                                       }
                                                                                    },
                                                           'IND-BKG_CHEOPS_inst': {'quantity': 'raw',
                                                                                   'spline_type': 'UnivariateSpline',
                                                                                   'spline_kwargs': {'k': 3, },
                                                                                   'match datasets': {'LC_WASP-76_CHEOPS_105': 'IND-BKG_WASP-76_CHEOPS_105', }
                                                                                   },
                                                           'IND-TF_CHEOPS_inst': {'quantity': 'raw',
                                                                                  'spline_type': 'UnivariateSpline',
                                                                                  'spline_kwargs': {'k': 3, },
                                                                                  'match datasets': {'LC_WASP-76_CHEOPS_105': 'IND-TF_WASP-76_CHEOPS_105', }
                                                                                  },
                                                           }
                                                },
                            'LC_CHEOPS_inst6': {'do': True,
                                                'order': [('bispline', 'XY2'), ('spline', 'IND-BKG_CHEOPS_inst'), ('spline', 'IND-TF_CHEOPS_inst'), ('spline', 'IND-ROLL_CHEOPS_inst'), ],
                                                'bispline': {'XY2': {'IND instument models': ['IND-CX_CHEOPS_inst', 'IND-CY_CHEOPS_inst'],
                                                                     'quantity': 'raw',
                                                                     'spline_type': 'SmoothBivariateSpline',
                                                                     'spline_kwargs': {'kx': 3, 'ky': 3},
                                                                     'match datasets': {'LC_WASP-76_CHEOPS_102': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_102',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_102'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_103': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_103',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_103'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_104': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_104',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_104'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_105': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_105',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_105'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_106': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_106',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_106'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_107': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_107',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_107'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_108': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_108',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_108'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_109': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_109',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_109'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_110': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_110',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_110'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_111': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_111',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_111'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_112': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_112',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_112'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_113': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_113',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_113'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_114': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_114',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_114'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_0': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_0',
                                                                                                                'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_0'
                                                                                                                },
                                                                                        'LC_WASP-76_CHEOPS_1': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_1',
                                                                                                                'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_1'
                                                                                                                },
                                                                                        }
                                                                     },
                                                             },
                                                'spline': {'IND-ROLL_CHEOPS_inst': {'quantity': 'raw',
                                                                                    'spline_type': 'UnivariateSpline',
                                                                                    'spline_kwargs': {'k': 3, },
                                                                                    'match datasets': {'LC_WASP-76_CHEOPS_100': 'IND-ROLL_WASP-76_CHEOPS_100',
                                                                                                       'LC_WASP-76_CHEOPS_101': 'IND-ROLL_WASP-76_CHEOPS_101',
                                                                                                       'LC_WASP-76_CHEOPS_102': 'IND-ROLL_WASP-76_CHEOPS_102',
                                                                                                       'LC_WASP-76_CHEOPS_103': 'IND-ROLL_WASP-76_CHEOPS_103',
                                                                                                       'LC_WASP-76_CHEOPS_104': 'IND-ROLL_WASP-76_CHEOPS_104',
                                                                                                       'LC_WASP-76_CHEOPS_105': 'IND-ROLL_WASP-76_CHEOPS_105',
                                                                                                       'LC_WASP-76_CHEOPS_106': 'IND-ROLL_WASP-76_CHEOPS_106',
                                                                                                       'LC_WASP-76_CHEOPS_107': 'IND-ROLL_WASP-76_CHEOPS_107',
                                                                                                       'LC_WASP-76_CHEOPS_108': 'IND-ROLL_WASP-76_CHEOPS_108',
                                                                                                       'LC_WASP-76_CHEOPS_109': 'IND-ROLL_WASP-76_CHEOPS_109',
                                                                                                       'LC_WASP-76_CHEOPS_110': 'IND-ROLL_WASP-76_CHEOPS_110',
                                                                                                       'LC_WASP-76_CHEOPS_111': 'IND-ROLL_WASP-76_CHEOPS_111',
                                                                                                       'LC_WASP-76_CHEOPS_112': 'IND-ROLL_WASP-76_CHEOPS_112',
                                                                                                       'LC_WASP-76_CHEOPS_113': 'IND-ROLL_WASP-76_CHEOPS_113',
                                                                                                       'LC_WASP-76_CHEOPS_114': 'IND-ROLL_WASP-76_CHEOPS_114',
                                                                                                       'LC_WASP-76_CHEOPS_115': 'IND-ROLL_WASP-76_CHEOPS_115',
                                                                                                       'LC_WASP-76_CHEOPS_116': 'IND-ROLL_WASP-76_CHEOPS_116',
                                                                                                       'LC_WASP-76_CHEOPS_117': 'IND-ROLL_WASP-76_CHEOPS_117',
                                                                                                       'LC_WASP-76_CHEOPS_118': 'IND-ROLL_WASP-76_CHEOPS_118',
                                                                                                       'LC_WASP-76_CHEOPS_119': 'IND-ROLL_WASP-76_CHEOPS_119',
                                                                                                       'LC_WASP-76_CHEOPS_0': 'IND-ROLL_WASP-76_CHEOPS_0',
                                                                                                       'LC_WASP-76_CHEOPS_1': 'IND-ROLL_WASP-76_CHEOPS_1',
                                                                                                       'LC_WASP-76_CHEOPS_2': 'IND-ROLL_WASP-76_CHEOPS_2',
                                                                                                       }
                                                                                    },
                                                           'IND-BKG_CHEOPS_inst': {'quantity': 'raw',
                                                                                   'spline_type': 'UnivariateSpline',
                                                                                   'spline_kwargs': {'k': 3, },
                                                                                   'match datasets': {'LC_WASP-76_CHEOPS_106': 'IND-BKG_WASP-76_CHEOPS_106', }
                                                                                   },
                                                           'IND-TF_CHEOPS_inst': {'quantity': 'raw',
                                                                                  'spline_type': 'UnivariateSpline',
                                                                                  'spline_kwargs': {'k': 3, },
                                                                                  'match datasets': {'LC_WASP-76_CHEOPS_106': 'IND-TF_WASP-76_CHEOPS_106', }
                                                                                  },
                                                           }
                                                },
                            'LC_CHEOPS_inst7': {'do': True,
                                                'order': [('bispline', 'XY2'), ('spline', 'IND-BKG_CHEOPS_inst'), ('spline', 'IND-TF_CHEOPS_inst'), ('spline', 'IND-ROLL_CHEOPS_inst'), ],
                                                'bispline': {'XY2': {'IND instument models': ['IND-CX_CHEOPS_inst', 'IND-CY_CHEOPS_inst'],
                                                                     'quantity': 'raw',
                                                                     'spline_type': 'SmoothBivariateSpline',
                                                                     'spline_kwargs': {'kx': 3, 'ky': 3},
                                                                     'match datasets': {'LC_WASP-76_CHEOPS_102': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_102',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_102'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_103': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_103',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_103'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_104': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_104',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_104'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_105': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_105',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_105'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_106': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_106',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_106'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_107': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_107',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_107'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_108': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_108',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_108'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_109': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_109',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_109'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_110': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_110',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_110'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_111': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_111',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_111'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_112': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_112',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_112'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_113': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_113',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_113'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_114': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_114',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_114'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_0': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_0',
                                                                                                                'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_0'
                                                                                                                },
                                                                                        'LC_WASP-76_CHEOPS_1': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_1',
                                                                                                                'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_1'
                                                                                                                },
                                                                                        }
                                                                     },
                                                             },
                                                'spline': {'IND-ROLL_CHEOPS_inst': {'quantity': 'raw',
                                                                                    'spline_type': 'UnivariateSpline',
                                                                                    'spline_kwargs': {'k': 3, },
                                                                                    'match datasets': {'LC_WASP-76_CHEOPS_100': 'IND-ROLL_WASP-76_CHEOPS_100',
                                                                                                       'LC_WASP-76_CHEOPS_101': 'IND-ROLL_WASP-76_CHEOPS_101',
                                                                                                       'LC_WASP-76_CHEOPS_102': 'IND-ROLL_WASP-76_CHEOPS_102',
                                                                                                       'LC_WASP-76_CHEOPS_103': 'IND-ROLL_WASP-76_CHEOPS_103',
                                                                                                       'LC_WASP-76_CHEOPS_104': 'IND-ROLL_WASP-76_CHEOPS_104',
                                                                                                       'LC_WASP-76_CHEOPS_105': 'IND-ROLL_WASP-76_CHEOPS_105',
                                                                                                       'LC_WASP-76_CHEOPS_106': 'IND-ROLL_WASP-76_CHEOPS_106',
                                                                                                       'LC_WASP-76_CHEOPS_107': 'IND-ROLL_WASP-76_CHEOPS_107',
                                                                                                       'LC_WASP-76_CHEOPS_108': 'IND-ROLL_WASP-76_CHEOPS_108',
                                                                                                       'LC_WASP-76_CHEOPS_109': 'IND-ROLL_WASP-76_CHEOPS_109',
                                                                                                       'LC_WASP-76_CHEOPS_110': 'IND-ROLL_WASP-76_CHEOPS_110',
                                                                                                       'LC_WASP-76_CHEOPS_111': 'IND-ROLL_WASP-76_CHEOPS_111',
                                                                                                       'LC_WASP-76_CHEOPS_112': 'IND-ROLL_WASP-76_CHEOPS_112',
                                                                                                       'LC_WASP-76_CHEOPS_113': 'IND-ROLL_WASP-76_CHEOPS_113',
                                                                                                       'LC_WASP-76_CHEOPS_114': 'IND-ROLL_WASP-76_CHEOPS_114',
                                                                                                       'LC_WASP-76_CHEOPS_115': 'IND-ROLL_WASP-76_CHEOPS_115',
                                                                                                       'LC_WASP-76_CHEOPS_116': 'IND-ROLL_WASP-76_CHEOPS_116',
                                                                                                       'LC_WASP-76_CHEOPS_117': 'IND-ROLL_WASP-76_CHEOPS_117',
                                                                                                       'LC_WASP-76_CHEOPS_118': 'IND-ROLL_WASP-76_CHEOPS_118',
                                                                                                       'LC_WASP-76_CHEOPS_119': 'IND-ROLL_WASP-76_CHEOPS_119',
                                                                                                       'LC_WASP-76_CHEOPS_0': 'IND-ROLL_WASP-76_CHEOPS_0',
                                                                                                       'LC_WASP-76_CHEOPS_1': 'IND-ROLL_WASP-76_CHEOPS_1',
                                                                                                       'LC_WASP-76_CHEOPS_2': 'IND-ROLL_WASP-76_CHEOPS_2',
                                                                                                       }
                                                                                    },
                                                           'IND-BKG_CHEOPS_inst': {'quantity': 'raw',
                                                                                   'spline_type': 'UnivariateSpline',
                                                                                   'spline_kwargs': {'k': 3, },
                                                                                   'match datasets': {'LC_WASP-76_CHEOPS_107': 'IND-BKG_WASP-76_CHEOPS_107', }
                                                                                   },
                                                           'IND-TF_CHEOPS_inst': {'quantity': 'raw',
                                                                                  'spline_type': 'UnivariateSpline',
                                                                                  'spline_kwargs': {'k': 3, },
                                                                                  'match datasets': {'LC_WASP-76_CHEOPS_107': 'IND-TF_WASP-76_CHEOPS_107', }
                                                                                  },
                                                           }
                                                },
                            'LC_CHEOPS_inst8': {'do': True,
                                                'order': [('bispline', 'XY2'), ('spline', 'IND-BKG_CHEOPS_inst'), ('spline', 'IND-TF_CHEOPS_inst'), ('spline', 'IND-ROLL_CHEOPS_inst'), ],
                                                'bispline': {'XY2': {'IND instument models': ['IND-CX_CHEOPS_inst', 'IND-CY_CHEOPS_inst'],
                                                                     'quantity': 'raw',
                                                                     'spline_type': 'SmoothBivariateSpline',
                                                                     'spline_kwargs': {'kx': 3, 'ky': 3},
                                                                     'match datasets': {'LC_WASP-76_CHEOPS_102': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_102',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_102'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_103': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_103',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_103'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_104': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_104',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_104'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_105': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_105',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_105'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_106': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_106',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_106'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_107': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_107',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_107'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_108': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_108',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_108'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_109': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_109',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_109'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_110': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_110',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_110'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_111': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_111',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_111'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_112': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_112',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_112'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_113': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_113',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_113'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_114': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_114',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_114'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_0': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_0',
                                                                                                                'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_0'
                                                                                                                },
                                                                                        'LC_WASP-76_CHEOPS_1': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_1',
                                                                                                                'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_1'
                                                                                                                },
                                                                                        }
                                                                     },
                                                             },
                                                'spline': {'IND-ROLL_CHEOPS_inst': {'quantity': 'raw',
                                                                                    'spline_type': 'UnivariateSpline',
                                                                                    'spline_kwargs': {'k': 3, },
                                                                                    'match datasets': {'LC_WASP-76_CHEOPS_100': 'IND-ROLL_WASP-76_CHEOPS_100',
                                                                                                       'LC_WASP-76_CHEOPS_101': 'IND-ROLL_WASP-76_CHEOPS_101',
                                                                                                       'LC_WASP-76_CHEOPS_102': 'IND-ROLL_WASP-76_CHEOPS_102',
                                                                                                       'LC_WASP-76_CHEOPS_103': 'IND-ROLL_WASP-76_CHEOPS_103',
                                                                                                       'LC_WASP-76_CHEOPS_104': 'IND-ROLL_WASP-76_CHEOPS_104',
                                                                                                       'LC_WASP-76_CHEOPS_105': 'IND-ROLL_WASP-76_CHEOPS_105',
                                                                                                       'LC_WASP-76_CHEOPS_106': 'IND-ROLL_WASP-76_CHEOPS_106',
                                                                                                       'LC_WASP-76_CHEOPS_107': 'IND-ROLL_WASP-76_CHEOPS_107',
                                                                                                       'LC_WASP-76_CHEOPS_108': 'IND-ROLL_WASP-76_CHEOPS_108',
                                                                                                       'LC_WASP-76_CHEOPS_109': 'IND-ROLL_WASP-76_CHEOPS_109',
                                                                                                       'LC_WASP-76_CHEOPS_110': 'IND-ROLL_WASP-76_CHEOPS_110',
                                                                                                       'LC_WASP-76_CHEOPS_111': 'IND-ROLL_WASP-76_CHEOPS_111',
                                                                                                       'LC_WASP-76_CHEOPS_112': 'IND-ROLL_WASP-76_CHEOPS_112',
                                                                                                       'LC_WASP-76_CHEOPS_113': 'IND-ROLL_WASP-76_CHEOPS_113',
                                                                                                       'LC_WASP-76_CHEOPS_114': 'IND-ROLL_WASP-76_CHEOPS_114',
                                                                                                       'LC_WASP-76_CHEOPS_115': 'IND-ROLL_WASP-76_CHEOPS_115',
                                                                                                       'LC_WASP-76_CHEOPS_116': 'IND-ROLL_WASP-76_CHEOPS_116',
                                                                                                       'LC_WASP-76_CHEOPS_117': 'IND-ROLL_WASP-76_CHEOPS_117',
                                                                                                       'LC_WASP-76_CHEOPS_118': 'IND-ROLL_WASP-76_CHEOPS_118',
                                                                                                       'LC_WASP-76_CHEOPS_119': 'IND-ROLL_WASP-76_CHEOPS_119',
                                                                                                       'LC_WASP-76_CHEOPS_0': 'IND-ROLL_WASP-76_CHEOPS_0',
                                                                                                       'LC_WASP-76_CHEOPS_1': 'IND-ROLL_WASP-76_CHEOPS_1',
                                                                                                       'LC_WASP-76_CHEOPS_2': 'IND-ROLL_WASP-76_CHEOPS_2',
                                                                                                       }
                                                                                    },
                                                           'IND-BKG_CHEOPS_inst': {'quantity': 'raw',
                                                                                   'spline_type': 'UnivariateSpline',
                                                                                   'spline_kwargs': {'k': 3, },
                                                                                   'match datasets': {'LC_WASP-76_CHEOPS_108': 'IND-BKG_WASP-76_CHEOPS_108', }
                                                                                   },
                                                           'IND-TF_CHEOPS_inst': {'quantity': 'raw',
                                                                                  'spline_type': 'UnivariateSpline',
                                                                                  'spline_kwargs': {'k': 3, },
                                                                                  'match datasets': {'LC_WASP-76_CHEOPS_108': 'IND-TF_WASP-76_CHEOPS_108', }
                                                                                  },
                                                           }
                                                },
                            'LC_CHEOPS_inst9': {'do': True,
                                                'order': [('bispline', 'XY2'), ('spline', 'IND-BKG_CHEOPS_inst'), ('spline', 'IND-TF_CHEOPS_inst'), ('spline', 'IND-ROLL_CHEOPS_inst'), ],
                                                'bispline': {'XY2': {'IND instument models': ['IND-CX_CHEOPS_inst', 'IND-CY_CHEOPS_inst'],
                                                                     'quantity': 'raw',
                                                                     'spline_type': 'SmoothBivariateSpline',
                                                                     'spline_kwargs': {'kx': 3, 'ky': 3},
                                                                     'match datasets': {'LC_WASP-76_CHEOPS_102': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_102',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_102'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_103': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_103',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_103'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_104': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_104',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_104'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_105': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_105',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_105'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_106': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_106',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_106'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_107': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_107',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_107'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_108': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_108',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_108'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_109': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_109',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_109'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_110': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_110',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_110'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_111': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_111',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_111'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_112': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_112',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_112'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_113': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_113',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_113'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_114': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_114',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_114'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_0': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_0',
                                                                                                                'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_0'
                                                                                                                },
                                                                                        'LC_WASP-76_CHEOPS_1': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_1',
                                                                                                                'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_1'
                                                                                                                },
                                                                                        }
                                                                     },
                                                             },
                                                'spline': {'IND-ROLL_CHEOPS_inst': {'quantity': 'raw',
                                                                                    'spline_type': 'UnivariateSpline',
                                                                                    'spline_kwargs': {'k': 3, },
                                                                                    'match datasets': {'LC_WASP-76_CHEOPS_100': 'IND-ROLL_WASP-76_CHEOPS_100',
                                                                                                       'LC_WASP-76_CHEOPS_101': 'IND-ROLL_WASP-76_CHEOPS_101',
                                                                                                       'LC_WASP-76_CHEOPS_102': 'IND-ROLL_WASP-76_CHEOPS_102',
                                                                                                       'LC_WASP-76_CHEOPS_103': 'IND-ROLL_WASP-76_CHEOPS_103',
                                                                                                       'LC_WASP-76_CHEOPS_104': 'IND-ROLL_WASP-76_CHEOPS_104',
                                                                                                       'LC_WASP-76_CHEOPS_105': 'IND-ROLL_WASP-76_CHEOPS_105',
                                                                                                       'LC_WASP-76_CHEOPS_106': 'IND-ROLL_WASP-76_CHEOPS_106',
                                                                                                       'LC_WASP-76_CHEOPS_107': 'IND-ROLL_WASP-76_CHEOPS_107',
                                                                                                       'LC_WASP-76_CHEOPS_108': 'IND-ROLL_WASP-76_CHEOPS_108',
                                                                                                       'LC_WASP-76_CHEOPS_109': 'IND-ROLL_WASP-76_CHEOPS_109',
                                                                                                       'LC_WASP-76_CHEOPS_110': 'IND-ROLL_WASP-76_CHEOPS_110',
                                                                                                       'LC_WASP-76_CHEOPS_111': 'IND-ROLL_WASP-76_CHEOPS_111',
                                                                                                       'LC_WASP-76_CHEOPS_112': 'IND-ROLL_WASP-76_CHEOPS_112',
                                                                                                       'LC_WASP-76_CHEOPS_113': 'IND-ROLL_WASP-76_CHEOPS_113',
                                                                                                       'LC_WASP-76_CHEOPS_114': 'IND-ROLL_WASP-76_CHEOPS_114',
                                                                                                       'LC_WASP-76_CHEOPS_115': 'IND-ROLL_WASP-76_CHEOPS_115',
                                                                                                       'LC_WASP-76_CHEOPS_116': 'IND-ROLL_WASP-76_CHEOPS_116',
                                                                                                       'LC_WASP-76_CHEOPS_117': 'IND-ROLL_WASP-76_CHEOPS_117',
                                                                                                       'LC_WASP-76_CHEOPS_118': 'IND-ROLL_WASP-76_CHEOPS_118',
                                                                                                       'LC_WASP-76_CHEOPS_119': 'IND-ROLL_WASP-76_CHEOPS_119',
                                                                                                       'LC_WASP-76_CHEOPS_0': 'IND-ROLL_WASP-76_CHEOPS_0',
                                                                                                       'LC_WASP-76_CHEOPS_1': 'IND-ROLL_WASP-76_CHEOPS_1',
                                                                                                       'LC_WASP-76_CHEOPS_2': 'IND-ROLL_WASP-76_CHEOPS_2',
                                                                                                       }
                                                                                    },
                                                           'IND-BKG_CHEOPS_inst': {'quantity': 'raw',
                                                                                   'spline_type': 'UnivariateSpline',
                                                                                   'spline_kwargs': {'k': 3, },
                                                                                   'match datasets': {'LC_WASP-76_CHEOPS_109': 'IND-BKG_WASP-76_CHEOPS_109', }
                                                                                   },
                                                           'IND-TF_CHEOPS_inst': {'quantity': 'raw',
                                                                                  'spline_type': 'UnivariateSpline',
                                                                                  'spline_kwargs': {'k': 3, },
                                                                                  'match datasets': {'LC_WASP-76_CHEOPS_109': 'IND-TF_WASP-76_CHEOPS_109', }
                                                                                  },
                                                           }
                                                },
                            'LC_CHEOPS_inst10': {'do': True,
                                                 'order': [('bispline', 'XY2'), ('spline', 'IND-BKG_CHEOPS_inst'), ('spline', 'IND-TF_CHEOPS_inst'), ('spline', 'IND-ROLL_CHEOPS_inst'), ],
                                                 'bispline': {'XY2': {'IND instument models': ['IND-CX_CHEOPS_inst', 'IND-CY_CHEOPS_inst'],
                                                                     'quantity': 'raw',
                                                                     'spline_type': 'SmoothBivariateSpline',
                                                                     'spline_kwargs': {'kx': 3, 'ky': 3},
                                                                     'match datasets': {'LC_WASP-76_CHEOPS_102': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_102',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_102'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_103': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_103',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_103'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_104': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_104',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_104'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_105': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_105',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_105'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_106': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_106',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_106'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_107': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_107',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_107'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_108': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_108',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_108'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_109': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_109',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_109'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_110': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_110',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_110'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_111': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_111',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_111'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_112': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_112',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_112'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_113': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_113',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_113'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_114': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_114',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_114'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_0': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_0',
                                                                                                                'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_0'
                                                                                                                },
                                                                                        'LC_WASP-76_CHEOPS_1': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_1',
                                                                                                                'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_1'
                                                                                                                },
                                                                                        }
                                                                     },
                                                             },
                                                'spline': {'IND-ROLL_CHEOPS_inst': {'quantity': 'raw',
                                                                                    'spline_type': 'UnivariateSpline',
                                                                                    'spline_kwargs': {'k': 3, },
                                                                                    'match datasets': {'LC_WASP-76_CHEOPS_100': 'IND-ROLL_WASP-76_CHEOPS_100',
                                                                                                       'LC_WASP-76_CHEOPS_101': 'IND-ROLL_WASP-76_CHEOPS_101',
                                                                                                       'LC_WASP-76_CHEOPS_102': 'IND-ROLL_WASP-76_CHEOPS_102',
                                                                                                       'LC_WASP-76_CHEOPS_103': 'IND-ROLL_WASP-76_CHEOPS_103',
                                                                                                       'LC_WASP-76_CHEOPS_104': 'IND-ROLL_WASP-76_CHEOPS_104',
                                                                                                       'LC_WASP-76_CHEOPS_105': 'IND-ROLL_WASP-76_CHEOPS_105',
                                                                                                       'LC_WASP-76_CHEOPS_106': 'IND-ROLL_WASP-76_CHEOPS_106',
                                                                                                       'LC_WASP-76_CHEOPS_107': 'IND-ROLL_WASP-76_CHEOPS_107',
                                                                                                       'LC_WASP-76_CHEOPS_108': 'IND-ROLL_WASP-76_CHEOPS_108',
                                                                                                       'LC_WASP-76_CHEOPS_109': 'IND-ROLL_WASP-76_CHEOPS_109',
                                                                                                       'LC_WASP-76_CHEOPS_110': 'IND-ROLL_WASP-76_CHEOPS_110',
                                                                                                       'LC_WASP-76_CHEOPS_111': 'IND-ROLL_WASP-76_CHEOPS_111',
                                                                                                       'LC_WASP-76_CHEOPS_112': 'IND-ROLL_WASP-76_CHEOPS_112',
                                                                                                       'LC_WASP-76_CHEOPS_113': 'IND-ROLL_WASP-76_CHEOPS_113',
                                                                                                       'LC_WASP-76_CHEOPS_114': 'IND-ROLL_WASP-76_CHEOPS_114',
                                                                                                       'LC_WASP-76_CHEOPS_115': 'IND-ROLL_WASP-76_CHEOPS_115',
                                                                                                       'LC_WASP-76_CHEOPS_116': 'IND-ROLL_WASP-76_CHEOPS_116',
                                                                                                       'LC_WASP-76_CHEOPS_117': 'IND-ROLL_WASP-76_CHEOPS_117',
                                                                                                       'LC_WASP-76_CHEOPS_118': 'IND-ROLL_WASP-76_CHEOPS_118',
                                                                                                       'LC_WASP-76_CHEOPS_119': 'IND-ROLL_WASP-76_CHEOPS_119',
                                                                                                       'LC_WASP-76_CHEOPS_0': 'IND-ROLL_WASP-76_CHEOPS_0',
                                                                                                       'LC_WASP-76_CHEOPS_1': 'IND-ROLL_WASP-76_CHEOPS_1',
                                                                                                       'LC_WASP-76_CHEOPS_2': 'IND-ROLL_WASP-76_CHEOPS_2',
                                                                                                       }
                                                                                    },
                                                           'IND-BKG_CHEOPS_inst': {'quantity': 'raw',
                                                                                   'spline_type': 'UnivariateSpline',
                                                                                   'spline_kwargs': {'k': 3, },
                                                                                   'match datasets': {'LC_WASP-76_CHEOPS_110': 'IND-BKG_WASP-76_CHEOPS_110', }
                                                                                   },
                                                           'IND-TF_CHEOPS_inst': {'quantity': 'raw',
                                                                                  'spline_type': 'UnivariateSpline',
                                                                                  'spline_kwargs': {'k': 3, },
                                                                                  'match datasets': {'LC_WASP-76_CHEOPS_110': 'IND-TF_WASP-76_CHEOPS_110', }
                                                                                  },
                                                           }
                                                },
                            'LC_CHEOPS_inst11': {'do': True,
                                                'order': [('bispline', 'XY2'), ('spline', 'IND-BKG_CHEOPS_inst'), ('spline', 'IND-TF_CHEOPS_inst'), ('spline', 'IND-ROLL_CHEOPS_inst'), ],
                                                'bispline': {'XY2': {'IND instument models': ['IND-CX_CHEOPS_inst', 'IND-CY_CHEOPS_inst'],
                                                                     'quantity': 'raw',
                                                                     'spline_type': 'SmoothBivariateSpline',
                                                                     'spline_kwargs': {'kx': 3, 'ky': 3},
                                                                     'match datasets': {'LC_WASP-76_CHEOPS_102': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_102',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_102'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_103': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_103',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_103'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_104': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_104',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_104'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_105': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_105',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_105'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_106': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_106',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_106'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_107': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_107',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_107'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_108': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_108',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_108'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_109': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_109',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_109'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_110': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_110',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_110'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_111': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_111',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_111'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_112': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_112',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_112'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_113': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_113',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_113'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_114': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_114',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_114'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_0': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_0',
                                                                                                                'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_0'
                                                                                                                },
                                                                                        'LC_WASP-76_CHEOPS_1': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_1',
                                                                                                                'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_1'
                                                                                                                },
                                                                                        }
                                                                     },
                                                             },
                                                'spline': {'IND-ROLL_CHEOPS_inst': {'quantity': 'raw',
                                                                                    'spline_type': 'UnivariateSpline',
                                                                                    'spline_kwargs': {'k': 3, },
                                                                                    'match datasets': {'LC_WASP-76_CHEOPS_100': 'IND-ROLL_WASP-76_CHEOPS_100',
                                                                                                       'LC_WASP-76_CHEOPS_101': 'IND-ROLL_WASP-76_CHEOPS_101',
                                                                                                       'LC_WASP-76_CHEOPS_102': 'IND-ROLL_WASP-76_CHEOPS_102',
                                                                                                       'LC_WASP-76_CHEOPS_103': 'IND-ROLL_WASP-76_CHEOPS_103',
                                                                                                       'LC_WASP-76_CHEOPS_104': 'IND-ROLL_WASP-76_CHEOPS_104',
                                                                                                       'LC_WASP-76_CHEOPS_105': 'IND-ROLL_WASP-76_CHEOPS_105',
                                                                                                       'LC_WASP-76_CHEOPS_106': 'IND-ROLL_WASP-76_CHEOPS_106',
                                                                                                       'LC_WASP-76_CHEOPS_107': 'IND-ROLL_WASP-76_CHEOPS_107',
                                                                                                       'LC_WASP-76_CHEOPS_108': 'IND-ROLL_WASP-76_CHEOPS_108',
                                                                                                       'LC_WASP-76_CHEOPS_109': 'IND-ROLL_WASP-76_CHEOPS_109',
                                                                                                       'LC_WASP-76_CHEOPS_110': 'IND-ROLL_WASP-76_CHEOPS_110',
                                                                                                       'LC_WASP-76_CHEOPS_111': 'IND-ROLL_WASP-76_CHEOPS_111',
                                                                                                       'LC_WASP-76_CHEOPS_112': 'IND-ROLL_WASP-76_CHEOPS_112',
                                                                                                       'LC_WASP-76_CHEOPS_113': 'IND-ROLL_WASP-76_CHEOPS_113',
                                                                                                       'LC_WASP-76_CHEOPS_114': 'IND-ROLL_WASP-76_CHEOPS_114',
                                                                                                       'LC_WASP-76_CHEOPS_115': 'IND-ROLL_WASP-76_CHEOPS_115',
                                                                                                       'LC_WASP-76_CHEOPS_116': 'IND-ROLL_WASP-76_CHEOPS_116',
                                                                                                       'LC_WASP-76_CHEOPS_117': 'IND-ROLL_WASP-76_CHEOPS_117',
                                                                                                       'LC_WASP-76_CHEOPS_118': 'IND-ROLL_WASP-76_CHEOPS_118',
                                                                                                       'LC_WASP-76_CHEOPS_119': 'IND-ROLL_WASP-76_CHEOPS_119',
                                                                                                       'LC_WASP-76_CHEOPS_0': 'IND-ROLL_WASP-76_CHEOPS_0',
                                                                                                       'LC_WASP-76_CHEOPS_1': 'IND-ROLL_WASP-76_CHEOPS_1',
                                                                                                       'LC_WASP-76_CHEOPS_2': 'IND-ROLL_WASP-76_CHEOPS_2',
                                                                                                       }
                                                                                    },
                                                           'IND-BKG_CHEOPS_inst': {'quantity': 'raw',
                                                                                   'spline_type': 'UnivariateSpline',
                                                                                   'spline_kwargs': {'k': 3, },
                                                                                   'match datasets': {'LC_WASP-76_CHEOPS_111': 'IND-BKG_WASP-76_CHEOPS_111', }
                                                                                   },
                                                           'IND-TF_CHEOPS_inst': {'quantity': 'raw',
                                                                                  'spline_type': 'UnivariateSpline',
                                                                                  'spline_kwargs': {'k': 3, },
                                                                                  'match datasets': {'LC_WASP-76_CHEOPS_111': 'IND-TF_WASP-76_CHEOPS_111', }
                                                                                  },
                                                           }
                                                },
                            'LC_CHEOPS_inst12': {'do': True,
                                                'order': [('bispline', 'XY2'), ('spline', 'IND-BKG_CHEOPS_inst'), ('spline', 'IND-TF_CHEOPS_inst'), ('spline', 'IND-ROLL_CHEOPS_inst'), ],
                                                'bispline': {'XY2': {'IND instument models': ['IND-CX_CHEOPS_inst', 'IND-CY_CHEOPS_inst'],
                                                                     'quantity': 'raw',
                                                                     'spline_type': 'SmoothBivariateSpline',
                                                                     'spline_kwargs': {'kx': 3, 'ky': 3},
                                                                     'match datasets': {'LC_WASP-76_CHEOPS_102': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_102',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_102'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_103': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_103',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_103'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_104': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_104',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_104'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_105': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_105',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_105'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_106': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_106',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_106'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_107': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_107',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_107'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_108': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_108',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_108'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_109': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_109',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_109'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_110': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_110',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_110'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_111': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_111',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_111'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_112': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_112',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_112'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_113': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_113',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_113'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_114': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_114',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_114'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_0': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_0',
                                                                                                                'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_0'
                                                                                                                },
                                                                                        'LC_WASP-76_CHEOPS_1': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_1',
                                                                                                                'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_1'
                                                                                                                },
                                                                                        }
                                                                     },
                                                             },
                                                'spline': {'IND-ROLL_CHEOPS_inst': {'quantity': 'raw',
                                                                                    'spline_type': 'UnivariateSpline',
                                                                                    'spline_kwargs': {'k': 3, },
                                                                                    'match datasets': {'LC_WASP-76_CHEOPS_100': 'IND-ROLL_WASP-76_CHEOPS_100',
                                                                                                       'LC_WASP-76_CHEOPS_101': 'IND-ROLL_WASP-76_CHEOPS_101',
                                                                                                       'LC_WASP-76_CHEOPS_102': 'IND-ROLL_WASP-76_CHEOPS_102',
                                                                                                       'LC_WASP-76_CHEOPS_103': 'IND-ROLL_WASP-76_CHEOPS_103',
                                                                                                       'LC_WASP-76_CHEOPS_104': 'IND-ROLL_WASP-76_CHEOPS_104',
                                                                                                       'LC_WASP-76_CHEOPS_105': 'IND-ROLL_WASP-76_CHEOPS_105',
                                                                                                       'LC_WASP-76_CHEOPS_106': 'IND-ROLL_WASP-76_CHEOPS_106',
                                                                                                       'LC_WASP-76_CHEOPS_107': 'IND-ROLL_WASP-76_CHEOPS_107',
                                                                                                       'LC_WASP-76_CHEOPS_108': 'IND-ROLL_WASP-76_CHEOPS_108',
                                                                                                       'LC_WASP-76_CHEOPS_109': 'IND-ROLL_WASP-76_CHEOPS_109',
                                                                                                       'LC_WASP-76_CHEOPS_110': 'IND-ROLL_WASP-76_CHEOPS_110',
                                                                                                       'LC_WASP-76_CHEOPS_111': 'IND-ROLL_WASP-76_CHEOPS_111',
                                                                                                       'LC_WASP-76_CHEOPS_112': 'IND-ROLL_WASP-76_CHEOPS_112',
                                                                                                       'LC_WASP-76_CHEOPS_113': 'IND-ROLL_WASP-76_CHEOPS_113',
                                                                                                       'LC_WASP-76_CHEOPS_114': 'IND-ROLL_WASP-76_CHEOPS_114',
                                                                                                       'LC_WASP-76_CHEOPS_115': 'IND-ROLL_WASP-76_CHEOPS_115',
                                                                                                       'LC_WASP-76_CHEOPS_116': 'IND-ROLL_WASP-76_CHEOPS_116',
                                                                                                       'LC_WASP-76_CHEOPS_117': 'IND-ROLL_WASP-76_CHEOPS_117',
                                                                                                       'LC_WASP-76_CHEOPS_118': 'IND-ROLL_WASP-76_CHEOPS_118',
                                                                                                       'LC_WASP-76_CHEOPS_119': 'IND-ROLL_WASP-76_CHEOPS_119',
                                                                                                       'LC_WASP-76_CHEOPS_0': 'IND-ROLL_WASP-76_CHEOPS_0',
                                                                                                       'LC_WASP-76_CHEOPS_1': 'IND-ROLL_WASP-76_CHEOPS_1',
                                                                                                       'LC_WASP-76_CHEOPS_2': 'IND-ROLL_WASP-76_CHEOPS_2',
                                                                                                       }
                                                                                    },
                                                           'IND-BKG_CHEOPS_inst': {'quantity': 'raw',
                                                                                   'spline_type': 'UnivariateSpline',
                                                                                   'spline_kwargs': {'k': 3, },
                                                                                   'match datasets': {'LC_WASP-76_CHEOPS_112': 'IND-BKG_WASP-76_CHEOPS_112', }
                                                                                   },
                                                           'IND-TF_CHEOPS_inst': {'quantity': 'raw',
                                                                                  'spline_type': 'UnivariateSpline',
                                                                                  'spline_kwargs': {'k': 3, },
                                                                                  'match datasets': {'LC_WASP-76_CHEOPS_112': 'IND-TF_WASP-76_CHEOPS_112', }
                                                                                  },
                                                           }
                                                },
                            'LC_CHEOPS_inst13': {'do': True,
                                                'order': [('bispline', 'XY2'), ('spline', 'IND-BKG_CHEOPS_inst'), ('spline', 'IND-TF_CHEOPS_inst'), ('spline', 'IND-ROLL_CHEOPS_inst'), ],
                                                'bispline': {'XY2': {'IND instument models': ['IND-CX_CHEOPS_inst', 'IND-CY_CHEOPS_inst'],
                                                                     'quantity': 'raw',
                                                                     'spline_type': 'SmoothBivariateSpline',
                                                                     'spline_kwargs': {'kx': 3, 'ky': 3},
                                                                     'match datasets': {'LC_WASP-76_CHEOPS_102': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_102',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_102'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_103': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_103',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_103'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_104': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_104',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_104'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_105': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_105',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_105'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_106': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_106',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_106'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_107': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_107',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_107'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_108': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_108',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_108'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_109': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_109',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_109'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_110': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_110',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_110'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_111': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_111',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_111'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_112': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_112',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_112'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_113': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_113',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_113'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_114': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_114',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_114'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_0': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_0',
                                                                                                                'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_0'
                                                                                                                },
                                                                                        'LC_WASP-76_CHEOPS_1': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_1',
                                                                                                                'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_1'
                                                                                                                },
                                                                                        }
                                                                     },
                                                             },
                                                'spline': {'IND-ROLL_CHEOPS_inst': {'quantity': 'raw',
                                                                                    'spline_type': 'UnivariateSpline',
                                                                                    'spline_kwargs': {'k': 3, },
                                                                                    'match datasets': {'LC_WASP-76_CHEOPS_100': 'IND-ROLL_WASP-76_CHEOPS_100',
                                                                                                       'LC_WASP-76_CHEOPS_101': 'IND-ROLL_WASP-76_CHEOPS_101',
                                                                                                       'LC_WASP-76_CHEOPS_102': 'IND-ROLL_WASP-76_CHEOPS_102',
                                                                                                       'LC_WASP-76_CHEOPS_103': 'IND-ROLL_WASP-76_CHEOPS_103',
                                                                                                       'LC_WASP-76_CHEOPS_104': 'IND-ROLL_WASP-76_CHEOPS_104',
                                                                                                       'LC_WASP-76_CHEOPS_105': 'IND-ROLL_WASP-76_CHEOPS_105',
                                                                                                       'LC_WASP-76_CHEOPS_106': 'IND-ROLL_WASP-76_CHEOPS_106',
                                                                                                       'LC_WASP-76_CHEOPS_107': 'IND-ROLL_WASP-76_CHEOPS_107',
                                                                                                       'LC_WASP-76_CHEOPS_108': 'IND-ROLL_WASP-76_CHEOPS_108',
                                                                                                       'LC_WASP-76_CHEOPS_109': 'IND-ROLL_WASP-76_CHEOPS_109',
                                                                                                       'LC_WASP-76_CHEOPS_110': 'IND-ROLL_WASP-76_CHEOPS_110',
                                                                                                       'LC_WASP-76_CHEOPS_111': 'IND-ROLL_WASP-76_CHEOPS_111',
                                                                                                       'LC_WASP-76_CHEOPS_112': 'IND-ROLL_WASP-76_CHEOPS_112',
                                                                                                       'LC_WASP-76_CHEOPS_113': 'IND-ROLL_WASP-76_CHEOPS_113',
                                                                                                       'LC_WASP-76_CHEOPS_114': 'IND-ROLL_WASP-76_CHEOPS_114',
                                                                                                       'LC_WASP-76_CHEOPS_115': 'IND-ROLL_WASP-76_CHEOPS_115',
                                                                                                       'LC_WASP-76_CHEOPS_116': 'IND-ROLL_WASP-76_CHEOPS_116',
                                                                                                       'LC_WASP-76_CHEOPS_117': 'IND-ROLL_WASP-76_CHEOPS_117',
                                                                                                       'LC_WASP-76_CHEOPS_118': 'IND-ROLL_WASP-76_CHEOPS_118',
                                                                                                       'LC_WASP-76_CHEOPS_119': 'IND-ROLL_WASP-76_CHEOPS_119',
                                                                                                       'LC_WASP-76_CHEOPS_0': 'IND-ROLL_WASP-76_CHEOPS_0',
                                                                                                       'LC_WASP-76_CHEOPS_1': 'IND-ROLL_WASP-76_CHEOPS_1',
                                                                                                       'LC_WASP-76_CHEOPS_2': 'IND-ROLL_WASP-76_CHEOPS_2',
                                                                                                       }
                                                                                    },
                                                           'IND-BKG_CHEOPS_inst': {'quantity': 'raw',
                                                                                   'spline_type': 'UnivariateSpline',
                                                                                   'spline_kwargs': {'k': 3, },
                                                                                   'match datasets': {'LC_WASP-76_CHEOPS_113': 'IND-BKG_WASP-76_CHEOPS_113', }
                                                                                   },
                                                           'IND-TF_CHEOPS_inst': {'quantity': 'raw',
                                                                                  'spline_type': 'UnivariateSpline',
                                                                                  'spline_kwargs': {'k': 3, },
                                                                                  'match datasets': {'LC_WASP-76_CHEOPS_113': 'IND-TF_WASP-76_CHEOPS_113', }
                                                                                  },
                                                           }
                                                },
                            'LC_CHEOPS_inst14': {'do': True,
                                                'order': [('bispline', 'XY2'), ('spline', 'IND-BKG_CHEOPS_inst'), ('spline', 'IND-TF_CHEOPS_inst'), ('spline', 'IND-ROLL_CHEOPS_inst'), ],
                                                'bispline': {'XY2': {'IND instument models': ['IND-CX_CHEOPS_inst', 'IND-CY_CHEOPS_inst'],
                                                                     'quantity': 'raw',
                                                                     'spline_type': 'SmoothBivariateSpline',
                                                                     'spline_kwargs': {'kx': 3, 'ky': 3},
                                                                     'match datasets': {'LC_WASP-76_CHEOPS_102': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_102',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_102'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_103': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_103',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_103'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_104': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_104',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_104'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_105': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_105',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_105'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_106': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_106',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_106'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_107': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_107',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_107'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_108': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_108',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_108'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_109': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_109',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_109'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_110': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_110',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_110'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_111': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_111',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_111'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_112': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_112',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_112'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_113': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_113',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_113'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_114': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_114',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_114'
                                                                                                                  },
                                                                                        'LC_WASP-76_CHEOPS_0': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_0',
                                                                                                                'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_0'
                                                                                                                },
                                                                                        'LC_WASP-76_CHEOPS_1': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_1',
                                                                                                                'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_1'
                                                                                                                },
                                                                                        }
                                                                     },
                                                             },
                                                'spline': {'IND-ROLL_CHEOPS_inst': {'quantity': 'raw',
                                                                                    'spline_type': 'UnivariateSpline',
                                                                                    'spline_kwargs': {'k': 3, },
                                                                                    'match datasets': {'LC_WASP-76_CHEOPS_100': 'IND-ROLL_WASP-76_CHEOPS_100',
                                                                                                       'LC_WASP-76_CHEOPS_101': 'IND-ROLL_WASP-76_CHEOPS_101',
                                                                                                       'LC_WASP-76_CHEOPS_102': 'IND-ROLL_WASP-76_CHEOPS_102',
                                                                                                       'LC_WASP-76_CHEOPS_103': 'IND-ROLL_WASP-76_CHEOPS_103',
                                                                                                       'LC_WASP-76_CHEOPS_104': 'IND-ROLL_WASP-76_CHEOPS_104',
                                                                                                       'LC_WASP-76_CHEOPS_105': 'IND-ROLL_WASP-76_CHEOPS_105',
                                                                                                       'LC_WASP-76_CHEOPS_106': 'IND-ROLL_WASP-76_CHEOPS_106',
                                                                                                       'LC_WASP-76_CHEOPS_107': 'IND-ROLL_WASP-76_CHEOPS_107',
                                                                                                       'LC_WASP-76_CHEOPS_108': 'IND-ROLL_WASP-76_CHEOPS_108',
                                                                                                       'LC_WASP-76_CHEOPS_109': 'IND-ROLL_WASP-76_CHEOPS_109',
                                                                                                       'LC_WASP-76_CHEOPS_110': 'IND-ROLL_WASP-76_CHEOPS_110',
                                                                                                       'LC_WASP-76_CHEOPS_111': 'IND-ROLL_WASP-76_CHEOPS_111',
                                                                                                       'LC_WASP-76_CHEOPS_112': 'IND-ROLL_WASP-76_CHEOPS_112',
                                                                                                       'LC_WASP-76_CHEOPS_113': 'IND-ROLL_WASP-76_CHEOPS_113',
                                                                                                       'LC_WASP-76_CHEOPS_114': 'IND-ROLL_WASP-76_CHEOPS_114',
                                                                                                       'LC_WASP-76_CHEOPS_115': 'IND-ROLL_WASP-76_CHEOPS_115',
                                                                                                       'LC_WASP-76_CHEOPS_116': 'IND-ROLL_WASP-76_CHEOPS_116',
                                                                                                       'LC_WASP-76_CHEOPS_117': 'IND-ROLL_WASP-76_CHEOPS_117',
                                                                                                       'LC_WASP-76_CHEOPS_118': 'IND-ROLL_WASP-76_CHEOPS_118',
                                                                                                       'LC_WASP-76_CHEOPS_119': 'IND-ROLL_WASP-76_CHEOPS_119',
                                                                                                       'LC_WASP-76_CHEOPS_0': 'IND-ROLL_WASP-76_CHEOPS_0',
                                                                                                       'LC_WASP-76_CHEOPS_1': 'IND-ROLL_WASP-76_CHEOPS_1',
                                                                                                       'LC_WASP-76_CHEOPS_2': 'IND-ROLL_WASP-76_CHEOPS_2',
                                                                                                       }
                                                                                    },
                                                           'IND-BKG_CHEOPS_inst': {'quantity': 'raw',
                                                                                   'spline_type': 'UnivariateSpline',
                                                                                   'spline_kwargs': {'k': 3, },
                                                                                   'match datasets': {'LC_WASP-76_CHEOPS_114': 'IND-BKG_WASP-76_CHEOPS_114', }
                                                                                   },
                                                           'IND-TF_CHEOPS_inst': {'quantity': 'raw',
                                                                                  'spline_type': 'UnivariateSpline',
                                                                                  'spline_kwargs': {'k': 3, },
                                                                                  'match datasets': {'LC_WASP-76_CHEOPS_114': 'IND-TF_WASP-76_CHEOPS_114', }
                                                                                  },
                                                           }
                                                },
                            'LC_CHEOPS_inst15': {'do': True,
                                                'order': [('bispline', 'XY15'), ('spline', 'IND-BKG_CHEOPS_inst'), ('spline', 'IND-TF_CHEOPS_inst'), ('spline', 'IND-ROLL_CHEOPS_inst'), ],
                                                'bispline': {'XY15': {'IND instument models': ['IND-CX_CHEOPS_inst', 'IND-CY_CHEOPS_inst'],
                                                                      'quantity': 'raw',
                                                                      'spline_type': 'SmoothBivariateSpline',
                                                                      'spline_kwargs': {'kx': 3, 'ky': 3},
                                                                      'match datasets': {'LC_WASP-76_CHEOPS_115': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_115',
                                                                                                                   'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_115'
                                                                                                                   },
                                                                                         'LC_WASP-76_CHEOPS_116': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_116',
                                                                                                                   'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_116'
                                                                                                                   },
                                                                                         'LC_WASP-76_CHEOPS_117': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_117',
                                                                                                                   'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_117'
                                                                                                                   },
                                                                                         'LC_WASP-76_CHEOPS_118': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_118',
                                                                                                                   'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_118'
                                                                                                                   },
                                                                                         'LC_WASP-76_CHEOPS_119': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_119',
                                                                                                                   'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_119'
                                                                                                                   },
                                                                                         'LC_WASP-76_CHEOPS_2': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_2',
                                                                                                                 'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_2'
                                                                                                                 },
                                                                                         }
                                                                      },
                                                             },
                                                'spline': {'IND-ROLL_CHEOPS_inst': {'quantity': 'raw',
                                                                                    'spline_type': 'UnivariateSpline',
                                                                                    'spline_kwargs': {'k': 3, },
                                                                                    'match datasets': {'LC_WASP-76_CHEOPS_100': 'IND-ROLL_WASP-76_CHEOPS_100',
                                                                                                       'LC_WASP-76_CHEOPS_101': 'IND-ROLL_WASP-76_CHEOPS_101',
                                                                                                       'LC_WASP-76_CHEOPS_102': 'IND-ROLL_WASP-76_CHEOPS_102',
                                                                                                       'LC_WASP-76_CHEOPS_103': 'IND-ROLL_WASP-76_CHEOPS_103',
                                                                                                       'LC_WASP-76_CHEOPS_104': 'IND-ROLL_WASP-76_CHEOPS_104',
                                                                                                       'LC_WASP-76_CHEOPS_105': 'IND-ROLL_WASP-76_CHEOPS_105',
                                                                                                       'LC_WASP-76_CHEOPS_106': 'IND-ROLL_WASP-76_CHEOPS_106',
                                                                                                       'LC_WASP-76_CHEOPS_107': 'IND-ROLL_WASP-76_CHEOPS_107',
                                                                                                       'LC_WASP-76_CHEOPS_108': 'IND-ROLL_WASP-76_CHEOPS_108',
                                                                                                       'LC_WASP-76_CHEOPS_109': 'IND-ROLL_WASP-76_CHEOPS_109',
                                                                                                       'LC_WASP-76_CHEOPS_110': 'IND-ROLL_WASP-76_CHEOPS_110',
                                                                                                       'LC_WASP-76_CHEOPS_111': 'IND-ROLL_WASP-76_CHEOPS_111',
                                                                                                       'LC_WASP-76_CHEOPS_112': 'IND-ROLL_WASP-76_CHEOPS_112',
                                                                                                       'LC_WASP-76_CHEOPS_113': 'IND-ROLL_WASP-76_CHEOPS_113',
                                                                                                       'LC_WASP-76_CHEOPS_114': 'IND-ROLL_WASP-76_CHEOPS_114',
                                                                                                       'LC_WASP-76_CHEOPS_115': 'IND-ROLL_WASP-76_CHEOPS_115',
                                                                                                       'LC_WASP-76_CHEOPS_116': 'IND-ROLL_WASP-76_CHEOPS_116',
                                                                                                       'LC_WASP-76_CHEOPS_117': 'IND-ROLL_WASP-76_CHEOPS_117',
                                                                                                       'LC_WASP-76_CHEOPS_118': 'IND-ROLL_WASP-76_CHEOPS_118',
                                                                                                       'LC_WASP-76_CHEOPS_119': 'IND-ROLL_WASP-76_CHEOPS_119',
                                                                                                       'LC_WASP-76_CHEOPS_0': 'IND-ROLL_WASP-76_CHEOPS_0',
                                                                                                       'LC_WASP-76_CHEOPS_1': 'IND-ROLL_WASP-76_CHEOPS_1',
                                                                                                       'LC_WASP-76_CHEOPS_2': 'IND-ROLL_WASP-76_CHEOPS_2',
                                                                                                       }
                                                                                    },
                                                           'IND-BKG_CHEOPS_inst': {'quantity': 'raw',
                                                                                   'spline_type': 'UnivariateSpline',
                                                                                   'spline_kwargs': {'k': 3, },
                                                                                   'match datasets': {'LC_WASP-76_CHEOPS_115': 'IND-BKG_WASP-76_CHEOPS_115', }
                                                                                   },
                                                           'IND-TF_CHEOPS_inst': {'quantity': 'raw',
                                                                                  'spline_type': 'UnivariateSpline',
                                                                                  'spline_kwargs': {'k': 3, },
                                                                                  'match datasets': {'LC_WASP-76_CHEOPS_115': 'IND-TF_WASP-76_CHEOPS_115', }
                                                                                  },
                                                           }
                                                },
                            'LC_CHEOPS_inst16': {'do': True,
                                                'order': [('bispline', 'XY15'), ('spline', 'IND-BKG_CHEOPS_inst'), ('spline', 'IND-TF_CHEOPS_inst'), ('spline', 'IND-ROLL_CHEOPS_inst'), ],
                                                'bispline': {'XY15': {'IND instument models': ['IND-CX_CHEOPS_inst', 'IND-CY_CHEOPS_inst'],
                                                                      'quantity': 'raw',
                                                                      'spline_type': 'SmoothBivariateSpline',
                                                                      'spline_kwargs': {'kx': 3, 'ky': 3},
                                                                      'match datasets': {'LC_WASP-76_CHEOPS_115': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_115',
                                                                                                                   'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_115'
                                                                                                                   },
                                                                                         'LC_WASP-76_CHEOPS_116': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_116',
                                                                                                                   'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_116'
                                                                                                                   },
                                                                                         'LC_WASP-76_CHEOPS_117': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_117',
                                                                                                                   'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_117'
                                                                                                                   },
                                                                                         'LC_WASP-76_CHEOPS_118': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_118',
                                                                                                                   'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_118'
                                                                                                                   },
                                                                                         'LC_WASP-76_CHEOPS_119': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_119',
                                                                                                                   'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_119'
                                                                                                                   },
                                                                                         'LC_WASP-76_CHEOPS_2': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_2',
                                                                                                                 'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_2'
                                                                                                                 },
                                                                                         }
                                                                      },
                                                             },
                                                'spline': {'IND-ROLL_CHEOPS_inst': {'quantity': 'raw',
                                                                                    'spline_type': 'UnivariateSpline',
                                                                                    'spline_kwargs': {'k': 3, },
                                                                                    'match datasets': {'LC_WASP-76_CHEOPS_100': 'IND-ROLL_WASP-76_CHEOPS_100',
                                                                                                       'LC_WASP-76_CHEOPS_101': 'IND-ROLL_WASP-76_CHEOPS_101',
                                                                                                       'LC_WASP-76_CHEOPS_102': 'IND-ROLL_WASP-76_CHEOPS_102',
                                                                                                       'LC_WASP-76_CHEOPS_103': 'IND-ROLL_WASP-76_CHEOPS_103',
                                                                                                       'LC_WASP-76_CHEOPS_104': 'IND-ROLL_WASP-76_CHEOPS_104',
                                                                                                       'LC_WASP-76_CHEOPS_105': 'IND-ROLL_WASP-76_CHEOPS_105',
                                                                                                       'LC_WASP-76_CHEOPS_106': 'IND-ROLL_WASP-76_CHEOPS_106',
                                                                                                       'LC_WASP-76_CHEOPS_107': 'IND-ROLL_WASP-76_CHEOPS_107',
                                                                                                       'LC_WASP-76_CHEOPS_108': 'IND-ROLL_WASP-76_CHEOPS_108',
                                                                                                       'LC_WASP-76_CHEOPS_109': 'IND-ROLL_WASP-76_CHEOPS_109',
                                                                                                       'LC_WASP-76_CHEOPS_110': 'IND-ROLL_WASP-76_CHEOPS_110',
                                                                                                       'LC_WASP-76_CHEOPS_111': 'IND-ROLL_WASP-76_CHEOPS_111',
                                                                                                       'LC_WASP-76_CHEOPS_112': 'IND-ROLL_WASP-76_CHEOPS_112',
                                                                                                       'LC_WASP-76_CHEOPS_113': 'IND-ROLL_WASP-76_CHEOPS_113',
                                                                                                       'LC_WASP-76_CHEOPS_114': 'IND-ROLL_WASP-76_CHEOPS_114',
                                                                                                       'LC_WASP-76_CHEOPS_115': 'IND-ROLL_WASP-76_CHEOPS_115',
                                                                                                       'LC_WASP-76_CHEOPS_116': 'IND-ROLL_WASP-76_CHEOPS_116',
                                                                                                       'LC_WASP-76_CHEOPS_117': 'IND-ROLL_WASP-76_CHEOPS_117',
                                                                                                       'LC_WASP-76_CHEOPS_118': 'IND-ROLL_WASP-76_CHEOPS_118',
                                                                                                       'LC_WASP-76_CHEOPS_119': 'IND-ROLL_WASP-76_CHEOPS_119',
                                                                                                       'LC_WASP-76_CHEOPS_0': 'IND-ROLL_WASP-76_CHEOPS_0',
                                                                                                       'LC_WASP-76_CHEOPS_1': 'IND-ROLL_WASP-76_CHEOPS_1',
                                                                                                       'LC_WASP-76_CHEOPS_2': 'IND-ROLL_WASP-76_CHEOPS_2',
                                                                                                       }
                                                                                    },
                                                           'IND-BKG_CHEOPS_inst': {'quantity': 'raw',
                                                                                   'spline_type': 'UnivariateSpline',
                                                                                   'spline_kwargs': {'k': 3, },
                                                                                   'match datasets': {'LC_WASP-76_CHEOPS_116': 'IND-BKG_WASP-76_CHEOPS_116', }
                                                                                   },
                                                           'IND-TF_CHEOPS_inst': {'quantity': 'raw',
                                                                                  'spline_type': 'UnivariateSpline',
                                                                                  'spline_kwargs': {'k': 3, },
                                                                                  'match datasets': {'LC_WASP-76_CHEOPS_116': 'IND-TF_WASP-76_CHEOPS_116', }
                                                                                  },
                                                           }
                                                },
                            'LC_CHEOPS_inst17': {'do': True,
                                                'order': [('bispline', 'XY15'), ('spline', 'IND-BKG_CHEOPS_inst'), ('spline', 'IND-TF_CHEOPS_inst'), ('spline', 'IND-ROLL_CHEOPS_inst'), ],
                                                'bispline': {'XY15': {'IND instument models': ['IND-CX_CHEOPS_inst', 'IND-CY_CHEOPS_inst'],
                                                                      'quantity': 'raw',
                                                                      'spline_type': 'SmoothBivariateSpline',
                                                                      'spline_kwargs': {'kx': 3, 'ky': 3},
                                                                      'match datasets': {'LC_WASP-76_CHEOPS_115': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_115',
                                                                                                                   'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_115'
                                                                                                                   },
                                                                                         'LC_WASP-76_CHEOPS_116': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_116',
                                                                                                                   'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_116'
                                                                                                                   },
                                                                                         'LC_WASP-76_CHEOPS_117': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_117',
                                                                                                                   'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_117'
                                                                                                                   },
                                                                                         'LC_WASP-76_CHEOPS_118': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_118',
                                                                                                                   'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_118'
                                                                                                                   },
                                                                                         'LC_WASP-76_CHEOPS_119': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_119',
                                                                                                                   'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_119'
                                                                                                                   },
                                                                                         'LC_WASP-76_CHEOPS_2': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_2',
                                                                                                                 'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_2'
                                                                                                                 },
                                                                                         }
                                                                      },
                                                             },
                                                'spline': {'IND-ROLL_CHEOPS_inst': {'quantity': 'raw',
                                                                                    'spline_type': 'UnivariateSpline',
                                                                                    'spline_kwargs': {'k': 3, },
                                                                                    'match datasets': {'LC_WASP-76_CHEOPS_100': 'IND-ROLL_WASP-76_CHEOPS_100',
                                                                                                       'LC_WASP-76_CHEOPS_101': 'IND-ROLL_WASP-76_CHEOPS_101',
                                                                                                       'LC_WASP-76_CHEOPS_102': 'IND-ROLL_WASP-76_CHEOPS_102',
                                                                                                       'LC_WASP-76_CHEOPS_103': 'IND-ROLL_WASP-76_CHEOPS_103',
                                                                                                       'LC_WASP-76_CHEOPS_104': 'IND-ROLL_WASP-76_CHEOPS_104',
                                                                                                       'LC_WASP-76_CHEOPS_105': 'IND-ROLL_WASP-76_CHEOPS_105',
                                                                                                       'LC_WASP-76_CHEOPS_106': 'IND-ROLL_WASP-76_CHEOPS_106',
                                                                                                       'LC_WASP-76_CHEOPS_107': 'IND-ROLL_WASP-76_CHEOPS_107',
                                                                                                       'LC_WASP-76_CHEOPS_108': 'IND-ROLL_WASP-76_CHEOPS_108',
                                                                                                       'LC_WASP-76_CHEOPS_109': 'IND-ROLL_WASP-76_CHEOPS_109',
                                                                                                       'LC_WASP-76_CHEOPS_110': 'IND-ROLL_WASP-76_CHEOPS_110',
                                                                                                       'LC_WASP-76_CHEOPS_111': 'IND-ROLL_WASP-76_CHEOPS_111',
                                                                                                       'LC_WASP-76_CHEOPS_112': 'IND-ROLL_WASP-76_CHEOPS_112',
                                                                                                       'LC_WASP-76_CHEOPS_113': 'IND-ROLL_WASP-76_CHEOPS_113',
                                                                                                       'LC_WASP-76_CHEOPS_114': 'IND-ROLL_WASP-76_CHEOPS_114',
                                                                                                       'LC_WASP-76_CHEOPS_115': 'IND-ROLL_WASP-76_CHEOPS_115',
                                                                                                       'LC_WASP-76_CHEOPS_116': 'IND-ROLL_WASP-76_CHEOPS_116',
                                                                                                       'LC_WASP-76_CHEOPS_117': 'IND-ROLL_WASP-76_CHEOPS_117',
                                                                                                       'LC_WASP-76_CHEOPS_118': 'IND-ROLL_WASP-76_CHEOPS_118',
                                                                                                       'LC_WASP-76_CHEOPS_119': 'IND-ROLL_WASP-76_CHEOPS_119',
                                                                                                       'LC_WASP-76_CHEOPS_0': 'IND-ROLL_WASP-76_CHEOPS_0',
                                                                                                       'LC_WASP-76_CHEOPS_1': 'IND-ROLL_WASP-76_CHEOPS_1',
                                                                                                       'LC_WASP-76_CHEOPS_2': 'IND-ROLL_WASP-76_CHEOPS_2',
                                                                                                       }
                                                                                    },
                                                           'IND-BKG_CHEOPS_inst': {'quantity': 'raw',
                                                                                   'spline_type': 'UnivariateSpline',
                                                                                   'spline_kwargs': {'k': 3, },
                                                                                   'match datasets': {'LC_WASP-76_CHEOPS_117': 'IND-BKG_WASP-76_CHEOPS_117', }
                                                                                   },
                                                           'IND-TF_CHEOPS_inst': {'quantity': 'raw',
                                                                                  'spline_type': 'UnivariateSpline',
                                                                                  'spline_kwargs': {'k': 3, },
                                                                                  'match datasets': {'LC_WASP-76_CHEOPS_117': 'IND-TF_WASP-76_CHEOPS_117', }
                                                                                  },
                                                           }
                                                },
                            'LC_CHEOPS_inst18': {'do': True,
                                                'order': [('bispline', 'XY15'), ('spline', 'IND-BKG_CHEOPS_inst'), ('spline', 'IND-TF_CHEOPS_inst'), ('spline', 'IND-ROLL_CHEOPS_inst'), ],
                                                'bispline': {'XY15': {'IND instument models': ['IND-CX_CHEOPS_inst', 'IND-CY_CHEOPS_inst'],
                                                                      'quantity': 'raw',
                                                                      'spline_type': 'SmoothBivariateSpline',
                                                                      'spline_kwargs': {'kx': 3, 'ky': 3},
                                                                      'match datasets': {'LC_WASP-76_CHEOPS_115': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_115',
                                                                                                                   'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_115'
                                                                                                                   },
                                                                                         'LC_WASP-76_CHEOPS_116': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_116',
                                                                                                                   'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_116'
                                                                                                                   },
                                                                                         'LC_WASP-76_CHEOPS_117': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_117',
                                                                                                                   'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_117'
                                                                                                                   },
                                                                                         'LC_WASP-76_CHEOPS_118': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_118',
                                                                                                                   'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_118'
                                                                                                                   },
                                                                                         'LC_WASP-76_CHEOPS_119': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_119',
                                                                                                                   'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_119'
                                                                                                                   },
                                                                                         'LC_WASP-76_CHEOPS_2': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_2',
                                                                                                                 'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_2'
                                                                                                                 },
                                                                                         }
                                                                      },
                                                             },
                                                'spline': {'IND-ROLL_CHEOPS_inst': {'quantity': 'raw',
                                                                                    'spline_type': 'UnivariateSpline',
                                                                                    'spline_kwargs': {'k': 3, },
                                                                                    'match datasets': {'LC_WASP-76_CHEOPS_100': 'IND-ROLL_WASP-76_CHEOPS_100',
                                                                                                       'LC_WASP-76_CHEOPS_101': 'IND-ROLL_WASP-76_CHEOPS_101',
                                                                                                       'LC_WASP-76_CHEOPS_102': 'IND-ROLL_WASP-76_CHEOPS_102',
                                                                                                       'LC_WASP-76_CHEOPS_103': 'IND-ROLL_WASP-76_CHEOPS_103',
                                                                                                       'LC_WASP-76_CHEOPS_104': 'IND-ROLL_WASP-76_CHEOPS_104',
                                                                                                       'LC_WASP-76_CHEOPS_105': 'IND-ROLL_WASP-76_CHEOPS_105',
                                                                                                       'LC_WASP-76_CHEOPS_106': 'IND-ROLL_WASP-76_CHEOPS_106',
                                                                                                       'LC_WASP-76_CHEOPS_107': 'IND-ROLL_WASP-76_CHEOPS_107',
                                                                                                       'LC_WASP-76_CHEOPS_108': 'IND-ROLL_WASP-76_CHEOPS_108',
                                                                                                       'LC_WASP-76_CHEOPS_109': 'IND-ROLL_WASP-76_CHEOPS_109',
                                                                                                       'LC_WASP-76_CHEOPS_110': 'IND-ROLL_WASP-76_CHEOPS_110',
                                                                                                       'LC_WASP-76_CHEOPS_111': 'IND-ROLL_WASP-76_CHEOPS_111',
                                                                                                       'LC_WASP-76_CHEOPS_112': 'IND-ROLL_WASP-76_CHEOPS_112',
                                                                                                       'LC_WASP-76_CHEOPS_113': 'IND-ROLL_WASP-76_CHEOPS_113',
                                                                                                       'LC_WASP-76_CHEOPS_114': 'IND-ROLL_WASP-76_CHEOPS_114',
                                                                                                       'LC_WASP-76_CHEOPS_115': 'IND-ROLL_WASP-76_CHEOPS_115',
                                                                                                       'LC_WASP-76_CHEOPS_116': 'IND-ROLL_WASP-76_CHEOPS_116',
                                                                                                       'LC_WASP-76_CHEOPS_117': 'IND-ROLL_WASP-76_CHEOPS_117',
                                                                                                       'LC_WASP-76_CHEOPS_118': 'IND-ROLL_WASP-76_CHEOPS_118',
                                                                                                       'LC_WASP-76_CHEOPS_119': 'IND-ROLL_WASP-76_CHEOPS_119',
                                                                                                       'LC_WASP-76_CHEOPS_0': 'IND-ROLL_WASP-76_CHEOPS_0',
                                                                                                       'LC_WASP-76_CHEOPS_1': 'IND-ROLL_WASP-76_CHEOPS_1',
                                                                                                       'LC_WASP-76_CHEOPS_2': 'IND-ROLL_WASP-76_CHEOPS_2',
                                                                                                       }
                                                                                    },
                                                           'IND-BKG_CHEOPS_inst': {'quantity': 'raw',
                                                                                   'spline_type': 'UnivariateSpline',
                                                                                   'spline_kwargs': {'k': 3, },
                                                                                   'match datasets': {'LC_WASP-76_CHEOPS_118': 'IND-BKG_WASP-76_CHEOPS_118', }
                                                                                   },
                                                           'IND-TF_CHEOPS_inst': {'quantity': 'raw',
                                                                                  'spline_type': 'UnivariateSpline',
                                                                                  'spline_kwargs': {'k': 3, },
                                                                                  'match datasets': {'LC_WASP-76_CHEOPS_118': 'IND-TF_WASP-76_CHEOPS_118', }
                                                                                  },
                                                           }
                                                },
                            'LC_CHEOPS_inst19': {'do': True,
                                                'order': [('bispline', 'XY15'), ('spline', 'IND-BKG_CHEOPS_inst'), ('spline', 'IND-TF_CHEOPS_inst'), ('spline', 'IND-ROLL_CHEOPS_inst'), ],
                                                'bispline': {'XY15': {'IND instument models': ['IND-CX_CHEOPS_inst', 'IND-CY_CHEOPS_inst'],
                                                                      'quantity': 'raw',
                                                                      'spline_type': 'SmoothBivariateSpline',
                                                                      'spline_kwargs': {'kx': 3, 'ky': 3},
                                                                      'match datasets': {'LC_WASP-76_CHEOPS_115': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_115',
                                                                                                                   'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_115'
                                                                                                                   },
                                                                                         'LC_WASP-76_CHEOPS_116': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_116',
                                                                                                                   'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_116'
                                                                                                                   },
                                                                                         'LC_WASP-76_CHEOPS_117': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_117',
                                                                                                                   'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_117'
                                                                                                                   },
                                                                                         'LC_WASP-76_CHEOPS_118': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_118',
                                                                                                                   'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_118'
                                                                                                                   },
                                                                                         'LC_WASP-76_CHEOPS_119': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_119',
                                                                                                                   'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_119'
                                                                                                                   },
                                                                                         'LC_WASP-76_CHEOPS_2': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_2',
                                                                                                                 'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_2'
                                                                                                                 },
                                                                                         }
                                                                      },
                                                             },
                                                'spline': {'IND-ROLL_CHEOPS_inst': {'quantity': 'raw',
                                                                                    'spline_type': 'UnivariateSpline',
                                                                                    'spline_kwargs': {'k': 3, },
                                                                                    'match datasets': {'LC_WASP-76_CHEOPS_100': 'IND-ROLL_WASP-76_CHEOPS_100',
                                                                                                       'LC_WASP-76_CHEOPS_101': 'IND-ROLL_WASP-76_CHEOPS_101',
                                                                                                       'LC_WASP-76_CHEOPS_102': 'IND-ROLL_WASP-76_CHEOPS_102',
                                                                                                       'LC_WASP-76_CHEOPS_103': 'IND-ROLL_WASP-76_CHEOPS_103',
                                                                                                       'LC_WASP-76_CHEOPS_104': 'IND-ROLL_WASP-76_CHEOPS_104',
                                                                                                       'LC_WASP-76_CHEOPS_105': 'IND-ROLL_WASP-76_CHEOPS_105',
                                                                                                       'LC_WASP-76_CHEOPS_106': 'IND-ROLL_WASP-76_CHEOPS_106',
                                                                                                       'LC_WASP-76_CHEOPS_107': 'IND-ROLL_WASP-76_CHEOPS_107',
                                                                                                       'LC_WASP-76_CHEOPS_108': 'IND-ROLL_WASP-76_CHEOPS_108',
                                                                                                       'LC_WASP-76_CHEOPS_109': 'IND-ROLL_WASP-76_CHEOPS_109',
                                                                                                       'LC_WASP-76_CHEOPS_110': 'IND-ROLL_WASP-76_CHEOPS_110',
                                                                                                       'LC_WASP-76_CHEOPS_111': 'IND-ROLL_WASP-76_CHEOPS_111',
                                                                                                       'LC_WASP-76_CHEOPS_112': 'IND-ROLL_WASP-76_CHEOPS_112',
                                                                                                       'LC_WASP-76_CHEOPS_113': 'IND-ROLL_WASP-76_CHEOPS_113',
                                                                                                       'LC_WASP-76_CHEOPS_114': 'IND-ROLL_WASP-76_CHEOPS_114',
                                                                                                       'LC_WASP-76_CHEOPS_115': 'IND-ROLL_WASP-76_CHEOPS_115',
                                                                                                       'LC_WASP-76_CHEOPS_116': 'IND-ROLL_WASP-76_CHEOPS_116',
                                                                                                       'LC_WASP-76_CHEOPS_117': 'IND-ROLL_WASP-76_CHEOPS_117',
                                                                                                       'LC_WASP-76_CHEOPS_118': 'IND-ROLL_WASP-76_CHEOPS_118',
                                                                                                       'LC_WASP-76_CHEOPS_119': 'IND-ROLL_WASP-76_CHEOPS_119',
                                                                                                       'LC_WASP-76_CHEOPS_0': 'IND-ROLL_WASP-76_CHEOPS_0',
                                                                                                       'LC_WASP-76_CHEOPS_1': 'IND-ROLL_WASP-76_CHEOPS_1',
                                                                                                       'LC_WASP-76_CHEOPS_2': 'IND-ROLL_WASP-76_CHEOPS_2',
                                                                                                       }
                                                                                    },
                                                           'IND-BKG_CHEOPS_inst': {'quantity': 'raw',
                                                                                   'spline_type': 'UnivariateSpline',
                                                                                   'spline_kwargs': {'k': 3, },
                                                                                   'match datasets': {'LC_WASP-76_CHEOPS_119': 'IND-BKG_WASP-76_CHEOPS_119', }
                                                                                   },
                                                           'IND-TF_CHEOPS_inst': {'quantity': 'raw',
                                                                                  'spline_type': 'UnivariateSpline',
                                                                                  'spline_kwargs': {'k': 3, },
                                                                                  'match datasets': {'LC_WASP-76_CHEOPS_119': 'IND-TF_WASP-76_CHEOPS_119', }
                                                                                  },
                                                           }
                                                },
                            'LC_CHEOPS_instPC0': {'do': True,
                                                  'order': [('bispline', 'XY2'), ('spline', 'IND-BKG_CHEOPS_inst'), ('spline', 'IND-TF_CHEOPS_inst'), ('spline', 'IND-ROLL_CHEOPS_inst'), ],
                                                  'bispline': {'XY2': {'IND instument models': ['IND-CX_CHEOPS_inst', 'IND-CY_CHEOPS_inst'],
                                                                       'quantity': 'raw',
                                                                       'spline_type': 'SmoothBivariateSpline',
                                                                       'spline_kwargs': {'kx': 3, 'ky': 3},
                                                                       'match datasets': {'LC_WASP-76_CHEOPS_102': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_102',
                                                                                                                    'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_102'
                                                                                                                    },
                                                                                          'LC_WASP-76_CHEOPS_103': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_103',
                                                                                                                    'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_103'
                                                                                                                    },
                                                                                          'LC_WASP-76_CHEOPS_104': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_104',
                                                                                                                    'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_104'
                                                                                                                    },
                                                                                          'LC_WASP-76_CHEOPS_105': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_105',
                                                                                                                    'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_105'
                                                                                                                    },
                                                                                          'LC_WASP-76_CHEOPS_106': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_106',
                                                                                                                    'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_106'
                                                                                                                    },
                                                                                          'LC_WASP-76_CHEOPS_107': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_107',
                                                                                                                    'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_107'
                                                                                                                    },
                                                                                          'LC_WASP-76_CHEOPS_108': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_108',
                                                                                                                    'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_108'
                                                                                                                    },
                                                                                          'LC_WASP-76_CHEOPS_109': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_109',
                                                                                                                    'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_109'
                                                                                                                    },
                                                                                          'LC_WASP-76_CHEOPS_110': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_110',
                                                                                                                    'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_110'
                                                                                                                    },
                                                                                          'LC_WASP-76_CHEOPS_111': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_111',
                                                                                                                    'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_111'
                                                                                                                    },
                                                                                          'LC_WASP-76_CHEOPS_112': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_112',
                                                                                                                    'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_112'
                                                                                                                    },
                                                                                          'LC_WASP-76_CHEOPS_113': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_113',
                                                                                                                    'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_113'
                                                                                                                    },
                                                                                          'LC_WASP-76_CHEOPS_114': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_114',
                                                                                                                    'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_114'
                                                                                                                    },
                                                                                          'LC_WASP-76_CHEOPS_0': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_0',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_0'
                                                                                                                  },
                                                                                          'LC_WASP-76_CHEOPS_1': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_1',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_1'
                                                                                                                  },
                                                                                          }
                                                                       },
                                                               },
                                                  'spline': {'IND-ROLL_CHEOPS_inst': {'quantity': 'raw',
                                                                                      'spline_type': 'UnivariateSpline',
                                                                                      'spline_kwargs': {'k': 3, },
                                                                                      'match datasets': {'LC_WASP-76_CHEOPS_100': 'IND-ROLL_WASP-76_CHEOPS_100',
                                                                                                         'LC_WASP-76_CHEOPS_101': 'IND-ROLL_WASP-76_CHEOPS_101',
                                                                                                         'LC_WASP-76_CHEOPS_102': 'IND-ROLL_WASP-76_CHEOPS_102',
                                                                                                         'LC_WASP-76_CHEOPS_103': 'IND-ROLL_WASP-76_CHEOPS_103',
                                                                                                         'LC_WASP-76_CHEOPS_104': 'IND-ROLL_WASP-76_CHEOPS_104',
                                                                                                         'LC_WASP-76_CHEOPS_105': 'IND-ROLL_WASP-76_CHEOPS_105',
                                                                                                         'LC_WASP-76_CHEOPS_106': 'IND-ROLL_WASP-76_CHEOPS_106',
                                                                                                         'LC_WASP-76_CHEOPS_107': 'IND-ROLL_WASP-76_CHEOPS_107',
                                                                                                         'LC_WASP-76_CHEOPS_108': 'IND-ROLL_WASP-76_CHEOPS_108',
                                                                                                         'LC_WASP-76_CHEOPS_109': 'IND-ROLL_WASP-76_CHEOPS_109',
                                                                                                         'LC_WASP-76_CHEOPS_110': 'IND-ROLL_WASP-76_CHEOPS_110',
                                                                                                         'LC_WASP-76_CHEOPS_111': 'IND-ROLL_WASP-76_CHEOPS_111',
                                                                                                         'LC_WASP-76_CHEOPS_112': 'IND-ROLL_WASP-76_CHEOPS_112',
                                                                                                         'LC_WASP-76_CHEOPS_113': 'IND-ROLL_WASP-76_CHEOPS_113',
                                                                                                         'LC_WASP-76_CHEOPS_114': 'IND-ROLL_WASP-76_CHEOPS_114',
                                                                                                         'LC_WASP-76_CHEOPS_115': 'IND-ROLL_WASP-76_CHEOPS_115',
                                                                                                         'LC_WASP-76_CHEOPS_116': 'IND-ROLL_WASP-76_CHEOPS_116',
                                                                                                         'LC_WASP-76_CHEOPS_117': 'IND-ROLL_WASP-76_CHEOPS_117',
                                                                                                         'LC_WASP-76_CHEOPS_118': 'IND-ROLL_WASP-76_CHEOPS_118',
                                                                                                         'LC_WASP-76_CHEOPS_119': 'IND-ROLL_WASP-76_CHEOPS_119',
                                                                                                         'LC_WASP-76_CHEOPS_0': 'IND-ROLL_WASP-76_CHEOPS_0',
                                                                                                         'LC_WASP-76_CHEOPS_1': 'IND-ROLL_WASP-76_CHEOPS_1',
                                                                                                         'LC_WASP-76_CHEOPS_2': 'IND-ROLL_WASP-76_CHEOPS_2',
                                                                                                         }
                                                                                      },
                                                             'IND-BKG_CHEOPS_inst': {'quantity': 'raw',
                                                                                     'spline_type': 'UnivariateSpline',
                                                                                     'spline_kwargs': {'k': 3, },
                                                                                     'match datasets': {'LC_WASP-76_CHEOPS_0': 'IND-BKG_WASP-76_CHEOPS_0', }
                                                                                     },
                                                             'IND-TF_CHEOPS_inst': {'quantity': 'raw',
                                                                                    'spline_type': 'UnivariateSpline',
                                                                                    'spline_kwargs': {'k': 3, },
                                                                                    'match datasets': {'LC_WASP-76_CHEOPS_0': 'IND-TF_WASP-76_CHEOPS_0', }
                                                                                    },
                                                             }
                                                  },
                            'LC_CHEOPS_instPC1': {'do': True,
                                                  'order': [('bispline', 'XY2'), ('spline', 'IND-BKG_CHEOPS_inst'), ('spline', 'IND-TF_CHEOPS_inst'), ('spline', 'IND-ROLL_CHEOPS_inst'), ],
                                                  'bispline': {'XY2': {'IND instument models': ['IND-CX_CHEOPS_inst', 'IND-CY_CHEOPS_inst'],
                                                                       'quantity': 'raw',
                                                                       'spline_type': 'SmoothBivariateSpline',
                                                                       'spline_kwargs': {'kx': 3, 'ky': 3},
                                                                       'match datasets': {'LC_WASP-76_CHEOPS_102': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_102',
                                                                                                                    'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_102'
                                                                                                                    },
                                                                                          'LC_WASP-76_CHEOPS_103': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_103',
                                                                                                                    'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_103'
                                                                                                                    },
                                                                                          'LC_WASP-76_CHEOPS_104': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_104',
                                                                                                                    'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_104'
                                                                                                                    },
                                                                                          'LC_WASP-76_CHEOPS_105': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_105',
                                                                                                                    'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_105'
                                                                                                                    },
                                                                                          'LC_WASP-76_CHEOPS_106': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_106',
                                                                                                                    'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_106'
                                                                                                                    },
                                                                                          'LC_WASP-76_CHEOPS_107': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_107',
                                                                                                                    'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_107'
                                                                                                                    },
                                                                                          'LC_WASP-76_CHEOPS_108': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_108',
                                                                                                                    'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_108'
                                                                                                                    },
                                                                                          'LC_WASP-76_CHEOPS_109': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_109',
                                                                                                                    'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_109'
                                                                                                                    },
                                                                                          'LC_WASP-76_CHEOPS_110': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_110',
                                                                                                                    'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_110'
                                                                                                                    },
                                                                                          'LC_WASP-76_CHEOPS_111': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_111',
                                                                                                                    'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_111'
                                                                                                                    },
                                                                                          'LC_WASP-76_CHEOPS_112': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_112',
                                                                                                                    'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_112'
                                                                                                                    },
                                                                                          'LC_WASP-76_CHEOPS_113': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_113',
                                                                                                                    'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_113'
                                                                                                                    },
                                                                                          'LC_WASP-76_CHEOPS_114': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_114',
                                                                                                                    'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_114'
                                                                                                                    },
                                                                                          'LC_WASP-76_CHEOPS_0': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_0',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_0'
                                                                                                                  },
                                                                                          'LC_WASP-76_CHEOPS_1': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_1',
                                                                                                                  'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_1'
                                                                                                                  },
                                                                                          }
                                                                       },
                                                               },
                                                  'spline': {'IND-ROLL_CHEOPS_inst': {'quantity': 'raw',
                                                                                      'spline_type': 'UnivariateSpline',
                                                                                      'spline_kwargs': {'k': 3, },
                                                                                      'match datasets': {'LC_WASP-76_CHEOPS_100': 'IND-ROLL_WASP-76_CHEOPS_100',
                                                                                                         'LC_WASP-76_CHEOPS_101': 'IND-ROLL_WASP-76_CHEOPS_101',
                                                                                                         'LC_WASP-76_CHEOPS_102': 'IND-ROLL_WASP-76_CHEOPS_102',
                                                                                                         'LC_WASP-76_CHEOPS_103': 'IND-ROLL_WASP-76_CHEOPS_103',
                                                                                                         'LC_WASP-76_CHEOPS_104': 'IND-ROLL_WASP-76_CHEOPS_104',
                                                                                                         'LC_WASP-76_CHEOPS_105': 'IND-ROLL_WASP-76_CHEOPS_105',
                                                                                                         'LC_WASP-76_CHEOPS_106': 'IND-ROLL_WASP-76_CHEOPS_106',
                                                                                                         'LC_WASP-76_CHEOPS_107': 'IND-ROLL_WASP-76_CHEOPS_107',
                                                                                                         'LC_WASP-76_CHEOPS_108': 'IND-ROLL_WASP-76_CHEOPS_108',
                                                                                                         'LC_WASP-76_CHEOPS_109': 'IND-ROLL_WASP-76_CHEOPS_109',
                                                                                                         'LC_WASP-76_CHEOPS_110': 'IND-ROLL_WASP-76_CHEOPS_110',
                                                                                                         'LC_WASP-76_CHEOPS_111': 'IND-ROLL_WASP-76_CHEOPS_111',
                                                                                                         'LC_WASP-76_CHEOPS_112': 'IND-ROLL_WASP-76_CHEOPS_112',
                                                                                                         'LC_WASP-76_CHEOPS_113': 'IND-ROLL_WASP-76_CHEOPS_113',
                                                                                                         'LC_WASP-76_CHEOPS_114': 'IND-ROLL_WASP-76_CHEOPS_114',
                                                                                                         'LC_WASP-76_CHEOPS_115': 'IND-ROLL_WASP-76_CHEOPS_115',
                                                                                                         'LC_WASP-76_CHEOPS_116': 'IND-ROLL_WASP-76_CHEOPS_116',
                                                                                                         'LC_WASP-76_CHEOPS_117': 'IND-ROLL_WASP-76_CHEOPS_117',
                                                                                                         'LC_WASP-76_CHEOPS_118': 'IND-ROLL_WASP-76_CHEOPS_118',
                                                                                                         'LC_WASP-76_CHEOPS_119': 'IND-ROLL_WASP-76_CHEOPS_119',
                                                                                                         'LC_WASP-76_CHEOPS_0': 'IND-ROLL_WASP-76_CHEOPS_0',
                                                                                                         'LC_WASP-76_CHEOPS_1': 'IND-ROLL_WASP-76_CHEOPS_1',
                                                                                                         'LC_WASP-76_CHEOPS_2': 'IND-ROLL_WASP-76_CHEOPS_2',
                                                                                                         }
                                                                                      },
                                                             'IND-BKG_CHEOPS_inst': {'quantity': 'raw',
                                                                                     'spline_type': 'UnivariateSpline',
                                                                                     'spline_kwargs': {'k': 3, },
                                                                                     'match datasets': {'LC_WASP-76_CHEOPS_1': 'IND-BKG_WASP-76_CHEOPS_1', }
                                                                                     },
                                                             'IND-TF_CHEOPS_inst': {'quantity': 'raw',
                                                                                    'spline_type': 'UnivariateSpline',
                                                                                    'spline_kwargs': {'k': 3, },
                                                                                    'match datasets': {'LC_WASP-76_CHEOPS_1': 'IND-TF_WASP-76_CHEOPS_1', }
                                                                                    },
                                                             }
                                                  },
                            'LC_CHEOPS_instPC2': {'do': True,
                                                  'order': [('bispline', 'XY15'), ('spline', 'IND-BKG_CHEOPS_inst'), ('spline', 'IND-TF_CHEOPS_inst'), ('spline', 'IND-ROLL_CHEOPS_inst'), ],
                                                  'bispline': {'XY15': {'IND instument models': ['IND-CX_CHEOPS_inst', 'IND-CY_CHEOPS_inst'],
                                                                        'quantity': 'raw',
                                                                        'spline_type': 'SmoothBivariateSpline',
                                                                        'spline_kwargs': {'kx': 3, 'ky': 3},
                                                                        'match datasets': {'LC_WASP-76_CHEOPS_115': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_115',
                                                                                                                     'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_115'
                                                                                                                     },
                                                                                           'LC_WASP-76_CHEOPS_116': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_116',
                                                                                                                     'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_116'
                                                                                                                     },
                                                                                           'LC_WASP-76_CHEOPS_117': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_117',
                                                                                                                     'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_117'
                                                                                                                     },
                                                                                           'LC_WASP-76_CHEOPS_118': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_118',
                                                                                                                     'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_118'
                                                                                                                     },
                                                                                           'LC_WASP-76_CHEOPS_119': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_119',
                                                                                                                     'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_119'
                                                                                                                     },
                                                                                           'LC_WASP-76_CHEOPS_2': {'IND-CX_CHEOPS_inst': 'IND-CX_WASP-76_CHEOPS_2',
                                                                                                                   'IND-CY_CHEOPS_inst': 'IND-CY_WASP-76_CHEOPS_2'
                                                                                                                   },
                                                                                           }
                                                                        },
                                                               },
                                                  'spline': {'IND-ROLL_CHEOPS_inst': {'quantity': 'raw',
                                                                                      'spline_type': 'UnivariateSpline',
                                                                                      'spline_kwargs': {'k': 3, },
                                                                                      'match datasets': {'LC_WASP-76_CHEOPS_100': 'IND-ROLL_WASP-76_CHEOPS_100',
                                                                                                         'LC_WASP-76_CHEOPS_101': 'IND-ROLL_WASP-76_CHEOPS_101',
                                                                                                         'LC_WASP-76_CHEOPS_102': 'IND-ROLL_WASP-76_CHEOPS_102',
                                                                                                         'LC_WASP-76_CHEOPS_103': 'IND-ROLL_WASP-76_CHEOPS_103',
                                                                                                         'LC_WASP-76_CHEOPS_104': 'IND-ROLL_WASP-76_CHEOPS_104',
                                                                                                         'LC_WASP-76_CHEOPS_105': 'IND-ROLL_WASP-76_CHEOPS_105',
                                                                                                         'LC_WASP-76_CHEOPS_106': 'IND-ROLL_WASP-76_CHEOPS_106',
                                                                                                         'LC_WASP-76_CHEOPS_107': 'IND-ROLL_WASP-76_CHEOPS_107',
                                                                                                         'LC_WASP-76_CHEOPS_108': 'IND-ROLL_WASP-76_CHEOPS_108',
                                                                                                         'LC_WASP-76_CHEOPS_109': 'IND-ROLL_WASP-76_CHEOPS_109',
                                                                                                         'LC_WASP-76_CHEOPS_110': 'IND-ROLL_WASP-76_CHEOPS_110',
                                                                                                         'LC_WASP-76_CHEOPS_111': 'IND-ROLL_WASP-76_CHEOPS_111',
                                                                                                         'LC_WASP-76_CHEOPS_112': 'IND-ROLL_WASP-76_CHEOPS_112',
                                                                                                         'LC_WASP-76_CHEOPS_113': 'IND-ROLL_WASP-76_CHEOPS_113',
                                                                                                         'LC_WASP-76_CHEOPS_114': 'IND-ROLL_WASP-76_CHEOPS_114',
                                                                                                         'LC_WASP-76_CHEOPS_115': 'IND-ROLL_WASP-76_CHEOPS_115',
                                                                                                         'LC_WASP-76_CHEOPS_116': 'IND-ROLL_WASP-76_CHEOPS_116',
                                                                                                         'LC_WASP-76_CHEOPS_117': 'IND-ROLL_WASP-76_CHEOPS_117',
                                                                                                         'LC_WASP-76_CHEOPS_118': 'IND-ROLL_WASP-76_CHEOPS_118',
                                                                                                         'LC_WASP-76_CHEOPS_119': 'IND-ROLL_WASP-76_CHEOPS_119',
                                                                                                         'LC_WASP-76_CHEOPS_0': 'IND-ROLL_WASP-76_CHEOPS_0',
                                                                                                         'LC_WASP-76_CHEOPS_1': 'IND-ROLL_WASP-76_CHEOPS_1',
                                                                                                         'LC_WASP-76_CHEOPS_2': 'IND-ROLL_WASP-76_CHEOPS_2',
                                                                                                         }
                                                                                      },
                                                             'IND-BKG_CHEOPS_inst': {'quantity': 'raw',
                                                                                     'spline_type': 'UnivariateSpline',
                                                                                     'spline_kwargs': {'k': 3, },
                                                                                     'match datasets': {'LC_WASP-76_CHEOPS_2': 'IND-BKG_WASP-76_CHEOPS_2', }
                                                                                     },
                                                             'IND-TF_CHEOPS_inst': {'quantity': 'raw',
                                                                                    'spline_type': 'UnivariateSpline',
                                                                                    'spline_kwargs': {'k': 3, },
                                                                                    'match datasets': {'LC_WASP-76_CHEOPS_2': 'IND-TF_WASP-76_CHEOPS_2', }
                                                                                    },
                                                             }
                                                  },
                            }
