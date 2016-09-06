#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Classes module.

The objective of this package is to provides the data classes to store and manipulate radial
velocity and light-curve data sets.
"""


class ExoP_timeserie():
    """
    Exoplanet time-serie data class
    """

    instrument_type = None
    instrument_name = None
    data = None
    flags_list = []
    __mandatory_columns = ["time"]  # Not sure if I should put time here if pandas time serie

    def plot_data(self):
        raise NotImplementedError

class LightCurve(ExoP_timeserie):
    """
    Light-curve class
    """

    instrument_type = "transit"
    ExoP_timeserie.__mandatory_columns.extend(["flux", "flux_err"])

    def __init__(self):
        """
        Create Light-curve instance.
        """
        raise NotImplementedError

    def likelihood(self, simulated_data):
        raise NotImplementedError


class RV(ExoP_timeserie):
    """
    Radial velocities class
    """

    instrument_type = "rv"
    ExoP_timeserie.__mandatory_columns.extend(["RV", "RV_err"])

    def __init__(self):
        """
        Create Radial velocities instance.
        """
        raise NotImplementedError

    def likelihood(self):
        raise NotImplementedError
