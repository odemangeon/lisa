#!/usr/bin/python
# -*- coding:  utf-8 -*-
# """
# manager_prior module.
#
# The objective of this module is to manage the priors.
#
# @DONE:
#     - __Mgr.__init__: UT
#     - __Mgr._reset_priors_database: Doc and UT
#     - __Mgr.load_setup: Doc but No UT because depend on the content of the setup file
#     - __Mgr.get_available_priors: Doc and UT
#     - __Mgr.add_available_prior: Doc and UT
#     - __Mgr.get_prior_subclass: Doc and UT
#     - __Mgr.is_available_priortype: Doc and UT
#     - Manager_Prior.__init__: Doc and UT
#     - Manager_Prior.__gettattr__: Doc and UT
#
# @TODO:
#     -
# """
# from logging import getLogger
# from ....software_parameters import setupfile_prior
# from .core_prior import Core_Prior_Function
#
# ## Logger
# logger = getLogger()
#
#
# # TODO: Store in different place the joint and marginal priors ?
#
#
# class Manager_Prior(object):
#     """docstring for Manager_Prior Singleton class."""
#
#     class __Mgr(object):
#         """docstring for __Mgr private class of Singleton class Manager_Prior.
#
#         For more information see Manager_Prior class.
#         """
#         def __init__(self):
#             """__Mgr init method.
#
#             For more information see Manager_Prior init method.
#             """
#             self.__priors = dict()
#
#         def _reset_priors_database(self):
#             """Reset database of available prior functions."""
#             self.__priors = dict()
#
#         def load_setup(self):
#             """Load the configuration of priors defined in the setup file.
#
#             Association prior type name and Prior_Function subclass.
#             """
#             f = open(setupfile_prior)
#             exec(f.read())
#             f.close()
#             logger.debug("Setup of Manager_Prior Loaded. Available priors: {}"
#                          "".format(self.get_available_priors()))
#
#         def get_available_priors(self):
#             """Returns the list of available prior types.
#             ----
#             Returns:
#                 list of string, giving the available prior types.
#             """
#             return list(self.__priors.keys())
#
#         def add_available_prior(self, priorfunction_subclass):
#             """Add a Prior_Function subclass to database.
#
#             This method checks that the priorfunction_subclass is indeed a Prior_Function subclass
#             before adding it to the database.
#             ----
#             Arguments:
#                 priorfunction_subclass : Subclass of Prior_Function,
#                     Custom subclass of the Prior_Function Class that you want to add to the
#                     database.
#             """
#             logger.debug("priorfunction_subclass type: {}".format(type(priorfunction_subclass)))
#             if not(issubclass(priorfunction_subclass, Core_Prior_Function)):
#                 raise ValueError("The provided class is not a subclass of the Prior_Function"
#                                  " class.")
#             self.__priors.update({priorfunction_subclass.category: priorfunction_subclass})
#
#         def get_priorfunc_subclass(self, category):
#             """Return Prior_Function Subclass associated to a given prior type.
#             ----
#             Arguments:
#                 category : string,
#                     Type of the prior function.
#             Returns:
#                 priorfunction_subclass : Subclass of Prior_Function,
#                     Sub-class of Prior_Function associated with the prior type.
#             """
#             if not self.is_available_priortype(category):
#                 raise ValueError("The prior type {} is not amongst the available priors {}"
#                                  "".format(category, self.get_available_priors()))
#             return self.__priors[category]
#
#         def is_available_priortype(self, category):
#             """Check if category refers to an available subclass of prior.
#             ----
#             Arguments:
#                 category : string,
#                     Type of the prior.
#             Returns:
#                 True if category is an available Prior_Function subclass. False otherwise.
#             """
#             return category in self.get_available_priors()
#
#     instance = None
#
#     def __init__(self):
#         """Manager_Prior init method (check if singleton exists and creates it if needed).
#
#         The init method of the inside class does:
#             1. Initialise the database of available prior types
#         """
#         if Manager_Prior.instance is None:
#             Manager_Prior.instance = Manager_Prior.__Mgr()
#
#     def __getattr__(self, name):
#         """Delegate every method or attribute call to the Singleton."""
#         return getattr(self.instance, name)
