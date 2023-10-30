"""
noise_model module.

The objective of this module is to define the Core_NoiseModel Class and the standard noise models.

@DONE:
    -

@TODO:
    -
"""

from .core_noise_model import Core_Noise_Model
from .gaussian_noisemodelconfiguration import GaussianModel


class Gaussian_Noise_Models(Core_Noise_Model):
    """A instance of this class will be created in the Model instance to store the configuration
    of the gaussian noise models used
    """

    __noise_cat__ = "gaussian"
    __has_GP__ = False
    __has_jitter__ = True

    ################
    # Main functions
    ################
    def __init__(self, model_instance, run_folder, config_file):
        super(Gaussian_Noise_Models, self).__init__(model_instance=model_instance, run_folder=run_folder, config_file=config_file)
        self._models_config = self._init_model_config()

    @property
    def dict2print(self):
        """Used to print the content in the parametrisation file."""
        dict2print = self._models_config.copy()
        for inst_model_fullname in dict2print:
            dict2print[inst_model_fullname] = dict2print[inst_model_fullname].dict2print
        return dict2print
    
    def get_model(self, inst_model_fullname):
        """Get the model for a given instrument model full name.
        """
        if inst_model_fullname not in self.l_inst_model_fullname:
            raise ValueError(f"The instrument model name provided ({inst_model_fullname}) doesn't exist or is not defined to be modeled with a gaussian noise model")
        return self._models_config[inst_model_fullname]
    
    ##############################
    # Required by the main methods
    ##############################

    # Required by the __init__ method
    #################################

    def _init_model_config(self):
        return {instmodfullname: GaussianModel(model_name='', instrument=self.model_instance.instruments[instmodfullname], dico_config_model=None) 
                for instmodfullname in self.l_inst_model_fullname
                }

    

        

