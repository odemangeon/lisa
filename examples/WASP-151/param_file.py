#!/usr/bin/python
# -*- coding:  utf-8 -*-
# Parametrisation file of WASP-151
import numpy as np

# Parameters
# instruments
# instruments LC
LC = {'K2': {'default': {'jitter': {'duplicate': None,
                                    'free': True,
                                    'value': None,  # unit: None
                                    'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1e-5},
                                              'joint_prior_ref': None
                                              }
                                    },
                         },
             # By default all the datasets of an instrument are associated to default.
             # If you want to model some datasets with another instrument model copy paste it,
             # give it a new name and file the Dataset dict.
             'Dataset': {0: 'default', },
             },
      'EulerCam': {'default': {'jitter': {'duplicate': None,
                                          'free': True,
                                          'value': None,  # unit: None
                                          'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1e-4},
                                                    'joint_prior_ref': None
                                                    }
                                          },
                               },
                   # By default all the datasets of an instrument are associated to default.
                   # If you want to model some datasets with another instrument model copy paste it,
                   # give it a new name and file the Dataset dict.
                   'Dataset': {0: 'default', 1: 'default', },
                   },
      'IAC80': {'default0': {'jitter': {'duplicate': None,
                                        'free': True,
                                        'value': None,  # unit: None
                                        'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1e-4},
                                                  'joint_prior_ref': None
                                                  }
                                        },
                             },
                'default1': {'jitter': {'duplicate': None,
                                        'free': True,
                                        'value': None,  # unit: None
                                        'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1e-4},
                                                  'joint_prior_ref': None
                                                  }
                                        },
                             },
                # By default all the datasets of an instrument are associated to default0.
                # If you want to model some datasets with another instrument model copy paste it,
                # give it a new name and file the Dataset dict.
                'Dataset': {0: 'default0', 1: 'default1', },
                },
      'TRAPPIST': {'default': {'jitter': {'duplicate': None,
                                          'free': True,
                                          'value': None,  # unit: None
                                          'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1e-4},
                                                    'joint_prior_ref': None
                                                    }
                                          },
                               },
                   # By default all the datasets of an instrument are associated to default.
                   # If you want to model some datasets with another instrument model copy paste it,
                   # give it a new name and file the Dataset dict.
                   'Dataset': {0: 'default', },
                   },

      }

# instruments RV
RV = {'SOPHIE': {'default': {'DeltaRV': {'duplicate': None,
                                         'free': False,
                                         'value': 0.0,  # unit: [amplitude of the RV data]
                                         'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                                                   'joint_prior_ref': None
                                                   }
                                         },
                             'jitter': {'duplicate': None,
                                        'free': True,
                                        'value': None,  # unit: None
                                        'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 0.005},
                                                  'joint_prior_ref': None
                                                  }
                                        },
                             },
                 # By default all the datasets of an instrument are associated to default.
                 # If you want to model some datasets with another instrument model copy paste it,
                 # give it a new name and file the Dataset dict.
                 'Dataset': {0: 'default', },

                 'RVref': 'default',

                 },
      'CORALIE': {'default': {'DeltaRV': {'duplicate': None,
                                          'free': True,
                                          'value': None,  # unit: [amplitude of the RV data]
                                          'prior': {'category': 'normal', 'args': {'mu': 0.1, 'sigma': 0.05},
                                                    'joint_prior_ref': None
                                                    }
                                          },
                              'jitter': {'duplicate': None,
                                         'free': True,
                                         'value': None,  # unit: None
                                         'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 0.005},
                                                   'joint_prior_ref': None
                                                   }
                                         },
                              },
                  # By default all the datasets of an instrument are associated to default.
                  # If you want to model some datasets with another instrument model copy paste it,
                  # give it a new name and file the Dataset dict.
                  'Dataset': {0: 'default', },

                  'RVref': 'default',

                  },
      'RVrefGlob': 'SOPHIE'

      }

# stars
A = {'rho': {'duplicate': None,
             'free': True,
             'value': None,  # unit: Solar density
             'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                       'joint_prior_ref': 'transiting'
                       }
             },
     'v0': {'duplicate': None,
            'free': True,
            'value': None,  # unit: [amplitude of the RV data]
            'prior': {'category': 'normal', 'args': {'mu': -12.4, 'sigma': 0.02},
                      'joint_prior_ref': None
                      }
            },
     }

# planets
b = {'P': {'duplicate': None,
           'free': True,
           'value': None,  # unit: [time of the RV/LC data]
           'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                     'joint_prior_ref': 'transiting'
                     }
           },
     'cosinc': {'duplicate': None,
                'free': True,
                'value': None,  # unit: w/o unit
                'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                          'joint_prior_ref': 'transiting'
                          }
                },
     'tic': {'duplicate': None,
             'free': True,
             'value': None,  # unit: [time of the RV data]
             'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                       'joint_prior_ref': 'transiting'
                       }
             },
     'K': {'duplicate': None,
           'free': True,
           'value': None,  # unit: [amplitude of the RV data]
           'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 0.1},
                     'joint_prior_ref': None
                     }
           },
     'Rrat': {'duplicate': None,
              'free': True,
              'value': None,  # unit: w/o unit
              'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                        'joint_prior_ref': 'transiting'
                        }
              },
     'ecosw': {'duplicate': None,
               'free': True,
               'value': None,  # unit: w/o unit
               'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                         'joint_prior_ref': 'polarew'
                         }
               },
     'esinw': {'duplicate': None,
               'free': True,
               'value': None,  # unit: w/o unit
               'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                         'joint_prior_ref': 'polarew'
                         }
               },
     }

# LDs
A_LDz = {'ldc1': {'duplicate': None,
                  'free': True,
                  'value': None,  # unit: None
                  'prior': {'category': 'normal', 'args': {'mu': 0.3412, 'sigma': 0.0013},
                            'joint_prior_ref': None
                            }
                  },
         'ldc2': {'duplicate': None,
                  'free': True,
                  'value': None,  # unit: None
                  'prior': {'category': 'normal', 'args': {'mu': 0.1269, 'sigma': 0.0039},
                            'joint_prior_ref': None
                            }
                  },
         }

A_LDNG = {'ldc1': {'duplicate': None,
                   'free': True,
                   'value': None,  # unit: None
                   'prior': {'category': 'normal', 'args': {'mu': 0.4861, 'sigma': 0.0021},
                             'joint_prior_ref': None
                             }
                   },
          'ldc2': {'duplicate': None,
                   'free': True,
                   'value': None,  # unit: None
                   'prior': {'category': 'normal', 'args': {'mu': 0.1286, 'sigma': 0.0052},
                             'joint_prior_ref': None
                             }
                   },
          }

A_LDKp = {'ldc1': {'duplicate': None,
                   'free': True,
                   'value': None,  # unit: None
                   'prior': {'category': 'normal', 'args': {'mu': 0.5501, 'sigma': 0.0025},
                             'joint_prior_ref': None
                             }
                   },
          'ldc2': {'duplicate': None,
                   'free': True,
                   'value': None,  # unit: None
                   'prior': {'category': 'normal', 'args': {'mu': 0.1191, 'sigma': 0.0054},
                             'joint_prior_ref': None
                             }
                   },
          }

A_LDR = {'ldc1': {'duplicate': None,
                  'free': True,
                  'value': None,  # unit: None
                  'prior': {'category': 'normal', 'args': {'mu': 0.4781, 'sigma': 0.0022},
                            'joint_prior_ref': None
                            }
                  },
         'ldc2': {'duplicate': None,
                  'free': True,
                  'value': None,  # unit: None
                  'prior': {'category': 'normal', 'args': {'mu': 0.1304, 'sigma': 0.0055},
                            'joint_prior_ref': None
                            }
                  },
         }

# GravitionalGroups

WASP151 = {}

# Joint parameters
# Define below the joint parameter distributions.
joint_prior = {
               'polarew': {'category': 'polar', 'args': {'r_prior': {'category': 'normal', 'args': {'mu': 0.0, 'sigma': 0.1, 'lims': [0, 1]}},
                                                         'theta_prior': {'category': 'uniform', 'args': {'vmin': -np.pi, 'vmax': np.pi}}
                                                         },
                           'params': {'x': 'b_ecosw', 'y': 'b_esinw'}
                           },
               'transiting': {'category': 'transiting_rho', 'args': {'transiting': [True, ], 'allow_grazing': [True, ], 't_ref': [57740, ],
                                                                     'rhostar_prior': {'category': 'normal', 'args': {'mu': 0.72, 'sigma': (0.02 + 0.04) / 2, 'lims': [0, np.inf]}},
                                                                     'Rrat_prior': [{"category": 'uniform', 'args': {'vmin': 0., 'vmax': 1.}}, ],
                                                                     'b_prior': [{"category": 'uniform', 'args': {'vmin': 0., 'vmax': 2.}}, ],
                                                                     'P_prior': [{"category": 'jeffreys', 'args': {'vmin': 1., 'vmax': 100.}}, ],
                                                                     'Phi_prior': [{'category': 'uniform', 'args': {'vmin': 0, 'vmax': 1}}, ],
                                                                     },
                              'params': {'rhostar': 'A_rho', 'P': ['b_P', ], 'tic': ['b_tic', ], 'cosinc': ['b_cosinc', ], 'Rrat': ['b_Rrat', ], }
                              }
               }
