#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
LC_instcat_model module.

The objective of this package is to provides the LC_InstCat_Model class to handle the LC instrument class
for the GravGroup class

@DONE:
    -

@TODO:
    - self.stars is used here but it's only define in GravGroup that makes the code a bit difficult to
    understand and follow. Is there a solution ? same thing for self.paramfile4instcat and self._ext_plonly
"""
from logging import getLogger
from textwrap import dedent
from collections import OrderedDict
from pprint import pformat

from .supersamp_exptime import SuperSampExpTimeAttr, _supersamp_key, _exptime_key
from .limb_darkening import Manager_LD, CoreLD
from .datasim_creator_lc import create_datasimulator_LC
from ..decorrelation.linear_decorrelation import LinearDecorrelation
from ...likelihood.decorrelation.spline_decorrelation import SplineDecorrelation
from ...likelihood.decorrelation.bispline_decorrelation import BiSplineDecorrelation
from ...dataset_and_instrument.lc import LC_inst_cat
from ....core.dataset_and_instrument.manager_dataset_instrument import Manager_Inst_Dataset
from ....core.model.core_instcat_model import Core_InstCat_Model
from ....core.model.polynomial_model import set_dico_config, get_dico_config
from ....core.parameter import Parameter
from .....tools.miscellaneous import spacestring_like


## Logger object
logger = getLogger()

mgr_LD = Manager_LD()
mgr_inst_dst = Manager_Inst_Dataset()
mgr_inst_dst.load_setup()


class LC_InstCat_Model(Core_InstCat_Model, SuperSampExpTimeAttr):
    """docstring for LC_InstCat_Model, interface class of GravGroup."""

    # Mandatory attributes for a sublass of Core_InstCat_Model
    __inst_cat__ = LC_inst_cat
    __has_instcat_paramfile__ = True
    __default_paramfile_name__ = "LC_param_file.py"
    __datasim_creator_name__ = "sim_LC"
    __l_decorrelation_class__ = [LinearDecorrelation, SplineDecorrelation, BiSplineDecorrelation]

    allowed_what2decorrelate_strs = ['multiply_2_totalflux', 'add_2_totalflux', ]

    ## List of available transit models, the 1st element is used as default
    _transit_models = ["batman", "pytransit"]  # ["batman", "pytransit-MandelAgol", "pytransit-Gimenez"] Temporarily? remove pytransit from the available transit_models

    ## List of available phase curve models, the 1st element is used as default
    _phasecurve_models = ["spiderman", "kelp", "sincos"]

    ## List of available occultation models, the 1st element is used as default
    _occultation_models = ["batman", ]  # ["spiderman", ]

    ## List of available limb-darkening models for each lc_models, the 1st element is used as
    ## default
    _ld_models = {"batman": ["quadratic", "nonlinear", "exponential", "logarithmic", "squareroot",
                             "linear", "uniform", "custom"],
                  "pytransit": ["quadratic", "linear", "uniform"],
                  }

    # Strings used in the inst_cat param_file
    __ld_dict_name = "LDs"
    __ldmod_dict_name = "LD_models"

    __supersamp_dict = "SuperSamps"

    def __init__(self, model_instance):
        super(LC_InstCat_Model, self).__init__(model_instance=model_instance)
        defaultmodel4instrument_dict = {instmod_obj.full_name: '' for instmod_obj in self.model_instance.get_instmodel_objs(inst_fullcat=self.__inst_cat__)}
        defaultlistmodel4instrument_dict = {instmod_obj.full_name: ['', ] for instmod_obj in self.model_instance.get_instmodel_objs(inst_fullcat=self.__inst_cat__)}
        self.transit_model = {planet.get_name(): {"do": True,
                                                  "model4instrument": defaultmodel4instrument_dict.copy(),
                                                  "model_definitions": {'': {"model": "batman", 'orbital_model': '', 'new_parameter': {'Rrat': True}, }, },
                                                  }
                              for planet in self.model_instance.planets.values()
                              }
        self.phasecurve_model = {planet.get_name(): {"do": False,
                                                     "model4instrument": defaultlistmodel4instrument_dict.copy(),
                                                     "model_definitions": {'': {"model": "sincos",
                                                                                "args": {'sincos': 'cos',
                                                                                         'factor_period': 1,
                                                                                         'flux_offset': 'param',
                                                                                         'phase_offset': 'param',
                                                                                         'occultation': True
                                                                                         },
                                                                                'orbital_model': '',
                                                                                'new_parameter': {'amp': True, 'flux_offset': True, 'phase_offset': True},
                                                                                },
                                                                           },
                                                     }
                                 for planet in self.model_instance.planets.values()
                                 }
        self.occultation_model = {planet.get_name(): {"do": False,
                                                      "model4instrument": defaultmodel4instrument_dict.copy(),
                                                      "model_definitions": {'': {"model": "batman", 'orbital_model': '', }, },
                                                      }
                                  for planet in self.model_instance.planets.values()
                                  }
        self.__ldmodel4instmodfname = OrderedDict()  # Limb darkening model for each instrument
        SuperSampExpTimeAttr.__init__(self)
        # Set the dictionaries for the polynomial models
        for star in self.model_instance.stars.values():
            star.set_dico_config_polymodel(inst_cat=self.inst_cat, dico_config={'do': False})
        for instmod_obj in self.model_instance.get_instmodel_objs(inst_fullcat=self.__inst_cat__):
            instmod_obj.set_dico_config_polymodel(dico_config={'do': True})  # Defined in lisa.posterior.exoplanet.dataset_and_instrument.rv.Instrument_RV and accessed through lisa.posterior.core.dataset_and_instrument.instrument.Instrument_Model.__getattr__

    @property
    def ldmodel4instmodfname(self):
        """Return the dictionary giving the LD object to use for each LC instrument model."""
        return self.__ldmodel4instmodfname

    @property
    def LDs(self):
        return self.model_instance.paramcontainers[CoreLD.category]

    def _init_decorrelation_model_config(self):
        # Get list of inst model full name for the inst cat
        l_instcat_instmod = self.model_instance.get_instmodel_objs(inst_fullcat=self.__inst_cat__)
        for inst_mod_obj in l_instcat_instmod:
            self.decorrelation_model_config[inst_mod_obj.full_name] = {"do": False, "what to decorrelate": {}}
            for model_part in self.allowed_what2decorrelate_strs:
                self.decorrelation_model_config[inst_mod_obj.full_name]["what to decorrelate"][model_part] = {}
                for decorr_model_cat in self.l_decorrelation_model_category:
                    self.decorrelation_model_config[inst_mod_obj.full_name]["what to decorrelate"][model_part][decorr_model_cat] = {}

    def datasim_creator(self, inst_models, datasets, get_times_from_datasets):
        """
        Arguments
        ---------
        inst_models : List of Instrument_Model instances
            List of intrument models corresponding to each datasets in datasets
        datasets    : List of IND_Dataset instances
            List of datasets
        get_times_from_datasets  : bool
            If True the times at which the LC model is computed is taken from the datasets.
            Else it is an input of the datasimulator function produced.
        """
        return create_datasimulator_LC(star=list(self.model_instance.stars.values())[0],
                                       planets=self.model_instance.planets,
                                       parametrisation=self.model_instance.parametrisation,
                                       ldmodel4instmodfname=self.ldmodel4instmodfname,
                                       LDs=self.LDs,
                                       transit_model=self.transit_model,
                                       SSE4instmodfname=self.SSE4instmodfname,
                                       phasecurve_model=self.phasecurve_model,
                                       occultation_model=self.occultation_model,
                                       inst_models=inst_models,
                                       datasets=datasets,
                                       get_times_from_datasets=get_times_from_datasets,
                                       dataset_db=self.model_instance.dataset_db,
                                       LCcat_model=self
                                       )

    def create_text_instcat_paramfile_model(self, model_instance):
        """Create text for parameter file for the light-curve parametrisation.

        Arguments
        ---------
        model_instance  :
        """
        text = """
        # Light-curve parametrisation file of {object_name}

        # Which model do you want to use for the transit ?
        transit_model = {transit_model}

        # Limb-darkening.
        # Associate LC instrument models with LD param containers.
        # Available limb-darkening models are:
        # {available_lds}
        {ld_dict_name} = {{{star_ld_dict}
        {tab_ld}}}

        # Supersampling and exposure_time
        {supersamp_dict} = {{{inst_ss_dict}
        {tab_ss}}}

        # Which model do you want to use for the phase curve ?
        phasecurve_model = {phasecurve_model}

        # Which model do you want to use for the occultation ?
        # WARNING: Some phasecurve models already include the occultation. No need to add it twice in these cases.
        occultation_model = {occultation_model}

        # Polynomial trends
        polynomial_model = {poly_models}
        """
        text = dedent(text)  # Remove undesired indentation

        # Create some of the easy content of the file
        available_lds = self._ld_models["batman"]  # For now I am providing the ld models available with batman
        tab_ld = spacestring_like(f"{self.__ld_dict_name} =  ")
        tab_ss = spacestring_like(f"{self.__supersamp_dict} =  ")
        tab_trmod = spacestring_like("transit_model = ")
        tab_pcmod = spacestring_like("phasecurve_model = ")
        tab_occmod = spacestring_like("occultation_model = ")
        tab_poly = spacestring_like("polynomial_model = ")

        # Create the structure of the star_ld_dict
        star_ld_dict = """
        '{star_name}': {{{inst_ld_dict}

        {tab_star_ld}'{LD_dict_name}': {{{LDmodels}}}
        {tab_star_ld}}}
        """
        star_ld_dict = dedent(star_ld_dict)[1:-1]  # Remove undesired indentation

        # Create some of the easy content of the star_ld_dict
        default_parcontname = 'default'
        star = self.model_instance.stars[list(self.model_instance.stars.keys())[0]]
        tab_star_ld = tab_ld + spacestring_like(f"'{star.get_name()}':  ")  # I put an extra space instead of the curly braket because the color algorithm of atom
        LDmodels = (f"'{default_parcontname}': 'quadratic'")

        # Create the content related to LC instruments (inst_ld_dict and inst_ss_dict)
        inst_ld_dict = ""
        inst_ss_dict = ""
        ss_dict = "'{instmod_fullname}': {{'{supersamp_key}': {default_supersamp}, '{exptime_key}': {default_exptime}}},"
        ld_dict = "'{instmod_fullname}': '{def_LDparcont}',"
        default_supersamp = 1
        default_exptime = 0.02043402778  # Kepler long cadence exposure time in days
        first_instmodel = True
        for instmod_obj in self.model_instance.get_instmodel_objs(inst_fullcat=self.__inst_cat__):
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

        # Create the dictionary for the polynomial models
        dico_poly = {}
        for star_name, star in self.model_instance.stars.items():
            dico_poly[star_name] = star.get_dico_config_polymodel(inst_cat=self.inst_cat, notexist_ok=False)
        for instmod_obj in self.model_instance.get_instmodel_objs(inst_fullcat=self.__inst_cat__):
            dico_poly[instmod_obj.full_name] = instmod_obj.get_dico_config_polymodel(notexist_ok=False)

        # Fill the whole text_LC_param string
        text = text.format(object_name=self.model_instance.get_name(),
                           transit_model=pformat(self.transit_model, compact=True).replace("\n", f"\n{tab_trmod}"),
                           available_lds=available_lds,
                           ld_dict_name=self.__ld_dict_name,
                           tab_ld=tab_ld, star_ld_dict=star_ld_dict,
                           supersamp_dict=self.__supersamp_dict,
                           tab_ss=tab_ss, inst_ss_dict=inst_ss_dict,
                           phasecurve_model=pformat(self.phasecurve_model, compact=True).replace("\n", f"\n{tab_pcmod}"),
                           occultation_model=pformat(self.occultation_model, compact=True).replace("\n", f"\n{tab_occmod}"),
                           poly_models=pformat(dico_poly, compact=True).replace("\n", f"\n{tab_poly}")
                           )

        return text

    def load_config(self, dico_config):
        """load the configuration specified by the dictionnary"""
        # Check and load the content of the LDs and Supersamps dict
        for star in self.model_instance.stars.values():
            star = self.model_instance.stars[list(self.model_instance.stars.keys())[0]]
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
        # Check the transit_model, phasecurve_model and occultation_model
        # A big part of structure of these dictionary are the same, we are going to check that
        l_dico_model_name = ["transit_model", "phasecurve_model", "occultation_model"]
        for dict_name in l_dico_model_name:
            if dict_name not in dico_config:
                raise ValueError(f"In file {self.paramfile_instcat}: Missing {dict_name} dictionary.")
            dico_model = dico_config[dict_name]
            for planet in self.model_instance.planets.values():
                planet_name = planet.get_name()
                # Check that there is a key for each planet
                if planet_name not in dico_model:
                    raise ValueError(f"In file {self.paramfile_instcat}: Dictionary {dict_name} is missing a key for planet {planet_name}.")
                # Check that there is a 'do' key with a boolean value for each planet dictionary
                if 'do' not in dico_model[planet_name]:
                    raise ValueError(f"In file {self.paramfile_instcat}: Dictionary {dict_name}[{planet_name}] is missing the 'do' key.")
                else:
                    if not(isinstance(dico_model[planet_name]["do"], bool)):
                        raise ValueError(f"In file {self.paramfile_instcat}: {dict_name}[{planet_name}]['do'] has to be a boolean.")
                if dico_model[planet_name]['do']:
                    # Check that there is a key each planet dictionary
                    for key in ["model_definitions", "model4instrument"]:
                        if key not in dico_model[planet_name]:
                            raise ValueError(f"In file {self.paramfile_instcat}: Dictionary {dict_name}[{planet_name}] is missing the '{key}' key.")
                    # Check that the name of all the LC instruments are all there and associated to an existing model
                    l_model = list(dico_model[planet_name]["model_definitions"].keys())
                    for inst_mod_obj in self.model_instance.get_instmodel_objs(inst_fullcat=self.inst_cat):
                        if inst_mod_obj.full_name not in dico_model[planet_name]["model4instrument"]:
                            raise ValueError(f"In file {self.paramfile_instcat}: Dictionary {dict_name}['{planet_name}']['model4instrument'] is missing the '{inst_mod_obj.full_name}' key.")
                        if dict_name in ["transit_model", "occultation_model"]:
                            if dico_model[planet_name]["model4instrument"][inst_mod_obj.full_name] not in l_model:
                                raise ValueError(f"In file {self.paramfile_instcat}: In {dict_name} for planet {planet_name}, {inst_mod_obj.full_name} is associated to model {dico_model[planet_name]['model4instrument'][inst_mod_obj.full_name]} which is not defined in {dict_name}['{planet_name}']['model_definitions'].")
                        elif dict_name in ["phasecurve_model", ]:
                            for model in dico_model[planet_name]["model4instrument"][inst_mod_obj.full_name]:
                                if model not in l_model:
                                    raise ValueError(f"In file {self.paramfile_instcat}: In {dict_name} for planet {planet_name}, {inst_mod_obj.full_name} is associated to model {model} which is not defined in {dict_name}['{planet_name}']['model_definitions'].")

        # Check and load the transit_model dictionary
        for planet in self.model_instance.planets.values():
            planet_name = planet.get_name()
            if dico_config["transit_model"][planet_name]["do"]:
                for model_comp_name, model_comp_dict in dico_config["transit_model"][planet_name]["model_definitions"].items():
                    l_key_mandatory = ['model', 'orbital_model', 'new_parameter']
                    if not(set(l_key_mandatory) == set(model_comp_dict.keys())):
                        raise ValueError(f"In file {self.paramfile_instcat}: (Planet {planet_name}) the keys of transit_model {model_comp_name} should be {l_key_mandatory}.")
                    if model_comp_dict['orbital_model'] not in self.model_instance.orbital_model[planet_name]['model_definitions'].keys():
                        raise ValueError(f"In file {self.paramfile_instcat}: (Planet {planet_name}, model {model_comp_name}) the provided orbital model {model_comp_dict['orbital_model']} is not an available orbital model. Should be in {list(self.model_instance.orbital_model[planet_name]['model_definitions'].keys())}")
                    if model_comp_dict['model'] not in self._transit_models:
                        raise ValueError(f"In file {self.paramfile_instcat}: (Planet {planet_name}, model {model_comp_name}) {model_comp_dict['model']} is not an available transit model.")
                    l_new_parameter_key = ['Rrat', ]
                    if not(set(l_new_parameter_key) == set(model_comp_dict['new_parameter'].keys())):
                        raise ValueError(f"In file {self.paramfile_instcat}: (Planet {planet_name}, model {model_comp_name}) the keys of the 'new_parameter' dictionary should be {l_new_parameter_key}.")
                    for new_parameter_key in l_new_parameter_key:
                        if (model_comp_dict['new_parameter'][new_parameter_key] is not True) and (model_comp_dict['new_parameter'][new_parameter_key] not in dico_config["transit_model"][planet_name]["model_definitions"]):
                            raise ValueError(f"In file {self.paramfile_instcat}: (Planet {planet_name}, model {model_comp_name}) the value of {new_parameter_key} in the 'new_parameter' dictionary should be True or the name of another model (current model names are {list(dico_config['transit_model'][planet_name]['model_definitions'].keys())}).")
                self.transit_model[planet_name] = dico_config["transit_model"][planet_name]
            else:
                self.transit_model[planet_name]['do'] = False

        # Check and load the phasecurve_model dictionary
        for planet in self.model_instance.planets.values():
            planet_name = planet.get_name()
            if dico_config["phasecurve_model"][planet_name]["do"]:
                for model_comp_name, model_comp_dict in dico_config["phasecurve_model"][planet_name]["model_definitions"].items():
                    l_key_mandatory = ["model", "args", 'orbital_model', 'new_parameter']
                    if not(set(l_key_mandatory) == set(model_comp_dict.keys())):
                        raise ValueError(f"In file {self.paramfile_instcat}: (Planet {planet_name}) the keys of phasecurve_model {model_comp_name} should be {l_key_mandatory}.")
                    if model_comp_dict['orbital_model'] not in self.model_instance.orbital_model[planet_name]['model_definitions'].keys():
                        raise ValueError(f"In file {self.paramfile_instcat}: (Planet {planet_name}, model {model_comp_name}) the provided orbital model {model_comp_dict['orbital_model']} is not an available orbital model. Should be in {list(self.model_instance.orbital_model[planet_name]['model_definitions'].keys())}")
                    if model_comp_dict['model'] not in self._phasecurve_models:
                        raise ValueError(f"In file {self.paramfile_instcat}: (Planet {planet_name}, model {model_comp_name}) {model_comp_dict['model']} is not an available phasecurve model.")
                    if model_comp_dict['model'] == "spiderman":
                        l_arg_mand_sp = ["ModelParams_kwargs", "attributes", "lightcurve_kwargs"]
                        if not(set(l_arg_mand_sp) == set(model_comp_dict['args'].keys())):
                            raise ValueError(f"In file {self.paramfile_instcat}: (Planet {planet_name}) the keys of phasecurve_model {model_comp_name}['args'] should be {l_arg_mand_sp}.")
                        if not("brightness_model" in model_comp_dict['args']['ModelParams_kwargs']):
                            raise ValueError(f"In file {self.paramfile_instcat}: (Planet {planet_name}) the keys of phasecurve_model {model_comp_name}['args']['ModelParams_kwargs'] is missing the 'brightness_model' key")
                        if model_comp_dict['args']['ModelParams_kwargs']['brightness_model'] == 'zhang':
                            l_new_parameter_key = ['Rrat', 'a', 'u1', 'u2', 'x1', 'Tn', 'deltaT']
                        else:
                            l_new_parameter_key = []
                    elif model_comp_dict['model'] == "kelp":
                        l_arg_mand_sp = ["Model_kwargs", "brightness_model", "brightness_model_kwargs"]
                        if not(set(l_arg_mand_sp) == set(model_comp_dict['args'].keys())):
                            raise ValueError(f"In file {self.paramfile_instcat}: (Planet {planet_name}) the keys of phasecurve_model {model_comp_name}['args'] should be {l_arg_mand_sp}.")
                        if model_comp_dict['args']['brightness_model'] == 'thermal':
                            l_new_parameter_key = ['Rrat', 'f', 'hotspotoffset', 'alpha', 'omegadrag', 'AB', 'c11']
                        else:
                            l_new_parameter_key = []
                    elif model_comp_dict['model'] == "sincos":
                        l_arg_mand_sp = ["sincos", "factor_period", "flux_offset", 'phase_offset', 'occultation']
                        if not(set(l_arg_mand_sp) == set(model_comp_dict['args'].keys())):
                            raise ValueError(f"In file {self.paramfile_instcat}: (Planet {planet_name}) the keys of phasecurve_model {model_comp_name}['args'] should be {l_arg_mand_sp}.")
                        if not(model_comp_dict['args']["sincos"] in [None, 'sin', 'cos']):
                            raise ValueError(f"In file {self.paramfile_instcat}: (Planet {planet_name}) phasecurve_model {model_comp_name}['args'], 'sincos' should be in [None, 'sin', 'cos'].")
                        if not(isinstance(model_comp_dict['args']["factor_period"], float) or isinstance(model_comp_dict['args']["factor_period"], int)):
                            raise ValueError(f"In file {self.paramfile_instcat}: (Planet {planet_name}) phasecurve_model {model_comp_name}['args'], 'factor_period' should be a float or an int.")
                        if not(model_comp_dict['args']["flux_offset"] in ['zero', 'semi-amplitude', 'param']):
                            raise ValueError(f"In file {self.paramfile_instcat}: (Planet {planet_name}) phasecurve_model {model_comp_name}['args'], 'average' should be in ['zero', 'semi-amplitude'].")
                        if not(isinstance(model_comp_dict['args']["phase_offset"], float) or isinstance(model_comp_dict['args']["phase_offset"], int) or (model_comp_dict['args']["phase_offset"] == 'param')):
                            raise ValueError(f"In file {self.paramfile_instcat}: (Planet {planet_name}) phasecurve_model {model_comp_name}['args'], 'phase_offset' should be a float or an int or be equal to 'param'.")
                        if not(isinstance(model_comp_dict['args']["occultation"], bool)):
                            raise ValueError(f"In file {self.paramfile_instcat}: (Planet {planet_name}) phasecurve_model {model_comp_name}['args'], 'occultation' should be a boolean.")
                        if model_comp_dict['args']['sincos'] is None:
                            l_new_parameter_key = []
                        else:
                            l_new_parameter_key = ['amp', 'flux_offset', 'phase_offset']
                    else:
                        logger.warning(f"Checking the content of the phasecurve dictionary for the phasecurve model {model_comp_dict['model']} is not implemented.")
                    if not(set(l_new_parameter_key) == set(model_comp_dict['new_parameter'].keys())):
                        raise ValueError(f"In file {self.paramfile_instcat}: (Planet {planet_name}, model {model_comp_name}) the keys of the 'new_parameter' dictionary should be {l_new_parameter_key}.")
                    for new_parameter_key in l_new_parameter_key:
                        if (model_comp_dict['new_parameter'][new_parameter_key] is not True) and (model_comp_dict['new_parameter'][new_parameter_key] not in dico_config["phasecurve_model"][planet_name]["model_definitions"]):
                            raise ValueError(f"In file {self.paramfile_instcat}: (Planet {planet_name}, model {model_comp_name}) the value of {new_parameter_key} in the 'new_parameter' dictionary should be True or the name of another model (current model names are {list(dico_config['phasecurve_model'][planet_name]['model_definitions'].keys())}).")
                self.phasecurve_model[planet_name] = dico_config["phasecurve_model"][planet_name]
            else:
                self.phasecurve_model[planet_name]['do'] = False

        # Check and load the occultation_model dictionary
        for planet in self.model_instance.planets.values():
            planet_name = planet.get_name()
            if dico_config["occultation_model"][planet_name]["do"]:
                for model_comp_name, model_comp_dict in dico_config["occultation_model"][planet_name]["model_definitions"].items():
                    l_key_mandatory = ["model", 'orbital_model']
                    if not(set(l_key_mandatory) == set(model_comp_dict.keys())):
                        raise ValueError(f"In file {self.paramfile_instcat}: (Planet {planet_name}) the keys of occultation_model {model_comp_name} should be {l_key_mandatory}.")
                    if model_comp_dict['orbital_model'] not in self.model_instance.orbital_model[planet_name]['model_definitions'].keys():
                        raise ValueError(f"In file {self.paramfile_instcat}: (Planet {planet_name}, model {model_comp_name}) the provided orbital model {model_comp_dict['orbital_model']} is not an available orbital model. Should be in {list(self.model_instance.orbital_model[planet_name]['model_definitions'].keys())}")
                    if model_comp_dict['model'] not in self._occultation_models:
                        raise ValueError(f"In file {self.paramfile_instcat}: (Planet {planet_name}, model {model_comp_name}) {model_comp_dict['model']} is not an available phasecurve model.")
                    l_new_parameter_key = ['Frat', 'Rrat']
                    if not(set(l_new_parameter_key) == set(model_comp_dict['new_parameter'].keys())):
                        raise ValueError(f"In file {self.paramfile_instcat}: (Planet {planet_name}, model {model_comp_name}) the keys of the 'new_parameter' dictionary should be {l_new_parameter_key}.")
                    for new_parameter_key in l_new_parameter_key:
                        if (model_comp_dict['new_parameter'][new_parameter_key] is not True) and (model_comp_dict['new_parameter'][new_parameter_key] not in dico_config["occultation_model"][planet_name]["model_definitions"]):
                            raise ValueError(f"In file {self.paramfile_instcat}: (Planet {planet_name}, model {model_comp_name}) the value of {new_parameter_key} in the 'new_parameter' dictionary should be True or the name of another model (current model names are {list(dico_config['occultation_model'][planet_name]['model_definitions'].keys())}).")
                self.occultation_model[planet_name] = dico_config["occultation_model"][planet_name]
            else:
                self.occultation_model[planet_name]['do'] = False

        # Check and load the polynomial models
        if "polynomial_model" in dico_config:
            for star_name, star in self.model_instance.stars.items():
                if star_name in dico_config["polynomial_model"]:
                    star.set_dico_config_polymodel(inst_cat=self.inst_cat, dico_config=dico_config["polynomial_model"][star_name])
            for instmod_obj in self.model_instance.get_instmodel_objs(inst_fullcat=self.__inst_cat__):
                if instmod_obj.full_name in dico_config["polynomial_model"]:
                    instmod_obj.set_dico_config_polymodel(dico_config=dico_config["polynomial_model"][instmod_obj.full_name])

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
        if self.model_instance.isavailable_paramcontainer(LD.store_name, category="LD"):
            raise ValueError("Names provided already exists ({}). LD cannot be added".format(LD.store_name))
        else:
            self.model_instance.add_a_paramcontainer(LD)

    def get_list_LD_parconts(self):
        return self.model_instance.paramcontainers[CoreLD.category].values()

    def load_config_decorrelation_model(self, dico_config):
        """Load the dict in any inst_cat specific param_file about to choosen the decorrelation models
        for each dataset.

        This function should be used in load_instcat_paramfile to load the configuration of the decorrelation
        models.

        Arguments
        ---------
        dico_config : dict
            Dictionary which contain the content of the inst_cat specific param_file
        """
        for instmod_obj_name, decorr_dict_instmod in dico_config.get(self._decorr_model_dict_name, {}).items():
            instmod_name_info = mgr_inst_dst.interpret_instmod_fullname(instmod_fullname=instmod_obj_name, raise_error=True)
            instmod_obj = self.model_instance.get_instmodel_objs(inst_fullcat=instmod_name_info["inst_fullcategory"],
                                                                 inst_model=instmod_name_info["inst_model"],
                                                                 inst_name=instmod_name_info["inst_name"])[0]
            # Check that the dictionary of each instrument model object has a "do" key
            assert "do" in decorr_dict_instmod.keys()
            if instmod_obj_name not in self.decorrelation_model_config:
                self.decorrelation_model_config[instmod_obj_name] = {}
            self.decorrelation_model_config[instmod_obj_name]["do"] = decorr_dict_instmod["do"]
            # Check that the "what to decorrelate" is in the dictionary
            if "what to decorrelate" not in decorr_dict_instmod:
                raise ValueError(f"The dictionary for the configuration of the linear decorrelation of {instmod_obj_name}"
                                 f" must include the key 'what to decorrelate'.")
            if 'what to decorrelate' not in self.decorrelation_model_config[instmod_obj_name]:
                self.decorrelation_model_config[instmod_obj_name]['what to decorrelate'] = {}
            for model_part, decorr_dict_instmod_modpart in decorr_dict_instmod['what to decorrelate'].items():
                # Check that the "what to decorrelate" value is valid
                if model_part not in self.allowed_what2decorrelate_strs:
                    raise ValueError(f"Keys of 'what to decorrelate' for the configuration of the {instmod_obj_name}"
                                     f" must be in {self.allowed_what2decorrelate_strs}.")
                if model_part not in self.decorrelation_model_config[instmod_obj_name]['what to decorrelate']:
                    self.decorrelation_model_config[instmod_obj_name]['what to decorrelate'][model_part] = {}
                for decorr_mod in self.l_decorrelation_model_class:
                    # Check that the dictionary of each instrument model object has a key for each decorrelation models
                    assert decorr_mod.category in decorr_dict_instmod_modpart.keys()
                    decorr_dict_instmod_modpart_decorrmod = decorr_dict_instmod_modpart[decorr_mod.category]
                    if decorr_mod.category not in self.decorrelation_model_config[instmod_obj_name]['what to decorrelate']:
                        self.decorrelation_model_config[instmod_obj_name]['what to decorrelate'][model_part][decorr_mod.category] = {}
                    decorr_mod.load_text_decorr_paramfile(inst_mod_obj=instmod_obj,
                                                          decorrelation_config_inst_decorr_paramfile=decorr_dict_instmod_modpart_decorrmod,
                                                          decorrelation_config_inst_decorr=self.decorrelation_model_config[instmod_obj_name]['what to decorrelate'][model_part][decorr_mod.category],
                                                          )

    def require_model_decorrelation(self, instmod_fullname):
        """True if any of the instrument models of the instrument category require model decorrelation

        Argument
        --------
        instmod_fullname    : str
            Intrument model full name

        Return
        ------
        require : bool
            True if the instrument model requires model decorelation
        """
        require = False
        if self.do_decorrelate_model_instmod(instmod_fullname=instmod_fullname):
            for model_part, dico_decor_model_part_config in self.decorrelation_model_config[instmod_fullname]['what to decorrelate'].items():
                for decor_cat, dico_decor_cat_config in dico_decor_model_part_config.items():
                    if len(dico_decor_cat_config) > 0:
                        require = True
                        break
        return require

    def apply_parametrisation(self, parametrisation, **kwargs):
        """Apply the parametrisation for the instrument category

        This method is called by Core_Parametrisation.apply_instcat_parameterisation
        """
        # Apply the parametrisation to the star and planets parameters
        self.apply_star_planet_parametrisation(parametrisation=parametrisation)

        # Apply the parametrisation to the instrument models parameters
        self.apply_instmodel_parametrisation(parametrisation=parametrisation)

        # If needed apply the limbdarkening coefficient parametrisation
        self.apply_limbdarkening_parametrisation(parametrisation=parametrisation)

    def apply_star_planet_parametrisation(self, parametrisation):
        """Apply the parametrisation to the star and planet objects.
        """
        ##################################################
        # Apply the parametrisation to the star parameters
        ##################################################
        # Stellar flux polynomial_model
        for star in self.model_instance.paramcontainers["stars"].values():
            star.apply_polymodel_parametrisation(inst_cat=LC_inst_cat)

        host_star = list(self.model_instance.paramcontainers["stars"].values())[0]

        # Apply the parametrisation to the planets parameters and star parameters triggerd by the transit, phase curve or ocultation models
        for planet in self.model_instance.planets.values():
            planet_name = planet.get_name()
            # Transit_model
            if self.transit_model[planet_name]['do']:
                if parametrisation == "Multis":
                    host_star.rho.main = True
                    host_star.rho.unit = "Solar density"
                l_orb_param_basename = ['P', 'tic', 'cosinc', 'ecosw', 'esinw']
                l_orb_new_param_key = ['P', 'tic', 'inc', 'ecc_and_omega', 'ecc_and_omega']
                l_orb_param_unit = ['time unit of LC/RV datasets', 'time unit of LC/RV datasets', 'w/o unit', 'w/o unit', 'w/o unit', ]
                if parametrisation == "EXOFAST":
                    l_orb_param_basename += ['aR']
                    l_orb_new_param_key += ['aR']
                    l_orb_param_unit += ['w/o unit']
                l_mod_comp_name = list(set(self.transit_model[planet_name]["model4instrument"].values()))
                l_tr_param_basename = ['Rrat', ]
                l_tr_new_param_key = ['Rrat', ]
                l_tr_param_unit = ['w/o unit', ]
                for mod_comp_name in l_mod_comp_name:
                    dico_config_tr_mod_comp = self.transit_model[planet_name]['model_definitions'][mod_comp_name]
                    orb_model_name = dico_config_tr_mod_comp['orbital_model']
                    dico_config_orb_mod_comp = self.model_instance.orbital_model[planet_name]['model_definitions'][orb_model_name]
                    for (l_param_basename, l_new_param_key, l_param_unit, dico_config_mod, mod_name
                         ) in zip([l_tr_param_basename, l_orb_param_basename],
                                  [l_tr_new_param_key, l_orb_new_param_key],
                                  [l_tr_param_unit, l_orb_param_unit],
                                  [dico_config_tr_mod_comp, dico_config_orb_mod_comp],
                                  [mod_comp_name, orb_model_name]
                                  ):
                        for param_basename, new_param_key, param_unit in zip(l_param_basename, l_new_param_key, l_param_unit):
                            if (new_param_key is None) or (dico_config_mod['new_parameter'][new_param_key] is True):
                                param_name = f"{param_basename}{mod_name}"
                            else:
                                param_name = f"{param_basename}{dico_config_mod['new_parameter'][new_param_key]}"
                            if planet.has_parameter(name=param_name, return_error=False, kwargs_get_list_params=None, kwargs_get_name={'recursive': False, 'include_prefix': False}):
                                param = planet.parameters[param_name]
                            else:
                                param = Parameter(name=param_name, name_prefix=planet.name, unit=param_unit)
                                planet.add_parameter(param)
                            param.main = True

            # Phase curve model
            if self.phasecurve_model[planet_name]['do']:
                l_mod_comp_name = []
                for l_mod_comp_name_instmod in self.phasecurve_model[planet_name]["model4instrument"].values():
                    l_mod_comp_name += l_mod_comp_name_instmod
                l_mod_comp_name = list(set(l_mod_comp_name))
                for mod_comp_name in l_mod_comp_name:
                    dico_config_pc_mod_comp = self.phasecurve_model[planet_name]['model_definitions'][mod_comp_name]
                    orb_model_name = dico_config_pc_mod_comp['orbital_model']
                    dico_config_orb_mod_comp = self.model_instance.orbital_model[planet_name]['model_definitions'][orb_model_name]
                    if self.phasecurve_model[planet_name]["model_definitions"][mod_comp_name]["model"] == 'spiderman':
                        if parametrisation == "Multis":
                            host_star.rho.main = True
                            host_star.rho.unit = "Solar density"
                        if self.phasecurve_model[planet_name]["model_definitions"][mod_comp_name]['args']['ModelParams_kwargs']['brightness_model'] == 'zhang':
                            host_star.Teff.main = True
                            l_orb_param_basename = ['P', 'tic', 'cosinc', 'ecosw', 'esinw']
                            l_orb_new_param_key = ['P', 'tic', 'inc', 'ecc_and_omega', 'ecc_and_omega']
                            l_orb_param_unit = ['time unit of LC/RV datasets', 'time unit of LC/RV datasets', 'w/o unit', 'w/o unit', 'w/o unit', ]
                            if parametrisation == "EXOFAST":
                                l_orb_param_basename += ['aR']
                                l_orb_new_param_key += ['aR']
                                l_orb_param_unit += ['w/o unit']
                            l_pc_param_basename = ['Rrat', 'a', 'u1', 'u2', 'x1', 'Tn', 'deltaT']
                            l_pc_new_param_key = ['Rrat', 'a', 'u1', 'u2', 'x1', 'Tn', 'deltaT']
                            l_pc_param_unit = ['w/o unit', 'AU', 'w/o unit', 'w/o unit', 'w/o unit', 'K', 'K']
                        else:
                            raise NotImplementedError()
                    elif self.phasecurve_model[planet_name]["model_definitions"][mod_comp_name]["model"] == 'kelp':
                        if parametrisation == "Multis":
                            host_star.rho.main = True
                            host_star.rho.unit = "Solar density"
                        l_orb_param_basename = ['P', 'tic']
                        l_orb_new_param_key = ['P', 'tic']
                        l_orb_param_unit = ['time unit of LC/RV datasets', 'time unit of LC/RV datasets']
                        if parametrisation == "EXOFAST":
                            l_orb_param_basename += ['aR']
                            l_orb_new_param_key += ['aR']
                            l_orb_param_unit += ['w/o unit']
                        if self.phasecurve_model[planet_name]["model_definitions"][mod_comp_name]['args']['brightness_model'] == 'thermal':
                            host_star.Teff.main = True
                            l_pc_param_basename = ['Rrat', 'f', 'hotspotoffset', 'alpha', 'omegadrag', 'AB', 'c11']
                            l_pc_new_param_key = ['Rrat', 'f', 'hotspotoffset', 'alpha', 'omegadrag', 'AB', 'c11']
                            l_pc_param_unit = ['w/o unit', 'w/o unit', 'radians', 'w/o unit', 'w/o unit', 'w/o unit', 'w/o unit']
                        else:
                            raise NotImplementedError()
                    elif self.phasecurve_model[planet_name]["model_definitions"][mod_comp_name]["model"] == 'sincos':
                        l_orb_param_basename = ['P', 'tic']
                        l_orb_new_param_key = ['P', 'tic']
                        l_orb_param_unit = ['time unit of LC/RV datasets', 'time unit of LC/RV datasets']
                        if self.phasecurve_model[planet_name]["model_definitions"][mod_comp_name]['args']['sincos'] is None:
                            l_pc_param_basename = ['C']
                            l_pc_new_param_key = [None]
                            l_pc_param_unit = ['unit of LC data']
                        else:
                            l_pc_param_basename = ['A', 'Phi', 'Foffset']
                            l_pc_new_param_key = ['amp', 'phase_offset', 'flux_offset']
                            l_pc_param_unit = ['unit of LC data', 'radians', 'unit of LC data']
                    else:
                        raise NotImplementedError()
                    for (l_param_basename, l_new_param_key, l_param_unit, dico_config_mod, mod_name
                         ) in zip([l_pc_param_basename, l_orb_param_basename],
                                  [l_pc_new_param_key, l_orb_new_param_key],
                                  [l_pc_param_unit, l_orb_param_unit],
                                  [dico_config_pc_mod_comp, dico_config_orb_mod_comp],
                                  [mod_comp_name, orb_model_name]
                                  ):
                        for param_basename, new_param_key, param_unit in zip(l_param_basename, l_new_param_key, l_param_unit):
                            if (new_param_key is None) or (dico_config_mod['new_parameter'][new_param_key] is True):
                                param_name = f"{param_basename}{mod_name}"
                            else:
                                param_name = f"{param_basename}{dico_config_mod['new_parameter'][new_param_key]}"
                            if planet.has_parameter(name=param_name, return_error=False, kwargs_get_list_params=None, kwargs_get_name={'recursive': False, 'include_prefix': False}):
                                param = planet.parameters[param_name]
                            else:
                                param = Parameter(name=param_name, name_prefix=planet.name, unit=param_unit)
                                planet.add_parameter(param)
                            param.main = True
            # Occultation model
            if self.occultation_model[planet_name]['do']:
                for mod_comp_name in l_mod_comp_name:
                    dico_config_occ_mod_comp = self.occultation_model[planet_name]['model_definitions'][mod_comp_name]
                    orb_model_name = dico_config_occ_mod_comp['orbital_model']
                    dico_config_orb_mod_comp = self.model_instance.orbital_model[planet_name]['model_definitions'][orb_model_name]
                    l_orb_param_basename = ['P', 'tic', 'cosinc', 'ecosw', 'esinw']
                    l_orb_new_param_key = ['P', 'tic', 'inc', 'ecc_and_omega', 'ecc_and_omega']
                    l_orb_param_unit = ['time unit of LC/RV datasets', 'time unit of LC/RV datasets', 'w/o unit', 'w/o unit', 'w/o unit', ]
                    if parametrisation == "Multis":
                        host_star.rho.main = True
                        host_star.rho.unit = "Solar density"
                    l_mod_comp_name = list(set(self.occultation_model[planet_name]["model4instrument"].values()))
                    l_occ_param_basename = ['Frat', 'Rrat']
                    l_occ_new_param_key = ['Frat', 'Rrat']
                    l_occ_param_unit = ['w/o unit', 'w/o unit']
                    if parametrisation == "EXOFAST":
                        l_orb_param_basename += ['aR']
                        l_orb_new_param_key += ['aR']
                        l_orb_param_unit += ['w/o unit']
                    for (l_param_basename, l_new_param_key, l_param_unit, dico_config_mod, mod_name
                         ) in zip([l_occ_param_basename, l_orb_param_basename],
                                  [l_occ_new_param_key, l_orb_new_param_key],
                                  [l_occ_param_unit, l_orb_param_unit],
                                  [dico_config_occ_mod_comp, dico_config_orb_mod_comp],
                                  [mod_comp_name, orb_model_name]
                                  ):
                        for param_basename, new_param_key, param_unit in zip(l_param_basename, l_new_param_key, l_param_unit):
                            if (new_param_key is None) or (dico_config_mod['new_parameter'][new_param_key] is True):
                                param_name = f"{param_basename}{mod_name}"
                            else:
                                param_name = f"{param_basename}{dico_config_mod['new_parameter'][new_param_key]}"
                            if planet.has_parameter(name=param_name, return_error=False, kwargs_get_list_params=None, kwargs_get_name={'recursive': False, 'include_prefix': False}):
                                param = planet.parameters[param_name]
                            else:
                                param = Parameter(name=param_name, name_prefix=planet.name, unit=param_unit)
                                planet.add_parameter(param)
                            param.main = True

    def apply_limbdarkening_parametrisation(self, parametrisation):
        """Make all the parameters of all the Limb Darkening param containers main parameters."""
        if LC_inst_cat in set(self.model_instance.dataset_db.inst_categories):
            for LD_parcont in self.get_list_LD_parconts():
                for param in LD_parcont.get_list_params(no_duplicate=True):
                    param.main = True

    def apply_instmodel_parametrisation(self, parametrisation):
        """Apply the parametrisation to an instrument model object.
        """
        # # instrumental variation parametrisation
        # inst_mod_obj.init_inst_var_parameters(with_inst_var=self.model_instance.parametrisation_kwargs.get("with_inst_var", False),
        #                                       inst_var_order=self.model_instance.parametrisation_kwargs.get("inst_var_order", None))
        # # The initialisation of the instrumental contamination is already made in the instrument model
        # # See exoplanet.dataset_and_instrument.lc.LC_Instrument.__params_model__
        l_inst_fullcat = self.model_instance.instruments.get_inst_fullcat4inst_cat(inst_cat=LC_inst_cat)
        for inst_fullcat_i in l_inst_fullcat:
            for inst_model in self.model_instance.get_instmodel_objs(inst_fullcat=LC_inst_cat):
                inst_model.apply_parametrisation()
                self.apply_instmod_parametrisation_decorrelation(inst_mod_obj=inst_model)

    def apply_instmod_parametrisation_decorrelation(self, inst_mod_obj):
        """Apply the parametrisation for the decorrelation to an instrument model object.

        Arguments
        ---------
        inst_mod_obj : Instrument_Model
            Instrument_Model instance providing the instrument model to be parametrised.
        """
        # Decorrelation model
        if self.do_decorrelate_model_instmod(instmod_fullname=inst_mod_obj.full_name):
            for model_part in self.decorrelation_model_config[inst_mod_obj.full_name]['what to decorrelate'].keys():
                for DecorModel in self.l_decorrelation_model_class:
                    DecorModel.apply_parametrisation(inst_mod_obj=inst_mod_obj,
                                                     model_part=model_part,
                                                     decorrelation_config_inst_decorr=self.decorrelation_model_config[inst_mod_obj.full_name]['what to decorrelate'][model_part][DecorModel.category])
        # Decorrelation likelihood
        if self.do_decorrelate_likelihood_instmod(instmod_fullname=inst_mod_obj.full_name):
            for DecorModel in self.l_decorrelation_likelihood_class:
                DecorModel.apply_parametrisation(inst_mod_obj=inst_mod_obj,
                                                 decorrelation_config_inst_decorr=self.decorrelation_likelihood_config[inst_mod_obj.full_name][DecorModel.category])
