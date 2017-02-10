#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
dico_database module.

The objective of this package is to provides a toolbox to manipulate dico_datases

@ DONE:
    -
@TODO:
    -
"""
from logging import getLogger


## logger object
logger = getLogger()


def get_nblevels_in_dico(dico_db):
    """Return the number of level in a dictionnary database."""
    dico_leveln = dico_db
    n = 0
    while True:
        if len(dico_leveln.keys()) > 0:
            n += 1
            key = list(dico_leveln.keys())[0]
            dico_leveln = dico_leveln[key]
            if not(isinstance(dico_leveln, dict)):
                break
        else:
            break
    return n


def get_content_2ndlevel(dico_db, level1_key=None):
    """Return the content of the 2nd level in dico_db.

    If the level1 key is specified return only the content of the this key otherwise return a
    dictionnary with the content of all the level1 keys.
    If dico_db has more than 1 level the result if the list of keys in the 2nd level.
    """
    nb_level = get_nblevels_in_dico(dico_db)
    logger.debug("Number of levels in dico_db: {}".format(nb_level))
    if nb_level < 1:
        raise ValueError("dico_db is empty.")
    if level1_key is None:
        iter_level1key = list(dico_db.keys())
        result = dict()
    else:
        iter_level1key = [level1_key, ]
    for key in iter_level1key:
        if nb_level > 1:
            content_level1key = list(dico_db[key].keys())
        else:
            content_level1key = dico_db[key]
        if level1_key is None:
            result[key] = content_level1key
        else:
            result = content_level1key
    return result


def get_content_3ndlevel(dico_db, level1_key=None, level2_key=None):
    """Return the content of the 3nd level in dico_db.

    If the level1 key is specified return only the content of the this key otherwise return a
    dictionnary with the content of all the level1 keys.
    then if level2 key is specified return only the content of the this key otherwise return a
    dictionnary with the content of all the level2 keys.
    If dico_db has more than 2 levels the result if the list of keys in the 3nd level.
    """
    if (level2_key is not None) and (level1_key is None):
        raise ValueError("You cannot specify level2 key without providing level 1 key.")
    nb_level = get_nblevels_in_dico(dico_db)
    logger.debug("Number of levels in dico_db: {}".format(nb_level))
    if nb_level < 2:
        raise ValueError("dico_db should have at least 2 levelss.")
    contentlevel2 = get_content_2ndlevel(dico_db, level1_key=level1_key)
    logger.debug("content level2: {}".format(contentlevel2))
    if level1_key is None:
        iter_level1key = list(contentlevel2.keys())
        result = dict.fromkeys(contentlevel2, None)
    else:
        iter_level1key = [level1_key, ]
    for key1 in iter_level1key:
        content_level3key = get_content_2ndlevel(dico_db[key1], level1_key=level2_key)
        logger.debug("content level3: {}".format(content_level3key))
        if level1_key is None:
            result[key1] = content_level3key
        else:
            result = content_level3key
    return result
