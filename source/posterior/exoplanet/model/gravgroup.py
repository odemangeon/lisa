#!/usr/bin/python
# -*- coding:  utf-8 -*-
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
from logging import getLogger
from os.path import isfile, join
from collections import OrderedDict
from string import ascii_lowercase
from string import ascii_uppercase
from textwrap import dedent

from .celestial_bodies import Star, Planet
from .parametrisation_gravgroup import GravGroup_Parametrisation
from .limb_darkening import Manager_LD, CoreLD
from .datasim_creator_rv import create_datasimulator_RV
from .datasim_creator_lc import create_datasimulator_LC
from .supersamp_exptime import SuperSampExpTimeAttr, _supersamp_key, _exptime_key
from ..dataset_and_instrument.lc import LC_inst_cat
from ..dataset_and_instrument.rv import RV_inst_cat
from ...core.model.core_model import Core_Model, create_key, load_key
from ....tools.human_machine_interface.QCM import QCM_utilisateur
from ....tools.miscellaneous import spacestring_like


# from pdb import set_trace


## Logger object
logger = getLogger()


mgr_LD = Manager_LD()


class GravGroup(GravGroup_Parametrisation, Core_Model, SuperSampExpTimeAttr):  # GravGroup_Parametrisation has to be before Core_Model to overriding Core_Parametrisation
    """docstring for GravGroup."""

    ## Model category string
    __category__ = "GravitionalGroups"

    ## Set of possible instrument categories
    __possible_inst_categories__ = {LC_inst_cat, RV_inst_cat}

    ## List of available rv models, the 1st element is used as default
    _rv_models = ["radvel", "ajplanet"]

    ## List of available lc models, the 1st element is used as default
    _transit_models = ["batman", "pytransit-MandelAgol", "pytransit-Gimenez"]

    ## List of available limb-darkening models for each lc_models, the 1st element is used as
    ## default
    _ld_models = {"batman": ["quadratic", "nonlinear", "exponential", "logarithmic", "squareroot",
                             "linear", "uniform", "custom"],
                  "pytransit-MandelAgol": ["quadratic", "linear", "uniform"],
                  "pytransit-Gimenez": ["quadratic", "linear", "uniform"]
                  }

    def __init__(self, name, dataset_db, instmodel4dataset=None, l_instmod_fullnames=[],
                 transit_model=None, rv_model=None, stars=None, planets=None, run_folder=None):
        """docstring GravGroup init method."""
        super(GravGroup, self).__init__(name=name, dataset_db=dataset_db, run_folder=run_folder,
                                        instmodel4dataset=instmodel4dataset,
                                        l_instmod_fullnames=l_instmod_fullnames)
        if LC_inst_cat in self.dataset_db.inst_categories:
            # light-curve model
            self.transit_model = transit_model
            self.__ldmodel4instmodfname = OrderedDict()  # Limb darkening model for each instrument
            SuperSampExpTimeAttr.__init__(self)
            # instrument
            # Limb darkening model
            # self.ld_model = ld_model
            # TODO: Create the LC_param_file and create a function to load its content and build the
            # Associated LD param containers.
        if RV_inst_cat in self.dataset_db.inst_categories:
            # radial velocities model
            self.rv_model = rv_model
            # Initialise the dictionary giving the RV zero point RV_references
            self.__RV_references = dict.fromkeys(self.get_inst_names(RV_inst_cat), None)
            logger.debug("RV instruments names: {}".format(list(self.__RV_references.keys())))
            self.__RV_references["global"] = list(self.__RV_references.keys())[0]
            for key in self.__RV_references:
                if key != "global":
                    self.__RV_references[key] = self.get_instmodel_names(inst_name=key,
                                                                         inst_cat=RV_inst_cat)[0]
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

        # Initialise available parametrisation
        GravGroup_Parametrisation.add_available_parametrisations(self)

        # Fill the datasimcreatorname4instcat dictionary
        self.datasimcreatorname4instcat[RV_inst_cat] = "sim_RV"
        self.datasimcreatorname4instcat[LC_inst_cat] = "sim_LC"

        # Fill the datasimcreator dictionary
        self.datasimcreator["sim_RV"] = self._create_datasimulator_RV
        self.datasimcreator["sim_LC"] = self._create_datasimulator_LC

        # Fill the handlers4instcatparamfile dictionary
        self.handlers4instcatparamfile[RV_inst_cat] = {create_key: None, load_key: None}
        self.handlers4instcatparamfile[LC_inst_cat] = {create_key: self.create_LC_param_file,
                                                       load_key: self.load_LC_param_file}
        ## List of Dict: [{"stars": [key in self.stars,], "planets":[key in self.planets]}]
        ## Define sub-gravitational group for example for planets orbiting one componant of a wide
        ## separation binary star. This is kept for later.
        # self.subgravgroups = []

    @property
    def init_kwargs(self):
        """Return the dictionary giving the arguments for the define_model method of Posterior."""
        dico = {}
        dico["stars"] = self.nb_star
        dico["planets"] = self.nb_planets
        if LC_inst_cat in self.dataset_db.inst_categories:
            dico["transit_model"] = self.transit_model
        if RV_inst_cat in self.dataset_db.inst_categories:
            dico["rv_model"] = self.rv_model
        dico["parametrisation"] = self.parametrisation
        return dico

    @property
    def transit_model(self):
        """Returns the name of the transit model used."""
        return self.__transit_model

    @transit_model.setter
    def transit_model(self, model_name):
        """Returns the name of the transit model used."""
        if model_name in self._transit_models:
            self.__transit_model = model_name
        elif model_name is None:
            self.__transit_model = self._transit_models[0]
        else:
            raise AssertionError("transit_model should be in {}".format(self._transit_models))

    @property
    def ldmodel4instmodfname(self):
        """Return the dictionary giving the LD object to use for each LC instrument model."""
        return self.__ldmodel4instmodfname

    @property
    def rv_model(self):
        """Returns the name of the transit model used."""
        return self.__rv_model

    @rv_model.setter
    def rv_model(self, model_name):
        """Returns the name of the transit model used."""
        if model_name in self._rv_models:
            self.__rv_model = model_name
        elif model_name is None:
            self.__rv_model = self._rv_models[0]
        else:
            raise AssertionError("rv_model should be in {}".format(self._rv_models))

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

    @property
    def RV_references(self):
        return self.__RV_references

    @property
    def RV_globalref_instname(self):
        return self.__RV_references["global"]

    def set_RV_globalref_instname(self, inst_name):
        self.__RV_references["global"] = inst_name

    def get_RVref4inst_modname(self, inst_name):
        return self.__RV_references[inst_name]

    def set_RVref4inst_modname(self, inst_name, inst_model_name):
        self.__RV_references[inst_name] = inst_model_name

    __ld_dict_name = "LDs"
    __ldmod_dict_name = "LD_models"
    __supersamp_dict = "SuperSamps"

    def create_LC_param_file(self, paramfile_path=None, answer_overwrite=None, answer_create=None):
        """Create a parameter file for the light-curve parametrisation.

        :param string paramfile_path: Path to the LC_param_file.
        :param string answer_overwrite: If the LC_param_file already exists, do you want to
            overwrite it ? "y" or "n". If this not provide the program will ask you interactively.
        :param string answer_create: If the LC_param_file doesn't exists aleardy, where do you want
            to create it ? "absolute", "run_folder" or "error". If this not provide the program will
            ask you interactively.
        """
        if paramfile_path is None:
            paramfile_path = "LC_param_file.py"
        file_path = self.look4runfile(file_path=paramfile_path)
        if file_path is not None:
            answers_list_yn = ['y', 'n']
            if answer_overwrite is None:
                question = ("File {} already exists. Do you want to overwrite it ? {}\n"
                            "".format(file_path, answers_list_yn))
                reply = QCM_utilisateur(question, answers_list_yn)
            else:
                if answer_overwrite in answers_list_yn:
                    reply = answer_overwrite
                else:
                    raise ValueError("answer_overwrite should by in {}".format(answers_list_yn))
        else:
            answers_list_create = ["absolute", "error"]
            if self.hasrun_folder:
                answers_list_create.append("run_folder")
                run_folder_path = join(self.run_folder, paramfile_path)
            if answer_create is None:
                question = ("File {} doesn't exists. Do you want to\nCreate it at the 'absolute' path: "
                            "{}".format(paramfile_path, paramfile_path))
                if self.hasrun_folder:
                    question += "\nCreate it at the 'run_folder' path: {}".format(run_folder_path)
                question += "\nNot create it and raise an 'error' ? {}\n".format(answers_list_create)
                reply = QCM_utilisateur(question, answers_list_create)
            else:
                if answer_create in answers_list_create:
                    reply = answer_create
                else:
                    raise ValueError("answer_create should by in {}".format(answers_list_create))
            if reply == "absolute":
                file_path = paramfile_path
            elif reply == "run_folder":
                file_path = run_folder_path
            else:
                raise ValueError("File {} doesn't exist and the user doesn't want to create it."
                                 "".format(paramfile_path))
            reply = "y"
        if reply == "y":
            with open(file_path, 'w') as f:
                # Write the header
                f.write("#!/usr/bin/python\n# -*- coding:  utf-8 -*-\n")

                # Define the global structure of the file
                text_LC_param = """
                # Light-curve parametrisation file of {object_name}
                transit_model = '{transit_model}'

                # Limb-darkening.
                # Associate LC instrument models with LD param containers.
                # Available limb-darkening models are:
                # {available_lds}
                {ld_dict_name} = {{{star_ld_dict}
                {tab_ld}}}

                # Supersampling and exposure_time
                {supersamp_dict} = {{{inst_ss_dict}
                {tab_ss}}}
                """
                text_LC_param = dedent(text_LC_param)  # Remove undesired indentation

                # Create some of the easy content of the file
                available_lds = self._ld_models[self.transit_model]
                tab_ld = spacestring_like("{ld_dict_name} = {{"
                                          "".format(ld_dict_name=self.__ld_dict_name))
                tab_ss = spacestring_like("{supersamp_dict} = {{"
                                          "".format(supersamp_dict=self.__supersamp_dict))

                # Create the structure of the star_ld_dict
                star_ld_dict = """
                '{star_name}': {{{inst_ld_dict}

                {tab_star_ld}'{LD_dict_name}': {{{LDmodels}}}
                {tab_star_ld}}}
                """
                star_ld_dict = dedent(star_ld_dict)[1:-1]  # Remove undesired indentation

                # Create some of the easy content of the star_ld_dict
                default_parcontname = 'default'
                star = self.stars[list(self.stars.keys())[0]]
                tab_star_ld = tab_ld + spacestring_like("'{star_name}': {{"
                                                        "".format(star_name=star.get_name()))
                LDmodels = ("'{def_LDparcont}': '{def_LDmodname}'"
                            "".format(def_LDparcont=default_parcontname,
                                      def_LDmodname="quadratic"))

                # Create the content related to LC instruments (inst_ld_dict and inst_ss_dict)
                inst_ld_dict = ""
                inst_ss_dict = ""
                ss_dict = ("'{instmod_fullname}': {{'{supersamp_key}': {default_supersamp}, "
                           "'{exptime_key}': {default_exptime}}},")
                ld_dict = "'{instmod_fullname}': '{def_LDparcont}',"
                default_supersamp = 1
                default_exptime = 0.02043402778  # Kepler long cadence exposure time in days
                first_instmodel = True
                for instmod_obj in self.get_instmodel_objs(inst_cat=LC_inst_cat):
                    ld_tab = ""
                    ss_tab = ""
                    if not(first_instmodel):
                        ld_tab = "\n{tab_star_ld}"
                        ss_tab = "\n{tab_ss}"
                    else:
                        first_instmodel = False
                    inst_ld_dict += (ld_tab +
                                     ld_dict).format(tab_star_ld=tab_star_ld,
                                                     instmod_fullname=instmod_obj.get_name(include_prefix=True, code_version=True, recursive=True),
                                                     def_LDparcont=default_parcontname)
                    inst_ss_dict += (ss_tab +
                                     ss_dict).format(tab_ss=tab_ss,
                                                     instmod_fullname=instmod_obj.get_name(include_prefix=True, code_version=True, recursive=True),
                                                     supersamp_key=_supersamp_key,
                                                     default_supersamp=default_supersamp,
                                                     exptime_key=_exptime_key,
                                                     default_exptime=default_exptime)

                # Fill the structures of star_ld_dict
                star_ld_dict = star_ld_dict.format(star_name=star.get_name(), inst_ld_dict=inst_ld_dict,
                                                   tab_star_ld=tab_star_ld, LDmodels=LDmodels,
                                                   LD_dict_name=self.__ldmod_dict_name)

                # Fill the whole text_LC_param string
                text_LC_param = text_LC_param.format(object_name=self.get_name(),
                                                     transit_model=self.transit_model,
                                                     available_lds=available_lds,
                                                     ld_dict_name=self.__ld_dict_name,
                                                     tab_ld=tab_ld, star_ld_dict=star_ld_dict,
                                                     supersamp_dict=self.__supersamp_dict,
                                                     tab_ss=tab_ss, inst_ss_dict=inst_ss_dict)

                # Write the file
                f.write(text_LC_param)
            logger.info("Parameter file created at path: {}".format(file_path))
        else:
            logger.info("Parameter file already existing and not overwritten: {}".format(file_path))
        self.paramfile4instcat[LC_inst_cat] = file_path

    @property
    def isdefined_LCparamfile(self):
        """Return True is the attribute param_file has been defined."""
        return self.isdefined_paramfile_instcat(inst_cat=LC_inst_cat)

    def read_LC_param_file(self):
        """Read the content of the LC parameter file."""
        if self.isdefined_LCparamfile:
            with open(self.paramfile4instcat[LC_inst_cat]) as f:
                exec(f.read())
            dico = locals().copy()
            dico.pop("self")
            logger.debug("LC parameter file read.\nContent of the parameter file: {}"
                         "".format(dico.keys()))
            return dico
        else:
            raise IOError("Impossible to read LC parameter file: {}".format(self.self.paramfile4instcat[LC_inst_cat]))

    def load_LC_config(self, dico_config):
        """load the configuration specified by the dictionnary"""
        # Check that transit_model has not been changed
        if dico_config['transit_model'] != self.transit_model:
            raise ValueError("You cannot change the transit model that you previously selected.")
        for star in self.stars.values():
            star = self.stars[list(self.stars.keys())[0]]
            LD_models = dico_config[self.__ld_dict_name][star.code_name][self.__ldmod_dict_name]
            l_LC_instmod_name = list(dico_config[self.__ld_dict_name][star.code_name].keys())
            l_LC_instmod_name.remove(self.__ldmod_dict_name)
            for instmod_name in l_LC_instmod_name:
                ld_name = dico_config[self.__ld_dict_name][star.code_name][instmod_name]
                if instmod_name not in self.ldmodel4instmodfname:
                    self.ldmodel4instmodfname[instmod_name] = {}
                self.ldmodel4instmodfname[instmod_name][star.code_name] = ld_name
            for ld_name, ld_type in LD_models.items():
                # Create the LD paramcontainer with
                self.add_a_LD(star=star, ld_type=ld_type, name=ld_name)
        supersamp_dict = dico_config[self.__supersamp_dict]
        for instmod_name, dico in supersamp_dict.items():
            self.SSE4instmodfname.add_instmodel_SSEdict(instmod_name, dico)

    def load_LC_param_file(self):
        """Load LC_param_file."""
        dico_config = self.read_LC_param_file()
        self.load_LC_config(dico_config)

    def add_a_LD(self, star, ld_type, name, kwargs_getname_4_storename={"include_prefix": True, "code_version": True},
                 kwargs_getname_4_codename={"include_prefix": True, "code_version": True}):
        """Add a Planet in the GravGroup.

        :param Star star: Star instance the limb darkening refers to.
        :param str ld_type: Type of the limb darkening model.
        :param str name: Name of the limb darkening param container to be created.

        Arguments kwargs_getname_4_storename and kwargs_getname_4_codename are passed to a Core_LD.__init__
        method (see Core_LD.__init__ docstring for more info). Only the default values are
        modified.
        """
        LDparcont_class = mgr_LD.get_LD_parcont_subclass(ld_type)
        LD = LDparcont_class(star=star, name=name, kwargs_getname_4_storename=kwargs_getname_4_storename,
                             kwargs_getname_4_codename=kwargs_getname_4_codename)
        if self.isavailable_paramcontainer(LD.store_name, category="LD"):
            raise ValueError("Names provided already exists ({}). LD cannot be added".format(LD.store_name))
        else:
            self.add_a_paramcontainer(LD)

    @property
    def LDs(self):
        return self.paramcontainers[CoreLD.category]

    def get_list_LD_parconts(self):
        return self.paramcontainers[CoreLD.category].values()

    def _create_datasimulator_RV(self, inst_models=None, datasets=None):
        return create_datasimulator_RV(star=list(self.stars.values())[0],
                                       planets=self.planets,
                                       key_whole=self.key_whole,
                                       key_param=self.key_param,
                                       key_mand_kwargs=self.key_mand_kwargs,
                                       key_opt_kwargs=self.key_opt_kwargs,
                                       RV_globalref_instname=self.RV_globalref_instname,
                                       RV_instref_modnames=self.RV_references,
                                       RV_inst_db=self.instruments[RV_inst_cat],
                                       rv_model=self.rv_model,
                                       inst_models=inst_models, datasets=datasets)

    def _create_datasimulator_LC(self, inst_models, datasets=None):
        return create_datasimulator_LC(star=list(self.stars.values())[0],
                                       planets=self.planets,
                                       key_whole=self.key_whole,
                                       key_param=self.key_param,
                                       key_mand_kwargs=self.key_mand_kwargs,
                                       key_opt_kwargs=self.key_opt_kwargs,
                                       parametrisation=self.parametrisation,
                                       ldmodel4instmodfname=self.ldmodel4instmodfname,
                                       LDs=self.LDs, transit_model=self.transit_model,
                                       SSE4instmodfname=self.SSE4instmodfname,
                                       inst_models=inst_models, datasets=datasets)
