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

    __l_model_class__ = [GaussianModel]

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
    
    ################################
    # Dealing with the configuration
    ################################

    # Init the configuration dictionary
    ###################################

    def _init_model_config(self):
        return {instmodfullname: GaussianModel(model_name='', instrument=self.model_instance.instruments[instmodfullname], dico_config_model=None) 
                for instmodfullname in self.l_inst_model_fullname
                }

    # Configure the gaussian noise models
    #####################################
    def _configure_noisemodcat_model(self, **kwargs):
        """Apply the parametrisation for the noise model

        This method is called by Core_Model._configure_noisemodel
        """
        self._load_config(config2load='gaussian')

    # Function that get the function required by  ConfigFileAttr._load_config
    #########################################################################

    def _get_function_config(self, function_type, config2load):
        if function_type == 'add_default_config':
            if config2load == 'gaussian':
                return self.__add_default_config_var_gaussian
        elif function_type == 'check_config_exists':
            if config2load == 'gaussian':
                return self.__config_var_exist_gaussian
        elif function_type == 'load_config_content':
            if config2load == 'gaussian':
                return self.__load_config_var_content_gaussian
        raise ValueError(f"Either the function_type (you provided {function_type}) or the config2load (you provided {config2load}) is invalid")

    # Methods for the noise model definition part of the config file
    ################################################################
    def __add_default_config_var_gaussian(self, file):
        file.write("\n# Gaussian noise models"
                   "\n#######################\n"
                   )
        tab = spacestring_like('gaussian_models' + " = ")
        file.write("{var} = {content}\n".format(var='gaussian_models',
                                                content=pformat(self.dict2print, compact=True).replace('\n', f'\n{tab}')
                                                )
                   )
        
    def __config_var_exist_gaussian(self, dico_config_file):
        return 'gaussian_models' in dico_config_file

    def __load_config_var_content_gaussian(self, dico_config_file, **kwargs):
        gaussian_models_config = dico_config_file['gaussian_models']
        assert isinstance(gaussian_models_config, dict)
        assert set(gaussian_models_config.keys()) == set(self.l_inst_model_fullname)
        for instmod_fullname in gaussian_models_config:
            gaussian_model = self.get_model(inst_model_fullname=instmod_fullname)
            gaussian_model.load_config(dico_config=gaussian_models_config[instmod_fullname])