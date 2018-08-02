#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
parametrisation module

The Objective of this file is to define the different type of parametrisation available.
"""
from logging import getLogger
from collections import Counter
from numpy import pi

from .parametrisation_gravgroup import GravGroup_Parametrisation
from ..dataset_and_instrument.lc import LC_inst_cat
from ..dataset_and_instrument.rv import RV_inst_cat


## Logger Object
logger = getLogger()


class GravGroupDyn_Parametrisation(GravGroup_Parametrisation):
    """docstring for the interface class GravGroup_Parametrisation."""

    @property
    def available_parametrisations(self):
        """List of the available parametrisation."""
        return ["Standard", "Np"]

    def _choose_default_parametrisation(self):
        """Return the best parametrisation when no choice is made by the user."""
         if self.nb_planets == 2:
             return "Np"
         else:
             return "Standard"

    def _check_validity_parametrisation(self, parametrisation):
        """Check that the parametrisation requested is valid for the current model.

        If not raise ValueError. For now there is no validity concern for model given the existing
        parametrisations.

        :param str parametrisation: String which designate the parametrisation. Should be in
            self.available_parametrisations
        """
        if parametrisation == "Np" and (self.nb_planets not in [2, ]):
            raise ValueError("Parametrisation {} is not available with the current number of "
                             "planets. Possible number of planets: {}"
                             "".format(parametrisation, self.nb_planets))

    # TODO: This function doesn't seems to be used anywhere. SO I didn't updated it.
    def __check_args(self, **kwargs):
        """Raise an error if the provided arguments are the one expected.
        """
        l_missing = []
        l_unexpected = []
        l_mandatory_keywords = []
        l_optional_keywords = []

        # Fill the list of mandatory and optional keywords depending on the parameterisation
        if RV_inst_cat in self.RV_parametrisations:
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
        l_unexpected += [arg for arg in kwargs if arg not in (l_mandatory_keywords +
                                                              l_optional_keywords)]
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

    def apply_star_planet_parametrisation(self, OmegaRef_planet=None, ):
        """Apply the parametrisation for the star and planets.

        For Np and number of planet equal to 2, see Barros+16

        :param str OmegaRef_planet: Name of the planet used as reference for OMEGA (Longitude of
            ascendal node). For this planet, OMEGA will be fixed and it's value set to 180.
        """
        # Apply the parametrisation to the star parameters
        if RV_inst_cat in set(self.dataset_db.inst_categories):
            self.apply_star_SystemicRV_parametrisation()

        star_name = list(self.paramcontainers["stars"].keys())[0]
        self.paramcontainers["stars"][star_name].M.main = True

        if LC_inst_cat in set(self.dataset_db.inst_categories):
            self.paramcontainers["stars"][star_name].R.main = True

        # Apply the parametrisation to the planets parameters
        if OmegaRef_planet is None:
            OmegaRef_planet = self.paramcontainers["planets"].keys()[0]
        for planet_name in list(self.paramcontainers["planets"].keys()):
            self.paramcontainers["planets"][planet_name].P.main = True
            self.paramcontainers["planets"][planet_name].tic.main = True
            self.paramcontainers["planets"][planet_name].inc.main = True
            if planet_name == OmegaRef_planet:
                self.paramcontainers["planets"][planet_name].OMEGA.main = True
                self.paramcontainers["planets"][planet_name].OMEGA.free = False
                self.paramcontainers["planets"][planet_name].OMEGA.value = pi
            else:
                self.paramcontainers["planets"][planet_name].OMEGA.main = True
            if self.parametrisation == "Standard":
                self.paramcontainers["planets"][planet_name].M.main = True
                self.paramcontainers["planets"][planet_name].secosw.main = True
                self.paramcontainers["planets"][planet_name].sesinw.main = True
            if LC_inst_cat in set(self.dataset_db.inst_categories):
                self.paramcontainers["planets"][planet_name].Rrat.main = True

        if self.parametrisation == "Np":
            self.add_parameter(Parameter(name="qplus", name_prefix=self.full_name, main=True))
            self.add_parameter(Parameter(name="qp", name_prefix=self.full_name, main=True))
            self.add_parameter(Parameter(name="hplus", name_prefix=self.full_name, main=True))
            self.add_parameter(Parameter(name="hminus", name_prefix=self.full_name, main=True))
            self.add_parameter(Parameter(name="kplus", name_prefix=self.full_name, main=True))
            self.add_parameter(Parameter(name="kminus", name_prefix=self.full_name, main=True))
