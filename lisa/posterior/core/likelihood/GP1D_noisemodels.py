"""Provides the GP1D_Noise_Models classes.

The instance of GP1D_Noise_Models class is used to store the informations of all the GP1D noise models
that are going to be defined in the Model instance.
It stores the Core_GP1DModel subclasses.
There is only on GP1D_Noise_Models instance in a Model instance
"""

from loguru import logger
from george.kernels import ExpSquaredKernel, ExpSine2Kernel
from george import GP
import numpy as np
from collections import defaultdict, Counter, OrderedDict
import os
from pprint import pformat
# from collections import OrderedDict

# from ..model.celestial_bodies import Star
from .core_noise_model import Core_Noise_Model
from ....tools.miscellaneous import spacestring_like
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
        # By default all instruments of a given inst_fullcat are modeled by one QPGeorge model.
        for inst_fullcat, l_instmod in self.get_instmod(sortby_instfullcat=True).items():
            model_name = f"{inst_fullcat}"
            for instmod in l_instmod:
                self._models_config['model4instrument'][instmod.full_name] = model_name
            self._define_model(model_name=model_name, model_category='QPGeorge', dico_config_model=None, overwrite=False)
    
    def _define_model(self, model_name, model_category, dico_config_model=None, overwrite=False):
        """Define the model for the planet

        Arguments
        ---------
        planet_name                     : str
            Name of the planet for which you are defining the model
        model_category                  : str
            Catergory of the models
        dico_config_model               : dict
            Dictionary provide arguments for the model if needed.
        overwrite                       : bool
            Wheter or not you wish to overwrite if the model is already defined
        """
        if not(overwrite) and (model_name in self._models_config["model_definitions"]):
            raise ValueError(f"A model of name {model_name} already exists and overwrite is False.")
        if not(self._is_available_model_category(model_category=model_category)):
            raise ValueError(f"{model_category} is not in the list of available model categories ({self.l_available_model_category}).")
        (self._models_config["model_definitions"]
         [model_name]) = self.model_classes[model_category](model_name=model_name, model_instance=self.model_instance, dico_config_model=dico_config_model)


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
        
    def __config_var_exist_gp(self, dico_config_file):
        return 'GP1D_models' in dico_config_file

    def __load_config_var_content_gp(self, dico_config_file, **kwargs):
        GP1D_models_config = dico_config_file['GP1D_models']
        assert isinstance(GP1D_models_config, dict)
        if set(GP1D_models_config.keys()) != set(['model4instrument', 'model_definitions']):
            raise ValueError(f"The keys of the 'GP1D_models' dictionary should be ['model4instrument', 'model_definitions']. You provided {set(GP1D_models_config.keys())}")
        if set(GP1D_models_config['model4instrument'].keys()) != set(self.l_inst_model_fullname):
            raise ValueError(f"The list of instrument models using a GP1D noise model is {self.l_inst_model_fullname}. It should be the same as the list of instrument model full name in GP1D_models['model4instrument'] ({GP1D_models_config['model4instrument']})")
        if set(GP1D_models_config['model4instrument'].values()) != set(GP1D_models_config['model_definitions'].keys()):
            raise ValueError(f"The list of GP1D model names provided in GP1D_models['model4instrument'] should match the list of the names of the GP1D models defined in GP1D_models['model_definitions'].")
        # Clean the GP1D Container of model instance
        for GP1D_model_name in self.model_instance.l_GP1D_fullname:
            if GP1D_model_name not in GP1D_models_config['model_definitions'].keys():
                self.model_instance.rm_a_GP1D(name=GP1D_model_name)
        # load the config of the GP1D models defined in the configuration
        for GP1D_model_name in GP1D_models_config['model_definitions']:
            model_category = GP1D_models_config['model_definitions'][GP1D_model_name].pop("category")
            self._define_model(model_name=GP1D_model_name, model_category=model_category, dico_config_model=GP1D_models_config['model_definitions'][GP1D_model_name], overwrite=True)
    
    #############################################
    # Dealing with the parameters/parametrisation
    #############################################

    def set_parametrisation(self):
        l_model_done = []
        for instmodfullname in self.l_inst_model_fullname:  # l_inst_model_fullname is defined in Core_Noise_Model
            GP1D_config = self.get_model(inst_model_fullname=instmodfullname)
            if GP1D_config not in l_model_done:
                GP1D_config.create_parameters_and_set_main()
    
