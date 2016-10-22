#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Run module.

The objective of this module is to provide tools to set up a run.
"""
import os.path
import logging

from .software_parameters import input_run_folder

logger = logging.getLogger()


def set_up_run(target, run_name, main_run_folder=input_run_folder, run_folder=None):
    """
    Set up a run.

    Select a folder which will be used to put the input files for the run.
    There is two ways to specify the input folder:
        - main_run_folder: You provide the main run_folder which is made to receive the run input
        files for all the targets. So this folder should contain a folder name after the target.
        you want to study. If not this folder will be created.
        - run_folder: You provide directly the path of folder that you want to use for the input
        files.

    ----

    Arguments:
        target: string
            Gives the target name
        run_name: string
            gives the run_name
        main_run_folder : string, optional,
            path to the main run folder which is made to receive the run input files for all the
            targets. Inside this folder a folder with the name of the target will then contain the
            input files for the run.
        run_folder : string,
            path to the folder which will be used to put the input files for the run. If provided,
            the main_data_folder argument is ignored.

    Returns:
        datasets_filename: string
            Path to the datasets file
    """
    # Create the run folder if necessary
    if run_folder is not None:
        folder = run_folder
    else:
        folder = os.path.join(main_run_folder, target)
    if not(os.path.isdir(folder)):
        logger.info("The run folder doesn't exist and is created: {}".format(folder))
        os.makedirs(folder)
    else:
        logger.info("The run folder already exists: {}".format(folder))

    # Create datasets file if necessary
    datasets_filename = os.path.join(folder, "datasets_{}_{}.txt".format(target, run_name))
    if os.path.isfile(datasets_filename):
        logger.warning("A datasets file already exists at {}".format(datasets_filename))
    else:
        logger.info("The dataset file is created: {}".format(datasets_filename))
        with open(datasets_filename, 'x') as fdatasets:
            header = "# Datasets file: List below all the files you want to use for this run"
            fdatasets.write(header)
    return datasets_filename
