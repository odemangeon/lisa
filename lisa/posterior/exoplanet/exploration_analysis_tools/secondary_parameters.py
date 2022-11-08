"""Module to compute the secondary parameters chains.
"""
from collections import Counter
from numbers import Number
from numpy import ndarray, stack, arcsin, sqrt, rad2deg, random, pi

from ..model import convert as cv
from ....tools.human_machine_interface.QCM import QCM_utilisateur
from ....tools.human_machine_interface.standard_questions import Ask4Number, Ask4PositiveNumber
from ....tools.chain_interpreter import ChainsInterpret
from logging import getLogger


logger = getLogger()


def get_secondary_chains(chainI_main, sec_params, star_kwargs=None, planet_kwargs=None):
    """Return ChainInterpret instance with the computed chain of the secondary parameters.

    Arguments
    ---------
    chainI_main
    sec_params
    star_kwargs
    planet_kwargs
    """
    sec_par_chains = {}
    for sec_par_fullname, dico_sec_par in sec_params.items():
        if dico_sec_par['kwargs'] is not None:
            kwargs = dico_sec_par['kwargs']
            for arg_name, arg_value in kwargs.items():
                if arg_value == 'shape(nwalker,niter)':
                    kwargs[arg_name] = chainI_main.shape[:-1]
        else:
            kwargs = {}
        if dico_sec_par['l_param_name'] is not None:
            l_chains_param = []
            for param_name in dico_sec_par['l_param_name']:
                if param_name in chainI_main.param_names:
                    l_chains_param.append(chainI_main[..., param_name])
                else:
                    raise ValueError(f"Parameter {param_name} is not found anywhere")
        else:
            l_chains_param = []
        sec_par_chains[sec_par_fullname] = dico_sec_par['function'](*l_chains_param, **kwargs)

    l_parname_sec_chain = list(sec_par_chains.keys())
    chainIsec = ChainsInterpret(stack([sec_par_chains[param] for param in l_parname_sec_chain],
                                      axis=-1
                                      ),
                                l_parname_sec_chain)
    return chainIsec


# TODO: Make a function that creates the typical secondary parameters files.
