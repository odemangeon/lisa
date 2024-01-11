#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Gravitational group (gravgroup) module.

The objective of this module is to define the CelestialBody, Star and Planet class.

@TODO:
"""
from loguru import logger

from numpy import rad2deg, arcsin, sqrt, pi

from ...core.parameter import Parameter
from ...core.paramcontainer import Core_ParamContainer
from ...core.model.polynomial_model import get_dico_config, set_dico_config
from ...core.model.polynomial_model import set_polymodel_parametrisation as set_polymodel_parametrisation_def


class Planet(Core_ParamContainer):
    """docstring for Planet."""

    __category__ = "planets"

    def __init__(self, name="", **kwargs):
        """docstring Planet init method.

        :param str name: (default: ""), Name of the star (if the star is K2-19_b, its name will be 'b')

        Keyword arguments are passed to Core_Paramcontainer.__init__ (see docstring for more info).
        Only name_prefix should not be provided as arguments, since it set automatically to gravgroup.name
        """
        super(Planet, self).__init__(name=name, **kwargs)
        ## Radius of the planet
        self.add_parameter(Parameter(name="R", name_prefix=self.name, main=False))
        ## Mass of the planet
        self.add_parameter(Parameter(name="M", name_prefix=self.name, main=False))
        self.add_parameter(Parameter(name="Mfromincaverage", name_prefix=self.name, main=False))
        ## Mass of the planet over (Mass of the star)**(2/3)
        self.add_parameter(Parameter(name="MoverMs23rd", name_prefix=self.name, main=False))
        ## Mass sin i of the planet
        self.add_parameter(Parameter(name="Msini", name_prefix=self.name, main=False))
        ## Mass sin i of the planet over (Mass of the star)**(2/3)
        self.add_parameter(Parameter(name="MsinioverMs23rd", name_prefix=self.name, main=False))
        ## Mean density of the planet
        self.add_parameter(Parameter(name="rho", name_prefix=self.name, main=False))
        ## Density of the star from the transit
        self.add_parameter(Parameter(name="rhostar", name_prefix=self.name, main=False))
        ## logg of the star from the transit
        self.add_parameter(Parameter(name="loggstar", name_prefix=self.name, main=False))
        ## Age of the planet
        self.add_parameter(Parameter(name="age", name_prefix=self.name, main=False))
        ## Orbital period
        self.add_parameter(Parameter(name="P", name_prefix=self.name, main=False))
        ## log Orbital period
        self.add_parameter(Parameter(name="logP", name_prefix=self.name, main=False))
        ## Semi-major axis
        self.add_parameter(Parameter(name="a", name_prefix=self.name, main=False))
        self.add_parameter(Parameter(name="afromaR", name_prefix=self.name, main=False))
        ## Periastron distance peridist
        self.add_parameter(Parameter(name="peridist", name_prefix=self.name, main=False))
        self.add_parameter(Parameter(name="peridistminusR", name_prefix=self.name, main=False))
        ## Excentricity
        self.add_parameter(Parameter(name="ecc", name_prefix=self.name, main=False, unit="w/o unit"))
        ## Inclination
        self.add_parameter(Parameter(name="inc", name_prefix=self.name, main=False))
        self.add_parameter(Parameter(name="incaverage", name_prefix=self.name, main=False, free=False, value=rad2deg(arcsin(sqrt(pi / 4)))))
        ## Cos Inclination
        self.add_parameter(Parameter(name="cosinc", name_prefix=self.name, main=False, unit="w/o unit"))
        ## Impact parameter
        self.add_parameter(Parameter(name="b", name_prefix=self.name, main=False))
        ## Argument of periastron of star (= argument of periastron of planet + pi)
        self.add_parameter(Parameter(name="omega", name_prefix=self.name, main=False))
        ## Longitude of the acending node
        self.add_parameter(Parameter(name="OMEGA", name_prefix=self.name, main=False))
        ## Mean anomaly
        self.add_parameter(Parameter(name="MeanAnomaly", name_prefix=self.name, main=False))
        ## Reference time of inferior conjunction
        self.add_parameter(Parameter(name="tic", name_prefix=self.name, main=False))
        ## Reference time of periastron passage
        self.add_parameter(Parameter(name="tp", name_prefix=self.name, main=False))
        ## Radial velocity semi-amplitude
        self.add_parameter(Parameter(name="K", name_prefix=self.name, main=False))
        ## log Radial velocity semi-amplitude
        self.add_parameter(Parameter(name="logK", name_prefix=self.name, main=False))
        ## Radius ratio planet over star
        self.add_parameter(Parameter(name="Rrat", name_prefix=self.name, main=False))
        ## Transit depth
        self.add_parameter(Parameter(name="Trdepth", name_prefix=self.name, main=False))
        ## Mass ratio planet over star
        self.add_parameter(Parameter(name="Mrat", name_prefix=self.name, main=False))
        ## a over R, ratio of semi-major axis over Radius of the host star
        self.add_parameter(Parameter(name="aR", name_prefix=self.name, main=False, unit="w/o unit"))
        ## log a over R, ratio of semi-major axis over Radius of the host star
        # self.add_parameter(Parameter(name="logaR", name_prefix=self.name, main=False))
        ## sqrt(ecc) . cos(w)
        self.add_parameter(Parameter(name="secosw", name_prefix=self.name, main=False, unit="w/o unit"))
        ## ecc . cos(w)
        self.add_parameter(Parameter(name="ecosw", name_prefix=self.name, main=False, unit="w/o unit"))
        ## sqrt(ecc) . sin(w)
        self.add_parameter(Parameter(name="sesinw", name_prefix=self.name, main=False, unit="w/o unit"))
        ## ecc . sin(w)
        self.add_parameter(Parameter(name="esinw", name_prefix=self.name, main=False, unit="w/o unit"))
        ## Transit duration D14
        self.add_parameter(Parameter(name="D14", name_prefix=self.name, main=False))
        ## Transit duration D23
        self.add_parameter(Parameter(name="D23", name_prefix=self.name, main=False))
        ## Transit duration D12
        self.add_parameter(Parameter(name="D12", name_prefix=self.name, main=False))
        ## Circularisation time
        self.add_parameter(Parameter(name="circtime", name_prefix=self.name, main=False))
        ## Teq: Equilibrium Temperature
        self.add_parameter(Parameter(name="Teq", name_prefix=self.name, main=False))
        ## Fi: insolation flux
        self.add_parameter(Parameter(name="Fi", name_prefix=self.name, main=False))
        ## H: scale height
        self.add_parameter(Parameter(name="H", name_prefix=self.name, main=False))
        ## u1: Planetary first limb-darkening parameter
        self.add_parameter(Parameter(name="u1", name_prefix=self.name, main=False))
        ## u2: Planetary second limb-darkening parameter
        self.add_parameter(Parameter(name="u2", name_prefix=self.name, main=False))
        ## xi: ratio of radiative timescale over advective timescale ))
        self.add_parameter(Parameter(name="xi", name_prefix=self.name, main=False, unit="w/o unit"))
        ## Tn: temperature of the nightside
        self.add_parameter(Parameter(name="Tn", name_prefix=self.name, main=False, unit="K"))
        ## DeltaT: Day-night temperature contrast
        self.add_parameter(Parameter(name="deltaT", name_prefix=self.name, main=False, unit="K"))
        ## Mref: Mean Anomaly at reference time
        self.add_parameter(Parameter(name="Mref", name_prefix=self.name, main=False))
        ## f: The Greenhouse factor (typically 1/sqrt(2))
        self.add_parameter(Parameter(name="f", name_prefix=self.name, main=False))
        ## hotspotoffset: Offset of the hotspot of the thermal phase curve
        self.add_parameter(Parameter(name="hotspotoffset", name_prefix=self.name, main=False))
        ## alpha: Dimensionless fluid number
        self.add_parameter(Parameter(name="alpha", name_prefix=self.name, main=False))
        ## omegadrag: Dimensionless drag frequency
        self.add_parameter(Parameter(name="omegadrag", name_prefix=self.name, main=False))
        ## AB: Bond Albedo
        self.add_parameter(Parameter(name="AB", name_prefix=self.name, main=False))
        ## c11: m=1 l=1 Spherical harmonic coefficients in the kelp thermal phasecurve model
        self.add_parameter(Parameter(name="c11", name_prefix=self.name, main=False))
        ## Frat: Flux ratio between the planet and the star
        self.add_parameter(Parameter(name="Frat", name_prefix=self.name, main=False))
        ## rpa: Ratio between the planetary radius and its orbital semi-major axis
        self.add_parameter(Parameter(name="rpa", name_prefix=self.name, main=False))
        ## transit times
        self.transit_times = {}


class Star(Core_ParamContainer):
    """docstring for Star.

    The idea is to have a class attribute for every parameters that we could want to output (not
    only a non redundant set of parameters)
    """

    __category__ = "stars"
    # __drift_basename__ = "drift"
    # __name_coeff_const_LC__ = "F0"
    # __name_coeff_const_RV__ = "v0"

    def __init__(self, name="", **kwargs):
        """docstring Planet init method.

        :param str name: (default: ""), Name of the star (if the star is K2-19_A, its name will be 'A'

        Keyword arguments are passed to Core_Paramcontainer.__init__ (see docstring for more info).
        Only name_prefix should not be provided as arguments, since it set automatically to gravgroup.name
        """
        super(Star, self).__init__(name=name, **kwargs)
        ## Radius of the star
        self.add_parameter(Parameter(name="R", name_prefix=self.name, main=False))
        ## Mass of the star
        self.add_parameter(Parameter(name="M", name_prefix=self.name, main=False))
        ## Mean density of the star
        self.add_parameter(Parameter(name="rho", name_prefix=self.name, main=False))
        ## Age of the star
        self.add_parameter(Parameter(name="age", name_prefix=self.name, main=False))
        ## logg
        self.add_parameter(Parameter(name="logg", name_prefix=self.name, main=False))
        ## Effective temperature of the star
        self.add_parameter(Parameter(name="Teff", name_prefix=self.name, main=False, unit='K'))
        ## Distance to observer
        self.add_parameter(Parameter(name="dist", name_prefix=self.name, main=False))
        ## Extinction E(B-V)
        self.add_parameter(Parameter(name="ebmv", name_prefix=self.name, main=False))
        ## Proper motion radial velocity contribution
        self.add_parameter(Parameter(name="v0", name_prefix=self.name, main=False))
        ## drift in the radial velocity signal
        # self.add_parameter(Parameter(name="drift", name_prefix=self.name, main=False))
        ## Mean Luminosity
        self.add_parameter(Parameter(name="L", name_prefix=self.name, main=False))
        ## Mean Magnitude
        self.add_parameter(Parameter(name="mag", name_prefix=self.name, main=False))
        ## Mean Flux
        self.add_parameter(Parameter(name="F", name_prefix=self.name, main=False))
        ## Metallicity
        self.add_parameter(Parameter(name="feh", name_prefix=self.name, main=False))

    def set_polymodel_parametrisation(self, inst_cat):
        """Set the parametrisation for the polynomial modelling of a given instrument category.

        Arguments
        ---------
        inst_cat    : str
            Instrument category
        """
        if inst_cat == "RV":
            name_coeff_const = "v0"
        elif inst_cat == "LC":
            name_coeff_const = "F0"
        set_polymodel_parametrisation_def(param_container=self, name_coeff_const=name_coeff_const,
                                          func_param_name=lambda order: self.get_polymodel_param_name(order=order, inst_cat=inst_cat),
                                          full_category_4_unit=inst_cat,
                                          prefix=inst_cat)

    def get_polymodel_param_name(self, order, inst_cat):
        """Return the parameter name of the coefficient of the RV drift model.

        Arguments
        ---------
        inst_cat    : str
            Instrument category
        """
        if inst_cat == "RV":
            return f"vdrift{order}"
        elif inst_cat == "LC":
            return f"Fdrift{order}"
        else:
            return f"{inst_cat}drift{order}"

    def set_dico_config_polymodel(self, inst_cat, dico_config=None):
        """Get the dictionary that configures the polynomial model for a given instrument category
        Proxy for lisa.posterior.core.model.polynomial_model.set_dico_config

        Arguments
        ---------
        inst_cat        : str
            Instrument category
        dico_config     : dict
            Updates that you might want to do to the dico that configure the polynomial model
        """
        set_dico_config(param_container=self, prefix=inst_cat, dico_config=dico_config)

    def get_dico_config_polymodel(self, inst_cat, notexist_ok=False, return_None_if_notexist=False):
        """Get the dictionary that configures the polynomial model for a given instrument category
        Proxy for lisa.posterior.core.model.polynomial_model.set_dico_config

        Arguments
        ---------
        inst_cat        : str
            Instrument category
        dico_config     : dict
            Updates that you might want to do to the dico that configure the polynomial model
        """
        return get_dico_config(param_container=self, prefix=inst_cat, notexist_ok=notexist_ok,
                               return_None_if_notexist=return_None_if_notexist)
