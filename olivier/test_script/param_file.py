#!/usr/bin/python
# -*- coding:  utf-8 -*-
# Parametrisation file of HD106315
from numpy import sqrt

# Parameters
# instruments
# instruments LC
K2 = {'def': {'jitter': {'free': True,
                         'value': None,  # unit: n/a
                         'prior': {'category': 'normal', 'args': {'mu': 0.0, 'sigma': 0.01}
                                   }
                         },
              },
      # By default all the datasets of an instrument are associated to def.
      # If you want to model some datasets with another instrument model copy paste it,
      # give it a new name and file the Dataset dict.
      'Dataset': {0: 'def', },
      }


# stars
A = {'rho': {'free': True,
             'value': None,  # unit: n/a
             'prior': {'category': 'normal', 'args': {'mu': 0.5197525024, 'sigma': 0.1}
                       }
             },
     }

# planets
b = {'P': {'free': True,
           'value': None,  # unit: n/a
           'prior': {'category': 'normal', 'args': {'mu': 9.55236, 'sigma': 8.8e-4}
                     }
           },
     'cosinc': {'free': True,
                'value': None,  # unit: n/a
                'prior': {'category': 'normal', 'args': {'mu': 0.0, 'sigma': 0.1, 'lims': [0., 1.]}
                          }
                },
     'tc': {'free': True,
            'value': None,  # unit: n/a
            'prior': {'category': 'normal', 'args': {'mu': 57586.5486, 'sigma': 2.9e-3}
                      }
            },
     'Rrat': {'free': True,
              'value': None,  # unit: n/a
              'prior': {'category': 'uniform', 'args': {'vmax': 0.5, 'vmin': 0.0}
                        }
              },
     'secosw': {'free': True,
                'value': None,  # unit: n/a
                'prior': {'category': 'normal', 'args': {'mu': 0.0, 'sigma': 0.05, 'lims': [-1 / sqrt(2), 1 / sqrt(2)]}
                          }
                },
     'sesinw': {'free': True,
                'value': None,  # unit: n/a
                'prior': {'category': 'normal', 'args': {'mu': 0.0, 'sigma': 0.05, 'lims': [-1 / sqrt(2), 1 / sqrt(2)]}
                          }
                },
     }

c = {'P': {'free': True,
           'value': None,  # unit: n/a
           'prior': {'category': 'normal', 'args': {'mu': 21.05704, 'sigma': 4.3e-4}
                     }
           },
     'cosinc': {'free': True,
                'value': None,  # unit: n/a
                'prior': {'category': 'normal', 'args': {'mu': 0.0, 'sigma': 0.1, 'lims': [0., 1.]}
                          }
                },
     'tc': {'free': True,
            'value': None,  # unit: n/a
            'prior': {'category': 'normal', 'args': {'mu': 57569.0173, 'sigma': 1.4e-3}
                      }
            },
     'Rrat': {'free': True,
              'value': None,  # unit: n/a
              'prior': {'category': 'uniform', 'args': {'vmax': 0.1, 'vmin': 0.0}
                        }
              },
     'secosw': {'free': True,
                'value': None,  # unit: n/a
                'prior': {'category': 'normal', 'args': {'mu': 0.0, 'sigma': 0.05, 'lims': [-1 / sqrt(2), 1 / sqrt(2)]}
                          }
                },
     'sesinw': {'free': True,
                'value': None,  # unit: n/a
                'prior': {'category': 'normal', 'args': {'mu': 0.0, 'sigma': 0.05, 'lims': [-1 / sqrt(2), 1 / sqrt(2)]}
                          }
                },
     }

# LDs
default = {'ldc1': {'free': True,
                    'value': None,  # unit: n/a
                    'prior': {'category': 'normal', 'args': {'mu': 0.3024, 'sigma': 0.0049}
                              }
                    },
           'ldc2': {'free': True,
                    'value': None,  # unit: n/a
                    'prior': {'category': 'uniform', 'args': {'vmax': 0.3057, 'vmin': 0.0018}
                              }
                    },
           }
