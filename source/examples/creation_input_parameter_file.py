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
import os
import sys
# import pdb

import source.problems.posterior.systemmodel.parameter as par
import source.problems.posterior.systemmodel.planet as pla
import source.problems.posterior.systemmodel.star as sta
import source.problems.posterior.systemmodel.instrument as ist

from source.software_parameters import input_run_folder

# pdb.set_trace()

logger = logging.getLogger()
logger.setLevel("DEBUG")

if len(logger.handlers) == 0:
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

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

# Test the string production with only a Planet object
logger.info("\n#### Test the production of a string for an instrument only "
            "for the input definition file.\n")

# Create the instrument instance
logger.info("Create the isntrument instance")
instrument_test = ist.Instrument(name="SOPHIE", inst_type="RV")
logger.info("Set parametrisation")
for param in instrument_test.get_list_params():
    param.main = True
logger.info("Show the string")
print(instrument_test.get_paramfile_section())

# Test the string production with an instrument, a planet and a star
logger.info("\n#### Test the production of a file in the run directory with an instrument, a planet"
            " , and a star and reading it after as we want to do we the input definition file.\n")
logger.info("Select and create run_folder")
run_folder = input_run_folder + "/" + star_test.get_short_name()
if not(os.path.isdir(run_folder)):
    logger.info("The run folder doesn't exist and is created: {}".format(run_folder))
    os.makedirs(run_folder)
logger.info("Create file")
with open(os.path.join(run_folder, "run_input_file.py"), "w") as f_input:
    f_input.write(star_test.get_paramfile_section())
    f_input.write(planet_test.get_paramfile_section())
    f_input.write(instrument_test.get_paramfile_section())
exec(open(os.path.join(run_folder, "run_input_file.py")).read())
