from collections import OrderedDict
from numpy.random import normal

import lisa.posterior.exoplanet.model.convert as cv

target_name = "WASP-76"

star_kwargs = {"M": {"value": 1.426717,  # TS3 https://docs.google.com/spreadsheets/d/12KA3-A3h5T7IJR5J7T1DE9SYTtjoS8rI6-98HwgQFF4/edit#gid=1232635509
                     "error": (0.08047 + 0.074749) / 2},
               "R": {"value": 1.764,  # TS3 https://docs.google.com/spreadsheets/d/12KA3-A3h5T7IJR5J7T1DE9SYTtjoS8rI6-98HwgQFF4/edit#gid=1232635509
                     "error": 0.036},
               "Teff": {"value": 6329,  # TS3 https://docs.google.com/spreadsheets/d/12KA3-A3h5T7IJR5J7T1DE9SYTtjoS8rI6-98HwgQFF4/edit#gid=1232635509
                        "error": 65}
               }

sp = OrderedDict()

sp['A_M'] = {'function': normal, 'kwargs': {'loc': star_kwargs['M']['value'], 'scale': star_kwargs['M']['error'], 'size': 'shape(nwalker,niter)'}, 'l_param_name': None}
sp['A_R'] = {'function': normal, 'kwargs': {'loc': star_kwargs['R']['value'], 'scale': star_kwargs['R']['error'], 'size': 'shape(nwalker,niter)'}, 'l_param_name': None}
sp['A_Teff'] = {'function': normal, 'kwargs': {'loc': star_kwargs['Teff']['value'], 'scale': star_kwargs['Teff']['error'], 'size': 'shape(nwalker,niter)'}, 'l_param_name': None}
for planet in ['b', 'c']:
      sp[f'{planet}_ecc'] = {'function': cv.getecc, 'kwargs': None, 'l_param_name': [f'{planet}_ecosw', f'{planet}_esinw']}
      sp[f'{planet}_omega'] = {'function': cv.getomega_deg, 'kwargs': None, 'l_param_name': [f'{planet}_ecosw', f'{planet}_esinw']}
      sp[f'{planet}_inc'] = {'function': cv.getinc, 'kwargs': None, 'l_param_name': [f'{planet}_cosinc', ]}
      sp[f'{planet}_aR'] = {'function': cv.getaoverr, 'kwargs': None, 'l_param_name': [f'{planet}_P', 'A_rho', f'{planet}_ecc', f'{planet}_omega']}
      sp[f'{planet}_b'] = {'function': cv.getb(), 'kwargs': None, 'l_param_name': [f'{planet}_inc', f'{planet}_aR', f'{planet}_ecc', f'{planet}_omega']}
      sp[f'{planet}_R'] = {'function': cv.getRp, 'kwargs': None, 'l_param_name': [f'{planet}_Rrat', 'A_R']}
      sp[f'{planet}_Frat'] = {'function': cv.getFrat_sincos, 'kwargs': None, 'l_param_name': [f'{planet}_A', f'{planet}_Foffset']}
      sp[f'{planet}_Phioffset'] = {'function': cv.getPhioffset_sincos, 'kwargs': {'sincos': 'cos'}, 'l_param_name': [f'{planet}_Phi', ]}
      sp[f'{planet}_M'] = {'function': cv.getMpsininc, 'kwargs': {'Kfact': 1}, 'l_param_name': [f'{planet}_P', f'{planet}_K', 'A_M', f'{planet}_ecc']}
