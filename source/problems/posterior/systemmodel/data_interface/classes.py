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

    def readLC(lcfile):
        """
        read light curve into a pandas database
        path should alwasy be the same...organise
        file name should denine the object and the run (type of analysis)
        need to define format of file to know how many raws to skip
        the name of the file is an identification of the filter but if 2 ground based instruments with same filter we might need to identified them as diferent
        """
        nlc = len(lcfile)
        path = always_the_same
        skip_lc_rows = 1

        for i in lcfile:
            # we can also read the header from the file with
            # lc = pd.read_table('cuttransits.txt', delim_whitespace=True, header=0, index_col=0)
            lc1 = pd.read_table(path+i, delim_whitespace=True, names=["time", "flux", "flux_err"], index_col=0, skiprows=1 )
            # to acces the colum values lc['time'], lc['flux'], lc['flux_err']
            # to have a  quick statistic summary of your data
            # lc.describe()

            # add column with filter
            lc1['instr'] = lcfile
            if (self.lc == 0):
                self.lc = lc1
            else:
                self.lc = pd.concat([self.lc,lc1] )



#could do it in one line but we canot aapend instrments
            pd.concat((pd.read_table(f , delim_whitespace=True, names=["time", "flux", "flux_err"], index_col=0, skiprows=1 ) for lcfile in all_files))

#could do it in a faster way not checked but for me the first way is ok

        np_array_list = []
        for i in lcfile:
            df = pd.read_table( path+i , delim_whitespace=True, index_col=0, skiprows=1 )
            np_array_list.append(df.as_matrix())

        comb_np_array = np.vstack(np_array_list)
        big_frame = pd.DataFrame(comb_np_array, names=["time", "flux", "flux_err"])



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
