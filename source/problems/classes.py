#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Classes module.

The objective of this package is to provides the classes to solve exo planetary problems.
"""

class Problem():

    problem_type = None
    ## List of possible problems
    _problems = ["rv only", "lc only", "rv + lc", "rv + lc + dyn"]

    def __init__(self):
        self

    def choose_parametrization(self):
        raise NotImplementedError

    def convert_param(self):
        """
        Convert one parametrisation in an other. For example if inclination is in the
        parametrization but you want the impact parameter
        """
        raise NotImplementedError

    def freeze_param(self):
        raise NotImplementedError

    def add_star(self):
        raise NotImplementedError

    def add_planet(self):
        raise NotImplementedError
