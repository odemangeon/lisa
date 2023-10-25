"""
Gravitational group (gravgroup) module.

The objective of this module is to define the GravGroup class.
A GravGroup intance is a group of gravitationnaly bond objects (stars or planets).
It could be:
- a stellar planetary system (one star, and one or several planets),
- a binary system (two star, no planets),
- a herarchical triple system (two stars, one planet orbiting around one of the stars)
- a circum binary system (a planet orbiting, a binary star)
- any combinaison of stars and planets (for now I think it should contain at least two objects
  including at least a star so that it produces a variable signal in RV and or LC)

@TODO:
    - Move the part of load_parameter_file that update one parameter value to parameter.py
    - Log info the creation of stars and planets in a model
    - Deal with fitting transit times individually
    - Deal with limb darkening coefficients parametrisation
    - Redefine the get_list_main_params routine in gravgroup so that it give the parametrisation of
      the planets and stars inside it.
    - Implement subgravgroups in GravGroup
    - Transform the attributes transit_model, rv_model and ld_model into set and get properties
"""
from loguru import logger
# from os.path import isfile, join
from string import ascii_lowercase
from string import ascii_uppercase
from textwrap import dedent
from pprint import pformat

from .planetstarmodel_parametrisation import OrbitalModels
from .LC_instcat_model import LC_InstCat_Model
from .RV_instcat_model import RV_InstCat_Model
from .parametrisation_gravgroup import GravGroup_Parametrisation
from ..celestial_bodies import Star, Planet
# from ...dataset_and_instrument.lc import LC_inst_cat
# from ...dataset_and_instrument.rv import RV_inst_cat
from ...likelihood.GP1D_noisemodel import GP1D_Noise_Model
from ....core.model.core_model import Core_Model, create_key, load_key
from ....core.model.indicator_model.IND_instcat_model import IND_InstCat_Model
from ....core.likelihood.gaussian_noisemodel import Gaussian_Noise_Model
from .....tools.miscellaneous import spacestring_like


# from pdb import set_trace


class GravGroup(GravGroup_Parametrisation, Core_Model):  # GravGroup_Parametrisation has to be before Core_Model to override Core_Parametrisation
    """docstring for GravGroup."""

    ## Model category string
    __category__ = "GravitionalGroups"

    ## Set of possible instrument categories (Used by Core_Model._check_dataset_instcat)
    __instcat_model_classes__ = [LC_InstCat_Model, RV_InstCat_Model, IND_InstCat_Model]

    ## Set of possible noise model categories
    __noise_model_classes__ = [Gaussian_Noise_Model, GP1D_Noise_Model]

    ## Does the model requires a model parametrisation file
    __has_model_paramfile__ = True

    # Available orbital models
    _orbital_models = ["batman", ]

    _ext_plonly = "_only"  # Extension used by the datasimulator creator for the planet only datasimulator (withou the instrument nor the star)

    ###########################################
    ## Methods for interface with other modules
    ###########################################

    def _finish_init_modelparam(self, stars, planets):
        """docstring GravGroup finish init method."""
        # Finish the initialisation
        super(GravGroup, self).finish_init(self)

        # Initialise the stars in the system
        ## stars: ordered dictionary of the stars in the grav group
        if isinstance(stars, int):
            if stars >= 1:
                self.add_stars(number=stars)
            else:
                raise ValueError("If you specify the number of stars, it should be "
                                 "strictly positive ! Got {}".format(stars))
        elif isinstance(stars, list) and isinstance(stars[0], str):
            self.add_stars(number=len(stars), names=stars)
        elif stars is None:
            pass
        else:
            raise ValueError("stars should be either a strictly positive int or a list of sting "
                             "or None. {}".format(stars))
        # Initialise the planets in the system
        ## planets: ordered dictionary of the planets in the grav group
        if isinstance(planets, int):
            if planets >= 1:
                self.add_planets(number=planets)
            else:
                raise ValueError("If you specify the number of planets, it should be "
                                 "strictly positive ! Got {}".format(planets))
        elif isinstance(planets, list) and isinstance(planets[0], str):
            self.add_planets(number=len(planets), names=planets)
        elif planets is None:
            pass
        else:
            raise ValueError("planets should be either a strictly positive int or a list of sting "
                             "or None. Got {}".format(planets))

        # # Fill the handlers4noisecatparamfile dictionary
        # self.handlers4noisecatparamfile[stelact_GP_noisemodel] = {create_key: self.create_SANM_param_file,
        #                                                           load_key: self.load_SANM_param_file
        #                                                           }

        # Initialise the orbital_model dictionnary which will define the orbital model to use for the
        # RV and LC instrument models
        self.orbital_model = OrbitalModels(l_planet=[planet for planet in self.planets.values()],
                                           host_star=self.stars[list(self.stars.keys())[0]],
                                           l_inst_model_fullname=l_inst_model_fullname
                                           )

        

    @property
    def model_kwargs(self):
        """This property contains the model_kwargs of this model. A dictionary of arguments to initialise the models.

        This function shoudl be overridden in the sub classes
        """
        return {"stars": len(self.stars), "planets": len(self.planets)}
    
    ##################################################
    ## Dealing with the model category parametrisation
    ##################################################

    def _add_default_config_modelcatparam(self, file):
        """Add the default config for the parametrisation specific to the model category in the configuration file.

        This function is stored in Posterior.get_function_config and used by Posterior._load_config

        # This function needs to be overloaded in the Model subclass if you want to add more variables in the section dedicated to 
        # the parametrisation specific to the model category has a whole (not specific to the modeling a certain category of data)
        """
        file.write("\n# Stars\n#######\n"
                   "# Specify the number of stars in the gravitational group. This can be specified by giving a number (ex: 1)"
                   "stars = 1\n"
                   )  
        file.write("\n# Planets\n#########\n"
                   "# Specify the number of planets in the gravitational group. This can be specified by giving a number (ex: 1) or a list of planet names (ex: ['b'])"
                   "planets = 1\n"
                   )

    def _config_var_exist_modelcatparam(self, dico_config_file):
        """Check if the variable(s) required for the parametrisation specific to the model category are defined in the configuration file.

        This function is stored Posterior.get_function_config and used by Posterior._load_config

        # This function needs to be overloaded in the Model subclass if you want to add more variables in the section dedicated to 
        # the parametrisation specific to the model category has a whole (not specific to the modeling a certain category of data)
        """
        return [var in dico_config_file for var in ['stars', 'planets']]
    
    
    def _load_config_var_content_modelcatparam(self, dico_config_file):
        """Check if the variable(s) required for the parametrisation specific to the model category are defined in the configuration file.

        This function is stored Posterior.get_function_config and used by Posterior._load_config

        # This function needs to be overloaded in the Model subclass if you want to add more variables in the section dedicated to 
        # the parametrisation specific to the model category has a whole (not specific to the modeling a certain category of data)
        """
        self.init_stars_and_planets(stars=dico_config_file['stars'], planets=dico_config_file['planets'])
    
    def _add_default_config_modelcategorydef(self, file):
        """Add the default config for the parametrisation specific to the model category inn the configuration file.

        This function is stored in Posterior._add_default_config_var and used by Posterior._load_config
        """
        file.write("\n####################################\n## Model definition for the category\n####################################\n"
                   f"# Define the parameters of the model that are specfic to the model category ({self.category}).\n"
                   )
        tab_orbmod = spacestring_like("orbital_model = ")
        file.write("\n# Orbital models\n################\n"
                   "orbital_model = {orbital_model}".format(orbital_model=pformat(self.orbital_model.dict2print, compact=True).replace("\n", f"\n{tab_orbmod}"))
                   )
        
    def _config_var_exist_modelcategorydef(self, dico_config_file):
        """Check if the variable(s) required for the parametrisation specific to the model category are defined in the configuration file.

        This function is stored Posterior.get_function_config and used by Posterior._load_config

        # This function needs to be overloaded in the Model subclasses that requierts parameterisation specific to the model category
        """
        return 'orbital_model' in dico_config_file

    def _load_config_var_content_noisemoddef(self, dico_config_file):
        """Check if the variable(s) required for the parametrisation specific to the model category are defined in the configuration file.

        This function is stored Posterior.get_function_config and used by Posterior._load_config

        # This function needs to be overloaded in the Model subclasses that requierts parameterisation specific to the model category
        """
        self.orbital_model.load_config(dico_config=dico_config_file['orbital_model'])

    ##########
    ## To sort
    ##########

    @property
    def init_kwargs(self):
        """Return the dictionary giving the arguments for the define_model method of Posterior."""
        dico = {}
        dico["stars"] = self.nb_star
        dico["planets"] = self.nb_planets
        # dico["parametrisation"] = self.parametrisation
        return dico

    ##########################################
    ## Dealing with Stars and planet instances
    ##########################################

    def add_a_star(self, name=None, kwargs_getname_4_storename={"include_prefix": False, "code_version": True},
                   kwargs_getname_4_codename={"include_prefix": False, "code_version": True}):
        """Add a Star in the GravGroup.

        :param str/None name: Name of the star (ex: A, B and should not include gravgroup name)

        Arguments kwargs_getname_4_storename and kwargs_getname_4_codename are passed to Star.__init__
        method (see ParamContainer.__init__ docstring for more info). Only the default values are
        modified.
        """
        if name is None:
            list_of_possible_name = ascii_uppercase
        else:
            list_of_possible_name = [name]
        for possible_name in list_of_possible_name:
            star = Star(name=possible_name, gravgroup=self, kwargs_getname_4_storename=kwargs_getname_4_storename,
                        kwargs_getname_4_codename=kwargs_getname_4_codename)
            if self.isavailable_paramcontainer(star.store_name, category=star.category):
                continue
            else:
                self.add_a_paramcontainer(star)
                return
        raise ValueError("All names provided already exists ({}). Star cannot be added".format(list_of_possible_name))

    def add_stars(self, number, names=None):
        """Add Stars in the GravGroup."""
        if names is None:
            for i in range(number):
                self.add_a_star()
        else:
            for i in range(number):
                self.add_a_star(names[i])

    @property
    def stars(self):
        return self.paramcontainers["stars"]

    @property
    def nb_star(self):
        return self.nb_of_paramcontainers["stars"]

    def add_a_planet(self, name=None, kwargs_getname_4_storename={"include_prefix": False, "code_version": True},
                     kwargs_getname_4_codename={"include_prefix": False, "code_version": True}):
        """Add a Planet in the GravGroup.

        :param str/None name: Name of the star (ex: A, B and should not include gravgroup name)

        Arguments kwargs_getname_4_storename and kwargs_getname_4_codename are passed to Planet.__init__
        method (see ParamContainer.__init__ docstring for more info). Only the default values are
        modified.
        """
        if name is None:
            list_of_possible_name = ascii_lowercase[1:]
        else:
            list_of_possible_name = [name]
        for possible_name in list_of_possible_name:
            planet = Planet(name=possible_name, gravgroup=self, kwargs_getname_4_storename=kwargs_getname_4_storename,
                            kwargs_getname_4_codename=kwargs_getname_4_codename)
            if self.isavailable_paramcontainer(planet.store_name, category=planet.category):
                continue
            else:
                self.add_a_paramcontainer(planet)
                return
        raise ValueError("All names provided already exists ({}). Planet cannot be added".format(list_of_possible_name))

    def add_planets(self, number, names=None):
        """Add Planets in the GravGroup."""
        if names is None:
            for i in range(number):
                self.add_a_planet()
        else:
            for i in range(number):
                self.add_a_planet(names[i])

    @property
    def planets(self):
        return self.paramcontainers["planets"]

    @property
    def nb_planets(self):
        return self.nb_of_paramcontainers["planets"]
