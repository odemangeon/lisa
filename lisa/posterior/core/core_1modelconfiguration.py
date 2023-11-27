"""Module to define the class Core_ModelConfig

The class that define the object that will be used to store the configuration 
of various models
"""
from copy import copy
from pprint import pformat

from .paramcontainer import Core_ParamContainer
from .parameter import Parameter
from ...tools.metaclasses import MandatoryReadOnlyAttr


class Core_1ModelConfig(metaclass=MandatoryReadOnlyAttr):
    """docstring for Core_ModelConfig.

    Definition of the configuration of models
    """

    __mandatoryattrs__ = ["category", ]
    _show_category_in_dict2print = True

    ################
    # Main functions
    ################

    def __init__(self, model_name):
        self._object_categories = {}  # This are parameter containers required by the model that host the model parameters
        self.__model_name = model_name  # This is the name of the model
        self.__parametrisation = {}  # This is the dictionary that will contains the parameters related to the parameterisation (ex: you want to jump the log of a parameter instead of the parameter itself)
        self.__args = {}  # This is the dictionary that contains some parameters to define some properties of the model (ex: wether you want to let a given parameter vary or if you want to include an occultation in the phase curve model)

    @property
    def dict2print(self):
        """Used to print the content in the parametrisation file."""
        dict2print = {}
        if self._show_category_in_dict2print:
            dict2print = {'category': self.category}
        if len(self.args) > 0:
            dict2print['args'] = self.args
        if len(self.parametrisation) > 0:
            dict2print['parametrisation'] = self.parametrisation
        if len(self.param_extensions) > 0:
            dict2print['param_extensions'] = self.param_extensions
        return dict2print

    def load_config(self, dico_config):
        """Load the content of the configuration dictionary read from the parametrisation file

        Argument
        --------
        dico_config : dict
        """
        if dico_config is None:
            dico_config = {}
        self._set_parametrisation(parametrisation=dico_config.get('parametrisation', None))
        self._set_args(args=dico_config.get('args', None))
        self._set_param_extensions(param_extensions=dico_config.get('param_extensions', None))

    ################################
    # Deal with the parameterisation
    ################################

    def _set_parametrisation(self, parametrisation=None):
        if not(isinstance(parametrisation, dict) or (parametrisation is None)):
            raise ValueError(f"parametrisation should be None or a dictionary whose keys are in {list(self.parametrisation.keys())}")
        if parametrisation is not None:
            for key in parametrisation:
                if key not in list(self.parametrisation.keys()):
                    raise ValueError(f"{key} is not a valid key for the parametrisation dictionary. Should be {list(self.parametrisation.keys())}")

    def _set_param_extensions(self, param_extensions=None, **kwargs):
        self.__param_extensions = self._get_default_param_extensions(**kwargs)
        if not(isinstance(param_extensions, dict) or (param_extensions is None)):
            raise ValueError(f"parametrisation should be None or a dictionary whose keys are in {list(self.parametrisation.keys())}")
        if param_extensions is not None:
            for key in param_extensions:
                if key not in list(self.__param_extensions.keys()):
                    raise ValueError(f"{key} is not a valid key for the param_extensions dictionary. Should be {list(self.__param_extensions.keys())}")
                for param_basename in param_extensions[key]:
                    if param_basename not in self.__param_extensions[key]:
                        raise ValueError(f"Param base name is not use by the model. Should be {list(self.__param_extensions[key].keys())}")
                    if not(isinstance(param_extensions[key][param_basename], str)):
                        raise ValueError(f"param_extensions[{key}][{param_basename}] should be a str (got {param_extensions[key][param_basename]})")
                    self.__param_extensions[key][param_basename] = param_extensions[key][param_basename]

    def _get_default_param_extensions(self, **kwargs):
        return {obj_cat: {param_basename: self.model_name for param_basename in self._get_l_parameter_basename(object_category=obj_cat, **kwargs)}
                for obj_cat in self.object_categories}

    def _set_args(self, args=None):
        """"""
        if not(isinstance(args, dict) or (args is None)):
            raise ValueError(f"parametrisation should be None or a dictionary whose keys are in {list(self.args.keys())}")
        if args is not None:
            for key in args:
                if key not in list(self.args.keys()):
                    raise ValueError(f"{key} is not a valid key for the parametrisation dictionary. Should be {list(self.args.keys())}")

    ###############################################
    ## Deal with the object categories in the model
    ###############################################

    @property
    def object_categories(self):
        """Dictionary of object categories."""
        return self._object_categories

    @property
    def l_object_category(self):
        """list of available object categories."""
        return list(self.object_categories.keys())

    def _get_l_object_category_arg(self, object_category):
        """Create l_object_category from object_category argument provided by the user."""
        if object_category is None:
            l_object_category = self.l_object_category
        elif isinstance(object_category, list):
            l_object_category = copy(object_category)
        else:
            l_object_category = [object_category, ]
        return l_object_category
    
    def _find_object_category(self, param_basename, **kwargs):
        """Find the object category of a param_basename.

        Argument
        --------
        param_basename  : str

        Return
        ------
        object_category    : str
        """
        l_object_category = []
        for obj_cat in self.l_object_category:
            if param_basename in self._get_l_parameter_basename(object_category=obj_cat, **kwargs):
                l_object_category.append(obj_cat)
        if len(l_object_category) == 0:
            raise ValueError(f"Object category of parameter {param_basename}, could not be found.")
        elif len(l_object_category) > 1:
            raise ValueError(f"There are multiple possible categories for parameter {param_basename}: {l_object_category}.")
        else:
            return l_object_category[0]
    
    ###########################################################
    ## Dealing with the parameter and their names for the model
    ###########################################################

    # Dealing with parameter basenames
    ##################################

    def _get_l_parameter_basename(self, object_category=None, **kwargs):
        """Return the list of all parameter basename for the model"""
        l_object_category = self._get_l_object_category_arg(object_category)
        l_param_basename = []
        for obj_cat in l_object_category:
            l_param_basename += self._get_function_get_l_parameter_basename(object_category=obj_cat)(**self._get_function_get_kwargs_4_get_l_parameter_basename(object_category=obj_cat)(object_category=object_category, force_object_category=False, **kwargs))
        return l_param_basename
    
    def _get_function_get_l_parameter_basename(self, object_category):
        if object_category in self.object_categories:
            raise NotImplementedError(f"The function has not been implemented for object category {object_category}. BUT IT SHOULD !")
        else:
            raise ValueError(f"The object_category that you provided ({object_category}) is invalid")
    
    def _get_function_get_kwargs_4_get_l_parameter_basename(self, object_category):
        if object_category in self.object_categories:
            raise NotImplementedError(f"The function has not been implemented for object category {object_category}. BUT IT SHOULD !")
        else:
            raise ValueError(f"The object_category that you provided ({object_category}) is invalid")
    
    def _get_kwargs_4_get_l_parameter_basename_default(self, object_category, force_object_category, **kwargs):
        if force_object_category:
            return {"object_category": object_category}
        else:
            return {}
    
    # Dealing with parameter names
    ##############################

    def _get_parameter_name(self, param_basename, object_category=None, **kwargs):
        """Return the parameter name"""
        if object_category is None:
            object_category = self._find_object_category(param_basename=param_basename, **kwargs)
        if param_basename not in self._get_l_parameter_basename(object_category=object_category, **kwargs):
            raise ValueError(f"parameter basename {param_basename} is not in the list of parameter base names for object category {object_category} and kwargs {kwargs}")
        return self._get_function_get_parameter_name(object_category=object_category)(**self._get_function_get_kwargs_4_get_parameter_name(object_category=object_category)(param_basename=param_basename, object_category=object_category, **kwargs))
    
    def _get_param_extension(self, param_basename, object_category):
        """
        """
        return self.__param_extensions[object_category][param_basename]

    def _get_function_get_parameter_name(self, object_category):
        if object_category in self.object_categories:
            raise NotImplementedError(f"The function has not been implemented for object category {object_category}. BUT IT SHOULD !")
        else:
            raise ValueError(f"The object_category that you provided ({object_category}) is invalid")
        # As is this function provides only argument checks. It is meant to be overload in the child class
    
    def _get_function_get_kwargs_4_get_parameter_name(self, object_category):
        if object_category in self.object_categories:
            raise NotImplementedError(f"The function has not been implemented for object category {object_category}. BUT IT SHOULD !")
        else:
            raise ValueError(f"The object_category that you provided ({object_category}) is invalid")
        # As is this function provides only argument checks. It is meant to be overload in the child class

    def _get_parameter_name_default(self, param_basename, object_category):
        return f"{param_basename}{self._get_param_extension(param_basename=param_basename, object_category=object_category)}"
    
    def _get_kwargs_4_get_parameter_name_default(self, param_basename, object_category, **kwargs):
        return {'param_basename':  param_basename, 'object_category': object_category}

    # Deal with creating parameters
    ###############################

    def create_parameters_and_set_main(self, object_category=None, **kwargs):
        """Create (if needed) the parameters of the model.

        This function should be used in the function doing the parametrisation of the model

        Arguments
        ---------
        inst_model_fullname : str
        object_category     : str or list of str or None
            If not provided (None) the list of all available object_categories will be used
        """
        l_object_category = self._get_l_object_category_arg(object_category)
        for obj_cat in l_object_category:
            l_param_basename = self._get_l_parameter_basename(object_category=obj_cat, **kwargs)
            for param_basename in l_param_basename:
                param_name = self._get_parameter_name(param_basename=param_basename, object_category=obj_cat, **kwargs)
                param = self._create_parameter(param_name=param_name, param_basename=param_basename, object_category=obj_cat,
                                              **kwargs
                                              )
                param.main = True

    def _create_parameter(self, param_name, param_basename, object_category=None, **kwargs):
        """Create (if needed) a parameter of the given object category"""
        if object_category is None:
            object_category = self._find_object_category(param_basename=param_basename, **kwargs)
        if param_basename not in self._get_l_parameter_basename(object_category=object_category, **kwargs):
            raise ValueError(f"parameter basename {param_basename} is not in the list of parameter base names for object category {object_category} and kwargs {kwargs}")
        return self._get_function_create_parameter(object_category=object_category)(**self._get_function_get_kwargs_4_create_parameter(object_category=object_category)(param_name=param_name, param_basename=param_basename, object_category=object_category, **kwargs))

    def _get_function_create_parameter(self, object_category):
        if object_category in self.object_categories:
            raise NotImplementedError(f"The function has not been implemented for object category {object_category}. BUT IT SHOULD !")
        else:
            raise ValueError(f"The object_category that you provided ({object_category}) is invalid")
        
    def _get_function_get_kwargs_4_create_parameter(self, object_category):
        if object_category in self.object_categories:
            raise NotImplementedError(f"The function has not been implemented for object category {object_category}. BUT IT SHOULD !")
        else:
            raise ValueError(f"The object_category that you provided ({object_category}) is invalid")

    def _create_parameter_default(self, param_name, object_category):
        param_container = self.object_categories[object_category]
        if not(param_container.has_parameter(name=param_name)):
                param = Parameter(name=param_name, name_prefix=param_container.name)
                param_container.add_parameter(param)
        else:
            param = param_container._get_parameter(name=param_name)  
        return param  

    def _get_kwargs_4_create_parameter_default(self, param_name, param_basename, object_category, **kwargs):
        return {'param_name': param_name, 'object_category': object_category}

    # Deal with getting parameter
    #############################
    def get_parameters(self, object_category=None, **kwargs):
        """Get a dictionary of the parameter of the models.

        This function will be used when producing the datasimulator to get the proper parameters

        Arguments
        ---------
        object_category     : str or list of str or None
            If not provided (None) the list of all available object_categories will be used

        Return
        ------
        parameters : dict of dict of Parameter
        """
        l_object_category = self._get_l_object_category_arg(object_category)
        parameters = {}
        for obj_cat in l_object_category:
            parameters[obj_cat] = {}
            l_param_basename = self._get_l_parameter_basename(object_category=obj_cat, **kwargs)
            for param_basename in l_param_basename:
                parameters[obj_cat][param_basename] = self._get_parameter(param_basename=param_basename, object_category=obj_cat, **kwargs)
        return parameters

    def _get_parameter(self, param_basename, object_category=None, **kwargs):
        """Return the parameter"""
        if object_category is None:
            object_category = self._find_object_category(param_basename=param_basename, **kwargs)
        if param_basename not in self._get_l_parameter_basename(object_category=object_category, **kwargs):
            raise ValueError(f"parameter basename {param_basename} is not in the list of parameter base names object category {object_category} ")
        return self._get_function_get_parameter(object_category=object_category)(**self._get_function_get_kwargs_4_get_parameter(object_category=object_category)(param_basename=param_basename, object_category=object_category, **kwargs))
        
    def _get_function_get_parameter(self, object_category):
        if object_category in self.object_categories:
            raise NotImplementedError(f"The function has not been implemented for object category {object_category}. BUT IT SHOULD !")
        else:
            raise ValueError(f"The object_category that you provided ({object_category}) is invalid")
        
    def _get_function_get_kwargs_4_get_parameter(self, object_category):
        if object_category in self.object_categories:
            raise NotImplementedError(f"The function has not been implemented for object category {object_category}. BUT IT SHOULD !")
        else:
            raise ValueError(f"The object_category that you provided ({object_category}) is invalid")

    def _get_parameter_default(self, param_basename, object_category):
        param_name = self._get_parameter_name(param_basename=param_basename, object_category=object_category)
        param_container = self.object_categories[object_category]
        return param_container.parameters[param_name]
    
    def _get_kwargs_4_get_parameter_default(self, param_basename, object_category, **kwargs):
        return {'param_basename': param_basename, 'object_category': object_category}

    ##############################
    # Functions used by Subclasses
    ##############################

    @property
    def model_name(self):
        """model_name"""
        return self.__model_name

    @property
    def parametrisation(self):
        """parametrisation dictionary"""
        return self.__parametrisation

    @property
    def param_extensions(self):
        """parametrisation dictionary"""
        return self.__param_extensions

    @property
    def args(self):
        """parametrisation dictionary"""
        return self.__args
