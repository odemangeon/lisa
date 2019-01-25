#!/usr/bin/python
# -*- coding:  utf-8 -*-
# Parametrisation file of WASP-151
from numpy import sqrt

# Parameters
# instruments
# instruments RV
SOPHIE = {'default': {'DeltaRV': {'free': False,
                                  'value': 0.0,  # unit: [K]
                                  'prior': {'category': 'uniform', 'args': {'vmax': 1.0, 'vmin': 0.0}
                                            }
                                  },
                      'jitter': {'free': True,
                                 'value': None,  # unit: n/a
                                 'prior': {'category': 'normal', 'args': {'mu': 0.0, 'sigma': 0.1}
                                           }
                                 },
                      },
          # By default all the datasets of an instrument are associated to default.
          # If you want to model some datasets with another instrument model copy paste it,
          # give it a new name and file the Dataset dict.
          'Dataset': {0: 'default', },

          'RVref': 'default',
          }

CORALIE = {'default': {'DeltaRV': {'free': True,
                                   'value': None,  # unit: [K]
                                   'prior': {'category': 'normal', 'args': {'mu': -0.1, 'sigma': 0.05}
                                             }
                                   },
                       'jitter': {'free': True,
                                  'value': None,  # unit: n/a
                                  'prior': {'category': 'normal', 'args': {'mu': 0.0, 'sigma': 0.1}
                                            }
                                  },
                       },
           # By default all the datasets of an instrument are associated to default.
           # If you want to model some datasets with another instrument model copy paste it,
           # give it a new name and file the Dataset dict.
           'Dataset': {0: 'default', },

           'RVref': 'default',
           }

RVrefGlob = 'SOPHIE'

# instruments LC
IAC80 = {'default0': {'DeltaOOT': {'free': True,
                                   'value': None,  # unit: wo unit
                                   'prior': {'category': 'normal', 'args': {'mu': 0.005, 'sigma': 0.01}
                                             }
                                   },
                      'driftOOT': {'free': True,
                                   'value': None,  # unit: wo unit/s
                                   'prior': {'category': 'normal', 'args': {'mu': 0.0, 'sigma': 0.33}
                                             }
                                   },
                      'jitter': {'free': False,
                                 'value': 0.0,  # unit: n/a
                                 'prior': {'category': 'uniform', 'args': {'vmax': 1.0, 'vmin': 0.0}
                                           }
                                 },
                      },
         'default1': {'DeltaOOT': {'free': True,
                                   'value': None,  # unit: wo unit
                                   'prior': {'category': 'normal', 'args': {'mu': 0.0, 'sigma': 0.01}
                                             }
                                   },
                      'driftOOT': {'free': True,
                                   'value': None,  # unit: wo unit/s
                                   'prior': {'category': 'normal', 'args': {'mu': 0.0, 'sigma': 0.1}
                                             }
                                   },
                      'jitter': {'free': False,
                                 'value': 0.0,  # unit: n/a
                                 'prior': {'category': 'uniform', 'args': {'vmax': 1.0, 'vmin': 0.0}
                                           }
                                 },
                      },
         # By default all the datasets of an instrument are associated to default0.
         # If you want to model some datasets with another instrument model copy paste it,
         # give it a new name and file the Dataset dict.
         'Dataset': {1: 'default1', 0: 'default0', },         }

K2 = {'default': {'DeltaOOT': {'free': False,
                               'value': 0.0,  # unit: wo unit
                               'prior': {'category': 'uniform', 'args': {'vmax': 1.0, 'vmin': 0.0}
                                         }
                               },
                  'driftOOT': {'free': False,
                               'value': 0.0,  # unit: wo unit/s
                               'prior': {'category': 'uniform', 'args': {'vmax': 1.0, 'vmin': 0.0}
                                         }
                               },
                  'jitter': {'free': False,
                             'value': 1.596557332287149,  # unit: n/a
                             'prior': {'category': 'normal', 'args': {'mu': 0.0, 'sigma': 0.2}
                                       }
                             },
                  },
      # By default all the datasets of an instrument are associated to default.
      # If you want to model some datasets with another instrument model copy paste it,
      # give it a new name and file the Dataset dict.
      'Dataset': {0: 'default', },      }

EulerCam = {'default': {'DeltaOOT': {'free': False,
                                     'value': 0.0,  # unit: wo unit
                                     'prior': {'category': 'uniform', 'args': {'vmax': 1.0, 'vmin': 0.0}
                                               }
                                     },
                        'driftOOT': {'free': False,
                                     'value': 0.0,  # unit: wo unit/s
                                     'prior': {'category': 'uniform', 'args': {'vmax': 1.0, 'vmin': 0.0}
                                               }
                                     },
                        'jitter': {'free': False,
                                   'value': 0.0,  # unit: n/a
                                   'prior': {'category': 'uniform', 'args': {'vmax': 1.0, 'vmin': 0.0}
                                             }
                                   },
                        },
            # By default all the datasets of an instrument are associated to default.
            # If you want to model some datasets with another instrument model copy paste it,
            # give it a new name and file the Dataset dict.
            'Dataset': {0: 'default', 1: 'default', },            }

TRAPPIST = {'default': {'DeltaOOT': {'free': False,
                                     'value': 0.0,  # unit: wo unit
                                     'prior': {'category': 'uniform', 'args': {'vmax': 1.0, 'vmin': 0.0}
                                               }
                                     },
                        'driftOOT': {'free': False,
                                     'value': 0.0,  # unit: wo unit/s
                                     'prior': {'category': 'uniform', 'args': {'vmax': 1.0, 'vmin': 0.0}
                                               }
                                     },
                        'jitter': {'free': False,
                                   'value': 0.0,  # unit: n/a
                                   'prior': {'category': 'uniform', 'args': {'vmax': 1.0, 'vmin': 0.0}
                                             }
                                   },
                        },
            # By default all the datasets of an instrument are associated to default.
            # If you want to model some datasets with another instrument model copy paste it,
            # give it a new name and file the Dataset dict.
            'Dataset': {0: 'default', },            }


# stars
A = {'v0': {'free': True,
            'value': None,  # unit: n/a
            'prior': {'category': 'normal', 'args': {'mu': -12.4, 'sigma': 0.02}
                      }
            },
     }

# planets
b = {'P': {'free': True,
           'value': None,  # unit: n/a
           'prior': {'category': 'normal', 'args': {'mu': 4.5334, 'sigma': 0.003}
                     }
           },
     'cosinc': {'free': True,
                'value': None,  # unit: n/a
                'prior': {'category': 'normal', 'args': {'mu': 0.0, 'sigma': 0.1, 'lims': [0., 1.]}
                          }
                },
     'tc': {'free': True,
            'value': None,  # unit: n/a
            'prior': {'category': 'normal', 'args': {'mu': 57741.00885442065, 'sigma': 0.1}
                      }
            },
     'K': {'free': True,
           'value': None,  # unit: n/a
           'prior': {'category': 'uniform', 'args': {'vmax': 0.1, 'vmin': 0.0}
                     }
           },
     'Rrat': {'free': True,
              'value': None,  # unit: n/a
              'prior': {'category': 'normal', 'args': {'mu': 0.097, 'sigma': 0.01, 'lims': [0., 1.]}
                        }
              },
     'aR': {'free': True,
            'value': None,  # unit: n/a
            'prior': {'category': 'normal', 'args': {'mu': 8.67, 'sigma': 1., 'lims': [0., 30.]}
                      }
            },
     'secosw': {'free': True,
                'value': None,  # unit: n/a
                'prior': {'category': 'normal', 'args': {'mu': 0.0, 'sigma': 0.05, 'lims': [-1/sqrt(2), 1/sqrt(2)]}
                          }
                },
     'sesinw': {'free': True,
                'value': None,  # unit: n/a
                'prior': {'category': 'normal', 'args': {'mu': 0.0, 'sigma': 0.05, 'lims': [-1/sqrt(2), 1/sqrt(2)]}
                          }
                },
     }

# LDs
LDz = {'ldc1': {'free': True,
                 'value': None,  # unit: n/a
                 'prior': {'category': 'normal', 'args': {'mu': 0.3412, 'sigma': 0.0013}
                           }
                 },
        'ldc2': {'free': True,
                 'value': None,  # unit: n/a
                 'prior': {'category': 'normal', 'args': {'mu': 0.1269, 'sigma': 0.0039}
                           }
                 },
       }

LDKp = {'ldc1': {'free': True,
                 'value': None,  # unit: n/a
                 'prior': {'category': 'normal', 'args': {'mu': 0.5501, 'sigma': 0.0025}
                           }
                 },
        'ldc2': {'free': True,
                 'value': None,  # unit: n/a
                 'prior': {'category': 'normal', 'args': {'mu': 0.1191, 'sigma': 0.0054}
                           }
                 },
        }

LDNG = {'ldc1': {'free': True,
                 'value': None,  # unit: n/a
                 'prior': {'category': 'normal', 'args': {'mu': 0.4861, 'sigma': 0.0021}
                           }
                 },
        'ldc2': {'free': True,
                 'value': None,  # unit: n/a
                 'prior': {'category': 'normal', 'args': {'mu': 0.1286, 'sigma': 0.0052}
                           }
                 },
        }

LDR = {'ldc1': {'free': True,
                'value': None,  # unit: n/a
                'prior': {'category': 'normal', 'args': {'mu': 0.4781, 'sigma': 0.0022}
                          }
                },
       'ldc2': {'free': True,
                'value': None,  # unit: n/a
                'prior': {'category': 'normal', 'args': {'mu': 0.1304, 'sigma': 0.0055}
                          }
                },
       }
