#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Sysmodel module.

The objective of this package is to provides the classes to create exo systems and function to
 provide simulated light-curve and radial velocities for these systems.
"""
import numpy as np


class SystemModel():

    number_star = 0
    number_planet = 0
    dynamic = False
    ## List of available rv models
    _rv_models = ["ajplanet"]
    ## List of available lc models
    _lc_models = ["batman", "pytransit"]

    def __init__(self, model):
        # transit parameters
        self.rp = 0.          # planet radius (in units of stellar radii)
        self.ar = 0.           # semi-major axis (in units of stellar radii)
        self.inc = 0.         # orbital inclination (in degrees)

        self.model = model

        if self.model == 'batman':
            # it can be changed later but I dont know how to make it 0 string
            self.limb_dark = "quadratic" #  if  batman limb darkening model
        else:
            self.limb_dark = 2 # if pyttransit , do we want to give the option now ?


        '''
        this will depend on how many LC data sets ..? how to set it?
        '''
        self.jitter_lc = 0.
        self.u = [0., 0.]     # limb darkening coefficients
        self.supersample = 0 # 21 supersampling factor needs to be defined for each light curve
        self.exp_time = 0.5/24. # if supersampling is done we need to define this for each light curve
        #we can also calculate it but sometimes if we miss data this will be wrong


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
        self.t0 = 0.     # time of inferior conjunction
        self.period = 0. # orbital period





    def set_lc_model():
        """
        Choose the lc_model to be used in the list of available lc model (_lc_models).
        Define the number of planets.
        """
        raise NotImplementedError

    def set_rv_model():
        """
        Choose the rv_model to be used in the list of available rv model (_rv_models).
        Define the number of planets.
        """
        raise NotImplementedError

    def get_lc(self, time):
        """
        Produce a simulated lc
        """
        if self.model == 'batman':
            import batman
            self.params = batman.TransitParams()
            self.params.limb_dark = self.limb_dark  # limb darkening model  "quadratic"
            self.params.u = self.u    # limb darkening coefficients

            self.params.t0 = self.t0
            self.params.per = self.period
            self.params.rp = self.rp
            self.params.a = self.ar
            self.params.inc = self.inc
            self.params.ecc = self.ecc
            self.params.w = self.w

            self.batman_model = batman.TransitModel(self.params, time, supersample_factor = self.supersample, exp_time = self.exp_time)
            light_curve = self.batman_model.light_curve(self.params)

        else:
            from pytransit import MandelAgol
            model = MandelAgol(nldc = self.limb_dark ,exptime = self.exp_time, supersampling = self.supersample)
            light_curve = model.evaluate(time, self.rp, self.u, self.t0, self.period, self.ar, self.inc * np.pi/180., self.ecc, self.w * np.pi/180.)

        return light_curve




    def get_rv(self,time):
        """
        Produce simulated rv
        """
        from ajplanet import pl_rv_array
        rv_model = pl_rv_array(time, self.rvsys, self.K, np.deg2rad(self.w), self.ecc, self.t0, self.period)
        return rv_model


    def get_lc_and_rv(self, time_lc, time_rv):
        """
        Produce a simulated lc and rv
        """
        light_curve = self.get_lc(time_lc)
        rv_curve =  self.get_rv(time_rv)

        return light_curve, rv_curve
