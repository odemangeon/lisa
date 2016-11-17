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

from ....software_parameters import input_data_folder
from .data_interface.classes import ExoP_datasets


class SystemModel():
    """
    Sysmodel class which defines the model used.

    Provide function to model the observables: radial velocities, transit photometry (and SED)
    """

    nb_star = 0
    nb_planet = 0

    dynamic = False

    ## List of available rv models
    _rv_models = ["ajplanet"]
    rv_model = None

    ## List of available lc models
    _lc_models = ["batman", "pytransit"]
    transit_model = None

    ## List of available analysis
    _analysis_types = ["lc", "rv", "lc+rv", "lc+rv+dynamic"]
    analysis_type = None

    datasets = None

    def __init__(self,
                 target, main_data_folder=input_data_folder, data_folder=None,
                 analysis_type=None, transit_model=None, LD_model=None, rv_model=None,
                 nb_planet=1, nb_star=1):
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
            target : string,
                Name of the target studied.
            main_data_folder : string, optional,
                path to the data_folder which should contain a folder named after the target and
                contain the data.
            data_folder : string,
                path to the folder which contain the data. If provided the main_data_folder argument
                is ignored.
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
            else:
                raise ValueError("transit_model should be in ['batman', 'pytransit']")
            # Define the limb darkening model: I think we should have an argument to select the LD
            # model here.
            if self.transit_model == 'batman':
                # it can be changed later but I dont know how to make it 0 string
                self.limb_dark = "quadratic"  # if  batman limb darkening model
            else:
                self.limb_dark = 2  # if pyttransit , do we want to give the option now ?

        # Define the rv model used if needed
        if analysis_type in ['rv', 'lc+rv']:
            if rv_model in self._rv_models:
                self.rv_model = rv_model
            else:
                raise ValueError("rv_model should be in ['ajplanet']")

        if analysis_type == "lc+rv+dynamic":
            raise NotImplementedError("Models with dynamic have not been implemented yet.")

        # Define the number of planets in the system
        if nb_planet >= 1:
            self.nb_planet = nb_planet
        # Define the number of stars in the system
        if nb_star >= 1:
            self.nb_star = nb_star

        # Create the ExoP_datasets instance and store it in the datasets attribute
        self.datasets = ExoP_datasets(target,
                                      main_data_folder=main_data_folder,
                                      data_folder=data_folder)

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
