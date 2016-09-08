#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Sysmodel module.

The objective of this package is to provides the classes to create exo systems and function to
 provide simulated light-curve and radial velocities for these systems.
"""

class SystemModel():

    number_star = 0
    number_planet = 0
    dynamic = False
    ## List of available rv models
    _rv_models = ["ajplanet"]
    ## List of available lc models
    _lc_models = ["batman", "pytransit"]

    def __init__(self):
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

    def get_lc():
        """
        Produce a simulated lc
        """
        raise NotImplementedError

    def get_rv():
        """
        Produce simulated rv
        """
        raise NotImplementedError

    def get_lc_and_rv():
        """
        Produce a simulated lc and rv
        """
        raise NotImplementedError
