# Configuration file for the analysis of WASP-151.

###########
## Datasets
###########

# List of the paths to the dataset files that you want to use
l_dataset = ["LC_WASP-151_K2.txt",
             "LC_WASP-151_EulerCam.txt",
             "LC_WASP-151_EulerCam_1.txt",
             "LC_WASP-151_IAC80.txt",
             "LC_WASP-151_IAC80_1.txt",
             "LC_WASP-151_TRAPPIST.txt",
             "RV_WASP-151_SOPHIE.txt",
             "RV_WASP-151_CORALIE.txt",
             ]

##############################
## Instrument model definition
##############################
# Define which instrument model you want to use for each dataset
# By default each instrument is modeled by one instrument model which is used for all the datasets of this instrument
# This is imposed by the fact that below all datasets have the same instrument model short name 'inst'.
# If you want to model one dataset of an instrument with a different instrument model from the others change 'inst' into whatever else you want (for example 'inst0').
d_inst_model_def = {'LC': {'EulerCam': {'0': 'inst0', '1': 'inst1'},
                           'IAC80': {'0': 'inst0', '1': 'inst1'},
                           'K2': {'0': 'inst'},
                           'TRAPPIST': {'0': 'inst'}},
                    'RV': {'CORALIE': {'0': 'inst'}, 'SOPHIE': {'0': 'inst'}}}

####################################
## Model category definition
####################################
# Define the model category and the parameters of the model that are specfic to the model category.

# Available model categories are ['GravitionalGroups', 'GravitionalGroupsDynamic']
model_category = 'GravitionalGroups'

#########################
## Noise model definition
#########################
# Define which noise model you want to use for each instrument model
# By default the gaussian noise model is used for all the instrument models
# This is imposed by the fact that below all instrument models have 'gaussian' as entry.
# However there is other noise models available. Currently the list of possible noise model is ['gaussian', 'GP1D'].
# If you want to change the noise model used for a given instrument model, just change the value of its key.
d_noise_model_def = {'LC': {'EulerCam': {'inst0': 'gaussian', 'inst1': 'gaussian'},
                            'IAC80': {'inst0': 'gaussian', 'inst1': 'gaussian'},
                            'K2': {'inst': 'GP1D'},
                            'TRAPPIST': {'inst': 'gaussian'}},
                     'RV': {'CORALIE': {'inst': 'GP1D'}, 'SOPHIE': {'inst': 'GP1D'}}}
