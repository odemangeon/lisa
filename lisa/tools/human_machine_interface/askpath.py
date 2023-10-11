"""
Created on June 6 2018

@author: olivierdemangeon
"""
from loguru import logger
import readline  # When readline module was loaded, input() will use it to provide elaborate line editing and history features.

from os.path import isfile, isdir

def ask_exisiting_path(intitule_question, exit_answer="", file_or_dir="both"):
    """Ask for a path.

    :param string intitule_question: Question that you want to ask
    :param string exit_answer: Answer insterpreted as I want to quit
    :param string file_or_dir: If file, the path is expected to lead to an existing file.
        If dir, the path is expected to lead to an existing directory. Finally is both the path is
        expected to lead to an existing directory or file
    """
    root_warn_msg = 'Reply is not an exisiting {}!'
    dico_warn_msg = {"both": root_warn_msg.format("file or directory"),
                     "file": root_warn_msg.format("file"),
                     "dir": root_warn_msg.format("directory")}
    if file_or_dir not in dico_warn_msg.keys():
        raise ValueError("file_or_dir should be in ['both', 'file', 'dir']")
    logger.debug("Exit answer: {}".format(exit_answer))
    while True:
        rep = str(input(intitule_question))
        rep = rep.strip('"')
        rep = rep.strip("'")
        logger.debug("Reply received: {}".format(rep))
        if rep == exit_answer:
            logger.warning("Quit without providing a file or directory")
            return
        else:
            if file_or_dir == "both":
                test = isfile(rep) or isdir(rep)
            elif file_or_dir == "file":
                test = isfile(rep)
            else:  # file_or_dir == "dir"
                test = isdir(rep)
            if test:
                return rep
            else:
                logger.warning(dico_warn_msg[file_or_dir])
