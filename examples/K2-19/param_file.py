#!/usr/bin/python
# -*- coding:  utf-8 -*-
# Parametrisation file of K2-19
import numpy as np

# Parameters
# instruments
# instruments RV
RV = {'SOPHIE': {'def': {'DeltaRV': {'duplicate': None,
                                     'free': False,
                                     'value': 0.0,  # unit: [amplitude of the RV data]
                                     'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                                               'joint_prior_ref': None
                                               }
                                     },
                         'jitter': {'duplicate': None,
                                    'free': False,
                                    'value': 0.0,  # unit: None
                                    'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                                              'joint_prior_ref': None
                                              }
                                    },
                         },
                 # By default all the datasets of an instrument are associated to def.
                 # If you want to model some datasets with another instrument model copy paste it,
                 # give it a new name and file the Dataset dict.
                 'Dataset': {0: 'def', },

                 'RVref': 'def',

                 },
      'HARPS': {'0': {'DeltaRV': {'duplicate': None,
                                  'free': True,
                                  'value': None,  # unit: [amplitude of the RV data]
                                  'prior': {'category': 'normal', 'args': {'mu': 0.10, 'sigma': 0.01},
                                            'joint_prior_ref': None
                                            }
                                  },
                      'jitter': {'duplicate': None,
                                 'free': False,
                                 'value': 0.0,  # unit: None
                                 'prior': {'category': 'normal', 'args': {'mu': 0.0, 'sigma': 0.05},
                                           'joint_prior_ref': None
                                           }
                                 },
                      },
                '1': {'DeltaRV': {'duplicate': None,
                                  'free': True,
                                  'value': None,  # unit: [amplitude of the RV data]
                                  'prior': {'category': 'normal', 'args': {'mu': -7.32, 'sigma': 0.01},
                                            'joint_prior_ref': None
                                            }
                                  },
                      'jitter': {'duplicate': None,
                                 'free': False,
                                 'value': 0.0,  # unit: None
                                 'prior': {'category': 'normal', 'args': {'mu': 0.0, 'sigma': 0.05},
                                           'joint_prior_ref': None
                                           }
                                 },
                      },
                # By default all the datasets of an instrument are associated to 0.
                # If you want to model some datasets with another instrument model copy paste it,
                # give it a new name and file the Dataset dict.
                'Dataset': {0: '0', 1: '1', },

                'RVref': '0',

                },
      'FIES': {'def': {'DeltaRV': {'duplicate': None,
                                   'free': True,
                                   'value': None,  # unit: [amplitude of the RV data]
                                   'prior': {'category': 'normal', 'args': {'mu': -0.04, 'sigma': 0.01},
                                             'joint_prior_ref': None
                                             }
                                   },
                       'jitter': {'duplicate': None,
                                  'free': False,
                                  'value': 0.0,  # unit: None
                                  'prior': {'category': 'normal', 'args': {'mu': 0.0, 'sigma': 0.05},
                                            'joint_prior_ref': None
                                            }
                                  },
                       },
               # By default all the datasets of an instrument are associated to def.
               # If you want to model some datasets with another instrument model copy paste it,
               # give it a new name and file the Dataset dict.
               'Dataset': {0: 'def', },

               'RVref': 'def',

               },
      'HARPSN': {'def': {'DeltaRV': {'duplicate': None,
                                     'free': True,
                                     'value': None,  # unit: [amplitude of the RV data]
                                     'prior': {'category': 'normal', 'args': {'mu': 0.09, 'sigma': 0.01},
                                               'joint_prior_ref': None
                                               }
                                     },
                         'jitter': {'duplicate': None,
                                    'free': False,
                                    'value': 0.0,  # unit: None
                                    'prior': {'category': 'normal', 'args': {'mu': 0.0, 'sigma': 0.05},
                                              'joint_prior_ref': None
                                              }
                                    },
                         },
                 # By default all the datasets of an instrument are associated to def.
                 # If you want to model some datasets with another instrument model copy paste it,
                 # give it a new name and file the Dataset dict.
                 'Dataset': {0: 'def', },

                 'RVref': 'def',

                 },
      'PFS': {'def': {'DeltaRV': {'duplicate': None,
                                  'free': True,
                                  'value': None,  # unit: [amplitude of the RV data]
                                  'prior': {'category': 'normal', 'args': {'mu': -7.24, 'sigma': 0.01},
                                            'joint_prior_ref': None
                                            }
                                  },
                      'jitter': {'duplicate': None,
                                 'free': False,
                                 'value': 0.0,  # unit: None
                                 'prior': {'category': 'normal', 'args': {'mu': 0.0, 'sigma': 0.05},
                                           'joint_prior_ref': None
                                           }
                                 },
                      },
              # By default all the datasets of an instrument are associated to def.
              # If you want to model some datasets with another instrument model copy paste it,
              # give it a new name and file the Dataset dict.
              'Dataset': {0: 'def', },

              'RVref': 'def',

              },
      'RVrefGlob': 'SOPHIE'

      }

# instruments LC
LC = {'Balesta': {'def': {'jitter': {'duplicate': None,
                                     'free': False,
                                     'value': 0.0,  # unit: None
                                     'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                                               'joint_prior_ref': None
                                               }
                                     },
                          },
                  # By default all the datasets of an instrument are associated to def.
                  # If you want to model some datasets with another instrument model copy paste it,
                  # give it a new name and file the Dataset dict.
                  'Dataset': {0: 'def', },
                  },
      'C2PU': {'def': {'jitter': {'duplicate': None,
                                  'free': False,
                                  'value': 0.0,  # unit: None
                                  'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                                            'joint_prior_ref': None
                                            }
                                  },
                       },
               # By default all the datasets of an instrument are associated to def.
               # If you want to model some datasets with another instrument model copy paste it,
               # give it a new name and file the Dataset dict.
               'Dataset': {0: 'def', },
               },
      'K2': {'def': {'jitter': {'duplicate': None,
                                'free': False,
                                'value': 0.0,  # unit: None
                                'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                                          'joint_prior_ref': None
                                          }
                                },
                     },
             # By default all the datasets of an instrument are associated to def.
             # If you want to model some datasets with another instrument model copy paste it,
             # give it a new name and file the Dataset dict.
             'Dataset': {0: 'def', },
             },
      'NITES': {'def': {'jitter': {'duplicate': None,
                                   'free': False,
                                   'value': 0.0,  # unit: None
                                   'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                                             'joint_prior_ref': None
                                             }
                                   },
                        },
                # By default all the datasets of an instrument are associated to def.
                # If you want to model some datasets with another instrument model copy paste it,
                # give it a new name and file the Dataset dict.
                'Dataset': {0: 'def', },
                },

      }

# stars
A = {'R': {'duplicate': None,
           'free': True,
           'value': None,  # unit: solRad
           'prior': {'category': 'normal', 'args': {'mu': 0.926, 'sigma': 0.19, 'sigma_lims': [1.1, 3]},
                     'joint_prior_ref': None
                     }
           },
     'M': {'duplicate': None,
           'free': True,
           'value': None,  # unit: solMass
           'prior': {'category': 'normal', 'args': {'mu': 0.918, 'sigma': 0.086, 'sigma_lims': [3, 3]},
                     'joint_prior_ref': None
                     }
           },
     'v0': {'duplicate': None,
            'free': True,
            'value': None,  # unit: [amplitude of the RV data]
            'prior': {'category': 'normal', 'args': {'mu': 7.2, 'sigma': 0.1, 'sigma_lims': [3, 3]},
                      'joint_prior_ref': None
                      }
            },
     }

# planets
b = {'P': {'duplicate': None,
           'free': True,
           'value': None,  # unit: d
           'prior': {'category': 'normal', 'args': {'mu': 7.919454, 'sigma': 0.01, 'sigma_lims': [3, 3]},
                     'joint_prior_ref': 'priorhkPt'
                     }
           },
     'inc': {'duplicate': None,
             'free': True,
             'value': None,  # unit: rad
             'prior': {'category': 'sine', 'args': {'vmin': np.radians(84), 'vmax': np.radians(90)},
                       'joint_prior_ref': None
                       }
             },
     'OMEGA': {'duplicate': None,
               'free': False,
               'value': 3.141592653589793,  # unit: rad
               'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                         'joint_prior_ref': None
                         }
               },
     'tic': {'duplicate': None,
             'free': True,
             'value': None,  # unit: [time of the RV/LC data]
             'prior': {'category': 'normal', 'args': {'mu': 56813.38345, 'sigma': 0.004, 'sigma_lims': [3, 3]},
                       'joint_prior_ref': 'priorhkPt'
                       }
             },
     'Rrat': {'duplicate': None,
              'free': True,
              'value': None,  # unit: w/o unit
              'prior': {'category': 'normal', 'args': {'mu': 0.07, 'sigma': 0.01, 'sigma_lims': [3, 3]},
                        'joint_prior_ref': None
                        }
              },
     }

c = {'P': {'duplicate': None,
           'free': True,
           'value': None,  # unit: d
           'prior': {'category': 'normal', 'args': {'mu': 11.90701, 'sigma': 0.01, 'sigma_lims': [3, 3]},
                     'joint_prior_ref': 'priorhkPt'
                     }
           },
     'inc': {'duplicate': None,
             'free': True,
             'value': None,  # unit: rad
             'prior': {'category': 'normal', 'args': {'mu': np.radians(88.92), 'sigma': np.radians(0.41), 'sigma_lims': [3, 3]},
                       'joint_prior_ref': None
                       }
             },
     'OMEGA': {'duplicate': None,
               'free': True,
               'value': None,  # unit: rad
               'prior': {'category': 'uniform', 'args': {'vmin': np.radians(0), 'vmax': np.radians(360)},
                         'joint_prior_ref': None
                         }
               },
     'tic': {'duplicate': None,
             'free': True,
             'value': None,  # unit: [time of the RV/LC data]
             'prior': {'category': 'normal', 'args': {'mu': 56817.2759, 'sigma': 0.01, 'sigma_lims': [3, 3]},
                       'joint_prior_ref': 'priorhkPt'
                       }
             },
     'Rrat': {'duplicate': None,
              'free': True,
              'value': None,  # unit: w/o unit
              'prior': {'category': 'normal', 'args': {'mu': 0.04, 'sigma': 0.01, 'sigma_lims': [3, 3]},
                        'joint_prior_ref': None
                        }
              },
     }

# LDs
A_LDKp = {'ldc1': {'duplicate': None,
                   'free': True,
                   'value': None,  # unit: None
                   'prior': {'category': 'normal', 'args': {'mu': 0.460, 'sigma': 0.1, 'sigma_lims': [3, 3]},
                             'joint_prior_ref': None
                             }
                   },
          'ldc2': {'duplicate': None,
                   'free': True,
                   'value': None,  # unit: None
                   'prior': {'category': 'normal', 'args': {'mu': 0.210, 'sigma': 0.1, 'sigma_lims': [3, 3]},
                             'joint_prior_ref': None
                             }
                   },
          }

A_LDC2PU = {'ldc1': {'duplicate': None,
                     'free': True,
                     'value': None,  # unit: None
                     'prior': {'category': 'normal', 'args': {'mu': 0.476, 'sigma': 0.1, 'sigma_lims': [3, 3]},
                               'joint_prior_ref': None
                               }
                     },
            'ldc2': {'duplicate': None,
                     'free': True,
                     'value': None,  # unit: None
                     'prior': {'category': 'normal', 'args': {'mu': 0.232, 'sigma': 0.1, 'sigma_lims': [3, 3]},
                               'joint_prior_ref': None
                               }
                     },
            }

A_LDBalesta = {'ldc1': {'duplicate': None,
                        'free': True,
                        'value': None,  # unit: None
                        'prior': {'category': 'normal', 'args': {'mu': 0.435, 'sigma': 0.1, 'sigma_lims': [3, 3]},
                                  'joint_prior_ref': None
                                  }
                        },
               'ldc2': {'duplicate': None,
                        'free': True,
                        'value': None,  # unit: None
                        'prior': {'category': 'normal', 'args': {'mu': 0.232, 'sigma': 0.1, 'sigma_lims': [3, 3]},
                                  'joint_prior_ref': None
                                  }
                        },
               }

A_LDNITES = {'ldc1': {'duplicate': None,
                      'free': True,
                      'value': None,  # unit: None
                      'prior': {'category': 'normal', 'args': {'mu': 0.442, 'sigma': 0.1, 'sigma_lims': [3, 3]},
                                'joint_prior_ref': None
                                }
                      },
             'ldc2': {'duplicate': None,
                      'free': True,
                      'value': None,  # unit: None
                      'prior': {'category': 'normal', 'args': {'mu': 0.231, 'sigma': 0.1, 'sigma_lims': [3, 3]},
                                'joint_prior_ref': None
                                }
                      },
             }

# GravitionalGroupsDynamic

K219 = {'qplus': {'duplicate': None,
                  'free': True,
                  'value': None,  # unit: w/o unit
                  'prior': {'category': 'jeffreys', 'args': {'vmin': 1e-6, 'vmax': 1e-2},
                            'joint_prior_ref': None
                            }
                  },
        'qp': {'duplicate': None,
               'free': True,
               'value': None,  # unit: w/o unit
               'prior': {'category': 'jeffreys', 'args': {'vmin': 0.01, 'vmax': 100},
                         'joint_prior_ref': None
                         }
               },
        'hplus': {'duplicate': None,
                  'free': True,
                  'value': None,  # unit: w/o unit
                  'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                            'joint_prior_ref': 'priorhkPt'
                            }
                  },
        'hminus': {'duplicate': None,
                   'free': True,
                   'value': None,  # unit: w/o unit
                   'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                             'joint_prior_ref': 'priorhkPt'
                             }
                   },
        'kplus': {'duplicate': None,
                  'free': True,
                  'value': None,  # unit: w/o unit
                  'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                            'joint_prior_ref': 'priorhkPt'
                            }
                  },
        'kminus': {'duplicate': None,
                   'free': True,
                   'value': None,  # unit: w/o unit
                   'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                             'joint_prior_ref': 'priorhkPt'
                             }
                   },
        }

# Joint parameters
# Define below the joint parameter distributions.
joint_prior = {# Example:
               'priorhkPt': {'category': 'hkPt', 'args': {'Pb_prior': {'category': 'normal', 'args': {'mu': 7.919454, 'sigma': 0.01, 'sigma_lims': [3, 3]}},
                                                          'Pc_prior': {'category': 'normal', 'args': {'mu': 11.90701, 'sigma': 0.01, 'sigma_lims': [3, 3]}},
                                                          'eb_prior': {'category': 'normal', 'args': {'mu': 0., 'sigma': 0.1, 'lims': [0., 1.]}},
                                                          'ec_prior': {'category': 'normal', 'args': {'mu': 0., 'sigma': 0.1, 'lims': [0., 1.]}},
                                                          'omegab_prior': {'category': 'uniform', 'args': {'vmin': -np.radians(180), 'vmax': np.radians(180)}},
                                                          'omegac_prior': {'category': 'uniform', 'args': {'vmin': -np.radians(180), 'vmax': np.radians(180)}},
                                                          'tb_prior': {'category': 'normal', 'args': {'mu': 56813.38345, 'sigma': 0.004, 'sigma_lims': [3, 3]}},
                                                          'tc_prior': {'category': 'normal', 'args': {'mu': 56817.2759, 'sigma': 0.01, 'sigma_lims': [3, 3]}},
                                                          't_ref': 56816.,
                                                          },
                             'params': {'hplus': 'K219_hplus', 'hminus': 'K219_hminus',
                                        'kplus': 'K219_kplus', 'kminus': 'K219_kminus',
                                        'Pb': 'b_P', 'Pc': 'c_P', 'tb': 'b_tic', 'tc': 'c_tic'}
                             },
               }
