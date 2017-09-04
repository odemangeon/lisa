#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Supersampling factor and exposure time module.
"""
from collections import OrderedDict

_supersamp_key = "supersamp"
_exptime_key = "exptime"


class SuperSampExpTime(OrderedDict):
    """docstring for SuperSampExpTime_Attr."""

    def __init__(self):
        super(SuperSampExpTime, self).__init__()

    def get_supersamp(self, instmod_fullname):
        """Return the supersampling factor to apply for the instrument model."""
        return self[instmod_fullname][_supersamp_key]

    def get_exptime(self, instmod_fullname):
        """Return the supersampling factor to apply for the instrument model."""
        return self[instmod_fullname][_exptime_key]

    def add_instmodel_SSE(self, inst_model_fullname, supersamp=None, exptime=None):
        """Add a supersamp and/or an exposure time for a given instrument full name."""
        self[inst_model_fullname] = {_supersamp_key: supersamp,
                                     _exptime_key: exptime}

    def add_instmodel_SSEdict(self, inst_model_fullname, SSEdict):
        """Add a supersamp and/or an exposure time for a given instrument full name."""
        self.add_instmodel_SSE(inst_model_fullname, supersamp=SSEdict[_supersamp_key],
                               exptime=SSEdict[_exptime_key])


class SuperSampExpTimeAttr(object):
    """docstring for SuperSampExpTime_Attr."""
    def __init__(self):
        super(SuperSampExpTimeAttr, self).__init__()
        self.__SSE4instmodfname = SuperSampExpTime()  # Supersampling and Exposure time for each

    @property
    def SSE4instmodfname(self):
        """Return the dictionary giving the supersampling factors and exposure_time for each LC
        instrument model."""
        return self.__SSE4instmodfname

    def get_supersamp(self, instmod_fullname):
        """Return the supersampling factor to apply for the instrument model."""
        self.SSE4instmodfname.get_supersamp(instmod_fullname)

    def get_exptime(self, instmod_fullname):
        """Return the supersampling factor to apply for the instrument model."""
        self.SSE4instmodfname.get_exptime(instmod_fullname)
