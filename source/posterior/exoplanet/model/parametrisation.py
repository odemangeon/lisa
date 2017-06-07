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
    def available_parametrisation_dico(self):
        """Dictionary defining the available parametrisation and their apply functions."""
        return {"RV_EXOFAST": self.apply_RV_EXOFAST_param,
                "LC_EXOFAST": self.apply_LC_EXOFAST_param,
                "RV&LC_EXOFAST": self.apply_RV_LC_EXOFAST_param}

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
                self.__parametrisation = "LC_EXOFAST"
            elif Counter(self.dataset_db.inst_categories) == Counter(["LC", "RV"]):
                self.__parametrisation = "RV&LC_EXOFAST"
            else:
                raise ValueError("{} doesn't correspond to a predefined parametrisation."
                                 "".format(self.dataset_db.inst_categories))
        else:
            if value in self.available_parametrisation_dico.keys():
                self.__parametrisation = value
            else:
                raise ValueError("{} is not an available parametrisation ({})"
                                 "".format(value, self.available_parametrisation_dico.keys()))
        logger.info("The parametrisation has been set: {}".format(self.__parametrisation))

    @property
    def parametrisation_kwargs(self):
        """Dictionary giving the keyword arguments of the apply_parametrisation method."""
        return self.__parametrisation_kwargs

    def apply_parametrisation(self, *args, **kwargs):
        """Apply the parametrisation pointed by the parametrisation property."""
        self.available_parametrisation_dico[self.parametrisation](*args, **kwargs)

    def apply_RV_EXOFAST_param(self, with_DeltaRV=False, with_RVdrift=False, RVdrift_order=1):
        """Apply the parametrisation for the fit of RV only.

        Apply the parametrisation for Radial Velocity data described in Eastman, J., et
         al., 2013, Publications of the Astronomical Society of the Pacific, Volume 125, Number 923.
        As this parametrisation should be applied only to a GravGroup with one star and one or more
        planets, the function chack first that the GravGroup is compliant.
        """
        # Check that there is just 1 star
        self.__check_only1star()

        # Check that there is at least 1 planet
        self.__check_atleast1planet()

        # Check that the instrument category of all the datasets is "RV" otherwise raise a warning
        self.__check_dataset_instcat(["RV", ])

        # Init and Fill the dictionary parametrisation_kwargs
        self.__parametrisation_kwargs = {}
        self.__parametrisation_kwargs["with_DeltaRV"] = with_DeltaRV
        self.__parametrisation_kwargs["with_RVdrift"] = with_RVdrift
        self.__parametrisation_kwargs["RVdrift_order"] = RVdrift_order

        # Apply the parametrisation to the star parameters
        star_name = list(self.paramcontainers["stars"].keys())[0]
        self.paramcontainers["stars"][star_name].v0.main = True
        (self.paramcontainers["stars"][star_name].
         init_RVdrift_parameters)(with_RVdrift=with_RVdrift, RVdrift_order=RVdrift_order)

        # Apply the parametrisation to the planets parameters
        for planet_name in list(self.paramcontainers["planets"].keys()):
            self.paramcontainers["planets"][planet_name].secosw.main = True
            self.paramcontainers["planets"][planet_name].sesinw.main = True
            self.paramcontainers["planets"][planet_name].P.main = True
            self.paramcontainers["planets"][planet_name].K.main = True
            self.paramcontainers["planets"][planet_name].tc.main = True

        # Apply the parametrisation to the RV instrument models parameters
        self.instmodel_RV_parametrisation(DeltaRV_main=with_DeltaRV)

    def apply_LC_EXOFAST_param(self, with_OOT_var=False, OOT_var_order=1):
        """Apply the parametrisation for the fit of LC only.

        Apply the parametrisation for Radial Velocity data described in Eastman, J., et
         al., 2013, Publications of the Astronomical Society of the Pacific, Volume 125, Number 923.
        As this parametrisation should be applied only to a GravGroup with one star and one or more
        planets, the function chack first that the GravGroup is compliant.
        """
        # Check that there is just 1 star
        self.__check_only1star()

        # Check that there is at least 1 planet
        self.__check_atleast1planet()

        # Check that the instrument category of all the datasets is "RV" otherwise raise a warning
        self.__check_dataset_instcat(["LC", ])

        # Init and Fill the dictionary parametrisation_kwargs
        self.__parametrisation_kwargs = {}
        self.__parametrisation_kwargs["with_OOT_var"] = with_OOT_var
        self.__parametrisation_kwargs["OOT_var_order"] = OOT_var_order

        # Apply the parametrisation to the planets parameters
        for planet_name in list(self.paramcontainers["planets"].keys()):
            self.paramcontainers["planets"][planet_name].Rrat.main = True
            self.paramcontainers["planets"][planet_name].P.main = True
            self.paramcontainers["planets"][planet_name].tc.main = True
            self.paramcontainers["planets"][planet_name].aR.main = True
            self.paramcontainers["planets"][planet_name].cosinc.main = True
            self.paramcontainers["planets"][planet_name].secosw.main = True
            self.paramcontainers["planets"][planet_name].sesinw.main = True

        # Apply the parametrisation to the LC instrument models parameters
        self.instmodel_LC_parametrisation(with_OOT_var=with_OOT_var, OOT_var_order=OOT_var_order)

        # Apply the parametrisation to the Limb darkening models parameters
        self.limbdarkening_parametrisation()

    def apply_RV_LC_EXOFAST_param(self, with_DeltaRV=False, with_RVdrift=False, RVdrift_order=1,
                                  with_OOT_var=False, OOT_var_order=1):
        """Apply the parametrisation for the fit of LC and RV.

        Apply the parametrisation for Radial Velocity and Transit data described in Eastman, J., et
         al., 2013, Publications of the Astronomical Society of the Pacific, Volume 125, Number 923.
        As this parametrisation should be applied only to a GravGroup with one star and one or more
        planets, the function chack first that the GravGroup is compliant.
        """
        # Check that there is just 1 star
        self.__check_only1star()

        # Check that there is at least 1 planet
        self.__check_atleast1planet()

        # Check that the instrument categories of all the datasets are "RV" or "LC" otherwise raise
        # a warning
        self.__check_dataset_instcat(["RV", "LC"])

        # Init and Fill the dictionary parametrisation_kwargs (Important to reconstruct from pickle)
        self.__parametrisation_kwargs = {}
        self.__parametrisation_kwargs["with_DeltaRV"] = with_DeltaRV
        self.__parametrisation_kwargs["with_RVdrift"] = with_RVdrift
        self.__parametrisation_kwargs["RVdrift_order"] = RVdrift_order
        self.__parametrisation_kwargs["with_OOT_var"] = with_OOT_var
        self.__parametrisation_kwargs["OOT_var_order"] = OOT_var_order

        # Apply the parametrisation to the star parameters
        star_name = list(self.paramcontainers["stars"].keys())[0]
        self.paramcontainers["stars"][star_name].v0.main = True
        (self.paramcontainers["stars"][star_name].
         init_RVdrift_parameters)(with_RVdrift=with_RVdrift, RVdrift_order=RVdrift_order)
        # Apply the parametrisation to the planets parameters
        for planet_name in list(self.planets.keys()):
            self.paramcontainers["planets"][planet_name].Rrat.main = True
            self.paramcontainers["planets"][planet_name].secosw.main = True
            self.paramcontainers["planets"][planet_name].sesinw.main = True
            self.paramcontainers["planets"][planet_name].P.main = True
            self.paramcontainers["planets"][planet_name].K.main = True
            self.paramcontainers["planets"][planet_name].tc.main = True
            self.paramcontainers["planets"][planet_name].cosinc.main = True
            self.paramcontainers["planets"][planet_name].aR.main = True

        # Apply the parametrisation to the RV instrument models parameters
        self.instmodel_RV_parametrisation(DeltaRV_main=with_DeltaRV)

        # Apply the parametrisation to the LC instrument models parameters
        self.instmodel_LC_parametrisation(with_OOT_var=with_OOT_var, OOT_var_order=OOT_var_order)

        # Apply the parametrisation to the Limb darkening models parameters
        self.limbdarkening_parametrisation()

    def __check_only1star(self):
        """Raise an error if there is more than 1 star in the gravgroup."""
        if self.nb_of_paramcontainers["stars"] != 1:
            raise ValueError("The RV_LC_EXOFAST parametrisation can only be applied to gravgroups "
                             "with exactly 1 star. This gravgroups has {} star(s)."
                             "".format(self.nb_of_paramcontainers["stars"]))

    def __check_atleast1planet(self):
        """Raise an error if there is more than 1 star in the gravgroup."""
        if self.nb_of_paramcontainers["planets"] < 1:
            raise ValueError("The RV_LC_EXOFAST parametrisation can only be applied to gravgroups "
                             "with at least 1 planet. This gravgroups has {} planet(s)."
                             "".format(self.nb_of_paramcontainers["planets"]))

    def __check_dataset_instcat(self, l_instcat_expected):
        """Raise aa warning if the instrument categories of the dataset are not as expected."""
        if Counter(self.dataset_db.inst_categories) != Counter(l_instcat_expected):
            raise ValueError("You are using a paprametrisation that has been defined to fit {}"
                             "but you have to analyse {}."
                             "".format(l_instcat_expected, self.dataset_db.inst_categories))

    def instmodel_RV_parametrisation(self, DeltaRV_main=False):
        """Make all the jitter arguments of all the RV instrument models main parameters."""
        if DeltaRV_main:
            RVrefglobal_instname = self.RV_globalref_instname
            RVrefglobal_modname = self.get_RVref4inst_modname(RVrefglobal_instname)
        list_instmodel = self.get_instmodel_objs(inst_cat="RV")
        for inst_model in list_instmodel:
            inst_name = inst_model.instrument.name
            inst_model.DeltaRV.main = DeltaRV_main
            if DeltaRV_main:
                if (inst_name == RVrefglobal_instname) and (inst_model.name == RVrefglobal_modname):
                    inst_model.DeltaRV.free = False
                    inst_model.DeltaRV.value = 0.0

    def instmodel_LC_parametrisation(self, with_OOT_var=False, OOT_var_order=1):
        """Make all the DeltaOOT arguments of all the LC instrument models main parameters."""
        list_instmodel = self.get_instmodel_objs(inst_cat="LC")
        for inst_model in list_instmodel:
            inst_model.init_OOT_var_parameters(with_OOT_var=with_OOT_var,
                                               OOT_var_order=OOT_var_order)

    def limbdarkening_parametrisation(self):
        """Make all the parameters of all the Limb Darkening param containers main parameters."""
        for LD_parcont in self.get_list_LD_parconts():
            for param in LD_parcont.get_list_params():
                param.main = True
