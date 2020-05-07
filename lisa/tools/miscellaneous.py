#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
miscellaneous module.

Provide toolbox with miscellaneous tools.

@TODO:
"""
from logging import getLogger
from os.path import basename, splitext, expanduser
import os

from .human_machine_interface.QCM import QCM_utilisateur
from .human_machine_interface.askpath import ask_exisiting_path

## Logger object
logger = getLogger()


def spacestring_like(string):
    """Return an empty string with the same size than string."""
    return " " * len(string)


def get_filename_from_file_path(file_path):
    """Return the filename from the file path.
    ----
    Arguments:
        file_path   : string,
            Path to the dataset file.

    Returns:
        file_name   : string,
            Name of the file extracted from the file_path.
    """
    return basename(file_path)


def get_filename_woext_from_filename(file_name):
    """Return the filename without extension from the filename with extension."""
    return splitext(file_name)[0]


def interpret_data_filename(data_file_name):
    """
    Interpret data file name.

    If the format of the data file name is recognized the function return a dictionnary (see
    Returns below) otherwise return None.
    ----
    Arguments:
        data_file_name : string,
            Data file name, should be in the format instcategory_object_instname(_number).*

    Returns:
        dictionnary with the interpration of the filename which contains the following keys:
            - object : name of the object observed with the data
            - inst_category : category of instrument used to take the data. e.g. "LC", "RV" or "SED"
            - inst_name : instrument name
            - number : give the number of the data file if there is several data files of the
                same object observed with the same instrument
    """
    cuts = data_file_name.split("_")   # List of fields that were separated by "_"
    cuts[-1] = cuts[-1].split(".")[0]  # Remove the extension
    if len(cuts) < 3 or len(cuts) > 4:
        raise ValueError("Data file name not recognized. Should be in the format "
                         "category_target_instrument(_number).txt. Got: {}".format(data_file_name))
    result = {"object": cuts[1],
              "inst_category": cuts[0],
              "inst_name": cuts[2]}
    if len(cuts) == 3:
        result["number"] = 0
    elif len(cuts) == 4:
        result["number"] = int(cuts[3])
    return result


def define_folder_withdefault(main_default_folder, object_name, folder="default"):
    """Return the selected folder.

    It can be specified in two ways:
        - Via the folder defined by main_default: In this case the folder is
          automatically define as "main_default/object_name". To use this you should assign
          "default"
        - Via the folder argument: You can provide any folder here

    ----
    Arguments:
        main_default_folder : string,
            Main default folder
        object_name         : string
            name of the object to be used as subfolder of the main_default_folder
        folder              : string, (default: None),
            path to the folder which contain the data. If provided the main_default_folder and
            objected argument are ignored.
    """
    # 1. Check if the folder argument has been provided. If yes use this otherwise try to use a folder
    # with the object name in the folder designated by the main_default_folder provided in argument
    folder_provided = (folder != "default")
    if folder_provided:
        folder_selected = expanduser(folder)
    else:
        folder_selected = os.path.join(expanduser(main_default_folder), object_name)
    # 2. Test is the folder selected in 1 exists
    folder_exist = os.path.isdir(folder_selected)
    # 3. If yes, return this folder
    if folder_exist:
        folder_defined = True
    # 4. If no, Ask if the user want to create the folder selected.
    else:
        if folder_provided:
            error_msg = "Folder doesn't exist: {}".format(folder_selected)
            reply = QCM_utilisateur(error_msg + "\n Do you want to create it ? (reply by 'y' or 'n')\n",
                                    ['y', 'n'])
        else:
            msg = ("You didn't provided any folder and the standard one doesn't exist. "
                   "Do you want to create the standard folder (reply by 'y' or 'n'):\n")
            reply = QCM_utilisateur(msg, ["y", "n"])
        # 4.1. If yes, create it and return the folder selected
        if reply == "y":
            os.makedirs(folder_selected)
            folder_defined = True
            logger.info("Folder created: {}".format(folder_selected))
        # 4.2. If no, don't create, and ask for an existing folder
        else:
            msg = ("Provide the path to an existing folder (Press enter to quit without defining "
                   "any folder)\n")
            reply = ask_exisiting_path(msg, exit_answer="", file_or_dir="dir")
            if reply is None:
                folder_defined = False
                logger.warning("folder has not been defined because provided folder doesn't "
                               "exist and has not been created.")
            else:
                folder_defined = True
                folder_selected = reply
    # 5. Log the result of the execution
    if folder_defined:
        if folder_provided:
            logger.debug("folder is defined as a specific folder: {}".format(folder_selected))
        else:
            logger.debug("folder not provided but standard folder exist and is used:"
                         " {}".format(folder_selected))
        return folder_selected
    else:
        return None


def look4file_withdeffolder(file_path, default_folder=None):
    """Look for a file in absolute or in the default folder.

    Return None if file is not found.
    """
    if os.path.exists(file_path):
        file_exist = True
        result = file_path
        logger.debug("File found at absolute path {}".format(file_path))
    elif (default_folder is not None):
        result = os.path.join(default_folder, file_path)
        if os.path.exists(result):
            file_exist = True
            logger.debug("File found in default folder path {}".format(result))
        else:
            file_exist = False
            result = None
    else:
        file_exist = False
        result = None
    if not(file_exist):
        logger.debug("File {} not found".format(file_path))
    return result
