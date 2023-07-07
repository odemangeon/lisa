# -*- coding: utf-8 -*-
"""
Created on Fri May 25 17:39:11 2012

@author: olivierdemangeon
"""
from loguru import logger
import readline  # When readline module was loaded, input() will use it to provide elaborate line editing and history features.


def QCM_utilisateur(intitule_question, l_reponses_possibles):
    """Ask a multiple choice question with a predefined set of possible answers.

    :param string       intitule_question: Question that you want to ask
    :param string_list  l_reponses_possibles: list of possible replies
    """
    while True:
        rep = str(input(intitule_question))
        rep = rep.strip('"')
        rep = rep.strip("'")
        logger.debug("Reply received: {}".format(rep))
        logger.debug("List of possible replies: {}".format(l_reponses_possibles))
        if rep in l_reponses_possibles:
            return rep
        elif rep == 'quit':
            return
        else:
            logger.warning('Reply not recognised !')
