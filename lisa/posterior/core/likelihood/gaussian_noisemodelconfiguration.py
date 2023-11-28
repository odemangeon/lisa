"""
The objective of this module is to define the GaussianModel class which allow to configure gaussian noise models
"""
from loguru import logger
from numpy import sum as npsum
from numpy import log as nplog
from numpy import pi, concatenate

from ..core_1modelconfiguration import Core_1ModelConfig

twopi = 2 * pi


class GaussianModel(Core_1ModelConfig):
    """
    """

    __category__ = "gaussian"
    _show_category_in_dict2print = False

    ################
    # Main functions
    ################

    def __init__(self, model_name, instrument, dico_config_model=None):
        super(GaussianModel, self).__init__(model_name=model_name)
        self._object_categories = {'instrument': instrument}
        self.load_config(dico_config=dico_config_model)

    def create_parameters_and_set_main(self, object_category=None):
        super(GaussianModel, self).create_parameters_and_set_main(object_category=object_category)

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
                    if args[key] not in ['additive', 'multiplicative']:
                        raise ValueError("jitter_type must be in ['additive', 'multiplicative']")

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
        if param_basename == 'jitter':
            if self.jitter_type == 'additive':
                param_name = 'jitter'
            elif self.jitter_type == 'multiplicative':
                param_name = 'jittermulti'
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


    ########################################
    # Compute impact of jitter on error bars
    ########################################

    def get_compute_jitteredvar(self):
        if self.jitter_type == 'additive':
            if self.log10jitter:
                def compute_jitteredvar(data_err, jitter):
                    return data_err**2 + 10**(2 * jitter)
            else:
                def compute_jitteredvar(data_err, jitter):
                    return data_err**2 + jitter**2
        if self.jitter_type == 'multiplicative':
            if self.log10jitter:
                def compute_jitteredvar(data_err, jitter):
                    return data_err**2 * 10**(2 * jitter)
            else:
                def compute_jitteredvar(data_err, jitter):
                    return (data_err * jitter)**2
        return compute_jitteredvar
    
    def add_text_compute_lnlike(self, nparam_datasim, function_builder_1inst, function_shortname_1inst):
        tab = "    " 
        if self.use_Baluevfactor:
            text_return = f"{tab}return -0.5 * npsum((concatenate(dict_datakwargs['data']) - concatenate(sim_data)).reshape((-1))**2 / concatenate(dict_datakwargs['data_err']) / (1 - (nparam_datasim / len(dict_datakwargs['data_err']))) - nplog(twopi / concatenate(dict_datakwargs['data_err'])))"
        else:
            text_return = f"{tab}return -0.5 * npsum((concatenate(dict_datakwargs['data']) - concatenate(sim_data)).reshape((-1))**2 / concatenate(dict_datakwargs['data_err']) - nplog(twopi / concatenate(dict_datakwargs['data_err'])))"
        function_builder_1inst.add_to_body_text(text=text_return, function_shortname=function_shortname_1inst)
        function_builder_1inst.add_variable_to_ldict(variable_name='npsum', variable_content=npsum, function_shortname=function_shortname_1inst , exist_ok=False, overwrite=False)
        function_builder_1inst.add_variable_to_ldict(variable_name='nplog', variable_content=nplog, function_shortname=function_shortname_1inst , exist_ok=False, overwrite=False)
        function_builder_1inst.add_variable_to_ldict(variable_name='twopi', variable_content=twopi, function_shortname=function_shortname_1inst , exist_ok=False, overwrite=False)
        function_builder_1inst.add_variable_to_ldict(variable_name='concatenate', variable_content=concatenate, function_shortname=function_shortname_1inst , exist_ok=False, overwrite=False)

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
