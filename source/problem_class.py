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
    ## List of radial velocity data for the problem
    rv_dataset = []
    ## List of light-curves data for the problem
    lc_dataset = []

    def __init__(self):
        """
        Choose the problem type.
        Define the number of star and planet.
        Define the rv and lc datasets.
        All the problem type should not be change afterward.
        Create a rv_dataset and/or
        """
        self

    def choose_parametrization(self):
        """
        Choose amongst different set of jumping parameters.
        """
        raise NotImplementedError

    def convert_param(self):
        """
        Convert one parametrisation in an other. For example if inclination is in the
        parametrization but you want the impact parameter
        """
        raise NotImplementedError

    def freeze_param(self):
        """
        Freeze a jupping parameter. Should impact the priors and the call to the solver.
        """
        raise NotImplementedError

    def unfreeze_param(self):
        """
        UnFreeze a jupping parameter. Should impact the priors and the call to the solver.
        """
        raise NotImplementedError

    def add_star(self):
        raise NotImplementedError

    def add_planet(self):
        raise NotImplementedError

    def show_problem_summary(self):
        """
        Return on the prompt a summary of the current definition of the problem.

        Give the current problem type, parametrization, number of stars, number of planets
        """
        raise NotImplementedError
