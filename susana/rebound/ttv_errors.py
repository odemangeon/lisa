import rebound
import numpy as np
import matplotlib.pyplot as pl
import astropy.constants as const

import getttv_reb
from scipy import stats

from distribution_anali import getconfi

"""
Calculates transit times and durations using a simulation given the orbital paramters of the system for one of the planet of a chains
to calculate also errors for these quantaties.

inputs:
chain  = a few values from a mcmc chain to calculate errors from
list of parameters that are in the mcmc chain
planet  = which planet to calculate values for

planet =1 for the b
planet =2 for the c
planet =0 DOESNOT WORK

treference =  reference time of the paramters
first = first transit to consider
total = when it finishes to search for transits
conf_level = of the errors given, 1 = 1 sigma, 2 = 2 sigma , 3 = 3 sigma
filename name of the file to write the transit times errors and durations and errors
Transit_times   error_left    error_right   duration error_left    error_right


output:
list of 2 matrices  [etimes ,   edur]
etimes[jj,0] - times (days)
etimes[jj,1] - errors left
etimes[jj,2]  - errors right
edur[jj,0]  -  duration  (days)
edur[jj,1]  - errors left
edur[jj,2]- errors right



This code calls
 getttv_reb to force the first time to be the same for all the simulations.

This might need work testing with real chains.

TO DO
It should be made into a function once we have a example chains
Use confidence limit as parameters
print to file and send variable


"""


#def ttv_errors(chain,planet, treference, first,total, conf_level, filename ):



total = 60000.0
treference =  56813.0
planet = 2
conf_level = 1 # choose confidence level to calculate the errors
first = 56817.28121
filename = 'transit_dur_k2_10c.txt'
#chains given

#calculate number of planets from number of parameters
nplanets = 2

#nchain = len(chain)
nchains = 1000



#stellar_radius = np.random.normal(0.913,0.094 , nchains)
#stellar_mass = np.random.normal( 0.949, 0.077, nchains)

stellar_radius = np.random.normal(0.913,0.00094 , nchains)
stellar_mass = np.random.normal( 0.949, 0.00077, nchains)


a = np.zeros((nplanets,nchains),dtype=float)
period = np.zeros((nplanets,nchains),dtype=float)
pmass = np.zeros((nplanets,nchains),dtype=float)
ecc = np.zeros((nplanets,nchains),dtype=float)
omega = np.zeros((nplanets,nchains),dtype=float)
inc = np.zeros((nplanets,nchains),dtype=float)
Omega = np.zeros((nplanets,nchains),dtype=float)
meanano = np.zeros((nplanets,nchains),dtype=float)
rp = np.zeros((nplanets,nchains),dtype=float)




a[0,:] = np.random.normal(0.0762,0.0022 , nchains)
a[1,:] = np.random.normal(0.1001,0.0029 ,nchains)


pmass[0,:] = np.random.normal(44 , 12 ,nchains)
pmass[1,:] = np.random.normal( 15.9 ,3 , nchains)

pmass =pmass.clip(min=0.1)

pmass = pmass*const.M_earth.value/const.M_sun.value

ecc[0,:] = np.random.normal( 0.119,0.035 ,nchains)
ecc[1,:] = np.random.normal( 0.095,0.035 ,nchains)

ecc = ecc.clip(min=0)

#omega[0,:] = np.random.normal(179.0,52.0 ,nchains)
#omega[1,:] = np.random.normal( 237.0, 15.0,nchains)

omega[0,:] = np.random.normal(179.0,0.5 ,nchains)
omega[1,:] = np.random.normal( 237.0, 0.15,nchains)

inc[0,:] = np.random.normal(88.87, 0.16,nchains)
inc[1,:] = np.random.normal(88.92,0.14 ,nchains)

#Omega[0,:] = np.random.normal( 180.0,0.0001 ,nchains)
#Omega[1,:] = np.random.normal( 173.1,  3.0,nchains)

Omega[0,:] = np.random.normal( 180.0,0.00001 ,nchains)
Omega[1,:] = np.random.normal( 173.1,  0.03,nchains)

#meanano[0,:] = np.random.normal(253.0, 27.0,nchains)
#meanano[1,:] = np.random.normal( 110.0, 35.0,nchains)

meanano[0,:] = np.random.normal(253.0, 0.27,nchains)
meanano[1,:] = np.random.normal( 110.0, 0.35,nchains)

rp[0,:] = np.random.normal( 0.07451, 0.00045,nchains)
rp[1,:] = np.random.normal( 0.04515,7.3e-4 , nchains)

#period[0,:] = np.random.normal( 7.92008,4.0e-4, nchains)
#period[1,:] = np.random.normal( 11.9068,0.0013 ,nchains)


period[0,:] = np.random.normal( 7.92008,4.0e-6, nchains)
period[1,:] = np.random.normal( 11.9068,0.000013 ,nchains)

#period[0,:] = np.sqrt (a[0,:]**3/(stellar_mass[:]))*365.2422
#period[1,:] = np.sqrt (a[1,:]**3/(stellar_mass[:]))*365.2422



N = np.int((total-first)/np.mean(period[planet-1,:])) + 1

transittimes = np.zeros((N,nchains),dtype=float)
duration = np.zeros((N,nchains),dtype=float)


'''
for jj in range(0, nchains):
for jj in range(0, nchains):
    p_parameters = [ pmass[0,jj] ,period[0,jj] , ecc[0,jj], np.radians(inc[0,jj]), np.radians(Omega[0,jj]) , np.radians(omega[0,jj]) , np.radians(meanano[0,jj]), rp[0,jj] ]
    for ll in range(1,nplanets):
        p_parameters.extend([ pmass[ll,jj] ,period[ll,jj] , ecc[ll,jj], np.radians(inc[ll,jj]), np.radians(Omega[ll,jj]) , np.radians(omega[ll,jj]) , np.radians(meanano[ll,jj]), rp[ll,jj] ])
'''
# get transit times and duration for each chain
for jj in range(0, nchains):

    p_parameters = [  0.00014932535033861051 ,period[0,jj] , ecc[0,jj], np.radians(inc[0,jj]), np.radians(Omega[0,jj]) , np.radians(omega[0,jj]) , np.radians(meanano[0,jj]), rp[0,jj] ]
    for ll in range(1,nplanets):
        p_parameters.extend([ 6.3494930075318071e-05 ,period[ll,jj] , ecc[ll,jj], np.radians(inc[ll,jj]), np.radians(Omega[ll,jj]) , np.radians(omega[ll,jj]) , np.radians(meanano[ll,jj]), rp[ll,jj] ])


    #print('chain', jj)
    [tt, dur ] = getttv_reb.getttv_reb(p_parameters,stellar_mass[jj],stellar_radius[jj], N, planet, treference, first, precision = 1e-7  )
    transittimes[:, jj] = tt
    duration[:, jj] = dur


etimes = np.zeros((N,3),dtype=float)
edur = np.zeros((N,3),dtype=float)

# get confidence limits for times and durations
for jj in range(0,N):
    dis_right, loc, dis_left = getconfi(transittimes[jj,: ] , conf_level)
    etimes[jj,:] = loc, dis_left,  dis_right

    dis_right, loc, dis_left = getconfi(duration[jj,: ] , conf_level)
    edur[jj,:] = loc, dis_left,  dis_right





# write to file
fp = open(filename, 'w')
fp.write('#Transit_times   error_left    error_right   duration error_left    error_right \n')
for jj in range(0,N):
    fp.write('%.30f\t%.30f\t%.30f\t%.30f\t%.30f\t%.30f \n'%(etimes[jj,0] ,etimes[jj,1] ,etimes[jj,2] , edur[jj,0], edur[jj,1] ,edur[jj,2] ))
fp.close()


# return  [etimes ,   edur]


'''


x = np.arange(0,N,1)
result = np.polyfit(x, etimes[:,0], 1)

pl.errorbar(x, etimes[:,0]-np.polyval(result, x), yerr=[etimes[:,1],etimes[:,2]] , fmt=".k", capsize=0)
pl.show()

pl.errorbar(x, edur[:,0], yerr=[edur[:,1],edur[:,2]], fmt=".k", capsize=0)
pl.show()






pl.hist(transittimes[0, :])
pl.show()

pl.hist(duration[0, :])
pl.show()





a[0,:] = np.random.normal(0.0769897231391472,0.0022 , nchains)
a[1,:] = np.random.normal( 0.1010372336036388,0.0029 ,nchains)


pmass[0,:] = np.random.normal(0.00014932535033861051 ,0.000014, nchains)
pmass[1,:] = np.random.normal( 6.3494930075318071e-05 ,6.349e-6, nchains)

ecc[0,:] = np.random.normal( 0.0869586103515203,0.035 ,nchains)
ecc[1,:] = np.random.normal( 0.1124375085494681,0.035 ,nchains)

ecc = ecc.clip(min=0)

omega[0,:] = np.random.normal(214.09963960544101,52.0 ,nchains)
omega[1,:] = np.random.normal( 167.5154616287283, 15.0,nchains)

inc[0,:] = np.random.normal(88.74540570700838, 0.16,nchains)
inc[1,:] = np.random.normal(88.95595877430457,0.14 ,nchains)

Omega[0,:] = np.random.normal( 180.0,0.0001 ,nchains)
Omega[1,:] = np.random.normal( 167.5154616287283, 3.0,nchains)

meanano[0,:] = np.random.normal( 227.0106215751976, 27.0,nchains)
meanano[1,:] = np.random.normal( 250.7761358353399, 35.0,nchains)

rp[0,:] = np.random.normal( 0.07451, 0.00045,nchains)
rp[1,:] = np.random.normal( 0.04515,7.3e-4 , nchains)
'''
