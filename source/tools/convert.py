#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module to convert system parameters

@package tools
@ingroup convert

@brief functions to convert system parameters
@details functions to convert system parameters from normal parametrization to others and to the
physical values

@file
@author Susana Barros
@date Decembre 14, 2016
@version 1.0
@todo: to convertions to other parametrisations
    include the call to SI parameters from scipy
    for now not done because I didn't find all the values I wanted.
"""
import numpy as np
import math
# import math
# import scipy.constants as konst
# Code that converts the fitted parameters to the ones we want
# import matplotlib.pyplot as plt

import astropy.constants as const
from collections import Counter
from numbers import Number
from numpy import ndarray, stack
from numpy import random
from logging import getLogger

from IPython import get_ipython
from numpy import pi

from .human_machine_interface.standard_questions import Ask4Number, Ask4PositiveNumber
from .emcee_tools import ChainsInterpret


logger = getLogger()

# http://maia.usno.navy.mil/NSFA/IAU2009_consts.html  SI
spyr = 3.155815e7
g = const.G.value
au = const.au.value
gm = 1.32712440041e20
msun = gm / g
mjup = const.M_jup.value  # msun/msunjup
msunjup = msun / mjup
mearth = const.M_earth.value  # 5.9742e27 was wrong
Teffsun = ((const.L_sun/(const.sigma_sb * 4 * pi * const.R_sun**2))**(1/4.)).value

rsun = const.R_sun.value
rjup = const.R_jup.value
rearth = const.R_earth.value

densun = 1.409  # g/cm^3
denjup = 1.33  # g/cm^3

grav = const.G.cgs.value  # g in  cgs


def get_transit_depth(Rrat):
    """Return the transit depth.

    :param float/np.ndarray Rrat: Radius ratio

    TODO: Make relation working for grazing transit too
    """
    return np.power(Rrat, 2)


def getinc(cosinc):
    """Return the inclination of the orbit.

    :param float/np.ndarray cosinc: cosinus of the inclination
    """
    return np.rad2deg(np.arccos(cosinc))


def getRp(Rrat, Rs, Rsfact=rsun, Rpfact=rjup):
    """Return the planetary radius.


    :param float/np.ndarray Rrat: Radius ratio, planetary radius over stellar radius
    :param float/np.ndarray Rs: Stellar radius
    :param float Rsfact: Unit factor for stellar radius (optional and default solar radius in meter)
    :param float Rpfact: Unit factor for planetary radius (optional and default jupiter radius in
                         meter)
    :return float/np.ndarray Rp: Planetary radius in the same unit than Rs
    """
    return np.multiply(Rrat, Rs) * Rsfact / Rpfact


def geta(P, Ms, Mp):
    """Return semi-major axis in meters (SI) using kepler equation

    :param float/np.ndarray P: Planetary orbital period in days
    :param float/np.ndarray Ms: Stellar mass in solar mass
    :param float/np.ndarray Mp: Planetary mass in jupiter mass
    :return float/np.ndarray a: Planetary orbital semi-major axis in au
    """
    Ps = P * 24. * 3600.0  # change P to seconds for SI
    return ((Ps / (2. * np.pi))**2. * gm * (Ms + Mp / msunjup))**(1. / 3.) / au


def getP(a, Ms, Mp):
    """Return planetary orbital period in days using kepler equation

    :param float/np.ndarray a: Planetary orbital semi-major axis in meters
    :param float/np.ndarray Ms: Stellar mass in solar mass
    :param float/np.ndarray Mp: Planetary mass in jupiter mass
    :return float/np.ndarray P: Planetary orbital period in days
    """
    P = ((2. * np.pi)**2. * a**3. / (gm * (Ms + Mp / msunjup)))**(1. / 2.)
    return P / (24. * 3600.0)


def getb(inc, aR, ecc, omega):
    """Return the impact parameter

    See Kipping 2011 (PhD thesis) p. 55, eq. 3.26

    :param float/np.ndarray inc: Planetary orbital inclination in degrees
    :param float/np.ndarray aR: Planetary orbital semi-major axis over stellar radius without unit
    :param float/np.ndarray ecc: Planetary orbital eccentricity without unit
    :param float/np.ndarray omega: Stellar argument of periastron associated to the planet orbital
                                   in degrees
    :return float/np.ndarray b: Planetary orbital impact parameter without unit
    """
    corrfactor = (1. - ecc**2.) / (1. + ecc * np.sin(omega))
    return np.cos(np.deg2rad(inc)) * aR * corrfactor


def getRs(aR, a):
    """Return stellar radius

    :param float/np.ndarray aR: Planetary orbital semi-major axis over stellar radius without unit
    :param float/np.ndarray a: Planetary orbital semi-major axis in meters (SI)
    :return float/np.ndarray Rs: Stellar radius in solar radius
    """
    return a / (aR * rsun)


def getdurkip(per, inc, ar, ecc, omega):
    """
    compute the duration with kipping formulat that has smaller error in hours
    inputs are period is days, inclination,  ar =a/rstar, eccentricity , omega
    call getdurkip (per,  inc, ar, ecc, omega )
    """
    P = per * 24.  # change days to hours
    corrfactor = (1. - ecc**2.) / (1. + ecc * np.sin(omega))
    bb = getb(inc, ar, ecc, omega)
    tkip = (P * corrfactor**2. / (np.pi * np.sqrt(1. - ecc**2.)) *
            np.arcsin(np.sqrt(1. - bb**2.) / (corrfactor * ar * np.sin(np.deg2rad(inc)))))
    return tkip


def getD14(P, inc, aR, ecc, omega, Rrat):
    """Return the full transit duration.

    :param float/np.ndarray P: Planetary period in days
    :param float/np.ndarray inc: Planetary orbital inclination in degrees
    :param float/np.ndarray aR: Planetary orbital semi-major axis over stellar radius without unit
    :param float/np.ndarray ecc: Planetary orbital eccentricity without unit
    :param float/np.ndarray omega: Stellar argument of periastron associated to the planet orbital
                                   in degrees
    :param float/np.ndarray Rrat: Radius ratio (Planetary radius over stellar radius) without unit
    :return float/np.ndarray D14: full transit duration in hours
    """
    Ph = P * 24.  # change days to hours
    corrfactor = (1. - ecc**2.) / (1. + ecc * np.sin(np.deg2rad(omega)))
    b = getb(inc, aR, ecc, omega)
    return (Ph * corrfactor**2. / (np.pi * np.sqrt(1. - ecc**2.)) *
            np.arcsin(np.sqrt((1. + Rrat)**2. - b**2.) /
                      (corrfactor * aR * np.sin(np.deg2rad(inc)))))


# def gett14(P, inc, aR, ecc, omega, Rrat):
#     """
#     compute full duration in the usual definition in hours
#     # inputs are period is days, inclination,  ar =a/rstar, eccentricity , omega, rp =rp/rs,
#     call gett14(per,  inc, ar, ecc, omega, rp )
#     """
#     P = per * 24.  # change days to hours
#     corrfactor = (1. - ecc**2.) / (1. + ecc * np.sin(omega))
#     bb = getb(inc, ar, ecc, omega)
#     tdura = (P * corrfactor**2. / (np.pi * np.sqrt(1. - ecc**2.)) *
#              np.arcsin(np.sqrt((1. + rp)**2. - bb**2.) /
#                        (corrfactor * ar * np.sin(np.deg2rad(inc)))))
#     return tdura


def getD23(P, inc, aR, ecc, omega, Rrat):
    """
    compute ingres/egress duration in the usual definition in hours
    inputs are period is days, inclination,  ar =a/rstar, eccentricity , omega, rp =rp/rs,
    call getD23(per,  inc, ar, ecc, omega, rp )
    """
    Ph = P * 24.  # change days to hours
    corrfactor = (1. - ecc**2.) / (1. + ecc * np.sin(np.deg2rad(omega)))
    b = getb(inc, aR, ecc, omega)
    return (Ph * corrfactor**2. / (np.pi * np.sqrt(1. - ecc**2.)) *
            np.arcsin(np.sqrt((1. - Rrat)**2. - b**2.) /
                      (corrfactor * aR * np.sin(np.deg2rad(inc)))))


# def gett12(per, inc, ar, ecc, omega, rp):
#     """
#     compute ingres/egress duration in the usual definition in hours
#     inputs are period is days, inclination,  ar =a/rstar, eccentricity , omega, rp =rp/rs,
#     call gett12(per,  inc, ar, ecc, omega, rp )
#     """
#     P = per * 24.  # change days to hours
#     corrfactor = (1. - ecc**2.) / (1. + ecc * np.sin(omega))
#     bb = getb(inc, ar, ecc, omega)
#     t23 = (P * corrfactor**2. / (np.pi * np.sqrt(1. - ecc**2.)) *
#            np.arcsin(np.sqrt((1. - rp)**2. - bb**2.) / (corrfactor * ar * np.sin(np.deg2rad(inc)))))
#     return t23


def getrhostar(P, aR, rhofact=1):
    """Return the stellar density from the transit.

    :param float/np.ndarray P: Planetary orbital period im days
    :param float/np.ndarray aR: Planetary orbital semi-major axis over stellar radius without unit
    :param float rhofact: multiplicative factor for unit purposes
    :return float/np.ndarray rhostar: Density of the star from transit in solar density
    """
    Ps = P * 24. * 3600.0  # change P to seconds for SI
    return aR**3. * 4. * np.pi**2. * rsun**3. / (gm * Ps**2.) * rhofact


# def getrpjup(rp, rstar):
#     """
#     get the radius of the planet in units jupiter radius
#     inputs are rp =rp/rs, rstar in solar radius
#     call getrpjup(rp, rstar)
#     """
#     return rp * rstar * rsun / rjup


def getrhopl(M, R, rhofact=1):
    """Return he density of a spherical body.

    :param float/np.ndarray M: Mass of the body
    :param float/np.ndarray R: Radius of the body
    :param float/np.ndarray rhofact: multiplicative factor for unit purposes
    :return float/np.ndarray rho: density of the body in unit of mass per unit of radius cube
    """
    return rhofact * M / R**3.


def getplsurfaceg(per, ar, rp, inc, ecc, velocity):
    """
    get planet surface gravity with formulat from southworth
    Inputs are period in days , ar =a/rstar, rp =rp/rs, inclination eccentricity and velocity in
    meters second
    call getplsurfaceg(per, ar, rp, inc,  ecc, velocity )
    """
    P = per * 24. * 3600.0  # change P to seconds for SI
    # velocity in meters per second
    surgp = (np.sqrt(1 - ecc**2.) * velocity * 2. * np.pi * ar**2. /
             (P * np.sin(np.deg2rad(inc)) * rp**2.))
    return surgp


def getloggstar(P, aR, Rs):
    """Return the logg value of the star computed from the transit.

    :param float/np.ndarray P: Planetary orbital period im days
    :param float/np.ndarray aR: Planetary orbital semi-major axis over stellar radius without unit
    :param float/np.ndarray Rs: Stellar radius in solar radius
    """
    density = getrhostar(P, aR)  # densun in cgs and rsun in meters
    return np.log10(4. * np.pi * grav / 3.) + np.log10(density * densun * Rs * rsun * 100.)


def getcirctime(P, Ms, Rs, Mp, Rrat):
    """Return circulisation timescale in giga years

    This assumes the tidal factor to be 10^5 if it is 10^6 we need to multiply by 10.

    :param float/np.ndarray P: Planetary orbital period in days
    :param float/np.ndarray Ms: Stellar mass in solar mass
    :param float/np.ndarray Rs: Stellar radius in solar radius
    :param float/np.ndarray Mp: Planetary mass in jupiter radius
    :param float/np.ndarray Rrat: Radius ratio (Planetary radius over stellar radius) without unit

    call getcirtime(per, mstar, rstar, mp, rp)
    """
    Rp = getRp(Rrat, Rs, Rsfact=rsun, Rpfact=rjup)
    a = geta(P, Ms, Mp) * au
    # print(a0/au)
    return 0.63 * Mp * ((1. / Ms)**1.5) * ((a / (rsun * 10.))**6.5) * ((1. / Rp)**5.) * 0.1


def getecc(secosw, sesinw):
    """Get eccentricity from e.cos(omega) and e.sin(omega).

    This method works with np.array as input.
    """
    return secosw**2 + sesinw**2


def getecc_fast(secosw, sesinw):
    """Returns eccentricity as a float.

    :param float secosw: sqrt(eccentricity).cos(omega)
    :param float sesinw: sqrt(eccentricity).sin(omega)
    """
    return secosw * secosw + sesinw * sesinw


def getomega(secosw, sesinw):
    """Get omego in radians from e.cos(omega) and e.sin(omega).

    :param np.ndarray secosw: sqrt(eccentricity).cos(omega)
    :param np.ndarray sesinw: sqrt(eccentricity).sin(omega)
    """
    return np.arctan(sesinw / secosw)


def getomega_deg(secosw, sesinw):
    """Get omego in degrees from e.cos(omega) and e.sin(omega).

    :param np.ndarray secosw: sqrt(eccentricity).cos(omega)
    :param np.ndarray sesinw: sqrt(eccentricity).sin(omega)
    """
    return np.rad2deg(np.arctan(sesinw / secosw))


def getomega_fast(secosw, sesinw):
    """Returns omega as a float radian.

    :param float secosw: sqrt(eccentricity).cos(omega)
    :param float sesinw: sqrt(eccentricity).sin(omega)
    """
    if secosw == 0.:
        return math.copysign(math.pi / 2, sesinw)
    else:
        return math.atan(sesinw / secosw)


def getomega_deg_fast(secosw, sesinw):
    """Returns omega as a float degrees.

    :param float secosw: sqrt(eccentricity).cos(omega)
    :param float sesinw: sqrt(eccentricity).sin(omega)
    """
    if secosw == 0.:
        return math.degrees(math.copysign(math.pi / 2, sesinw))
    else:
        return math.degrees(math.atan(sesinw / secosw))


def getK(P, Ms, Mp, inc, ecc):
    """Return radial velocity semi-amplitude of a star associated to a planet

    from equation 14 page 3
        http://exoplanets.astro.yale.edu/workshop/EPRV/Bibliography_files/Radial_Velocity.pdf

    :param float/np.ndarray P: Planetary orbital period in days
    :param float/np.ndarray Ms: Stellar mass in solar mass
    :param float/np.ndarray Mp: Planet mass in Jupiter mass
    :param float/np.ndarray inc: Planet orbital inclination in degrees
    :param float/np.ndarray ecc: Planet orbital eccentricity
    :return float/np.ndarray K: Radial velocity semi-amplitude of a star associated to a planet in
                                meter per second
    """
    return (28.4329 / np.sqrt(1.0 - ecc**2.0) * Mp * np.sin(np.deg2rad(inc)) *
            (Mp / msunjup + Ms)**(-2.0 / 3.0) * (P / 365.25)**(-1.0 / 3.0))


def getMpsininc(P, K, Ms, ecc, Kfact=1000):
    """Return radial velocity semi-amplitude of a star associated to a planet

    Adapted from equation 14 page 3, assuming that the planet mass in negligeable compared to the
    stellar mass
    http://exoplanets.astro.yale.edu/workshop/EPRV/Bibliography_files/Radial_Velocity.pdf

    :param float/np.ndarray P: Planetary orbital period in days
    :param float/np.ndarray K: Radial velocity semi-amplitude of a star associated to a planet in
                               meter per second
    :param float/np.ndarray Ms: Stellar mass in solar mass
    :param float/np.ndarray ecc: Planet orbital eccentricity
    :param float/np.ndarray Kfact: Facteur to convert the K value in meter per sec
    :return float/np.ndarray Mpsininc: Planet mass multiply by sinus of the okanetary orbital
                                       inclination in Jupiter mass
    """
    return (K * Kfact / 28.4329 * np.sqrt(1.0 - ecc**2.0) * Ms**(2.0 / 3.0) *
            (P / 365.25)**(1.0 / 3.0))


def getMp(P, K, Ms, ecc, inc, Kfact=1000):
    """Return radial velocity semi-amplitude of a star associated to a planet

    Adapted from equation 14 page 3, assuming that the planet mass in negligeable compared to the
    stellar mass
    http://exoplanets.astro.yale.edu/workshop/EPRV/Bibliography_files/Radial_Velocity.pdf

    :param float/np.ndarray P: Planetary orbital period in days
    :param float/np.ndarray K: Radial velocity semi-amplitude of a star associated to a planet in
                               meter per second
    :param float/np.ndarray Ms: Stellar mass in solar mass
    :param float/np.ndarray ecc: Planet orbital eccentricity
    :param float/np.ndarray inc: Planet orbital inclination in degrees
    :return float/np.ndarray Mp: Planet mass in Jupiter mass
    """
    return (K * Kfact / 28.4329 * np.sqrt(1.0 - ecc**2.0) * Ms**(2.0 / 3.0) *
            (P / 365.25)**(1.0 / 3.0)) / np.sin(np.deg2rad(inc))


def gettp(P, tc, secosw, sesinw):
    """Returns tp (time of periastron passage) of the body (star or planet).

    :param numpy.ndarray P: period in [time unit]
    :param numpy.ndarray tc: time of conjonction of the planet in [time unit]
    :param numpy.ndarray ecc: eccentricity
    :param numpy.ndarray omega: argument of periastron in radian

    If eccentricity is zero the code applies convention correction which is in agrement with if
    calculated through formula
    """
    omega = getomega(secosw, sesinw)
    ecc = getecc(secosw, sesinw)
    f = pi * 0.5 - omega
    E = 2.0 * np.arctan(np.sqrt((1.0 - ecc) / (1.0 + ecc)) * np.tan(f / 2.0))
    mshift = E - ecc * np.sin(E)
    return tc - P * mshift / (2.0 * pi)


def gettp_fast(P, tc, ecc, omega):
    """Returns tp (time of periastron passage) of the body (star or planet).

    :param float P: period in [time unit]
    :param float tc: time of conjonction of the planet in [time unit]
    :param float ecc: eccentricity
    :param float omega: argument of periastron of the body (star or planet) in radian

    If eccentricity is zero the code applies convention correction which is in agrement with if
    calculated through formula
    """
    # if ecc == 0.:
    #     return tc - P / 4.
    f = pi * 0.5 - omega
    E = 2.0 * math.atan(math.sqrt((1.0 - ecc) / (1.0 + ecc)) * math.tan(f / 2.0))
    mshift = E - ecc * math.sin(E)
    return tc - P * mshift / (2.0 * pi)


def getTeqpl(Teffst, aR, ecc, A=0):
    """Return the planet equilibrium temperature.

    Relation adapted from equation 4 page 4 in http://www.mpia.de/homes/ppvi/chapter/madhusudhan.pdf
    and https://en.wikipedia.org/wiki/Stefan%E2%80%93Boltzmann_law
    and later updated to include the effect of excentricity on the average stellar planet distance
    according to equation 5 of Laughlin & Lissauer 2015arXiv150105685L

    :param float/np.ndarray Teffst: Effective temperature of the star
    :param float/np.ndarray Rst: Stellar radius in solar radius
    :param float/np.ndarray a: Planetary orbital semi-major axis (mean planet to star distance) in
                               au
    :return float/np.ndarray Teqpl: Equilibrium temperature of the planet
    """
    return Teffst * (1 - A)**(1 / 4.) * np.sqrt(0.5 / aR) / (1 - ecc**2)**(1/8.)

def getscaleheigh(Mp, Rp, Teqpl, mu=0.0022, Hfact=1):
    """Return the scale height of atmosphere in kilometers

    Relation obtained from Guillaume and it works for hot Jupiters

    :param float/np.ndarray mp: Planetary mass (in jupiter mass)
    :param float/np.ndarray rp: Planetary mass (in jupiter radius)
    :param float/np.ndarray Teqpl: Equilibrium temperature of the planet (K)
    :param float/np.ndarray mu: mean molecular weight kg/mol (default: 0.0022) (from guillaume)
    :param float Hfact: Multiplicative factor for unit purposes (if !=1 watch out units)

    :return float/np.ndarray scaleheight: Scale height (in km)
    """
    rgas = 8.3144621 #The gas constant (also known as the molar, universal, or ideal gas constant, J⋅mol−1⋅K−1
    gra=(g * Mp * mjup) / ( Rp * rjup)**2.

    h = (rgas * Teqpl) / (mu * gra)
    return Hfact * h/1e3


def getLs(Rs, Teffst, Lfact=1.):
    """Return the stellar luminosity.

    https://exoplanetarchive.ipac.caltech.edu/docs/poet_calculations.html

    :param float/np.ndarray Rs: Radius of the star (in sun radius)
    :param float/np.ndarray Teffst: Effective temperature of the star (in K)
    :param float Lfact: Multiplicative factor for unit purposes (if !=1 watch out units)

    :return float/np.ndarray Ls: Luminosity of the star (in solar luminosity)
    """
    return Lfact * Rs**2 * (Teffst/Teffsun)**4


def getFi(Ls, a, Fifact=1.):
    """Return the insolation flux at the planetary surface.

    https://exoplanetarchive.ipac.caltech.edu/docs/poet_calculations.html

    :param float/np.ndarray Ls: Luminosity of the star (in solar luminosity)
    :param float/np.ndarray a: semi-major axis (in au)
    :param float Fifact: Multiplicative factor for unit purposes (if !=1 watch out units)

    :return float/np.ndarray Fi: Insolation flux (in earth insolation flux)
    """
    return Fifact * Ls / a**2


def get_secondary_chains(model, chaininterpret, star_kwargs=None):
    """Return ChainInterpret isntance with the computed chain of the secondary parameters.
    """
    if Counter(["LC", "RV"]) == Counter(model.dataset_db.inst_categories):
        # Create a dictionary with the main parameter values either chain (if free) or one value
        dico_par = {}
        for param in model.get_list_params(main=True):
            if param.free:
                dico_par[param.full_name] = chaininterpret[..., param.full_name]
            else:
                dico_par[param.full_name] = param.value

        # Compute the chains for secondary parameters.
        # Initialise the results object
        l_parname_sec_chain = []
        l_parname_sec_fixed = []

        star = model.stars[list(model.stars.keys())[0]]
        # Simulate stellar Mass and radius chains if needed
        for param in [star.M, star.R, star.Teff]:
            if param.main is False:
                ask_param_value = True
                ask_param_error = True
                if param.name in star_kwargs:
                    if "value" in star_kwargs[param.name]:
                        param_value = star_kwargs[param.name]["value"]
                        ask_param_value = False
                    if "error" in star_kwargs[param.name]:
                        param_error = star_kwargs[param.name]["error"]
                        ask_param_error = False
                if ask_param_value:
                    # Ask to provide a stellar mass value
                    intitule_question = ("Enter a {} value. If you just press enter 1. solar"
                                         " mass is assumed.\n".format(param.full_name))
                    param_value, answered = Ask4Number(intitule_question, default_value=1.)
                else:
                    answered = False
                # If replied ask to provide and mass error value, otherwise assume no error
                if ask_param_error and not(ask_param_value and not(answered)):
                    intitule_question = ("Enter a {} error (1 sigma). If you just press enter "
                                         "no uncertainty is assumed.\n".format(param.full_name))
                    param_error, _ = Ask4PositiveNumber(intitule_question, default_value=0.)
                else:
                    if ask_param_value and not(answered):
                        param_error = 0.

                # if provided simulated a stellar mass chains else only give a fixed value.
                if param_error == 0.:
                    dico_par[param.full_name] = param_value
                else:
                    dico_par[param.full_name] = random.normal(loc=param_value,
                                                              scale=param_error,
                                                              size=chaininterpret.shape[:-1])

        # Iterate over planet related secondary
        for planet in model.planets.values():
            # Prepare the list of tuples secondary parameter name, function, parameters
            l_tup_planet = []
            # Transit depth
            l_tup_planet.append((planet.Trdepth.full_name, get_transit_depth,
                                 [planet.Rrat.full_name]))
            # Inclination
            l_tup_planet.append((planet.inc.full_name, getinc,
                                 [planet.cosinc.full_name]))
            # eccentricity
            l_tup_planet.append((planet.ecc.full_name, getecc,
                                 [planet.secosw.full_name, planet.sesinw.full_name]))
            # omega : argument of periastron in degrees
            l_tup_planet.append((planet.omega.full_name, getomega_deg,
                                 [planet.secosw.full_name, planet.sesinw.full_name]))
            # b: impact parameter
            l_tup_planet.append((planet.b.full_name, getb,
                                 [planet.inc.full_name, planet.aR.full_name,
                                  planet.ecc.full_name, planet.omega.full_name]))
            # Rp: planetary radius
            l_tup_planet.append((planet.R.full_name, getRp,
                                 [planet.Rrat.full_name, star.R.full_name]))
            # D14: full transit duration
            l_tup_planet.append((planet.D14.full_name, getD14,
                                 [planet.P.full_name, planet.inc.full_name, planet.aR.full_name,
                                  planet.ecc.full_name, planet.omega.full_name,
                                  planet.Rrat.full_name]))
            # D12: ingress/egress duration
            l_tup_planet.append((planet.D23.full_name, getD23,
                                 [planet.P.full_name, planet.inc.full_name, planet.aR.full_name,
                                  planet.ecc.full_name, planet.omega.full_name,
                                  planet.Rrat.full_name]))
            # Mp: Planetary mass
            l_tup_planet.append((planet.M.full_name, getMp,
                                 [planet.P.full_name, planet.K.full_name, star.M.full_name,
                                  planet.ecc.full_name, planet.inc.full_name]))
            # a: semi major axis
            l_tup_planet.append((planet.a.full_name, geta,
                                 [planet.P.full_name, star.M.full_name, planet.M.full_name]))
            # rhostar: Density of the star
            l_tup_planet.append((planet.rhostar.full_name, getrhostar,
                                 [planet.P.full_name, planet.aR.full_name]))
            # loggstar: logg of the star
            l_tup_planet.append((planet.loggstar.full_name, getloggstar,
                                 [planet.P.full_name, planet.aR.full_name, star.R.full_name]))
            # circtime: circularisation timescale of the planet
            l_tup_planet.append((planet.circtime.full_name, getcirctime,
                                 [planet.P.full_name, star.M.full_name, star.R.full_name,
                                  planet.M.full_name, planet.Rrat.full_name]))
            # rhoplanet: Density of the planet
            l_tup_planet.append((planet.rho.full_name, getrhopl,
                                 [planet.M.full_name, planet.R.full_name]))
            # Teq: Equilibrium temperature
            l_tup_planet.append((planet.Teq.full_name, getTeqpl,
                                 [star.Teff.full_name, planet.aR.full_name, planet.ecc.full_name]))

            # L: Stellar luminosity
            l_tup_planet.append((star.L.full_name, getLs,
                                 [star.R.full_name, star.Teff.full_name]))

            # Fi: Planetary insolation flux
            l_tup_planet.append((planet.Fi.full_name, getFi,
                                 [star.L.full_name, planet.a.full_name]))

            # H: Scale Height
            l_tup_planet.append((planet.H.full_name, getscaleheigh,
                                 [planet.M.full_name, planet.R.full_name, planet.Teq.full_name]))

            # Compute teh secondary parameter
            for sec_paraname, func, param_list in l_tup_planet:
                logger.debug("Computing secondary parameter: {}".format(sec_paraname))
                values = func(*[dico_par[param] for param in param_list])
                if isinstance(values, Number) or isinstance(values, ndarray):
                    dico_par[sec_paraname] = values
                    if isinstance(values, Number):
                        l_parname_sec_fixed.append(sec_paraname)
                    else:
                        if values.size == 1:
                            l_parname_sec_fixed.append(sec_paraname)
                        elif values.size > 1:
                            l_parname_sec_chain.append(sec_paraname)
                        else:
                            raise ValueError("Secondary parameter computation {} didn't return "
                                             "any result: {}".format(sec_paraname, values))
                else:
                    raise ValueError("Secondary parameter computation {} return an unexpected "
                                     "object type: {}".format(sec_paraname, type(values)))
        chainIsec = ChainsInterpret(stack([dico_par[param] for param in l_parname_sec_chain],
                                          axis=-1),
                                    l_parname_sec_chain)
        return chainIsec, l_parname_sec_chain
    else:
        raise ValueError("For now this function only handles LC and RV parametrisation.")


if __name__ == "__main__":
    ipython = get_ipython()
    print("Time it for getecc(0.1, 0.2)")
    ipython.magic("timeit getecc(0.1, 0.2)")
    print("Time it for getecc_fast(0.1, 0.2)")
    ipython.magic("timeit getecc_fast(0.1, 0.2)")
    print("\nTime it for getomega(0.1, 0.2)")
    ipython.magic("timeit getomega(0.1, 0.2)")
    print("Time it for getomega_fast(0.1, 0.2)")
    ipython.magic("timeit getomega_fast(0.1, 0.2)")
