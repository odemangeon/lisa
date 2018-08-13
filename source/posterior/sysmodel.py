#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Sysmodel module.

The objective of this package is to provides the classes to create exo systems and function to
 provide simulated light-curve and radial velocities for these systems.

@TODO:
    THIS IS OUTDATED CHECK IF THERE SOMETHING USEFUL AND DELETE
"""
import logging
import numpy as np
from string import ascii_lowercase
from string import ascii_uppercase

from collections import OrderedDict

from .gravgroup import GravGroup
from tools.miscellaneous import check_name

## Logger
logger = logging.getLogger()


class SystemModel(object):
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

    def __init__(self, name, analysis_type,
                 transit_model=None, ld_model=None, rv_model=None,
                 gravgroups=None,
                 stars, planets
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
            name        : string,
                Name of the system studied.
            gravgroups  : OrderedDict or list, (default: None),
                Defines the GravGroup of the system studied. Each entry correspond to a GravGroup.
                The first one is the target GravGroup.
                Each entry should contain a dict with two entries: "stars" and "planets".
                Those entries should in turn contain list of stars/planets names in the GravGroup
                The classical name for a star is 'A', 'B',...
                The classical name for a planet is 'b', 'c',...
        """
        super(SystemModel, self).__init__()
        ## String: System name which is also the name of the target GravGroup
        self.name = check_name(name)

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
        self.gravgroups = OrderedDict()
        if gravgroups is not None:
            if isinstance(gravgroups, list):
                if len(gravgroups) > 0:
                    pass
                else:
                    logger.warning("gravgroup has been ")
        interpret_grav_group(gravgroups=gravgroups)
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
        else:
            raise ValueError("planets should be either a strictly positive int or a list of sting."
                             "Got {}".format(planets))
        for l in list_planets:
            self.list_planets[l] = Planet(host_star=system + '_A', name=l)

        # Choose the parametrization. I think that if we want to be able to choose the set of
        # Jumping parameters, It's now. Don't clear right now how to do it.

    def add_GravGroup(self, name, stars_name, planets_name):
        """Add a GravGroup to the system gravgroups attribute.

        ----

        Arguments:
            name        : string,
                name of the GravGroup
            stars_name  : list of string,
                list containing the names of the stars in the GravGroup
            planets_name  : list of string,
                list containing the names of the planets in the GravGroup
        """
        self.gravgroups[name] = GravGroup()

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
