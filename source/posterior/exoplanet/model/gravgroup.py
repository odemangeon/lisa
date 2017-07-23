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
from copy import deepcopy
from textwrap import dedent
from math import acos, degrees
from ajplanet import pl_rv_array
from batman import TransitModel, TransitParams
from pytransit import MandelAgol


from .celestial_bodies import Star, Planet
from .parametrisation import GravGroup_Parametrisation
from .limb_darkening import Manager_LD, CoreLD
from ...core.dataset_and_instrument.instrument import Instrument_Model
from ...core.dataset_and_instrument.dataset import Dataset
from ...core.model.core_model import Core_Model
from ....tools.function_w_doc import DocFunction
from ....tools.convert import getecc_fast, getomega_fast, gettp_fast, getaoverr
from ....tools.human_machine_interface.QCM import QCM_utilisateur
from ....tools.miscellaneous import spacestring_like


from pdb import set_trace


## Logger object
logger = getLogger()


mgr_LD = Manager_LD()


class GravGroup(Core_Model, GravGroup_Parametrisation):
    """docstring for GravGroup."""

    ## category
    __category__ = "GravitionalGroups"

    ## List of available rv models, the 1st element is used as default
    _rv_models = ["ajplanet"]

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
                 transit_model=None, rv_model=None, parametrisation=None,
                 stars=None, planets=None, run_folder=None):
        """docstring Planet init method."""
        super(GravGroup, self).__init__(name, dataset_db, run_folder,
                                        instmodel4dataset=instmodel4dataset,
                                        l_instmod_fullnames=l_instmod_fullnames)
        if "LC" in self.dataset_db.inst_categories:
            # light-curve model
            self.transit_model = transit_model
            self.__ldmodel4instmodfname = OrderedDict()  # Limb darkening model for each instrument
            self.__SSE4instmodfname = OrderedDict()  # Supersampling and Exposure time for each
            # instrument
            # Limb darkening model
            # self.ld_model = ld_model
            # TODO: Create the LC_param_file and create a function to load its content and build the
            # Associated LD param containers.
        if "RV" in self.dataset_db.inst_categories:
            # radial velocities model
            self.rv_model = rv_model
            # Initialise the dictionary giving the RV zero point RV_references
            self.__RV_references = dict.fromkeys(self.get_inst_names("RV"), None)
            logger.debug("RV instruments names: {}".format(list(self.__RV_references.keys())))
            self.__RV_references["global"] = list(self.__RV_references.keys())[0]
            for key in self.__RV_references:
                if key != "global":
                    self.__RV_references[key] = self.get_instmodel_names(inst_name=key,
                                                                         inst_cat="RV")[0]
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
        # Set parametrisation
        self.parametrisation = parametrisation

        # Fill the datasimcreatorname4instcat dictionnary
        self.datasimcreatorname4instcat["RV"] = "sim_RV"
        self.datasimcreatorname4instcat["LC"] = "sim_LC"

        # Fill the datasimcreator dictionnary
        self.datasimcreator["sim_RV"] = self._create_datasimulator_RV
        self.datasimcreator["sim_LC"] = self._create_datasimulator_LC

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
        if "LC" in self.dataset_db.inst_categories:
            dico["transit_model"] = self.transit_model
        if "RV" in self.dataset_db.inst_categories:
            dico["rv_model"] = self.rv_model
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
    def SSE4instmodfname(self):
        """Return the dictionary giving the supersampling factors and exposure_time for each LC
        instrument model."""
        return self.__SSE4instmodfname

    def get_supersamp(self, instmod_fullname):
        """Return the supersampling factor to apply for the instrument model."""
        return self.SSE4instmodfname[instmod_fullname][self.__supersamp_key]

    def get_exptime(self, instmod_fullname):
        """Return the supersampling factor to apply for the instrument model."""
        return self.SSE4instmodfname[instmod_fullname][self.__exptime_key]

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

    def add_a_star(self, name=None):
        """Add a Star in the GravGroup."""
        if self.isavailable_paramcontainer(name, category="stars"):
            logger.warning("A star with name {} already exists ! It will be overwritten"
                           "".format(name))
        if name is None:
            for possible_name in ascii_uppercase:
                if self.isavailable_paramcontainer(possible_name, category="stars"):
                    continue
                else:
                    name = possible_name
                    break
        self.add_a_paramcontainer(Star(name=name, gravgroup=self))

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

    def add_a_planet(self, name=None):
        """Add a Planet in the GravGroup."""
        if self.isavailable_paramcontainer(name, category="planets"):
            logger.warning("A planet with name {} already exists ! It will be overwritten"
                           "".format(name))
        if name is None:
            for possible_name in ascii_lowercase[1:]:
                if self.isavailable_paramcontainer(possible_name, category="planets"):
                    continue
                else:
                    name = possible_name
                    break
        self.add_a_paramcontainer(Planet(name=name, gravgroup=self))

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

    @property
    def lc_param_file(self):
        """Path to the light-curve parametrisation file"""
        return self.__lc_param_file

    @lc_param_file.setter
    def lc_param_file(self, path):
        """Path to the light-curve parametrisation file"""
        file_exists = isfile(path)
        if file_exists:
            self.__lc_param_file = path
        else:
            raise AssertionError("File {} doesn't exists".format(path))

    __ld_dict_name = "LDs"
    __ldmod_dict_name = "LD_models"
    __supersamp_dict = "SuperSamps"
    __supersamp_key = "supersamp"
    __exptime_key = "exptime"

    def create_LC_param_file(self, paramfile_path):
        """Create a parameter file for the light-curve parametrisation.

        :param string paramfile_path: Path to the LC_param_file.
        """
        file_path = self.look4runfile(file_path=paramfile_path)
        if file_path is not None:
            answers_list_yn = ['y', 'n']
            question = ("File {} already exists. Do you want to overwrite it ? {}\n"
                        "".format(file_path, answers_list_yn))
            reply = QCM_utilisateur(question, answers_list_yn)
        else:
            answers_list_create = ["absolute", "error"]
            question = ("File {} doesn't exists. Do you want to\nCreate it at the 'absolute' path: "
                        "{}".format(paramfile_path, paramfile_path))
            if self.hasrun_folder:
                answers_list_create.append("run_folder")
                run_folder_path = join(self.run_folder, paramfile_path)
                question += "\nCreate it at the 'run_folder' path: {}".format(run_folder_path)
            question += "\nNot create it and raise an 'error' ? {}\n".format(answers_list_create)
            reply = QCM_utilisateur(question, answers_list_create)
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
                                                        "".format(star_name=star.name))
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
                for instmod_obj in self.get_instmodel_objs(inst_cat="LC"):
                    ld_tab = ""
                    ss_tab = ""
                    if not(first_instmodel):
                        ld_tab = "\n{tab_star_ld}"
                        ss_tab = "\n{tab_ss}"
                    else:
                        first_instmodel = False
                    inst_ld_dict += (ld_tab +
                                     ld_dict).format(tab_star_ld=tab_star_ld,
                                                     instmod_fullname=instmod_obj.full_name,
                                                     def_LDparcont=default_parcontname)
                    inst_ss_dict += (ss_tab +
                                     ss_dict).format(tab_ss=tab_ss,
                                                     instmod_fullname=instmod_obj.full_name,
                                                     supersamp_key=self.__supersamp_key,
                                                     default_supersamp=default_supersamp,
                                                     exptime_key=self.__exptime_key,
                                                     default_exptime=default_exptime)

                # Fill the structures of star_ld_dict
                star_ld_dict = star_ld_dict.format(star_name=star.name, inst_ld_dict=inst_ld_dict,
                                                   tab_star_ld=tab_star_ld, LDmodels=LDmodels,
                                                   LD_dict_name=self.__ldmod_dict_name)

                # Fill the whole text_LC_param string
                text_LC_param = text_LC_param.format(object_name=self.name,
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
        self.lc_param_file = file_path

    @property
    def isdefined_LCparamfile(self):
        """Return True is the attribute param_file has been defined."""
        return self.lc_param_file is not None

    def read_LC_param_file(self):
        """Read the content of the LC parameter file."""
        if self.isdefined_LCparamfile:
            exec(open(self.lc_param_file).read())
            dico = locals().copy()
            dico.pop("self")
            logger.debug("LC parameter file read.\nContent of the parameter file: {}"
                         "".format(dico.keys()))
            return dico
        else:
            raise IOError("Impossible to read LC parameter file: {}".format(self.param_file))

    def load_LC_config(self, dico_config):
        """load the configuration specified by the dictionnary"""
        # Check that transit_model has not been changed
        if dico_config['transit_model'] != self.transit_model:
            raise ValueError("You cannot change the transit model that you previously selected.")
        star = self.stars[list(self.stars.keys())[0]]
        LD_models = dico_config[self.__ld_dict_name][star.name][self.__ldmod_dict_name]
        l_LC_instmod_name = list(dico_config[self.__ld_dict_name][star.name].keys())
        l_LC_instmod_name.remove(self.__ldmod_dict_name)
        for instmod_name in l_LC_instmod_name:
            ld_name = dico_config[self.__ld_dict_name][star.name][instmod_name]
            self.ldmodel4instmodfname[instmod_name] = ld_name
        for ld_name, ld_type in LD_models.items():
            self.add_a_LD(star=star, ld_type=ld_type, name=ld_name)
            # Create the LD paramcontainer with
        supersamp_dict = dico_config[self.__supersamp_dict]
        for instmod_name, dico in supersamp_dict.items():
            self.SSE4instmodfname[instmod_name] = dico

    def load_LC_param_file(self):
        """Load LC_param_file."""
        dico_config = self.read_LC_param_file()
        self.load_LC_config(dico_config)

    def add_a_LD(self, star, ld_type, name):
        """Add a Planet in the GravGroup."""
        if self.isavailable_paramcontainer(name, category="LD"):
            logger.warning("A LD model with name {} already exists ! It will be overwritten"
                           "".format(name))
        LDparcont_class = mgr_LD.get_LD_parcont_subclass(ld_type)
        self.add_a_paramcontainer(LDparcont_class(star=star, name=name))

    @property
    def LDs(self):
        return self.paramcontainers[CoreLD.category]

    def get_list_LD_parconts(self):
        return self.paramcontainers[CoreLD.category].values()

    @property
    def automatic_init_kwargs(self):
        """Return a dictionary giving the keyword arguments for automatic_model_initialisation."""
        dico = super(GravGroup, self).automatic_init_kwargs
        dico["lc_param_file"] = self.lc_param_file
        dico["kwargs_parametrisation"] = self.parametrisation_kwargs
        return dico

    def automatic_model_initialisation(self, lc_param_file, kwargs_parametrisation, **kwargs):
        """load the parameter file."""
        self.lc_param_file = lc_param_file
        self.load_LC_param_file()
        self.apply_parametrisation(**kwargs_parametrisation)
        super(GravGroup, self).automatic_model_initialisation(**kwargs)

    def _create_datasimulator_RV(self, inst_models=None, datasets=None):
        """Return datasimulator functions.

        A datasimualtor function is created for the whole dataset_database and for each instrument
        model individually.

        ----
        Returns:
            - 1 data simulator function for the whole dataset.
            - 3 levels dictionary with instrument category, instrument name, instrument model
            containing function that take parameters values and return simulated data.
        """
        # Get the star object.
        star = self.stars[list(self.stars.keys())[0]]

        # text_def_func is a dictionary which will received the text of the datasimulator functions
        # It has several keys for several datasimulator functions:
        #   - "whole" for the whole system with all the planets
        #   - "b", "c", ... ("planet name") for only the contribution of one planet.
        text_def_func = {}

        # param_nb is a dictionary that will keep track of the number of parameter for each
        # function in text_def_func (so the keys are the same).
        param_nb = {}

        # arg_list is a dictionary which will receive the argument list of the datasimulator
        # function in text_def_func (so the keys are the same).
        # The argument list of a function is itself a dictionary (OrderedDict) that get at least two
        # keys:
        #   - "param": list of the free parameters name in order
        #   - "kwargs": list of the additional argument taht you need to provide to simulate the
        #               data. For example the time
        arg_list = {}

        if isinstance(inst_models, Instrument_Model):
            l_inst_model = [inst_models]
            inst_model_full_name = inst_models.full_name
            multi_instmodl = False
        elif isinstance(inst_models, list):
            l_inst_model = inst_models
            multi_instmodl = True
            inst_model_full_name = "multiinst"
        elif inst_models is None:
            l_inst_model = [inst_models]
            inst_model_full_name
            multi_instmodl = False
        else:
            raise ValueError("If provided inst_model has to be an Instrument_Model subclass "
                             "instance or a list of Instrument_Model subclass instance")

        # Initialise the template function text
        function_name = ("RVsim_{{object}}_{instmod_fullname}"
                         "".format(instmod_fullname=inst_model_full_name))
        template_function = """
        def {function_name}({{arguments}}):
        {{tab}}{{preambule}}
        {{tab}}return {{returns}}
        """.format(function_name=function_name)
        tab = "    "
        template_function = dedent(template_function)

        # Initialise the template for each instmodel
        template_returns_instmod = "{delta_inst_rv} {star_mean_rv} {planets_rv}"

        # Create the arguments text
        if isinstance(datasets, Dataset):
            l_dataset = [datasets]
            arguments = "p"
        elif isinstance(datasets, list):
            l_dataset = datasets
            arguments = "p"
        elif datasets is None:
            l_dataset = [datasets]
            if multi_instmodl:
                arguments = "p, l_t, l_tref"
            else:
                arguments = "p, t, tref"
        else:
            raise ValueError("If provided datasets has to be a Dataset subclass "
                             "instance or a list of Dataset subclass instance")

        # Initialise arg_list and param_nb for key "whole"
        arg_list[self.key_whole] = OrderedDict()
        arg_list[self.key_whole]["param"] = []
        arg_list[self.key_whole]["kwargs"] = []
        param_nb[self.key_whole] = 0

        # Add time in the kwargs entry of the whole system arg_list
        if datasets is None:
            if multi_instmodl:
                arg_list[self.key_whole]["kwargs"].append("l_t")
            else:
                arg_list[self.key_whole]["kwargs"].append("t")

        # Create for the instrument Delta RV (delta_inst_rv)
        l_delta_inst_rv = []
        l_star_mean_rv = []
        for ii, instmdl, dst in zip(range(len(l_inst_model)), l_inst_model, l_dataset):
            l_delta_inst_rv.append("")
            if instmdl is not None:
                inst_name = instmdl.instrument.name
                ## RVrefglobal_inst: name of the instrument chosen as global RV reference
                ## (eg: HARPS)
                RVrefglobal_instname = self.RV_globalref_instname
                ## RVref4inst_modname: name of the instrument model chosen as reference for the
                ## current instrument (eg: default)
                RVref4inst_modname = self.get_RVref4inst_modname(inst_name)
                # Add the Delta_RV of the global RV reference instrument model if needed
                if inst_name != RVrefglobal_instname:
                    instmod_RVref4inst = self.instruments["RV"][inst_name][RVref4inst_modname]
                    if instmod_RVref4inst.DeltaRV.main:
                        if instmod_RVref4inst.DeltaRV.free:
                            l_delta_inst_rv[ii] += "p[{}] + ".format(param_nb[self.key_whole])
                            param_nb[self.key_whole] += 1
                            arg_list[self.key_whole]["param"].append(instmod_RVref4inst.DeltaRV.
                                                                     full_name)
                        else:
                            l_delta_inst_rv[ii] += "{} + ".format(instmod_RVref4inst.DeltaRV.value)
                # Add the Delta_RV of the model used as RV reference for the current instrument
                if instmdl.name != RVref4inst_modname:
                    if instmdl.DeltaRV.main:
                        if instmdl.DeltaRV.free:
                            l_delta_inst_rv[ii] += "p[{}] + ".format(param_nb[self.key_whole])
                            param_nb[self.key_whole] += 1
                            arg_list[self.key_whole]["param"].append(instmdl.DeltaRV.full_name)
                        else:
                            l_delta_inst_rv[ii] += "{} + ".format(instmdl.DeltaRV.value)

            # Create the text for the star mean RV (star_mean_rv)
            l_star_mean_rv.append("")
            if star.v0.free:
                l_star_mean_rv[ii] += "p[{}]".format(param_nb[self.key_whole])
                param_nb[self.key_whole] += 1
                arg_list[self.key_whole]["param"].append(star.v0.full_name)
            else:
                l_star_mean_rv[ii] += "{}".format(star.v0.value)
            if star.with_RVdrift:
                for order in range(1, star.RVdrift_order + 1):
                    RVdrift_param_name = star.get_RVdrift_param_name(order)
                    RVdrift_param_fullname = star.parameters[RVdrift_param_name].full_name
                    if star.parameters[RVdrift_param_name].main:
                        value_not0 = True
                        if star.parameters[RVdrift_param_name].free:
                            l_star_mean_rv[ii] += "+ p[{}]".format(param_nb[self.key_whole])
                            param_nb[self.key_whole] += 1
                            arg_list[self.key_whole]["param"].append(RVdrift_param_fullname)
                        else:
                            if star.parameters[RVdrift_param_name].value != 0.0:
                                l_star_mean_rv[ii] += "+ {}".format(star.
                                                                    parameters[RVdrift_param_name].
                                                                    value)
                            else:
                                value_not0 = False
                        if value_not0:
                            if ((("tref" not in arg_list[self.key_whole]["kwargs"]) or
                                 ("tref" not in arg_list[self.key_whole]["kwargs"])) and
                               (dst is None)):
                                if multi_instmodl:
                                    arg_list[self.key_whole]["kwargs"].append("l_tref")
                                else:
                                    arg_list[self.key_whole]["kwargs"].append("tref")
                            if order == 1:
                                if multi_instmodl:
                                    l_star_mean_rv[ii] += (" * (l_t[{ii}] - l_tref[{ii}]) "
                                                           "".format(ii=ii))
                                else:
                                    l_star_mean_rv[ii] += " * (t - tref) "
                            elif order > 1:
                                if multi_instmodl:
                                    l_star_mean_rv[ii] += (" * (l_t[{ii}] - l_tref[{ii}])**{order} "
                                                           "".format(order=order, ii=ii))
                                else:
                                    l_star_mean_rv[ii] += (" * (t - tref)**{order}"
                                                           "".format(order=order))

        # Save the param_nb and arg_list for the whole function before iterating over the planets
        # text_def_func_before = text_def_func[self.key_whole]
        param_nb_before = param_nb[self.key_whole]
        arg_list_before = deepcopy(arg_list[self.key_whole])

        # Iterate over the planets to create the preambules (preambule_planet and preambule_whole),
        # the planets RV contribution (planet_rv and whole_planets_rv) and finalise the text of
        # planets functions.
        template_preambule = """
        {tab}ecc_{planet} = getecc_fast({secosw}, {sesinw})
        {tab}omega_{planet} = getomega_fast({secosw}, {sesinw})
        {tab}tp_{planet} = gettp_fast({P}, {tc}, ecc_{planet}, omega_{planet})
        """
        if multi_instmodl:
            template_planet_rv = ("+ pl_rv_array(l_t[{ii}], 0., {K}, omega_{planet}, "
                                  "ecc_{planet}, tp_{planet}, {P})")
        else:
            template_planet_rv = ("+ pl_rv_array(t, 0., {K}, omega_{planet}, "
                                  "ecc_{planet}, tp_{planet}, {P})")

        # Initialise the local dictionary for the creation of the datasim functions by exec
        ldict = locals().copy()
        if datasets is not None:
            if multi_instmodl:
                l_t = []
                l_tref = []
                for instmdl, dst in zip(l_inst_model, l_dataset):
                        l_t.append(dst.get_time())
                        l_tref.append(dst.get_tref())
                ldict["l_t"] = l_t
                ldict["l_tref"] = l_tref
            else:
                ldict["t"] = datasets.get_time()
                ldict["tref"] = datasets.get_tref()

        # Initialise the text for the whole system preambule
        preambule_whole = ""
        l_whole_planets_rv = []
        for instmdl in l_inst_model:
            l_whole_planets_rv.append("")
        for i, planet in enumerate(self.planets.values()):
            # Initialise arg_list and param_nb for the current planet
            arg_list[planet.name] = deepcopy(arg_list_before)
            param_nb[planet.name] = param_nb_before

            # Create two dictionaries which will contain the text for each planet parameter for the
            # current planet and for the whole system.
            params_planet = {}
            params_whole = {}
            # Create the text for each planet parameter for the current planet and for the whole
            # system.
            for param_name, param in zip(["K", "secosw", "sesinw", "tc", "P"],
                                         [planet.K, planet.secosw, planet.sesinw, planet.tc,
                                          planet.P]):
                if param.free:
                    param_text = "p[{}]"
                    params_whole[param_name] = param_text.format(param_nb[self.key_whole])
                    param_nb[self.key_whole] += 1
                    arg_list[self.key_whole]["param"].append(param.full_name)
                    params_planet[param_name] = param_text.format(param_nb[planet.name])
                    param_nb[planet.name] += 1
                    arg_list[planet.name]["param"].append(param.full_name)
                else:
                    params_whole[param_name] = "{}".format(param.value)
                    params_planet[param_name] = params_whole[param_name]

            # Create the preambule text that compute intermediate variables
            preambule_planet = (dedent(template_preambule).
                                format(planet=planet.name, secosw=params_planet["secosw"],
                                       sesinw=params_planet["sesinw"], P=params_planet["P"],
                                       tc=params_planet["tc"], tab=tab))
            preambule_whole += (dedent(template_preambule).
                                format(planet=planet.name, secosw=params_whole["secosw"],
                                       sesinw=params_whole["sesinw"], P=params_whole["P"],
                                       tc=params_whole["tc"], tab=tab))

            # planets RV contribution (planet_rv and whole_planets_rv)
            l_planet_rv = []
            if multi_instmodl:
                for ii, instmdl in enumerate(l_inst_model):
                    l_planet_rv.append(template_planet_rv.format(ii=ii,
                                                                 planet=planet.name,
                                                                 K=params_planet["K"],
                                                                 P=params_planet["P"]))
                    l_whole_planets_rv[ii] += template_planet_rv.format(ii=ii,
                                                                        planet=planet.name,
                                                                        K=params_whole["K"],
                                                                        P=params_whole["P"])
            else:
                l_planet_rv.append(template_planet_rv.format(planet=planet.name,
                                                             K=params_whole["K"],
                                                             P=params_whole["P"]))
                l_whole_planets_rv[ii] += template_planet_rv.format(planet=planet.name,
                                                                    K=params_whole["K"],
                                                                    P=params_whole["P"])

            # Fill returns text for each planet
            returns_pl = ""
            for delta_inst_rv, planet_rv, star_mean_rv in zip(l_delta_inst_rv,
                                                              l_planet_rv,
                                                              l_star_mean_rv):
                returns_pl += template_returns_instmod.format(delta_inst_rv=delta_inst_rv,
                                                              star_mean_rv=star_mean_rv,
                                                              planets_rv=planet_rv)
                returns_pl += ", "
            returns_pl = returns_pl[:-2]

            # Finalise the text of planet RV simulator function
            text_def_func[planet.name] = (template_function.
                                          format(object=planet.name, preambule=preambule_planet,
                                                 arguments=arguments, returns=returns_pl,
                                                 tab=tab))
            logger.debug("text of {object} RV simulator function :\n{text_func}"
                         "".format(object=planet.name, text_func=text_def_func[planet.name]))

        # Fill returns text for the whole system
        returns_whole = ""
        for delta_inst_rv, whole_planet_rv, star_mean_rv in zip(l_delta_inst_rv,
                                                                l_whole_planets_rv,
                                                                l_star_mean_rv):
            returns_whole += template_returns_instmod.format(delta_inst_rv=delta_inst_rv,
                                                             star_mean_rv=star_mean_rv,
                                                             planets_rv=whole_planet_rv)
            returns_whole += ", "
        returns_whole = returns_whole[:-2]

        # Finalise the  text of whole system RV simulator function
        text_def_func[self.key_whole] = (template_function.
                                         format(object=self.key_whole, preambule=preambule_whole,
                                                arguments=arguments, returns=returns_whole, tab=tab
                                                ))
        logger.debug("text of {object} RV simulator function :\n{text_func}"
                     "".format(object=self.key_whole, text_func=text_def_func[self.key_whole]))

        # Create and fill the output dictionnary containing the datasimulators functions.
        dico_docf = dict.fromkeys(text_def_func.keys(), None)
        for obj_key in dico_docf:
            ldict["getecc_fast"] = getecc_fast
            ldict["getomega_fast"] = getomega_fast
            ldict["gettp_fast"] = gettp_fast
            ldict["pl_rv_array"] = pl_rv_array
            exec(text_def_func[obj_key], ldict)
            dico_docf[obj_key] = DocFunction(function=ldict[function_name.format(object=obj_key)],
                                             arg_list=arg_list[obj_key])
            dico_docf[obj_key].inst_models = [instmdl.full_name for instmdl in l_inst_model]
        return dico_docf

    def _create_datasimulator_LC(self, inst_models, datasets=None):
        """Return datasimulator functions.

        A datasimualtor function is created for the whole dataset_database and for each planet
        individually.

        :param Instrument_Model inst_model: instance of Instrument_Model
        :param Dataset dataset: instance of Dataset

        ----
        Returns:
            - A dictionary with DocFunctions containing the data simulator function for the whole
             system ("whole") and for the each planet individually ("planet_name")
        """
        # Get the star object.
        # star = self.stars[list(self.stars.keys())[0]]

        # text_def_func is a dictionary which will received the text of the datasimulator functions
        # It has several keys for several datasimulator functions:
        #   - "whole" for the whole system with all the planets
        #   - "b", "c", ... ("planet name") for only the contribution of one planet.
        text_def_func = {}

        # param_nb is a dictionary that will keep track of the number of parameter for each
        # function in text_def_func (so the keys are the same).
        param_nb = {}

        # arg_list is a dictionary which will receive the argument list of the datasimulator
        # function in text_def_func (so the keys are the same).
        # The argument list of a function is itself a dictionary (OrderedDict) that get at least two
        # keys:
        #   - "param": list of the free parameters name in order
        #   - "kwargs": list of the additional argument taht you need to provide to simulate the
        #               data. For example the time
        arg_list = {}

        if isinstance(inst_models, Instrument_Model):
            l_inst_model = [inst_models]
            inst_model_full_name = inst_models.full_name
            multi_instmodl = False
        elif isinstance(inst_models, list):
            l_inst_model = inst_models
            multi_instmodl = True
            inst_model_full_name = "multiinst"
        elif inst_models is None:
            l_inst_model = [inst_models]
            inst_model_full_name
            multi_instmodl = False
        else:
            raise ValueError("If provided inst_model has to be an Instrument_Model subclass "
                             "instance or a list of Instrument_Model subclass instance")

        # Initialise the template function text
        function_name = ("LCsim_{{object}}_{instmod_fullname}"
                         "".format(instmod_fullname=inst_model_full_name))
        template_function = """
        def {function_name}({{arguments}}):
        {{tab}}{{preambule}}
        {{tab}}return {{returns}}
        """.format(function_name=function_name)
        tab = "    "
        template_function = dedent(template_function)

        # Initialise the template for each instmodel
        template_returns_instmod = "1 {oot_var}{planets_lc}"

        # Create the arguments text
        if isinstance(datasets, Dataset):
            l_dataset = [datasets]
            arguments = "p"
        elif isinstance(datasets, list):
            l_dataset = datasets
            arguments = "p"
        elif datasets is None:
            l_dataset = [datasets]
            if multi_instmodl:
                arguments = "p, l_t, l_tref"
            else:
                arguments = "p, t, tref"
        else:
            raise ValueError("If provided datasets has to be a Dataset subclass "
                             "instance or a list of Dataset subclass instance")

        # Initialise arg_list and param_nb for key "whole"
        arg_list[self.key_whole] = OrderedDict()
        arg_list[self.key_whole]["param"] = []
        arg_list[self.key_whole]["kwargs"] = []
        param_nb[self.key_whole] = 0

        # Add time in the kwargs entry of the whole system arg_list
        if datasets is None:
            if multi_instmodl:
                arg_list[self.key_whole]["kwargs"].append("l_t")
            else:
                arg_list[self.key_whole]["kwargs"].append("t")

        # Create the text for oot_var
        l_oot_var = []
        for ii, instmdl, dst in zip(range(len(l_inst_model)), l_inst_model, l_dataset):
            l_oot_var.append("")
            if instmdl.get_with_OOT_var():
                for order in range(instmdl.get_OOT_var_order() + 1):
                    OOT_param_name = instmdl.get_OOT_param_name(order)
                    OOT_param_fullname = instmdl.parameters[OOT_param_name].full_name
                    if instmdl.parameters[OOT_param_name].main:
                        value_not0 = True
                        if instmdl.parameters[OOT_param_name].free:
                            l_oot_var[ii] += "+ p[{}]".format(param_nb[self.key_whole])
                            param_nb[self.key_whole] += 1
                            arg_list[self.key_whole]["param"].append(OOT_param_fullname)
                        else:
                            if instmdl.parameters[OOT_param_name].value != 0.0:
                                l_oot_var[ii] += "+ {}".format(instmdl.parameters[OOT_param_name].
                                                               value)
                            else:
                                value_not0 = False
                        if value_not0 and order > 0:
                            if ((("tref" not in arg_list[self.key_whole]["kwargs"]) or
                                 ("tref" not in arg_list[self.key_whole]["kwargs"])) and
                               (dst is None)):
                                if multi_instmodl:
                                    arg_list[self.key_whole]["kwargs"].append("l_tref")
                                else:
                                    arg_list[self.key_whole]["kwargs"].append("tref")
                            if order == 1:
                                if multi_instmodl:
                                    l_oot_var[ii] += (" * (l_t[{ii}] - l_tref[{ii}]) "
                                                      "".format(ii=ii))
                                else:
                                    l_oot_var[ii] += " * (t - tref) "
                            elif order > 1:
                                if multi_instmodl:
                                    l_oot_var[ii] += (" * (l_t[{ii}] - l_tref[{ii}])**{order} "
                                                      "".format(order=order, ii=ii))
                                else:
                                    l_oot_var[ii] += " * (t - tref)**{} ".format(order)
                        elif value_not0 and order == 0:
                            l_oot_var[ii] += " "

        if self.parametrisation in self.LC_multis_parametrisations:
            # Get the star object.
            star = self.stars[list(self.stars.keys())[0]]
            if star.rho.free:
                rhostar = "p[{}]".format(param_nb[self.key_whole])
                param_nb[self.key_whole] += 1
                arg_list[self.key_whole]["param"].append(star.rho.full_name)
            else:
                rhostar = "{}".format(star.rho.value)
        else:
            rhostar = None

        # Get the ld_parcont and ld_param_list
        l_LD_parcont_name = []
        l_LD_parcont = []
        l_ld_param_list = []
        for ii, instmdl in enumerate(l_inst_model):
            l_LD_parcont_name.append(self.ldmodel4instmodfname[instmdl.full_name])
            l_LD_parcont.append(self.LDs[l_LD_parcont_name[ii]])
            l_ld_param_list.append("[")
            for param in l_LD_parcont[ii].get_list_params(main=True):
                if param.free:
                    l_ld_param_list[ii] += "p[{}], ".format(param_nb[self.key_whole])
                    param_nb[self.key_whole] += 1
                    arg_list[self.key_whole]["param"].append(param.full_name)
                else:
                    l_ld_param_list[ii] += "{}, ".format(param.value)
            l_ld_param_list[ii] += "]"

        # Create the template preambule
        # template_preambule_pl = """
        #     {tab}ecc_{planet} = getecc_fast({secosw}, {sesinw})"""
        # if self.parametrisation in self.LC_multis_parametrisations:
        #     template_preambule_pl += """
        #     {tab}aR_{planet} = getaoverr({P}, {rhostar})"""
        # if self.transit_model == "batman":
        #     template_preambule_pl += """
        #     {tab}omega_{planet} = degrees(getomega_fast({secosw}, {sesinw}))
        #     {tab}inc_{planet} = degrees(acos({cosinc}))
        #     {tab}params_{planet}.t0 = {tc}
        #     {tab}params_{planet}.per = {P}
        #     {tab}params_{planet}.rp = {Rrat}
        #     {tab}params_{planet}.inc = inc_{planet}
        #     {tab}params_{planet}.ecc = ecc_{planet}
        #     {tab}params_{planet}.w = omega_{planet}
        #     {tab}params_{planet}.u = {ld_param_list}
        #     {tab}params_{planet}.limb_dark = '{ld_mod_name}'"""
        #     if self.parametrisation in self.LC_multis_parametrisations:
        #         template_preambule_pl += """
        #     {tab}params_{planet}.a = aR_{planet}
        #     """
        #     else:
        #         template_preambule_pl += """
        #     {tab}params_{planet}.a = {aR}
        #     """
        # else:
        #     template_preambule_pl += """
        #     {tab}omega_{planet} = getomega_fast({secosw}, {sesinw})
        #     {tab}inc_{planet} = acos({cosinc})
        #     """
        # template_preambule_pl = dedent(template_preambule_pl)
        template_preambule_pl = """
            {tab}ecc_{planet} = getecc_fast({secosw}, {sesinw})"""
        if self.parametrisation in self.LC_multis_parametrisations:
            template_preambule_pl += """
            {tab}aR_{planet} = getaoverr({P}, {rhostar})"""

        if self.transit_model == "batman":
            template_preambule_pl += """
            {tab}omega_{planet} = degrees(getomega_fast({secosw}, {sesinw}))
            {tab}inc_{planet} = degrees(acos({cosinc}))"""

            for instmdl, LD_parcont, ld_param_list in zip(l_inst_model, l_LD_parcont,
                                                          l_ld_param_list):
                if multi_instmodl:
                    template_batman_pl = """
            {{tab}}params_{{planet}}_{instmod_fullname}.t0 = {{tc}}
            {{tab}}params_{{planet}}_{instmod_fullname}.per = {{P}}
            {{tab}}params_{{planet}}_{instmod_fullname}.rp = {{Rrat}}
            {{tab}}params_{{planet}}_{instmod_fullname}.inc = inc_{{planet}}
            {{tab}}params_{{planet}}_{instmod_fullname}.ecc = ecc_{{planet}}
            {{tab}}params_{{planet}}_{instmod_fullname}.w = omega_{{planet}}
            {{tab}}params_{{planet}}_{instmod_fullname}.u = {ld_param_list}
            {{tab}}params_{{planet}}_{instmod_fullname}.limb_dark = '{ld_mod_name}'"""
                    template_batman_pl = (template_batman_pl.
                                          format(instmod_fullname=instmdl.full_name,
                                                 ld_mod_name=LD_parcont.ld_type,
                                                 ld_param_list=ld_param_list))
                else:
                    template_batman_pl = """
            {{tab}}params_{{planet}}.t0 = {{tc}}
            {{tab}}params_{{planet}}.per = {{P}}
            {{tab}}params_{{planet}}.rp = {{Rrat}}
            {{tab}}params_{{planet}}.inc = inc_{{planet}}
            {{tab}}params_{{planet}}.ecc = ecc_{{planet}}
            {{tab}}params_{{planet}}.w = omega_{{planet}}
            {{tab}}params_{{planet}}.u = {ld_param_list}
            {{tab}}params_{{planet}}.limb_dark = '{ld_mod_name}'"""
                    template_batman_pl = template_batman_pl.format(ld_mod_name=LD_parcont.ld_type,
                                                                   ld_param_list=ld_param_list)
                template_preambule_pl += template_batman_pl

                if self.parametrisation in self.LC_multis_parametrisations:
                    if multi_instmodl:
                        for instmdl in l_inst_model:
                            template_batman_pl_2 = """
            {{tab}}params_{{planet}}_{instmod_fullname}.a = aR_{{planet}}
            """.format(instmod_fullname=instmdl.full_name)
                        template_preambule_pl += template_batman_pl_2
                    else:
                        template_preambule_pl += """
            {tab}params_{planet}.a = aR_{planet}
            """
                else:
                    if multi_instmodl:
                        for instmdl in l_inst_model:
                            template_batman_pl_3 = """
            {{tab}}params_{{planet}}_{instmod_fullname}.a = {{aR}}
            """.format
                            template_preambule_pl += template_batman_pl_3
                    else:
                        template_preambule_pl += """
            {tab}params_{planet}.a = {aR}
            """
        else:
            template_preambule_pl += """
            {tab}omega_{planet} = getomega_fast({secosw}, {sesinw})
            {tab}inc_{planet} = acos({cosinc})
            """
        template_preambule_pl = dedent(template_preambule_pl)

        # Initialise the local dictionary for the creation of the datasim functions by exec
        # ldict = locals().copy()
        ldict = {}
        if datasets is not None:
            if multi_instmodl:
                l_t = []
                l_tref = []
                for instmdl, dst in zip(l_inst_model, l_dataset):
                        l_t.append(dst.get_time())
                        l_tref.append(dst.get_tref())
                ldict["l_t"] = l_t
                ldict["l_tref"] = l_tref
            else:
                ldict["t"] = datasets.get_time()
                ldict["tref"] = datasets.get_tref()

        # Add the initialisation of the TransitModel (to the template_preambule)
        l_par_bat = []
        for ii, instmdl, dst, LD_parcont in zip(range(len(l_inst_model)), l_inst_model, l_dataset,
                                                l_LD_parcont):
            supersamp = self.get_supersamp(instmdl.full_name)
            if supersamp > 1:
                exptime = self.get_exptime(instmdl.full_name)
                if self.transit_model == "batman":
                    if dst is None:
                        if multi_instmodl:
                            template_batman_pl_4 = ("{{tab}}m_{{planet}}_{instmod_fullname} "
                                                    "= TransitModel("
                                                    "params_{{planet}}_{instmod_fullname}, "
                                                    "l_t[{ii}], "
                                                    "supersample_factor={supersamp},"
                                                    "exp_time={exptime})"
                                                    "\n".format(supersamp=supersamp,
                                                                exptime=exptime,
                                                                ii=ii,
                                                                instmod_fullname=instmdl.full_name))
                        else:
                            template_batman_pl_4 = ("{{tab}}m_{{planet}} = TransitModel("
                                                    "params_{{planet}}, t, "
                                                    "supersample_factor={supersamp},"
                                                    "exp_time={exptime})"
                                                    "\n".format(supersamp=supersamp,
                                                                exptime=exptime))
                        template_preambule_pl += template_batman_pl_4
                        l_par_bat.append({})
                        for planet in self.planets.values():
                            l_par_bat[ii][planet.name] = TransitParams()
                    else:
                        l_par_bat.append({})
                        for planet in self.planets.values():
                            l_par_bat[ii][planet.name] = TransitParams()
                            if multi_instmodl:  # time of inf. conjunction
                                l_par_bat[ii][planet.name].t0 = ldict["l_t"][ii].mean()
                            else:
                                l_par_bat[ii][planet.name].t0 = ldict["t"][ii].mean()
                            l_par_bat[ii][planet.name].per = 1.   # orbital period
                            l_par_bat[ii][planet.name].rp = 0.1   # planet radius(in stel radii)
                            l_par_bat[ii][planet.name].a = 15.    # semi-major axis(in stel radii)
                            l_par_bat[ii][planet.name].inc = 87.  # orbital inclination (in degrees)
                            l_par_bat[ii][planet.name].ecc = 0.   # eccentricity
                            l_par_bat[ii][planet.name].w = 90.    # long. of periastron (in deg.)
                            l_par_bat[ii][planet.name].limb_dark = LD_parcont.ld_type  # LD model
                            l_par_bat[ii][planet.name].u = LD_parcont.init_LD_values  # LDC init val
                else:
                    m_pytransit = MandelAgol(supersampling=supersamp, exptime=exptime,
                                             model=LD_parcont.ld_type)
            else:
                if self.transit_model == "batman":
                    if dst is None:
                        if multi_instmodl:
                            template_batman_pl_5 = ("{{tab}}m_{{planet}} = TransitModel("
                                                    "params_{{planet}}, l_tp[{ii}])"
                                                    "\n".format(ii=ii))
                            template_preambule_pl += template_batman_pl_5
                        else:
                            template_preambule_pl += ("{tab}m_{planet} = TransitModel("
                                                      "params_{planet}, t)\n")
                        l_par_bat.append({})
                        for planet in self.planets.values():
                            l_par_bat[ii][planet.name] = TransitParams()
                    else:
                        l_par_bat.append({})
                        for planet in self.planets.values():
                            l_par_bat[ii][planet.name] = TransitParams()
                            if multi_instmodl:  # time of inf. conjunction
                                l_par_bat[ii][planet.name].t0 = ldict["l_t"][ii].mean()
                            else:
                                l_par_bat[ii][planet.name].t0 = ldict["t"][ii].mean()
                            l_par_bat[ii][planet.name].per = 1.   # orbital period
                            l_par_bat[ii][planet.name].rp = 0.1   # planet radius(in stel radii)
                            l_par_bat[ii][planet.name].a = 15.    # semi-major axis(in stel radii)
                            l_par_bat[ii][planet.name].inc = 87.  # orbital inclination (in degrees)
                            l_par_bat[ii][planet.name].ecc = 0.   # eccentricity
                            l_par_bat[ii][planet.name].w = 90.    # long. of periastron (in deg.)
                            l_par_bat[ii][planet.name].limb_dark = LD_parcont.ld_type  # LD model
                            l_par_bat[ii][planet.name].u = LD_parcont.init_LD_values  # LDC init val
                else:
                    m_pytransit = MandelAgol(model=LD_parcont.ld_type)

        # Create the text for template_planet_lc
        if self.transit_model == "batman":
            if multi_instmodl:
                template_planet_lc = ("+ m_{{planet}}_{instmod_fullname}.light_curve("
                                      "params_{{planet}}_{instmod_fullname}) - 1 "
                                      "".format(instmod_fullname=instmdl.full_name))
            else:
                template_planet_lc = ("+ m_{planet}.light_curve(params_{planet}) - 1 ")
        else:
            if self.parametrisation in self.LC_multis_parametrisations:
                if multi_instmodl:
                    template_planet_lc = ("+ m.evaluate(l_t[{ii}], {Rrat}, {ld_param_list}, "
                                          "{tc}, {P}, aR_{planet}, inc_{planet}, "
                                          "ecc_{planet}, omega_{planet}) - 1 ")
                else:
                    template_planet_lc = ("+ m.evaluate(t, {Rrat}, {ld_param_list}, {tc}, {P}, "
                                          "aR_{planet}, inc_{planet}, ecc_{planet}, "
                                          "omega_{planet}) - 1 ")
            else:
                if multi_instmodl:
                    template_planet_lc = ("+ m.evaluate(l_t[{ii}], {Rrat}, {ld_param_list}, "
                                          "{tc}, {P}, {aR}, inc_{planet}, "
                                          "ecc_{planet}, omega_{planet}) - 1 ")
                else:
                    template_planet_lc = ("+ m.evaluate(t, {Rrat}, {ld_param_list}, {tc}, "
                                          "{P}, {aR}, inc_{planet}, ecc_{planet}, "
                                          "omega_{planet}) - 1 ")

        # Save the param_nb and arg_list for the whole function before iterating over the planets
        # text_def_func_before = text_def_func[self.key_whole]
        param_nb_before = param_nb[self.key_whole]
        arg_list_before = deepcopy(arg_list[self.key_whole])

        # Initialise the text for the whole system preambule
        preambule_whole = ""
        l_whole_planets_lc = []
        for instmdl in l_inst_model:
            l_whole_planets_lc.append("")
        for jj, planet in enumerate(self.planets.values()):
            # Initialise arg_list and param_nb for the current planet
            arg_list[planet.name] = deepcopy(arg_list_before)
            param_nb[planet.name] = param_nb_before

            # Create the params_planet object
            if self.transit_model == "batman":
                for ii, instmdl, dst, par_bat in zip(range(len(l_inst_model)), l_inst_model,
                                                     l_dataset, l_par_bat):
                    if dst is not None:
                        if multi_instmodl:
                            params_pl_inst = ("params_{planet}_{instmod_fullname}"
                                              "".format(planet=planet.name,
                                                        instmod_fullname=instmdl.full_name))
                            tt = ldict["l_t[{ii}]".format(ii=ii)]
                        else:
                            params_pl_inst = "params_{planet}".format(planet=planet.name)
                            tt = ldict["t"]
                        ldict[params_pl_inst] = par_bat[planet.name]
                        supersamp = self.get_supersamp(instmdl.full_name)
                        if supersamp > 1:
                            exptime = self.get_exptime(instmdl.full_name)
                            m_batman = TransitModel(ldict[params_pl_inst],
                                                    tt, supersample_factor=supersamp,
                                                    exp_time=exptime)
                        else:
                            m_batman = TransitModel(ldict[params_pl_inst], tt)
                        if multi_instmodl:
                            m_pl_inst = ("m_{planet}_{instmod_fullname}"
                                         "".format(planet=planet.name,
                                                   instmod_fullname=instmdl.full_name))

                        else:
                            m_pl_inst = "m_{planet}".format(planet=planet.name)
                        ldict[m_pl_inst] = m_batman
                    else:
                        if multi_instmodl:
                            params_pl_inst = ("params_{planet}_{instmod_fullname}"
                                              "".format(planet=planet.name,
                                                        instmod_fullname=instmdl.full_name))
                        else:
                            params_pl_inst = "params_{planet}".format(planet=planet.name)
                        ldict[params_pl_inst] = par_bat[planet.name]

            # Create two dictionaries which will contain the text for each planet parameter for the
            # current planet and for the whole system.
            params_planet = {}
            params_whole = {}
            # Create the text for each planet parameter for the current planet and for the whole
            # system.
            l_param_name = ["secosw", "sesinw", "cosinc", "tc", "P", "Rrat"]
            l_param = [planet.secosw, planet.sesinw, planet.cosinc, planet.tc, planet.P,
                       planet.Rrat]
            if self.parametrisation not in self.LC_multis_parametrisations:
                l_param_name.append("aR")
                l_param.append(planet.aR)
            else:
                params_planet["aR"] = ""
            for param_name, param in zip(l_param_name, l_param):
                if param.free:
                    param_text = "p[{}]"
                    params_whole[param_name] = param_text.format(param_nb[self.key_whole])
                    param_nb[self.key_whole] += 1
                    arg_list[self.key_whole]["param"].append(param.full_name)
                    params_planet[param_name] = param_text.format(param_nb[planet.name])
                    param_nb[planet.name] += 1
                    arg_list[planet.name]["param"].append(param.full_name)
                else:
                    params_whole[param_name] = "{}".format(param.value)
                    params_planet[param_name] = params_whole[param_name]

            # Create the preambule text that compute intermediate variables
            # No need to make different cases for if batman or not or is dataset is None or not
            # because if one argument is not in the template, it is not used and this is it.
            preambule_planet = (template_preambule_pl.
                                format(planet=planet.name, secosw=params_planet["secosw"],
                                       sesinw=params_planet["sesinw"],
                                       tc=params_planet["tc"], rhostar=rhostar,
                                       cosinc=params_planet["cosinc"], P=params_planet["P"],
                                       Rrat=params_planet["Rrat"], aR=params_planet["aR"],
                                       # ld_mod_name=LD_parcont.ld_type,
                                       # ld_param_list=ld_param_list,
                                       tab=tab))
            preambule_whole += (template_preambule_pl.
                                format(planet=planet.name, secosw=params_whole["secosw"],
                                       sesinw=params_whole["sesinw"], tc=params_whole["tc"],
                                       cosinc=params_whole["cosinc"], P=params_whole["P"],
                                       Rrat=params_whole["Rrat"], aR=params_planet["aR"],
                                       # ld_mod_name=LD_parcont.ld_type,
                                       rhostar=rhostar,
                                       # ld_param_list=ld_param_list,
                                       tab=tab))

            # planets LC contribution (planet_lc and whole_planets_lc)
            # No need for case if batman or if dataset is None. Same reason than above
            l_planet_lc = []
            for ii, ld_param_list in zip(range(len(l_inst_model)), l_ld_param_list):
                l_planet_lc.append(template_planet_lc.format(planet=planet.name,
                                                             aR=params_planet["aR"],
                                                             Rrat=params_planet["Rrat"],
                                                             tc=params_planet["tc"],
                                                             P=params_planet["P"],
                                                             ld_param_list=ld_param_list,
                                                             ii=ii
                                                             ))
                l_whole_planets_lc[ii] += template_planet_lc.format(planet=planet.name,
                                                                    aR=params_planet["aR"],
                                                                    Rrat=params_whole["Rrat"],
                                                                    tc=params_whole["tc"],
                                                                    P=params_whole["P"],
                                                                    ld_param_list=ld_param_list,
                                                                    ii=ii
                                                                    )

            # Fill returns text for each planet
            returns_pl = ""
            for oot_var, planet_lc in zip(l_oot_var, l_planet_lc):
                returns_pl += template_returns_instmod.format(oot_var=oot_var,
                                                              planets_lc=planet_lc)
                returns_pl += ", "
            returns_pl = returns_pl[:-2]

            # Finalise the  text of planet LC simulator function
            text_def_func[planet.name] = (template_function.
                                          format(object=planet.name, preambule=preambule_planet,
                                                 arguments=arguments, returns=returns_pl, tab=tab))
            logger.debug("text of {object} LC simulator function :\n{text_func}"
                         "".format(object=planet.name, text_func=text_def_func[planet.name]))

        # Fill returns text for the whole system
        returns_whole = ""
        for oot_var, whole_planet_lc in zip(l_oot_var, l_whole_planets_lc):
            returns_whole += template_returns_instmod.format(oot_var=oot_var,
                                                             planets_lc=whole_planet_lc)
            returns_whole += ", "
        returns_whole = returns_whole[:-2]

        # Finalise the text of whole system LC simulator function
        text_def_func[self.key_whole] = (template_function.
                                         format(object=self.key_whole, preambule=preambule_whole,
                                                arguments=arguments, returns=returns_whole,
                                                tab=tab))
        logger.debug("text of {object} LC simulator function :\n{text_func}"
                     "".format(object=self.key_whole, text_func=text_def_func[self.key_whole]))

        # Create and fill the output dictionnary containing the datasimulators functions.
        dico_docf = dict.fromkeys(text_def_func.keys(), None)
        for obj_key in dico_docf:
            ldict["getecc_fast"] = getecc_fast
            ldict["getomega_fast"] = getomega_fast
            ldict["acos"] = acos
            if self.parametrisation in self.LC_multis_parametrisations:
                ldict["getaoverr"] = getaoverr
            if self.transit_model == "batman":
                if datasets is None:
                    ldict["TransitModel"] = TransitModel
                ldict["degrees"] = degrees
            else:
                ldict["m"] = m_pytransit
            exec(text_def_func[obj_key], ldict)
            dico_docf[obj_key] = DocFunction(function=ldict[function_name.format(object=obj_key)],
                                             arg_list=arg_list[obj_key])
            dico_docf[obj_key].inst_models = [instmdl.full_name for instmdl in l_inst_model]
        # print(list(dico_docf.keys()))
        return dico_docf

    # def is_star(self, name):
    #     """Returns True if a star of this name exists in the gravgroup."""
    #     return name in self.stars
    #
    # def is_planet(self, name):
    #     """Returns True if a planet of this name exists in the gravgroup."""
    #     return name in self.planets
    #
    # def rm_star(self, name):
    #     """Delete a Star in the GravGroup."""
    #     res = self.stars.pop(name, None)
    #     if res is None:
    #         logger.warning("The deletion of the star {} from the GravGroup has failed because "
    #                        "this star was not found.".format(name))
    #     else:
    #         logger.info("The star {} has been removed from the GravGroup."
    #                     "".format(name))
    #
    # def rm_planet(self, name):
    #     """Delete a Planet in the GravGroup."""
    #     res = self.planets.pop(name, None)
    #     if res is None:
    #         logger.warning("The deletion of the planet {} from the GravGroup has failed because "
    #                        "this star was not found.".format(name))
    #     else:
    #         logger.info("The planet {} has been removed from the GravGroup."
    #                     "".format(name))
