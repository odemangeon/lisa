# -*- coding: utf-8 -*-
"""
Created on Fri May 25 17:39:11 2012

@author: olivierdemangeon
"""
import logging

## logger
logger = logging.getLogger()


def QCM_utilisateur(intitule_question, l_reponses_possibles):
    """
    Syntaxe:
        reponse = QCM_utilisateur(intitule_question,l_reponses_possibles)
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
