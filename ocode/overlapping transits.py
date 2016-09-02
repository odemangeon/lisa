################ To get all the parameters for overlapping cases #######################

import numpy as np
import matplotlib.pyplot as plt
from pytransit import MandelAgol
import untrendy as ut
import emcee
import astropy.constants as cst
import corner

#######################################################################################

main = np.genfromtxt('LCdata.txt')
lm = len(main)
transits = np.genfromtxt('transits for both.txt')
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
            #fnottrended = []
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
                #fnottrended.append(foriginal[w])
            
            plt.figure()
            plt.plot(time,f,'b.')
            treal.append(time)
            ferr1.append(ferrrr)
            f1.append(f)

# Now we have data for separate overlapping transits in separate lists of lists in treal, f1 and ferr1.
#### WE wuill call it all in a loop #####
############################ Defining the functions ######################################

model = MandelAgol(nldc=2,exptime=0.02,supersampling=10)

def lnlikenew(theta_free, theta_fixed, tfunc, yfunc, yerrfunc): ## why have I been using tfunc and treal interchangeably ???
    
    k1, k2, t1, t2, a1, a2, i1,i2, e1, e2, ffunc = theta_free
    u, p1,p2, w1,w2  = theta_fixed
    
    y_model = model.evaluate(tfunc, k1, u, t1, p1, a1, i1, e1, w1) + model.evaluate(tfunc, k2, u, t2, p2, a2, i2, e2, w2) - 1
    inv_sigma = 1.0/((ffunc*yerrfunc)**2) #+ y_model**2*np.exp(2*lnf))
    return -0.5*(np.sum((yfunc-y_model)**2*inv_sigma - np.log(inv_sigma)))
    
def lnpriornew(theta_free,tfunc):
    k1, k2, t1, t2, a1, a2, i1,i2, e1,e2, ffunc = theta_free
    if  0.01 < ffunc < 100 and 0 < k1 < 1 and 0 < k2 < 1 and 15 < a1 < 25 and 15 < a2 < 30 and 1 < i1 < np.pi/2 and 1 < i2 < np.pi and 0 <= e1 < 1 and 0 <= e2 < 1 and tfunc[10] < t1 < tfunc[30] and tfunc[10] < t2 < tfunc[30]:
        return 0.0            
    return -np.inf   

def lnprobnew(theta_free, theta_fixed, tfunc, yfunc, yerrfunc):
    lp = lnpriornew(theta_free,tfunc)
    if not np.isfinite(lp): 
        return -np.inf
    ll = lnlikenew(theta_free, theta_fixed, tfunc, yfunc, yerrfunc)
    return lp + ll      
        
################data values for constants#####################
#%%
rad_st = 0.913 * cst.R_sun.value

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

ffuncorig = 1

fixed = [u, p1, p2, w1, w2]
nwalkers = 100
number_of_iterations = 1000

### List to store all the values ####

k1_same = []
k2_same = []
t1_same = []
t2_same = []
a1_same = []
a2_same = []
i1_same = []
i2_same = []
e1_same = []
e2_same = []

for q in range(1,2):
    
    time = np.array(treal[q])  #these are our values for each iteration
    flux = np.array(f1[q])
    fluxerror = np.array(ferr1[q])
    
    t1 = t1_initials[q]
    t2 = t2_initials[q]
    initial = [k1orig, k2orig, t1, t2, a1orig, a2orig, i1orig, i2orig, e1orig, e2orig, ffuncorig]
    ndim = len(initial)
    initial0 = [initial + 1e-2*np.random.randn(ndim) for i in range(nwalkers)] 
    
    ###############
    sampler = emcee.EnsembleSampler(nwalkers, ndim, lnprobnew, args=( fixed, time, flux, fluxerror))      
    
    print("Running burn-in...")
    sampler.run_mcmc(initial0, number_of_iterations)
    
    burnin = np.int(number_of_iterations/5)
    
    samples = sampler.chain[:, burnin:, :].reshape((-1, ndim)) #this generates the values of the varying parameters
    
    ############################# Printing walkers ##################################
    
    fig, axes = plt.subplots(11, 1, sharex=True, figsize=(8, 9))
    
    axes[0].plot(sampler.chain[:, :, 0].T, color="k", alpha=0.4)
    axes[0].set_ylabel("$k1$")
    
    axes[1].plot(sampler.chain[:, :, 1].T, color="k", alpha=0.4)
    axes[1].set_ylabel("$k2$")
    
    axes[2].plot(sampler.chain[:, :, 2].T, color="k", alpha=0.4)
    axes[2].set_ylabel("$t1$")
    
    axes[3].plot(sampler.chain[:, :, 3].T, color="k", alpha=0.4)
    axes[3].set_ylabel("$t2$")
    
    axes[4].plot(sampler.chain[:, :, 4].T, color="k", alpha=0.4)
    axes[4].set_ylabel("$a1$")
    
    axes[5].plot(sampler.chain[:, :, 5].T, color="k", alpha=0.4)
    axes[5].set_ylabel("$a2$")
    
    axes[6].plot(sampler.chain[:, :, 6].T, color="k", alpha=0.4)
    axes[6].set_ylabel("$i1$")
    
    axes[7].plot(sampler.chain[:, :, 7].T, color="k", alpha=0.4)
    axes[7].set_ylabel("$i2$")
    
    axes[8].plot(sampler.chain[:, :, 8].T, color="k", alpha=0.4)
    axes[8].set_ylabel("$e1$")
    
    axes[9].plot(sampler.chain[:, :, 9].T, color="k", alpha=0.4)
    axes[9].set_ylabel("$e2$")
    
    axes[10].plot(sampler.chain[:, :, 10].T, color="k", alpha=0.4)
    axes[10].set_ylabel("$ffunc$")
    
    fig.tight_layout(h_pad=0.0)
    
    #%%
    ######################## The triangle plot and obtaining the values ############################
    
    samples = sampler.chain[:, burnin:, :].reshape((-1, ndim))

    k1temp = float(np.percentile(samples[:,0], [50]))
    k2temp = float(np.percentile(samples[:,1], [50]))
    t1temp = float(np.percentile(samples[:,2], [50]))
    t2temp = float(np.percentile(samples[:,3], [50]))
    a1temp = float(np.percentile(samples[:,4], [50]))
    a2temp = float(np.percentile(samples[:,5], [50]))
    i1temp = float(np.percentile(samples[:,6], [50]))
    i2temp = float(np.percentile(samples[:,7], [50]))
    e1temp = float(np.percentile(samples[:,8], [50]))
    e2temp = float(np.percentile(samples[:,9], [50]))
    
    k1_same.append(np.percentile(samples[:,0], [50]))
    k2_same.append(np.percentile(samples[:,1], [50]))
    t1_same.append(np.percentile(samples[:,2], [50]))
    t2_same.append(np.percentile(samples[:,3], [50]))
    a1_same.append(np.percentile(samples[:,4], [50]))
    a2_same.append(np.percentile(samples[:,5], [50]))
    i1_same.append(np.percentile(samples[:,6], [50]))
    i2_same.append(np.percentile(samples[:,7], [50]))
    e1_same.append(np.percentile(samples[:,8], [50]))
    e2_same.append(np.percentile(samples[:,9], [50]))
    ffunc_same = np.percentile(samples[:,10], [50])
    
    #fig = corner.corner(samples, labels=["$k1$","$k2$","$t1$","$t2$","$a1$", "$a2$","$i1$","$i2$", "$e1$","$e2$","$ffunc$"])
 
    
    #%%
    ################################### Final fit #######################################
    t1orig = t1_initials[q]
    t2orig = t2_initials[q]
    
    plt.figure()
    y_model = model.evaluate(time, k1temp, u, t1temp, p1, a1temp, i1temp, e1temp, w1) + model.evaluate(time , k2temp, u, t2temp, p2, a2temp, i2temp, e2temp, w2) - 1
    y_real_parameters = model.evaluate(time, k1orig, u, t1orig, p1, a1orig, i1orig, e1orig, w1) + model.evaluate(time , k2orig, u, t2orig, p2, a2orig, i2orig, e2orig, w2) - 1
   
    plt.plot( time, y_model,"b-", time, flux,'r.')
    plt.savefig('model that i generated for overlapping transit 2.png')
    
    plt.figure()
    plt.plot( time, y_real_parameters,"r-", time, flux,'b.')
    plt.savefig('Real given values 2.png')

print(k1_same)
print(t1_same)
print(t2_same)





