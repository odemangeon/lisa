#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Gravitational group (gravgroup) module.

The objective of this module is to define the GravGroup, Star and Planet class.
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
from ...core.model.core_model import Core_Model
from ....tools.function_w_doc import DocFunction
from ....tools.convert import getecc_fast, getomega_fast, gettp_fast
from ....tools.human_machine_interface.QCM import QCM_utilisateur
from ....tools.miscellaneous import spacestring_like

# from pdb import set_trace


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
            self.__SSE4instmodfname = OrderedDict()  # Supersampling and Exposure time for each instrument
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
        dico["transit_model"] = self.transit_model
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

    def _create_datasimulator_RV(self, inst_model):
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

        # Initialise the template function text
        function_name = ("RVsim_{{object}}_{instmod_fullname}"
                         "".format(instmod_fullname=inst_model.full_name))
        template_function = """
        def {function_name}(p, t, tref=None):
        {{tab}}{{preambule}}
        {{tab}}return {{delta_inst_rv}} {{drift_rv}} {{star_mean_rv}} {{planets_rv}}
        """.format(function_name=function_name)
        tab = "    "
        template_function = dedent(template_function)

        # Initialise arg_list and param_nb for key "whole"
        arg_list[self.key_whole] = OrderedDict()
        arg_list[self.key_whole]["param"] = []
        arg_list[self.key_whole]["kwargs"] = []
        param_nb[self.key_whole] = 0

        # Add time in the kwargs entry of the whole system arg_list
        arg_list[self.key_whole]["kwargs"].append("t")

        # Create for the instrument Delta RV (delta_inst_rv)
        inst_name = inst_model.instrument.name
        ## RVrefglobal_inst: name of the instrument chosen as global RV reference (eg: HARPS)
        RVrefglobal_instname = self.RV_globalref_instname
        ## RVref4inst_modname: name of the instrument model chosen as reference for the current
        ## instrument (eg: default)
        RVref4inst_modname = self.get_RVref4inst_modname(inst_name)
        ## RVrefglobal_modname: name of the instrument model chosen as reference for the global RV
        ## reference instrument (eg: default model of the HARPS instrument)
        RVrefglobal_modname = self.get_RVref4inst_modname(RVrefglobal_instname)
        # Add the Delta_RV of the global RV reference instrument model if needed
        delta_inst_rv = ""  # If no delta RV is main, I still need an empty string
        if inst_name != RVrefglobal_instname:
            instmod_RVref4inst = self.instruments["RV"][inst_name][RVref4inst_modname]
            if instmod_RVref4inst.DeltaRV.main:
                if instmod_RVref4inst.DeltaRV.free:
                    delta_inst_rv += "p[{}] + ".format(param_nb[self.key_whole])
                    param_nb[self.key_whole] += 1
                    arg_list[self.key_whole]["param"].append(instmod_RVref4inst.DeltaRV.full_name)
                else:
                    delta_inst_rv += "{} + ".format(instmod_RVref4inst.DeltaRV.value)
        # Add the Delta_RV of the model used as RV reference for the current instrument
        if inst_model.name != RVref4inst_modname:
            if inst_model.DeltaRV.main:
                if inst_model.DeltaRV.free:
                    delta_inst_rv += "p[{}] + ".format(param_nb[self.key_whole])
                    param_nb[self.key_whole] += 1
                    arg_list[self.key_whole]["param"].append(inst_model.DeltaRV.full_name)
                else:
                    delta_inst_rv += "{} + ".format(inst_model.DeltaRV.value)

        # Create the text for the istrument RV drift (drift_rv)
        if inst_model.driftRV.main:
            arg_list[self.key_whole]["kwargs"].append("tref")
            if inst_model.driftRV.free:
                drift_rv = "p[{}] * (t - tref) + ".format(param_nb[self.key_whole])
                param_nb[self.key_whole] += 1
                arg_list[self.key_whole]["param"].append(inst_model.driftRV.full_name)
            else:
                if inst_model.driftRV.value != 0.0:
                    drift_rv = "{} * (t - tref) + ".format(inst_model.driftRV.value)
                else:
                    drift_rv = ""
        else:
            drift_rv = ""

        # Create the text for the star mean RV (star_mean_rv)
        if star.v0.free:
            star_mean_rv = "p[{}]".format(param_nb[self.key_whole])
            param_nb[self.key_whole] += 1
            arg_list[self.key_whole]["param"].append(star.v0.full_name)
        else:
            star_mean_rv = "{}".format(star.v0.value)

        # Save the param_nb and arg_list for the whole function before iterating over the planets
        # text_def_func_before = text_def_func[self.key_whole]
        param_nb_before = param_nb[self.key_whole]
        arg_list_before = deepcopy(arg_list[self.key_whole])

        # Iterate over the planets to create the preambules (preambule_planet and preambule_whole),
        # the planets RV contribution (planet_rv and whole_planets_rv) and finalise the text of
        # planets functions.
        preambule_whole = ""
        template_preambule = """
        {tab}ecc_{planet} = getecc_fast({secosw}, {sesinw})
        {tab}omega_{planet} = getomega_fast({secosw}, {sesinw})
        {tab}tp_{planet} = gettp_fast({P}, {tc}, ecc_{planet}, omega_{planet})
        """
        template_planet_rv = ("+ pl_rv_array(t, 0., {K}, omega_{planet}, ecc_{planet}, tp_{planet},"
                              " {P})")
        whole_planets_rv = ""
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
            planet_rv = template_planet_rv.format(planet=planet.name, K=params_planet["K"],
                                                  P=params_planet["P"])
            whole_planets_rv += template_planet_rv.format(planet=planet.name, K=params_whole["K"],
                                                          P=params_whole["P"])

            # Finalise the  text of planet RV simulator function
            text_def_func[planet.name] = (template_function.
                                          format(object=planet.name, preambule=preambule_planet,
                                                 delta_inst_rv=delta_inst_rv, drift_rv=drift_rv,
                                                 star_mean_rv=star_mean_rv, planets_rv=planet_rv,
                                                 tab=tab))
            logger.debug("text of {object} RV simulator function :\n{text_func}"
                         "".format(object=planet.name, text_func=text_def_func[planet.name]))

        # Finalise the  text of whole system RV simulator function
        text_def_func[self.key_whole] = (template_function.
                                         format(object=self.key_whole, preambule=preambule_whole,
                                                delta_inst_rv=delta_inst_rv, drift_rv=drift_rv,
                                                star_mean_rv=star_mean_rv, tab=tab,
                                                planets_rv=whole_planets_rv))
        logger.debug("text of {object} RV simulator function :\n{text_func}"
                     "".format(object=self.key_whole, text_func=text_def_func[self.key_whole]))

        # Create and fill the output dictionnary containing the datasimulators functions.
        dico_docf = dict.fromkeys(text_def_func.keys(), None)
        for obj_key in dico_docf:
            ldict = locals().copy()
            ldict["getecc_fast"] = getecc_fast
            ldict["getomega_fast"] = getomega_fast
            ldict["gettp_fast"] = gettp_fast
            ldict["pl_rv_array"] = pl_rv_array
            exec(text_def_func[obj_key], ldict)
            dico_docf[obj_key] = DocFunction(function=ldict[function_name.format(object=obj_key)],
                                             arg_list=arg_list[obj_key])
        return dico_docf

    def _create_datasimulator_LC(self, inst_model):
        """Return datasimulator functions.

        A datasimualtor function is created for the whole dataset_database and for each planet
        individually.

        :param Instrument_Model inst_model: instance of Instrument_Model

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

        # Initialise the template function text
        function_name = ("LCsim_{{object}}_{instmod_fullname}"
                         "".format(instmod_fullname=inst_model.full_name))
        template_function = """
        def {function_name}(p, t, tref=None):
        {{tab}}{{preambule}}
        {{tab}}return 1 {{oot_var}}{{planets_lc}}
        """.format(function_name=function_name)
        tab = "    "
        template_function = dedent(template_function)

        # Initialise arg_list and param_nb for key "whole"
        arg_list[self.key_whole] = OrderedDict()
        arg_list[self.key_whole]["param"] = []
        arg_list[self.key_whole]["kwargs"] = []
        param_nb[self.key_whole] = 0

        # Add time in the kwargs entry of the whole system arg_list
        arg_list[self.key_whole]["kwargs"].append("t")

        # Create the text for oot_var
        oot_var = ""
        if inst_model.get_with_OOT_var():
            for order in range(inst_model.get_OOT_var_order() + 1):
                OOT_param_name = inst_model.get_OOT_param_name(order)
                OOT_param_fullname = inst_model.parameters[OOT_param_name].full_name
                if inst_model.parameters[OOT_param_name].main:
                    value_not0 = True
                    if inst_model.parameters[OOT_param_name].free:
                        oot_var += "+ p[{}]".format(param_nb[self.key_whole])
                        param_nb[self.key_whole] += 1
                        arg_list[self.key_whole]["param"].append(OOT_param_fullname)
                    else:
                        if inst_model.parameters[OOT_param_name].value != 0.0:
                            oot_var += "+ {}".format(OOT_param_name.value)
                        else:
                            value_not0 = False
                    if value_not0 and order > 0:
                        if "tref" not in arg_list[self.key_whole]["kwargs"]:
                            arg_list[self.key_whole]["kwargs"].append("tref")
                        if order == 1:
                            oot_var += " * (t - tref) "
                        elif order > 1:
                            oot_var += " * (t - tref)**{} ".format(order)
                    elif value_not0 and order == 0:
                        oot_var += " "

        # # Create text for the instrument DeltaOOT (delta_oot)
        # #inst_name = inst_model.instrument.name
        # if inst_model.DeltaOOT.main:
        #     if inst_model.DeltaOOT.free:
        #         delta_oot = "+ p[{}]".format(param_nb[self.key_whole])
        #         param_nb[self.key_whole] += 1
        #         arg_list[self.key_whole]["param"].append(inst_model.DeltaOOT.full_name)
        #     else:
        #         if inst_model.DeltaOOT.value != 0.0:
        #             delta_oot = "+ {}".format(inst_model.DeltaOOT.value)
        #         else:
        #             delta_oot = ""
        # else:
        #     delta_oot = ""  # If no deltaOOT is main, I still need an empty string
        #
        # # Create the text for the instrument OOT drift (drift_oot)
        # if inst_model.driftOOT.main:
        #     arg_list[self.key_whole]["kwargs"].append("tref")
        #     if inst_model.driftOOT.free:
        #         # drift_oot = "+ p[{}] * (t - t.min())".format(param_nb[self.key_whole])
        #         drift_oot = "+ p[{}] * (t - tref)".format(param_nb[self.key_whole])
        #         param_nb[self.key_whole] += 1
        #         arg_list[self.key_whole]["param"].append(inst_model.driftOOT.full_name)
        #     else:
        #         # drift_oot = "+ {} * (t - t.min())".format(inst_model.driftOOT.value)
        #         if inst_model.driftOOT.value != 0.0:
        #             drift_oot = "+ {} * (t - tref)".format(inst_model.driftOOT.value)
        #         else:
        #             drift_oot = ""
        # else:
        #     drift_oot = ""

        # Create the template preambule
        if self.transit_model == "batman":
            template_preambule = """
            {tab}ecc_{planet} = getecc_fast({secosw}, {sesinw})
            {tab}omega_{planet} = degrees(getomega_fast({secosw}, {sesinw}))
            {tab}inc_{planet} = degrees(acos({cosinc}))
            {tab}params_{planet}.t0 = {tc}
            {tab}params_{planet}.per = {P}
            {tab}params_{planet}.rp = {Rrat}
            {tab}params_{planet}.a = {aR}
            {tab}params_{planet}.inc = inc_{planet}
            {tab}params_{planet}.ecc = ecc_{planet}
            {tab}params_{planet}.w = omega_{planet}
            {tab}params_{planet}.limb_dark = '{ld_mod_name}'
            {tab}params_{planet}.u = {ld_param_list}
            """
        else:
            template_preambule = """
            {tab}ecc_{planet} = getecc_fast({secosw}, {sesinw})
            {tab}omega_{planet} = getomega_fast({secosw}, {sesinw})
            {tab}inc_{planet} = acos({cosinc})
            """
        template_preambule = dedent(template_preambule)

        # Get the ld_parcont
        LD_parcont_name = self.ldmodel4instmodfname[inst_model.full_name]
        LD_parcont = self.LDs[LD_parcont_name]

        # Add the initialisation of the TransitModel to the template
        supersamp = self.get_supersamp(inst_model.full_name)
        if supersamp > 1:
            exptime = self.get_exptime(inst_model.full_name)
            if self.transit_model == "batman":
                template_preambule += ("{{tab}}m_{{planet}} = TransitModel(params_{{planet}}, t, "
                                       "supersample_factor={supersamp}, exp_time={exptime})\n"
                                       "".format(supersamp=supersamp, exptime=exptime))
            else:
                m_pytransit = MandelAgol(supersampling=supersamp, exptime=exptime,
                                         model=LD_parcont.ld_type)
        else:
            if self.transit_model == "batman":
                template_preambule += ("{tab}m_{planet} = TransitModel(params_{planet}, t)\n")
            else:
                m_pytransit = MandelAgol(model=LD_parcont.ld_type)

        # Create the ld_param_list
        ld_param_list = "["
        for param in LD_parcont.get_list_params(main=True):
            if param.free:
                ld_param_list += "p[{}], ".format(param_nb[self.key_whole])
                param_nb[self.key_whole] += 1
                arg_list[self.key_whole]["param"].append(param.full_name)
            else:
                ld_param_list += "{}, ".format(param.value)
        ld_param_list += "]"

        # Create the text for template_planet_lc
        if self.transit_model == "batman":
            template_planet_lc = ("+ m_{planet}.light_curve(params_{planet}) - 1 ")
        else:
            template_planet_lc = ("+ m.evaluate(t, {Rrat}, {ld_param_list}, {tc}, {P}, {aR}, "
                                  "inc_{planet}, ecc_{planet}, omega_{planet}) - 1 ")

        # Save the param_nb and arg_list for the whole function before iterating over the planets
        # text_def_func_before = text_def_func[self.key_whole]
        param_nb_before = param_nb[self.key_whole]
        arg_list_before = deepcopy(arg_list[self.key_whole])

        # Initialise the local dictionary for the creation of the datasim functions by exec
        ldict = locals().copy()

        # Initialise the text for the whole system preambule
        preambule_whole = ""
        whole_planets_lc = ""
        for i, planet in enumerate(self.planets.values()):
            # Initialise arg_list and param_nb for the current planet
            arg_list[planet.name] = deepcopy(arg_list_before)
            param_nb[planet.name] = param_nb_before

            # Create the params_planet object
            ldict["params_{planet}".format(planet=planet.name)] = TransitParams()

            # Create two dictionaries which will contain the text for each planet parameter for the
            # current planet and for the whole system.
            params_planet = {}
            params_whole = {}
            # Create the text for each planet parameter for the current planet and for the whole
            # system.
            for param_name, param in zip(["secosw", "sesinw", "cosinc", "tc", "P", "Rrat", "aR"],
                                         [planet.secosw, planet.sesinw, planet.cosinc, planet.tc,
                                          planet.P, planet.Rrat, planet.aR]):
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
            if self.transit_model == "batman":
                preambule_planet = (template_preambule.
                                    format(planet=planet.name, secosw=params_planet["secosw"],
                                           sesinw=params_planet["sesinw"], tc=params_planet["tc"],
                                           cosinc=params_planet["cosinc"], P=params_planet["P"],
                                           Rrat=params_planet["Rrat"], aR=params_planet["aR"],
                                           ld_mod_name=LD_parcont.ld_type,
                                           ld_param_list=ld_param_list, tab=tab))
                preambule_whole += (template_preambule.
                                    format(planet=planet.name, secosw=params_whole["secosw"],
                                           sesinw=params_whole["sesinw"], tc=params_whole["tc"],
                                           cosinc=params_whole["cosinc"], P=params_whole["P"],
                                           Rrat=params_whole["Rrat"], aR=params_whole["aR"],
                                           ld_mod_name=LD_parcont.ld_type,
                                           ld_param_list=ld_param_list, tab=tab))
            else:
                preambule_planet = (template_preambule.
                                    format(planet=planet.name, secosw=params_planet["secosw"],
                                           sesinw=params_planet["sesinw"],
                                           cosinc=params_planet["cosinc"], tab=tab))
                preambule_whole += (template_preambule.
                                    format(planet=planet.name, secosw=params_whole["secosw"],
                                           sesinw=params_whole["sesinw"],
                                           cosinc=params_whole["cosinc"], tab=tab))

            # planets RV contribution (planet_lc and whole_planets_lc)
            if self.transit_model == "batman":
                planet_lc = template_planet_lc.format(planet=planet.name)
                whole_planets_lc += template_planet_lc.format(planet=planet.name)
            else:
                planet_lc = template_planet_lc.format(planet=planet.name, aR=params_planet["aR"],
                                                      Rrat=params_planet["Rrat"],
                                                      tc=params_planet["tc"], P=params_planet["P"],
                                                      ld_param_list=ld_param_list)
                whole_planets_lc += template_planet_lc.format(planet=planet.name,
                                                              aR=params_whole["aR"],
                                                              Rrat=params_whole["Rrat"],
                                                              tc=params_whole["tc"],
                                                              P=params_whole["P"],
                                                              ld_param_list=ld_param_list)

            # Finalise the  text of planet LC simulator function
            text_def_func[planet.name] = (template_function.
                                          format(object=planet.name, preambule=preambule_planet,
                                                 oot_var=oot_var,
                                                 planets_lc=planet_lc, tab=tab))
            logger.debug("text of {object} LC simulator function :\n{text_func}"
                         "".format(object=planet.name, text_func=text_def_func[planet.name]))

        # Finalise the  text of whole system RV simulator function
        text_def_func[self.key_whole] = (template_function.
                                         format(object=self.key_whole, preambule=preambule_whole,
                                                oot_var=oot_var,
                                                planets_lc=whole_planets_lc, tab=tab))
        logger.debug("text of {object} LC simulator function :\n{text_func}"
                     "".format(object=self.key_whole, text_func=text_def_func[self.key_whole]))

        # Create and fill the output dictionnary containing the datasimulators functions.
        dico_docf = dict.fromkeys(text_def_func.keys(), None)
        for obj_key in dico_docf:
            ldict["getecc_fast"] = getecc_fast
            ldict["getomega_fast"] = getomega_fast
            ldict["acos"] = acos
            ldict["degrees"] = degrees
            if self.transit_model == "batman":
                ldict["TransitModel"] = TransitModel
            else:
                ldict["m"] = m_pytransit
            exec(text_def_func[obj_key], ldict)
            dico_docf[obj_key] = DocFunction(function=ldict[function_name.format(object=obj_key)],
                                             arg_list=arg_list[obj_key])
        return dico_docf

    def _create_datasimulator_woinst_RV(self):
        """Return datasimulator functions without instrument impact.

        A datasimualtor function is created for the whole dataset_database and for each planet
         individually.

        ----
        Returns:
            Returns:
                - A dictionary with DocFunctions containing the data simulator function for the
                 whole system ("whole") and for the each planet individually ("planet_name")
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

        # Initialise the template function text
        function_name = "RVsim_{{object}}_woinst"
        template_function = """
        def {function_name}(p, t):
        {{tab}}{{preambule}}
        {{tab}}return {{star_mean_rv}} {{planets_rv}}
        """.format(function_name=function_name)
        tab = "    "
        template_function = dedent(template_function)

        # Initialise arg_list and param_nb for key "whole"
        arg_list[self.key_whole] = OrderedDict()
        arg_list[self.key_whole]["param"] = []
        arg_list[self.key_whole]["kwargs"] = []
        param_nb[self.key_whole] = 0

        # Create the text for the star mean RV (star_mean_rv)
        if star.v0.free:
            star_mean_rv = "p[{}]".format(param_nb[self.key_whole])
            param_nb[self.key_whole] += 1
            arg_list[self.key_whole]["param"].append(star.v0.full_name)
        else:
            star_mean_rv = "{}".format(star.v0.value)

        # Save the param_nb and arg_list for the whole function before iterating over the planets
        # text_def_func_before = text_def_func[self.key_whole]
        param_nb_before = param_nb[self.key_whole]
        arg_list_before = deepcopy(arg_list[self.key_whole])

        # Iterate over the planets to create the preambules (preambule_planet and preambule_whole),
        # the planets RV contribution (planet_rv and whole_planets_rv) and finalise the text of
        # planets functions.
        preambule_whole = ""
        template_preambule = """
        {tab}ecc_{planet} = getecc_fast({secosw}, {sesinw})
        {tab}omega_{planet} = getomega_fast({secosw}, {sesinw})
        {tab}tp_{planet} = gettp_fast({P}, {tc}, ecc_{planet}, omega_{planet})
        """
        template_planet_rv = ("+ pl_rv_array(t, 0., {K}, omega_{planet}, ecc_{planet}, tp_{planet},"
                              " {P})")
        whole_planets_rv = ""
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
            planet_rv = template_planet_rv.format(planet=planet.name, K=params_planet["K"],
                                                  P=params_planet["P"])
            whole_planets_rv += template_planet_rv.format(planet=planet.name, K=params_whole["K"],
                                                          P=params_whole["P"])

            # Finalise the  text of planet RV simulator function
            text_def_func[planet.name] = (template_function.
                                          format(object=planet.name, preambule=preambule_planet,
                                                 star_mean_rv=star_mean_rv, planets_rv=planet_rv,
                                                 tab=tab))
            logger.debug("text of {object} RV simulator function :\n{text_func}"
                         "".format(object=planet.name, text_func=text_def_func[planet.name]))

            # Add time in the kwargs entry of the planet arg_list
            arg_list[planet.name]["kwargs"].append("t")

        # Finalise the  text of whole system RV simulator function
        text_def_func[self.key_whole] = (template_function.
                                         format(object=self.key_whole, preambule=preambule_whole,
                                                star_mean_rv=star_mean_rv, tab=tab,
                                                planets_rv=whole_planets_rv))
        logger.debug("text of {object} RV simulator function :\n{text_func}"
                     "".format(object=self.key_whole, text_func=text_def_func[self.key_whole]))

        # Add time in the kwargs entry of the whole system arg_list
        arg_list[self.key_whole]["kwargs"].append("t")

        # Create and fill the output dictionnary containing the datasimulators functions.
        dico_docf = dict.fromkeys(text_def_func.keys(), None)
        for obj_key in dico_docf:
            ldict = locals().copy()
            ldict["getecc_fast"] = getecc_fast
            ldict["getomega_fast"] = getomega_fast
            ldict["gettp_fast"] = gettp_fast
            ldict["pl_rv_array"] = pl_rv_array
            exec(text_def_func[obj_key], ldict)
            dico_docf[obj_key] = DocFunction(function=ldict[function_name.format(object=obj_key)],
                                             arg_list=arg_list[obj_key])
        return dico_docf

    def _create_datasimulator_woinst_LC(self, LD_parcont, supersamp=1, exptime=0.02043402778):
        """Return datasimulator functions that doesn't include any instrument effect.

        A datasimualtor function is created for the whole dataset_database and for each planet
        individually.

        :param TBC LD_parcont: Limb darkening parameter container
        :param int supersamp: Supersampling for the model
        :param float exptime: Exposure time for the model

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

        # Initialise the template function text
        function_name = "LCsim_{{object}}_woinst"
        template_function = """
        def {function_name}(p, t):
        {{tab}}{{preambule}}
        {{tab}}return 1 {{planets_lc}}
        """.format(function_name=function_name)
        tab = "    "
        template_function = dedent(template_function)

        # Initialise arg_list and param_nb for key "whole"
        arg_list[self.key_whole] = OrderedDict()
        arg_list[self.key_whole]["param"] = []
        arg_list[self.key_whole]["kwargs"] = []
        param_nb[self.key_whole] = 0

        # Create the template preambule
        if self.transit_model == "batman":
            template_preambule = """
            {tab}ecc_{planet} = getecc_fast({secosw}, {sesinw})
            {tab}omega_{planet} = degrees(getomega_fast({secosw}, {sesinw}))
            {tab}inc_{planet} = degrees(acos({cosinc}))
            {tab}params_{planet}.t0 = {tc}
            {tab}params_{planet}.per = {P}
            {tab}params_{planet}.rp = {Rrat}
            {tab}params_{planet}.a = {aR}
            {tab}params_{planet}.inc = inc_{planet}
            {tab}params_{planet}.ecc = ecc_{planet}
            {tab}params_{planet}.w = omega_{planet}
            {tab}params_{planet}.limb_dark = '{ld_mod_name}'
            {tab}params_{planet}.u = {ld_param_list}
            """
        else:
            template_preambule = """
            {tab}ecc_{planet} = getecc_fast({secosw}, {sesinw})
            {tab}omega_{planet} = getomega_fast({secosw}, {sesinw})
            {tab}inc_{planet} = acos({cosinc})
            """
        template_preambule = dedent(template_preambule)

        # Add the initialisation of the TransitModel to the template
        if supersamp > 1:
            if self.transit_model == "batman":
                template_preambule += ("{{tab}}m_{{planet}} = TransitModel(params_{{planet}}, t, "
                                       "supersample_factor={supersamp}, exp_time={exptime})\n"
                                       "".format(supersamp=supersamp, exptime=exptime))
            else:
                m_pytransit = MandelAgol(supersampling=supersamp, exptime=exptime,
                                         model=LD_parcont.ld_type)
        else:
            if self.transit_model == "batman":
                template_preambule += ("{tab}m_{planet} = TransitModel(params_{planet}, t)\n")
            else:
                m_pytransit = MandelAgol(model=LD_parcont.ld_type)

        # Create the ld_param_list
        ld_param_list = "["
        for param in LD_parcont.get_list_params(main=True):
            if param.free:
                ld_param_list += "p[{}], ".format(param_nb[self.key_whole])
                param_nb[self.key_whole] += 1
                arg_list[self.key_whole]["param"].append(param.full_name)
            else:
                ld_param_list += "{}, ".format(param.value)
        ld_param_list += "]"

        # Create the text for template_planet_lc
        if self.transit_model == "batman":
            template_planet_lc = ("+ m_{planet}.light_curve(params_{planet}) - 1 ")
        else:
            template_planet_lc = ("+ m.evaluate(t, {Rrat}, {ld_param_list}, {tc}, {P}, {aR}, "
                                  "inc_{planet}, ecc_{planet}, omega_{planet}) - 1 ")

        # Save the param_nb and arg_list for the whole function before iterating over the planets
        # text_def_func_before = text_def_func[self.key_whole]
        param_nb_before = param_nb[self.key_whole]
        arg_list_before = deepcopy(arg_list[self.key_whole])

        # Initialise the local dictionary for the creation of the datasim functions by exec
        ldict = locals().copy()

        # Initialise the text for the whole system preambule
        preambule_whole = ""
        whole_planets_lc = ""
        for i, planet in enumerate(self.planets.values()):
            # Initialise arg_list and param_nb for the current planet
            arg_list[planet.name] = deepcopy(arg_list_before)
            param_nb[planet.name] = param_nb_before

            # Create the params_planet object
            ldict["params_{planet}".format(planet=planet.name)] = TransitParams()

            # Create two dictionaries which will contain the text for each planet parameter for the
            # current planet and for the whole system.
            params_planet = {}
            params_whole = {}
            # Create the text for each planet parameter for the current planet and for the whole
            # system.
            for param_name, param in zip(["secosw", "sesinw", "cosinc", "tc", "P", "Rrat", "aR"],
                                         [planet.secosw, planet.sesinw, planet.cosinc, planet.tc,
                                          planet.P, planet.Rrat, planet.aR]):
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
            if self.transit_model == "batman":
                preambule_planet = (template_preambule.
                                    format(planet=planet.name, secosw=params_planet["secosw"],
                                           sesinw=params_planet["sesinw"], tc=params_planet["tc"],
                                           cosinc=params_planet["cosinc"], P=params_planet["P"],
                                           Rrat=params_planet["Rrat"], aR=params_planet["aR"],
                                           ld_mod_name=LD_parcont.ld_type,
                                           ld_param_list=ld_param_list, tab=tab))
                preambule_whole += (template_preambule.
                                    format(planet=planet.name, secosw=params_whole["secosw"],
                                           sesinw=params_whole["sesinw"], tc=params_whole["tc"],
                                           cosinc=params_whole["cosinc"], P=params_whole["P"],
                                           Rrat=params_whole["Rrat"], aR=params_whole["aR"],
                                           ld_mod_name=LD_parcont.ld_type,
                                           ld_param_list=ld_param_list, tab=tab))
            else:
                preambule_planet = (template_preambule.
                                    format(planet=planet.name, secosw=params_planet["secosw"],
                                           sesinw=params_planet["sesinw"],
                                           cosinc=params_planet["cosinc"], tab=tab))
                preambule_whole += (template_preambule.
                                    format(planet=planet.name, secosw=params_whole["secosw"],
                                           sesinw=params_whole["sesinw"],
                                           cosinc=params_whole["cosinc"], tab=tab))

            # planets LC contribution (planet_lc and whole_planets_lc)
            if self.transit_model == "batman":
                planet_lc = template_planet_lc.format(planet=planet.name)
                whole_planets_lc += template_planet_lc.format(planet=planet.name)
            else:
                planet_lc = template_planet_lc.format(planet=planet.name, aR=params_planet["aR"],
                                                      Rrat=params_planet["Rrat"],
                                                      tc=params_planet["tc"], P=params_planet["P"],
                                                      ld_param_list=ld_param_list)
                whole_planets_lc += template_planet_lc.format(planet=planet.name,
                                                              aR=params_whole["aR"],
                                                              Rrat=params_whole["Rrat"],
                                                              tc=params_whole["tc"],
                                                              P=params_whole["P"],
                                                              ld_param_list=ld_param_list)

            # Finalise the  text of planet LC simulator function
            text_def_func[planet.name] = (template_function.
                                          format(object=planet.name, preambule=preambule_planet,
                                                 planets_lc=planet_lc, tab=tab))
            logger.debug("text of {object} LC simulator function wo inst:\n{text_func}"
                         "".format(object=planet.name, text_func=text_def_func[planet.name]))

            # Add time in the kwargs entry of the planet arg_list
            arg_list[planet.name]["kwargs"].append("t")

        # Finalise the  text of whole system RV simulator function
        text_def_func[self.key_whole] = (template_function.
                                         format(object=self.key_whole, preambule=preambule_whole,
                                                planets_lc=whole_planets_lc, tab=tab))
        logger.debug("text of {object} LC simulator function wo inst:\n{text_func}"
                     "".format(object=self.key_whole, text_func=text_def_func[self.key_whole]))

        # Add time in the kwargs entry of the whole system arg_list
        arg_list[self.key_whole]["kwargs"].append("t")

        # Create and fill the output dictionnary containing the datasimulators functions.
        dico_docf = dict.fromkeys(text_def_func.keys(), None)
        for obj_key in dico_docf:
            ldict["getecc_fast"] = getecc_fast
            ldict["getomega_fast"] = getomega_fast
            ldict["acos"] = acos
            ldict["degrees"] = degrees
            if self.transit_model == "batman":
                ldict["TransitModel"] = TransitModel
            else:
                ldict["m"] = m_pytransit
            exec(text_def_func[obj_key], ldict)
            dico_docf[obj_key] = DocFunction(function=ldict[function_name.format(object=obj_key)],
                                             arg_list=arg_list[obj_key])
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
