#!/usr/bin/python
# -*- coding:  utf-8 -*-
# Parametrisation file of K2-19
from numpy import sqrt

# Parameters
# instruments
# instruments RV
SOPHIE = {'default': {'jitter': {'free': True,
                                 'value': None,  # unit: wo unit
                                 'prior': {'category': 'normal', 'args': {'mu': 0.0, 'sigma': 0.5}
                                           }
                                 },
                      'DeltaRV': {'free': False,
                                  'value': 0.0,  # unit: [K]
                                  'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0}
                                            }
                                  },
                      },
          # By default all the datasets of an instrument are associated to default.
          # If you want to model some datasets with another instrument model copy paste it,
          # give it a new name and file the Dataset dict.
          'Dataset': {'0': 'default', },

          'RVref': 'default',
          }

HARPS = {'default0': {'jitter': {'free': True,
                                'value': None,  # unit: wo unit
                                'prior': {'category': 'normal', 'args': {'mu': 0.0, 'sigma': 0.5}
                                          }
                                },
                     'DeltaRV': {'free': True,
                                 'value': None,  # unit: [K]
                                 'prior': {'category': 'normal', 'args': {'mu': 0.1, 'sigma': 0.05}
                                           }
                                 },
                     },
         'default1': {'jitter': {'free': True,
                                'value': None,  # unit: wo unit
                                'prior': {'category': 'normal', 'args': {'mu': 0.0, 'sigma': 0.5}
                                          }
                                },
                     'DeltaRV': {'free': True,
                                 'value': None,  # unit: [K]
                                 'prior': {'category': 'normal', 'args': {'mu': -7.3, 'sigma': 0.05}
                                           }
                                 },
                     },
         # By default all the datasets of an instrument are associated to default.
         # If you want to model some datasets with another instrument model copy paste it,
         # give it a new name and file the Dataset dict.
         'Dataset': {'0': 'default0', '1': 'default1', },

         'RVref': 'default0',
         }

FIES = {'default': {'jitter': {'free': True,
                               'value': None,  # unit: wo unit
                               'prior': {'category': 'normal', 'args': {'mu': 0.0, 'sigma': 0.5}
                                         }
                               },
                    'DeltaRV': {'free': True,
                                'value': None,  # unit: [K]
                                'prior': {'category': 'normal', 'args': {'mu': 0.0, 'sigma': 0.5}
                                          }
                                },
                    },
        # By default all the datasets of an instrument are associated to default.
        # If you want to model some datasets with another instrument model copy paste it,
        # give it a new name and file the Dataset dict.
        'Dataset': {'0': 'default', },

        'RVref': 'default',
        }

HARPSN = {'default': {'jitter': {'free': True,
                                 'value': None,  # unit: wo unit
                                 'prior': {'category': 'normal', 'args': {'mu': 0.0, 'sigma': 0.5}
                                           }
                                 },
                      'DeltaRV': {'free': True,
                                  'value': None,  # unit: [K]
                                  'prior': {'category': 'normal', 'args': {'mu': 0.0, 'sigma': 0.5}
                                            }
                                  },
                      },
          # By default all the datasets of an instrument are associated to default.
          # If you want to model some datasets with another instrument model copy paste it,
          # give it a new name and file the Dataset dict.
          'Dataset': {'0': 'default', },

          'RVref': 'default',
          }

PFS = {'default': {'jitter': {'free': True,
                              'value': None,  # unit: wo unit
                              'prior': {'category': 'normal', 'args': {'mu': 0.0, 'sigma': 0.5}
                                        }
                              },
                   'DeltaRV': {'free': True,
                               'value': None,  # unit: [K]
                               'prior': {'category': 'normal', 'args': {'mu': -7.2, 'sigma': 0.05}
                                         }
                               },
                   },
       # By default all the datasets of an instrument are associated to default.
       # If you want to model some datasets with another instrument model copy paste it,
       # give it a new name and file the Dataset dict.
       'Dataset': {'0': 'default', },

       'RVref': 'default',
       }

RVrefGlob = 'SOPHIE'

# stars
A = {'v0': {'free': True,
            'value': None,  # unit: n/a
            'prior': {'category': 'normal', 'args': {'mu': 7.2, 'sigma': 0.1}
                      }
            },
     }

# planets
b = {'P': {'free': True,
           'value': None,  # unit: n/a
           'prior': {'category': 'normal', 'args': {'mu': 7.92008, 'sigma': 0.0013}  # 0.0013
                     }
           },
     't0': {'free': True,
            'value': None,  # unit: n/a
            'prior': {'category': 'uniform', 'args': {'vmin': 57423.26918-0.02765*100, 'vmax': 57423.26918+0.03515*20}  # vmin: 57423.26918-0.02765*5 vmax: 23.26918+0.03515*5    0.00184
                      }
            },
     'K': {'free': True,
           'value': None,  # unit: n/a
           'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 0.0400}
                     }
           },
     'secosw': {'free': True,
               'value': None,  # unit: n/a
               'prior': {'category': 'normal', 'args': {'mu': 0.0, 'sigma': 0.1, 'lims': [-1/sqrt(2), 1/sqrt(2)]}
                         }
               },
     'sesinw': {'free': True,
               'value': None,  # unit: n/a
               'prior': {'category': 'normal', 'args': {'mu': 0.0, 'sigma': 0.1, 'lims': [-1/sqrt(2), 1/sqrt(2)]}
                         }
               },
     }

c = {'P': {'free': True,
           'value': None,  # unit: n/a
           'prior': {'category': 'normal', 'args': {'mu': 11.9068, 'sigma': 0.0026}  # # mu: 11.9068  sigma:0.0026  0.0026
                     }
           },
     't0': {'free': True,
            'value': None,  # unit: n/a
            'prior': {'category': 'normal', 'args': {'mu': 57424.27004, 'sigma': 0.15345}  # mu: 57424.27004  sigma:0.15345 0.04
                      }
            },
     'K': {'free': True,
           'value': None,  # unit: n/a
           'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 0.015}  # 0.0048
                     }
           },
     'secosw': {'free': True,
               'value': None,  # unit: n/a
               'prior': {'category': 'normal', 'args': {'mu': 0.0, 'sigma': 0.1, 'lims': [-1/sqrt(2), 1/sqrt(2)]}
                         }
               },
     'sesinw': {'free': True,
               'value': None,  # unit: n/a
               'prior': {'category': 'normal', 'args': {'mu': 0.0, 'sigma': 0.1, 'lims': [-1/sqrt(2), 1/sqrt(2)]}
                         }
               },
     }

d = {'P': {'free': True,
           'value': None,  # unit: n/a
           'prior': {'category': 'normal', 'args': {'mu': 2.50856, 'sigma': 0.00041}
                     }
           },
     't0': {'free': True,
            'value': None,  # unit: n/a
            'prior': {'category': 'normal', 'args': {'mu': 56808.9207, 'sigma': 0.0086}
                      }
            },
     'K': {'free': True,
           'value': None,  # unit: n/a
           'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 0.010}
                     }
           },
     'secosw': {'free': True,
                'value': None,  # unit: n/a
                'prior': {'category': 'normal', 'args': {'mu': 0.0, 'sigma': 0.1, 'lims': [-1/sqrt(2), 1/sqrt(2)]}
                          }
                },
     'sesinw': {'free': True,
                'value': None,  # unit: n/a
                'prior': {'category': 'normal', 'args': {'mu': 0.0, 'sigma': 0.1, 'lims': [-1/sqrt(2), 1/sqrt(2)]}
                          }
                },
     }
