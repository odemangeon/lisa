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

from IPython import get_ipython
from numpy import pi


# http://maia.usno.navy.mil/NSFA/IAU2009_consts.html  SI
spyr = 3.155815e7
g = const.G.value
au = const.au.value
gm = 1.32712440041e20
msun = gm / g
mjup = const.M_jup.value  # msun/msunjup
msunjup = msun / mjup
mearth = const.M_earth.value  # 5.9742e27 was wrong

rsun = const.R_sun.value
rjup = const.R_jup.value
rearth = const.R_earth.value

densun = 1.409  # g/cm^3
denjup = 1.33  # g/cm^3

grav = const.G.cgs.value  # g in  cgs


def geta0(per, ms, mp):
    """
    get semi-major axis in meters (SI) using kepler equation
    inputs are period in days, stellar mass in solar masses, plabet mass in jupiter masses
    call geta0( per, ms, mp )
    """
    P = per * 24. * 3600.0  # change P to seconds for SI
    a0 = ((P / (2. * np.pi))**2. * gm * (ms + mp / msunjup))**(1. / 3.)
    return a0


def getper(a0, ms, mp):
    """
    get period in days using kepler equation
    inputs are a0 in meters (SI), stellar mass in solar masses, plabet mass in jupiter masses
    call getper(a, ms,mp)
    """
    p =  (  (2. * np.pi)**2. *a0**3. /( gm * (ms + mp / msunjup) )   )**(1. / 2.)

    return p/(24. * 3600.0 )


def getb(inc, ar, ecc, omega):
    """
    get the impact parameter
    inputs are inclination, ar=a/rstar, ccentricity , omega
    call getb( inc, ar, ecc, omega )
    """
    corrfactor = (1. - ecc**2.) / (1. + ecc * np.sin(omega))
    return np.cos(np.deg2rad(inc)) * ar * corrfactor


def getrstar(ar, a0):
    """
    get radius of the star in units of rsun
    input are  ar =a/rstar and the semi-major axis in meters (SI)
    call getrstar (ar, a0)
    """
    return a0 / (ar * rsun)


def getdurkip(per, inc, ar, ecc, omega):
    """
    compute the duration with kipping formulat that has smller error in hours
    inputs are period is days, inclination,  ar =a/rstar, eccentricity , omega
    call getdurkip (per,  inc, ar, ecc, omega )
    """
    P = per * 24.  # change days to hours
    corrfactor = (1. - ecc**2.) / (1. + ecc * np.sin(omega))
    bb = getb(inc, ar, ecc, omega)
    tkip = (P * corrfactor**2. / (np.pi * np.sqrt(1. - ecc**2.)) *
            np.arcsin(np.sqrt(1. - bb**2.) / (corrfactor * ar * np.sin(np.deg2rad(inc)))))
    return tkip


def gett14(per, inc, ar, ecc, omega, rp):
    """
    compute full duration in the usual definition in hours
    # inputs are period is days, inclination,  ar =a/rstar, eccentricity , omega, rp =rp/rs,
    call gett14(per,  inc, ar, ecc, omega, rp )
    """
    P = per * 24.  # change days to hours
    corrfactor = (1. - ecc**2.) / (1. + ecc * np.sin(omega))
    bb = getb(inc, ar, ecc, omega)
    tdura = (P * corrfactor**2. / (np.pi * np.sqrt(1. - ecc**2.)) *
             np.arcsin(np.sqrt((1. + rp)**2. - bb**2.) /
                       (corrfactor * ar * np.sin(np.deg2rad(inc)))))
    return tdura


def gett12(per, inc, ar, ecc, omega, rp):
    """
    compute ingres/egress duration in the usual definition in hours
    inputs are period is days, inclination,  ar =a/rstar, eccentricity , omega, rp =rp/rs,
    call gett12(per,  inc, ar, ecc, omega, rp )
    """
    P = per * 24.  # change days to hours
    corrfactor = (1. - ecc**2.) / (1. + ecc * np.sin(omega))
    bb = getb(inc, ar, ecc, omega)
    t23 = (P * corrfactor**2. / (np.pi * np.sqrt(1. - ecc**2.)) *
           np.arcsin(np.sqrt((1. - rp)**2. - bb**2.) / (corrfactor * ar * np.sin(np.deg2rad(inc)))))
    return t23


def getdenstar(per, ar):
    """
    get the stellar density in solar values
    inputs are period in days and   ar =a/rstar
    call getdenstar(per, ar)
    """
    P = per * 24. * 3600.0  # change P to seconds for SI
    return ar**3. * 4. * np.pi**2. * rsun**3. / (gm * P**2.)


def getrpjup(rp, rstar):
    """
    get the radius of the planet in units jupiter radius
    inputs are rp =rp/rs, rstar in solar radius
    call getrpjup(rp, rstar)
    """
    return rp * rstar * rsun / rjup


def getden(m, r):
    """
    get density of planet or star in the units of mass and radius they already have
    inputs are m and radius in the same units relative as the result
    call getden( m, r)
    """
    return m / r**3.


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


def getlogg(per, ar, rstar):
    """
    get log g from ar
    inputs  per in days, ar =a/rstar rstar in solar radius
    call getlogg(per, ar, rstar )
    """
    density = getdenstar(per, ar)  # densun in cgs and rsun in meters
    loggstar = np.log10(4. * np.pi * grav / 3.) + np.log10(density * densun * rstar * rsun * 100.)
    return loggstar


def gettequ(teff, ar):
    """
    get equilibrium temperature
    inputs teff in kelvin, ar =a/rstar
    call gettequ(teff, ar)
    """
    return teff * np.sqrt(0.5 / ar)


def getcirtime(per, mstar, rstar, mp, rp):
    """
    circulisation timescale  in giga years
    inputs are per is days, mstar in sun masses, rstar in solar masses , mp in jupiter masses,
    rp =rp/rs
    this assumes the tidal factor to be 10^5 if it is 10^6 we need to multiply by 10.
    call getcirtime(per, mstar, rstar, mp, rp)
    """
    rprjup = getrpjup(rp, rstar)
    a0 = geta0(per, mstar, mp)
    # print(a0/au)
    tau5 = 0.63 * mp * ((1. / mstar)**1.5) * ((a0 / (rsun * 10.))**6.5) * ((1. / rprjup)**5.) * 0.1
    return tau5


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
    """Get omego from e.cos(omega) and e.sin(omega).

    :param np.ndarray secosw: sqrt(eccentricity).cos(omega)
    :param np.ndarray sesinw: sqrt(eccentricity).sin(omega)
    """
    return np.arctan(sesinw / secosw)


def getomega_fast(secosw, sesinw):
    """Returns omega as a float radian.

    :param float secosw: sqrt(eccentricity).cos(omega)
    :param float sesinw: sqrt(eccentricity).sin(omega)
    """
    if secosw == 0.:
        return math.copysign(math.pi / 2, sesinw)
    else:
        return math.atan(sesinw / secosw)


def getkamp(per, ms, mp, inc, ecc):
    """
    semi amplitude in meter /s
    inputs, per in days ,ms=stellar mass in msun,  mp planet mass in Jupiter masses,
    inclination in degrees, eccentricity
    from equation
    http://exoplanets.astro.yale.edu/workshop/EPRV/Bibliography_files/Radial_Velocity.pdf
    """
    return (28.4329 * mp * np.sin(np.deg2rad(inc)) * (mp / msunjup + ms)**(-2.0 / 3.0) *
            (per / 365.25)**(-1.0 / 3.0) / np.sqrt(1.0 - ecc**2.0))


def gettp(P, tc, secosw, sesinw):
    """Returns tp (time of periastron passage).

    :param numpy.ndarray P: period in [time unit]
    :param numpy.ndarray tc: time of conjonction in [time unit]
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
    """Returns tp (time of periastron passage).

    :param float P: period in [time unit]
    :param float tc: time of conjonction in [time unit]
    :param float ecc: eccentricity
    :param float omega: argument of periastron in radian

    If eccentricity is zero the code applies convention correction which is in agrement with if
    calculated through formula
    """
    # if ecc == 0.:
    #     return tc - P / 4.
    f = pi * 0.5 - omega
    E = 2.0 * math.atan(math.sqrt((1.0 - ecc) / (1.0 + ecc)) * math.tan(f / 2.0))
    mshift = E - ecc * math.sin(E)
    return tc - P * mshift / (2.0 * pi)


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
