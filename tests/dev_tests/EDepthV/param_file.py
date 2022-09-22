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
                 'inst5': {'contam': {'duplicate': None,
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
                 'inst6': {'contam': {'duplicate': None,
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
                 'inst7': {'contam': {'duplicate': None,
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
                 'inst8': {'contam': {'duplicate': None,
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
                 'inst9': {'contam': {'duplicate': None,
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
                 'inst10': {'contam': {'duplicate': None,
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
                 'inst11': {'contam': {'duplicate': None,
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
                 'inst12': {'contam': {'duplicate': None,
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
                 'inst13': {'contam': {'duplicate': None,
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
                 'inst14': {'contam': {'duplicate': None,
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
                 'inst15': {'contam': {'duplicate': None,
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
                 'inst16': {'contam': {'duplicate': None,
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
                 'inst17': {'contam': {'duplicate': None,
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
                 'inst18': {'contam': {'duplicate': None,
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
                 'inst19': {'contam': {'duplicate': None,
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
                 'Dataset': {100: 'inst0', 101: 'inst1', 102: 'inst2', 103: 'inst3', 104: 'inst4', 105: 'inst5', 106: 'inst6', 107: 'inst7', 108: 'inst8', 109: 'inst9', 110: 'inst10', 111: 'inst11', 112: 'inst12', 113: 'inst13', 114: 'inst14', 115: 'inst15', 116: 'inst16', 117: 'inst17', 118: 'inst18', 119: 'inst19', },
                 },

      }

# instruments IND-ROLL
INDROLL = {'CHEOPS': {'inst': {                               },
                      'Dataset': {100: 'inst', 101: 'inst', 102: 'inst', 103: 'inst', 104: 'inst', 105: 'inst', 106: 'inst', 107: 'inst', 108: 'inst', 109: 'inst', 110: 'inst', 111: 'inst', 112: 'inst', 113: 'inst', 114: 'inst', 115: 'inst', 116: 'inst', 117: 'inst', 118: 'inst', 119: 'inst', },
                      },

           }

# instruments IND-CX
INDCX = {'CHEOPS': {'inst': {                             },
                    'Dataset': {100: 'inst', 101: 'inst', 102: 'inst', 103: 'inst', 104: 'inst', 105: 'inst', 106: 'inst', 107: 'inst', 108: 'inst', 109: 'inst', 110: 'inst', 111: 'inst', 112: 'inst', 113: 'inst', 114: 'inst', 115: 'inst', 116: 'inst', 117: 'inst', 118: 'inst', 119: 'inst', },
                    },

         }

# instruments IND-CY
INDCY = {'CHEOPS': {'inst': {                             },
                    'Dataset': {100: 'inst', 101: 'inst', 102: 'inst', 103: 'inst', 104: 'inst', 105: 'inst', 106: 'inst', 107: 'inst', 108: 'inst', 109: 'inst', 110: 'inst', 111: 'inst', 112: 'inst', 113: 'inst', 114: 'inst', 115: 'inst', 116: 'inst', 117: 'inst', 118: 'inst', 119: 'inst', },
                    },

         }

# instruments IND-SMEAR
INDSMEAR = {'CHEOPS': {'inst': {                                },
                       'Dataset': {100: 'inst', 101: 'inst', 102: 'inst', 103: 'inst', 104: 'inst', 105: 'inst', 106: 'inst', 107: 'inst', 108: 'inst', 109: 'inst', 110: 'inst', 111: 'inst', 112: 'inst', 113: 'inst', 114: 'inst', 115: 'inst', 116: 'inst', 117: 'inst', 118: 'inst', 119: 'inst', },
                       },

            }

# instruments IND-TF
INDTF = {'CHEOPS': {'inst': {                             },
                    'Dataset': {100: 'inst', 101: 'inst', 102: 'inst', 103: 'inst', 104: 'inst', 105: 'inst', 106: 'inst', 107: 'inst', 108: 'inst', 109: 'inst', 110: 'inst', 111: 'inst', 112: 'inst', 113: 'inst', 114: 'inst', 115: 'inst', 116: 'inst', 117: 'inst', 118: 'inst', 119: 'inst', },
                    },

         }

# instruments IND-BKG
INDBKG = {'CHEOPS': {'inst': {                              },
                     'Dataset': {100: 'inst', 101: 'inst', 102: 'inst', 103: 'inst', 104: 'inst', 105: 'inst', 106: 'inst', 107: 'inst', 108: 'inst', 109: 'inst', 110: 'inst', 111: 'inst', 112: 'inst', 113: 'inst', 114: 'inst', 115: 'inst', 116: 'inst', 117: 'inst', 118: 'inst', 119: 'inst', },
                     },

          }

# instruments IND-DARK
INDDARK = {'CHEOPS': {'inst': {                               },
                      'Dataset': {100: 'inst', 101: 'inst', 102: 'inst', 103: 'inst', 104: 'inst', 105: 'inst', 106: 'inst', 107: 'inst', 108: 'inst', 109: 'inst', 110: 'inst', 111: 'inst', 112: 'inst', 113: 'inst', 114: 'inst', 115: 'inst', 116: 'inst', 117: 'inst', 118: 'inst', 119: 'inst', },
                      },

           }

# instruments IND-CONTA
INDCONTA = {'CHEOPS': {'inst': {                                },
                       'Dataset': {100: 'inst', 101: 'inst', 102: 'inst', 103: 'inst', 104: 'inst', 105: 'inst', 106: 'inst', 107: 'inst', 108: 'inst', 109: 'inst', 110: 'inst', 111: 'inst', 112: 'inst', 113: 'inst', 114: 'inst', 115: 'inst', 116: 'inst', 117: 'inst', 118: 'inst', 119: 'inst', },
                       },

            }

# stars
A = {     }

# planets
b = {'P': {'duplicate': None,
           'free': True,
           'value': None,  # unit: None
           'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                     'joint_prior_ref': None
                     }
           },
     'tic': {'duplicate': None,
             'free': True,
             'value': None,  # unit: None
             'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                       'joint_prior_ref': None
                       }
             },
     'A': {'duplicate': None,
           'free': True,
           'value': None,  # unit: unit of LC data
           'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                     'joint_prior_ref': None
                     }
           },
     'Phi': {'duplicate': None,
             'free': True,
             'value': None,  # unit: radians
             'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                       'joint_prior_ref': None
                       }
             },
     'Foffset': {'duplicate': None,
                 'free': True,
                 'value': None,  # unit: unit of LC data
                 'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                           'joint_prior_ref': None
                           }
                 },
     'A2': {'duplicate': None,
            'free': True,
            'value': None,  # unit: unit of LC data
            'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                      'joint_prior_ref': None
                      }
            },
     'A19': {'duplicate': None,
             'free': True,
             'value': None,  # unit: unit of LC data
             'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                       'joint_prior_ref': None
                       }
             },
     'A16': {'duplicate': None,
             'free': True,
             'value': None,  # unit: unit of LC data
             'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                       'joint_prior_ref': None
                       }
             },
     'A3': {'duplicate': None,
            'free': True,
            'value': None,  # unit: unit of LC data
            'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                      'joint_prior_ref': None
                      }
            },
     'A17': {'duplicate': None,
             'free': True,
             'value': None,  # unit: unit of LC data
             'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                       'joint_prior_ref': None
                       }
             },
     'A4': {'duplicate': None,
            'free': True,
            'value': None,  # unit: unit of LC data
            'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                      'joint_prior_ref': None
                      }
            },
     'A11': {'duplicate': None,
             'free': True,
             'value': None,  # unit: unit of LC data
             'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                       'joint_prior_ref': None
                       }
             },
     'A12': {'duplicate': None,
             'free': True,
             'value': None,  # unit: unit of LC data
             'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                       'joint_prior_ref': None
                       }
             },
     'A9': {'duplicate': None,
            'free': True,
            'value': None,  # unit: unit of LC data
            'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                      'joint_prior_ref': None
                      }
            },
     'A8': {'duplicate': None,
            'free': True,
            'value': None,  # unit: unit of LC data
            'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                      'joint_prior_ref': None
                      }
            },
     'A1': {'duplicate': None,
            'free': True,
            'value': None,  # unit: unit of LC data
            'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                      'joint_prior_ref': None
                      }
            },
     'A10': {'duplicate': None,
             'free': True,
             'value': None,  # unit: unit of LC data
             'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                       'joint_prior_ref': None
                       }
             },
     'A7': {'duplicate': None,
            'free': True,
            'value': None,  # unit: unit of LC data
            'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                      'joint_prior_ref': None
                      }
            },
     'A14': {'duplicate': None,
             'free': True,
             'value': None,  # unit: unit of LC data
             'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                       'joint_prior_ref': None
                       }
             },
     'A6': {'duplicate': None,
            'free': True,
            'value': None,  # unit: unit of LC data
            'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                      'joint_prior_ref': None
                      }
            },
     'A15': {'duplicate': None,
             'free': True,
             'value': None,  # unit: unit of LC data
             'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                       'joint_prior_ref': None
                       }
             },
     'A5': {'duplicate': None,
            'free': True,
            'value': None,  # unit: unit of LC data
            'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                      'joint_prior_ref': None
                      }
            },
     'A13': {'duplicate': None,
             'free': True,
             'value': None,  # unit: unit of LC data
             'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 1.0},
                       'joint_prior_ref': None
                       }
             },
     'A18': {'duplicate': None,
             'free': True,
             'value': None,  # unit: unit of LC data
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
