#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Sysmodel module.

The objective of this package is to provides the classes to create exo systems and function to
 provide simulated light-curve and radial velocities for these systems.

@TODO:
    - Implement LD_model argument in __init__ of SystemModel
"""
import numpy as np
from string import ascii_lowercase
from string import ascii_uppercase

from collections import OrderedDict

from .planet import Planet
from .star import Star


def interpret_grav_group(grav_groups):
    """

    """


class SystemModel():
    """
    Sysmodel class which defines the model used.

    Provide function to model the observables: radial velocities, transit photometry (and SED)
    """

    nb_star = 0
    nb_planet = 0

    ## List of available rv models, the 1st element is used as default
    _rv_models = ["ajplanet"]

    ## List of available lc models, the 1st element is used as default
    _lc_models = ["batman", "pytransit-MandelAgol", "pytransit-Gimenez"]

    ## List of available limb-darkening models for each lc_models, the 1st element is used as
    ## default
    _ld_models = {"batman": ["quadratic", "nonlinear", "exponential", "logarithmic", "squareroot",
                             "linear", "uniform", "custom"],
                  "pytransit-MandelAgol": ["quadratic", "linear", "uniform"],
                  "pytransit-Gimenez": ["quadratic", "linear", "uniform"]
                  }

    ## List of available analysis
    _analysis_types = ["lc", "rv", "lc+rv", "lc+rv+dynamic"]

    def __init__(self, system, analysis_type,
                 transit_model=None, ld_model=None, rv_model=None,
                 grav_groups=[{'stars': 1, 'planets': 1}, ]
                 ):
        """
        Create SystemModel instance Object.

        Defines the transit, rv models and SED models used. Defines the parametrisation.
        So I think here we can either read the text file or fill some main information that will
        produce a template and then we fill oit and create a function that will read it.

        If we want to produce the a template, we need to give the transit model, the LD model used,
        the rv model, the number of star and the number of planet and we need to have a
        data_set instance.

        ----

        Arguments:
            system : string,
                Name of the system studied.
        """
        # Define the type of analysis
        if analysis_type in self._analysis_types:
            self.analysis_type = analysis_type
        else:
            raise ValueError("analysis_type should be in ['lc', 'rv', 'lc+rv', 'lc+rv+dynamic']")

        # Define the transit and limbdarkening model used if needed
        if analysis_type in ['lc', 'lc+rv', 'lc+rv+dynamic']:
            # transit
            if transit_model in self._lc_models:
                self.transit_model = transit_model
            elif transit_model is None:
                self.transit_model = self._lc_models[0]
            else:
                raise ValueError("transit_model should be in {}".format(self._lc_models))
            # Define the limb darkening model: I think we should have an argument to select the LD
            # model here.
            if ld_model in self._ld_models[self.transit_model]:
                self.ld_model = ld_model  # if  batman limb darkening model
            elif ld_model is None:
                self.ld_model = self._ld_models[self.transit_model][0]
            else:
                raise ValueError("For transit model {}, ld_model should be in {}"
                                 "".format(self.transit_model, self._ld_models[self.transit_model]))

        # Define the rv model used if needed
        if analysis_type in ['rv', 'lc+rv']:
            if rv_model in self._rv_models:
                self.rv_model = rv_model
            elif rv_model is None:
                self.rv_model = self._rv_models[0]
            else:
                raise ValueError("rv_model should be in {}".format(self._rv_models))

        # Define if the model will use dynamic
        if analysis_type == "lc+rv+dynamic":
            self.dynamic = True
            raise NotImplementedError("Models with dynamic have not been implemented yet.")
        else:
            self.dynamic = False

        # Define gravitational groups
        interpret_grav_group(grav_groups=grav_groups)
        ## TODO

        # Initialise the stars in the system
        self.stars = OrderedDict()
        if isinstance(stars, int):
            if stars >= 1:
                if stars == 1:
                    list_stars = []
                else:
                    list_stars = [L for L in ascii_uppercase[:stars]]
            else:
                raise ValueError("If you specify the number of stars, it should be "
                                 "strictly positive ! Got {}".format(stars))
        elif isinstance(stars, list) and isinstance(stars[0], str):
            list_stars = stars
        else:
            raise ValueError("stars should be either a strictly positive int or a list of sting."
                             "Got {}".format(stars))
        if len(list_stars) == 0:
            self.stars["A"] = Star(system=system)
        else:
            for L in list_stars:
                self.stars["A"] = Star(system=system, name=L)

        # Initialise the planets in the system
        self.planets = OrderedDict()
        if isinstance(planets, int):
            if planets >= 1:
                list_planets = [l for l in ascii_lowercase[1:planets + 1]]
            else:
                raise ValueError("If you specify the number of planets, it should be "
                                 "strictly positive ! Got {}".format(planets))
        elif isinstance(planets, list) and isinstance(planets[0], str):
            list_planets = planets
        elif
        else:
            raise ValueError("planets should be either a strictly positive int or a list of sting."
                             "Got {}".format(planets))
        for l in list_planets:
            self.list_planets[l] = Planet(host_star=system + '_A', name=l)

        # Choose the parametrization. I think that if we want to be able to choose the set of
        # Jumping parameters, It's now. Don't clear right now how to do it.

        ## The following will be filled when reading the text file.

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

    def create_filetemplate(self):
        """
        Create template file to be filed with the initial parameter values and prior functions
        """

        raise NotImplementedError

    def read_initfile():
        """
        Read the file and init the value of parameters and priors
        """
        raise NotImplementedError

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

            self.batman_model = batman.TransitModel(self.params,
                                                    time,
                                                    supersample_factor=self.supersample,
                                                    exp_time=self.exp_time)
            light_curve = self.batman_model.light_curve(self.params)

        else:
            from pytransit import MandelAgol
            model = MandelAgol(nldc=self.limb_dark, exptime=self.exp_time,
                               supersampling=self.supersample)
            light_curve = model.evaluate(time, self.rp, self.u, self.t0, self.period, self.ar,
                                         self.inc * np.pi / 180., self.ecc, self.w * np.pi / 180.)

        return light_curve

    def get_rv(self, time):
        """
        Produce simulated rv
        """
        from ajplanet import pl_rv_array
        rv_model = pl_rv_array(time, self.rvsys, self.K, np.deg2rad(self.w), self.ecc, self.t0,
                               self.period)
        return rv_model

    def get_lc_and_rv(self, time_lc, time_rv):
        """
        Produce a simulated lc and rv
        """
        light_curve = self.get_lc(time_lc)
        rv_curve = self.get_rv(time_rv)

        return light_curve, rv_curve
