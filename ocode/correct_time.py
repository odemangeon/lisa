###This is for getting the right value of t0

import numpy as np
import matplotlib.pyplot as plt
from pytransit import MandelAgol
import astropy.constants as cst
import emcee
import corner

def give_t0(time,flux,fluxerr):

    model = MandelAgol(nldc=2,exptime=0.02,supersampling=10)

    
#%%
    def lnliket(theta_free,theta_fixed, t, y, yerr):
        k,t0,a,i,e = theta_free
        #k, logf = theta_free
        u, p, w  = theta_fixed
        y_model = model.evaluate(t,k,u, t0, p, a, i, e, w)
        #u = [0.460,0.210] #quadratic limb darkening coefficients
        inv_sigma = 1.0/(yerr**2) #+ y_model**2*np.exp(2*lnf) #apparently a list cant be put to pwer
        #inv_sigma = 1.0/((yerr*10**(logf))**2)
        #return -0.5*(np.sum((y-y_model)**2*inv_sigma - np.log(inv_sigma)))
        return -0.5*(np.sum((y-y_model)**2*inv_sigma))
        #return -0.5 * np.sum(((y - model(p, x))/yerr) ** 2)
        
    def lnpriort(theta_free,tless,tmore):
        k,t0,a,i,e= theta_free
        if tless < t0 < tmore and 0 < k < 1 and 1 < i < 2 and 0 < e < 1 and 0 < a < 30:
            return 0.0            
        return -np.inf   
                
    def lnprobt(theta_free, theta_fixed,tless,tmore, t, y, yerr):
        lp = lnpriort(theta_free,tless,tmore)
        if not np.isfinite(lp):
            return -np.inf
        ll = lnliket(theta_free, theta_fixed, t, y, yerr)
        return lp + ll
        
#%% #Just get the data set
    mt = time
    mf = flux
    mferr = fluxerr
    mferr = np.array(fluxerr)   
#%%
    ##Initialising emcee
    model = MandelAgol(nldc=2,exptime=0.02,supersampling=10)
        
    rad_st = 0.913 * cst.R_sun.value
    k = 0.0753 #planet-star radius ratio
    u = [0.460,0.210] #quadratic limb darkening coefficients
    t0 =  mt[19]
    u = [0.460,0.210] #quadratic limb darkening coefficients
    p = 7.919 #orbital period
    a = 0.077 * cst.au.value / rad_st #0.0762  #scaled semi major axis
    i = 88.83*np.pi/180  #orbital inclination
    e = 0.119#0.119 #orbital eccentricity
    w = 179*np.pi/180 #argument of periastron

    initial = [k,t0,a,i,e]

    fixed = [ u, p, w]

    ndim = len(initial)
    #ndim = 1
    nwalkers = 50
    #k = abs(1e-8*np.random.randn(ndim))
    
    initial0 = [initial + 1e-8*np.random.randn(ndim) for i in range(nwalkers)] 

    sampler = emcee.EnsembleSampler(nwalkers, ndim, lnprobt, args=(fixed,mt[14],mt[26],mt,mf,mferr))      

    print("Running burn-in...")
    sampler.run_mcmc(initial0, 1000)

    samples = sampler.chain[:, 140:, :].reshape((-1, ndim)) #this generates the values of variables
    K_same = np.percentile(samples[:,0], [50])  
#    print("The K in each little iteration is = ",K_same)
#    print(" the tless and tmore values are = ", mt[14], mt[26])
#    #%%
#    #Make the triangle plot.
#    burnin = 50
#    samples1 = sampler.chain[:, burnin:, :].reshape((-1, ndim))
#    plt.figure()    
#    fig = corner.corner(samples1, labels=["$t0$"])
#    fig.savefig("line-triangle.png")
#    
#    #%%All walkers treated as one walker for many iterations
#    plt.figure()    
#    plt.plot(samples, color = "b", alpha = .8) ##to plot the walker vs iterations
#    plt.savefig('one walker entire.png')
#    #samples = walker_print.reshape((-1, ndim))
    
#    #%%All walkers together
#    plt.figure()
#    plt.plot(sampler.chain[:, 140:, 1].T,"g", alpha = .1) #to plot all the walkers on the same place
#    plt.savefig('All walkers all iterations.png')
#    
    #%%
    t0_less, t0_same, t0_more = np.percentile(samples[:,1], [16, 50, 84])
    
    #%%    


    return t0_same







