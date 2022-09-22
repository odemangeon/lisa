#!/usr/bin/python
# -*- coding:  utf-8 -*-
# Parametrisation file of WASP-76
import numpy as np

# Parameters
# instruments
# instruments LC
LC = {'CHEOPS': {'inst0': {'contam': {'duplicate': None,
                                      'free': False,
                                      'value': 0,  # unit: wo unit
                                      'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                                                'joint_prior_ref': None
                                                }
                                      },
                           'DeltaF': {'duplicate': None,
                                      'free': True,
                                      'value': None,  # unit: wo unit
                                      'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                                                'joint_prior_ref': None
                                                }
                                      },
                           'jitter': {'duplicate': None,
                                      'free': True,
                                      'value': None,  # unit: None
                                      'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                                                'joint_prior_ref': None
                                                }
                                      },
                           },
                 'inst1': {'contam': {'duplicate': None,
                                      'free': False,
                                      'value': 0,  # unit: wo unit
                                      'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                                                'joint_prior_ref': None
                                                }
                                      },
                           'DeltaF': {'duplicate': None,
                                      'free': True,
                                      'value': None,  # unit: wo unit
                                      'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                                                'joint_prior_ref': None
                                                }
                                      },
                           'jitter': {'duplicate': None,
                                      'free': True,
                                      'value': None,  # unit: None
                                      'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                                                'joint_prior_ref': None
                                                }
                                      },
                           },
                 'inst2': {'contam': {'duplicate': None,
                                      'free': False,
                                      'value': 0,  # unit: wo unit
                                      'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                                                'joint_prior_ref': None
                                                }
                                      },
                           'DeltaF': {'duplicate': None,
                                      'free': True,
                                      'value': None,  # unit: wo unit
                                      'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                                                'joint_prior_ref': None
                                                }
                                      },
                           'jitter': {'duplicate': None,
                                      'free': True,
                                      'value': None,  # unit: None
                                      'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                                                'joint_prior_ref': None
                                                }
                                      },
                           },
                 'inst3': {'contam': {'duplicate': None,
                                      'free': False,
                                      'value': 0,  # unit: wo unit
                                      'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                                                'joint_prior_ref': None
                                                }
                                      },
                           'DeltaF': {'duplicate': None,
                                      'free': True,
                                      'value': None,  # unit: wo unit
                                      'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                                                'joint_prior_ref': None
                                                }
                                      },
                           'jitter': {'duplicate': None,
                                      'free': True,
                                      'value': None,  # unit: None
                                      'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                                                'joint_prior_ref': None
                                                }
                                      },
                           },
                 'inst4': {'contam': {'duplicate': None,
                                      'free': False,
                                      'value': 0,  # unit: wo unit
                                      'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                                                'joint_prior_ref': None
                                                }
                                      },
                           'DeltaF': {'duplicate': None,
                                      'free': True,
                                      'value': None,  # unit: wo unit
                                      'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                                                'joint_prior_ref': None
                                                }
                                      },
                           'jitter': {'duplicate': None,
                                      'free': True,
                                      'value': None,  # unit: None
                                      'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                                                'joint_prior_ref': None
                                                }
                                      },
                           },
                 'Dataset': {10: 'inst0', 11: 'inst1', 12: 'inst2', 13: 'inst3', 14: 'inst4', },
                 },

      }

# instruments IND-ROLL
INDROLL = {'CHEOPS': {'inst': {                               },
                      'Dataset': {10: 'inst', 11: 'inst', 12: 'inst', 13: 'inst', 14: 'inst', },
                      },

           }

# instruments IND-CX
INDCX = {'CHEOPS': {'inst': {                             },
                    'Dataset': {10: 'inst', 11: 'inst', 12: 'inst', 13: 'inst', 14: 'inst', },
                    },

         }

# instruments IND-CY
INDCY = {'CHEOPS': {'inst': {                             },
                    'Dataset': {10: 'inst', 11: 'inst', 12: 'inst', 13: 'inst', 14: 'inst', },
                    },

         }

# instruments IND-SMEAR
INDSMEAR = {'CHEOPS': {'inst': {                                },
                       'Dataset': {10: 'inst', 11: 'inst', 12: 'inst', 13: 'inst', 14: 'inst', },
                       },

            }

# instruments IND-TF
INDTF = {'CHEOPS': {'inst': {                             },
                    'Dataset': {10: 'inst', 11: 'inst', 12: 'inst', 13: 'inst', 14: 'inst', },
                    },

         }

# instruments IND-BKG
INDBKG = {'CHEOPS': {'inst': {                              },
                     'Dataset': {10: 'inst', 11: 'inst', 12: 'inst', 13: 'inst', 14: 'inst', },
                     },

          }

# instruments IND-DARK
INDDARK = {'CHEOPS': {'inst': {                               },
                      'Dataset': {10: 'inst', 11: 'inst', 12: 'inst', 13: 'inst', 14: 'inst', },
                      },

           }

# instruments IND-CONTA
INDCONTA = {'CHEOPS': {'inst': {                                },
                       'Dataset': {10: 'inst', 11: 'inst', 12: 'inst', 13: 'inst', 14: 'inst', },
                       },

            }

# stars
A = {'rho': {'duplicate': None,
             'free': True,
             'value': None,  # unit: Solar density
             'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                       'joint_prior_ref': None
                       }
             },
     }

# planets
b = {'Rrat': {'duplicate': None,
              'free': True,
              'value': None,  # unit: None
              'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                        'joint_prior_ref': None
                        }
              },
     'P0': {'duplicate': None,
            'free': True,
            'value': None,  # unit: time unit of LC/RV datasets
            'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                      'joint_prior_ref': None
                      }
            },
     'tic0': {'duplicate': None,
              'free': True,
              'value': None,  # unit: time unit of LC/RV datasets
              'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                        'joint_prior_ref': None
                        }
              },
     'cosinc0': {'duplicate': None,
                 'free': True,
                 'value': None,  # unit: w/o unit
                 'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                           'joint_prior_ref': None
                           }
                 },
     'ecosw0': {'duplicate': None,
                'free': True,
                'value': None,  # unit: w/o unit
                'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                          'joint_prior_ref': None
                          }
                },
     'esinw0': {'duplicate': None,
                'free': True,
                'value': None,  # unit: w/o unit
                'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                          'joint_prior_ref': None
                          }
                },
     'tic2': {'duplicate': None,
              'free': True,
              'value': None,  # unit: time unit of LC/RV datasets
              'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                        'joint_prior_ref': None
                        }
              },
     'tic1': {'duplicate': None,
              'free': True,
              'value': None,  # unit: time unit of LC/RV datasets
              'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                        'joint_prior_ref': None
                        }
              },
     'tic4': {'duplicate': None,
              'free': True,
              'value': None,  # unit: time unit of LC/RV datasets
              'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                        'joint_prior_ref': None
                        }
              },
     'tic3': {'duplicate': None,
              'free': True,
              'value': None,  # unit: time unit of LC/RV datasets
              'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                        'joint_prior_ref': None
                        }
              },
     }

# LDs
A_LD = {'ldc1': {'duplicate': None,
                 'free': True,
                 'value': None,  # unit: None
                 'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                           'joint_prior_ref': None
                           }
                 },
        'ldc2': {'duplicate': None,
                 'free': True,
                 'value': None,  # unit: None
                 'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                           'joint_prior_ref': None
                           }
                 },
        'ldc3': {'duplicate': None,
                 'free': True,
                 'value': None,  # unit: None
                 'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                           'joint_prior_ref': None
                           }
                 },
        'ldc4': {'duplicate': None,
                 'free': True,
                 'value': None,  # unit: None
                 'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                           'joint_prior_ref': None
                           }
                 },
        }

# GravitionalGroups

WASP76 = {          }

# Joint parameters
# Define below the joint parameter distributions.
joint_prior = {# Example:
               # 'priorhkP': {'category': 'hkP', 'args': {'Pb_prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0} } },
               #              'params': {'hplus': 'K219_hplus', 'hminus': 'K219_hminus',
               #                         'kplus': 'K219_kplus', 'kminus': 'K219_kminus',
               #                         'Pb': 'K219_b_P', 'Pc': 'K219_c_P'}
               #              }
               }
