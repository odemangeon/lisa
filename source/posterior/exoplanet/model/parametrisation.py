#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
parametrisation module

The Objective of this file is to define the different type of parametrisation available.
"""
from logging import getLogger
from collections import Counter


## Logger Object
logger = getLogger()


class GravGroup_Parametrisation(object):
    """docstring for the interface class GravGroup_Parametrisation."""

    @property
    def available_parametrisations(self):
        """List of the available parametrisation."""
        return ["RV_EXOFAST", "LC_EXOFAST", "RV&LC_EXOFAST", "LC_Multis", "RV&LC_Multis"]

    @property
    def RV_parametrisations(self):
        """List of the available parametrisations for RV datasets."""
        return ["RV_EXOFAST", "RV&LC_EXOFAST", "RV&LC_Multis"]

    @property
    def LC_parametrisations(self):
        """List of the available parametrisations for RV datasets."""
        return ["LC_EXOFAST", "LC_Multis", "RV&LC_EXOFAST", "RV&LC_Multis"]

    @property
    def LC_multis_parametrisations(self):
        """List of the available parametrisations for LC datasets using the Multis params."""
        return ["LC_Multis", "RV&LC_Multis"]

    @property
    def RVandLC_parametrisations(self):
        """List of the available parametrisations for RV datasets."""
        return ["RV&LC_EXOFAST", "RV&LC_Multis"]

    @property
    def parametrisation(self):
        """Dictionary defining the available parametrisation and their apply functions."""
        return self.__parametrisation

    @parametrisation.setter
    def parametrisation(self, value=None):
        """Set the parametrisation to use."""
        if value is None:
            if Counter(self.dataset_db.inst_categories) == Counter(["RV", ]):
                self.__parametrisation = "RV_EXOFAST"
            elif Counter(self.dataset_db.inst_categories) == Counter(["LC", ]):
                if self.nb_planets > 1:
                    self.__parametrisation = "LC_Multis"
                else:
                    self.__parametrisation = "LC_EXOFAST"
            elif Counter(self.dataset_db.inst_categories) == Counter(["LC", "RV"]):
                if self.nb_planets > 1:
                    self.__parametrisation = "RV&LC_Multis"
                else:
                    self.__parametrisation = "RV&LC_EXOFAST"
            else:
                raise ValueError("{} doesn't correspond to a predefined parametrisation."
                                 "".format(self.dataset_db.inst_categories))
            logger.info("No parametrisation provided. The automatically selected parametrisation is"
                        ": {}".format(self.parametrisation))
        else:
            if value in self.available_parametrisations:
                self.__parametrisation = value
            else:
                raise ValueError("{} is not an available parametrisation ({})"
                                 "".format(value, self.available_parametrisations))
        logger.info("The parametrisation has been set: {}".format(self.__parametrisation))

    @property
    def parametrisation_kwargs(self):
        """Dictionary giving the keyword arguments of the apply_parametrisation method."""
        try:
            return self.__parametrisation_kwargs
        except:
            self.__parametrisation_kwargs = {}
            return self.__parametrisation_kwargs

    def apply_parametrisation(self, **kwargs):
        """Apply the parametrisation pointed by the parametrisation property."""
        # Check that there is just 1 star and at least 1 planet
        self.__check_nstar()
        self.__check_nplanet()

        # Check that the instrument category of all the datasets is as expected otherwise raise a
        # warning
        self.__check_dataset_instcat()
        # Init and Fill the dictionary parametrisation_kwargs
        self.save_parametrisation_kwargs(**kwargs)

        # Apply the parametrisation to the star and planets parameters
        self.apply_star_planet_parametrisation()

        # Apply the parametrisation to the instrument models parameters
        self.apply_instmodel_parametrisation()

        # If needed apply the limbdarkening coefficient parametrisation
        self.limbdarkening_parametrisation()

    def __check_args(self, **kwargs):
        """Raise an error if the provided arguments are the one expected."""
        l_missing = []
        l_unexpected = []
        l_mandatory_keywords = []
        l_optional_keywords = []

        # Fill the list of mandatory and optional keywords depending on the parameterisation
        if self.parametrisation in self.RV_parametrisatons:
            l_mandatory_keywords += ["with_DeltaRV", "with_RVdrift"]
            l_optional_keywords += ["RVdrift_order"]
        if self.parametrisation in self.LC_parametrisatons:
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
        if self.parametrisation in self.RV_parametrisatons:
            if not(kwargs["with_RVdrift"]):
                l_optional_keywords.remove("RVdrift_order")
        if self.parametrisation in self.LC_parametrisatons:
            if not(kwargs["with_OOT_var"]):
                l_optional_keywords.remove("OOT_var_order")
        l_missing += [arg for arg in l_optional_keywords if arg not in kwargs]
        if len(l_missing) > 0:
            raise TypeError("apply_parametrisation missing {} keyword argument: {}"
                            "".format(len(l_missing), l_missing))

    def __check_nstar(self):
        """Raise an error if the number of stars in the gravgroup is not the one expected."""
        if self.parametrisation in ["RV_EXOFAST", "LC_EXOFAST", "RV&LC_EXOFAST", "LC_Multis",
                                    "RV&LC_Multis"]:
            if self.nb_of_paramcontainers["stars"] != 1:
                raise ValueError("{} parametrisation can only be applied to gravgroups "
                                 "with exactly 1 star. This gravgroups has {} star(s)."
                                 "".format(self.parametrisation,
                                           self.nb_of_paramcontainers["stars"]))

    def __check_nplanet(self):
        """Raise an error if the number of planets in the gravgroup is not the one expected."""
        if self.parametrisation in ["RV_EXOFAST", "LC_EXOFAST", "RV&LC_EXOFAST", "LC_Multis",
                                    "RV&LC_Multis"]:
            if self.nb_of_paramcontainers["planets"] < 1:
                raise ValueError("{} parametrisation can only be applied to gravgroups "
                                 "with at least 1 planet. This gravgroups has {} planet(s)."
                                 "".format(self.parametrisation,
                                           self.nb_of_paramcontainers["planets"]))

    def __check_dataset_instcat(self):
        """Raise an error if the instrument categories of the dataset are not as expected."""
        if self.parametrisation in ["RV_EXOFAST", ]:
            l_instcat_expected = ["RV", ]
        elif self.parametrisation in ["LC_EXOFAST", "LC_Multis"]:
            l_instcat_expected = ["RV", ]
        elif self.parametrisation in ["RV&LC_EXOFAST", "RV&LC_Multis"]:
            l_instcat_expected = ["RV", "LC"]
        if Counter(self.dataset_db.inst_categories) != Counter(l_instcat_expected):
            raise ValueError("You are using a paprametrisation that has been defined to fit {}"
                             "but you have to analyse {}."
                             "".format(l_instcat_expected, self.dataset_db.inst_categories))

    def apply_star_planet_parametrisation(self):
        """Apply the parametrisation for the star and planets.

        For the EXOFAST parametrisations:
        See Eastman, J., et al., 2013, Publications of the Astronomical Society of the Pacific,
        Volume 125,Number 923.
        """
        # Apply the parametrisation to the star parameters
        star_name = list(self.paramcontainers["stars"].keys())[0]
        if self.parametrisation in self.RV_parametrisatons:
            self.paramcontainers["stars"][star_name].v0.main = True
            (self.paramcontainers["stars"][star_name].
             init_RVdrift_parameters)(with_RVdrift=self.parametrisation_kwargs["with_RVdrift"],
                                      RVdrift_order=self.parametrisation_kwargs.get("RVdrift_order",
                                                                                    None))
        if self.parametrisation in ["LC_multis", "RV&LC_EXOFAST"]:
            self.paramcontainers["stars"][star_name].rho.main = True

        # Apply the parametrisation to the planets parameters
        for planet_name in list(self.paramcontainers["planets"].keys()):
            if self.parametrisation in self.LC_parametrisations:
                self.paramcontainers["planets"][planet_name].Rrat.main = True
                self.paramcontainers["planets"][planet_name].cosinc.main = True
            if self.parametrisation in ["LC_EXOFAST", "RV&LC_EXOFAST"]:
                self.paramcontainers["planets"][planet_name].aR.main = True
            if self.parametrisation in self.RV_parametrisations:
                self.paramcontainers["planets"][planet_name].K.main = True
            if self.parametrisation in ["RV_EXOFAST", "LC_EXOFAST", "RV&LC_EXOFAST", "LC_Multis",
                                        "RV&LC_Multis"]:
                self.paramcontainers["planets"][planet_name].P.main = True
                self.paramcontainers["planets"][planet_name].tc.main = True
                self.paramcontainers["planets"][planet_name].secosw.main = True
                self.paramcontainers["planets"][planet_name].sesinw.main = True

    def apply_instmodel_parametrisation(self):
        """Apply the instmodel parametrisation according to the parametrisation chosen."""
        if self.parametrisation in self.RV_parametrisations:
            DeltaRV_main = self.parametrisation_kwargs["with_DeltaRV"]
            if DeltaRV_main:
                RVrefglobal_instname = self.RV_globalref_instname
                RVrefglobal_modname = self.get_RVref4inst_modname(RVrefglobal_instname)
            list_instmodel = self.get_instmodel_objs(inst_cat="RV")
            for inst_model in list_instmodel:
                inst_name = inst_model.instrument.name
                inst_model.DeltaRV.main = DeltaRV_main
                if DeltaRV_main:
                    if ((inst_name == RVrefglobal_instname) and
                       (inst_model.name == RVrefglobal_modname)):
                        inst_model.DeltaRV.free = False
                        inst_model.DeltaRV.value = 0.0
        if self.parametrisation in self.LC_parametrisations:
            list_instmodel = self.get_instmodel_objs(inst_cat="LC")
            for inst_model in list_instmodel:
                (inst_model.
                 init_OOT_var_parameters(with_OOT_var=self.parametrisation_kwargs["with_OOT_var"],
                                         OOT_var_order=(self.
                                                        parametrisation_kwargs["OOT_var_order"])))

    def limbdarkening_parametrisation(self):
        """Make all the parameters of all the Limb Darkening param containers main parameters."""
        if self.parametrisation in self.LC_parametrisations:
            for LD_parcont in self.get_list_LD_parconts():
                for param in LD_parcont.get_list_params():
                    param.main = True

    def save_parametrisation_kwargs(self, **kwargs):
        """Save the keyword arguments of the parmetrisation function in parametrisation_kwargs."""
        for key, value in kwargs.items():
            self.parametrisation_kwargs[key] = value
