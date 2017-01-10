

#!/usr/bin/env python
# -*- coding: utf-8 -*-

#from __future__ import division, print_function

import emcee
import corner
import numpy as np
import matplotlib.pyplot as pl
from scipy import stats

import george
from george import kernels
#import pyfits
#from astropy.io import fits


def model(params, t):
    import batman
    parbat = batman.TransitParams()
    parbat.t0 = params[0]                      #time of transit
    parbat.per = 0.93                    #orbital period
    parbat.rp = params[1]                     #planet radius (in units of stellar radii)
    parbat.a = params[2]                    #semi-major axis (in units of stellar radii)
    parbat.inc = params[3]                     #orbital inclination (in degrees)
    parbat.ecc = 0.0                      #eccentricity
    parbat.w = 90.                       #longitude of periastron (in degrees)
    parbat.u = [0.35, 0.3]                #limb darkening coefficients
    parbat.limb_dark = "quadratic"       #limb darkening model

    m = batman.TransitModel(parbat, t)    #initializes model
    return m.light_curve(parbat)





# calculate likelihood of gp
def lnlike_gp(p, t, y, yerr):
    # fiting lna, lntau instead of a and tau so we need to transform
    a, gamma, period = np.exp(p[:3])
    # define the kernal
    gp = george.GP(a * kernels.ExpSine2Kernel(gamma, period))
    #Pre-compute the factorization of the matrix.
    gp.compute(t, yerr)
    # Compute the log likelihood
    return gp.lnlikelihood(y - model(p[3:7], t) )


# define the prioirs of the gp
def lnprior_gp(p):
    lna, lngamma, lnperiod = p[:3]
    if not -25 < lna < 5:
        return -np.inf
    if not -5 < lngamma < 15:
        return -np.inf
    if not -5 < lnperiod < 5:
        return -np.inf
    return 0.0 + lnprior_ind(p)


# for the granualtaion one I changed the priors maximum value to 10 instead of 5

# calculculate priors for the parameters
def lnprior_ind(p):
    t0, rp, a , inc  = p[3:7]

    if not -0.01 < t0 < 0.01:
    #if not -10.0 < t0 < 10.0:
        return -np.inf
    if not  0 < rp < 0.5:
        return -np.inf
    if not  70 < inc < 90.0:
        return -np.inf


    prior_a = stats.reciprocal(0.1, 5.)
    pa = prior_a.logpdf(a)

    return pa



# log probability = log prior+ log like  data given the model
def lnprob_gp(p, t, y, yerr):
    lp = lnprior_gp(p)
    if not np.isfinite(lp):
        return -np.inf
    return lp + lnlike_gp(p, t, y, yerr)


def fit_gp(initial, data, nwalkers=32):
    ndim = len(initial)
    p0 = [np.array(initial) + 1e-8 * np.random.randn(ndim)
          for i in range(nwalkers)]
    sampler = emcee.EnsembleSampler(nwalkers, ndim, lnprob_gp, args=data)

    print("Running burn-in")
    p0, lnp, _ = sampler.run_mcmc(p0, 500)
    sampler.reset()

    print("Running second burn-in")
    p = p0[np.argmax(lnp)]
    p0 = [p + 1e-8 * np.random.randn(ndim) for i in range(nwalkers)]
    p0, _, _ = sampler.run_mcmc(p0, 500)
    sampler.reset()

    print("Running production")
    p0, _, _ = sampler.run_mcmc(p0, 1000)

    return sampler





if __name__ == "__main__":


    #read data
    #ts, ys , yerrs = np.genfromtxt('act3_tran_incibin.txt', unpack=True)
    ts, ys , yerrs = np.genfromtxt('act3_tran.txt', unpack=True)

    t = ts.astype("float64")
    y = ys.astype("float64")
    yerr = yerrs.astype("float64")



    print("Fitting transit + GP ")
    data = (t, y, yerr)

    # expected values
    truth_gp =  [-19.95, 2.161, -2.6733, 0, 0.1093, 2.978, 86.3]



    sampler = fit_gp(truth_gp, data)




    #plot the chains
    nwalkers=32
    #for i in range(0,nwalkers-1): pl.plot(sampler.chain[i,:, 0])
    #pl.show()


    samples = sampler.flatchain


    #a, gamma, period
    ampfit = np.median(samples[:,0])
    gammafit = np.median(samples[:,1])
    periodfit = np.median(samples[:,2])
    print('par', ampfit,gammafit, periodfit)
    print('exp par', np.exp(ampfit),np.exp(gammafit), np.exp(periodfit))

    #fitparams[ t0, rp, a , inc ]
    fitparams = [ np.median(samples[:,3]),np.median(samples[:,4]), np.median(samples[:,5]), np.median(samples[:,6])]

    print('fitted parameters')
    print(fitparams)

    # Plot the samples in data space.
    print("Making plots")
    x = np.linspace(t.min(),t.max() , 500)
    pl.figure()
    pl.errorbar(t, y, yerr=yerr, fmt=".k", capsize=0)
    pl.plot(t, model( fitparams[0:4] , t),color='green')

    for s in samples[np.random.randint(len(samples), size=24)]:
        gp = george.GP(np.exp(s[0]) * kernels.ExpSine2Kernel(np.exp(s[1]),np.exp(s[2])))
        gp.compute(t, yerr)
        m = gp.sample_conditional(y - model( fitparams[0:4] , t), x) + model(fitparams[0:4], x)
        pl.plot(x, m, color="#4682b4", alpha=0.3)

    gp = george.GP(np.exp(ampfit) * kernels.ExpSine2Kernel(np.exp(gammafit),np.exp(periodfit)))
    gp.compute(t, yerr)
    # Compute the prediction conditioned on the observations and plot it.
    m = gp.sample_conditional(y - model( fitparams[0:4] , t), x) + model(fitparams[0:4], x)
    pl.plot(x , m, color='red')
    print('red',gp.lnlikelihood(y))


    pl.ylabel(r"$y$")
    pl.xlabel(r"$t$")
    pl.xlim(t.min(),t.max())
    pl.title("results with Gaussian process noise model")
    #pl.savefig("../_static/model/gp-results.png", dpi=150)
    pl.show()





    #samples.shape   (32000, 5)


    # Make the corner plot.
    labels = ["amp","gamma", "period","t0","rp", "a", "inc"]
    #truth_gp the gps are not real but the others ones are
    fig = corner.corner(samples[:, :], truths=truth_gp, labels=labels)
    fig.show()

    #fig.savefig("transit_gp_corner.png", dpi=150)


    sampler.acceptance_fraction



    # results for real data
    #par -19.8312035855 2.09292629976 -2.67160144868
    #exp par 2.44015668262e-09 8.10860869986 0.0691414101808
    #fitted parameters
    #[7.4377601785292045e-06, 0.10931300710203108, 2.970937008885131, 86.061836712910477]
