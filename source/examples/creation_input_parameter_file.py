#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Test script to creat the input parameter file.

@TODO:
    - Do the creation of the string for the Instrument
    - Compile instrument, star and planet string to create the full input parameter file
    - Read and interpret the input parameter file
"""
import logging
# import pdb

import source.problems.posterior.systemmodel.parameter as par
import source.problems.posterior.systemmodel.planet as pla
import source.problems.posterior.systemmodel.star as sta

# pdb.set_trace()

logger = logging.getLogger()
logger.setLevel("DEBUG")

# Test the string production with only a parameter
logger.info("\n#### Test the production of a string for only one parameter "
            "for the input definition file.\n")

logger.info("Create the parameter instance")
param_test = par.Parameter(name="Param_Test", free=True, main=None, joint_prior=False,
                           prior_type=None, prior_args=None,
                           joint_prior_ref=None, joint_prior_pos=None,
                           value=None)
logger.info("Show the string")
print(param_test.get_paramfile_section())

# Test the string production with only a Star object
logger.info("\n#### Test the production of a string for a Star only "
            "for the input definition file.\n")

# Create the star instance
logger.info("Create the star instance")
star_test = sta.Star(name="K2-19")
logger.info("Set parametrisation")
for param in star_test.get_list_params():
    param.main = True
logger.info("Show the string")
print(star_test.get_paramfile_section())

# Test the string production with only a Planet object
logger.info("\n#### Test the production of a string for a Planet only "
            "for the input definition file.\n")

# Create the planet instance
logger.info("Create the planet instance")
planet_test = pla.Planet(name="b", host_star=star_test)
logger.info("Set parametrisation")
for param in planet_test.get_list_params():
    param.main = True
logger.info("Show the string")
print(planet_test.get_paramfile_section())
