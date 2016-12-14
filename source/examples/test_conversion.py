#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module to test convert system parameters module and exemplify usage

@package tools
@ingroup convert

@brief Module to test convert system parameters module and exemplify usage
@details It uses the example of WASP-10 the values calculated by the already tested IDL code are below for comparion
        it stars with the values that we know from other terms and from the fit of the light curve with the normal parametrisation

@file
@author Susana Barros
@date Decembre 14, 2016
@version 1.0
@todo: tested a circular case so maybe test eccentric but the one with distribution including eccentric seams ok so maybe not needed.

"""


import numpy as np
from source.tools import convert as ct
#import math
#import scipy.constants as konst
#Code that converts the fitted parameters to the ones we want




#parameters for WASP-10b
epoch=    54664.03723440623
dperiod= 0.00000029
per= 3.0927287820879963 + np.random.normal(loc=0.0, scale=dperiod, size=1000)

P=per*24.*3600.0

ecc = 0.0000000 + np.random.normal(loc=0.0, scale=0.01, size=1000)
omega =  0.0000000 + np.random.normal(loc=0.0, scale=30, size=1000)

dar=  0.08
ar=     11.895 + np.random.normal(loc=0.0, scale=dar, size=1000)


'''
plt.plot(ar)
plt.show()

plt.hist(ar, 50)
plt.show()
'''

dpp =  0.000357
pp =  0.157581 + np.random.normal(loc=0.0, scale=dpp, size=1000)
dinc= 0.124
inc =  88.66 + np.random.normal(loc=0.0, scale=dinc, size=1000)


teff=4675.0 + np.random.normal(loc=0.0, scale=50.0, size=1000)
dvel=9.2
velocity=520.1+ np.random.normal(loc=0.0, scale=dvel, size=1000)


# testing the converstions
b = ct.getb( inc, ar, ecc, omega )
print('b', np.median(b))

dms=0.04
ms=0.75 + np.random.normal(loc=0.0, scale=dms, size=1000)
dmp =0.27
mp=3.15 + np.random.normal(loc=0.0, scale=dmp, size=1000)

au=1.495978707e11
a0=  ct.geta0( per, ms, mp )
print('a0', np.median(a0/au))

rstar = ct.getrstar (ar, a0)
print('rstar',np.median(rstar))


tkip = ct.getdurkip (per,  inc, ar, ecc, omega )
print('tkip',np.median(tkip))
t14 = ct.gett14(per,  inc, ar, ecc, omega, pp )
print('t14',np.median(t14))
t12 = ct.gett12(per,  inc, ar, ecc, omega, pp )
print('t12',np.median(t12))

denstar = ct.getdenstar(per, ar)
print('denstar',np.median(denstar))
rprjup = ct.getrpjup(pp, rstar)
print('rprjup',np.median(rprjup))


plsurfaceg = ct.getplsurfaceg(per, ar, pp, inc,  ecc, velocity )
print('plsurfaceg',np.median(plsurfaceg))
logg = ct.getlogg(per, ar, rstar )
print('logg',np.median(logg))

tequ = ct.gettequ(teff, ar)
print('tequ',np.median(tequ))

cirtime = ct.getcirtime(per, ms,rstar, mp, pp)
print('cirtime',np.median(cirtime))



'''
  den            2.3590986694825058  +  0.0528889730200257  -  0.0473123395939758

RESULTS DERIVED OF MCMC
    b            0.2772870489888264  +  0.0213668298315106  -  0.0250423225920893
Tdura            2.2362719846748149  +  0.0051057004817592  -  0.0050716104836925
  T23            1.5816693174848235  +  0.0061191425540996  -  0.0063354727210843
 TKip            1.9109797717068713  +  0.0020236737944139  -  0.0021025017243947
Rstar            0.6771840152515501  +  0.0302093532231356  -  0.0306235595201373
Mstar                     0.7300000  +           0.0400000  -           0.0280000
  T equilibrium          958.4794859373282634  +  3.3900238613152851  -  3.3308783723380202
   a0            0.0374460454650040  +  0.0015332429231952  -  0.0017919644712762
  log g of star            4.6408623945689396  +  0.0194774603817791  -  0.0219012491539257
   Rp            1.0382915641062587  +  0.0451554981453604  -  0.0502727842018674
   Mp            3.1448541575370101  +  0.2709772767917880  -  0.2911348768101494
 denp            2.8097724463950953  +  0.4351590644724399  -  0.3304052622071625
surf            72.3197062499132386  +  1.9574464953411734  -  1.9247303667106763
   Circulization timescale 10^5 and 10^6            0.0644985919645167            0.6449859196451674






#ptest with just numbers
epoch=    54664.03723440623
per= 3.0927287820879963

P=per*24.*3600.0

ecc = 0.0000000
omega =  0.0000000

ar=     11.895
dar=  0.08
pp =  0.157581
dpp =  0.000357
inc =  88.66
dinc= 0.124

teff=4675.0
velocity=520.1


# testing the converstions
b = ct.getb( inc, ar, ecc, omega )
print('b', b))

ms=0.75
dms=0.04
mp=3.15
au=1.495978707e11
a0=  ct.geta0( per, ms, mp )
print('a0', a0/au)

rstar = ct.getrstar (ar, a0)
print('rstar',rstar)


tkip = ct.getdurkip (per,  inc, ar, ecc, omega )
print('tkip',tkip)
t14 = ct.gett14(per,  inc, ar, ecc, omega, pp )
print('t14',t14)
t12 = ct.gett12(per,  inc, ar, ecc, omega, pp )
print('t12',t12)

denstar = ct.getdenstar(per, ar)
print('denstar',denstar)
rprjup = ct.getrpjup(pp, rstar)
print('rprjup',rprjup)


plsurfaceg = ct.getplsurfaceg(per, ar, pp, inc,  ecc, velocity )
print('plsurfaceg',plsurfaceg)
logg = ct.getlogg(per, ar, rstar )
print('logg',logg)

tequ = ct.gettequ(teff, ar)
print('tequ',tequ)

cirtime = ct.getcirtime(per, ms,rstar, mp, pp)
print('cirtime',cirtime)



'''
