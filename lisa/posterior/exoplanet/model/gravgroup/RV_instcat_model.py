#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
RV_instcat_model module.

The objective of this package is to provides the RV_InstCat_Model class to handle the RV instrument class
for the GravGroup class.

@DONE:
    -

@TODO:
    - self.stars is used here but it's only define in GravGroup that makes the code a bit difficult to
    understand and follow. Is there a solution ? same thing for self.paramfile4instcat
"""
from logging import getLogger
from textwrap import dedent
from pprint import pformat
# from os.path import basename
# import os

from .datasim_creator_rv import create_datasimulator_RV
from ..decorrelation.linear_decorrelation import LinearDecorrelation
from ...dataset_and_instrument.rv import RV_inst_cat
from ...likelihood.decorrelation.spline_decorrelation import SplineDecorrelation
from ...likelihood.decorrelation.bispline_decorrelation import BiSplineDecorrelation
from ....core.model.core_instcat_model import Core_InstCat_Model
from ....core.model.polynomial_model import set_dico_config, get_dico_config
from ....core.dataset_and_instrument.manager_dataset_instrument import Manager_Inst_Dataset
from .....tools.miscellaneous import spacestring_like


## Logger object
logger = getLogger()

mgr_inst_dst = Manager_Inst_Dataset()
mgr_inst_dst.load_setup()


class RV_InstCat_Model(Core_InstCat_Model):
    """docstring for LC_InstCat_Model, interface class of GravGroup."""

    # Mandatory attributes for a sublass of Core_InstCat_Model
    __inst_cat__ = RV_inst_cat
    __has_instcat_paramfile__ = True
    __default_paramfile_name__ = "RV_param_file.py"
    __datasim_creator_name__ = "sim_RV"
    __l_decorrelation_class__ = [LinearDecorrelation, SplineDecorrelation, BiSplineDecorrelation]

    allowed_what2decorrelate_strs = ['add_2_totalrv', 'multiply_2_totalrv']

    ## List of available rv models, the 1st element is used as default
    _rv_models = ["radvel", ]  # ["radvel", "ajplanet"] Temporarily? remove ajplanet from the available rv_models

    def __init__(self, model_instance):
        super(RV_InstCat_Model, self).__init__(model_instance=model_instance)
        self.rv_model = {planet.get_name(): {"do": True,
                                             "model": "radvel"
                                             }
                         for planet in self.model_instance.planets.values()
                         }
        # # Initialise the dictionary giving the RV zero point RV_references
        # self.__RV_references = dict.fromkeys(model_instance.get_inst_names(inst_fullcat=RV_inst_cat), None)
        # logger.debug("RV instruments names: {}".format(list(self.__RV_references.keys())))
        # self.__RV_references["global"] = list(self.__RV_references.keys())[0]
        # for key in self.__RV_references:
        #     if key != "global":
        #         self.__RV_references[key] = model_instance.get_instmodel_names(inst_name=key,
        #                                                                        inst_fullcat=RV_inst_cat)[0]
        # Set the dictionaries for the polynomial models
        for star in self.model_instance.stars.values():
            star.set_dico_config_polymodel(inst_cat=self.inst_cat, dico_config={'do': True})
        for ii, instmod_obj in enumerate(self.model_instance.get_instmodel_objs(inst_fullcat=self.__inst_cat__)):
            if ii == 0:
                dico_config = {'do': False}
            else:
                dico_config = {'do': True}
            instmod_obj.set_dico_config_polymodel(dico_config=dico_config)  # Defined in lisa.posterior.exoplanet.dataset_and_instrument.rv.Instrument_RV and accessed through lisa.posterior.core.dataset_and_instrument.instrument.Instrument_Model.__getattr__

    # @property
    # def RV_references(self):
    #     return self.__RV_references
    #
    # @property
    # def RV_globalref_instname(self):
    #     return self.__RV_references["global"]

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
        return create_datasimulator_RV(star=list(self.model_instance.stars.values())[0], planets=self.model_instance.planets,
                                       rv_model=self.rv_model, dataset_db=self.model_instance.dataset_db,
                                       RVcat_model=self, inst_models=inst_models, datasets=datasets,
                                       get_times_from_datasets=get_times_from_datasets
                                       )

    def create_text_instcat_paramfile_model(self, model_instance):
        """Create a parameter file for the light-curve parametrisation.

        Arguments
        ---------
        model_instance      : Model instance
        """
        # Define the global structure of the file
        text_RV_param = """
        # Radial Velocity parametrisation file of {object_name}

        # Which model do you want to use for the rv keplerian ?
        keplerian_rv_model = {keprv_model}

        # Polynomial trends
        polynomial_model = {poly_models}
        """
        text_RV_param = dedent(text_RV_param)  # Remove undesired indentation

        # Create some of the easy content of the file
        tab_keprvmod = spacestring_like("keplerian_rv_model = ")
        tab_poly = spacestring_like("polynomial_model = ")

        # Create the dictionary for the polynomial models
        dico_poly = {}
        for star_name, star in self.model_instance.stars.items():
            dico_poly[star_name] = star.get_dico_config_polymodel(inst_cat=self.inst_cat, notexist_ok=False)
        for instmod_obj in self.model_instance.get_instmodel_objs(inst_fullcat=self.__inst_cat__):
            dico_poly[instmod_obj.full_name] = instmod_obj.get_dico_config_polymodel(notexist_ok=False)  # Defined in lisa.posterior.exoplanet.dataset_and_instrument.rv.Instrument_RV and accessed through lisa.posterior.core.dataset_and_instrument.instrument.Instrument_Model.__getattr__

        # Fill the whole text_LC_param string
        text_RV_param = text_RV_param.format(object_name=self.model_instance.get_name(),
                                             keprv_model=pformat(self.rv_model, compact=True).replace("\n", f"\n{tab_keprvmod}"),
                                             poly_models=pformat(dico_poly, compact=True).replace("\n", f"\n{tab_poly}"),
                                             )

        return text_RV_param

    def load_config(self, dico_config):
        """load the configuration specified by the dictionnary"""
        # Check the rv_model
        dict_name = "keplerian_rv_model"
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
                key = "model"
                if key not in dico_model[planet_name]:
                    raise ValueError(f"In file {self.paramfile_instcat}: Dictionary {dict_name}[{planet_name}] is missing the '{key}' key.")
                # Check and load the rv_model dictionary
                # TODO?: Make checks on the content of each model in 'model_definitions'
                self.rv_model[planet_name] = dico_config["keplerian_rv_model"][planet_name]

        # Check and load the polynomial models
        if "polynomial_model" in dico_config:
            for star_name, star in self.model_instance.stars.items():
                if star_name in dico_config["polynomial_model"]:
                    star.set_dico_config_polymodel(inst_cat=self.inst_cat, dico_config=dico_config["polynomial_model"][star_name])
            for instmod_obj in self.model_instance.get_instmodel_objs(inst_fullcat=self.__inst_cat__):
                if instmod_obj.full_name in dico_config["polynomial_model"]:
                    instmod_obj.set_dico_config_polymodel(dico_config=dico_config["polynomial_model"][instmod_obj.full_name])  # Defined in lisa.posterior.exoplanet.dataset_and_instrument.rv.Instrument_RV and accessed through lisa.posterior.core.dataset_and_instrument.instrument.Instrument_Model.__getattr__

    # def set_RV_globalref_instname(self, inst_name):
    #     self.__RV_references["global"] = inst_name
    #
    # def get_RVref4inst_modname(self, inst_name):
    #     return self.__RV_references[inst_name]
    #
    # def set_RVref4inst_modname(self, inst_name, inst_model_name):
    #     self.__RV_references[inst_name] = inst_model_name

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
        # TODO: Check that the decorrelation dictionary has on entry per instrument model object of
        # the current instrument category
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

    def apply_star_planet_parametrisation(self, parametrisation):
        """Apply the parametrisation to the star and planet objects.
        """
        ##################################################
        # Apply the parametrisation to the star parameters
        ##################################################
        # Systemic velocity (RVs)
        for star in self.model_instance.stars.values():
            star.apply_polymodel_parametrisation(inst_cat=RV_inst_cat)

        # Apply the parametrisation to the planets parameters
        for planet in self.model_instance.planets.values():
            # planet_name = planet.get_name()
            planet.K.main = True
            planet.K.unit = "[amplitude of the RV data]"
            planet.P.main = True
            planet.P.unit = "[time of the RV/LC data]"
            planet.tic.main = True
            planet.tic.unit = "[time of the RV/LC data]"
            planet.ecosw.main = True  # Unit already defined in celestial_bodies
            planet.esinw.main = True  # Unit already defined in celestial_bodies

    def apply_instmodel_parametrisation(self, parametrisation):
        """Apply the parametrisation to an instrument model object.

        This parametrisation should not include the decorrelation

        Arguments
        ---------
        inst_mod_obj : Instrument_Model
            Instrument_Model instance providing the instrument model to be parametrised.
        """
        # instrumental variation parametrisation
        # For I have not implemented how the use can define inst_var for RVs but once it's done
        # It only needs to be provided here
        # inst_mod_obj.init_inst_var_parameters(with_inst_var=False, inst_var_order=1)
        l_inst_fullcat = self.model_instance.instruments.get_inst_fullcat4inst_cat(inst_cat=RV_inst_cat)
        for inst_fullcat_i in l_inst_fullcat:
            for inst_model in self.model_instance.get_instmodel_objs(inst_fullcat=RV_inst_cat):
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
