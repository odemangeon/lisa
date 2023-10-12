# Define which instrument model you want to use for each dataset
# By default each instrument is modeled by one instrument model which is used for all the datasets of this instrument# This is imposed by the fact that below all datasets have the same instrument model short name 'inst'.
# If you want to model one dataset of an instrument with a different instrument model from the others change 'inst' into whatever else you want (for example 'inst0')
LC = {'EulerCam': {0: 'inst0', 1: 'inst1'},
      'IAC80': {0: 'inst0', 1: 'inst1'},
      'K2': {0: 'inst'},
      'TRAPPIST': {0: 'inst'}}
RV = {'CORALIE': {0: 'inst'}, 'SOPHIE': {0: 'inst'}}
