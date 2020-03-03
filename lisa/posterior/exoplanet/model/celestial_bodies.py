#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Gravitational group (gravgroup) module.

The objective of this module is to define the CelestialBody, Star and Planet class.

@TODO:
"""
from logging import getLogger

from ...core.parameter import Parameter
from ...core.paramcontainer import Core_ParamContainer

## Logger object
logger = getLogger()


class CelestialBody(Core_ParamContainer):
    """docstring for CelestialBody."""

    __category__ = "celestialbodies"

    def __init__(self, gravgroup=None, name="", **kwargs):
        """docstring GravGroup init method.

        :param Gravgroup gravgroup: (default: None), Gravgroup instance to which the star belongs.
        :param str name: (default: ""), Name of the star (if the star is K2-19_A, its name will be
            'A' and 'K2-19' would be the name of the GravGroup)

        Keyword arguments are passed to Core_Paramcontainer.__init__ (see docstring for more info).
        Only name_prefix should not be provided as arguments, since it set automatically to gravgroup.name
        """
        # name_prefix is set to None because it will be set when the gravgroup is set.
        if "name_prefix" in kwargs:
            raise TypeError("'name_prefix' is an invalid keyword argument for this function. "
                            "name_prefix is automatically set as gravgroup.name if gravgroup is"
                            "provided")
        super(CelestialBody, self).__init__(name=name, **kwargs)
        # Set the gravgroup attribute
        self.gravgroup = gravgroup
        # Make CelestialBody not instanciable (abstract class)
        if type(self) is CelestialBody:
            raise NotImplementedError("CelestialBody should not be instanciated !")

    @property
    def gravgroup(self):
        """Return the GravGroup instance to which the Celestial Body belongs."""
        return self.__gravgroup

    @gravgroup.setter
    def gravgroup(self, gravgroup):
        """Set the gravgroup attribute of a CelestialBody."""
        if self.hasgravgroup:
            logger.warning("The GravGroup to which the Celestial body belongs has already been "
                           "defined. One should not redefined it so set_gravgroup command is "
                           "ignored")
        else:
            if gravgroup is None:
                logger.debug("No Gravgroup provided for CelestialBody {}.".format(self.get_name()))
            else:
                self.__gravgroup = gravgroup
                self.name.prefix = gravgroup.name
                logger.debug("gravgroup of CelestialBody {} set to {}."
                             "".format(self.get_name(), gravgroup.get_name()))

    @property
    def hasgravgroup(self):
        """Indicate if a CelestialBody instance has a attibute gravgroup defined."""
        if hasattr(self, "gravgroup"):
            return self.gravgroup is not None
        else:
            return False


class Planet(CelestialBody):
    """docstring for Planet."""

    __category__ = "planets"

    def __init__(self, gravgroup=None, name="", **kwargs):
        """docstring Planet init method.

        :param Gravgroup gravgroup: (default: None), Gravgroup instance to which the star belongs.
        :param str name: (default: ""), Name of the star (if the star is K2-19_b, its name will be
            'b' and 'K2-19' would be the name of the GravGroup)

        Keyword arguments are passed to Core_Paramcontainer.__init__ (see docstring for more info).
        Only name_prefix should not be provided as arguments, since it set automatically to gravgroup.name
        """
        super(Planet, self).__init__(gravgroup=gravgroup, name=name, **kwargs)
        ## Radius of the planet
        self.add_parameter(Parameter(name="R", name_prefix=self.name, main=False))
        ## Mass of the planet
        self.add_parameter(Parameter(name="M", name_prefix=self.name, main=False))
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
        ## Excentricity
        self.add_parameter(Parameter(name="ecc", name_prefix=self.name, main=False, unit="w/o unit"))
        ## Inclination
        self.add_parameter(Parameter(name="inc", name_prefix=self.name, main=False))
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
        ## transit times
        self.transit_times = {}


class Star(CelestialBody):
    """docstring for Star.

    The idea is to have a class attribute for every parameters that we could want to output (not
    only a non redundant set of parameters)
    """

    __category__ = "stars"
    __RVdrift_basename__ = "RVdrift"

    def __init__(self, gravgroup=None, name="", **kwargs):
        """docstring Planet init method.

        :param Gravgroup gravgroup: (default: None), Gravgroup instance to which the star belongs.
        :param str name: (default: ""), Name of the star (if the star is K2-19_A, its name will be
            'A' and 'K2-19' would be the name of the GravGroup)

        Keyword arguments are passed to Core_Paramcontainer.__init__ (see docstring for more info).
        Only name_prefix should not be provided as arguments, since it set automatically to gravgroup.name
        """
        super(Star, self).__init__(gravgroup, name, **kwargs)
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
        self.add_parameter(Parameter(name="Teff", name_prefix=self.name, main=False))
        ## Distance to observer
        self.add_parameter(Parameter(name="dist", name_prefix=self.name, main=False))
        ## Extinction E(B-V)
        self.add_parameter(Parameter(name="ebmv", name_prefix=self.name, main=False))
        ## Proper motion radial velocity contribution
        self.add_parameter(Parameter(name="v0", name_prefix=self.name, main=False))
        ## drift in the radial velocity signal
        self.add_parameter(Parameter(name="drift", name_prefix=self.name, main=False))
        ## Mean Luminosity
        self.add_parameter(Parameter(name="L", name_prefix=self.name, main=False))
        ## Mean Magnitude
        self.add_parameter(Parameter(name="mag", name_prefix=self.name, main=False))
        ## Mean Flux
        self.add_parameter(Parameter(name="F", name_prefix=self.name, main=False))
        ## Metallicity
        self.add_parameter(Parameter(name="feh", name_prefix=self.name, main=False))

    def init_RVdrift_parameters(self, with_RVdrift=False, RVdrift_order=1):
        """Initialise/Create the required parameter for the modelling of the RV_drift."""
        self.__with_RVdrift = with_RVdrift
        self.__RVdrift_order = RVdrift_order
        if with_RVdrift:
            if isinstance(RVdrift_order, int) and RVdrift_order >= 1:
                for order in range(1, RVdrift_order + 1):
                    self.add_parameter(Parameter(name=(self.get_RVdrift_param_name(order)),
                                                 name_prefix=self.name,
                                                 main=True,
                                                 unit="[K].s^(-{})".format(order)))
            else:
                raise ValueError("If you want to model an RV drift you need to "
                                 "provide an RVdrift_order that above 1 !")

    @property
    def with_RVdrift(self):
        """True if the stellar model includes an RV drift."""
        try:
            return self.__with_RVdrift
        except:
            return False

    @property
    def RVdrift_order(self):
        """Return the order of the RV drift model or None, if it's not modeled."""
        if self.with_RVdrift:
            return self.__RVdrift_order
        else:
            return None

    def get_RVdrift_param_name(self, order):
        """Return the parameter name of the coefficient of the RV drift model."""
        return "{}{}".format(self.__RVdrift_basename__, order)
