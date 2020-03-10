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

import astropy.constants as cst
import astropy.units as uu
from logging import getLogger

# from IPython import get_ipython
from numpy import pi


logger = getLogger()

# http://maia.usno.navy.mil/NSFA/IAU2009_consts.html  SI
spyr = 3.155815e7
g = cst.G.value
au = cst.au.value
gm = 1.32712440041e20
msun = gm / g
mjup = cst.M_jup.value  # msun/msunjup
msunjup = msun / mjup
mearth = cst.M_earth.value  # 5.9742e27 was wrong
Teffsun = ((cst.L_sun / (cst.sigma_sb * 4 * pi * cst.R_sun**2))**(1 / 4.)).value

rsun = cst.R_sun.value
rjup = cst.R_jup.value
rearth = cst.R_earth.value

densun = 1.409  # g/cm^3
denjup = 1.33  # g/cm^3

grav = cst.G.cgs.value  # g in  cgs


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
    :return float/np.ndarray Rp: Planetary radius in jupiter radius by default (Rsfact and Rpfact)
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


def getaoverr(P, rhostar):
    """Return the a over Rstar.

    :param float/np.ndarray P: Planetary orbital period in days
    :param float/np.ndarray rhostar: Density of the star from transit in solar density
    :return float/np.ndarray aR: Planetary orbital semi-major axis over stellar radius without unit
    """
    Ps = P * 24. * 3600.0  # change P to seconds for SI
    return ((rhostar * gm * Ps**2. / (4. * np.pi**2.)))**(1.0 / 3.0) / rsun


def getaoverr_fromRstar(a, Rstar):
    """Return the a over Rstar.

    :param float/np.ndarray a: Planetary orbital semi-major axis in au.
    :param float/np.ndarray Rstar: Stellar radius in solar radius
    :return float/np.ndarray aR: Planetary orbital semi-major axis over stellar radius without unit
    """
    return a * au / (Rstar * rsun)


def getaoverr_fromspec(loggstar, P, Rstar):
    """Return the stellar density from the transit.

    :param float/np.ndarray loggstar: log g of the star (log10 of the cgs value of g)
    :param float/np.ndarray P: Planetary orbital period in days
    :param float/np.ndarray Rstar: Radius of the star in Sun radii
    :return float/np.ndarray aR: Planetary orbital semi-major axis over stellar radius without unit
    """
    Ps = P * 24. * 3600.0  # change P to seconds for SI
    return ((Ps**2 * 10**(loggstar)) / (4 * np.pi**2 * Rstar * rsun * 100))**(1.0 / 3.0)

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
    surgp = (np.sqrt(1 - ecc**2.) * velocity * 2. * np.pi * ar**2. / (P * np.sin(np.deg2rad(inc)) * rp**2.))
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


def getecc(ecosw, esinw):
    """Get eccentricity from e.cos(omega) and e.sin(omega).

    :param np.array/float ecosw: eccentricity.cos(omega)
    :param np.array/float esinw: eccentricity.sin(omega)
    """
    return np.sqrt(ecosw**2 + esinw**2)


def getecc_fast(ecosw, esinw):
    """Get eccentricity from e.cos(omega) and e.sin(omega).

    :param np.array/float ecosw: eccentricity.cos(omega)
    :param np.array/float esinw: eccentricity.sin(omega)
    """
    return math.sqrt(ecosw * ecosw + esinw * esinw)


def getecc_plc_4_handk(hplus, hminus, kplus, kminus):
    """Get eccentricity of c planet from h+, h-, k+, k-.

    :param np.array/float hplus: (Pb/Pc)**2/3 * e_b * cos(omega_b) + e_c * cos(omega_c)
    :param np.array/float hminus: (Pb/Pc)**2/3 * e_b * cos(omega_b) - e_c * cos(omega_c)
    :param np.array/float kplus: (Pb/Pc)**2/3 * e_b * sin(omega_b) + e_c * sin(omega_c)
    :param np.array/float kminus: (Pb/Pc)**2/3 * e_b * sin(omega_b) - e_c * sin(omega_c)
    :return float e_c: eccentricity of the planet c [0, 1]
    """
    return np.sqrt(((hplus - hminus)**2 / 4) + ((kplus - kminus)**2 / 4))


def getecc_plc_4_handk_fast(hplus, hminus, kplus, kminus):
    """Get eccentricity of c planet from h+, h-, k+, k-.

    :param float hplus: (Pb/Pc)**2/3 * e_b * cos(omega_b) + e_c * cos(omega_c)
    :param float hminus: (Pb/Pc)**2/3 * e_b * cos(omega_b) - e_c * cos(omega_c)
    :param float kplus: (Pb/Pc)**2/3 * e_b * sin(omega_b) + e_c * sin(omega_c)
    :param float kminus: (Pb/Pc)**2/3 * e_b * sin(omega_b) - e_c * sin(omega_c)
    :return float e_c: eccentricity of the planet c [0, 1]
    """
    return math.sqrt((((hplus - hminus) * (hplus - hminus)) / 4) + (((kplus - kminus) * (kplus - kminus)) / 4))


def getecc_plb_4_handk(hplus, hminus, kplus, kminus, Pc_over_Pb):
    """Get eccentricity of b planet from h+, h-, k+, k-.

    :param np.array/float hplus: (Pb/Pc)**2/3 * e_b * cos(omega_b) + e_c * cos(omega_c)
    :param np.array/float hminus: (Pb/Pc)**2/3 * e_b * cos(omega_b) - e_c * cos(omega_c)
    :param np.array/float kplus: (Pb/Pc)**2/3 * e_b * sin(omega_b) + e_c * sin(omega_c)
    :param np.array/float kminus: (Pb/Pc)**2/3 * e_b * sin(omega_b) - e_c * sin(omega_c)
    :param np.array/float Pc_over_Pb: ratio of the orbital period of planet c over the one of planet b
    :return float e_c: eccentricity of the planet c [0, 1]
    """
    return Pc_over_Pb**(2. / 3.) * np.sqrt(((hplus + hminus)**2 / 4) + ((kplus + kminus)**2 / 4))


def getecc_plb_4_handk_fast(hplus, hminus, kplus, kminus, Pc_over_Pb):
    """Get eccentricity of b planet from h+, h-, k+, k-.

    :param float hplus: (Pb/Pc)**2/3 * e_b * cos(omega_b) + e_c * cos(omega_c)
    :param float hminus: (Pb/Pc)**2/3 * e_b * cos(omega_b) - e_c * cos(omega_c)
    :param float kplus: (Pb/Pc)**2/3 * e_b * sin(omega_b) + e_c * sin(omega_c)
    :param float kminus: (Pb/Pc)**2/3 * e_b * sin(omega_b) - e_c * sin(omega_c)
    :param float Pc_over_Pb: ratio of the orbital period of planet c over the one of planet b
    :return float e_c: eccentricity of the planet c [0, 1]
    """
    return math.pow(Pc_over_Pb, 2. / 3.) * math.sqrt((((hplus + hminus) * (hplus + hminus)) / 4) + (((kplus + kminus) * (kplus + kminus)) / 4))


def getomega(ecosw, esinw):
    """Get omego in radians from e.cos(omega) and e.sin(omega).

    :param np.array/float ecosw: eccentricity.cos(omega)
    :param np.array/float esinw: eccentricity.sin(omega)
    :return float omega: argument of periastron [-pi, pi]
    """
    return np.arctan2(esinw, ecosw)


def getomega_deg(ecosw, esinw):
    """Get omego in degrees from e.cos(omega) and e.sin(omega).

    :param np.array/float ecosw: eccentricity.cos(omega)
    :param np.array/float esinw: eccentricity.sin(omega)
    :return float omega: argument of periastron [-180, 180]
    """
    return np.rad2deg(np.arctan2(esinw, ecosw))


def getomega_fast(ecosw, esinw):
    """Get omego in radians from e.cos(omega) and e.sin(omega).

    :param np.array/float ecosw: eccentricity.cos(omega)
    :param np.array/float esinw: eccentricity.sin(omega)
    :return float omega: argument of periastron [-pi, pi]
    """
    return math.atan2(esinw, ecosw)


def getomega_deg_fast(ecosw, esinw):
    """Get omego in degrees from e.cos(omega) and e.sin(omega).

    :param np.array/float ecosw: eccentricity.cos(omega)
    :param np.array/float esinw: eccentricity.sin(omega)
    :return float omega: argument of periastron [-180, 180]
    """
    return math.degrees(math.atan2(esinw, ecosw))


def getomega_plc_4_handk(hplus, hminus, kplus, kminus):
    """Get eccentricity of c planet from h+, h-, k+, k-.

    :param float hplus: (Pb/Pc)**2/3 * e_b * cos(omega_b) + e_c * cos(omega_c)
    :param float hminus: (Pb/Pc)**2/3 * e_b * cos(omega_b) - e_c * cos(omega_c)
    :param float kplus: (Pb/Pc)**2/3 * e_b * sin(omega_b) + e_c * sin(omega_c)
    :param float kminus: (Pb/Pc)**2/3 * e_b * sin(omega_b) - e_c * sin(omega_c)
    :return float omega_c: argument of periastron for the c planet [-pi, pi]
    """
    return np.arctan2((kplus - kminus), (hplus - hminus))


def getomega_plc_4_handk_fast(hplus, hminus, kplus, kminus):
    """Get eccentricity of c planet from h+, h-, k+, k-.

    :param float hplus: (Pb/Pc)**2/3 * e_b * cos(omega_b) + e_c * cos(omega_c)
    :param float hminus: (Pb/Pc)**2/3 * e_b * cos(omega_b) - e_c * cos(omega_c)
    :param float kplus: (Pb/Pc)**2/3 * e_b * sin(omega_b) + e_c * sin(omega_c)
    :param float kminus: (Pb/Pc)**2/3 * e_b * sin(omega_b) - e_c * sin(omega_c)
    :return float omega_c: argument of periastron for the c planet  [-pi, pi]
    """
    return math.atan2((kplus - kminus), (hplus - hminus))


def getomega_plb_4_handk(hplus, hminus, kplus, kminus):
    """Get eccentricity of b planet from h+, h-, k+, k-.

    :param float hplus: (Pb/Pc)**2/3 * e_b * cos(omega_b) + e_c * cos(omega_c)
    :param float hminus: (Pb/Pc)**2/3 * e_b * cos(omega_b) - e_c * cos(omega_c)
    :param float kplus: (Pb/Pc)**2/3 * e_b * sin(omega_b) + e_c * sin(omega_c)
    :param float kminus: (Pb/Pc)**2/3 * e_b * sin(omega_b) - e_c * sin(omega_c)
    :return float omega_c: argument of periastron for the c planet [-pi, pi]
    """
    return np.arctan2((kplus + kminus), (hplus + hminus))


def getomega_plb_4_handk_fast(hplus, hminus, kplus, kminus):
    """Get eccentricity of b planet from h+, h-, k+, k-.

    :param float hplus: (Pb/Pc)**2/3 * e_b * cos(omega_b) + e_c * cos(omega_c)
    :param float hminus: (Pb/Pc)**2/3 * e_b * cos(omega_b) - e_c * cos(omega_c)
    :param float kplus: (Pb/Pc)**2/3 * e_b * sin(omega_b) + e_c * sin(omega_c)
    :param float kminus: (Pb/Pc)**2/3 * e_b * sin(omega_b) - e_c * sin(omega_c)
    :return float omega_c: argument of periastron for the c planet [-pi, pi]
    """
    return math.atan2((kplus + kminus), (hplus + hminus))


def gethplus(Pb_over_Pc, eb, ec, omegab, omegac):
    """Get hplus in a 2 planet system from eccentricities, omegas and periods.

    Follow the equation 16 of Huber, D.; et al. 2013. Science. 342(6156):331 Supplementary materials

    :param np.array/float Pb_over_Pc: ratio of the orbital period of the b planet over the one of the c planet.
    :param np.array/float eb: eccentricity of the b planet
    :param np.array/float ec: eccentricity of the c planet
    :param np.array/float omegab: argument of periastron for the b planet
    :param np.array/float omegac: argument of periastron for the c planet
    :return np.array/float hplus: hplus (see above)
    """
    return Pb_over_Pc**(2. / 3.) * eb * np.cos(omegab) + ec * np.cos(omegac)


def gethplus_fast(Pb_over_Pc, eb, ec, omegab, omegac):
    """Get hplus in a 2 planet system from eccentricities, omegas and periods.

    Follow the equation 16 of Huber, D.; et al. 2013. Science. 342(6156):331 Supplementary materials

    :param float Pb_over_Pc: ratio of the orbital period of the b planet over the one of the c planet.
    :param float eb: eccentricity of the b planet
    :param float ec: eccentricity of the c planet
    :param float omegab: argument of periastron for the b planet
    :param float omegac: argument of periastron for the c planet
    :return float hplus: hplus (see above)
    """
    return math.pow(Pb_over_Pc, 2. / 3.) * eb * math.cos(omegab) + ec * math.cos(omegac)


def gethminus(Pb_over_Pc, eb, ec, omegab, omegac):
    """Get hminus in a 2 planet system from eccentricities, omegas and periods.

    Follow the equation 15 of Huber, D.; et al. 2013. Science. 342(6156):331 Supplementary materials

    :param np.array/float Pb_over_Pc: ratio of the orbital period of the b planet over the one of the c planet.
    :param np.array/float eb: eccentricity of the b planet
    :param np.array/float ec: eccentricity of the c planet
    :param np.array/float omegab: argument of periastron for the b planet
    :param np.array/float omegac: argument of periastron for the c planet
    :return np.array/float hminus: hminus (see above)
    """
    return Pb_over_Pc**(2. / 3.) * eb * np.cos(omegab) - ec * np.cos(omegac)


def gethminus_fast(Pb_over_Pc, eb, ec, omegab, omegac):
    """Get hminus in a 2 planet system from eccentricities, omegas and periods.

    Follow the equation 15 of Huber, D.; et al. 2013. Science. 342(6156):331 Supplementary materials

    :param float Pb_over_Pc: ratio of the orbital period of the b planet over the one of the c planet.
    :param float eb: eccentricity of the b planet
    :param float ec: eccentricity of the c planet
    :param float omegab: argument of periastron for the b planet
    :param float omegac: argument of periastron for the c planet
    :return float hminus: hminus (see above)
    """
    return math.pow(Pb_over_Pc, 2. / 3.) * eb * math.cos(omegab) - ec * math.cos(omegac)


def getkplus(Pb_over_Pc, eb, ec, omegab, omegac):
    """Get kplus in a 2 planet system from eccentricities, omegas and periods.

    Follow the equation 18 of Huber, D.; et al. 2013. Science. 342(6156):331 Supplementary materials

    :param np.array/float Pb_over_Pc: ratio of the orbital period of the b planet over the one of the c planet.
    :param np.array/float eb: eccentricity of the b planet
    :param np.array/float ec: eccentricity of the c planet
    :param np.array/float omegab: argument of periastron for the b planet
    :param np.array/float omegac: argument of periastron for the c planet
    :return np.array/float kplus: kplus (see above)
    """
    return Pb_over_Pc**(2. / 3.) * eb * np.sin(omegab) + ec * np.sin(omegac)


def getkplus_fast(Pb_over_Pc, eb, ec, omegab, omegac):
    """Get kplus in a 2 planet system from eccentricities, omegas and periods.

    Follow the equation 18 of Huber, D.; et al. 2013. Science. 342(6156):331 Supplementary materials

    :param float Pb_over_Pc: ratio of the orbital period of the b planet over the one of the c planet.
    :param float eb: eccentricity of the b planet
    :param float ec: eccentricity of the c planet
    :param float omegab: argument of periastron for the b planet
    :param float omegac: argument of periastron for the c planet
    :return float kplus: kplus (see above)
    """
    return math.pow(Pb_over_Pc, 2. / 3.) * eb * math.sin(omegab) + ec * math.sin(omegac)


def getkminus(Pb_over_Pc, eb, ec, omegab, omegac):
    """Get kminus in a 2 planet system from eccentricities, omegas and periods.

    Follow the equation 15 of Huber, D.; et al. 2013. Science. 342(6156):331 Supplementary materials

    :param np.array/float Pb_over_Pc: ratio of the orbital period of the b planet over the one of the c planet.
    :param np.array/float eb: eccentricity of the b planet
    :param np.array/float ec: eccentricity of the c planet
    :param np.array/float omegab: argument of periastron for the b planet
    :param np.array/float omegac: argument of periastron for the c planet
    :return np.array/float kminus: kminus (see above)
    """
    return Pb_over_Pc**(2. / 3.) * eb * np.sin(omegab) - ec * np.sin(omegac)


def getkminus_fast(Pb_over_Pc, eb, ec, omegab, omegac):
    """Get kminus in a 2 planet system from eccentricities, omegas and periods.

    Follow the equation 15 of Huber, D.; et al. 2013. Science. 342(6156):331 Supplementary materials

    :param float Pb_over_Pc: ratio of the orbital period of the b planet over the one of the c planet.
    :param float eb: eccentricity of the b planet
    :param float ec: eccentricity of the c planet
    :param float omegab: argument of periastron for the b planet
    :param float omegac: argument of periastron for the c planet
    :return float kminus: kminus (see above)
    """
    return math.pow(Pb_over_Pc, 2. / 3.) * eb * math.sin(omegab) - ec * math.sin(omegac)


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
    :param float/np.ndarray K: Radial velocity semi-amplitude of a star associated to a planet.
        K * Kfact should be in m/s.
    :param float/np.ndarray Ms: Stellar mass in solar mass
    :param float/np.ndarray ecc: Planet orbital eccentricity
    :param float/np.ndarray Kfact: Facteur to convert the K value in meter per sec
    :return float/np.ndarray Mpsininc: Planet mass multiply by sinus of the okanetary orbital
                                       inclination in Jupiter mass
    """
    return (K * Kfact / 28.4329 * np.sqrt(1.0 - ecc**2.0) * Ms**(2.0 / 3.0) *
            (P / 365.25)**(1.0 / 3.0))


def getMpsinincoverMs23rd(P, K, ecc, units=None):
    """Return the planetary mass

    Adapted from equation 14 page 3, assuming that the planet mass in negligeable compared to the
    stellar mass
    http://exoplanets.astro.yale.edu/workshop/EPRV/Bibliography_files/Radial_Velocity.pdf

    :param float/np.ndarray P: Planetary orbital period (by default in days)
    :param float/np.ndarray K: Radial velocity semi-amplitude of a star associated to a planet (by default in m/s)
    :param float/np.ndarray ecc: Planet orbital eccentricity
    :param dict_of_units units: Dictionary providing the units of the inputs and outputs. Keys must be in
        ["P", "K", "MpsinincoverMs23rd", "output"] and values must by units from the astropy.units module. If the unit
        of a given input/output is not provided, then the default value is used.
    :return float/np.ndarray MpoverMs23rd: Mp/(Ms)**(2/3) (by default in Mjup**(1/3))
    """
    if units is None:
        units = {}
    # Define output unit as several keys can be used.
    ouput_unit_found = [key for key in ["MpsinincoverMs23rd", "MsinincoverMs23rd", "ouput"] if key in units]
    if len(ouput_unit_found) == 0:
        ouput_unit = uu.Mjup**(1 / 3)
    else:
        ouput_unit = units[ouput_unit_found[0]]
    fact = 1 * units.get("K", uu.m / uu.s) * (cst.G)**(-1. / 3.) * (4 * np.pi**2)**(-1. / 6.) * (1 * units.get("P", uu.day))**(1. / 3.)
    return (fact * K * np.sqrt(1.0 - ecc**2.0) * P**(1. / 3.)).to(ouput_unit).value


def getMp(P, K, Ms, ecc, inc, Kfact=1000):
    """Return the planetary mass

    Adapted from equation 14 page 3, assuming that the planet mass in negligeable compared to the
    stellar mass
    http://exoplanets.astro.yale.edu/workshop/EPRV/Bibliography_files/Radial_Velocity.pdf

    :param float/np.ndarray P: Planetary orbital period in days
    :param float/np.ndarray K: Radial velocity semi-amplitude of a star associated to a planet.
        K * Kfact should be in m/s.
    :param float/np.ndarray Ms: Stellar mass in solar mass
    :param float/np.ndarray ecc: Planet orbital eccentricity
    :param float/np.ndarray inc: Planet orbital inclination in degrees
    :param float/np.ndarray Kfact: Conversion factor for K
    :return float/np.ndarray Mp: Planet mass in Jupiter mass
    """
    return (K * Kfact / 28.4329 * np.sqrt(1.0 - ecc**2.0) * Ms**(2.0 / 3.0) *
            (P / 365.25)**(1.0 / 3.0)) / np.sin(np.deg2rad(inc))


def getMpoverMs23rd(P, K, ecc, inc, units=None):
    """Return the planetary mass

    Adapted from equation 14 page 3, assuming that the planet mass in negligeable compared to the
    stellar mass
    http://exoplanets.astro.yale.edu/workshop/EPRV/Bibliography_files/Radial_Velocity.pdf

    :param float/np.ndarray P: Planetary orbital period (by default in days)
    :param float/np.ndarray K: Radial velocity semi-amplitude of a star associated to a planet (by default in m/s)
    :param float/np.ndarray ecc: Planet orbital eccentricity
    :param float/np.ndarray inc: Planet orbital inclination (by default in degrees)
    :param dict_of_units units: Dictionary providing the units of the inputs and outputs. Keys must be in
        ["P", "K", "inc", "MpoverMs23rd", "output"] and values must by units from the astropy.units module. If the unit
        of a given input/output is not provided, then the default value is used.
    :return float/np.ndarray MpoverMs23rd: Mp/(Ms)**(2/3) (by default in Mjup**(1/3))
    """
    if units is None:
        units = {}
    # Define output unit as several keys can be used.
    ouput_unit_found = [key for key in ["MpoverMs23rd", "MoverMs23rd", "ouput"] if key in units]
    if len(ouput_unit_found) == 0:
        ouput_unit = uu.Mjup**(1 / 3)
    else:
        ouput_unit = units[ouput_unit_found[0]]
    fact = 1 * units.get("K", uu.m / uu.s) * (cst.G)**(-1. / 3.) * (4 * np.pi**2)**(-1. / 6.) * (1 * units.get("P", uu.day))**(1. / 3.)
    return (fact * K * np.sqrt(1.0 - ecc**2.0) * P**(1. / 3.) /
            np.sin((inc * units.get("inc", uu.deg)).to(uu.rad).value)).to(ouput_unit).value


def gettp(P, tc, ecosw, esinw):
    """Returns tp (time of periastron passage) of the body (star or planet).

    :param numpy.ndarray P: period in [time unit]
    :param numpy.ndarray tc: time of conjonction of the planet in [time unit]
    :param np.array/float ecosw: eccentricity.cos(omega)
    :param np.array/float esinw: eccentricity.sin(omega)
    :param numpy.ndarray omega: argument of periastron in radian

    """
    omega = getomega(ecosw, esinw)
    ecc = getecc(ecosw, esinw)
    f = pi * 0.5 - omega
    E = 2.0 * np.arctan2(np.tan(f / 2.0) * np.sqrt((1.0 - ecc)), np.sqrt((1.0 + ecc)))
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
    E = 2.0 * math.atan2(math.tan(f / 2.0) * math.sqrt((1.0 - ecc)), math.sqrt((1.0 + ecc)))
    mshift = E - ecc * math.sin(E)
    return tc - P * mshift / (2.0 * pi)


def get_meanA(P, tc, treference, ecosw, esinw):
    """Returns the mean anomaly in radians for a specific reference time given the transit time

    :param numpy.ndarray P: period in [time unit]
    :param numpy.ndarray tc: time of conjonction of the planet in [time unit]
    :param numpy.ndarray treference: time for which we want the mean anomaly  [time unit]
    :param np.array/float ecosw: eccentricity.cos(omega)
    :param np.array/float esinw: eccentricity.sin(omega)

    TODO: check if works well
    """
    omega = getomega(ecosw, esinw)
    ecc = getecc(ecosw, esinw)
    f = pi * 0.5 - omega
    E = 2.0 * np.arctan2(np.tan(f / 2.0) * np.sqrt((1.0 - ecc)), np.sqrt((1.0 + ecc)))
    mshift = E - ecc * np.sin(E)
    meananomaly = 2.0 * pi * ((treference - tc) / P) + mshift
    return meananomaly % 2.0 * pi


def getTeqpl(Teffst, aR, ecc, A=0, f=1 / 4.):
    """Return the planet equilibrium temperature.

    Relation adapted from equation 4 page 4 in http://www.mpia.de/homes/ppvi/chapter/madhusudhan.pdf
    and https://en.wikipedia.org/wiki/Stefan%E2%80%93Boltzmann_law
    and later updated to include the effect of excentricity on the average stellar planet distance
    according to equation 5 p 25 of Laughlin & Lissauer 2015arXiv150105685L (1501.05685)
    Plus Exoplanet atmospheres, physical processes, Sara Seager, p30 eq 3.9 for f contribution.

    :param float/np.ndarray Teffst: Effective temperature of the star
    :param float/np.ndarray aR: Ration of the planetary orbital semi-major axis over the stellar
        radius (without unit)
    :param float/np.ndarray A: Bond albedo (should be between 0 and 1)
    :param float/np.ndarray f: Redistribution factor. If 1/4 the energy is uniformly redistributed
        over the planetary surface. If f = 2/3, no redistribution at all, the atmosphere immediately
        reradiate whithout advection.
    :return float/np.ndarray Teqpl: Equilibrium temperature of the planet
    """
    return Teffst * (f * (1 - A))**(1 / 4.) * np.sqrt(1 / aR) / (1 - ecc**2)**(1 / 8.)


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
    rgas = 8.3144621  # The gas constant (also known as the molar, universal, or ideal gas constant, J⋅mol−1⋅K−1
    gra = (g * Mp * mjup) / (Rp * rjup)**2.

    h = (rgas * Teqpl) / (mu * gra)
    return Hfact * h / 1e3


def getLs(Rs, Teffst, Lfact=1.):
    """Return the stellar luminosity.

    https://exoplanetarchive.ipac.caltech.edu/docs/poet_calculations.html

    :param float/np.ndarray Rs: Radius of the star (in sun radius)
    :param float/np.ndarray Teffst: Effective temperature of the star (in K)
    :param float Lfact: Multiplicative factor for unit purposes (if !=1 watch out units)

    :return float/np.ndarray Ls: Luminosity of the star (in solar luminosity)
    """
    return Lfact * Rs**2 * (Teffst / Teffsun)**4


def getFi(Ls, a, Fifact=1.):
    """Return the insolation flux at the planetary surface.

    https://exoplanetarchive.ipac.caltech.edu/docs/poet_calculations.html

    :param float/np.ndarray Ls: Luminosity of the star (in solar luminosity)
    :param float/np.ndarray a: semi-major axis (in au)
    :param float Fifact: Multiplicative factor for unit purposes (if !=1 watch out units)

    :return float/np.ndarray Fi: Insolation flux (in earth insolation flux)
    """
    return Fifact * Ls / a**2


def getRstar(rho, M, Rfact=1.):
    """Return the stellar radius.

    :param float/np.ndarray rho: Stellar density (in solar density)
    :param float/np.ndarray M: Stellar mass (in solar mass)
    :param float Rfact: Multiplicative factor for unit purposes (if !=1 watch out units)

    :return float/np.ndarray R: Stellar radius (in solar radius if Rfact=1)
    """
    return Rfact * (M / rho)**(1. / 3)


def getloggpl(M, R):
    """Return the planetary log(g).

    :param float/np.ndarray M: Planetary mass (in jupiter mass)
    :param float/np.ndarray R: Planetary radius (in jupiter radius)

    :return float/np.ndarray loggpl: Planetary logg
    """
    # mjup in kg and rjup in m
    return np.log10(grav * M * mjup * 1000 / np.power(R * rjup * 100, 2))


def getgpl(M, R):
    """Return the planetary surface gravity.

    :param float/np.ndarray M: Planetary mass (in jupiter mass)
    :param float/np.ndarray R: Planetary radius (in jupiter radius)

    :return float/np.ndarray gpl: Planetary surface gravity (im m.s-2)
    """
    return cst.G.value * M * mjup / np.power(R * rjup, 2)


def getM_4_E(E, ecc):
    """Return the Mean anomalie from eccentric anomalie and eccentricity.

    This function works with numpy arrays as arguments.

    :param float/np.array E: Eccentric anomaly in radians
    :param float/np.array ecc: Eccentricity [0, 1]
    :param float/np.array M: Mean anomaly in radians
    """
    return E - ecc * np.sin(E)


def getM_4_E_fast(E, ecc):
    """Return the Mean anomalie from eccentric anomalie and eccentricity.

    This function works only with floats as arguments.

    :param float E: Eccentric anomaly in radians
    :param float ecc: Eccentricity [0, 1]
    :param float M: Mean anomaly in radians
    """
    return E - ecc * math.sin(E)


def getM_4_f(f, ecc, positive=True):
    """Compute mean anomaly from true anomaly and eccentricity.

    This function works with numpy arrays as arguments.

    :param float/np.array f: true anomaly in radians
    :param float/np.array ecc: eccentricity
    :param float/np.array positive: if True, the result is in [0, 2.pi], else in [-pi, pi].
    :return float/np.array m: mean anomaly in radians
    """
    E = getE_4_f(f, ecc, positive)  # eccentric anomaly
    return getM_4_E(E, ecc)  # mean anomalie


def getM_4_f_fast(f, ecc):
    """Compute mean anomaly from true anomaly and eccentricity.

    This function works with numpy arrays as arguments.

    :param f: true anomaly in radians
    :param ecc: eccentricity
    :return m: mean anomaly in radians in [-pi, pi]
    """
    ee = getE_4_f_fast(f, ecc)  # eccentric anomaly
    return getM_4_E_fast(ee, ecc)  # mean anomalie


def getM_4_f_fast_positive(f, ecc):
    """Compute mean anomaly from true anomaly and eccentricity.

    This function works with numpy arrays as arguments.

    :param f: true anomaly in radians
    :param ecc: eccentricity
    :return m: mean anomaly in radians in [0, 2.pi]
    """
    ee = getE_4_f_fast_positive(f, ecc)  # eccentric anomaly
    return getM_4_E_fast(ee, ecc)  # mean anomalie


def getE_4_f(f, ecc, positive=True):
    """Compute eccentric anomaly from true anomaly and eccentricity.

    This function works with numpy arrays as arguments and eccentricity.

    :param float/np.array f: true anomaly in radians
    :param float/np.array ecc: eccentricity [0, 1]
    :param float/np.array positive: if True, the result is in [0, 2.pi], else in [-pi, pi].
    :return float/np.array ee: eccentric anomaly in radians
    """
    ee = 2 * np.arctan2(np.tan(f / 2) * np.sqrt((1 - ecc)), np.sqrt((1 + ecc)))  # eccentric anomaly
    if ee < 0 and positive:
        return 2 * np.pi + ee
    else:
        return ee


def getE_4_f_fast(f, ecc):
    """Compute eccentric anomaly from true anomaly and eccentricity.

    This function works only with floats as arguments.

    :param f: true anomaly in radians
    :param ecc: eccentricity [0, 1]
    :return ee: eccentric anomaly in radians in [-pi, pi].
    """
    return 2 * math.atan2(math.tan(f / 2) * math.sqrt((1 - ecc)), math.sqrt((1 + ecc)))


def getE_4_f_fast_positive(f, ecc):
    """Compute eccentric anomaly from true anomaly and eccentricity.

    This function works only with floats as arguments.

    :param f: true anomaly in radians
    :param ecc: eccentricity [0, 1]
    :return ee: eccentric anomaly in radians in [0, 2.pi].
    """
    ee = 2 * math.atan2(math.tan(f / 2) * math.sqrt((1 - ecc)), math.sqrt((1 + ecc)))
    if ee < 0:
        return 2 * np.pi + ee
    else:
        return ee


def gettic_4_Mref(M_ref, P, ecc, omega, t_ref=0.0):
    """Compute the next time of inferior conjection from the mean anomaly at a given reference time.

    :param float/np.array M_ref: Mean anomaly of the planet at the reference time (t_ref) in radians
        and between [0, 2pi]
    :param float/np.array P: period
    :param float/np.array ecc: eccentricity
    :param float/np.array omega: argument of periastron in radians
    :param float/np.array t_ref: refrence time
    :return float/np.array tic: next time of inferior conjunction after t_ref
    """
    deltat = P / (2 * pi) * (getM_4_f(pi / 2 - omega, ecc, positive=True) - M_ref)
    if deltat < 0:
        return t_ref + P + deltat
    else:
        return t_ref + deltat


def gettic_4_Mref_fast(M_ref, P, ecc, omega, t_ref=0.0):
    """Compute the next time of inferior conjection from the mean anomaly at a given reference time.

    :param float M_ref: Mean anomaly of the planet at the reference time (t_ref) in radians
        and between [0, 2pi]
    :param float P: period
    :param float ecc: eccentricity
    :param float omega: argument of periastron in radians
    :param float t_ref: refrence time
    :return float tic: next time of inferior conjunction after t_ref
    """
    deltat = P / (2 * pi) * (getM_4_f_fast_positive(pi / 2 - omega, ecc) - M_ref)
    if deltat < 0:
        return t_ref + P + deltat
    else:
        return t_ref + deltat


def getMref_4_tic(tic, P, ecc, omega, t_ref=0.0):
    """Compute the mean anomaly at a given reference time from a time of inferior conjection.

    :param float/np.array tic: Time of inferior conjunction after t_ref
    :param float/np.array P: period
    :param float/np.array ecc: eccentricity
    :param float/np.array omega: argument of periastron in radians
    :param float/np.array t_ref: refrence time
    :return float/np.array M_ref: Mean anomaly of the planet at the reference time (t_ref) in radians
        and between [0, 2pi]
    """
    return (getM_4_f(pi / 2 - omega, ecc, positive=True) - 2 * pi / P * (tic - t_ref)) % (2 * pi)


def getMref_4_tic_fast(tic, P, ecc, omega, t_ref=0.0):
    """Compute the mean anomaly at a given reference time from a time of inferior conjection.

    :param float tic: Time of inferior conjunction after t_ref
    :param float P: period
    :param float ecc: eccentricity
    :param float omega: argument of periastron in radians
    :param float t_ref: refrence time
    :return float M_ref: Mean anomaly of the planet at the reference time (t_ref) in radians
        and between [0, 2pi]
    """
    return (getM_4_f_fast_positive(pi / 2 - omega, ecc) - 2 * pi / P * (tic - t_ref)) % (2 * pi)


# if __name__ == "__main__":
#     ipython = get_ipython()
#     print("Time it for getecc(0.1, 0.2)")
#     ipython.magic("timeit getecc(0.1, 0.2)")
#     print("Time it for getecc_fast(0.1, 0.2)")
#     ipython.magic("timeit getecc_fast(0.1, 0.2)")
#     print("\nTime it for getomega(0.1, 0.2)")
#     ipython.magic("timeit getomega(0.1, 0.2)")
#     print("Time it for getomega_fast(0.1, 0.2)")
#     ipython.magic("timeit getomega_fast(0.1, 0.2)")
