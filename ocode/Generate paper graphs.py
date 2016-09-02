################ This is to get the graphs for data according to the paper parameters #######################

import statistics as stat
import numpy as np
import matplotlib.pyplot as plt
from pytransit import MandelAgol
from operator import itemgetter
import ajplanet as ap
import untrendy as ut
#import emcee
import astropy.constants as cst
import corner
from lmfit import Model

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
                for z in range(x-14, x+14): #for abs min in each trnsit
                    if flux[z] <= minimum:
                        minimum = flux[z]
                        least_time = toriginal[z]
                        b = z
                print('The least time for the given planet is ', least_time)
                timetemp = []            
                fluxtemp =[] 
                fluxerrtemp = []
                fluxtempfornormalisation = []
                
                for w in range(b-14, b+14):
                    fluxtempfornormalisation.append(flux[w])
                
                for w in range(b-12, b+12): ###This is to do the normalisation for each set of transit data
                    aeta=0
                    beta=0.0
                    if flux[w] > 0.999 :
                        aeta = aeta + fnew[w]
                        beta = beta + 1
                ceta = aeta/float(beta)
                fluxtempfornormalisation = fluxtempfornormalisation/ceta
                
                for w in range(b-14, b+14):
                    timetemp.append(time[w])
#                    fluxtemp.append(flux[w])
                    fluxerrtemp.append(fluxerr[w])
                for k in range(0,28):
                    fluxtemp.append(fluxtempfornormalisation[k])
                
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

rad_st = 0.913 * cst.R_sun.value
kb = 0.0753 #planet-star radius ratio
u = [0.460,0.210] #quadratic limb darkening coefficients
t0b = 56813.3838955076789716
t1b = 56821.3041009308653884
t2b = 56837.1390043609353597
t3b = 56845.0615602324542124
t4b = 56860.9000513591236086
t5b = 56868.8208007124194410
t6b = 56884.6583386091224384
pb = 7.919 #orbital period
ab = 0.077 * cst.au.value / rad_st #0.0762  #scaled semi major axis
ib = 88.83*np.pi/180  #orbital inclination
eb = 0.119#0.119 #orbital eccentricity
wb = 179*np.pi/180 #argument of periastron

### Data for Planet c

kc = 0.04515 #planet-star radius ratio
t0c = 56817.2730369411219726
t1c = 56841.0922051513116457
t2c = 56864.9083268223839696
t3c = 56888.7161356498108944
pc = 11.90727 #orbital period
ac = 0.1001 * cst.au.value / rad_st #0.0762  #scaled semi major axis
ic = 88.92*np.pi/180  #orbital inclination
ec = 0.095#0.119 #orbital eccentricity
wc = 237*np.pi/180 #argument of periastron
ffunclc = 1

###Data for overlapping transit

t1bothb = 56829.2219446640083333
t2bothb = 56852.9794481836579507
t3bothb = 56876.7385602784561343

t1bothc = 56829.1834754796655034
t2bothc = 56853.0090568114028429
t3bothc = 56876.8149934560351539


### Data for Radial velocity analysis

gamma1 = 7.20
gamma2 = 7.32
Krad1 = 0.05  ## These are different from the kb and kc values. These tell the amplitude of the function in RV analysis
Krad2 = 0.04

###############################################################################
######################## Print the graphs in a loop ##############################

model = MandelAgol(nldc=2,exptime=0.02,supersampling=10)

time_centre_values_b = [t0b, t1b, t2b, t3b, t4b, t5b, t6b]
time_centre_values_c = [t0c, t1c, t2c, t3c]
time_centre_values_bothb = [t1bothb,t2bothb,t3bothb]
time_centre_values_bothc = [t1bothc,t2bothc,t3bothc]

###plot for planet b :
for x in range(0,len(time_centre_values_b)):
    plt.figure()
    ymodb = model.evaluate(time_b[x], kb, u, time_centre_values_b[x], pb, ab, ib, eb, wb)
    plt.plot(time_b[x], ymodb,"r-",time_b[x],flux_b[x],'b.')
#    plt.savefig('Plot according to paper planet b transit  number.png')
#    plt.savefig('Plot according to paper planet b transit.png')

###plot for planet c :
for x in range(0,len(time_centre_values_c)):
    plt.figure()
    ymod = model.evaluate(time_c[x], kc, u, time_centre_values_c[x], pc, ac, ic, ec, wc)
    plt.plot(time_c[x], ymod,"r-",time_c[x],flux_c[x],'b.')
#    plt.savefig('Plot according to paper planet c transit number.png')
 
##################### Special load for these: ##########################
 
k1orig = 0.0753 #planet-star radius ratio
t1_initials = [ 56829.2219446640083333, 56852.9794481836579507, 56876.7385602784561343]
p1 = 7.919 #orbital period
a1orig = 0.077 * cst.au.value / rad_st #0.0762  #scaled semi major axis
i1orig = 88.83*np.pi/180  #orbital inclination
e1orig = 0.119#0.119 #orbital eccentricity
w1 = 179*np.pi/180 #argument of periastron

k2orig = 0.04515 #planet-star radius ratio
u = [0.460,0.210] #quadratic limb darkening coefficients
t2_initials = [ 56829.1834754796655034, 56853.0090568114028429, 56876.8149934560351539]
p2 = 11.90727 #orbital period
a2orig = 0.1001 * cst.au.value / rad_st #0.0762  #scaled semi major axis
i2orig = 88.92*np.pi/180  #orbital inclination
e2orig = 0.095#0.119 #orbital eccentricity
w2 = 237*np.pi/180 #argument of periastron

   
###plot for planet both :
for x in range(0,len(time_centre_values_bothb)):
    plt.figure()
    y_model = model.evaluate(time_both[x], kb, u, time_centre_values_bothb[x], pb, ab, ib, eb, wb) + model.evaluate(time_both[x] , kc, u, time_centre_values_bothc[x], pc, ac, ic, ec, wc) - 1
#    y_real_parameters = model.evaluate(time_both[x], k1orig, u, t1_initials[x], p1, a1orig, i1orig, e1orig, w1) + model.evaluate(time_both[x] , k2orig, u, t2_initials, p2, a2orig, i2orig, e2orig, w2) - 1    
#    plt.plot(time_both[x], y_real_parameters,"r-",time_both[x],flux_both[x],'b.',time_both[x],y_model,'k--')
    plt.plot(time_both[x],flux_both[x],'b.',time_both[x],y_model,'k--')
#    plt.savefig('Plot according to paper both planet transit  number.png')
    
############################ Getting the TTV plot #############################
                            #### Planet b #### 
    
## Maybe they have used some other time centre values for the TTV estimations ##
    
TTVdata_b = []

ab1 = 56813.376721
pb = 7.92110169
ab2 = ab1 + 1*pb
ab3 = ab1 + 2*pb
ab4 = ab1 + 3*pb
ab5 = ab1 + 4*pb
ab6 = ab1 + 5*pb
ab7 = ab1 + 6*pb
ab8 = ab1 + 7*pb
ab9 = ab1 + 8*pb
ab10 = ab1 + 9*pb

time_centre_values_b_TTV = [t0b, t1b, t1bothb, t2b, t3b, t2bothb, t4b, t5b, t3bothb, t6b]
predicted_b = [ab1, ab2, ab3, ab4, ab5, ab6, ab7, ab8, ab9, ab10]

for x in range(0,len(time_centre_values_b_TTV)):
    TTVdata_b.append(time_centre_values_b_TTV[x] - predicted_b[x])
    
TTVdata_b = np.array(TTVdata_b)*24*60
x_axis = np.array([0,1,2,3,4,5,6,7,8,9])
upperlimitsb = [0.0005585785969845,0.0008791846910415, 0.0002534676834184, 0.0006372914278161, 0.0005320498244885, 0.0028462642846763, 0.0007894176934222, 0.0005210950765868, 0.0006465197000488, 0.0007990258610736]
lowerlimitsb = [0.0005585785969845,0.0008791846910415, 0.0002534676834184, 0.0006372914278161, 0.0005320498244885, 0.0028462642846763, 0.0007894176934222, 0.0005210950765868, 0.0006465197000488, 0.0007990258610736]
upperlimitsb = np.array(upperlimitsb)*24*60
lowerlimitsb = np.array(lowerlimitsb)*24*60

plt.figure()
plt.xlabel('Number of transits', fontsize=18)
plt.ylabel('TTV data (in minutes)', fontsize=16)
plt.plot(x_axis, TTVdata_b,'r-') 
plt.errorbar(x_axis, TTVdata_b, yerr=np.array([lowerlimitsb,upperlimitsb]))
                   
                                                        
###############################################################################                            
                            #### Planet c ####
TTVdata_c = []

ac1 = 56817.275522
pc = 11.9072758
ac2 = ac1 + 1*pc
ac3 = ac1 + 2*pc
ac4 = ac1 + 3*pc
ac5 = ac1 + 4*pc
ac6 = ac1 + 5*pc
ac7 = ac1 + 6*pc

time_centre_values_c_TTV = [t0c, t1bothc, t1c, t2bothc, t2c, t3bothc, t3c]
predicted_c = [ac1, ac2, ac3, ac4, ac5, ac6, ac7]

for x in range(0,len(time_centre_values_c_TTV)):
    TTVdata_c.append(time_centre_values_c_TTV[x] - predicted_c[x])
    
TTVdata_c = np.array(TTVdata_c)*24*60
x_axis = np.array([0,1,2,3,4,5,6])

upperlimitsc = [0.0014710560102536, 0.0013088201265999, 0.0014487374350743, 0.0076791273426557, 0.0018847471253605, 0.0013706851050895, 0.0013014019232472]
lowerlimitsc = [0.0014710560102536, 0.0013088201265999, 0.0014487374350743, 0.0076791273426557, 0.0018847471253605, 0.0013706851050895, 0.0013014019232472]
upperlimitsc = np.array(upperlimitsc)*24*60
lowerlimitsc = np.array(lowerlimitsc)*24*60

plt.figure()
plt.xlabel('Number of transits', fontsize=18)
plt.ylabel('TTV data (in minutes)', fontsize=16)
plt.plot(x_axis, TTVdata_c,'k-')
plt.errorbar(x_axis, TTVdata_c, yerr=np.array([lowerlimitsc,upperlimitsc]))
#plt.axis([-1, 7, -25, 15]) ###This is chosen specific to our case
#plt.errorbar(x_axis, TTVdata, yerr=np.array([lowerlimits,upperlimits]))
#plt.savefig('TTV so far for planet c.png')
    
    