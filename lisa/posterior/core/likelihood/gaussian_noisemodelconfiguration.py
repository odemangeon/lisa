"""
The objective of this module is to define the GaussianModel class which allow to configure gaussian noise models
"""
from ..core_1modelconfiguration import Core_1ModelConfig


class GaussianModel(Core_1ModelConfig):
    """
    """

    __category__ = "gaussian"

    ################
    # Main functions
    ################

    def __init__(self, model_name, instrument, dico_config_model=None):
        super(GaussianModel, self).__init__(model_name=model_name, dico_config_model=dico_config_model)
        self.__object_categories = {'instrument': instrument}

    ############################################################
    # Dealing with the parametrisation, param_extension and args
    ############################################################

    def _set_parametrisation(self, parametrisation=None):
        """ """
        self.parametrisation.update({"log10": False, "use_Baluevfactor": False})
        if parametrisation is not None:
            for key in parametrisation:
                if key not in ["log10", "use_Baluevfactor"]:
                    raise ValueError(f"The only possible keys to the 'parametrisation' are ['log10', 'use_Baluevfactor']. You provided {key}.")
                if not(isinstance(parametrisation[key], bool)):
                    raise ValueError(f"Value of key {key} of parametrisation dictionary should be a bool (got {parametrisation[key]})")
                self.parametrisation[key] = parametrisation[key]
        super(GaussianModel, self)._set_parametrisation(parametrisation=parametrisation)

    def _set_args(self, args=None):
        self.args.update({'jitter_type': 'additive'})
        if args is not None:
            for key in args:
                if key == 'jitter_type':
                    if args[key] not in ['additive', 'multiplicative', 'dfm']:
                        raise ValueError("jitter_type must be in ['additive', 'multiplicative', 'dfm']")

    ############################################################
    ## Dealing with the parameters and their names for the model
    ############################################################

    # Dealing with parameter basenames
    ##################################

    def _get_function_get_l_parameter_basename(self, object_category):
        if object_category == 'instrument':
            return self._get_l_parameter_basename_instrument
        super(GaussianModel, self)._get_function_get_l_parameter_basename(object_category=object_category)
    
    def _get_function_get_kwargs_4_get_l_parameter_basename(self, object_category):
        if object_category == 'instrument':
            return self._get_kwargs_4_get_l_parameter_basename_default
        super(GaussianModel, self)._get_function_get_kwargs_4_get_l_parameter_basename(object_category=object_category)
    
    def _get_l_parameter_basename_instrument(self):
        return ['jitter', ]
    
    # Dealing with parameter names
    ##############################

    def _get_function_get_parameter_name(self, object_category):
        if object_category == 'instrument':
            return self._get_parameter_name_instrument
        super(GaussianModel, self)._get_function_get_parameter_name(object_category=object_category)
    
    def _get_function_get_kwargs_4_get_parameter_name(self, object_category):
        if object_category == 'instrument':
            return self._get_kwargs_4_get_parameter_name_default
        super(GaussianModel, self)._get_function_get_kwargs_4_get_parameter_name(object_category=object_category)

    def _get_parameter_name_instrument(self, param_basename, object_category):
        if param_basename == 'jitter'
            if self.jitter_type == 'additive':
                param_name = 'jitter'
            elif self.jitter_type == 'multiplicative':
                param_name = 'jittermulti'
            elif self.jitter_type == 'dfm':
                param_name = 'jitterdfm'
            if self.log10jitter:
                param_name = 'log10' + param_basename            
            return f"{param_name}{self._get_param_extension(param_basename=param_basename, object_category=object_category)}"

    # Deal with creating parameters
    ###############################

    def _get_function_create_parameter(self, object_category):
        if object_category == 'instrument':
            return self._create_parameter_default
        super(GaussianModel, self)._get_function_create_parameter(object_category=object_category)

        
    def _get_function_get_kwargs_4_create_parameter(self, object_category):
        if object_category == 'instrument':
            return self._get_kwargs_4_create_parameter_default
        super(GaussianModel, self)._get_function_get_kwargs_4_create_parameter(object_category=object_category)

    # Deal with getting parameter
    #############################

    def _get_function_get_parameter(self, object_category):
        if object_category == 'instrument':
            return self._get_parameter_default
        super(GaussianModel, self)._get_function_get_parameter(object_category=object_category)

        
    def _get_function_get_kwargs_4_get_parameter(self, object_category):
        if object_category == 'instrument':
            return self._get_kwargs_4_get_parameter_default
        super(GaussianModel, self)._get_function_get_kwargs_4_get_parameter(object_category=object_category)

    ######################
    # Convenience function
    ######################

    @property
    def instrument(self):
        """Instrument model param container"""
        return self.object_categories["instrument"]
    
    @property
    def log10jitter(self):
        """True if the jumping jitter param should be log10"""
        return self.parametrisation["log10"]
    
    @property
    def use_Baluevfactor(self):
        """True if the Baluev factors should be used"""
        return self.parametrisation["use_Baluevfactor"]
    
    @property
    def jitter_type(self):
        """Type of jitter"""
        return self.args["jitter_type"]
