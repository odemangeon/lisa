#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Classes module.

The objective of this package is to provides the data classes to store and manipulate radial
velocity and light-curve data sets.
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


class ExoP_timeserie():
    """
    Exoplanet time-serie data class
    """

    instrument_type = None
    instrument_name = None
    data = None  # Pandas.Dataframe
    flags_list = []
    __mandatory_columns = ["time"]  # Not sure if I should put time here if pandas time serie

    def plot_data(self):
        """
        Plot the data.
        """
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

    def readLC(self,lcfile, path):
        """
        read light curve into a pandas database
        path should alwasy be the same...or given by person
        file name should denine the object and the run (type of analysis)
        need to define format of file to know how many raws to skip
        the name of the file is an identification of the filter but if 2 ground based instruments with same filter we might need to identified them as diferent
        """

        if path == 0:
            path =  always_the_same

        skip_lc_rows = 1

        self.lc_file = path+lcfile
        # we can also read the header from the file with
        # lc = pd.read_table('cuttransits.txt', delim_whitespace=True, header=0, index_col=0)
        self.lc = pd.read_table(self.lc_file, delim_whitespace=True, names=["time", "flux", "flux_err","inst_flag"] , index_col=0, skiprows= skip_lc_rows)
        # to acces the colum values lc['time'], lc['flux'], lc['flux_err']
        # they will come indexit to the time but when we transformed them into numpy np.asarray(lc['inst_flag']) it is just the column
        # to have a  quick statistic summary of your data
        #lc.describe()
        self.lc["inst_flag"].fillna(0, inplace=True)



    def plot_lc(self):
        '''
        this is not very pretty but it plots the flux versus time and the error bars
        '''
        self.lc.plot( y="flux", yerr=self.lc["flux_err"]
        plt.show()






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
