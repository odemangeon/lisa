"""Provides the Core_GP1DModel, QPGeorgeModel, QPCGeorgeModel, QPCeleriteModel, RotationCeleriteModel

The instance of the subclasses Core_GP1DModel is use to store the configuration of 1 GP1D model used in the Model instance.
It contain the configuration of a GP1D instance.
These instances are stored in GP1D_Noise_Models
There can be several Core_GP1DModel subclass instances in a Model instances.

The other classes are subclassed of Core_GP1DModel and are each used to store the configuration of 1 specific type of GP1D model.
There can be several instances of each of these subclasses in a Model instance.
Beside the configuration these subclasses also provide the function to create the likelihood and GP simulators
"""

from ..core_1modelconfiguration import Core_1ModelConfig
from .GP1D import GP1D


class Core_GP1DModel(Core_1ModelConfig):

    # Define the likelihood computation and GP simualtor functions

    ################
    # Main functions
    ################

    def __init__(self, model_name, model_instance, dico_config_model=None):
        super(Core_GP1DModel, self).__init__(model_name=model_name)
        if model_name in model_instance.l_GP1D_fullname:
            GP1D_paramcontainer = model_instance.GP1Ds[model_name]
        else:
            GP1D_paramcontainer = GP1D(name=model_name)
            model_instance.add_a_GP1D(GP=GP1D_paramcontainer, name=model_name)
        self._object_categories = {'GP': GP1D_paramcontainer}  # This are parameter containers required by the model that host the model parameters
        self.load_config(dico_config=dico_config_model)

    def create_parameters_and_set_main(self, object_category=None):
        super(Core_GP1DModel, self).create_parameters_and_set_main(object_category=object_category)

    ######################
    # Convenience function
    ######################

    @property
    def GP(self):
        """GP param container"""
        return self.object_categories["GP"]


class QPGeorgeModel(Core_GP1DModel):

    __category__ = "QPGeorge"

    ############################################################
    # Dealing with the parametrisation, param_extension and args
    ############################################################

    def _set_parametrisation(self, parametrisation=None):
        """ """
        self.parametrisation.update({"log10": {param_basename: False for param_basename in self._get_l_parameter_basename_GP()}})
        if parametrisation is not None:
            for key in parametrisation:
                if key not in ["log10"]:
                    raise ValueError(f"The only possible keys to the 'parametrisation' are 'log10'. You provided {key}.")
                if key == "log10":
                    if not(isinstance(parametrisation[key], dict)):
                        raise ValueError(f"'log10' in parametrisation should be a dictionary. You provided a {type(parametrisation[key])}.")
                    for param_basename in parametrisation[key]:
                        if param_basename not in self._get_l_parameter_basename_GP():
                            raise ValueError(f"The only possible keys to the 'log10' dictionary are {self._get_l_parameter_basename_GP()}. You provided {key}.")
                    if not(isinstance(parametrisation[key][param_basename], bool)):
                        raise ValueError(f"Value of parametrisation[{key}][{param_basename}] should be a bool (got {parametrisation[key][param_basename]})")
                    self.parametrisation[key][param_basename] = parametrisation[key][param_basename]
        super(QPGeorgeModel, self)._set_parametrisation(parametrisation=parametrisation)

    ############################################################
    ## Dealing with the parameters and their names for the model
    ############################################################

    # Dealing with parameter basenames
    ##################################

    def _get_function_get_l_parameter_basename(self, object_category):
        if object_category == 'GP':
            return self._get_l_parameter_basename_GP
        super(QPGeorgeModel, self)._get_function_get_l_parameter_basename(object_category=object_category)
    
    def _get_function_get_kwargs_4_get_l_parameter_basename(self, object_category):
        if object_category == 'GP':
            return self._get_kwargs_4_get_l_parameter_basename_default
        super(QPGeorgeModel, self)._get_function_get_kwargs_4_get_l_parameter_basename(object_category=object_category)
    
    def _get_l_parameter_basename_GP(self):
        return ['A', 'P', 'tau', 'gamma']

    # Dealing with parameter names
    ##############################

    def _get_function_get_parameter_name(self, object_category):
        if object_category == 'GP':
            return self._get_parameter_name_GP
        super(QPGeorgeModel, self)._get_function_get_parameter_name(object_category=object_category)
    
    def _get_function_get_kwargs_4_get_parameter_name(self, object_category):
        if object_category == 'GP':
            return self._get_kwargs_4_get_parameter_name_default
        super(QPGeorgeModel, self)._get_function_get_kwargs_4_get_parameter_name(object_category=object_category)

    def _get_parameter_name_GP(self, param_basename, object_category):
        param_name = param_basename
        if self.log10(param_basename=param_basename):
            param_name = 'log10' + param_name            
        return f"{param_name}{self._get_param_extension(param_basename=param_basename, object_category=object_category)}"
    
    # Deal with creating parameters
    ###############################

    def _get_function_create_parameter(self, object_category):
        if object_category == 'GP':
            return self._create_parameter_default
        super(QPGeorgeModel, self)._get_function_create_parameter(object_category=object_category)

        
    def _get_function_get_kwargs_4_create_parameter(self, object_category):
        if object_category == 'GP':
            return self._get_kwargs_4_create_parameter_default
        super(QPGeorgeModel, self)._get_function_get_kwargs_4_create_parameter(object_category=object_category)

    # Deal with getting parameter
    #############################

    def _get_function_get_parameter(self, object_category):
        if object_category == 'GP':
            return self._get_parameter_default
        super(QPGeorgeModel, self)._get_function_get_parameter(object_category=object_category)

        
    def _get_function_get_kwargs_4_get_parameter(self, object_category):
        if object_category == 'GP':
            return self._get_kwargs_4_get_parameter_default
        super(QPGeorgeModel, self)._get_function_get_kwargs_4_get_parameter(object_category=object_category)

    ######################
    # Convenience function
    ######################

    def log10(self, param_basename):
        """True if the jumping of name param_basename should be log10"""
        if param_basename not in self._get_l_parameter_basename_GP():
            raise ValueError(f"param_basename shoud be in {self._get_l_parameter_basename_GP()}")
        return self.parametrisation["log10"][param_basename]


class QPCGeorgeModel(QPGeorgeModel):

    __category__ = "QPCGeorge"


    ############################################################
    ## Dealing with the parameters and their names for the model
    ############################################################

    # Dealing with parameter basenames
    ##################################

    def _get_l_parameter_basename_GP(self):
        return ['A1', 'A2', 'P', 'tau']


class QPCeleriteModel(QPGeorgeModel):

    __category__ = "QPCelerite"


    ############################################################
    ## Dealing with the parameters and their names for the model
    ############################################################

    # Dealing with parameter basenames
    ##################################

    def _get_l_parameter_basename_GP(self):
        return ['B', 'C', 'P', 'L']


class RotationCeleriteModel(QPGeorgeModel):

    __category__ = "RotationCelerite"


    ############################################################
    ## Dealing with the parameters and their names for the model
    ############################################################

    # Dealing with parameter basenames
    ##################################

    def _get_l_parameter_basename_GP(self):
        return ['sigma', 'P', 'Q', 'dQ', 'f']


class SHOCeleriteModel(QPGeorgeModel):

    __category__ = "SHOCelerite"

    ############################################################
    # Dealing with the parametrisation, param_extension and args
    ############################################################

    def _set_parametrisation(self, parametrisation=None):
        """ """
        self.parametrisation.update({'use_rho': True, 'use_Q': True, 'use_sigma': True, 'log10': {'rho/omega0': False, 'Q/tau': False, 'sigma/S0': False}})
        if parametrisation is not None:
            for key in parametrisation:
                if key not in ['use_rho', 'use_Q', 'use_sigma', 'log10']:
                    raise ValueError(f"The only possible keys to the 'parametrisation' are ['use_rho', 'use_Q', 'use_sigma', 'log10']. You provided {key}.")
                if key in ['use_rho', 'use_Q', 'use_sigma']:
                    if not(isinstance(parametrisation[key], bool)):
                        raise ValueError(f"Value of parametrisation[{key}] should be a bool (got {parametrisation[key]})")
                    self.parametrisation[key] = parametrisation[key]
                if key == 'log10':
                    if not(isinstance(parametrisation[key], dict)):
                        raise ValueError(f"'log10' in parametrisation should be a dictionary. You provided a {type(parametrisation[key])}.")
                    for param_basename in parametrisation[key]:
                        if param_basename not in ['rho/omega0', 'Q/tau', 'sigma/S0']:
                            raise ValueError(f"The only possible keys to the 'log10' dictionary are ['rho/omega0', 'Q/tau', 'sigma/S0']. You provided {key}.")
                    if not(isinstance(parametrisation[key][param_basename], bool)):
                        raise ValueError(f"Value of parametrisation[{key}][{param_basename}] should be a bool (got {parametrisation[key][param_basename]})")
                    self.parametrisation[key][param_basename] = parametrisation[key][param_basename]
        super(QPGeorgeModel, self)._set_parametrisation(parametrisation=parametrisation)

    ############################################################
    ## Dealing with the parameters and their names for the model
    ############################################################

    # Dealing with parameter basenames
    ##################################

    def _get_l_parameter_basename_GP(self):
        res = []
        if self.use_sigma:
            res.append('sigma')
        else:
            res.append('S0')
        if self.use_rho:
            res.append('rho')
        else:
            res.append('omega0')
        if self.use_Q:
            res.append('Q')
        else:
            res.append('tau')
        return res

    ######################
    # Convenience function
    ######################

    @property
    def use_sigma(self):
        return self.parameterisation['use_sigma']

    @property
    def use_rho(self):
        return self.parameterisation['use_rho']
    
    @property
    def use_Q(self):
        return self.parameterisation['use_Q']

    def log10(self, param_basename):
        """True if the jumping of name param_basename should be log10"""
        if param_basename not in self._get_l_parameter_basename_GP():
            raise ValueError(f"param_basename shoud be in {self._get_l_parameter_basename_GP()}")
        if param_basename in ["sigma", "S0"]:
            return self.parametrisation["log10"]['sigma/S0']
        elif param_basename in ["rho", "omega0"]:
            return self.parametrisation["log10"]['rho/omega0']
        elif param_basename in ["Q", "tau"]:
            return self.parametrisation["log10"]['Q/tau']


class Matern32Model(QPGeorgeModel):

    __category__ = "Matern32Celerite"

    ############################################################
    ## Dealing with the parameters and their names for the model
    ############################################################

    # Dealing with parameter basenames
    ##################################

    def _get_l_parameter_basename_GP(self):
        return ['sigma', 'rho']
