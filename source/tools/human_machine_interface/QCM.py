# -*- coding: utf-8 -*-
"""
Created on Fri May 25 17:39:11 2012

@author: olivierdemangeon
"""


#### Fonctions
def QCM_utilisateur(intitule_question,l_reponses_possibles):
    """
    Syntaxe:
        reponse = QCM_utilisateur(intitule_question,l_reponses_possibles)
    """
    rep = None
    while True:
        rep = str(input(intitule_question))
        rep = rep.strip('"')
        rep = rep.strip("'")
        print(rep)
        print(l_reponses_possibles)
        if rep in l_reponses_possibles:
            return rep
        elif rep == 'quit':
            return
        else:
            print('Réponse non reconnue')   