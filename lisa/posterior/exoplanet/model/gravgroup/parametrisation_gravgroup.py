#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
parametrisation module

The Objective of this file is to define the different type of parametrisation available.
"""
from logging import getLogger

from ...dataset_and_instrument.lc import LC_inst_cat
from ...dataset_and_instrument.rv import RV_inst_cat
from ....core.model.core_parametrisation import Core_Parametrisation
from ....core.dataset_and_instrument.indicator import IND_inst_cat


## Logger Object
logger = getLogger()


# TODO: At one point, it might be usefull to make a Core_Parametrisation class


class GravGroup_Parametrisation(Core_Parametrisation):
    """docstring for the interface class GravGroup_Parametrisation."""

    @property
    def available_parametrisations(self):
        """List of the available parametrisation."""
        return super(GravGroup_Parametrisation, self).available_parametrisations + ["EXOFAST", "Multis"]

    def _choose_default_parametrisation(self):
        """Return the best parametrisation when no choice is made by the user."""
        if self.nb_planets > 1:
            return "Multis"
        else:
            return "EXOFAST"

    def _check_validity_parametrisation(self, parametrisation):
        """Check that the parametrisation requested is valid for the current model.

        If not raise ValueError. For now there is no validity concern for model given the existing
        parametrisations.

        :param str parametrisation: String which designate the parametrisation. Should be in
            self.available_parametrisations
        """
        pass

    def apply_parametrisation(self, **kwargs):
        """Apply the parametrisation pointed by the parametrisation property."""
        # Check that there is just 1 star and at least 1 planet
        self.__check_nstar()
        self.__check_nplanet()

        # Apply the parametrisation to the star and planets parameters
        self.apply_star_planet_parametrisation()

        # Apply the parametrisation to the instrument models parameters
        # TODO: I want it to got to Core_Parametrisation set_parametrisation method, but it requires a bit of uniformisation of the instrument category parameterisation methods.
        self.apply_instmodel_parametrisation()

        # If needed apply the limbdarkening coefficient parametrisation
        self.limbdarkening_parametrisation()

    # TODO: This function doesn't seems to be used anywhere. Check why
    def __check_args(self, **kwargs):
        """Raise an error if the provided arguments are the one expected."""
        l_missing = []
        l_unexpected = []
        l_mandatory_keywords = []
        l_optional_keywords = []

        # Fill the list of mandatory and optional keywords depending on the parameterisation
        if self.parametrisation in self.RV_parametrisations:
            l_mandatory_keywords += ["with_DeltaRV", "with_RVdrift"]
            l_optional_keywords += ["RVdrift_order"]
        if self.parametrisation in self.LC_parametrisations:
            l_mandatory_keywords += ["with_OOT_var"]
            l_optional_keywords += ["OOT_var_order"]

        # Check that the mandatory keywords arguments are provided.
        l_missing += [arg for arg in l_mandatory_keywords if arg not in kwargs]
        if len(l_missing) > 0:
            raise TypeError("apply_parametrisation missing {} keyword argument: {}"
                            "".format(len(l_missing), l_missing))

        # Check that no extra keywords arguments is provided.
        l_unexpected += [arg for arg in kwargs if arg not in (l_mandatory_keywords + l_optional_keywords)]
        if len(l_unexpected) > 0:
            raise TypeError("apply_parametrisation got {} unexpected keyword argument: {}"
                            "".format(len(l_unexpected), l_unexpected))

        # Check that no optional keyword is missing
        if self.parametrisation in self.RV_parametrisations:
            if not(kwargs["with_RVdrift"]):
                l_optional_keywords.remove("RVdrift_order")
        if self.parametrisation in self.LC_parametrisations:
            if not(kwargs["with_OOT_var"]):
                l_optional_keywords.remove("OOT_var_order")
        l_missing += [arg for arg in l_optional_keywords if arg not in kwargs]
        if len(l_missing) > 0:
            raise TypeError("apply_parametrisation missing {} keyword argument: {}"
                            "".format(len(l_missing), l_missing))

    def __check_nstar(self):
        """Raise an error if the number of stars in the gravgroup is not the one expected."""
        if self.nb_of_paramcontainers["stars"] != 1:
            raise ValueError("{} parametrisation can only be applied to gravgroups "
                             "with exactly 1 star. This gravgroups has {} star(s)."
                             "".format(self.parametrisation,
                                       self.nb_of_paramcontainers["stars"]))

    def __check_nplanet(self):
        """Raise an error if the number of planets in the gravgroup is not the one expected."""
        if self.nb_of_paramcontainers["planets"] < 1:
            raise ValueError("{} parametrisation can only be applied to gravgroups "
                             "with at least 1 planet. This gravgroups has {} planet(s)."
                             "".format(self.parametrisation,
                                       self.nb_of_paramcontainers["planets"]))

    def apply_star_planet_parametrisation(self):
        """Apply the parametrisation for the star and planets.

        For the EXOFAST parametrisations:
        See Eastman, J., et al., 2013, Publications of the Astronomical Society of the Pacific,
        Volume 125,Number 923.
        """
        ##################################################
        # Apply the parametrisation to the star parameters
        ##################################################
        # Systemic velocity (RVs)
        if RV_inst_cat in set(self.dataset_db.inst_categories):
            self.apply_star_SystemicRV_parametrisation()

        # Stellar density (orbit Multis parametrisation)
        if (LC_inst_cat in set(self.dataset_db.inst_categories)) and (self.parametrisation == "Multis"):
            star_name = list(self.paramcontainers["stars"].keys())[0]
            self.paramcontainers["stars"][star_name].rho.main = True
            self.paramcontainers["stars"][star_name].rho.unit = "Solar density"

        # Stellar effective temperature (Phase curve if spiderman and zhang brightness model)
        if LC_inst_cat in set(self.dataset_db.inst_categories):
            for planet in self.planets.values():
                planet_name = planet.get_name()
                if self.instcat_models[LC_inst_cat].phasecurve_model[planet_name]['do']:
                    for l_mod_comp_name in self.instcat_models[LC_inst_cat].phasecurve_model[planet_name]["model4instrument"].values():
                        for mod_comp_name in l_mod_comp_name:
                            if self.instcat_models[LC_inst_cat].phasecurve_model[planet_name]["model_definitions"][mod_comp_name]["model"] == 'spiderman':
                                if self.instcat_models[LC_inst_cat].phasecurve_model[planet_name]["model_definitions"][mod_comp_name]['args']['ModelParams_kwargs']['brightness_model'] == 'zhang':
                                    self.paramcontainers["stars"][star_name].Teff.main = True

        # Apply the parametrisation to the planets parameters
        for planet_name in list(self.paramcontainers["planets"].keys()):
            if LC_inst_cat in set(self.dataset_db.inst_categories):
                self.paramcontainers["planets"][planet_name].Rrat.main = True
                self.paramcontainers["planets"][planet_name].Rrat.unit = "w/o unit"
                self.paramcontainers["planets"][planet_name].cosinc.main = True  # Unit already defined in celestial_bodies
            if (LC_inst_cat in set(self.dataset_db.inst_categories)) and (self.parametrisation == "EXOFAST"):
                self.paramcontainers["planets"][planet_name].aR.main = True  # Unit already defined in celestial_bodies
            if RV_inst_cat in set(self.dataset_db.inst_categories):
                self.paramcontainers["planets"][planet_name].K.main = True
                self.paramcontainers["planets"][planet_name].K.unit = "[amplitude of the RV data]"
            self.paramcontainers["planets"][planet_name].P.main = True
            self.paramcontainers["planets"][planet_name].P.unit = "[time of the RV/LC data]"
            self.paramcontainers["planets"][planet_name].tic.main = True
            self.paramcontainers["planets"][planet_name].tic.unit = "[time of the RV data]"
            self.paramcontainers["planets"][planet_name].ecosw.main = True  # Unit already defined in celestial_bodies
            self.paramcontainers["planets"][planet_name].esinw.main = True  # Unit already defined in celestial_bodies
            if LC_inst_cat in set(self.dataset_db.inst_categories):
                if self.instcat_models[LC_inst_cat].phasecurve_model[planet_name]['do']:
                    for l_mod_comp_name in self.instcat_models[LC_inst_cat].phasecurve_model[planet_name]["model4instrument"].values():
                        for mod_comp_name in l_mod_comp_name:
                            if self.instcat_models[LC_inst_cat].phasecurve_model[planet_name]["model_definitions"][mod_comp_name]["model"] == 'spiderman':
                                if self.instcat_models[LC_inst_cat].phasecurve_model[planet_name]["model_definitions"][mod_comp_name]['args']['ModelParams_kwargs']['brightness_model'] == 'zhang':
                                    self.paramcontainers["planets"][planet_name].a.main = True
                                    self.paramcontainers["planets"][planet_name].a.unit = "AU"
                                    self.paramcontainers["planets"][planet_name].u1.main = True
                                    self.paramcontainers["planets"][planet_name].u2.main = True
                                    self.paramcontainers["planets"][planet_name].xi.main = True
                                    self.paramcontainers["planets"][planet_name].Tn.main = True
                                    self.paramcontainers["planets"][planet_name].deltaT.main = True

    def apply_star_SystemicRV_parametrisation(self):
        """Apply the parametrisation for the modelling of the systemic RV.
        """
        # Apply the parametrisation to the star parameters for the systemic RV
        star_name = list(self.paramcontainers["stars"].keys())[0]
        self.paramcontainers["stars"][star_name].v0.main = True
        self.paramcontainers["stars"][star_name].v0.unit = "[amplitude of the RV data]"
        self.paramcontainers["stars"][star_name].init_RVdrift_parameters(with_RVdrift=self.parametrisation_kwargs.get("with_RVdrift", False),
                                                                         RVdrift_order=self.parametrisation_kwargs.get("RVdrift_order", None))

    def apply_instmodel_parametrisation(self):
        """Apply the instmodel parametrisation according to the parametrisation chosen."""
        if RV_inst_cat in set(self.dataset_db.inst_categories):
            RV_instcat_model = self.instcat_models[RV_inst_cat]
            DeltaRV_main = self.parametrisation_kwargs.get("with_DeltaRV", False)
            RVrefglobal_instname = RV_instcat_model.RV_globalref_instname
            RVrefglobal_modname = RV_instcat_model.get_RVref4inst_modname(RVrefglobal_instname)
            list_instmodel = self.get_instmodel_objs(inst_fullcat=RV_inst_cat)  # self.get_instmodel_objs comes from InstrumentContainerInterface
            for inst_model in list_instmodel:
                inst_name = inst_model.instrument.get_name()
                inst_model.DeltaRV.main = DeltaRV_main
                if not(DeltaRV_main) or ((inst_name == RVrefglobal_instname) and (inst_model.get_name() == RVrefglobal_modname)):
                    inst_model.DeltaRV.free = False
                    inst_model.DeltaRV.value = 0.0
                RV_instcat_model.apply_instmod_parametrisation(inst_mod_obj=inst_model)
        if LC_inst_cat in set(self.dataset_db.inst_categories):
            LC_instcat_model = self.instcat_models[LC_inst_cat]
            list_instmodel = self.get_instmodel_objs(inst_fullcat=LC_inst_cat)
            for inst_model in list_instmodel:
                LC_instcat_model.apply_instmod_parametrisation(inst_mod_obj=inst_model)

        if IND_inst_cat in set(self.dataset_db.inst_categories):
            l_inst_fullcat_IND = self.instruments.get_inst_fullcat4inst_cat(inst_cat=IND_inst_cat)
            for inst_fullcat_i in l_inst_fullcat_IND:
                list_instmodel = self.get_instmodel_objs(inst_fullcat=inst_fullcat_i)
                for inst_model in list_instmodel:
                    indicator_model = self.instcat_models["IND"].model_4_indicator[inst_model.instrument.indicator_category]
                    if indicator_model is not None:
                        self.instcat_models[IND_inst_cat]._init_indmodel(inst_model_obj=inst_model, indicator_model=indicator_model,
                                                                         kwargs_indicator_model=self.instcat_models["IND"].params_indicator_models[indicator_model])
        # Decorrelation
        for inst_cat in self.dataset_db.inst_categories:
            # if inst_cat.startswith("IND"):
            #     import pdb; pdb.set_trace()
            instcat_model = self.instcat_models[inst_cat]
            if instcat_model.decorrelate_available:
                l_inst_fullcat = self.instruments.get_inst_fullcat4inst_cat(inst_cat=inst_cat)
                for inst_fullcat_i in l_inst_fullcat:
                    list_instmodel = self.get_instmodel_objs(inst_fullcat=inst_fullcat_i)
                    for inst_model in list_instmodel:
                        instcat_model.apply_instmod_parametrisation_decorrelation(inst_mod_obj=inst_model)

    def limbdarkening_parametrisation(self):
        """Make all the parameters of all the Limb Darkening param containers main parameters."""
        if LC_inst_cat in set(self.dataset_db.inst_categories):
            for LD_parcont in self.instcat_models[LC_inst_cat].get_list_LD_parconts():
                for param in LD_parcont.get_list_params(no_duplicate=True):
                    param.main = True
