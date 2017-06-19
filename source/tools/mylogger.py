#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Toolbox to use the python logger.

Todo:
"""
from __future__ import print_function
from logging import getLogger, StreamHandler, FileHandler, Formatter, DEBUG, INFO
from sys import stdout


def init_logger(logger=None, with_ch=True, with_fh=True, logger_lvl=DEBUG, ch_lvl=INFO,
                fh_lvl=DEBUG, fh_file="logfile.log"):
    """Initialise the logger.

    Args:
        logger (logging.Logger): Logger object
        with_ch (bool): True if you want to initialise a console handler
        with_fh (bool): True if you want to initialise a file handler
        logger_lvl (int): Level desired for the logger
        ch_lvl (int): Level desired for the console handler
        fh_lvl (int): Level desired for the file handler
        fh_file (str): Name for the file of the file handler

    Returns:
        logging.Logger: Logger object
    """
    ## Create the logger if needs be
    if logger is None:
        logger = getLogger()

    # Update the logger lvl
    if logger.level != logger_lvl:
        logger.setLevel(logger_lvl)

    # Check the existance of Console and File handlers
    ch = None
    fh = None
    for handl in logger.handlers:
        if isinstance(handl, StreamHandler):
            ch = handl
        if isinstance(handl, FileHandler):
            fh = handl

    # Create formatters
    formatter_short = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    formatter_detailled = Formatter("%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s "
                                    "- %(funcName)s() \n%(message)s")

    # Create or update handlers and add them to the logger.
    if with_ch:
        if ch is None:
            ch = StreamHandler(stdout)
            ch.setLevel(ch_lvl)
            ch.setFormatter(formatter_short)
            logger.addHandler(ch)
        else:
            if ch.level != ch_lvl:
                ch.setLevel(ch_lvl)

    if with_fh:
        if fh is None:
            fh = FileHandler(fh_file)
            fh.setLevel(fh_lvl)
            fh.setFormatter(formatter_detailled)
            logger.addHandler(fh)
        else:
            if fh.level != fh_lvl:
                fh.setLevel(fh_lvl)

    return logger
