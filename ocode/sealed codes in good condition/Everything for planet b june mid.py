################This script is to get all the parameters of planet b#######################

#import correct_time as ct
import numpy as np
import matplotlib.pyplot as plt
from pytransit import MandelAgol
from operator import itemgetter
import untrendy as ut
import emcee
import astropy.constants as cst
import corner
 
#############To get the grand data into list of list for the planet #########

main = np.genfromtxt('LCdata.txt')
lm = len(main)
transits = np.genfromtxt('transits for b.txt')
lt = len(transits)

t=[] 
f=[]
ferr=[]
#t1 = [] #observation times, list of lists
f1 = [] #flux
ferr1 = [] #fluxerr
f1new = [] #these are the arrays made instead of the list of lists
f1newerr = []
treal = [] #list os list with real time values

#for x in range(0,6):
#    temp = list(range(1, 41))
#    t1.append(temp)


for x in range(0, lm-1): #to get the data in separate arrays
    t.append(main[x][0])
    f.append(main[x][1])
    ferr.append(main[x][2])
    
fnew, ferrnew = ut.untrend(t, f, ferr)

for x in range(20, lm-1):
    for y in range(0,lt): #this will iterate for each transit
        
        if t[x] == transits[y] :
            minimum = fnew[x] 
            for z in range(x-20, x+20): #for abs min in each trnsit
                if fnew[z] < minimum:
                    minimum = fnew[z]
                    least_time = t[z]
                    b = z
            print('The least time is ', least_time)
            xx = 0
            f =[] 
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
                time.append(t[w])
                f.append(fnew[w])
                ferrrr.append(ferrnew[w])
                f1new.append(fnew[w])
                f1newerr.append(ferrnew[w])
            
            treal.append(time)
            ferr1.append(ferrrr)
            f1.append(f)

#Now we have data for separate transits in separate lists of lists in treal, f1 and ferr1.
#Use it together to get total iteration as discussed with Olivier

##########This is the method to be followed###############
##################### To do what olivier asked me to do#########################
################################################################################
#%%
tochanges = [] #Just the arrays for this again, these are the same as tfinal, fluxfinal etc i believe
fochanges = []
ferrochanges = []

for x in range(0, len(treal)):
    for y in range(0, len(treal[x])):

        tochanges.append(treal[x][y])
        fochanges.append(f1[x][y])
        ferrochanges.append(ferr1[x][y])

fochanges = np.array(fochanges)  ###this will convert the list type to array type, imp to be used in the func
ferrochanges = np.array(ferrochanges)        
#########use these arrays instead#######
##########define the new functions################

model = MandelAgol(nldc=2,exptime=0.02,supersampling=10)

def lnlikenew(theta_free, theta_fixed, tfunc, yfunc, yerrfunc):
    k, t00, t1, t2, t3, t4, t5, t6, a, i, e, ffunc = theta_free
    t0 = [t00,t1,t2,t3,t4,t5,t6]
    u, p, w  = theta_fixed
    ttemp = []
    for x in range(0,7):  ##########To get the reduced kinda list and get the total list #########
        for y in range(0,40):
            ttemp.append(treal[x][y] - t0[x])
            
    t01 = 0
    y_model = model.evaluate(ttemp, k, u, t01, p, a, i, e, w)
    inv_sigma = 1.0/((ffunc*yerrfunc)**2) #+ y_model**2*np.exp(2*lnf))
    return -0.5*(np.sum((yfunc-y_model)**2*inv_sigma - np.log(inv_sigma)))
    
def lnpriornew(theta_free):
    k, t00, t1, t2, t3, t4, t5, t6, a, i, e, ffunc = theta_free
    if  0.01 < ffunc <10 and 0 < k < 1 and 15 < a <25 and 1 < i < np.pi/2 and 0 <= e < 1 and 56813.266136 < t00 < 56813.566136 and 56821.1529457 < t1 < 56821.4798587 and 56836.9876936 < t2 < 56837.2737389 and 56844.9356528 < t3 < 56845.1808336 and 56860.7497779 < t4 < 56861.0358212 and 56868.6568315 < t5 < 56868.9837383 and 56884.4914118 < t6 < 56884.7774567:
        return 0.0            
    return -np.inf   

def lnprobnew(theta_free, theta_fixed, tfunc, yfunc, yerrfunc):
    lp = lnpriornew(theta_free)
    if not np.isfinite(lp):
        return -np.inf
    ll = lnlikenew(theta_free, theta_fixed, tfunc, yfunc, yerrfunc)
    return lp + ll           

################data values for constants#####################

rad_st = 0.913 * cst.R_sun.value
k = 0.0753 #planet-star radius ratio
u = [0.460,0.210] #quadratic limb darkening coefficients
t00 = 56813.3887294
t1 = 56821.2959702
t2 = 56837.151148
t3 = 56845.0582432
t4 = 56860.9132312
t5 = 56868.7998532
t6 = 56884.654866
p = 7.919 #orbital period
a = 0.077 * cst.au.value / rad_st #0.0762  #scaled semi major axis
i = 88.83*np.pi/180  #orbital inclination
e = 0.119#0.119 #orbital eccentricity
w = 179*np.pi/180 #argument of periastron
f = 1

initial = [k, t00, t1, t2, t3, t4, t5, t6, a, i, e ,f]
fixed = [ u, p, w]
ndim = len(initial)
nwalkers = 100

initial0 = [initial + 1e-2*np.random.randn(ndim) for i in range(nwalkers)] 

sampler = emcee.EnsembleSampler(nwalkers, ndim, lnprobnew, args=(fixed,treal,fochanges,ferrochanges))      

print("Running burn-in...")
sampler.run_mcmc(initial0, 10000)

samples = sampler.chain[:, 140:, :].reshape((-1, ndim)) #this generates the values of k, t0,i and e
#print(samples)

#%%
################ Printing all the walkers together for this ##################

plt.clf()
fig, axes = plt.subplots(11, 1, sharex=True, figsize=(8, 9))
axes[0].plot(sampler.chain[:, :, 0].T, color="k", alpha=0.4)
axes[0].set_ylabel("$k$")

axes[1].plot(sampler.chain[:, :, 1].T, color="k", alpha=0.4)
axes[1].set_ylabel("$t00$")

axes[2].plot(sampler.chain[:, :, 2].T, color="k", alpha=0.4)
axes[2].set_ylabel("$t1$")

axes[3].plot(sampler.chain[:, :, 3].T, color="k", alpha=0.4)
axes[3].set_ylabel("$t2$")

axes[4].plot(sampler.chain[:, :, 4].T, color="k", alpha=0.4)
axes[4].set_ylabel("$t3$")

axes[5].plot(sampler.chain[:, :, 5].T, color="k", alpha=0.4)
axes[5].set_ylabel("$t4$")

axes[6].plot(sampler.chain[:, :, 6].T, color="k", alpha=0.4)
axes[6].set_ylabel("$t5$")

axes[7].plot(sampler.chain[:, :, 7].T, color="k", alpha=0.4)
axes[7].set_ylabel("$t6$")

axes[8].plot(sampler.chain[:, :, 8].T, color="k", alpha=0.4)
axes[8].set_ylabel("$a$")
#axes[2].set_xlabel("step number")

axes[9].plot(sampler.chain[:, :, 9].T, color="k", alpha=0.4)
axes[9].set_ylabel("$i$")

axes[10].plot(sampler.chain[:, :, 10].T, color="k", alpha=0.4)
axes[10].set_ylabel("$e$")

fig.tight_layout(h_pad=0.0)
fig.savefig("line-time new as required.png")
#%%Also get the error bars####
###################### Make the triangle plot again for the new required one########################
burnin = 1000
samples = sampler.chain[:, burnin:, :].reshape((-1, ndim))

k_same = np.percentile(samples[:,0], [50])
t00_less,t00_same, t00_more = np.percentile(samples[:,1], [16,50,84])
t1_less,t1_same,t1_more = np.percentile(samples[:,2], [16,50,84])
t2_less,t2_same,t2_more = np.percentile(samples[:,3], [16,50,84])
t3_less,t3_same,t3_more = np.percentile(samples[:,4], [16,50,84])
t4_less,t4_same,t4_more = np.percentile(samples[:,5], [16,50,84])
t5_less,t5_same,t5_more = np.percentile(samples[:,6], [16,50,84])
t6_less,t6_same,t6_more = np.percentile(samples[:,7], [16,50,84])
a_same = np.percentile(samples[:,8], [50])
i_same = np.percentile(samples[:,9], [50])
e_same = np.percentile(samples[:,10], [50])
f_same = np.percentile(samples[:,11], [50])

fig = corner.corner(samples, labels=["$k$","$t00$","$t1$","$t2$","$t3$","$t4$","$t5$","$t6$","$a$", "$i$", "$e$","$f$"])
fig.savefig("line-triangle.png")

print("All the values are = ", k_same, t00_same, t1_same, t2_same, t3_same, t4_same, t5_same, t6_same, a_same, i_same, e_same, f_same)
#%%
#######Now we use these values as the actual t0 values and get the superimposed fit with proper parameters########

new_final_values = [t00_same, t1_same, t2_same, t3_same, t4_same, t5_same, t6_same]
#####now we need to subtract t0 from each respective element to get a proper overlap#####
#########################################################################################################

t_to_plot = [] ##This is the final time data centered around t0

for x in range(0,7):
    temp=[]
    for y in range(0,40):
        temp.append(treal[x][y]-new_final_values[x])
    t_to_plot.append(temp)


#%%
##############Generate a big array and sort it to be used in the fitting#############
###########It will have time in 1st column, flux in 2nd and flxerr in 3rd############

tonearray = []  ######as the name suggests...######
fonearray = []
ferronearray = []

for x in range(0,7):
    for y in range(0,40):
        tonearray.append(t_to_plot[x][y])
        fonearray.append(f1[x][y])
        ferronearray.append(ferr1[x][y])

tarray = np.array(tonearray)
farray = np.array(fonearray)
ferrarray = np.array(ferronearray)


grand = [] #create a 280 by 3 list and then fill eaach accordingly

for x in range(0,280):
     grand.append([0.0,0.0,0.0])

for x in range(0,280):   ##########he I have created the unsorted grand array
    grand[x][0] = tarray[x]
    grand[x][1] = farray[x]
    grand[x][2] = ferrarray[x]
   
grand.sort(key = itemgetter(0))  

final_time =[] #These are the arrays to be used to get the fit
final_flux = []
final_fluxerr = []

for x in range(0,280): #####This is to divide it into respective 3 arrays to get the model fit#####
    final_time.append(grand[x][0])
    final_flux.append(grand[x][1])
    final_fluxerr.append(grand[x][2])

final_time = np.array(final_time)
final_flux = np.array(final_flux)
final_fluxerr = np.array(final_fluxerr)

#%%
############################Getting the TTV plot#####################################

TTVdata = []
p = 7.921101
a1 = 56813.3767
a2 = 56813.3767 + p
a3 = 56813.3767 + 3*p
a4 = 56813.3767 + 4*p
a5 = 56813.3767 + 6*p
a6 = 56813.3767 + 7*p
a7 = 56813.3767 + 9*p

predicted = [a1,a2 ,a3 ,a4 ,a5 ,a6 ,a7]
for x in range(0,7):
    temp = new_final_values[x] - predicted[x]
    TTVdata.append(temp)
TTVdata = np.array(TTVdata)*24*60
x_axis = np.array([0,1,3,4,6,7,9])
upperlimits = [t00_more-t00_same, t1_more-t1_same, t2_more-t2_same, t3_more-t3_same, t4_more-t4_same, t5_more-t5_same, t6_more-t6_same]
lowerlimits = [t00_same-t00_less, t1_same - t1_less, t2_same -t2_less, t3_same - t3_less, t4_same - t4_less, t5_same - t5_less,t6_same - t6_less]
upperlimits = np.array(upperlimits)*24*60
lowerlimits = np.array(lowerlimits)*24*60
plt.figure()
plt.plot(x_axis, TTVdata,'k*', label = 'TTV')
plt.axis([-1, 10, -20, 15]) ###This is chosen specific to our case
plt.errorbar(x_axis, TTVdata, yerr=np.array([lowerlimits,upperlimits]))
plt.savefig('TTV so far.png')
    
#%%
model = MandelAgol(nldc=2,exptime=0.02,supersampling=10)
t0new = 0
plt.figure()
ymod = model.evaluate(final_time, k_same, u, t0new, p, a_same, i_same, e_same, w)
plt.plot(final_time, ymod,"r-",final_time,final_flux,'b.')
plt.savefig('obtained through emcee for k,a,i,e,.png')
