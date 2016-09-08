#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Module where the Mcmc classes is defined.

__Mcmc class inherit from the __Solver class, it defines which attibutes and methods those Mcmc
class should absolutely have.

Emcee class inherit from the Mcmc class, it defines the specific attributes and methods of the Mcmc
solver using the emcee package.

For now Emcee is the only Mcmc solver but in the future we could implement others like Rodrigo's.
"""
from .solver import __Solver


class __Mcmc(__Solver):
    """
    A __Mcmc is a tool to explore the posterior probability function with a Mcmc technique.

    This class is not meant to be instanciated directly. It defines the common attributes and
    methods that all the Mcmc solvers should have in common. What you should instanciate is :
    - Emcee

    The common attributes are:
    - realisations : Dictionnary of realisations resulting from the mcmc exploration

    The common methods are:
    - get_best_param : which gives the best value and confidence intervals for the free parameters.
    - explore : which explore the posterior probability function by Mcmc method
    """

    ## realisations is an Ordered dictionnary which will receive all the __Realisation instances
    ## created when running the Mcmc.
    realisations = {}

    def __init__(self):
        """
        Init method of the __Mcmc class.

        It should be called at the end of the creation of every Mcmc solver instance to check if the
        common attibutes and methods are available. It should also check if the class you trying
        to instanciate is not __Mcmc.

        ----

        Arguments:
            None

        Raises:
            Errors to indicate that you are missing a common attribute ar method
            Errors to indicate that you cannot instanciate __Solver directly
        """
        raise NotImplementedError

    def get_best_param(self, loc_method="median", uncertainty_intervals=[68, ], realisation=0):
        """
        get_best_param function of the __Mcmc solver class.

        This function sould be called only after you made an exploration with the explore function
        and when you just have one flat chain for each free parameter. It looks into the chains and
        returns the best value for each parameter and uncertainty intervals.

        ----

        Arguments:
            loc_method : string, optional (default = "median").
                Method used to compute the location for the jumping parameters. It could be:
                - "median" : median of the chain
                - "mean"
            uncertainty_intervals : list of int, optional (default = [68, ]).
                List of probablity interval that you want to get. For example [68, ] means that you
                wants the 68 % confidence  interval
            realisation : int or string, optional (default = 0)
                Indicate which realisation you want to use.

        Returns:
            best parameter value for each free parama
            list of confidence intervals
        """
        raise NotImplementedError("The get_best_param function of __Mcmc Solver class should not be"
                                  "called. It's just a place holder which defines the interfaces of"
                                  "this method for the Mcmc solvers!")

    def explore(self, ln_prob, **kwargs):
        """
        explore of the __Mcmc solver class.

        This function is used to explore the (log) posterior probability function.

        ----

        Arguments:
            ln_prob : logarithm a the joint posterior probability density function.

        Keyword Arguments:
            kwargs : additional arguments which depends on the Mcmc methods used

        Returns:
            add a __Realisation instance in the realisations attribute
        """
        raise NotImplementedError("The get_best_param function of __Mcmc Solver class should not be"
                                  "called. It's just a place holder which defines the interfaces of"
                                  "this method for the Mcmc solvers!")


class __Realisation():
    """
    The Realisation class is meant to received and interpret the result of a Mcmc run.
    """

class Emcee(__Mcmc):
    """
    The Emcee Mcmc Solver class.
    """
