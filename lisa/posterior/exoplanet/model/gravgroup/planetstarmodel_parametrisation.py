from .....tools.metaclasses import MandatoryReadOnlyAttr
from .planetstarmodel import (spiderman_imported, kelp_imported,
                              OrbitalModelBatman,
                              RVKeplerianModelRadvel,
                              TransitModelBatman,
                              OccultationModelBatman,
                              PhaseCurveModelSinCos, PhaseCurveModelBeaming, PhaseCurveModelEllipsoidal,
                              PhaseCurveModelLambertian, PhaseCurveModelKelpThermal, PhaseCurveModelSpidermanZhang,
                              PhaseCurveModelGauss, PhaseCurveModelKelpReflectHomogeneous, PhaseCurveModelKelpReflectInhomogeneous
                              )


class Core_PlanetStarModels_1model4allinst(metaclass=MandatoryReadOnlyAttr):
    """docstring for Core_PlanetStarModels_1model4allinst.

    Store the configuration of the models that are constrained to be identical for all instrument model
    (like the keplerian models). It provides convenience functions to create the relevant parameter
    and access them.

    Arguments
    ---------
    l_planet                : list of Planet
    host_star               : Star
    default_model_category  : str
        Model category to use by default
    orbital_models          : OrbitalModel instance
        OrbitalModel instance which defines the available orbital models
    default_do              : bool
        Whether or not the model should be done by default.
    """

    __mandatoryattrs__ = ['l_model_class']
    # l_model_class is a list of available model (Subclasses of PlanetStarModel).

    ################
    # Main functions
    ################
    def __init__(self, l_planet, host_star, default_model_category, orbital_models=None, default_do=False):
        """Initialise the instance which will contain the model configuration."""
        self.__planets = {planet.get_name(): planet for planet in l_planet}
        self.__host_star = host_star
        self.__model_classes = {model.category: model for model in self.l_model_class}
        self.__orbital_models = orbital_models
        self._models_config = self._init_model_config(default_do=default_do)
        self._define_default_model(default_model_category=default_model_category)

    @property
    def dict2print(self):
        """Used to print the content in the parametrisation file."""
        dict2print = self._models_config.copy()
        for planet_name in dict2print:
            dict2print[planet_name]['model'] = dict2print[planet_name]['model'].dict2print
        return dict2print

    def load_config(self, dico_config):
        """Load the content of the configuration dictionary read from the parametrisation file

        Argument
        --------
        dico_config : dict
        """
        if set(dico_config.keys()) != set(self.planets.keys()):
            raise ValueError(f"The planet names used in the parametrisation file ({set(dico_config.keys())}) do not correspond to the expected ones ({set(self.planets.keys())})")
        for planet_name, dico_config_planet in dico_config.items():
            if set(dico_config_planet.keys()) != set(['do', 'model']):
                raise ValueError(f"The keys of the config dictionary ({set(dico_config_planet.keys())}) for planet {planet_name:} are not the ones expected ({set(['do', 'model'])})")
            if not(isinstance(dico_config_planet['do'], bool)):
                raise ValueError(f"dico_config[{planet_name}]['do'] should be a boolean (got {dico_config_planet['do']})")
            self._set_do(planet_name=planet_name, do=dico_config_planet['do'])
            dico_config_model_planet = dico_config_planet['model']
            if 'category' not in dico_config_model_planet:
                raise ValueError(f"dico_config[{planet_name}]['model'] should at least contain a keys 'category' which specify the category of the model to use ({self.l_available_model_category})")
            model_category = dico_config_model_planet.pop('category')
            self._define_model(planet_name=planet_name, model_category=model_category, dico_config_model=dico_config_model_planet,
                               overwrite=True
                               )

    def get_do(self, planet_name):
        """Get the do for the model.

        If do is True it means that the model should be done. To be used by the datasimulator creator functions

        Argument
        --------
        do  : bool
        """
        return self._models_config[planet_name]["do"]

    def get_model(self, planet_name):
        """Get the do for the model.

        If do is True it means that the model should be done. To be used by the datasimulator creator functions

        Argument
        --------
        do  : bool
        """
        return self._models_config[planet_name]["model"]

    #################################################################
    # Functions directly or indirectly required by the main functions
    #################################################################

    def _define_default_model(self, default_model_category):
        """"""
        for planet_name in self._models_config:
            self._define_model(planet_name=planet_name, model_category=default_model_category,
                               dico_config_model=None, overwrite=False
                               )

    def _define_model(self, planet_name, model_category, dico_config_model=None, overwrite=False):
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
        if planet_name not in self.planets:
            raise ValueError(f"There is no Planet of name {planet_name} in the model.")
        if not(overwrite) and (self._models_config[planet_name]['model'] is not None):
            raise ValueError("A model is already defined and overwrite is False.")
        if not(self._is_available_model_category(model_category=model_category)):
            raise ValueError(f"{model_category} is not in the list of available model categories ({self.l_available_model_category}).")
        self._models_config[planet_name]["model"] = self.model_classes[model_category](model_name='',
                                                                                       planet=self.planets[planet_name],
                                                                                       host_star=self.host_star,
                                                                                       orbital_models=self.orbital_models,
                                                                                       dico_config_model=dico_config_model
                                                                                       )

    def _set_do(self, planet_name, do):
        """Set the do for the model.

        If do is True it means that the model should be done.

        Argument
        --------
        do  : bool
        """
        if not(isinstance(do, bool)):
            raise ValueError(f"do should be a boolean (got {do})")
        self._models_config[planet_name]["do"] = do

    def _is_available_model_category(self, model_category):
        """Return True if the model_category provided is amongst the available model categories.

        If no list of available model categories have been provided, this function always returns True.

        Argument
        --------
        model_category  : str

        Return
        ------
        isavailable : bool
        """
        return model_category in self.l_available_model_category

    def _init_model_config(self, default_do):
        """Return the dictionary with the initialised content for self._model_config.

        Argument
        --------
        default_do  : bool
            Should the models be done by default ?

        Return
        ------
        model_config    : str
        """
        return {planet.get_name(): {'do': default_do, 'model': None} for planet in self.planets.values()}

    @property
    def planets(self):
        """Dictionary of Planet instances. The keys are the planet (short) names"""
        return self.__planets

    @property
    def host_star(self):
        """Host star instance"""
        return self.__host_star

    @property
    def model_classes(self):
        """Dictionary with defines the available models. Keys are model_category and value are the
        model classes (subclasses of PlanetStarModel)"""
        return self.__model_classes

    @property
    def l_available_model_category(self):
        """List of available model category (list of str or None)"""
        return list(self.model_classes.keys())

    @property
    def orbital_models(self):
        """Instance of the OrbitalModel class which defines the configuration of orbital models"""
        return self.__orbital_models

    #################################
    # Convenience/Debugging functions
    #################################

    def __repr__(self):
        return (f"{self.__class__.__name__}(l_planet={list(self.planets.values())}, host_star={self.host_star}, "
                f"orbital_models={self.orbital_models})"
                )


class Core_PlanetStarModels_lmodel1inst(Core_PlanetStarModels_1model4allinst):
    """docstring for Core_PlanetStarModels_lmodel1inst.

    Store the configuration of the models that can be different for each instrument model (like the transit,
    occultation and phase curve models). It provides convenience functions to create the relevant parameter
    and access them.

    Arguments
    ---------
    l_planet                : list of Planet
    host_star               : Star
    l_inst_model_fullname   : list of str
        List of model full name associated with these models
    default_model_category  : str
        Model category to use by default
    orbital_models          : OrbitalModel instance
        OrbitalModel instance which defines the available orbital models
    default_do              : bool
        Whether or not the model should be done by default.
    """

    ################
    # Main functions
    ################
    def __init__(self, l_planet, host_star, l_inst_model_fullname, default_model_category,
                 orbital_models=None, default_do=False
                 ):
        self.__l_inst_model_fullname = l_inst_model_fullname
        super(Core_PlanetStarModels_lmodel1inst, self).__init__(l_planet=l_planet, host_star=host_star,
                                                                default_model_category=default_model_category,
                                                                orbital_models=orbital_models, default_do=default_do
                                                                )

    @property
    def dict2print(self):
        """Used to print the content in the parametrisation file."""
        dict2print = self._models_config.copy()
        for planet_name in dict2print:
            dict2print[planet_name] = dict2print[planet_name].copy()
            dict2print[planet_name]['model_definitions'] = dict2print[planet_name]['model_definitions'].copy()
            for model_name in dict2print[planet_name]['model_definitions']:
                dict2print[planet_name]['model_definitions'][model_name] = dict2print[planet_name]['model_definitions'][model_name].dict2print
        return dict2print

    def load_config(self, dico_config):
        """Load the content of the configuration dictionary read from the parameter file

        Argument
        --------
        dico_config : dict
        """
        if set(dico_config.keys()) != set(self.planets.keys()):
            raise ValueError(f"The planet names used in the parametrisation file ({set(dico_config.keys())}) do not correspond to the expected ones ({set(self.planets.keys())})")
        for planet_name, dico_config_planet in dico_config.items():
            if set(dico_config_planet.keys()) != set(['do', 'model_definitions', 'model4instrument']):
                raise ValueError(f"The keys of the config dictionary ({list(dico_config_planet.keys())}) for planet {planet_name:} are not the ones expected ({set(['do', 'model_definitions', 'model4instrument'])})")
            if not(isinstance(dico_config_planet['do'], bool)):
                raise ValueError(f"dico_config[{planet_name}]['do'] should be a boolean (got {dico_config_planet['do']})")
            self._set_do(planet_name=planet_name, do=dico_config_planet['do'])
            for model_name, dico_config_model_planet in dico_config_planet['model_definitions'].items():
                if 'category' not in dico_config_model_planet:
                    raise ValueError(f"dico_config[{planet_name}]['model_definitions']['{model_name}'] should at least contain a keys 'category' which specify the category of the model to use ({self.l_available_model_category})")
                model_category = dico_config_model_planet.pop('category')
                self._define_model(model_name=model_name, planet_name=planet_name, model_category=model_category,
                                   dico_config_model=dico_config_model_planet, overwrite=True
                                   )
            if set(dico_config_planet['model4instrument'].keys()) != set(self.l_inst_model_fullname):
                raise ValueError(f"The list of instrument model name in dico_config[{planet_name}]['model4instrument'] doesn't match the expected list.\n"
                                 f"The following keys of dico_config[{planet_name}]['model4instrument'] are not expected: {set(dico_config_planet['model4instrument'].keys()) - set(self.l_inst_model_fullname)}\n"
                                 f"The following keys of dico_config[{planet_name}]['model4instrument'] expected but not present: {set(self.l_inst_model_fullname) - set(dico_config_planet['model4instrument'].keys())}\n"
                                 )
            for inst_model_fullname, model_names in dico_config_planet['model4instrument'].items():
                self._set_model_names_4_inst_model(planet_name=planet_name, inst_model_fullname=inst_model_fullname, model_names=model_names)

    def get_l_model(self, planet_name, inst_model_fullname):
        """Get the do for the model.

        If do is True it means that the model should be done. To be used by the datasimulator creator functions

        Argument
        --------
        do  : bool
        """
        if planet_name not in self.planets:
            raise ValueError(f"planet name {planet_name} is not in an available planet in the model ({list(self.planets.keys())})")
        if inst_model_fullname not in self.l_inst_model_fullname:
            raise ValueError(f"Instrument model {inst_model_fullname} is not in an available instrument model in the model ({self.l_inst_model_fullname})")
        return [self._models_config[planet_name]['model_definitions'][model_name]
                for model_name in self._get_l_model_name(planet_name=planet_name, inst_model_fullname=inst_model_fullname)
                ]

    #################################################################
    # Functions directly or indirectly required by the main functions
    #################################################################

    def _define_default_model(self, default_model_category):
        """"""
        for planet_name in self._models_config:
            self._define_model(model_name='', planet_name=planet_name, model_category=default_model_category,
                               dico_config_model=None, overwrite=False
                               )

    def _define_model(self, model_name, planet_name, model_category, dico_config_model=None, overwrite=False):
        """Define the model for the planet

        Arguments
        ---------
        planet_name                     : str
            Name of the planet for which you are defining the model
        model_name                      : str
            Name provided to the model. It will be appended to the name of the parameters (except for the orbital parameters)
        model_category                  : str
            Catergory of the model
        dico_config_model               : dict
        overwrite                       : bool
            Wheter or not you wish to overwrite if the model is already defined
        """
        if planet_name not in self.planets:
            raise ValueError(f"There is no Planet of name {planet_name} in the model.")
        if not(overwrite) and (model_name in self._models_config[planet_name]["model_definitions"]):
            raise ValueError(f"A model of name {model_name} already exists and overwrite is False.")
        if not(self._is_available_model_category(model_category=model_category)):
            raise ValueError(f"{model_category} is not in the list of available model categories ({self.l_available_model_category}).")
        (self._models_config[planet_name]["model_definitions"]
         [model_name]) = self.model_classes[model_category](model_name=model_name, planet=self.planets[planet_name],
                                                            host_star=self.host_star, orbital_models=self.orbital_models,
                                                            dico_config_model=dico_config_model
                                                            )

    def _init_model_config(self, default_do):
        """Return the dictionary with the initialised content for self._model_config.

        Argument
        --------
        default_do  : bool
            Should the models be done by default ?

        Return
        ------
        model_config    : str
        """
        return {planet.get_name(): {'do': default_do,
                                    'model4instrument': {instmodfullname: [''] for instmodfullname in self.l_inst_model_fullname},
                                    'model_definitions': {},
                                    }
                for planet in self.planets.values()
                }

    def _set_model_names_4_inst_model(self, planet_name, inst_model_fullname, model_names):
        """Set the model_name for a given instrument model
        """
        if not(isinstance(model_names, list)):
            raise ValueError(f"dico_config[{planet_name}]['model4instrument'][{inst_model_fullname}] should be a list of model names (even if it has only one element)")
        for model_name in model_names:
            if not(model_name in self._get_l_available_model_name(planet_name=planet_name)):
                raise ValueError(f"{model_name} is not the name of a model that is currently defined.")
        self._models_config[planet_name]["model4instrument"][inst_model_fullname] = model_names

    @property
    def l_inst_model_fullname(self):
        """List of instrument model full names associated with these models"""
        return self.__l_inst_model_fullname

    def _get_l_available_model_name(self, planet_name):
        """List of currently available model names for a planet.

        Argument
        --------
        planet_name : str

        Return
        ------
        l_available_model_name  : list of str
        """
        return list(self._models_config[planet_name]['model_definitions'].keys())

    def _get_l_model_name(self, planet_name, inst_model_fullname):
        """
        """
        return self._models_config[planet_name]['model4instrument'][inst_model_fullname]

    #################################
    # Convenience/Debugging functions
    #################################

    def __repr__(self):
        return (f"{self.__class__.__name__}(l_planet={list(self.planets.values())}, host_star={self.host_star}, "
                f"l_inst_model_fullname={self.l_inst_model_fullname}, "
                f"orbital_models={self.orbital_models})"
                )

    def get_model(self, planet_name, inst_model_fullname=None):
        """"""
        raise NotImplementedError("You should not use get_model in this case but get_l_model.")


class Core_PlanetStarModels_1model1inst(Core_PlanetStarModels_lmodel1inst):
    """docstring for Core_PlanetStarModels_1model1inst.

    Store the configuration of the models that can be different for each instrument model (like the transit,
    occultation and phase curve models). It provides convenience functions to create the relevant parameter
    and access them.

    Arguments
    ---------
    l_planet                : list of Planet
    host_star               : Star
    l_inst_model_fullname   : list of str
        List of model full name associated with these models
    default_model_category  : str
        Model category to use by default
    orbital_models          : OrbitalModel instance
        OrbitalModel instance which defines the available orbital models
    default_do              : bool
        Whether or not the model should be done by default.
    """

    ################
    # Main functions
    ################

    def __init__(self, l_planet, host_star, l_inst_model_fullname, default_model_category,
                 orbital_models=None, default_do=False
                 ):
        super(Core_PlanetStarModels_1model1inst, self).__init__(l_planet=l_planet, host_star=host_star, l_inst_model_fullname=l_inst_model_fullname,
                                                                default_model_category=default_model_category,
                                                                orbital_models=orbital_models, default_do=default_do
                                                                )

    def get_model(self, planet_name, inst_model_fullname):
        """Get the model for a given planet name and a given instrument model full name.
        """
        if planet_name not in self.planets:
            raise ValueError(f"planet name {planet_name} is not in an available planet in the model ({list(self.planets.keys())})")
        if inst_model_fullname not in self.l_inst_model_fullname:
            raise ValueError(f"Instrument model {inst_model_fullname} is not in an available instrument model in the model ({self.l_inst_model_fullname})")
        return self._models_config[planet_name]['model_definitions'][self._get_model_name(planet_name=planet_name,
                                                                                          inst_model_fullname=inst_model_fullname
                                                                                          )
                                                                     ]

    #################################################################
    # Functions directly or indirectly required by the main functions
    #################################################################

    def _init_model_config(self, default_do):
        """Return the dictionary with the initialised content for self._model_config.

        Argument
        --------
        default_do  : bool
            Should the models be done by default ?

        Return
        ------
        model_config    : str
        """
        return {planet.get_name(): {'do': default_do,
                                    'model4instrument': {instmodfullname: '' for instmodfullname in self.l_inst_model_fullname},
                                    'model_definitions': {},
                                    }
                for planet in self.planets.values()
                }

    def _set_model_names_4_inst_model(self, planet_name, inst_model_fullname, model_names):
        """Set the model_name for a given instrument model
        """
        if not(model_names in self._get_l_available_model_name(planet_name=planet_name)):
            raise ValueError(f"{model_names} from dico_config[{planet_name}]['model4instrument'][{inst_model_fullname}] is not an available model name ({self._get_l_available_model_name(planet_name=planet_name)})")
        self._models_config[planet_name]["model4instrument"][inst_model_fullname] = model_names

    def _get_model_name(self, planet_name, inst_model_fullname):
        """
        """
        return self._models_config[planet_name]['model4instrument'][inst_model_fullname]

    #################################
    # Convenience/Debugging functions
    #################################

    def __repr__(self):
        return (f"{self.__class__.__name__}(l_planet={list(self.planets.values())}, host_star={self.host_star}, "
                f"l_inst_model_fullname={self.l_inst_model_fullname}, "
                f"orbital_models={self.orbital_models})"
                )

    def get_l_model(self, planet_name, inst_model_fullname=None):
        """"""
        raise NotImplementedError("You should not use get_l_model in this case but get_model")


class OrbitalModels(Core_PlanetStarModels_1model1inst):
    """docstring for OrbitalModel.

    Definition of the configuration of orbital models

    Arguments
    ---------
    l_planet                        : list of Planet
    host_star                       : Star
    l_inst_model_fullname           : list of str
        List of model full name associated with these models
    """

    __l_model_class__ = [OrbitalModelBatman, ]

    def __init__(self, l_planet, host_star, l_inst_model_fullname=[]):
        default_model_category = 'batman'
        super(OrbitalModels, self).__init__(l_planet=l_planet, host_star=host_star, l_inst_model_fullname=l_inst_model_fullname,
                                            default_model_category=default_model_category,
                                            orbital_models=None, default_do=True
                                            )

    def __repr__(self):
        return (f"{self.__class__.__name__}(l_planet={list(self.planets.values())}, host_star={self.host_star}, "
                f"l_inst_model_fullname={self.l_inst_model_fullname})"
                )


class RVKeplerianModels(Core_PlanetStarModels_1model4allinst):
    """docstring for KeplerianModel.

    Definition of the configuration of keplerian RV models

    Arguments
    ---------
    l_planet                        : list of Planet
    host_star                       : Star
    orbitalmodel_instance           : OrbitalModels
    """

    __l_model_class__ = [RVKeplerianModelRadvel, ]

    def __init__(self, l_planet, host_star, orbital_models):
        default_model_category = 'radvel'
        super(RVKeplerianModels, self).__init__(l_planet=l_planet, host_star=host_star,
                                                default_model_category=default_model_category, orbital_models=orbital_models,
                                                default_do=True
                                                )

    def __repr__(self):
        return (f"{self.__class__.__name__}(l_planet={list(self.planets.values())}, host_star={self.host_star}, "
                f"orbital_models={self.orbital_models!r})"
                )


class TransitModels(Core_PlanetStarModels_1model1inst):
    """docstring for TransitModel.

    Definition of the configuration of keplerian RV models

    Arguments
    ---------
    l_planet                        : list of Planet
    host_star                       : Star
    l_inst_model_fullname           : list of str
        List of model full name associated with these models
    orbitalmodel_instance           : OrbitalModels
    """

    __l_model_class__ = [TransitModelBatman, ]

    def __init__(self, l_planet, host_star, l_inst_model_fullname, orbital_models):
        default_model_category = 'batman'
        super(TransitModels, self).__init__(l_planet=l_planet, host_star=host_star, l_inst_model_fullname=l_inst_model_fullname,
                                            default_model_category=default_model_category,
                                            orbital_models=orbital_models, default_do=True
                                            )

    def __repr__(self):
        return (f"{self.__class__.__name__}(l_planet={list(self.planets.values())}, host_star={self.host_star}, "
                f"l_inst_model_fullname={self.l_inst_model_fullname}, orbital_models={self.orbital_models!r})"
                )


class PhaseCurveModels(Core_PlanetStarModels_lmodel1inst):
    """docstring for PhaseCurveModel.

    Definition of the configuration of keplerian RV models

    Arguments
    ---------
    l_planet                        : list of Planet
    host_star                       : Star
    orbitalmodel_instance           : OrbitalModels
    """
    __l_model_class__ = [PhaseCurveModelSinCos, PhaseCurveModelLambertian, PhaseCurveModelEllipsoidal, PhaseCurveModelBeaming, PhaseCurveModelGauss, ]
    if spiderman_imported:
        __l_model_class__.append(PhaseCurveModelSpidermanZhang)
    if kelp_imported:
        __l_model_class__.extend([PhaseCurveModelKelpThermal, PhaseCurveModelKelpReflectHomogeneous, PhaseCurveModelKelpReflectInhomogeneous])

    def __init__(self, l_planet, host_star, l_inst_model_fullname, orbital_models):
        default_model_category = 'sincos'
        super(PhaseCurveModels, self).__init__(l_planet=l_planet, host_star=host_star, l_inst_model_fullname=l_inst_model_fullname,
                                               default_model_category=default_model_category,
                                               orbital_models=orbital_models, default_do=False
                                               )

    def __repr__(self):
        return (f"{self.__class__.__name__}(l_planet={list(self.planets.values())}, host_star={self.host_star}, "
                f"l_inst_model_fullname={self.l_inst_model_fullname}, orbitalmodel_instance={self.orbital_models!r})"
                )


class OccultationModels(Core_PlanetStarModels_1model1inst):
    """docstring for TransitModels.

    Definition of the configuration of keplerian RV models

    Arguments
    ---------
    l_planet                        : list of Planet
    host_star                       : Star
    orbitalmodel_instance           : OrbitalModels
    """

    __l_model_class__ = [OccultationModelBatman, ]

    def __init__(self, l_planet, host_star, l_inst_model_fullname, orbital_models):
        default_model_category = 'batman'
        super(OccultationModels, self).__init__(l_planet=l_planet, host_star=host_star, l_inst_model_fullname=l_inst_model_fullname,
                                                default_model_category=default_model_category,
                                                orbital_models=orbital_models, default_do=False
                                                )

    def __repr__(self):
        return (f"{self.__class__.__name__}(l_planet={list(self.planets.values())}, host_star={self.host_star}, "
                f"l_inst_model_fullname={self.l_inst_model_fullname}, orbital_models={self.orbital_models!r})"
                )
