#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Instrument module.

The objective of this module is to define the Instrument classes.

"""


class Instrument(object):
    """docstring for Instrument."""

    spectral_transmission = None
    jitter = None
    inst_type = None

    def __init__(self, arg):
        """docstring for Instrument init method."""
        super(Instrument, self).__init__()
        self.arg = arg
