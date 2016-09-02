################ This script is to get all the parameters of planet c #######################

#import correct_time as ct
import numpy as np
import statistics as stat
import matplotlib.pyplot as plt
from pytransit import MandelAgol
from operator import itemgetter
import untrendy as ut
import emcee
import astropy.constants as cst
import corner
#from lmfit import Model
 
#############To get the grand data into list of list for the planet #########

main = np.genfromtxt('LCdata.txt') #store all the info in this list of lists
lm = len(main)
transits = np.genfromtxt('transits for c.txt') #store all the transit centre values obtained from the paper
lt = len(transits)

toriginal=[] #just to create the list for time from the grand list 
foriginal=[]
ferroriginal=[]
f1 = [] #flux
ferr1 = [] #fluxerr
treal = [] #list os list with real time values

for x in range(0, lm-1): #to get the data in separate arrays #actually should be lm instead of lm-1, we are not taking the last data point. doesn't matter anyways
    toriginal.append(main[x][0])
    foriginal.append(main[x][1])
    ferroriginal.append(main[x][2])
    
fnew, ferrnew = ut.untrend(toriginal, foriginal, ferroriginal)

for x in range(20, lm-1):#######chenged here for c from lm-1 to lm
    for y in range(0,lt): #this will iterate for each transit
        
        if toriginal[x] == transits[y] :
            minimum = fnew[x] 
            for z in range(x-20, x+20): #for abs min in each trnsit
                if fnew[z] < minimum:
                    minimum = fnew[z]
                    least_time = toriginal[z]
                    b = z
            print('The least time is ', least_time)
            xx = 0
            f =[]
            fnottrended = []
            ferrrr = []
            time = []

            for w in range(b-20, b+20): ###This is to do the normalisation for each set of transit data
                aeta=0
                beta=0.0
                if fnew[w] > 0.999 :
                    aeta = aeta + fnew[w]
                    beta = beta + 1
            ceta = aeta/float(beta)
            fnew = fnew/ceta
            
            for w in range(b-20, b+20):
                time.append(toriginal[w])
                f.append(fnew[w])
                ferrrr.append(ferrnew[w])
                fnottrended.append(foriginal[w])
            
            plt.figure()
#            plt.plot(time,f,'b.',time, fnottrended,'r.')
            plt.plot(time,f,'b.')
            treal.append(time)
            ferr1.append(ferrrr)
            f1.append(f)
#%%
#Now we have data for separate transits in separate lists of lists in treal, f1 and ferr1.
#Use it together to get total iteration as discussed with Olivier

##### This is the method to be followed to generate the transit centres of each transit through iteration #####
######################### (To do what olivier asked me to do) #############################
###########################################################################################
#%%
tochanges = [] 
fochanges = []
ferrochanges = []

for x in range(0, len(treal)):
    for y in range(0, len(treal[x])):

        tochanges.append(treal[x][y])
        fochanges.append(f1[x][y])
        ferrochanges.append(ferr1[x][y])

fochanges = np.array(fochanges)  ###this will convert the list type to array type, imp to be used in the func
ferrochanges = np.array(ferrochanges)      #We use these when we run the MCMC  
#########use these arrays instead#######
##########define the new functions################

model = MandelAgol(nldc=2,exptime=0.02,supersampling=10)

def lnlikenew(theta_free, theta_fixed, tfunc, yfunc, yerrfunc):
    k, t00, t1, t2, t3, a, i, e, ffunc = theta_free
    t0 = [t00,t1,t2,t3]
    u, p, w  = theta_fixed
    ttemp = []
    for x in range(0,4): ##To get the reduced(after centralizing it at the transit centres for each) time list#########
        for y in range(0,40):
            ttemp.append(treal[x][y] - t0[x])
            
    t01 = 0
    y_model = model.evaluate(ttemp, k, u, t01, p, a, i, e, w)
    inv_sigma = 1.0/((ffunc*yerrfunc)**2) #+ y_model**2*np.exp(2*lnf))
    return -0.5*(np.sum((yfunc-y_model)**2*inv_sigma - np.log(inv_sigma)))
    
def lnpriornew(theta_free):
    k, t00, t1, t2, t3, a, i, e, ffunc = theta_free
    if  0.01 < ffunc < 10 and 0 < k < 0.1 and 10 < a < 50 and 0 < i < np.pi and 0 <= e < 1 and 56817.156136 < t00 < 56817.456136 and 56840.9029457 < t1 < 56841.2598587 and 56864.7076936 < t2 < 56865.1037389 and 56888.5756528 < t3 < 56888.9008336 :
        return 0.0            
    return -np.inf   

def lnprobnew(theta_free, theta_fixed, tfunc, yfunc, yerrfunc):
    lp = lnpriornew(theta_free)
    if not np.isfinite(lp):
        return -np.inf
    ll = lnlikenew(theta_free, theta_fixed, tfunc, yfunc, yerrfunc)
    return lp + ll           

################data values for constants#####################
#%%
rad_st = 0.913 * cst.R_sun.value
k = 0.04515 #planet-star radius ratio
u = [0.460,0.210] #quadratic limb darkening coefficients
t00 = 56817.3117096
t1 = 56841.0944837
t2 = 56864.9178366
t3 = 56888.7207959
p = 11.90727 #orbital period
a = 0.1001 * cst.au.value / rad_st #0.0762  #scaled semi major axis
i = 88.92*np.pi/180  #orbital inclination
e = 0.095#0.119 #orbital eccentricity
w = 237*np.pi/180 #argument of periastron
ffunc = 1

initial = [k, t00, t1, t2, t3, a, i, e ,ffunc]
fixed = [ u, p, w]
ndim = len(initial)
nwalkers = 50

initial0 = [initial + 1e-2*np.random.randn(ndim) for i in range(nwalkers)] 
#%%
sampler = emcee.EnsembleSampler(nwalkers, ndim, lnprobnew, args=(fixed,treal,fochanges,ferrochanges))      

print("Running burn-in...")
number_of_iterations = 10000
sampler.run_mcmc(initial0, number_of_iterations)

burnin = 2000

samples = sampler.chain[:, burnin:, :].reshape((-1, ndim)) #this generates the values of the varying parameters
#print(samples)

#%%
#############Here create the array of arrays that will contain only the walkers which converge well##############

new_samples = np.zeros((nwalkers,number_of_iterations-burnin,ndim)) 
lenwalksamp = np.zeros(ndim)
cornerplottotal = [] ## this has 1000 iteration for every walker stored in 9 columns for every parameter
cornerplotfigsamples = [] # this with all the values of all the walkers in 9 columns for each parameter

for y in range(0, ndim):  #####this is to choose the parameter  
    temp = []  #just for putting it in new_samples  
    cornerplotwalker = []
    cornerfigtemp = []
    for x in range(0, nwalkers): ########this is to choose which walker we need to eliminate
        if (np.percentile(sampler.chain[:,burnin:,y].T, [16]) < np.median(sampler.chain[x,burnin:,y].T) < np.percentile(sampler.chain[:,burnin:,y].T, [84])) and stat.stdev(sampler.chain[x,burnin:,y].T)/np.median(sampler.chain[x,burnin:,y].T) < 1:  # this ratio in the end is the coefficient of variation 
            temp.append(sampler.chain[x,burnin:,y]) ### burnin because we need to have the same region for triangle plot
    lenwalksamp[y] = np.int(len(temp)) ##to keep track of total number of all useful walkers for each parameter
    for z in range(0, len(temp)):
        new_samples[z,:,y] = temp[z] #temp[z] is all iteration values for the zth walker
        cornerplotwalker.append(temp[z])
        for qw in range(0,len(temp[z])):
            cornerfigtemp.append(temp[z][qw])
    cornerplotfigsamples.append(cornerfigtemp)        
    cornerplottotal.append(cornerplottotal)

#new_samples  = new_samples.reshape((-1,ndim))

#%%
################ Printing all the walkers together for this ##################

plt.figure()
fig, axes = plt.subplots(9, 1, sharex=True, figsize=(8, 9))
axes[0].plot(new_samples[:int(lenwalksamp[0]), :, 0].T, color="k", alpha=0.4)
axes[0].set_ylabel("$k$")

axes[1].plot(new_samples[:int(lenwalksamp[1]), :, 1].T, color="k", alpha=0.4)
axes[1].set_ylabel("$t00$")

axes[2].plot(new_samples[:int(lenwalksamp[2]), :, 2].T, color="k", alpha=0.4)
axes[2].set_ylabel("$t1$")

axes[3].plot(new_samples[:int(lenwalksamp[3]), :, 3].T, color="k", alpha=0.4)
axes[3].set_ylabel("$t2$")

axes[4].plot(new_samples[:int(lenwalksamp[4]), :, 4].T, color="k", alpha=0.4)
axes[4].set_ylabel("$t3$")

axes[5].plot(new_samples[:int(lenwalksamp[5]), :, 5].T, color="k", alpha=0.4)
axes[5].set_ylabel("$a$")
#axes[2].set_xlabel("step number")

axes[6].plot(new_samples[:int(lenwalksamp[6]), :, 6].T, color="k", alpha=0.4)
axes[6].set_ylabel("$i$")

axes[7].plot(new_samples[:int(lenwalksamp[7]), :, 7].T, color="k", alpha=0.4)
axes[7].set_ylabel("$e$")

axes[8].plot(new_samples[:int(lenwalksamp[8]), :, 8].T, color="k", alpha=0.4)
axes[8].set_ylabel("$ffunc$")

fig.tight_layout(h_pad=0.0)
#fig.savefig("line-time new as required planet c.png")

#%%Also get the error bars####
###################### Make the triangle plot again for the new required one########################

newsamples = new_samples[:, 3000:, :].reshape((-1, ndim)) #reshaping needs to be done because corner plot needs a 1-d or a 2-d input. reshaping effectively redu ces the size 
# trying something, trying to get a good corner plot

new_corner = newsamples.copy()
for x in range(0, ndim):
    np.delete(new_corner[:,x],np.s_[len(cornerplotfigsamples[x])::],axis=0)
    print(new_corner[:,x])
#    np.delete(new_corner,len(cornerplotfigsamples[x]):,x)

k_same = np.percentile(new_samples[:int(lenwalksamp[0]),:,0], [50])
t00_less,t00_same, t00_more = np.percentile(new_samples[:int(lenwalksamp[1]),:,1], [16,50,84])
t1_less,t1_same,t1_more = np.percentile(new_samples[:int(lenwalksamp[2]),:,2], [16,50,84])
t2_less,t2_same,t2_more = np.percentile(new_samples[:int(lenwalksamp[3]),:,3], [16,50,84])
t3_less,t3_same,t3_more = np.percentile(new_samples[:int(lenwalksamp[4]),:,4], [16,50,84])
a_same = np.percentile(new_samples[:int(lenwalksamp[5]),:,5], [50])
i_same = np.percentile(new_samples[:int(lenwalksamp[6]),:,6], [50])
e_same = np.percentile(new_samples[:int(lenwalksamp[7]),:,7], [50])
f_same = np.percentile(new_samples[:int(lenwalksamp[8]),:,8], [50])

#%%
#################### To get the correct corner plot, we need the correct values ######################
####################### Hence we need to remove the values which are zero ############################

#cornerplotfigsamples is the list that I need to convert to a 2-D array

#new_corner = newsamples.copy()
#for x in range(0, ndim):
#    np.delete(new_corner[x],np.s_[len(cornerplotfigsamples[x])::],axis=0)
##    np.delete(new_corner,len(cornerplotfigsamples[x]):,x)


fig = corner.corner(new_corner, labels=["$k$","$t00$","$t1$","$t2$","$t3$","$a$", "$i$", "$e$","$f$"])
#fig = corner.corner(newsamples, labels=["$k$","$t00$","$t1$","$t2$","$t3$","$a$", "$i$", "$e$","$f$"])
#fig.savefig("line-triangle planet c.png")
#
#print("All the values are = ", k_same, t00_same, t1_same, t2_same, t3_same, a_same, i_same, e_same, f_same)
#%%
#######Now we use these values as the actual t0 values and get the superimposed fit with proper parameters########

new_final_values = [t00_same, t1_same, t2_same, t3_same]
#####now we need to subtract transit centre from each respective transit set to get a proper overlap#####
#########################################################################################################

t_to_plot = [] ##This is the final time data centered around the transit centre

for x in range(0,4):
    temp=[]
    for y in range(0,40):
        temp.append(treal[x][y]-new_final_values[x])
    t_to_plot.append(temp)
    
#%%
##############Generate a big array and sort it to be used in the fitting#############
###########It will have time in 1st column, flux in 2nd and flxerr in 3rd############

tonearray = []  ## we need arrays as the function only takes arrays, hence these three respective lists
fonearray = []
ferronearray = []

for x in range(0,4): #because 4 transits
    for y in range(0,40): #because 40 data points in each transit
        tonearray.append(t_to_plot[x][y])
        fonearray.append(f1[x][y])
        ferronearray.append(ferr1[x][y])

tarray = np.array(tonearray)
farray = np.array(fonearray)
ferrarray = np.array(ferronearray)


grand = [] #create a big list and then fill each accordingly

for x in range(0,160):
     grand.append([0.0,0.0,0.0])

for x in range(0,160):   ########## I have created the unsorted grand array
    grand[x][0] = tarray[x]
    grand[x][1] = farray[x]
    grand[x][2] = ferrarray[x]
   
grand.sort(key = itemgetter(0))  

final_time =[] #These are the arrays to be used to get the fit
final_flux = []
final_fluxerr = []

for x in range(0,160): #####This is to divide it into respective 3 arrays to get the model fit#####
    final_time.append(grand[x][0])
    final_flux.append(grand[x][1])
    final_fluxerr.append(grand[x][2])

final_time = np.array(final_time)
final_flux = np.array(final_flux)
final_fluxerr = np.array(final_fluxerr)

#%%
############################Getting the TTV plot#####################################

TTVdata = []
p = 11.90727
a1 = 56817.2755
a2 = a1 + 2*p
a3 = a1 + 4*p
a4 = a1 + 6*p

predicted = [a1,a2 ,a3 ,a4 ]
for x in range(0,4):
    temp = new_final_values[x] - predicted[x]
    TTVdata.append(temp)
TTVdata = np.array(TTVdata)*24*60
x_axis = np.array([0,2,4,6])
upperlimits = [t00_more-t00_same, t1_more-t1_same, t2_more-t2_same, t3_more-t3_same]
lowerlimits = [t00_same-t00_less, t1_same - t1_less, t2_same -t2_less, t3_same - t3_less]
upperlimits = np.array(upperlimits)*24*60
lowerlimits = np.array(lowerlimits)*24*60
plt.figure()
plt.xlabel('Number of transits', fontsize=18)
plt.ylabel('TTV data (in minutes)', fontsize=16)
plt.plot(x_axis, TTVdata,'k*')
plt.axis([-1, 7, -25, 15]) ###This is chosen specific to our case
plt.errorbar(x_axis, TTVdata, yerr=np.array([lowerlimits,upperlimits]))
#plt.savefig('TTV so far for planet c.png')
   
#%%
model = MandelAgol(nldc=2,exptime=0.02,supersampling=10)
t0new = 0
plt.figure()
ymod = model.evaluate(final_time, k_same, u, t0new, p, a_same, i_same, e_same, w)
plt.plot(final_time, ymod,"r-",final_time,final_flux,'b.')
#plt.savefig('emcee planet c for k,a,i,e,.png')
