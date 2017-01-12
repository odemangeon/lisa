#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Instrument module.

The objective of this module is to define the Instrument classes.

@TODO:
    - Implement spectral_transmission in Instrument class

"""
from .parameter import Parameter
from .paramcontainer import ParamContainer


class Instrument(ParamContainer):
    """docstring for Instrument."""

    def __init__(self, name, inst_type):
        """docstring for Instrument init method."""
        super(Instrument, self).__init__(name)
        ## Jitter of the instrument
        self.jitter = Parameter(name="jitter")
        # Update list of parameters
        super().extend_list_params([self.jitter])
        ## Spectral transmission
        self.spectral_transmission = None
