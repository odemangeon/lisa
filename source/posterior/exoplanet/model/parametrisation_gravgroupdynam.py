#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
parametrisation module

The Objective of this file is to define the different type of parametrisation available.
"""
from logging import getLogger
from collections import Counter

from .parametrisation_gravgroup import GravGroup_Parametrisation

## Logger Object
logger = getLogger()


class GravGroupDyn_Parametrisation(GravGroup_Parametrisation):
    """docstring for the interface class GravGroup_Parametrisation."""

    @property
    def available_parametrisations(self):
        """List of the available parametrisation."""
        return ["RV_Rebound_Standard", "LC_Rebound_Standard", "RV&LC_Rebound_Standard"]

    @property
    def RV_parametrisations(self):
        """List of the available parametrisations for RV datasets."""
        return ["RV_Rebound_Standard", "RV&LC_Rebound_Standard"]

    @property
    def LC_parametrisations(self):
        """List of the available parametrisations for RV datasets."""
        return ["LC_Rebound_Standard", "RV&LC_Rebound_Standard"]

    @property
    def RVandLC_parametrisations(self):
        """List of the available parametrisations for RV datasets."""
        return ["RV&LC_Rebound_Standard"]

    @GravGroup_Parametrisation.parametrisation.setter
    def parametrisation(self, value=None):
        """Set the parametrisation to use."""
        if value is None:
            if Counter(self.dataset_db.inst_categories) == Counter(["RV", ]):
                GravGroup_Parametrisation.parametrisation.fset(self, "RV_Rebound_Standard")
            elif Counter(self.dataset_db.inst_categories) == Counter(["LC", ]):
                GravGroup_Parametrisation.parametrisation.fset(self, "LC_Rebound_Standard")
            elif Counter(self.dataset_db.inst_categories) == Counter(["LC", "RV"]):
                GravGroup_Parametrisation.parametrisation.fset(self, "RV&LC_Rebound_Standard")
            else:
                raise ValueError("{} doesn't correspond to a predefined parametrisation."
                                 "".format(self.dataset_db.inst_categories))
            logger.info("No parametrisation provided. The automatically selected parametrisation is"
                        ": {}".format(self.parametrisation))
        else:
            super(GravGroupDyn_Parametrisation, self).parametrisation = value

    # TODO: This function doesn't seems to be used anywhere. Check why
    def __check_args(self, **kwargs):
        """Raise an error if the provided arguments are the one expected.
        """
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

    def _check_dataset_instcat(self):
        """Raise an error if the instrument categories of the dataset are not as expected."""
        if self.parametrisation in ["RV_Rebound_Standard", ]:
            l_instcat_expected = ["RV", ]
        elif self.parametrisation in ["LC_Rebound_Standard"]:
            l_instcat_expected = ["LC", ]
        elif self.parametrisation in ["RV&LC_Rebound_Standard"]:
            l_instcat_expected = ["RV", "LC"]
        if Counter(self.dataset_db.inst_categories) != Counter(l_instcat_expected):
            raise ValueError("You are using a parametrisation that has been defined to fit {}"
                             "but you have to analyse {}."
                             "".format(l_instcat_expected, self.dataset_db.inst_categories))

    def apply_star_planet_parametrisation(self):
        """Apply the parametrisation for the star and planets.

        For the EXOFAST parametrisations:
        See Eastman, J., et al., 2013, Publications of the Astronomical Society of the Pacific,
        Volume 125,Number 923.
        """
        # Apply the parametrisation to the star parameters
        self.apply_star_SystemicRV_parametrisation()

        star_name = list(self.paramcontainers["stars"].keys())[0]
        self.paramcontainers["stars"][star_name].M.main = True

        if self.parametrisation in self.LC_parametrisations:
            self.paramcontainers["stars"][star_name].R.main = True

        # Apply the parametrisation to the planets parameters
        for planet_name in list(self.paramcontainers["planets"].keys()):
            self.paramcontainers["planets"][planet_name].M.main = True
            self.paramcontainers["planets"][planet_name].P.main = True
            self.paramcontainers["planets"][planet_name].ecc.main = True
            self.paramcontainers["planets"][planet_name].inc.main = True
            self.paramcontainers["planets"][planet_name].OMEGA.main = True
            self.paramcontainers["planets"][planet_name].omega.main = True
            if self.parametrisation in self.LC_parametrisations:
                self.paramcontainers["planets"][planet_name].R.main = True
