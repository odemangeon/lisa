#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
parametrisation_file module

The Objective of this file is to define how the parametrisation file will look like.
"""
# transit parameters
self.rp = 0.          # planet radius (in units of stellar radii)
self.ar = 0.          # semi-major axis (in units of stellar radii)
self.inc = 0.         # orbital inclination (in degrees)

'''
this will depend on how many LC data sets ..? how to set it?
'''
self.jitter_lc = 0.
self.u = [0., 0.]     # limb darkening coefficients
self.supersample = 0  # 21 supersampling factor needs to be defined for each light curve
self.exp_time = 0.5 / 24.  # if supersampling is done we need to define this for each light
# curve
# we can also calculate it but sometimes if we miss data this will be wrong

# rv parameters
self.rvsys = 0.      # radial velocity systematic velocity
self.K = 0.          # semi-amplitude
'''
this will depend on how many rv data sets ..? how to set it?
'''
self.jitter_rv = 0.

# parameters shared between transit and rv
self.ecc = 0.    # eccentricity
self.w = 0.      # longitude of periastron (in degrees)
'''
This will depend if we if we are fiting individual transit times
'''
self.t0 = 0.      # time of inferior conjunction
self.period = 0.  # orbital period

# For each instrument
Instruments_LC = {"Instrument1": {"same_jitter": True,
                                  "dataset"}
# Create a dictionnary called instruments_LC
# for each instrument_LC, create a key in instruments_LC that contains a
# dictionnary instrument. Look how many data set there is for this instrument.
# If one create a jitter key in the instrument dictionnary which contains a dictionary for the
# jitter parameter.which contains a free which is true or false and a prior that is a dictionary
# which a joint which could be true or false, a type that could be Gaussian, Uniform, ..., args
# which gives the arguments of the prior function. If joint is true
#
jitter = {"free": True,
          "prior": {"joint": False, "joint_prior_ref": None,
                    "type": None, "args": {}
                    }
          "value": None
          }

# For LC each dataset
bandwidth = [None, None]  # bandwidth in microns
