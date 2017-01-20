

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

from ajplanet import pl_rv_array
import pickle


# RV model
def get_rv(params, time):
    rvsys, k, w, ecc, t0, period = params
    rv_model = pl_rv_array(time, rvsys , k, np.deg2rad(w), ecc, t0, period)
    return rv_model

def model(params, time):
    ngp = 4
    return get_rv(params[0+ngp:6+ngp], time) + get_rv( np.append([0,], params[6+ngp:11+ngp ]), time)



# calculate likelihood of gp
def lnlike_gp(p, t, y, yerr):
    # fiting lna, lntau instead of a and tau so we need to transform
    sigma, a  = np.exp(p[0:2])**2.0
    gamma, period = np.exp(p[2:4])
    # define the kernal
    gp = george.GP(a * kernels.ExpSine2Kernel(gamma, period) + kernels.WhiteKernel(sigma)  )
    #Pre-compute the factorization of the matrix.
    gp.compute(t, yerr)
    # Compute the log likelihood
    return gp.lnlikelihood(y - model(p, t) )


# define the prioirs of the gp
def lnprior_gp(p):
    lnsigma, lna, lngamma, lnperiod = p[:4]
    if not -15 < lnsigma < 2.99573:
        return -np.inf
    if not -25 < lna <  2.99573:
        return -np.inf
    if not -5 < lngamma < 15:
        return -np.inf
    if not 2.7080 < lnperiod < 3.2188758: # 15 and 25 period=20.3 days  +/-3
        return -np.inf
    return 0.0 + lnprior_ind(p)


# for the granualtaion one I changed the priors maximum value to 10 instead of 5

# calculculate priors for the parameters
def lnprior_ind(p):
    ngp =4
    rvsys, k, w, ecc, t0, period1 , k2, w2, ecc2, t02, period2  = p[4+0:4+11]

    if not 7.2e3 < rvsys < 7.4e3:
        return -np.inf
    if not 0 < k < 30.0:
        return -np.inf
    if not  0 < w < 180:
        return -np.inf
    if not  0 < ecc < 0.5:
        return -np.inf
    if not  7399.46948 - 0.08 < t0 < 7399.46948 +0.08:  # extrapolation gives 7399.46948  0.08 is an error of 2 hours
            return -np.inf
    if not  7.92008 -  0.0013 < period1 < 7.92008 + 0.0013: # error in the apper is 0.6 minutes i am allowng 2 minutes
            return -np.inf

    if not 0 < k2 < 30.0:
        return -np.inf
    if not  0 < w2 < 180:
        return -np.inf
    if not  0 < ecc2 < 0.5:
        return -np.inf
    if not  7400.7064 - 0.08 < t02 < 7400.7064 +0.08:  # extrapolation gives 7400.7064  0.08 is an error of 2 hours
            return -np.inf
    if not  11.9068-  0.0026 < period2 < 11.9068 + 0.0026: # error in the apper is 1.8 minutes i am allowng 4 minutes
            return -np.inf
    return 0



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
    p0, _, _ = sampler.run_mcmc(p0, 1000)
    sampler.reset()

    print("Running production")
    p0, _, _ = sampler.run_mcmc(p0, 2000)

    return sampler





if __name__ == "__main__":


    #read data
    #ts, ys , yerrs = np.genfromtxt('act3_tran_incibin.txt', unpack=True)
    ts, ys , yerrs = np.genfromtxt('/Users/sbarros/Documents/work/python/photodynamic/k2_19RVs.txt', unpack=True)

    t = ts.astype("float64")
    y = ys.astype("float64")*1e3
    yerr = yerrs.astype("float64")*1e3

    #pl.figure()
    #pl.errorbar(t, y, yerr=yerr, fmt=".k", capsize=0)
    #pl.show()
    #true parameters or close initial parameters
    #truth_par =  [t0, rp, a , inc ]

    print("Fitting transit + GP ")
    data = (t, y, yerr)


    truth_gp = [np.log(10), np.log(20), np.log(20.0), np.log(20.0), 7340.0,  14.4,179,0.119, 7399.46948,  7.92008, 4.2, 237, 0.094 , 7400.7064 ,11.9068    ]
    #for granulation
    #t, y , yerr = np.genfromtxt('cutact3.txt', unpack=True)


    sampler = fit_gp(truth_gp, data)


    #ndim = len(truth_gp)
    #nwalkers=32
    #p0 = [np.array(truth_gp) + 1e-8 * np.random.randn(ndim)
    #    for i in range(nwalkers)]
    #sampler = emcee.EnsembleSampler(nwalkers, ndim, lnprob_gp, args=data)

    #print("Running burn-in")
    #p0, lnp, _ = sampler.run_mcmc(p0, 500)


    #plot the chains
    nwalkers=32
    #for i in range(0,nwalkers-1): pl.plot(sampler.chain[i,:, 0])
    #pl.show()


    samples = sampler.flatchain

    pickle.dump(sampler, open("rvs_gp.pkl", 'wb'),  4)

    #a, gamma, period
    sigmafit = np.median(samples[:,0])
    ampfit = np.median(samples[:,1])
    gammafit = np.median(samples[:,2])
    periodfit = np.median(samples[:,3])
    print('par', sigmafit, ampfit,gammafit, periodfit)
    print('exp par', np.exp(sigmafit), np.exp(ampfit),np.exp(gammafit), np.exp(periodfit))

    #fitparams[ trvsys, k, w, ecc, t0, period  ]
    fitpar1 = [ np.median(samples[:,4]),np.median(samples[:,5]), np.median(samples[:,6]), np.median(samples[:,7]), np.median(samples[:,8]), np.median(samples[:,9])]
    fitpar2 = [ np.median(samples[:,10]),np.median(samples[:,11]), np.median(samples[:,12]), np.median(samples[:,13]), np.median(samples[:,14])]

    print('fitted parameters')
    print(fitpar1, fitpar2)


    result =[sigmafit, ampfit, gammafit, periodfit]
    result.extend(fitpar1)
    result.extend(fitpar2)

    #np.concatenate(([sigmafit, ampfit, gammafit, periodfit], fitpar1, fitpar2))

    # Plot the samples in data space.
    print("Making plots")
    x = np.linspace(t.min(),t.max() , 500)
    pl.figure()
    pl.errorbar(t, y, yerr=yerr, fmt=".k", capsize=0)

    pl.plot(t, model( result , t),color='green')

    '''
    for s in samples[np.random.randint(len(samples), size=24)]:
        gp = george.GP(np.exp(s[0]) * kernels.ExpSine2Kernel(np.exp(s[1]),np.exp(s[2])))
        gp.compute(t, yerr)
        #m = gp.sample_conditional(y , x) #+ model(s[2:], x)
        m = gp.sample_conditional(y - model( fitparams[0:4] , t), x) + model(fitparams[0:4], x)
        pl.plot(x, m, color="#4682b4", alpha=0.3)
    '''
    gp = george.GP(np.exp(ampfit)**2. * kernels.ExpSquaredKernel(np.exp(gammafit)**2.0 ) + kernels.WhiteKernel( np.exp(sigmafit)**2.0 ) )
    gp.compute(t, yerr)
    # Compute the prediction conditioned on the observations and plot it.
    m = gp.sample_conditional(y -  model(result , t) , x) + model(result , x)
    #m = gp.sample_conditional(y - model( truth_gp[3:7] , t), x) + model(truth_gp[3:7], x)
    pl.plot(x , m, color='red')
    print('red',gp.lnlikelihood(y))


    pl.ylabel(r"$y$")
    pl.xlabel(r"$t$")
    pl.xlim(t.min(),t.max())
    pl.title("results with Gaussian process noise model")
    #pl.savefig("../_static/model/gp-results.png", dpi=150)
    #pl.show()
    pl.savefig("rvs_gp_pl.png", dpi=150)




    #samples.shape   (32000, 5)


    # Make the corner plot.
    labels = ["sigma", "amp","gamma", "period","trvsys", "k", "w", "ecc", "t0", "period1", "k2", "w2", "ecc2", "t02", "period2" ]
    #truth_gp the gps are not real but the others ones are
    fig = corner.corner(samples[:, :], truths=truth_gp, labels=labels)
    #fig.show()

    fig.savefig("rvs_gp_corner.png", dpi=150)


    sampler.acceptance_fraction


        #fitparams[ t0, rp, a , inc ]
'''
    #samples[:,3]=samples[:,3]*24.*60.*60.
    fitparams[0]=fitparams[0]*24.*60.*60.

    for i in range(0,4):
        s1  =   np.percentile(samples[:,i+3], [16, 50, 84], axis=0)
        t0_right, t0_left =  s1[2]-fitparams[i] ,  fitparams[i] -s1[0]
        print(labels[i])
        print('%.5f^{+%.5f}_{-%.5f}' % ( fitparams[i], t0_right,t0_left))
'''
