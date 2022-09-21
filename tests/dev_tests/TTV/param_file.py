#!/usr/bin/python
# -*- coding:  utf-8 -*-
# Parametrisation file of WASP-76
import numpy as np

# Parameters
# instruments
# instruments LC
LC = {'CHEOPS': {'instPC0': {'contam': {'duplicate': None,
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
                 'instPC1': {'contam': {'duplicate': None,
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
                 'instPC2': {'contam': {'duplicate': None,
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
                 'inst0': {'contam': {'duplicate': None,
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
                 'Dataset': {100: 'inst0', 101: 'inst1', 102: 'inst2', 103: 'inst3', 104: 'inst4', 105: 'inst5', 106: 'inst6', 107: 'inst7', 108: 'inst8', 109: 'inst9', 110: 'inst10', 111: 'inst11', 112: 'inst12', 113: 'inst13', 114: 'inst14', 115: 'inst15', 116: 'inst16', 117: 'inst17', 118: 'inst18', 119: 'inst19', 0: 'instPC0', 1: 'instPC1', 2: 'instPC2'},
                 },

      }

# instruments IND-ROLL
INDROLL = {'CHEOPS': {'inst': {},
                      'Dataset': {0: 'inst', 1: 'inst', 2: 'inst', 100: 'inst', 101: 'inst', 102: 'inst', 103: 'inst', 104: 'inst', 105: 'inst', 106: 'inst', 107: 'inst', 108: 'inst', 109: 'inst', 110: 'inst', 111: 'inst', 112: 'inst', 113: 'inst', 114: 'inst', 115: 'inst', 116: 'inst', 117: 'inst', 118: 'inst', 119: 'inst', 0: 'inst', 1: 'inst', 2: 'inst'},
                      },

           }

# instruments IND-CX
INDCX = {'CHEOPS': {'inst': {},
                    'Dataset': {0: 'inst', 1: 'inst', 2: 'inst', 100: 'inst', 101: 'inst', 102: 'inst', 103: 'inst', 104: 'inst', 105: 'inst', 106: 'inst', 107: 'inst', 108: 'inst', 109: 'inst', 110: 'inst', 111: 'inst', 112: 'inst', 113: 'inst', 114: 'inst', 115: 'inst', 116: 'inst', 117: 'inst', 118: 'inst', 119: 'inst', 0: 'inst', 1: 'inst', 2: 'inst'},
                    },

         }

# instruments IND-CY
INDCY = {'CHEOPS': {'inst': {},
                    'Dataset': {0: 'inst', 1: 'inst', 2: 'inst', 100: 'inst', 101: 'inst', 102: 'inst', 103: 'inst', 104: 'inst', 105: 'inst', 106: 'inst', 107: 'inst', 108: 'inst', 109: 'inst', 110: 'inst', 111: 'inst', 112: 'inst', 113: 'inst', 114: 'inst', 115: 'inst', 116: 'inst', 117: 'inst', 118: 'inst', 119: 'inst', 0: 'inst', 1: 'inst', 2: 'inst'},
                    },

         }

# instruments IND-SMEAR
INDSMEAR = {'CHEOPS': {'inst': {},
                       'Dataset': {0: 'inst', 1: 'inst', 2: 'inst', 100: 'inst', 101: 'inst', 102: 'inst', 103: 'inst', 104: 'inst', 105: 'inst', 106: 'inst', 107: 'inst', 108: 'inst', 109: 'inst', 110: 'inst', 111: 'inst', 112: 'inst', 113: 'inst', 114: 'inst', 115: 'inst', 116: 'inst', 117: 'inst', 118: 'inst', 119: 'inst', 0: 'inst', 1: 'inst', 2: 'inst'},
                       },

            }

# instruments IND-TF
INDTF = {'CHEOPS': {'inst': {},
                    'Dataset': {0: 'inst', 1: 'inst', 2: 'inst', 100: 'inst', 101: 'inst', 102: 'inst', 103: 'inst', 104: 'inst', 105: 'inst', 106: 'inst', 107: 'inst', 108: 'inst', 109: 'inst', 110: 'inst', 111: 'inst', 112: 'inst', 113: 'inst', 114: 'inst', 115: 'inst', 116: 'inst', 117: 'inst', 118: 'inst', 119: 'inst', 0: 'inst', 1: 'inst', 2: 'inst'},
                    },

         }

# instruments IND-BKG
INDBKG = {'CHEOPS': {'inst': {},
                     'Dataset': {0: 'inst', 1: 'inst', 2: 'inst', 100: 'inst', 101: 'inst', 102: 'inst', 103: 'inst', 104: 'inst', 105: 'inst', 106: 'inst', 107: 'inst', 108: 'inst', 109: 'inst', 110: 'inst', 111: 'inst', 112: 'inst', 113: 'inst', 114: 'inst', 115: 'inst', 116: 'inst', 117: 'inst', 118: 'inst', 119: 'inst', 0: 'inst', 1: 'inst', 2: 'inst'},
                     },

          }

# instruments IND-DARK
INDDARK = {'CHEOPS': {'inst': {},
                      'Dataset': {0: 'inst', 1: 'inst', 2: 'inst', 100: 'inst', 101: 'inst', 102: 'inst', 103: 'inst', 104: 'inst', 105: 'inst', 106: 'inst', 107: 'inst', 108: 'inst', 109: 'inst', 110: 'inst', 111: 'inst', 112: 'inst', 113: 'inst', 114: 'inst', 115: 'inst', 116: 'inst', 117: 'inst', 118: 'inst', 119: 'inst', 0: 'inst', 1: 'inst', 2: 'inst'},
                      },

           }

# instruments IND-CONTA
INDCONTA = {'CHEOPS': {'inst': {},
                       'Dataset': {0: 'inst', 1: 'inst', 2: 'inst', 100: 'inst', 101: 'inst', 102: 'inst', 103: 'inst', 104: 'inst', 105: 'inst', 106: 'inst', 107: 'inst', 108: 'inst', 109: 'inst', 110: 'inst', 111: 'inst', 112: 'inst', 113: 'inst', 114: 'inst', 115: 'inst', 116: 'inst', 117: 'inst', 118: 'inst', 119: 'inst', 0: 'inst', 1: 'inst', 2: 'inst'},
                       },

            }

# stars
A = {'rho': {'duplicate': None,
             'free': True,
             'value': None,  # unit: Solar density
             'prior': {'category': 'normal', 'args': {'mu': 0.26943233617690693, 'sigma': 0.03294569900343486, 'lims': [0, np.inf]},
                       'joint_prior_ref': None
                       }
             },
     }

# planets
b = {'P': {'duplicate': None,
           'free': True,
           'value': None,  # unit: [time of the RV/LC data]
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
     'tic': {'duplicate': None,
             'free': True,
             'value': None,  # unit: [time of the RV/LC data]
             'prior': {'category': 'normal', 'args': {'mu': 859.81968, 'sigma': 1 / 24, 'sigma_lims': [3, 3]},  # 58080.626165 - 57000 = 1080.626165 From TEP cat (from Ehrenreich+2020)
                       'joint_prior_ref': None
                       }
             },
     'Rrat': {'duplicate': None,
              'free': True,
              'value': None,  # unit: w/o unit
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
     'APCcos1': {'duplicate': None,
                 'free': True,
                 'value': None,  # unit: None
                 'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 500e-6},
                           'joint_prior_ref': None
                           }
                 },
     'PhiPCcos1': {'duplicate': None,
                   'free': True,
                   'value': None,  # unit: None
                   'prior': {'category': 'uniform', 'args': {'vmin': np.pi / 2, 'vmax': 3 * np.pi / 2},
                             'joint_prior_ref': None
                             }
                   },
     'FoffsetPCcos1': {'duplicate': None,
                       'free': True,
                       'value': None,  # unit: None
                       'prior': {'category': 'uniform', 'args': {'vmin': 0.0, 'vmax': 500e-6},
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
