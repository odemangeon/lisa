from collections import OrderedDict
from numpy.random import normal

import lisa.posterior.exoplanet.model.convert as cv


star_kwargs = {"M": {"value": 1.458,
                     "error": 0.021},
               "R": {"value": 1.765,
                     "error": 0.071},
               "Teff": {"value": 6329,
                        "error": 65}
               }


sp = OrderedDict()

sp['A_M'] = {'function': normal, 'kwargs': {'loc': star_kwargs['M']['value'], 'scale': star_kwargs['M']['error'], 'size': 'shape(nwalker,niter)'}, 'l_param_name': None}
sp['A_R'] = {'function': normal, 'kwargs': {'loc': star_kwargs['R']['value'], 'scale': star_kwargs['R']['error'], 'size': 'shape(nwalker,niter)'}, 'l_param_name': None}
sp['A_Teff'] = {'function': normal, 'kwargs': {'loc': star_kwargs['Teff']['value'], 'scale': star_kwargs['Teff']['error'], 'size': 'shape(nwalker,niter)'}, 'l_param_name': None}
sp['b_Trdepth'] = {'function': cv.get_transit_depth, 'kwargs': None, 'l_param_name': ['b_Rrat']}
