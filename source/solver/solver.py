#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Module where the __Solver class is defined.

__Solver class is not meant to be instanciated directly. It is just meant to be used as
parent class for the Leastsquare and MCMC to define which attibutes and functions those class
should absolutely have.
"""


class __Solver():
    """
    A __Solver is a tool to explore the posterior probability function and find the best parameter.

    This class is not meant to be instanciated directly. It defines the common attributes and
    methods that all the Solvers should have in common. What you should instanciate is :
    - Mcmc
    - Leastsquare

    The common attributes are:
    None

    The common methods are:
    - get_best_param : which gives at minimum the best value for the free parameters.
    """

    def __init__(self):
        """
        Init method of the __Solver class.

        It should be called at the end of the creation of every Solver instance to check if the
        common attibutes and methods are available. It should also check if the class you trying
        to instanciate is not __Solver.

        ----

        Arguments:
            None

        Raises:
            Errors to indicate that you are missing a common attribute ar method
            Errors to indicate that you cannot instanciate __Solver directly
        """
        raise NotImplementedError("The __init__ method of __Solver is not implemented yet.")
