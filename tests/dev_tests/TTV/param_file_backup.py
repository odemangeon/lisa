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
                                      'prior': {'category': 'normal', 'args': {'mu': 0.0, 'sigma': 0.0039},
                                                'joint_prior_ref': None
                                                }
                                      },
                           'jitter': {'duplicate': None,
                                      'free': True,
                                      'value': None,  # unit: None
                                      'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 0.0012},
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
                                      'prior': {'category': 'normal', 'args': {'mu': 0.0, 'sigma': 0.0039},
                                                'joint_prior_ref': None
                                                }
                                      },
                           'jitter': {'duplicate': None,
                                      'free': True,
                                      'value': None,  # unit: None
                                      'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 0.0012},
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
                                      'prior': {'category': 'normal', 'args': {'mu': 0.0, 'sigma': 0.0039},
                                                'joint_prior_ref': None
                                                }
                                      },
                           'jitter': {'duplicate': None,
                                      'free': True,
                                      'value': None,  # unit: None
                                      'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 0.0012},
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
                                      'prior': {'category': 'normal', 'args': {'mu': 0.0, 'sigma': 0.0039},
                                                'joint_prior_ref': None
                                                }
                                      },
                           'jitter': {'duplicate': None,
                                      'free': True,
                                      'value': None,  # unit: None
                                      'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 0.0012},
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
                                      'prior': {'category': 'normal', 'args': {'mu': 0.0, 'sigma': 0.0039},
                                                'joint_prior_ref': None
                                                }
                                      },
                           'jitter': {'duplicate': None,
                                      'free': True,
                                      'value': None,  # unit: None
                                      'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 0.0012},
                                                'joint_prior_ref': None
                                                }
                                      },
                           },
                 'Dataset': {10: 'inst0', 11: 'inst1', 12: 'inst2', 13: 'inst3', 14: 'inst4', },
                 },

      }

# instruments IND-ROLL
INDROLL = {'CHEOPS': {'inst': {},
                      'Dataset': {10: 'inst', 11: 'inst', 12: 'inst', 13: 'inst', 14: 'inst', },
                      },

           }

# instruments IND-CX
INDCX = {'CHEOPS': {'inst': {},
                    'Dataset': {10: 'inst', 11: 'inst', 12: 'inst', 13: 'inst', 14: 'inst', },
                    },

         }

# instruments IND-CY
INDCY = {'CHEOPS': {'inst': {},
                    'Dataset': {10: 'inst', 11: 'inst', 12: 'inst', 13: 'inst', 14: 'inst', },
                    },

         }

# instruments IND-SMEAR
INDSMEAR = {'CHEOPS': {'inst': {},
                       'Dataset': {10: 'inst', 11: 'inst', 12: 'inst', 13: 'inst', 14: 'inst', },
                       },

            }

# instruments IND-TF
INDTF = {'CHEOPS': {'inst': {},
                    'Dataset': {10: 'inst', 11: 'inst', 12: 'inst', 13: 'inst', 14: 'inst', },
                    },

         }

# instruments IND-BKG
INDBKG = {'CHEOPS': {'inst': {},
                     'Dataset': {10: 'inst', 11: 'inst', 12: 'inst', 13: 'inst', 14: 'inst', },
                     },

          }

# instruments IND-DARK
INDDARK = {'CHEOPS': {'inst': {},
                      'Dataset': {10: 'inst', 11: 'inst', 12: 'inst', 13: 'inst', 14: 'inst', },
                      },

           }

# instruments IND-CONTA
INDCONTA = {'CHEOPS': {'inst': {},
                       'Dataset': {10: 'inst', 11: 'inst', 12: 'inst', 13: 'inst', 14: 'inst', },
                       },

            }

# stars
A = {'rho': {'duplicate': None,
             'free': True,
             'value': None,  # unit: None
             'prior': {'category': 'normal', 'args': {'mu': 0.26943233617690693, 'sigma': 0.03294569900343486, 'lims': [0, np.inf]},
                       'joint_prior_ref': None
                       }
             },
     }

# planets
b = {'P': {'duplicate': None,
           'free': True,
           'value': None,  # unit: None
           'prior': {'category': 'normal', 'args': {'mu': 1.80988198, 'sigma': 0.00000064, 'lims': [0, np.inf]},
                     'joint_prior_ref': None
                     }
           },
     'cosinc': {'duplicate': None,
                'free': True,
                'value': None,  # unit: w/o unit
                'prior': {'category': 'normal', 'args': {'mu': 0.006576095643725173, 'sigma': 0.0005876517196153033, 'lims': [0, 1]},
                          'joint_prior_ref': None
                          }
                },
     'Rrat': {'duplicate': None,
              'free': True,
              'value': None,  # unit: None
              'prior': {'category': 'normal', 'args': {'mu': 0.10852, 'sigma': 0.00096},
                        'joint_prior_ref': None
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
     'tic0': {'duplicate': None,
              'free': True,
              'value': None,  # unit: None
              'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                        'joint_prior_ref': None
                        }
              },
     'tic1': {'duplicate': None,
              'free': True,
              'value': None,  # unit: None
              'prior': {'category': 'normal', 'args': {'mu': 859.81968, 'sigma': 1 / 24, 'sigma_lims': [3, 3]},
                        'joint_prior_ref': None
                        }
              },
     'tic2': {'duplicate': None,
              'free': True,
              'value': None,  # unit: None
              'prior': {'category': 'normal', 'args': {'mu': 859.81968, 'sigma': 1 / 24, 'sigma_lims': [3, 3]},
                        'joint_prior_ref': None
                        }
              },
     'tic3': {'duplicate': None,
              'free': True,
              'value': None,  # unit: None
              'prior': {'category': 'normal', 'args': {'mu': 859.81968, 'sigma': 1 / 24, 'sigma_lims': [3, 3]},
                        'joint_prior_ref': None
                        }
              },
     'tic4': {'duplicate': None,
              'free': True,
              'value': None,  # unit: None
              'prior': {'category': 'normal', 'args': {'mu': 859.81968, 'sigma': 1 / 24, 'sigma_lims': [3, 3]},
                        'joint_prior_ref': None
                        }
              },
     }

# LDs
A_LD = {'ldc1': {'duplicate': None,
                 'free': True,
                 'value': None,  # unit: None
                 'prior': {'category': 'normal', 'args': {'mu': -0.0127, 'sigma': 0.0124},
                           'joint_prior_ref': None
                           }
                 },
        'ldc2': {'duplicate': None,
                 'free': True,
                 'value': None,  # unit: None
                 'prior': {'category': 'normal', 'args': {'mu': 0.8229, 'sigma': 0.0158},
                           'joint_prior_ref': None
                           }
                 },
        'ldc3': {'duplicate': None,
                 'free': True,
                 'value': None,  # unit: None
                 'prior': {'category': 'normal', 'args': {'mu': -0.0335, 'sigma': 0.0106},
                           'joint_prior_ref': None
                           }
                 },
        'ldc4': {'duplicate': None,
                 'free': True,
                 'value': None,  # unit: None
                 'prior': {'category': 'normal', 'args': {'mu': -0.1269, 'sigma': 0.0052},
                           'joint_prior_ref': None
                           }
                 },
        }

# GravitionalGroups

WASP76 = {}

# Joint parameters
# Define below the joint parameter distributions.
joint_prior = {'polarew': {'category': 'polar', 'args': {'r_prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 0.1}},
                                                         'theta_prior': {'category': 'uniform', 'args': {'vmin': -np.pi, 'vmax': np.pi}},
                                                         },
                           'params': {'x': 'WASP-76_b_ecosw', 'y': 'WASP-76_b_esinw'}
                           },
               }
