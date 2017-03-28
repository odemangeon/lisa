#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
gp_lnlike module.

The objective of this module is to define the log likelihood in case you want to use a GP to
model the residuals.

@DONE:
    -

@TODO:
    -
"""
from logging import getLogger

from ..exoplanet_parameters import stelact_GP_noisemodel
from ..exoplanet_parameters import amp_RV, evol_timescal, periodic_timescal, period
from ...core.parameter import Parameter
from ....tools.function_w_doc import DocFunction

## logger object
logger = getLogger()


class StellarActivityGP(object):
    """docstring for StellarActivityGP.

    This is an interface class for the gravgroup class
    """

    _available_stelact_GP_types = ["ExpSquared+ExpSine"]

    @property
    def stellaract_GP_type(self):
        """Return the type of GP used to model stellar activity."""
        return self.__stellaract_GP_type

    def model_stelact_w_GP(self, gp_type="ExpSquared+ExpSine", model_RV=True, model_LC=True):
        """Function to call to model stellar activity with a GP.
        ----
        gp_type     : string, (default: ExpSquared+ExpSine")
            Type of GP to use to model the stellar activity
        model_RV    : bool, (default: True), NOT IMPLEMENTED,
            Indicate if you want to use this model for the RV
        model_LC    : bool, (default: True), NOT IMPLEMENTED,
            Indicate if you want to use this model for the LC
        """
        if gp_type in self._available_stelact_GP_types:  # Check that the gp_type is available.
            self.__stellaract_GP_type = gp_type
        else:
            raise ValueError("gp_type must be in {}. Got {}"
                             "".format(self._available_stelact_GP_types, gp_type))
        if gp_type == "ExpSquared+ExpSine":  # Create the associated parameters to the star
            star = self.stars[list(self.stars.keys())[0]]
            star.add_parameter(Parameter(name=amp_RV, name_prefix=star.full_name, main=True))
            star.add_parameter(Parameter(name=evol_timescal, name_prefix=star.full_name, main=True))
            star.add_parameter(Parameter(name=periodic_timescal, name_prefix=star.full_name,
                                         main=True))
            star.add_parameter(Parameter(name=period, name_prefix=star.full_name, main=True))
        for inst_model in self.get_list_instmodel():  # Set the noise model of the instruments
            if inst_model.instrument.category == "RV":
                if model_RV:
                    inst_model.noise_model = stelact_GP_noisemodel
            if inst_model.instrument.category == "LC":
                if model_LC:
                    inst_model.noise_model = stelact_GP_noisemodel
