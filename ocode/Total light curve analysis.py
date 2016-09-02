################ This code is to get all the parameters of planet b and planet c together in the total LC data plus the RV data #######################

import statistics as stat
import numpy as np
import matplotlib.pyplot as plt
from pytransit import MandelAgol
from operator import itemgetter
import ajplanet as ap
import untrendy as ut
import emcee
import astropy.constants as cst
import corner
from lmfit import Model
import time

start_time = time.clock()


#################### Total light curve data storage ###########################

main = np.genfromtxt('LCdata.txt')
lm = len(main)

##Just storing all the data

transitsb = np.genfromtxt('transits for b.txt')
ltb = len(transitsb)
transitsc = np.genfromtxt('transits for c.txt') 
ltc = len(transitsc)
transitsboth = np.genfromtxt('transits for both.txt')
ltboth = len(transitsboth)
radial_data1 = np.genfromtxt('radial velocity data set from paper.txt')
ltradial1 = len(radial_data1)
radial_data2 = np.genfromtxt('radial velocity data set 2.txt')
ltradial2 = len(radial_data2)

toriginal=[] #just to create the list for time for total light curve 
foriginal=[]
ferroriginal=[]

for x in range(0, lm): #to get the data in separate arrays #actually should be lm instead of lm-1, we are not taking the last data point. doesn't matter anyways
    toriginal.append(main[x][0])
    foriginal.append(main[x][1])
    ferroriginal.append(main[x][2])
    
fnew, ferrnew = ut.untrend(toriginal, foriginal, ferroriginal) # the untrended lists

##################### Defining the function to generate the data files #########################

def give_me_datafiles(lmain,ltransits,transitdata,time,flux,fluxerr):
    
    final_time = []
    final_flux = []
    final_fluxerr =[]
    
    for x in range(20, lmain):
        for y in range(0,ltransits): #this will iterate for each transit
            
            if time[x] == transitdata[y] :
                minimum = fnew[20] 
                for z in range(x-20, x+20): #for abs min in each trnsit
                    if flux[z] <= minimum:
                        minimum = flux[z]
                        least_time = toriginal[z]
                        b = z
                print('The least time for the given planet is ', least_time)
                timetemp = []            
                fluxtemp =[] 
                fluxerrtemp = []
                
                for w in range(b-20, b+20): ###This is to do the normalisation for each set of transit data
                    aeta=0
                    beta=0.0
                    if flux[w] > 0.999 :
                        aeta = aeta + fnew[w]
                        beta = beta + 1
                ceta = aeta/float(beta)
                flux = flux/ceta
                
                for w in range(b-20, b+20):
                    timetemp.append(time[w])
                    fluxtemp.append(flux[w])
                    fluxerrtemp.append(fluxerr[w])
                
                final_time.append(timetemp)
                final_flux.append(fluxtemp)            
                final_fluxerr.append(fluxerrtemp)
    
    flux_array = []
    fluxerr_array = []

    for x in range(0, len(final_time)):
        for y in range(0, len(final_time[x])):

            flux_array.append(final_flux[x][y])
            fluxerr_array.append(final_fluxerr[x][y])

    flux_array = np.array(flux_array)  ###this will convert the list type to array type, imp to be used in the func
    fluxerr_array = np.array(fluxerr_array)   
    
    return final_time,final_flux,final_fluxerr,flux_array,fluxerr_array

    
#################### Just creating the data sets for each ######################
    
###### Data for light curves #######  
#### These are the lists and the array for data which is normalised ####

time_b,flux_b,fluxerr_b,flux_b_array,fluxerr_b_array = give_me_datafiles(lm,ltb,transitsb,toriginal,fnew,ferrnew)
time_c,flux_c,fluxerr_c,flux_c_array,fluxerr_c_array = give_me_datafiles(lm,ltc,transitsc,toriginal,fnew,ferrnew)
time_both,flux_both,fluxerr_both,flux_both_array,fluxerr_both_array = give_me_datafiles(lm,ltboth,transitsboth,toriginal,fnew,ferrnew)

###### Data for radial velocities ######

time_radial1 = []  
flux_radial1 = []
fluxerr_radial1 = []

time_radial2 = [] # for data 2
flux_radial2 = []
fluxerr_radial2 = []

time_radial3 = [] # for combined data
flux_radial3 = []
fluxerr_radial3 = [] 

for x in range(0, ltradial1): #to get the data in separate arrays
    time_radial1.append(radial_data1[x][0])
    flux_radial1.append(radial_data1[x][1])
    fluxerr_radial1.append(radial_data1[x][2])
    
for x in range(0, ltradial2): #to get the data in separate arrays
    time_radial2.append(radial_data2[x][0])
    flux_radial2.append(radial_data2[x][1])
    fluxerr_radial2.append(radial_data2[x][2])

time_radial3 = time_radial1 + time_radial2
flux_radial3 = flux_radial1 + flux_radial2
fluxerr_radial3 = fluxerr_radial1 + fluxerr_radial2

time_radial1 = np.array(time_radial1)
flux_radial1 = np.array(flux_radial1)
fluxerr_radial1 = np.array(fluxerr_radial1)

f2levelled = flux_radial2

time_radial2 = np.array(time_radial2)
flux_radial2 = np.array(flux_radial2)
fluxerr_radial2 = np.array(fluxerr_radial2)

time_radial3 = np.array(time_radial3)
flux_radial3 = np.array(flux_radial3)
fluxerr_radial3 = np.array(fluxerr_radial3)

###############################################################################
########################data values for constants##############################

### Data for Planet b

rad_st = 0.913 * cst.R_sun.value #from paper
kb = 0.07451 #planet-star radius ratio #from paper
u = [0.460,0.210] #quadratic limb darkening coefficients # from paper
t0b = 56813.3838955076789716 #from files given by Olivier
t1b = 56821.3041009308653884
t2b = 56837.1390043609353597
t3b = 56845.0615602324542124
t4b = 56860.9000513591236086
t5b = 56868.8208007124194410
t6b = 56884.6583386091224384
pb = 7.92 #orbital period #paper
ab = 0.0762 * cst.au.value / rad_st #0.0762  #scaled semi major axis
ib = 88.87*np.pi/180  #orbital inclination
eb = 0.119#0.119 #orbital eccentricity
wb = 179*np.pi/180 #argument of periastron

### Data for Planet c

kc = 0.04515 #planet-star radius ratio
t0c = 56817.2730369411219726 #from data given by Olivier
t1c = 56841.0922051513116457
t2c = 56864.9083268223839696
t3c = 56888.7161356498108944
pc = 11.9068 #orbital period #from paper
ac = 0.1001 * cst.au.value / rad_st #0.0762  #scaled semi major axis
ic = 88.92*np.pi/180  #orbital inclination
ec = 0.095#0.119 #orbital eccentricity
wc = 237*np.pi/180 #argument of periastron
ffunclc = 0.10093234 #(taken from iteration of planet b)

### Data for overlapping transit

t1bothb = 56829.2219446640083333 # these are taken from the data table by olivier
t2bothb = 56852.9794481836579507
t3bothb = 56876.7385602784561343

t1bothc = 56829.1834754796655034
t2bothc = 56853.0090568114028429
t3bothc = 56876.8149934560351539


### Data for Radial velocity analysis

gamma1 = 7.24
gamma2 = 7.34
Krad1 = 0.01  ## These are different from the kb and kc values. These tell the amplitude of the function in RV analysis
Krad2 = 0.005

### Defining the initial and the fixed

initial = [kc, t0c, t1c, t2c, t3c, ac, ic, ec, wc, kb, t0b, t1b, t2b, t3b, t4b, t5b, t6b, ab, ib, eb, wb, t1bothb, t1bothc, t2bothb, t2bothc, t3bothb, t3bothc, gamma1, gamma2, Krad1, Krad2]
fixed = [u, pb, pc, ffunclc]

###############################################################################
######### Defining the lnlike and the other functions and the model ###########

model = MandelAgol(nldc=2,exptime=0.02,supersampling=10)

def lnlikenew(theta_free, theta_fixed, tb, tc, tboth, tradial1, tradial2, fluxb, fluxc, fluxboth, radialdata, fluxerrb, fluxerrc, fluxerrboth, radialerr):
    
    kc, t0c, t1c, t2c, t3c, ac, ic, ec, wc, kb, t0b, t1b, t2b, t3b, t4b, t5b, t6b, ab, ib, eb, wb, t1bothb, t1bothc, t2bothb, t2bothc, t3bothb, t3bothc, gamma1, gamma2, Krad1, Krad2 = theta_free
    t_centre_b = [t0b,t1b,t2b, t3b, t4b, t5b, t6b]    
    t_centre_c = [t0c,t1c,t2c,t3c]
    u, pb, pc, ffunclc = theta_fixed
    
    ttempb = []
    for x in range(0,len(tb)): ##To get the reduced(after centralizing it at the transit centres for each) time list#########
        for y in range(0,40):
            ttempb.append(tb[x][y] - t_centre_b[x])
           
    ttempc = []
    for x in range(0,len(tc)): ##To get the reduced(after centralizing it at the transit centres for each) time list#########
        for y in range(0,40):
            ttempc.append(tc[x][y] - t_centre_c[x])
    
    modeldat1b = ap.pl_rv_array(tradial1, 0 , kb, wb, eb, t0b, pb) #data 1 for planet 1
    modeldat1c = ap.pl_rv_array(tradial1, 0, kc, wc, ec, t0c, pc) #data 1 for planet 2
    t_modeldat1 = modeldat1b + modeldat1c + gamma1
    
    modeldat2b = ap.pl_rv_array(tradial2, 0 , kb, wb, eb, t0b, pb)
    modeldat2c = ap.pl_rv_array(tradial2, 0, kc, wc, ec, t0c, pc)
    t_modeldat2 = modeldat2b + modeldat2c + gamma2   
    
    y_model_b = model.evaluate(ttempb, kb, u, 0, pb, ab, ib, eb, wb)
    y_model_c = model.evaluate(ttempc, kc, u, 0, pc, ac, ic, ec, wc)
    y_model_both1 = model.evaluate(tboth[0], kb, u, t1bothb, pb, ab, ib, eb, wb) + model.evaluate(tboth[0], kc, u, t1bothc, pc, ac, ic, ec, wc) - 1
    y_model_both2 = model.evaluate(tboth[1], kb, u, t2bothb, pb, ab, ib, eb, wb) + model.evaluate(tboth[1], kc, u, t2bothc, pc, ac, ic, ec, wc) - 1
    y_model_both3 = model.evaluate(tboth[2], kb, u, t3bothb, pb, ab, ib, eb, wb) + model.evaluate(tboth[2], kc, u, t3bothc, pc, ac, ic, ec, wc) - 1
    y_model_radial = np.concatenate((t_modeldat1,t_modeldat2))     
    
    inv_sigma_b = 1.0/((ffunclc*fluxerrb)**2) #+ y_model**2*np.exp(2*lnf))
    inv_sigma_c = 1.0/((ffunclc*fluxerrc)**2) #+ y_model**2*np.exp(2*lnf))
    inv_sigma_both1 = 1.0/((ffunclc*np.array(fluxerrboth[0]))**2)
    inv_sigma_both2 = 1.0/((ffunclc*np.array(fluxerrboth[1]))**2)
    inv_sigma_both3 = 1.0/((ffunclc*np.array(fluxerrboth[2]))**2)
    inv_sigma_radial = 1.0/((1*radialerr)**2)
   
    print("This works")
    return -(0.5*(np.sum((radialdata-y_model_radial)**2*inv_sigma_radial)))-(0.5*(np.sum((fluxb-y_model_b)**2*inv_sigma_b - np.log(inv_sigma_b)))) -(0.5*(np.sum((fluxc-y_model_c)**2*inv_sigma_c - np.log(inv_sigma_c)))) -(0.5*(np.sum((fluxboth[0] - y_model_both1)**2*inv_sigma_both1 - np.log(inv_sigma_both1)))) -(0.5*(np.sum((fluxboth[1] - y_model_both2)**2*inv_sigma_both2 - np.log(inv_sigma_both2)))) - (0.5*(np.sum(( - y_model_both3)**2*inv_sigma_both3 - np.log(inv_sigma_both3))))

   
def lnpriornew(theta_free, tmultp):
    
    kc, t0c, t1c, t2c, t3c, ac, ic, ec, wc, kb, t0b, t1b, t2b, t3b, t4b, t5b, t6b, ab, ib, eb, wb, t1bothb, t1bothc, t2bothb, t2bothc, t3bothb, t3bothc, gamma1, gamma2, Krad1, Krad2 = theta_free
    if 0 < Krad1 < 3 and 0 < Krad2 < 3 and 0 < wb < 2*np.pi and 0 < wc < 2*np.pi and 4 < gamma1 < 10 and 4 < gamma2 < 10 and tmultp[0][10] < t1bothb < tmultp[0][30] and tmultp[0][10] < t1bothc < tmultp[0][30] and tmultp[1][10] < t2bothb < tmultp[1][30] and tmultp[1][10] < t2bothc < tmultp[1][30] and tmultp[2][10] < t3bothb < tmultp[2][30] and tmultp[2][10] < t3bothc < tmultp[2][30] and 0 < kc < 0.1 and 10 < ac < 40 and 1 < ic < np.pi and 0 <= ec < 1 and 56817.156136 < t0c < 56817.456136 and 56840.9029457 < t1c < 56841.2598587 and 56864.7076936 < t2c < 56865.1037389 and 56888.5756528 < t3c < 56888.9008336 and 0 < kb < 0.1 and 15 < ab < 25 and 1 < ib < np.pi/2 and 0 <= eb < 1 and 56813.266136 < t0b < 56813.566136 and 56821.1529457 < t1b < 56821.4798587 and 56836.9876936 < t2b < 56837.2737389 and 56844.9356528 < t3b < 56845.1808336 and 56860.7497779 < t4b < 56861.0358212 and 56868.6568315 < t5b < 56868.9837383 and 56884.4914118 < t6b < 56884.7774567 :
        return 0.0            
    return -np.inf   

def lnprobnew(theta_free, theta_fixed, tb, tc, tboth, tradial1, tradial2, fluxb, fluxc, fluxboth, radialdata, fluxerrb, fluxerrc, fluxerrboth, radialerr):
    lp = lnpriornew(theta_free,tboth)
    if not np.isfinite(lp):
        return -np.inf
    ll = lnlikenew(theta_free, theta_fixed, tb, tc, tboth, tradial1, tradial2, fluxb, fluxc, fluxboth, radialdata, fluxerrb, fluxerrc, fluxerrboth, radialerr)  
    return lp + ll           

#%%
###############################################################################
############################ Emcee iteration ##################################

ndim = len(initial)
nwalkers = 100

initial0 = [initial + 1e-2*np.random.randn(ndim) for i in range(nwalkers)] 

sampler = emcee.EnsembleSampler(nwalkers, ndim, lnprobnew, args=(fixed, time_b, time_c, time_both, time_radial1, time_radial2, flux_b_array, flux_c_array, flux_both, flux_radial3, fluxerr_b_array, fluxerr_c_array, fluxerr_both, fluxerr_radial3))      
                                                                        #tb,       tc,     tboth,     tradial1,    tradial2,      fluxb,          fluxc,     fluxboth,  radialdata,       fluxerrb,       fluxerrc,    fluxerrboth,     radialerr

print("Running burn-in...")
number_of_iterations = 5000

sampler.run_mcmc(initial0, number_of_iterations)

#burnin = np.int(number_of_iterations/6)
wonderwall = sampler.lnprobability
burnin = 0

samples = sampler.chain[:, burnin:, :].reshape((-1, ndim)) #this generates the values of the varying parameters


print(' Here right now')

##%%
#### Just ignoring this for the time being ####
################################################################################
##################### Getting good walkers out of this #########################
#
#new_samples = np.zeros((nwalkers,number_of_iterations-burnin,ndim))
#temp = []  #just for putting it in new_samples  
#
#tempo =np.int(0)
#
#for x in range(0, nwalkers): ########this is to choose which walker we need to eliminate
#  #print('so far this works')  
#  if (np.percentile(sampler.chain[:,burnin:,0].T, [16]) < np.median(sampler.chain[x,burnin:,0].T) < np.percentile(sampler.chain[:,burnin:,0].T, [84])) and (np.percentile(sampler.chain[:,burnin:,1].T, [16]) < np.median(sampler.chain[x,burnin:,1].T) < np.percentile(sampler.chain[:,burnin:,1].T, [84])) and (np.percentile(sampler.chain[:,burnin:,2].T, [16]) < np.median(sampler.chain[x,burnin:,2].T) < np.percentile(sampler.chain[:,burnin:,2].T, [84])) and (np.percentile(sampler.chain[:,burnin:,3].T, [16]) < np.median(sampler.chain[x,burnin:,3].T) < np.percentile(sampler.chain[:,burnin:,3].T, [84])) and (np.percentile(sampler.chain[:,burnin:,4].T, [16]) < np.median(sampler.chain[x,burnin:,4].T) < np.percentile(sampler.chain[:,burnin:,4].T, [84])) and (np.percentile(sampler.chain[:,burnin:,5].T, [16]) < np.median(sampler.chain[x,burnin:,5].T) < np.percentile(sampler.chain[:,burnin:,5].T, [84])) and (np.percentile(sampler.chain[:,burnin:,6].T, [16]) < np.median(sampler.chain[x,burnin:,6].T) < np.percentile(sampler.chain[:,burnin:,6].T, [84])) and (np.percentile(sampler.chain[:,burnin:,7].T, [16]) < np.median(sampler.chain[x,burnin:,7].T) < np.percentile(sampler.chain[:,burnin:,7].T, [84])) and (np.percentile(sampler.chain[:,burnin:,8].T, [16]) < np.median(sampler.chain[x,burnin:,8].T) < np.percentile(sampler.chain[:,burnin:,8].T, [84])) and (np.percentile(sampler.chain[:,burnin:, 9 ].T, [16]) < np.median(sampler.chain[x,burnin:, 9 ].T) < np.percentile(sampler.chain[:,burnin:, 9 ].T, [84])) and (np.percentile(sampler.chain[:,burnin:, 10 ].T, [16]) < np.median(sampler.chain[x,burnin:, 10 ].T) < np.percentile(sampler.chain[:,burnin:, 10 ].T, [84])) and (np.percentile(sampler.chain[:,burnin:, 11 ].T, [16]) < np.median(sampler.chain[x,burnin:, 11 ].T) < np.percentile(sampler.chain[:,burnin:, 11 ].T, [84])) and (np.percentile(sampler.chain[:,burnin:, 12 ].T, [16]) < np.median(sampler.chain[x,burnin:, 12 ].T) < np.percentile(sampler.chain[:,burnin:, 12 ].T, [84])) and (np.percentile(sampler.chain[:,burnin:, 13 ].T, [16]) < np.median(sampler.chain[x,burnin:, 13 ].T) < np.percentile(sampler.chain[:,burnin:, 13 ].T, [84])) and (np.percentile(sampler.chain[:,burnin:, 14 ].T, [16]) < np.median(sampler.chain[x,burnin:, 14 ].T) < np.percentile(sampler.chain[:,burnin:, 14 ].T, [84])) and (np.percentile(sampler.chain[:,burnin:, 15 ].T, [16]) < np.median(sampler.chain[x,burnin:, 15 ].T) < np.percentile(sampler.chain[:,burnin:, 15 ].T, [84])) and (np.percentile(sampler.chain[:,burnin:, 16 ].T, [16]) < np.median(sampler.chain[x,burnin:, 16 ].T) < np.percentile(sampler.chain[:,burnin:, 16 ].T, [84])) and (np.percentile(sampler.chain[:,burnin:, 17 ].T, [16]) < np.median(sampler.chain[x,burnin:, 17 ].T) < np.percentile(sampler.chain[:,burnin:, 17 ].T, [84])) and (np.percentile(sampler.chain[:,burnin:, 18 ].T, [16]) < np.median(sampler.chain[x,burnin:, 18 ].T) < np.percentile(sampler.chain[:,burnin:, 18 ].T, [84])) and (np.percentile(sampler.chain[:,burnin:, 19 ].T, [16]) < np.median(sampler.chain[x,burnin:, 19 ].T) < np.percentile(sampler.chain[:,burnin:, 19 ].T, [84])) and (np.percentile(sampler.chain[:,burnin:, 20 ].T, [16]) < np.median(sampler.chain[x,burnin:, 20 ].T) < np.percentile(sampler.chain[:,burnin:, 20 ].T, [84])) and (np.percentile(sampler.chain[:,burnin:, 21 ].T, [16]) < np.median(sampler.chain[x,burnin:, 21 ].T) < np.percentile(sampler.chain[:,burnin:, 21 ].T, [84])) and (np.percentile(sampler.chain[:,burnin:, 22 ].T, [16]) < np.median(sampler.chain[x,burnin:, 22 ].T) < np.percentile(sampler.chain[:,burnin:, 22 ].T, [84])) and (np.percentile(sampler.chain[:,burnin:, 23 ].T, [16]) < np.median(sampler.chain[x,burnin:, 23 ].T) < np.percentile(sampler.chain[:,burnin:, 23 ].T, [84])) and (np.percentile(sampler.chain[:,burnin:, 24 ].T, [16]) < np.median(sampler.chain[x,burnin:, 24 ].T) < np.percentile(sampler.chain[:,burnin:, 24 ].T, [84])) and (np.percentile(sampler.chain[:,burnin:, 25 ].T, [16]) < np.median(sampler.chain[x,burnin:, 25 ].T) < np.percentile(sampler.chain[:,burnin:, 25 ].T, [84])) and (np.percentile(sampler.chain[:,burnin:, 26 ].T, [16]) < np.median(sampler.chain[x,burnin:, 26 ].T) < np.percentile(sampler.chain[:,burnin:, 26 ].T, [84])) and (np.percentile(sampler.chain[:,burnin:, 27 ].T, [16]) < np.median(sampler.chain[x,burnin:, 27 ].T) < np.percentile(sampler.chain[:,burnin:, 27 ].T, [84])) and (np.percentile(sampler.chain[:,burnin:, 28 ].T, [16]) < np.median(sampler.chain[x,burnin:, 28 ].T) < np.percentile(sampler.chain[:,burnin:, 28 ].T, [84])) and (np.percentile(sampler.chain[:,burnin:, 29 ].T, [16]) < np.median(sampler.chain[x,burnin:, 29 ].T) < np.percentile(sampler.chain[:,burnin:, 29 ].T, [84])) and (np.percentile(sampler.chain[:,burnin:, 30 ].T, [16]) < np.median(sampler.chain[x,burnin:, 30 ].T) < np.percentile(sampler.chain[:,burnin:, 30 ].T, [84])) : #and (np.percentile(sampler.chain[:,burnin:, 31 ].T, [16]) < np.median(sampler.chain[x,burnin:, 31 ].T) < np.percentile(sampler.chain[:,burnin:, 31 ].T, [84])) : #and (np.percentile(sampler.chain[:,burnin:, 32 ].T, [16]) < np.median(sampler.chain[x,burnin:, 32 ].T) < np.percentile(sampler.chain[:,burnin:, 32 ].T, [84])) and (np.percentile(sampler.chain[:,burnin:, 33 ].T, [16]) < np.median(sampler.chain[x,burnin:, 33 ].T) < np.percentile(sampler.chain[:,burnin:, 33 ].T, [84])) and (np.percentile(sampler.chain[:,burnin:, 34 ].T, [16]) < np.median(sampler.chain[x,burnin:, 34 ].T) < np.percentile(sampler.chain[:,burnin:, 34 ].T, [84])) and (np.percentile(sampler.chain[:,burnin:, 35 ].T, [16]) < np.median(sampler.chain[x,burnin:, 35 ].T) < np.percentile(sampler.chain[:,burnin:, 35 ].T, [84])) : #and (stat.stdev(sampler.chain[x,burnin:,0].T)/np.median(sampler.chain[x,burnin:,0].T) < 1) and (stat.stdev(sampler.chain[x,burnin:,1].T)/np.median(sampler.chain[x,burnin:,1].T) < 1) and (stat.stdev(sampler.chain[x,burnin:,2].T)/np.median(sampler.chain[x,burnin:,2].T) < 1) and (stat.stdev(sampler.chain[x,burnin:,3].T)/np.median(sampler.chain[x,burnin:,3].T) < 1)  and stat.stdev(sampler.chain[x,burnin:,4].T)/np.median(sampler.chain[x,burnin:,4].T) < 1 and stat.stdev(sampler.chain[x,burnin:,5].T)/np.median(sampler.chain[x,burnin:,5].T) < 1 and stat.stdev(sampler.chain[x,burnin:,6].T)/np.median(sampler.chain[x,burnin:,6].T) < 1 and stat.stdev(sampler.chain[x,burnin:,7].T)/np.median(sampler.chain[x,burnin:,7].T) < 1 and stat.stdev(sampler.chain[x,burnin:,8].T)/np.median(sampler.chain[x,burnin:,8].T) < 1 and stat.stdev(sampler.chain[x,burnin:, 9 ].T)/np.median(sampler.chain[x,burnin:, 9 ].T) < 1 and stat.stdev(sampler.chain[x,burnin:, 10 ].T)/np.median(sampler.chain[x,burnin:, 10 ].T) < 1 and stat.stdev(sampler.chain[x,burnin:, 11 ].T)/np.median(sampler.chain[x,burnin:, 11 ].T) < 1 and stat.stdev(sampler.chain[x,burnin:, 12 ].T)/np.median(sampler.chain[x,burnin:, 12 ].T) < 1 and stat.stdev(sampler.chain[x,burnin:, 13 ].T)/np.median(sampler.chain[x,burnin:, 13 ].T) < 1 and stat.stdev(sampler.chain[x,burnin:, 14 ].T)/np.median(sampler.chain[x,burnin:, 14 ].T) < 1 and stat.stdev(sampler.chain[x,burnin:, 15 ].T)/np.median(sampler.chain[x,burnin:, 15 ].T) < 1 and stat.stdev(sampler.chain[x,burnin:, 16 ].T)/np.median(sampler.chain[x,burnin:, 16 ].T) < 1 and stat.stdev(sampler.chain[x,burnin:, 17 ].T)/np.median(sampler.chain[x,burnin:, 17 ].T) < 1 and stat.stdev(sampler.chain[x,burnin:, 18 ].T)/np.median(sampler.chain[x,burnin:, 18 ].T) < 1 and stat.stdev(sampler.chain[x,burnin:, 19 ].T)/np.median(sampler.chain[x,burnin:, 19 ].T) < 1 and stat.stdev(sampler.chain[x,burnin:, 20 ].T)/np.median(sampler.chain[x,burnin:, 20 ].T) < 1 and stat.stdev(sampler.chain[x,burnin:, 21 ].T)/np.median(sampler.chain[x,burnin:, 21 ].T) < 1 and stat.stdev(sampler.chain[x,burnin:, 22 ].T)/np.median(sampler.chain[x,burnin:, 22 ].T) < 1 and stat.stdev(sampler.chain[x,burnin:, 23 ].T)/np.median(sampler.chain[x,burnin:, 23 ].T) < 1 and stat.stdev(sampler.chain[x,burnin:, 24 ].T)/np.median(sampler.chain[x,burnin:, 24 ].T) < 1 and stat.stdev(sampler.chain[x,burnin:, 25 ].T)/np.median(sampler.chain[x,burnin:, 25 ].T) < 1 and stat.stdev(sampler.chain[x,burnin:, 26 ].T)/np.median(sampler.chain[x,burnin:, 26 ].T) < 1 and stat.stdev(sampler.chain[x,burnin:, 27 ].T)/np.median(sampler.chain[x,burnin:, 27 ].T) < 1 and stat.stdev(sampler.chain[x,burnin:, 28 ].T)/np.median(sampler.chain[x,burnin:, 28 ].T) < 1 and stat.stdev(sampler.chain[x,burnin:, 29 ].T)/np.median(sampler.chain[x,burnin:, 29 ].T) < 1 and stat.stdev(sampler.chain[x,burnin:, 30 ].T)/np.median(sampler.chain[x,burnin:, 30 ].T) < 1 and stat.stdev(sampler.chain[x,burnin:, 31 ].T)/np.median(sampler.chain[x,burnin:, 31 ].T) < 1 and stat.stdev(sampler.chain[x,burnin:, 32 ].T)/np.median(sampler.chain[x,burnin:, 32 ].T) < 1 and stat.stdev(sampler.chain[x,burnin:, 33 ].T)/np.median(sampler.chain[x,burnin:, 33 ].T) < 1 and stat.stdev(sampler.chain[x,burnin:, 34 ].T)/np.median(sampler.chain[x,burnin:, 34 ].T) < 1 and stat.stdev(sampler.chain[x,burnin:, 35 ].T)/np.median(sampler.chain[x,burnin:, 35 ].T) < 1 :    
#    for y in range(0, ndim):  
##     temp = [] #just for putting it in new_samples  
##     temp.append(sampler.chain[x,burnin:,y])
#      new_samples[tempo,:,y] = sampler.chain[x,burnin:,y]
#    tempo = tempo + 1
#    #print('even this works')

#%%
###############################################################################
########################### The Walkers Plot ##################################

## Just correction when i removed the good walker selection
#
new_samples = samples = sampler.chain[:, burnin:, :]
tempo = nwalkers
#

plt.figure()
fig, axes = plt.subplots(31, 1, sharex=True, figsize=(8, 40))
axes[ 0 ].plot(new_samples[:tempo, :, 0].T, color="k", alpha=0.4)
axes[ 0 ].set_ylabel("$kc$")
axes[ 1 ].plot(new_samples[:tempo, :, 1 ].T, color="k", alpha=0.4)
axes[ 1 ].set_ylabel("$t0c$")
axes[ 2 ].plot(new_samples[:tempo, :, 2 ].T, color="k", alpha=0.4)
axes[ 2 ].set_ylabel("$t1c$")
axes[ 3 ].plot(new_samples[:tempo, :, 3 ].T, color="k", alpha=0.4)
axes[ 3 ].set_ylabel("$t2c$")
axes[ 4 ].plot(new_samples[:tempo, :, 4 ].T, color="k", alpha=0.4)
axes[ 4 ].set_ylabel("$t3c$")
axes[ 5 ].plot(new_samples[:tempo, :, 5 ].T, color="k", alpha=0.4)
axes[ 5 ].set_ylabel("$ac$")
axes[ 6 ].plot(new_samples[:tempo, :, 6 ].T, color="k", alpha=0.4)
axes[ 6 ].set_ylabel("$ic$")
axes[ 7 ].plot(new_samples[:tempo, :, 7 ].T, color="k", alpha=0.4)
axes[ 7 ].set_ylabel("$ec$")
axes[ 8 ].plot(new_samples[:tempo, :, 8 ].T, color="k", alpha=0.4)
axes[ 8 ].set_ylabel("$wc$")
#axes[ 9 ].plot(new_samples[:tempo, :, 9 ].T, color="k", alpha=0.4)
#axes[ 9 ].set_ylabel("$ffunclc$")
axes[ 9 ].plot(new_samples[:tempo, :, 9 ].T, color="k", alpha=0.4)
axes[ 9 ].set_ylabel("$kb$")
axes[ 10 ].plot(new_samples[:tempo, :, 10 ].T, color="k", alpha=0.4)
axes[ 10 ].set_ylabel("$t0b$")
axes[ 11 ].plot(new_samples[:tempo, :, 11 ].T, color="k", alpha=0.4)
axes[ 11 ].set_ylabel("$t1b$")
axes[ 12 ].plot(new_samples[:tempo, :, 12 ].T, color="k", alpha=0.4)
axes[ 12 ].set_ylabel("$t2b$")
axes[ 13 ].plot(new_samples[:tempo, :, 13 ].T, color="k", alpha=0.4)
axes[ 13 ].set_ylabel("$t3b$")
axes[ 14 ].plot(new_samples[:tempo, :, 14 ].T, color="k", alpha=0.4)
axes[ 14 ].set_ylabel("$t4b$")
axes[ 15 ].plot(new_samples[:tempo, :, 15 ].T, color="k", alpha=0.4)
axes[ 15 ].set_ylabel("$t5b$")
axes[ 16 ].plot(new_samples[:tempo, :, 16 ].T, color="k", alpha=0.4)
axes[ 16 ].set_ylabel("$t6b$")
axes[ 17 ].plot(new_samples[:tempo, :, 17 ].T, color="k", alpha=0.4)
axes[ 17 ].set_ylabel("$ab$")
axes[ 18 ].plot(new_samples[:tempo, :, 18 ].T, color="k", alpha=0.4)
axes[ 18 ].set_ylabel("$ib$")
axes[ 19 ].plot(new_samples[:tempo, :, 19 ].T, color="k", alpha=0.4)
axes[ 19 ].set_ylabel("$eb$")
axes[ 20 ].plot(new_samples[:tempo, :, 20 ].T, color="k", alpha=0.4)
axes[ 20 ].set_ylabel("$wb$")
axes[ 21 ].plot(new_samples[:tempo, :, 21 ].T, color="k", alpha=0.4)
axes[ 21 ].set_ylabel("$t1bothb$")
axes[ 22 ].plot(new_samples[:tempo, :, 22 ].T, color="k", alpha=0.4)
axes[ 22 ].set_ylabel("$t1bothc$")
axes[ 23 ].plot(new_samples[:tempo, :, 23 ].T, color="k", alpha=0.4)
axes[ 23 ].set_ylabel("$t2bothb$")
axes[ 24 ].plot(new_samples[:tempo, :, 24 ].T, color="k", alpha=0.4)
axes[ 24 ].set_ylabel("$t2bothc$")
axes[ 25 ].plot(new_samples[:tempo, :, 25 ].T, color="k", alpha=0.4)
axes[ 25 ].set_ylabel("$t3bothb$")
axes[ 26 ].plot(new_samples[:tempo, :, 26 ].T, color="k", alpha=0.4)
axes[ 26 ].set_ylabel("$t3bothc$")
axes[ 27 ].plot(new_samples[:tempo, :, 27 ].T, color="k", alpha=0.4)
axes[ 27 ].set_ylabel("$gamma1$")
axes[ 28 ].plot(new_samples[:tempo, :, 28 ].T, color="k", alpha=0.4)
axes[ 28 ].set_ylabel("$gamma2$")
axes[ 29 ].plot(new_samples[:tempo, :, 29 ].T, color="k", alpha=0.4)
axes[ 29 ].set_ylabel("$Krad1$")
axes[ 30 ].plot(new_samples[:tempo, :, 30 ].T, color="k", alpha=0.4)
axes[ 30 ].set_ylabel("$Krad2$")
#axes[ 31 ].plot(new_samples[:tempo, :, 31 ].T, color="k", alpha=0.4)

fig.tight_layout(h_pad=0.0)
fig.savefig(" Walkers plot complete.jpeg")

#%%
###############################################################################
############ The lnprobability plots similar to the walkers plot ############## 

plt.figure()

for x in range(0,100):
    plt.plot(wonderwall[x], color="k", alpha=0.4)




#%%
###############################################################################
####################### Getting the triangle plot #############################

just_for_corner = np.zeros((tempo,number_of_iterations-burnin,ndim)) #this is because there were some bad walkers, this won't be needed in the grand script

for y in range(0, ndim):
    for x in range(0,tempo):
        just_for_corner[x,:,y] = new_samples[x,:,y]
        
newcornersamples = just_for_corner[:, :, :].reshape((-1, ndim))
newcornersamples_new = samples

#fig = corner.corner(newcornersamples, labels=["$kc$","$t0c$","$t1c$","$t2c$","$t3c$","$ac$", "$ic$", "$ec$","$ffuncc$","$kb$","$t0b$","$t1b$","$t2b$","$t3b$","$t4b$","$t5b$","$t6b$","$ab$","$ib$","$eb$","$wb$","$ffuncb$","$t1bothb$","$t1bothc$","$t2bothb$","$t2bothc$","$t3bothb$","$t3bothc$","$ffuncboth1$","$ffuncboth2$","$ffuncboth3$","$Gamma1$","$Gamma2$","$Krad1$","$Krad2$"])
#fig = corner.corner(samples, labels=["$kc$","$t0c$","$t1c$","$t2c$","$t3c$","$ac$", "$ic$", "$ec$","$wc$","$ffuncc$","$kb$","$t0b$","$t1b$","$t2b$","$t3b$","$t4b$","$t5b$","$t6b$","$ab$","$ib$","$eb$","$wb$","$ffuncb$","$t1bothb$","$t1bothc$","$t2bothb$","$t2bothc$","$t3bothb$","$t3bothc$","$ffuncboth1$","$ffuncboth2$","$ffuncboth3$","$Gamma1$","$Gamma2$","$Krad1$","$Krad2$"])


###############################################################################
########################## Getting the values #################################

kc_same = np.percentile(newcornersamples[:,0], [50])
t0c_less,t0c_same, t0c_more = np.percentile(newcornersamples[:,1], [16,50,84])
t1c_less,t1c_same,t1c_more = np.percentile(newcornersamples[:,2], [16,50,84])
t2c_less,t2c_same,t2c_more = np.percentile(newcornersamples[:,3], [16,50,84])
t3c_less,t3c_same,t3c_more = np.percentile(newcornersamples[:,4], [16,50,84])
ac_same = np.percentile(newcornersamples[:,5], [50])
ic_same = np.percentile(newcornersamples[:,6], [50])
ec_same = np.percentile(newcornersamples[:,7], [50])
wc_same = np.percentile(newcornersamples[:,8], [50])
#ffunclc_same = np.percentile(newcornersamples[:,9], [50])
kb_same = np.percentile(newcornersamples[:,9], [50])
t0b_less,t0b_same,t0b_more = np.percentile(newcornersamples[:,10], [16,50,84])
t1b_less,t1b_same,t1b_more = np.percentile(newcornersamples[:,11], [16,50,84])
t2b_less,t2b_same,t2b_more = np.percentile(newcornersamples[:,12], [16,50,84])
t3b_less,t3b_same,t3b_more = np.percentile(newcornersamples[:,13], [16,50,84])
t4b_less,t4b_same,t4b_more = np.percentile(newcornersamples[:,14], [16,50,84])
t5b_less,t5b_same,t5b_more = np.percentile(newcornersamples[:,15], [16,50,84])
t6b_less,t6b_same,t6b_more = np.percentile(newcornersamples[:,16], [16,50,84])
ab_same = np.percentile(newcornersamples[:,17], [50])
ib_same = np.percentile(newcornersamples[:,18], [50])
eb_same = np.percentile(newcornersamples[:,19], [50])
wb_same = np.percentile(newcornersamples[:,20], [50])
#ffuncb_same = np.percentile(newcornersamples[:,22], [50])
t1bothb_less,t1bothb_same,t1bothb_more = np.percentile(newcornersamples[:,21], [16,50,84])
t1bothc_less,t1bothc_same,t1bothc_more = np.percentile(newcornersamples[:,22], [16,50,84])
t2bothb_less,t2bothb_same,t2bothb_more = np.percentile(newcornersamples[:,23], [16,50,84])
t2bothc_less,t2bothc_same,t2bothc_more = np.percentile(newcornersamples[:,24], [16,50,84])
t3bothb_less,t3bothb_same,t3bothb_more = np.percentile(newcornersamples[:,25], [16,50,84])
t3bothc_less,t3bothc_same,t3bothc_more = np.percentile(newcornersamples[:,26], [16,50,84])  
#ffuncboth1_same = np.percentile(newcornersamples[:,29], [50]) 
#ffuncboth2_same = np.percentile(newcornersamples[:,30], [50])
#ffuncboth3_same = np.percentile(newcornersamples[:,31], [50])  
gamma1_same = np.percentile(newcornersamples[:,27], [50]) 
gamma2_same = np.percentile(newcornersamples[:,28], [50])
Krad1_same = np.percentile(newcornersamples[:,29], [50])
Krad2_same = np.percentile(newcornersamples[:,30], [50])

###############################################################################
######### Defining the function to generate the centered data set #############

def give_me_centered_data(lenlist, time_centre_values, time, flux, fluxerr):
    
    t_to_plot = [] ##This is the final time data centered around the transit centre
    
    for x in range(0,lenlist):
        temp=[]
        for y in range(0,40):
            temp.append(time[x][y] - time_centre_values[x])
        t_to_plot.append(temp)
    
    tonearray = []  ## we need arrays as the function only takes arrays, hence these three respective lists
    fonearray = []
    ferronearray = []
    
    for x in range(0,lenlist): #because 4 transits
        for y in range(0,40): #because 40 data points in each transit
            tonearray.append(t_to_plot[x][y])
            fonearray.append(flux[x][y])
            ferronearray.append(fluxerr[x][y])
    
    tarray = np.array(tonearray)
    farray = np.array(fonearray)
    ferrarray = np.array(ferronearray)
    
    
    grand = [] #create a big list and then fill each accordingly
    
    for x in range(0,40*lenlist):
         grand.append([0.0,0.0,0.0])
    
    for x in range(0,40*lenlist):   ########## I have created the unsorted grand array
        grand[x][0] = tarray[x]
        grand[x][1] = farray[x]
        grand[x][2] = ferrarray[x]
       
    grand.sort(key = itemgetter(0))  
    
    final_time =[] #These are the arrays to be used to get the fit
    final_flux = []
    final_fluxerr = []
    
    for x in range(0,40*lenlist): #####This is to divide it into respective 3 arrays to get the model fit#####
        final_time.append(grand[x][0])
        final_flux.append(grand[x][1])
        final_fluxerr.append(grand[x][2])
    
    final_time = np.array(final_time)
    final_flux = np.array(final_flux)
    final_fluxerr = np.array(final_fluxerr)

    return final_time, final_flux, final_fluxerr
    
###############################################################################

time_centre_values_b = [t0b_same, t1b_same, t2b_same, t3b_same, t4b_same, t5b_same, t6b_same]
time_centre_values_c = [t0c_same, t1c_same, t2c_same, t3c_same]

print(kc_same, t0c_same, t1c_same, t2c_same, t3c_same, ac_same, ic_same, ec_same, wc_same, kb_same, t0b_same, t1b_same, t2b_same, t3b_same, t4b_same, t5b_same, t6b_same, ab_same, ib_same, eb_same, wb_same, t1bothb_same, t1bothc_same, t2bothb_same, t2bothc_same, t3bothb_same, t3bothc_same, gamma1_same, gamma2_same, Krad1_same, Krad2_same)

###############################################################################
############################### Final plots ####################################

#%%
###############################################################################
#### Getting the final plots for the data according to the parameters found here ####

for x in range (0,len(time_centre_values_b)):
    plt.figure()   
    ymodtemp = model.evaluate(time_b[x], kb_same, u, time_centre_values_b[x], pb, ab_same, ib_same, eb_same, wb_same)
    plt.plot(time_b[x], ymodtemp,"r-",time_b[x],flux_b[x],'b.')
    
for x in range (0,len(time_centre_values_c)):
    plt.figure()   
    ymodtempc = model.evaluate(time_c[x], kc_same, u, time_centre_values_c[x], pc, ac_same, ic_same, ec_same, wc_same)
    plt.plot(time_c[x], ymodtempc,"r-",time_c[x],flux_c[x],'b.')

##### Yet to do this for multiple transit case ######
time_centre_both_b = [t1bothb_same, t2bothb_same, t3bothb_same]
time_centre_both_c = [t1bothc_same, t2bothc_same, t3bothc_same]

for x in range (0, len(time_centre_both_b)):
    plt.figure()   
    ymodtempboth = model.evaluate(time_both[x], kb_same, u, time_centre_both_b[x], pb, ab_same, ib_same, eb_same, wb_same) + model.evaluate(time_both[x], kc_same, u, time_centre_both_c[x], pc, ac_same, ic_same, ec_same, wc_same) - 1
    plt.plot(time_both[x], ymodtempboth,"r-",time_both[x],flux_both[x],'b.')

################################## Getting things for the three wayword walkers ####################

### First, get the value of all the parameters ###
#the indices are 18,43,58














#%%
########################### Getting the TTV plot ##############################
                     ######       Planet b      ######

TTVdata_b = []

ab1 = 56813.3838955076789716
ab2 = ab1 + 1*pb
ab3 = ab1 + 2*pb
ab4 = ab1 + 3*pb
ab5 = ab1 + 4*pb
ab6 = ab1 + 5*pb
ab7 = ab1 + 6*pb
ab8 = ab1 + 7*pb
ab9 = ab1 + 8*pb
ab10 = ab1 + 9*pb

time_centre_values_b_TTV = [t0b_same, t1b_same, t1bothb_same, t2b_same, t3b_same, t2bothb_same, t4b_same, t5b_same, t3bothb_same, t6b_same]
predicted_b = [ab1, ab2, ab3, ab4, ab5, ab6, ab7, ab8, ab9, ab10]

for x in range(0,len(time_centre_values_b_TTV)):
    TTVdata_b.append(time_centre_values_b_TTV[x] - predicted_b[x])
    
TTVdata_b = np.array(TTVdata_b)*24*60
x_axis = np.array([0,1,2,3,4,5,6,7,8,9])

upperlimits_b = [t0b_more-t0b_same, t1b_more-t1b_same, t1bothb_more-t1bothb_same, t2b_more-t2b_same, t3b_more-t3b_same, t2bothb_more-t2bothb_same, t4b_more-t4b_same, t5b_more-t5b_same, t3bothb_more-t3bothb_same, t6b_more-t6b_same]
lowerlimits_b = [t0b_same-t0b_less, t1b_same-t1b_less, t1bothb_same-t1bothb_less, t2b_same-t2b_less, t3b_same-t3b_less, t2bothb_same-t2bothb_less, t4b_same-t4b_less, t5b_same-t5b_less, t3bothb_same-t3bothb_less, t6b_same-t6b_less]
upperlimits_b = np.array(upperlimits_b)*24*60
lowerlimits_b = np.array(lowerlimits_b)*24*60

plt.figure()
plt.xlabel('Number of transits', fontsize=18)
plt.ylabel('TTV data (in minutes)', fontsize=16)
plt.plot(x_axis, TTVdata_b,'k*')
#plt.axis([-1, 10, -400, 200]) ###This is chosen specific to our case
plt.errorbar(x_axis, TTVdata_b, yerr=np.array([lowerlimits_b,upperlimits_b]))
#plt.savefig('TTV so far for planet c.png')

########################### Getting the TTV plot ##############################
                     ######       Planet c      ######

TTVdata_c = []

ac1 = 56817.2730369411219726 
ac2 = ac1 + 1*pc
ac3 = ac1 + 2*pc
ac4 = ac1 + 3*pc
ac5 = ac1 + 4*pc
ac6 = ac1 + 5*pc
ac7 = ac1 + 6*pc

time_centre_values_c_TTV = [t0c_same, t1bothc_same, t1c_same, t2bothc_same, t2c_same, t3bothc_same, t3c_same]
predicted_c = [ac1, ac2, ac3, ac4, ac5, ac6, ac7]

for x in range(0,len(time_centre_values_c_TTV)):
    TTVdata_c.append(time_centre_values_c_TTV[x] - predicted_c[x])
    
TTVdata_c = np.array(TTVdata_c)*24*60
x_axis = np.array([0,1,2,3,4,5,6])

upperlimits_c = [t0c_more-t0c_same,t1bothc_more-t1bothc_same,t1c_more-t1c_same,t2bothc_more-t2bothc_same,t2c_more-t2c_same, t3bothc_more-t3bothc_same, t3c_more-t3c_same]
lowerlimits_c = [t0c_same-t0c_less, t1bothc_same - t1bothc_less, t1c_same-t1c_less, t2bothc_same-t2bothc_less, t2c_same-t2c_less, t3bothc_same-t3bothc_less, t3c_same-t3c_less]
upperlimits_c = np.array(upperlimits_c)*24*60
lowerlimits_c = np.array(lowerlimits_c)*24*60

plt.figure()
plt.xlabel('Number of transits', fontsize=18)
plt.ylabel('TTV data (in minutes)', fontsize=16)
plt.plot(x_axis, TTVdata_c,'k*')
plt.errorbar(x_axis, TTVdata_c, yerr=np.array([lowerlimits_c,upperlimits_c]))
#plt.savefig('TTV so far for planet c.png')

############################################################################### 

print( time.clock() - start_time, "seconds")











