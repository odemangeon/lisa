# Define which noise model you want to use for each instrument model
# By default the gaussian noise model is used for all the instrument models# This is imposed by the fact that below all instrument models have 'gaussian' as entry.
# However there is other noise models available. Currently the list of possible noise model is ['gaussian', 'GP1D'].
# If you want to change the noise model used for a given instrument model, just change the value of its key.
RV = {'CORALIE': {'inst': 'GP1D'}, 'SOPHIE': {'inst': 'GP1D'}}
LC = {'EulerCam': {'inst0': 'gaussian', 'inst1': 'gaussian'},
      'IAC80': {'inst0': 'GP1D', 'inst1': 'gaussian'},
      'K2': {'inst': 'gaussian'},
      'TRAPPIST': {'inst': 'GP1D'}}
