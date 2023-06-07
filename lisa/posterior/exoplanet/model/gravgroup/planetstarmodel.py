from copy import copy
from numpy import pi
from numbers import Number
# from pprint import pformat

from ....core.parameter import Parameter
from .....tools.metaclasses import MandatoryReadOnlyAttr

try:
    import spiderman
    spiderman_imported = True
except (ModuleNotFoundError, ImportError):
    spiderman_imported = False
try:
    from kelp import Filter, StellarSpectrum
    kelp_imported = True
except (ModuleNotFoundError, ImportError):
    kelp_imported = False


class Core_PlanetStarModel(metaclass=MandatoryReadOnlyAttr):
    """docstring for PlanetStarModel."""

    __mandatoryattrs__ = ["category"]

    ################
    # Main functions
    ################

    def __init__(self, model_name, planet, host_star, orbital_models=None, dico_config_model=None):
        # orbital_models=None, parametrisation=None, param_extensions=None
        if dico_config_model is None:
            dico_config_model = {}
        if orbital_models is None:
            self.__object_categories = {'planet': planet, 'star': host_star}
        else:
            self.__object_categories = {'planet': planet, 'star': host_star, 'orbit': orbital_models}
        self.__model_name = model_name
        self.__parametrisation = {}
        self.__args = {}
        self._set_parametrisation(parametrisation=dico_config_model.get('parametrisation', None))
        self._set_args(args=dico_config_model.get('args', None))
        self._set_param_extensions(param_extensions=dico_config_model.get('param_extensions', None))

    @property
    def dict2print(self):
        """Used to print the content in the parametrisation file."""
        dict2print = {'category': self.category}
        if len(self.args) > 0:
            dict2print['args'] = self.args
        if len(self.parametrisation) > 0:
            dict2print['parametrisation'] = self.parametrisation
        if len(self.param_extensions) > 0:
            dict2print['param_extensions'] = self.param_extensions
        return dict2print

    def create_parameters_and_set_main(self, inst_model_fullname=None, object_category=None):
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
            l_param_basename = self._get_l_parameter_basename(inst_model_fullname=inst_model_fullname,
                                                              object_category=object_category
                                                              )
            for param_basename in l_param_basename:
                param_name = self._get_parameter_name(param_basename=param_basename, inst_model_fullname=inst_model_fullname,
                                                      object_category=object_category
                                                      )
                param = self._create_parameter(param_name=param_name, param_basename=param_basename,
                                               object_category=object_category, inst_model_fullname=inst_model_fullname
                                               )
                param.main = True

    @property
    def config_dict(self):
        """Return the configuration dictionary for the parametrisation file.

        This will be used to print in the parametrisation file

        Return
        ------
        config_dict : dictionary
        """
        return {'category': self.category}

    def get_parameters(self, inst_model_fullname=None, object_category=None):
        """Get a dictionary of the parameter of the models.

        This function will be used when producing the datasimulator to get the proper parameters

        Arguments
        ---------
        inst_model_fullname : str
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
            l_param_basename = self._get_l_parameter_basename(inst_model_fullname=inst_model_fullname, object_category=obj_cat)
            for param_basename in l_param_basename:
                parameters[obj_cat][param_basename] = self._get_parameter(param_basename=param_basename, inst_model_fullname=inst_model_fullname,
                                                                          object_category=obj_cat
                                                                          )
        return parameters

    def get_orbital_model(self, inst_model_fullname):
        """Get the OrbitalModel instance associated to the instrument model

        This function will be used when producing the datasimulator to get the proper parameters

        Arguments
        ---------
        inst_model_fullname : str

        Return
        ------
        orbital_model : Subclass of Core_PlanetStarModel (OrbitalModel)
        """
        if not(self.with_orbital_models):
            raise ValueError("The model does not possible orbital models")
        return self.orbital_models.get_model(planet_name=self.planet.get_name(), inst_model_fullname=inst_model_fullname)

    #################################################################
    # Functions required directly or indirectly be the main functions
    #################################################################

    def _set_parametrisation(self, parametrisation=None):
        """ """
        if not(isinstance(parametrisation, dict) or (parametrisation is None)):
            raise ValueError(f"parametrisation should be None or a dictionary whose keys are in {list(self.parametrisation.keys())}")
        if parametrisation is not None:
            for key in parametrisation:
                if key not in list(self.parametrisation.keys()):
                    raise ValueError(f"{key} is not a valid key for the parametrisation dictionary. Should be {list(self.parametrisation.keys())}")

    def _set_param_extensions(self, param_extensions=None):
        """ """
        self.__param_extensions = {"planet": {param_basename: self.model_name for param_basename in self._get_l_parameter_basename_planet()},
                                   "star": {param_basename: self.model_name for param_basename in self._get_l_parameter_basename_star()},
                                   }
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

    def _set_args(self, args=None):
        """"""
        if not(isinstance(args, dict) or (args is None)):
            raise ValueError(f"parametrisation should be None or a dictionary whose keys are in {list(self.args.keys())}")
        if args is not None:
            for key in args:
                if key not in list(self.args.keys()):
                    raise ValueError(f"{key} is not a valid key for the parametrisation dictionary. Should be {list(self.args.keys())}")

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

    def _get_l_parameter_basename(self, inst_model_fullname=None, object_category=None):
        """Get the list of all parameter basename for the model.

        Argument
        --------
        inst_model_fullname : str
            Instrument model full name which can be necessary for orbital parameters

        Return
        ------
        l_param_basename    : list of str
        """
        l_object_category = self._get_l_object_category_arg(object_category)
        l_param_basename = []
        for obj_cat in l_object_category:
            if obj_cat == "planet":
                l_param_basename += self._get_l_parameter_basename_planet()
            elif obj_cat == "star":
                l_param_basename += self._get_l_parameter_basename_star()
            elif obj_cat == "orbit":
                l_param_basename += self._get_l_parameter_basename_orbit(inst_model_fullname=inst_model_fullname)
            else:
                raise ValueError(f"Object category {obj_cat} is not handled by this function.")
        return l_param_basename

    def _get_parameter_name(self, param_basename, inst_model_fullname=None, object_category=None):
        """Return the parameter name"""
        if object_category is None:
            object_category = self._find_object_category(param_basename=param_basename, inst_model_fullname=inst_model_fullname)
        if param_basename not in self._get_l_parameter_basename(inst_model_fullname=inst_model_fullname, object_category=object_category):
            raise ValueError(f"parameter basename {param_basename} is not in the list of parameter base names for instrument model {inst_model_fullname} and object category {object_category} ")
        if object_category in ['planet', 'star']:
            return self._get_parameter_name_planetstar(param_basename=param_basename, object_category=object_category)
        elif object_category == "orbit":
            return self._get_parameter_name_orbit(param_basename=param_basename, inst_model_fullname=inst_model_fullname)
        else:
            raise ValueError(f"Object category {object_category} is not handled by this function.")

    def _create_parameter(self, param_name, param_basename, object_category=None, inst_model_fullname=None):
        """Create (if needed) a parameter of the given object category"""
        if object_category is None:
            object_category = self._find_object_category(param_basename=param_basename, inst_model_fullname=inst_model_fullname)
        if object_category in ['planet', 'star']:
            if param_basename not in self._get_l_parameter_basename(inst_model_fullname=inst_model_fullname, object_category=object_category):
                raise ValueError(f"parameter basename {param_basename} is not in the list of parameter base names for instrument model {inst_model_fullname} and object category {object_category} ")
            param_container = self.object_categories[object_category]
            if not(param_container.has_parameter(name=param_name)):
                param = Parameter(name=param_name, name_prefix=param_container.name)
                param_container.add_parameter(param)
            else:
                param = param_container.get_parameter(name=param_name)
        elif object_category == "orbit":
            if not(self.with_orbital_models):
                raise ValueError(f"object category {object_category} is not valid as model doesn't have orbital models")
            else:
                orbital_model = self.orbital_models.get_model(planet_name=self.planet.get_name(), inst_model_fullname=inst_model_fullname)
                param = orbital_model._create_parameter(param_name=param_name, param_basename=param_basename, object_category=None)
        else:
            raise ValueError(f"Object category {object_category} is not handled by this function.")
        return param

    @property
    def object_categories(self):
        """Dictionary of object categories."""
        return self.__object_categories

    def _get_parameter(self, param_basename, inst_model_fullname, object_category):
        """Return the parameter"""
        object_category = self._find_object_category(param_basename=param_basename, inst_model_fullname=inst_model_fullname)
        if param_basename not in self._get_l_parameter_basename(inst_model_fullname=inst_model_fullname, object_category=object_category):
            raise ValueError(f"parameter basename {param_basename} is not in the list of parameter base names for instrument model {inst_model_fullname} and object category {object_category} ")
        if object_category in ['planet', 'star']:
            param_name = self._get_parameter_name(param_basename=param_basename, object_category=object_category)
            param_container = self.object_categories[object_category]
            return param_container.parameters[param_name]
        elif object_category == "orbit":
            if not(self.with_orbital_models):
                raise ValueError(f"object category {object_category} is not valid as model doesn't have orbital models")
            orbital_model = self.orbital_models.get_model(planet_name=self.planet.get_name(), inst_model_fullname=inst_model_fullname)
            return orbital_model._get_parameter(param_basename=param_basename, inst_model_fullname=inst_model_fullname,
                                                object_category=None
                                                )
        else:
            raise ValueError(f"Object category {object_category} is not handled by this function.")

    def _get_l_parameter_basename_orbit(self, inst_model_fullname=None):
        """Return the list of orbital parameter basenames."""
        if not(self.with_orbital_models):
            return []
        else:
            orbital_model = self.orbital_models.get_model(planet_name=self.planet.get_name(), inst_model_fullname=inst_model_fullname)
            return orbital_model._get_l_parameter_basename(l_required_orbital_param_type=self.l_required_orbital_param_type,
                                                           inst_model_fullname=inst_model_fullname, object_category=None
                                                           )

    def _get_l_parameter_basename_planet(self):
        """Return the list of orbital parameter basenames."""
        return []

    def _get_l_parameter_basename_star(self):
        """Return the list of orbital parameter basenames."""
        return []

    @property
    def planet(self):
        """Planet instance"""
        return self.object_categories["planet"]

    @property
    def with_orbital_models(self):
        """True if the models are associated with an orbital model"""
        return "orbit" in self.object_categories

    @property
    def orbital_models(self):
        """Instance of the OrbitalModel class which defines the configuration of orbital models"""
        if not(self.with_orbital_models):
            raise ValueError("Model doesn't have orbital models")
        return self.object_categories["orbit"]

    def _find_object_category(self, param_basename, inst_model_fullname=None):
        """Find the object category of a param_basename.

        Argument
        --------
        param_basename  : str
        model_category  : str

        Return
        ------
        object_category    : str
        """
        l_object_category = []
        for object_category in self.l_object_category:
            if param_basename in self._get_l_parameter_basename(inst_model_fullname=inst_model_fullname,
                                                                object_category=object_category
                                                                ):
                l_object_category.append(object_category)
        if len(l_object_category) == 0:
            raise ValueError(f"Object category of parameter {param_basename}, could not be found.")
        elif len(l_object_category) > 1:
            raise ValueError(f"There are multiple possible categories for parameter {param_basename}: {l_object_category}.")
        else:
            return l_object_category[0]

    def _get_parameter_name_orbit(self, param_basename, inst_model_fullname):
        """
        """
        if not(self.with_orbital_models):
            raise ValueError("Model doesn't have an orbital models")
        else:
            orbital_model = self.orbital_models.get_model(planet_name=self.planet.get_name(), inst_model_fullname=inst_model_fullname)
            return orbital_model._get_parameter_name(param_basename=param_basename, object_category=None)

    def _get_parameter_name_planetstar(self, param_basename, object_category):
        """
        """
        if not(param_basename in self._get_l_parameter_basename(inst_model_fullname=None, object_category=object_category)):
            raise ValueError(f"Parameter {param_basename} not a valid parameter base name for object category {object_category}.")
        return f"{param_basename}{self._get_param_extension(param_basename=param_basename, object_category=object_category)}"

    def _get_param_extension(self, param_basename, object_category):
        """
        """
        if not(param_basename in self._get_l_parameter_basename(inst_model_fullname=None, object_category=object_category)):
            raise ValueError(f"Parameter {param_basename} not a valid parameter base name for object category {object_category}.")
        return self.__param_extensions[object_category][param_basename]

    ##############################
    # Functions used by Subclasses
    ##############################

    # Used by OrbitalModelBatman
    @property
    def model_name(self):
        """model_name"""
        return self.__model_name

    # Used by OrbitalModelBatman
    @property
    def parametrisation(self):
        """parametrisation dictionary"""
        return self.__parametrisation

    # Used by OrbitalModelBatman
    @property
    def param_extensions(self):
        """parametrisation dictionary"""
        return self.__param_extensions

    # Used by OrbitalModelBatman
    @property
    def args(self):
        """parametrisation dictionary"""
        return self.__args

    ################################
    # Convenience/Degugging function
    ################################

    @property
    def host_star(self):
        """Host star instance"""
        return self.object_categories["star"]

    def __repr__(self):
        if self.with_orbital_models:
            return (f"{self.__class__.__name__}(model_name='{self.model_name}', planet={self.planet}, host_star={self.host_star}, "
                    f"orbital_models={self.orbital_models})"
                    )
        else:
            return (f"{self.__class__.__name__}(model_name='{self.model_name}', planet={self.planet}, host_star={self.host_star})"
                    )


class OrbitalModelBatman(Core_PlanetStarModel):
    """docstring for OrbitalModelBatman."""

    __category__ = "batman"

    ################
    # Main functions
    ################

    def __init__(self, model_name, planet, host_star, orbital_models=None, dico_config_model=None):
        super(OrbitalModelBatman, self).__init__(model_name=model_name, planet=planet, host_star=host_star,
                                                 orbital_models=None, dico_config_model=dico_config_model,
                                                 )

    @property
    def use_aR(self):
        return self.parametrisation["use_aR"]

    @property
    def use_rho(self):
        return not(self.parametrisation["use_aR"])

    ###################################################
    # Functions directly required by the main functions
    ###################################################

    def _set_parametrisation(self, parametrisation=None):
        """ """
        self.parametrisation.update({"use_aR": False, "use_tic": True, "ew_format": "ecosw-esinw", "inc_format": "cosinc"})
        super(OrbitalModelBatman, self)._set_parametrisation(parametrisation=parametrisation)
        if parametrisation is not None:
            for key in parametrisation:
                if key in ["use_aR", "use_tic"]:
                    if not(isinstance(parametrisation[key], bool)):
                        raise ValueError(f"Value of key {key} of parametrisation dictionary should be a bool (got {parametrisation[key]})")
                    self.parametrisation[key] = parametrisation[key]
                elif key == "ew_format":
                    if parametrisation[key] not in ["ecosw-esinw"]:
                        raise ValueError(f"Value of key {key} of parametrisation dictionary should be in {['ecosw-esinw']} (got {parametrisation[key]})")
                    self.parametrisation[key] = parametrisation[key]
                elif key == "inc_format":
                    if parametrisation[key] not in ["cosinc"]:
                        raise ValueError(f"Value of key {key} of parametrisation dictionary should be in {['cosinc']} (got {parametrisation[key]})")
                    self.parametrisation[key] = parametrisation[key]

    def _get_l_parameter_basename(self, l_required_orbital_param_type=None, inst_model_fullname=None, object_category=None):
        """ """
        l_object_category = self._get_l_object_category_arg(object_category)
        l_param_basename = []
        for obj_cat in l_object_category:
            if obj_cat == "planet":
                l_param_basename += self._get_l_parameter_basename_planet(l_required_orbital_param_type=l_required_orbital_param_type)
            elif obj_cat == "star":
                l_param_basename += self._get_l_parameter_basename_star(l_required_orbital_param_type=l_required_orbital_param_type)
            else:
                raise ValueError(f"Object category {obj_cat} is not handled by this function.")
        return l_param_basename

    def _get_l_parameter_basename_planet(self, l_required_orbital_param_type=None):
        """Return the list of orbital parameter basenames."""
        if l_required_orbital_param_type is None:
            l_required_orbital_param_type = ["P", "tic", "ew", "inc", "aR"]
        l_param_basename = []
        if "P" in l_required_orbital_param_type:
            l_param_basename.append("P")
        if "tic" in l_required_orbital_param_type:
            l_param_basename.append("tic")
        if "ew" in l_required_orbital_param_type:
            l_param_basename.extend(["ecosw", "esinw"])
        if "inc" in l_required_orbital_param_type:
            l_param_basename.append("cosinc")
        if "aR" in l_required_orbital_param_type:
            if self.use_aR:
                l_param_basename.append("aR")
        return l_param_basename

    def _get_l_parameter_basename_star(self, l_required_orbital_param_type=None):
        """Return the list of orbital parameter basenames."""
        if l_required_orbital_param_type is None:
            l_required_orbital_param_type = ["aR"]
        l_param_basename = []
        if "aR" in l_required_orbital_param_type:
            if self.use_rho:
                l_param_basename.append("rho")
        return l_param_basename


class TransitModelBatman(Core_PlanetStarModel):
    """docstring for TransitModelBatman."""

    __category__ = "batman"

    ################
    # Main functions
    ################

    def __init__(self, model_name, planet, host_star, orbital_models=None, dico_config_model=None):
        super(TransitModelBatman, self).__init__(model_name=model_name, planet=planet, host_star=host_star,
                                                 orbital_models=orbital_models, dico_config_model=dico_config_model,
                                                 )

    ###################################################
    # Functions directly required by the main functions
    ###################################################

    def _get_l_parameter_basename_planet(self):
        """Return the list of orbital parameter basenames."""
        return ['Rrat']

    def _get_l_parameter_basename_orbit(self, inst_model_fullname=None):
        """Return the list of orbital parameter basenames."""
        l_required_orbital_param_type = ['P', 'tic', 'ew', 'inc', 'aR']
        orbital_model = self.orbital_models.get_model(planet_name=self.planet.get_name(), inst_model_fullname=inst_model_fullname)
        return orbital_model._get_l_parameter_basename(l_required_orbital_param_type=l_required_orbital_param_type,
                                                       inst_model_fullname=inst_model_fullname, object_category=None
                                                       )


class RVKeplerianModelRadvel(Core_PlanetStarModel):
    """docstring for RVKeplerianModelRadvel."""

    __category__ = "radvel"

    ################
    # Main functions
    ################

    def __init__(self, model_name, planet, host_star, orbital_models=None, dico_config_model=None):
        super(RVKeplerianModelRadvel, self).__init__(model_name=model_name, planet=planet, host_star=host_star,
                                                     orbital_models=orbital_models, dico_config_model=dico_config_model,
                                                     )

    ###################################################
    # Functions directly required by the main functions
    ###################################################

    def _get_l_parameter_basename_planet(self):
        """Return the list of orbital parameter basenames."""
        return ['K']

    def _get_l_parameter_basename_orbit(self, inst_model_fullname=None):
        """Return the list of orbital parameter basenames."""
        l_required_orbital_param_type = ['P', 'tic', 'ew']
        orbital_model = self.orbital_models.get_model(planet_name=self.planet.get_name(), inst_model_fullname=inst_model_fullname)
        return orbital_model._get_l_parameter_basename(l_required_orbital_param_type=l_required_orbital_param_type,
                                                       inst_model_fullname=inst_model_fullname, object_category=None
                                                       )


class PhaseCurveModelSinCos(Core_PlanetStarModel):
    """docstring for PhaseCurveModelSinCos."""

    __category__ = "sincos"

    ################
    # Main functions
    ################

    def __init__(self, model_name, planet, host_star, orbital_models=None, dico_config_model=None):
        super(PhaseCurveModelSinCos, self).__init__(model_name=model_name, planet=planet, host_star=host_star,
                                                    orbital_models=orbital_models, dico_config_model=dico_config_model,
                                                    )

    @property
    def sincos(self):
        return self.args['sincos']

    @property
    def factor_period(self):
        return self.args['factor_period']

    @property
    def flux_offset(self):
        return self.args['flux_offset']

    @property
    def phase_offset(self):
        return self.args['phase_offset']

    @property
    def occultation(self):
        return self.args['occultation']

    ###################################################
    # Functions directly required by the main functions
    ###################################################

    def _set_args(self, args=None):
        """ """
        self.args.update({'sincos': 'cos', 'factor_period': 1, 'flux_offset': 'param', 'phase_offset': 'param',
                          'occultation': True
                          }
                         )
        super(PhaseCurveModelSinCos, self)._set_args(args=args)
        if args is not None:
            if set(args.keys()) != set(['sincos', 'factor_period', 'flux_offset', 'phase_offset', 'occultation']):
                raise ValueError(f"Model named {self.model_name} of planet {self.planet.get_name()}: sincos model definition needs to include an args key which contains a dictionary with the following keys: {['sincos', 'factor_period', 'flux_offset', 'phase_offset', 'occultation']}")
            if args['sincos'] not in ['sin', 'cos', None]:
                raise ValueError(f"Model named {self.model_name} of planet {self.planet.get_name()}: 'sincos' value should be in {['sin', 'cos', None]} (got {args['sincos']})")
            self.args['sincos'] = args['sincos']
            if not(isinstance(args['factor_period'], Number)) or (args['factor_period'] < 0):
                raise ValueError(f"Model named {self.model_name} of planet {self.planet.get_name()}: 'factor_period' should be a positive number (got {args['factor_period']})")
            self.args['factor_period'] = args['factor_period']
            if not(isinstance(args['flux_offset'], Number) or (args['flux_offset'] in ['param', 'zero', 'semi-amplitude'])):
                raise ValueError(f"Model named {self.model_name} of planet {self.planet.get_name()}: 'flux_offset' should be a number or 'param' or 'zero' or 'semi-amplitude' (got {args['flux_offset']})")
            self.args['flux_offset'] = args['flux_offset']
            if not(isinstance(args['phase_offset'], Number) or (args['phase_offset'] in ['param', ])):
                raise ValueError(f"Model named {self.model_name} of planet {self.planet.get_name()}: 'phase_offset' should be a number or 'param' (got {args['phase_offset']})")
            self.args['phase_offset'] = args['phase_offset']
            if not(isinstance(args['occultation'], bool)):
                raise ValueError(f"Model named {self.model_name} of planet {self.planet.get_name()}: 'occultation' should be a boolean (got {args['occultation']})")
            self.args['occultation'] = args['occultation']

    def _get_l_parameter_basename_planet(self):
        """Return the list of orbital parameter basenames."""
        if self.sincos is None:
            return ['C']
        else:
            l_param_basename = ['A']
            if self.occultation:
                l_param_basename.append('Rrat')
            if self.flux_offset == 'param':
                l_param_basename.append('Foffset')
            if self.phase_offset == 'param':
                l_param_basename.append('Phi')
            return l_param_basename

    def _get_l_parameter_basename_orbit(self, inst_model_fullname=None):
        """Return the list of orbital parameter basenames."""
        if self.occultation:
            l_required_orbital_param_type = ['P', 'tic', 'ew', 'inc', 'aR']
        else:
            l_required_orbital_param_type = ['P', 'tic']
        orbital_model = self.orbital_models.get_model(planet_name=self.planet.get_name(), inst_model_fullname=inst_model_fullname)
        return orbital_model._get_l_parameter_basename(l_required_orbital_param_type=l_required_orbital_param_type,
                                                       inst_model_fullname=inst_model_fullname, object_category=None
                                                       )


class PhaseCurveModelEllipsoidal(PhaseCurveModelSinCos):
    """docstring for PhaseCurveModelEllipsoidal."""

    __category__ = "ellipsoidal"

    ################
    # Main functions
    ################

    def __init__(self, model_name, planet, host_star, orbital_models=None, dico_config_model=None):
        super(PhaseCurveModelEllipsoidal, self).__init__(model_name=model_name, planet=planet, host_star=host_star,
                                                         orbital_models=orbital_models, dico_config_model=dico_config_model,
                                                         )

    ###################################################
    # Functions directly required by the main functions
    ###################################################

    def _set_args(self, args=None):
        """ """
        self.args.update({"sincos": "sin", "factor_period": 1, "flux_offset": 0., 'phase_offset': 0.,
                          'occultation': False
                          }
                         )
        super(PhaseCurveModelEllipsoidal, self)._set_args(args=args)
        if args is not None:
            for key in args:
                if key == 'phase_offset':
                    if not(isinstance(args['phase_offset'], Number) or (args['phase_offset'] == 'param')):
                        raise ValueError(f"Model named {self.model_name} of planet {self.planet.get_name()}: 'phase_offset' should be a number or 'param' (got {args['phase_offset']})")
                else:
                    raise ValueError(f"Model named {self.model_name} of planet {self.planet.get_name()}: args of ellipsoidal model definition can only be in {['phase_offset', ]}")
                self.args[key] = args['factor_period']


class PhaseCurveModelBeaming(PhaseCurveModelSinCos):
    """docstring for PhaseCurveModelBeaming."""

    __category__ = "beaming"

    ################
    # Main functions
    ################

    def __init__(self, model_name, planet, host_star, orbital_models=None, dico_config_model=None):
        super(PhaseCurveModelSinCos, self).__init__(model_name=model_name, planet=planet, host_star=host_star,
                                                    orbital_models=orbital_models, dico_config_model=dico_config_model
                                                    )

    ###################################################
    # Functions directly required by the main functions
    ###################################################

    def _set_args(self, args=None):
        """ """
        self.args.update({"sincos": "cos", "factor_period": 1. / 2., "flux_offset": 0., 'phase_offset': pi,
                          'occultation': False
                          }
                         )
        super(PhaseCurveModelEllipsoidal, self)._set_args(args=args)


class PhaseCurveModelGauss(Core_PlanetStarModel):
    """docstring for PhaseCurveModelGauss."""

    __category__ = "gaussian"

    ################
    # Main functions
    ################

    def __init__(self, model_name, planet, host_star, orbital_models=None, dico_config_model=None):
        super(PhaseCurveModelGauss, self).__init__(model_name=model_name, planet=planet, host_star=host_star,
                                                   orbital_models=orbital_models, dico_config_model=dico_config_model,
                                                   )

    @property
    def flux_offset(self):
        return self.args['flux_offset']

    @property
    def phase_offset(self):
        return self.args['phase_offset']

    @property
    def occultation(self):
        return self.args['occultation']

    ###################################################
    # Functions directly required by the main functions
    ###################################################

    def _set_args(self, args=None):
        """ """
        self.args.update({'flux_offset': 'param', 'phase_offset': 'param', 'occultation': True})
        super(PhaseCurveModelGauss, self)._set_args(args=args)
        if args is not None:
            if set(args.keys()) != set(['flux_offset', 'phase_offset', 'occultation']):
                raise ValueError(f"Model named {self.model_name} of planet {self.planet.get_name()}: gaussian model definition needs to include an args key which contains a dictionary with the following keys: {['flux_offset', 'phase_offset', 'occultation']}")
            if not(isinstance(args['flux_offset'], Number) or (args['flux_offset'] in ['param', 'zero'])):
                raise ValueError(f"Model named {self.model_name} of planet {self.planet.get_name()}: 'flux_offset' should be a number or 'param' or 'zero' (got {args['flux_offset']})")
            self.args['flux_offset'] = args['flux_offset']
            if not(isinstance(args['phase_offset'], Number) or (args['phase_offset'] in ['param'])):
                raise ValueError(f"Model named {self.model_name} of planet {self.planet.get_name()}: 'phase_offset' should be a number or 'param' (got {args['phase_offset']})")
            self.args['phase_offset'] = args['phase_offset']
            if not(isinstance(args['occultation'], bool)):
                raise ValueError(f"Model named {self.model_name} of planet {self.planet.get_name()}: 'occultation' should be a boolean (got {args['occultation']})")
            self.args['occultation'] = args['occultation']

    def _get_l_parameter_basename_planet(self):
        """Return the list of orbital parameter basenames."""
        l_param_basename = ['A', 'sigmaPhi']
        if self.occultation:
            l_param_basename.append('Rrat')
        if self.flux_offset == 'param':
            l_param_basename.append('Foffset')
        if self.phase_offset == 'param':
            l_param_basename.append('Phi')
        return l_param_basename

    def _get_l_parameter_basename_orbit(self, inst_model_fullname=None):
        """Return the list of orbital parameter basenames."""
        if self.occultation:
            l_required_orbital_param_type = ['P', 'tic', 'ew', 'inc', 'aR']
        else:
            l_required_orbital_param_type = ['P', 'tic']
        orbital_model = self.orbital_models.get_model(planet_name=self.planet.get_name(), inst_model_fullname=inst_model_fullname)
        return orbital_model._get_l_parameter_basename(l_required_orbital_param_type=l_required_orbital_param_type,
                                                       inst_model_fullname=inst_model_fullname, object_category=None
                                                       )
    

class PhaseCurveModelKelpThermal(Core_PlanetStarModel):
    """docstring for PhaseCurveModelKelpThermal."""

    __category__ = "kelp-thermal"

    ################
    # Main functions
    ################

    def __init__(self, model_name, planet, host_star, orbital_models=None, dico_config_model=None):
        super(PhaseCurveModelKelpThermal, self).__init__(model_name=model_name, planet=planet, host_star=host_star,
                                                         orbital_models=orbital_models, dico_config_model=dico_config_model,
                                                         )

    @property
    def Model_kwargs(self):
        return self.args['Model_kwargs']

    @property
    def pc_kwargs(self):
        return self.args['pc_kwargs']

    @property
    def stellar_spectrum(self):
        return self.args['Model_kwargs']['stellar_spectrum']

    ###################################################
    # Functions directly required by the main functions
    ###################################################

    def _set_args(self, args=None):
        """ """
        self.args.update({'Model_kwargs': {'lmax': 1, 'filt': None, 'stellar_spectrum': None, 'T_s': None},
                          'pc_kwargs': {'n_theta': 20, 'n_phi': 200, 'cython': True, 'quad': False, 'check_sorted': True},
                          }
                         )
        super(PhaseCurveModelKelpThermal, self)._set_args(args=args)
        if args is not None:
            for key in args:
                if key not in ['Model_kwargs', 'pc_kwargs']:
                    raise ValueError(f"Model named {self.model_name} of planet {self.planet.get_name()}: args dictionary in kelp-thermal model definition can only have the following keys {['Model_kwargs', 'brightness_model_kwargs']} (got {key}).")
            for key in ['filt', 'T_s']:
                if key not in args['Model_kwargs']:
                    raise ValueError(f"Model named {self.model_name} of planet {self.planet.get_name()}: args['Model_kwargs'] should at least contain the keys 'filt' and 'T_s'.")
            for key in args['Model_kwargs']:
                if key == 'lmax':
                    if args['Model_kwargs'][key] != 1:
                        raise ValueError(f"Model named {self.model_name} of planet {self.planet.get_name()}: currently the only possible value for args['Model_kwargs']['lmax'] is 1")
                elif key == 'filt':
                    if not(isinstance(args['Model_kwargs'][key], Filter)):
                        raise ValueError(f"Model named {self.model_name} of planet {self.planet.get_name()}: args['Model_kwargs']['filt'] should be an instance of kelp.Filter")
                elif key == 'stellar_spectrum':
                    if not(isinstance(args['Model_kwargs'][key], StellarSpectrum) or (args['Model_kwargs'][key] is None)):
                        raise ValueError(f"Model named {self.model_name} of planet {self.planet.get_name()}: args['Model_kwargs']['stellar_spectrum'] should be an instance of kelp.StellarSpectrum")
                elif key == 'T_s':
                    if not(isinstance(args['Model_kwargs'][key], Number) and (args['Model_kwargs'][key] > 0)):
                        raise ValueError(f"Model named {self.model_name} of planet {self.planet.get_name()}: args['Model_kwargs']['T_s'] should be a positive number (got {args['Model_kwargs'][key]})")
                else:
                    raise ValueError(f"Model named {self.model_name} of planet {self.planet.get_name()}: Valid keys for args['Model_kwargs'] are {['lmax', 'filt', 'stellar_spectrum', 'T_s']} (got {key})")
                self.args['Model_kwargs'][key] = args['Model_kwargs'][key]
            for key in args['pc_kwargs']:
                if key in ['n_theta', 'n_phi']:
                    if not(isinstance(args['pc_kwargs'][key], int) and (args['pc_kwargs'][key] > 0)):
                        raise ValueError(f"Model named {self.model_name} of planet {self.planet.get_name()}: args['pc_kwargs']['{key}'] should be a strictly positive int (got {args['pc_kwargs'][key]})")
                elif key in ['check_sorted', 'quad', 'cython']:
                    if not(isinstance(args['pc_kwargs'][key], bool)):
                        raise ValueError(f"Model named {self.model_name} of planet {self.planet.get_name()}: args['pc_kwargs']['{key}'] should be a boolean (got {args['pc_kwargs'][key]})")
                else:
                    raise ValueError(f"Model named {self.model_name} of planet {self.planet.get_name()}: Valid keys for args['pc_kwargs'] are {['n_theta', 'n_phi', 'cython', 'quad', 'check_sorted']} (got {key})")
                self.args['pc_kwargs'][key] = args['pc_kwargs'][key]

    def _get_l_parameter_basename_planet(self):
        """Return the list of orbital parameter basenames."""
        return ['Rrat', 'f', 'alpha', 'omegadrag', 'AB', 'c11', 'hotspotoffset']

    def _get_l_parameter_basename_star(self):
        """Return the list of orbital parameter basenames."""
        if self.stellar_spectrum is None:
            return ['Teff']
        else:
            return []

    def _get_l_parameter_basename_orbit(self, inst_model_fullname=None):
        """Return the list of orbital parameter basenames."""
        l_required_orbital_param_type = ['P', 'tic', 'ew', 'inc', 'aR']
        orbital_model = self.orbital_models.get_model(planet_name=self.planet.get_name(), inst_model_fullname=inst_model_fullname)
        return orbital_model._get_l_parameter_basename(l_required_orbital_param_type=l_required_orbital_param_type,
                                                       inst_model_fullname=inst_model_fullname, object_category=None
                                                       )


class PhaseCurveModelSpidermanZhang(Core_PlanetStarModel):
    """docstring for PhaseCurveModelSpidermanZhang."""

    __category__ = "spiderman-zhang"

    ################
    # Main functions
    ################

    def __init__(self, model_name, planet, host_star, orbital_models=None, dico_config_model=None):
        super(PhaseCurveModelSpidermanZhang, self).__init__(model_name=model_name, planet=planet, host_star=host_star,
                                                            orbital_models=orbital_models, dico_config_model=dico_config_model,
                                                            )

    @property
    def brightness_model(self):
        return self.args['ModelParams_kwargs']['brightness_model']

    @property
    def lightcurve_kwargs(self):
        return self.argss['lightcurve_kwargs']

    ###################################################
    # Functions directly required by the main functions
    ###################################################

    def _set_args(self, args=None):
        """ """
        self.args.update({'ModelParams_kwargs': {'brightness_model': 'zhang', 'stellar_model': None},
                          'attributes': {"filter": None, "l1": None, "l2": None, "n_layers": 5},
                          'lightcurve_kwargs': {}
                          }
                         )
        super(PhaseCurveModelSpidermanZhang, self)._set_args(args=args)
        if args is not None:
            for key in ['ModelParams_kwargs', 'attributes']:
                if key not in args:
                    raise ValueError(f"Model named {self.model_name} of planet {self.planet.get_name()}: args should at least contain the keys 'ModelParams_kwargs', 'attributes'.")
            for key in args:
                if key == 'ModelParams_kwargs':
                    for key in ['stellar_model']:
                        if key not in args['ModelParams_kwargs']:
                            raise ValueError(f"Model named {self.model_name} of planet {self.planet.get_name()}: args['ModelParams_kwargs'] should at least contain the keys 'stellar_model'.")
                    for key in args['ModelParams_kwargs']:
                        if key == 'stellar_model':
                            if not(args['ModelParams_kwargs'][key] in ['blackbody', 'PHOENIX']):
                                raise ValueError(f"Model named {self.model_name} of planet {self.planet.get_name()}: currently the only possible values for args['ModelParams_kwargs']['stellar_model'] are {['blackbody', 'PHOENIX']}")
                        else:
                            raise ValueError(f"Model named {self.model_name} of planet {self.planet.get_name()}: Valid keys for args['ModelParams_kwargs'] are {['stellar_model']} (got {key})")
                        self.args['ModelParams_kwargs'][key] = args['ModelParams_kwargs'][key]
                elif key == 'attributes':
                    for key in ['filter', 'l1', 'l2']:
                        if key not in args['attributes']:
                            raise ValueError(f"Model named {self.model_name} of planet {self.planet.get_name()}: args['attributes'] should at least contain the keys ['filter', 'l1', 'l2'].")
                    for key in args['attributes']:
                        if key in ['l1', 'l2']:
                            if not(isinstance(args['attributes'][key], Number) and (args['attributes'][key] > 0)):
                                raise ValueError(f"Model named {self.model_name} of planet {self.planet.get_name()}: args['attributes']['{key}'] should be a strictly positive number (got {args['attributes'][key]})")
                        if key == 'n_layers':
                            if not(isinstance(args['attributes'][key], int) and (args['attributes'][key] > 0)):
                                raise ValueError(f"Model named {self.model_name} of planet {self.planet.get_name()}: args['attributes']['{key}'] should be a strictly positive int (got {args['attributes'][key]})")
                        elif key == 'filter':
                            if not(isinstance(args['attributes'][key], str)):
                                raise ValueError(f"Model named {self.model_name} of planet {self.planet.get_name()}: args['attributes']['{key}'] should be the path of an existing file which specifies the filters response function of the observations, got {args['attributes'][key]})")
                        else:
                            raise ValueError(f"Model named {self.model_name} of planet {self.planet.get_name()}: Valid keys for args['attributes'] are {['filter', 'l1', 'l2', 'n_layers']} (got {key})")
                        self.args['attributes'][key] = args['attributes'][key]
                elif key == 'lightcurve_kwargs':
                    for key in args['lightcurve_kwargs']:
                        if key == 'stellar_grid':
                            if not(isinstance(args['lightcurve_kwargs'][key], list) and (len(args['lightcurve_kwargs'][key]) == 2)):
                                raise ValueError(f"Model named {self.model_name} of planet {self.planet.get_name()}: args['lightcurve_kwargs']['{key}'] should be produce by the spiderman.stellar_grid.gen_grid function.")
                        else:
                            raise ValueError(f"Model named {self.model_name} of planet {self.planet.get_name()}: Valid keys for args['lightcurve_kwargs'] are {['stellar_grid']} (got {key})")
                        self.args['attributes'][key] = args['attributes'][key]

    def _get_l_parameter_basename_planet(self):
        """Return the list of orbital parameter basenames."""
        return ['Rrat', 'xi', 'T_n', 'delta_T', 'a', 'u1', 'u2']

    def _get_l_parameter_basename_star(self):
        """Return the list of orbital parameter basenames."""
        return ['Teff']

    def _get_l_parameter_basename_orbit(self, inst_model_fullname=None):
        """Return the list of orbital parameter basenames."""
        l_required_orbital_param_type = ['P', 'tic', 'ew', 'inc', 'aR']
        orbital_model = self.orbital_models.get_model(planet_name=self.planet.get_name(), inst_model_fullname=inst_model_fullname)
        return orbital_model._get_l_parameter_basename(l_required_orbital_param_type=l_required_orbital_param_type,
                                                       inst_model_fullname=inst_model_fullname, object_category=None
                                                       )


class PhaseCurveModelLambertian(Core_PlanetStarModel):
    """docstring for PhaseCurveModelLambertian."""

    __category__ = "lambertian"

    ################
    # Main functions
    ################

    def __init__(self, model_name, planet, host_star, orbital_models=None, dico_config_model=None):
        super(PhaseCurveModelLambertian, self).__init__(model_name=model_name, planet=planet, host_star=host_star,
                                                        orbital_models=orbital_models, dico_config_model=dico_config_model,
                                                        )

    ###################################################
    # Functions directly required by the main functions
    ###################################################

    def _get_l_parameter_basename_planet(self):
        """Return the list of orbital parameter basenames."""
        return ['A']

    def _get_l_parameter_basename_orbit(self, inst_model_fullname=None):
        """Return the list of orbital parameter basenames."""
        l_required_orbital_param_type = ['P', 'tic', 'ew', 'inc', 'aR']
        orbital_model = self.orbital_models.get_model(planet_name=self.planet.get_name(), inst_model_fullname=inst_model_fullname)
        return orbital_model._get_l_parameter_basename(l_required_orbital_param_type=l_required_orbital_param_type,
                                                       inst_model_fullname=inst_model_fullname, object_category=None
                                                       )


class OccultationModelBatman(Core_PlanetStarModel):
    """docstring for OccultationModelBatman."""

    __category__ = "batman"

    ################
    # Main functions
    ################

    def __init__(self, model_name, planet, host_star, orbital_models=None, dico_config_model=None):
        super(OccultationModelBatman, self).__init__(model_name=model_name, planet=planet, host_star=host_star,
                                                     orbital_models=orbital_models, dico_config_model=dico_config_model,
                                                     )

    ###################################################
    # Functions directly required by the main functions
    ###################################################

    def _get_l_parameter_basename_planet(self):
        """Return the list of orbital parameter basenames."""
        return ['Rrat', 'Frat']

    def _get_l_parameter_basename_orbit(self, inst_model_fullname=None):
        """Return the list of orbital parameter basenames."""
        l_required_orbital_param_type = ['P', 'tic', 'ew', 'inc', 'aR']
        orbital_model = self.orbital_models.get_model(planet_name=self.planet.get_name(), inst_model_fullname=inst_model_fullname)
        return orbital_model._get_l_parameter_basename(l_required_orbital_param_type=l_required_orbital_param_type,
                                                       inst_model_fullname=inst_model_fullname, object_category=None
                                                       )
