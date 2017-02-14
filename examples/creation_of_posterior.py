#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Test script giving an example of what to do to create a posterior

@TODO:
"""
import logging
import sys
# from ipdb import set_trace

import source.posterior.core.posterior as cpost

## logger
logger = logging.getLogger()

level_log = logging.DEBUG
level_hand = logging.DEBUG

if logger.level != level_log:
    logger.setLevel(level_log)
if len(logger.handlers) == 0:
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level_hand)
    formatter_short = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    formatter_detailled = logging.Formatter("%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s "
                                            "- %(funcName)s() \n%(message)s")
    ch.setFormatter(formatter_detailled)
    logger.addHandler(ch)
else:
    ch = logger.handlers[0]
    if ch.level != level_hand:
        ch.setLevel(level_hand)


logger.info("1. Create a Posterior instance and give it the name of the object studied.")
post_instance = cpost.Posterior(object_name="K2-19")

logger.info("2. (Facultative) Define the folder where the data regarding this object are stored.")
post_instance.dataset_db.data_folder = "default"

logger.info("2. (Facultative) Define the run folder where the config files and outputs will be.")
post_instance.run_folder = "default"

logger.info("3. Add datasets (from a file, their is otherways).")
post_instance.dataset_db.add_datasets_from_datasetfile("datasets_K2-19.txt")

logger.info("4. Add a model")
post_instance.define_model(category="GravitionalGroups", name="K2-19", stars=1, planets=2)

logger.info("5. Apply a parametrisation to the model")
post_instance.model.apply_RV_EXOFAST_param()

logger.info("6. Create and modify the paramerisation file")
post_instance.model.create_parameter_file("param_file.py")

input("Modifiy the paramerisation file")

logger.info("7. Load the paramerisation file")
post_instance.model.load_parameter_file()

logger.info("7. Create prior functions")
joint_lnprior, lnpriors = post_instance.model.create_joint_lnprior(post_instance.model.get_list_paramnames(main=True, free=True, full_name=True))
