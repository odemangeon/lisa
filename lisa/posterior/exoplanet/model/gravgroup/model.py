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
from ...likelihood.stellar_activity_noisemodel import stelact_GP_noisemodel, StellarActivityNoiseModelInterface
from ....core.model.core_model import Core_Model, create_key, load_key
from ....core.model.indicator_model.IND_instcat_model import IND_InstCat_Model
from ....core.likelihood.jitter_noise_model import JitterNoiseModelInterface
from .....tools.miscellaneous import spacestring_like


# from pdb import set_trace


class GravGroup(GravGroup_Parametrisation, JitterNoiseModelInterface, StellarActivityNoiseModelInterface,
                Core_Model):  # LC_InstCat_Model, RV_InstCat_Model, IND_InstCat_Model GravGroup_Parametrisation has to be before Core_Model to overriding Core_Parametrisation
    """docstring for GravGroup."""

    ## Model category string
    __category__ = "GravitionalGroups"

    ## Set of possible instrument categories (Used by Core_Model._check_dataset_instcat)
    # __possible_inst_categories__ = {LC_inst_cat, RV_inst_cat, IND_inst_cat}
    __instcat_model_classes__ = [LC_InstCat_Model, RV_InstCat_Model, IND_InstCat_Model]

    ## Does the model requires a model parametrisation file
    __has_model_paramfile__ = True

    # Available orbital models
    _orbital_models = ["batman", ]

    _ext_plonly = "_only"  # Extension used by the datasimulator creator for the planet only datasimulator (withou the instrument nor the star)

    def __init__(self, name, dataset_db, instmodel4dataset=None, l_instmod_fullnames=[],
                 stars=None, planets=None, run_folder=None):
        """docstring GravGroup init method."""
        Core_Model.__init__(self=self, name=name, dataset_db=dataset_db, run_folder=run_folder,
                            instmodel4dataset=instmodel4dataset, l_instmod_fullnames=l_instmod_fullnames)

        # Init the noise models interfaces
        JitterNoiseModelInterface.__init__(self=self)
        StellarActivityNoiseModelInterface.__init__(self=self)
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

        # Fill the handlers4noisecatparamfile dictionary
        self.handlers4noisecatparamfile[stelact_GP_noisemodel] = {create_key: self.create_SANM_param_file,
                                                                  load_key: self.load_SANM_param_file
                                                                  }

        # Define the orbital_model dictionnary which will define the orbital model to use for the
        # RV and LC instrument models
        l_inst_model_fullname = []
        for InstCat_Model in [LC_InstCat_Model, RV_InstCat_Model]:
            if InstCat_Model.inst_cat in self.inst_categories:
                l_inst_model_fullname += [instmod_obj.full_name for instmod_obj in self.get_instmodel_objs(inst_fullcat=InstCat_Model.inst_cat)]
        self.orbital_model = OrbitalModels(l_planet=[planet for planet in self.planets.values()],
                                           host_star=self.stars[list(self.stars.keys())[0]],
                                           l_inst_model_fullname=l_inst_model_fullname
                                           )

        # Finish the initialisation
        Core_Model.finish_init(self)

    @property
    def init_kwargs(self):
        """Return the dictionary giving the arguments for the define_model method of Posterior."""
        dico = {}
        dico["stars"] = self.nb_star
        dico["planets"] = self.nb_planets
        # dico["parametrisation"] = self.parametrisation
        return dico

    ##############################################
    ## Dealing with the model parametrisation file
    ##############################################

    def get_model_paramfile_section(self):
        """Return the text for the model parametrisation file.

        If you set has_model_paramfile in the Subclass, you need to overwrite this method
        """
        text = """
        # Orbital models
        orbital_model = {orbital_model}
        """
        text = dedent(text)  # Remove undesired indentation

        # Create some of the easy content of the file
        tab_orbmod = spacestring_like("orbital_model = ")
        #
        # Fill the whole text_LC_param string
        text = text.format(orbital_model=pformat(self.orbital_model.dict2print, compact=True).replace("\n", f"\n{tab_orbmod}"))

        return text

    def load_config_model(self, dico_config):
        """Load the content of the model parametrisation file.

        If you set has_model_paramfile in the Subclass, you need to overwrite this method
        """
        dict_name = "orbital_model"

        if dict_name not in dico_config:
            raise ValueError(f"In file {self.paramfile_model}: Missing {dict_name} dictionary.")
        dico_model = dico_config[dict_name]
        self.orbital_model.load_config(dico_config=dico_model)

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
