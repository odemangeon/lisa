"""
Module with functions allowing to ask standard questions
"""
from loguru import logger
from os.path import join

from .QCM import QCM_utilisateur


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

def ask4CreationDefaultFile(path_file, default_file_content, default_folder=None):
    """
    """
    answers_list_yn = ['y', 'n']
    question = (f"File {path_file} doesn't exist. Do you want to create it ? {answers_list_yn}\n")
    reply = QCM_utilisateur(question, answers_list_yn)
    if reply == "y":

        answers_list_create = ["absolute", "error"]
        question = (f"File {path_file} doesn't exists. Do you want to\nCreate it at the 'absolute' "
                    f"path: {path_file}"
                    )
        if default_folder is not None:
            answers_list_create.append("run_folder")
            run_folder_path = join(default_folder, path_file)
            question += f"\nCreate it at the 'run_folder' path: {default_folder}"
        question += (f"\nNot create it and raise an 'error' ? {answers_list_create}\n")
        reply2 = QCM_utilisateur(question, answers_list_create)
        if reply2 == 'absolute':
            file_path = path_file
        elif reply2 == "run_folder":
            file_path = join(default_folder, path_file)
        else:
            raise ValueError(f"File {path_file} doesn't exist and the user doesn't want to create it.")
        with open(file_path, 'x') as fdatasets:
            fdatasets.write(default_file_content)
        return file_path
