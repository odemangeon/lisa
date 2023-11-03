"""Provides the GP1D_Noise_Models classes.

The instance of GP1D_Noise_Models class is used to store the informations of all the GP1D noise models
that are going to be defined in the Model instance.
It stores the Core_GP1DModel subclasses.
There is only on GP1D_Noise_Models instance in a Model instance
"""

from loguru import logger
from george.kernels import ExpSquaredKernel, ExpSine2Kernel
from george import GP
from numpy import concatenate, sqrt
import numpy as np
from collections import defaultdict, Counter, OrderedDict
import os
from os.path import basename
from pprint import pformat
# from collections import OrderedDict

# from ..model.celestial_bodies import Star
from ...exoplanet.dataset_and_instrument.rv import RV_inst_cat
from ...exoplanet.dataset_and_instrument.lc import LC_inst_cat
from ..parameter import Parameter
from .core_noise_model import Core_Noise_Model
from ..dataset_and_instrument.indicator import IND_inst_cat
from ....tools.miscellaneous import spacestring_like
from ....tools.human_machine_interface.QCM import QCM_utilisateur
from ....tools.function_from_text_toolbox import FunctionBuilder
# from ....tools.function_w_doc import DocFunction
from .GP1D_noisemodelconfiguration import QPGeorgeModel, QPCGeorgeModel, QPCeleriteModel, RotationCeleriteModel, SHOCeleriteModel, Matern32Model


class GP1D_Noise_Models(Core_Noise_Model):
    """docstring for GP1D_Noise_Models."""

    __noise_cat__ = "GP1D"
    __has_GP__ = True
    __has_jitter__ = True

    __l_model_class__ = [QPGeorgeModel, QPCGeorgeModel, QPCeleriteModel, RotationCeleriteModel, SHOCeleriteModel]

    ################
    # Main functions
    ################
    def __init__(self, model_instance, run_folder, config_file):
        super(GP1D_Noise_Models, self).__init__(model_instance=model_instance, run_folder=run_folder, config_file=config_file)
        self._models_config = self._init_model_config()
        self._define_default_model()

    @property
    def dict2print(self):
        """Used to print the content in the parametrisation file."""
        dict2print = self._models_config.copy()
        dict2print['model_definitions'] = dict2print['model_definitions'].copy()
        for model_name in dict2print['model_definitions']:
            dict2print['model_definitions'][model_name] = dict2print['model_definitions'][model_name].dict2print
        return dict2print
    
    def get_model(self, inst_model_fullname):
        """Get the model for a given instrument model full name.
        """
        if inst_model_fullname not in self.l_inst_model_fullname:
            raise ValueError(f"The instrument model name provided ({inst_model_fullname}) doesn't exist or is not defined to be modeled with a gaussian noise model")
        model_name = self._models_config['model4instrument'][inst_model_fullname]
        return self._models_config['model_definitions'][model_name]
    
    ################################
    # Dealing with the configuration
    ################################

    # Required by the __init__ method
    #################################

    def _init_model_config(self):
        return  {'model4instrument': {instmodfullname: '' for instmodfullname in self.l_inst_model_fullname},
                 'model_definitions': {},
                 }

    def _define_default_model(self):
        # TODO: By default all instruments of a given inst_fullcat are modeled by one QPGeorge model.
        raise NotImplementedError

    # Configure the gaussian noise models
    #####################################
    def _configure_noisemodcat_model(self, **kwargs):
        """Apply the parametrisation for the noise model

        This method is called by Core_Model._configure_noisemodel
        """
        self._load_config(config2load='gp')

    # Function that get the function required by  ConfigFileAttr._load_config
    #########################################################################

    def _get_function_config(self, function_type, config2load):
        if function_type == 'add_default_config':
            if config2load == 'gp':
                return self.__add_default_config_var_gp
        elif function_type == 'check_config_exists':
            if config2load == 'gp':
                return self.__config_var_exist_gp
        elif function_type == 'load_config_content':
            if config2load == 'gp':
                return self.__load_config_var_content_gp
        raise ValueError(f"Either the function_type (you provided {function_type}) or the config2load (you provided {config2load}) is invalid")

    # Methods for the noise model definition part of the config file
    ################################################################
    def __add_default_config_var_gp(self, file):
        file.write("\n# GP1D noise models"
                   "\n###################\n"
                   )
        tab = spacestring_like('GP1D_models' + " = ")
        file.write("{var} = {content}\n".format(var='GP1D_models',
                                                content=pformat(self.dict2print, compact=True).replace('\n', f'\n{tab}')
                                                )
                   )
        
    def __config_var_exist_gaussian(self, dico_config_file):
        return 'GP1D_models' in dico_config_file

    def __load_config_var_content_gaussian(self, dico_config_file, **kwargs):
        GP1D_models_config = dico_config_file['gaussian_models']
        assert isinstance(GP1D_models_config, dict)
        raise NotImplementedError
    

    
