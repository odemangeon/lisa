import rebound
import numpy as np
import matplotlib.pyplot as pl
import astropy.constants as const

import getttv_rebold



"""
Example how to call the getttv_rebold that produces the model of the light curve and RVs
For getttv_reb we need one extra parameter that is the time of the first transit to make sure the code gets exacly that transit.

planet =1 for the b
planet =2 for the c
planet =0 DOESNOT WORK


This code compares the result with the TTVs obtained with other codes, TTVfast, idl, jose

"""

total = 57000.0
treference =  56813.0
period = 7.92008
stellar_radius = 0.926
stellar_mass = 0.97061886114722451
planet = 1

a1=0.0769897231391472
period1 = np.sqrt (a1**3/(stellar_mass))*365.2422
#print(period1)
a2= 0.1010372336036388
period2 = np.sqrt (a2**3/(stellar_mass))*365.2422
#print(period2)

N = np.int((total-treference)/period1) + 1 -1

p_parameters = [ 0.00014932535033861051 , period1 , 0.0869586103515203, np.radians(88.74540570700838), np.radians(180.0), np.radians(214.09963960544101), np.radians(227.0106215751976), 0.07451,
                 6.3494930075318071e-05, period2, 0.1124375085494681 , np.radians(88.95595877430457), np.radians(167.5154616287283)  ,  np.radians(250.7761358353399) , np.radians(74.670769462202),0.04515 ]



#day1 = 86400.0
# precision of 1 sec is 1.1574074074074073e-05

[transitimes, duration ] = getttv_rebold.getttv_rebold(p_parameters,stellar_mass,stellar_radius, N, planet, treference, precision = 1e-7  )

#A = np.vstack([np.ones(N), range(N)]).T

pl.plot(duration*24*60)
pl.show()



nt1= len(transitimes)
#nt2= len(ttv2)
transitimes = transitimes #- 50000.0
tmidsb = np.genfromtxt('/Users/sbarros/Documents/work/mercury/k350/derived_times_test7_plb.txt')
tmidsbreb = np.genfromtxt('/Users/sbarros/Documents/work/python/photodynamic/testing/times_zerob.txt')
tmidb = tmidsb.astype("float64")[0:nt1]+ 50000.0
tmidbreb = tmidsbreb.astype("float64")[0:nt1]

pl.plot(transitimes)
pl.plot(tmidb)
pl.show()

pl.plot( (transitimes-tmidb)*24*60*60, '.' )
pl.show()

planet=2
[transitimes2, duration2 ] = getttv_reb.getttv_reb(p_parameters,stellar_mass,stellar_radius, N, planet, treference, precision = 1e-7  )

transitimes2 = transitimes2# - 50000.0
nt2= len(transitimes2)

tmidsc = np.genfromtxt('/Users/sbarros/Documents/work/mercury/k350/derived_times_test7_plc.txt')
tmidscreb = np.genfromtxt('/Users/sbarros/Documents/work/python/photodynamic/testing/times_zeroc.txt')
tmidc = tmidsc.astype("float64")[0:nt2]+ 50000.0
tmidcreb = tmidscreb.astype("float64")[0:nt2]

pl.plot(transitimes2)
pl.plot(tmidc)
pl.show()

pl.plot( (transitimes2-tmidc)*24*60*60, '.' )
pl.show()

'''
# linear least square fit to remove the linear trend from the transit times, thus leaving us with the transit time variations.
A = np.vstack([np.ones(N), range(N)]).T
c, m = np.linalg.lstsq(A, transittimes)[0]


# plot the TTVs.

fig = plt.figure(figsize=(10,5))
ax = plt.subplot(111)
ax.set_xlim([0,N])
ax.set_xlabel("Transit number")
ax.set_ylabel("TTV [hours]")
plt.scatter(range(N), (transittimes-m*np.array(range(N))-c)*(24.*365./2./np.pi));
plt.show()
'''
