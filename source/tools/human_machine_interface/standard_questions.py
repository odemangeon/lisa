# -*- coding: utf-8 -*-
"""
Module with functions allowing to ask standard questions
"""
import logging

## logger
logger = logging.getLogger()


def Ask4Number(intitule_question, default_value=None):
    """Ask to provide a number.

    :param  string  intitule_question: Question that you want to ask
    :param  float   default_value: default value if no answer provided (optional)
    :return float   number: Returned number
    :return Boolean answered: True is the user replied, False if not and return is the default value
    """
    while True:
        rep = str(input(intitule_question))
        if (rep == '') and (default_value is not None):
            return default_value, False
        else:
            try:
                return float(rep), True
            except ValueError:
                logger.warning("Reply is not a float number !")


def Ask4PositiveNumber(intitule_question, default_value=None):
    """Ask to provide a positive number.

    :param  string  intitule_question: Question that you want to ask
    :param  float   default_value: default value if no answer provided (optional)
    :return float   number: Returned number
    :return Boolean answered: True is the user replied, False if not and return is the default value
    """
    while True:
        rep = str(input(intitule_question))
        if (rep == '') and (default_value is not None):
            return default_value, False
        else:
            try:
                number = float(rep)
                if number >= 0.:
                    return number, True
                else:
                    logger.warning("Reply is not a POSITIVE number !")
            except ValueError:
                logger.warning("Reply is not a float number !")
