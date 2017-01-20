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
    rvsys, k, w, ecc, t0, period1 = params
    rv_model = pl_rv_array(time, rvsys , k, np.deg2rad(w), ecc, t0, period1)
    return rv_model

def model(params, time):
    ngp = 1
    return get_rv(params[0+ngp:6+ngp], time)



def lnlike_ind(p, x, y, yerr):
    jitter = p[0]
    inv_sigma2 = 1.0/(yerr**2 + model(p, x)**2 * np.exp(2*jitter))
    return -0.5*(np.sum( (y - model(p, x)) **2 *inv_sigma2 - np.log(inv_sigma2)) )


def lnprior_ind(p):

    jitter, rvsys, k, w, ecc, t0, period1   = p

    if not  - 50.0 < jitter < 50.0:
        return -np.inf
    if not 7330 < rvsys < 7360:
        return -np.inf
    if not 0 < k < 30.0:
        return -np.inf
    if not  0 <= w < 180:
        return -np.inf
    if not  0 <= ecc < 0.5:
        return -np.inf
    if not  7399.46948 - 0.08 < t0 < 7399.46948 +0.08:  # extrapolation gives 7399.46948  0.08 is an error of 2 hours
        return -np.inf
    if not  7.92008 - 0.0013 < period1 < 7.92008 + 0.0013: # error in the paper is 0.6 minutes i am allowng 2 minutes=0.0013
        return -np.inf
    return 0
# with priors of - 0.08 and 0.013 the t0 and the period are complitly unctrained within the prioir,
# need to check what is more resonable to contrain more from the transits and see what we can leave a bit more free
# with the 2 minutes error on the period the still unconstrained
# best values  [-6.8257349425078093, 7338.9844887266936, 13.483146579108936, 83.015771419678131, 0.18587751826421856, 7399.4731951955455, 7.9201067473287843]

# log probability = log prior+ log like  data given the model
def lnprob_ind(p, t, y, yerr):
    lp = lnprior_ind(p)
    if not np.isfinite(lp):
        return -np.inf
    return lp + lnlike_ind(p, t, y, yerr)


# initialise the walkers and run the burn-in and the producion chain
def fit_ind(initial, data, nwalkers=32):
    ndim = len(initial)
    p0 = [np.array(initial) + 1e-8 * np.random.randn(ndim)
          for i in range(nwalkers)]
    sampler = emcee.EnsembleSampler(nwalkers, ndim, lnprob_ind, args=data)


    print("Running burn-in")
    p0, _, _ = sampler.run_mcmc(p0, 1500)
    sampler.reset()


    print("Running production")
    p0, _, _ = sampler.run_mcmc(p0, 3000)

    return sampler



if __name__ == "__main__":


    #read data
    #ts, ys , yerrs = np.genfromtxt('act3_tran_incibin.txt', unpack=True)
    ts, ys , yerrs = np.genfromtxt('/Users/sbarros/Documents/work/python/photodynamic/k2_19RVs.txt', unpack=True)

    t = ts.astype("float64")
    y = ys.astype("float64")*1e3
    yerr = yerrs.astype("float64")*1e3

    truth_par = [1.0, 7340.0,  14.4, 0.0 ,90.0, 7399.46948,  7.92008]

    #x = np.linspace(t.min(),t.max() , 500)
    #y = model(truth_par, x ) + np.random.normal(0,2,500)
    #yerr = np.zeros_like(y) + 1.0
    #pl.figure()
    #pl.errorbar(t, y, yerr=yerr, fmt=".k", capsize=0)
    #pl.show()
    #true parameters or close initial parameters
    #truth_par =  [t0, rp, a , inc ]

    #t=x
    print("Fitting transit + GP ")
    data = (t, y, yerr)


    truth_par = [-8.295, 7340.0,  14.4, 90.0 ,0.01, 7399.46948,  7.92008]
    #for granulation


    sampler = fit_ind(truth_par, data)

    samples = sampler.flatchain

    '''
    #plot the chains
    nwalkers=32
    for i in range(0,nwalkers-1): pl.plot(sampler.chain[i,:, 0])
    pl.show()

    '''


    #fitparams[ t0, rp, a , inc ]
    fitparams = [ np.median(samples[:,0]),np.median(samples[:,1]), np.median(samples[:,2]), np.median(samples[:,3]) , np.median(samples[:,4]),np.median(samples[:,5]), np.median(samples[:,6]) ]


    print('fitted parameters')
    print(fitparams)



        # Plot the samples in data space.
    print("Making plots")

    x = np.linspace(t.min(),t.max() , 500)
    pl.figure()
    pl.errorbar(t, y, yerr=yerr, fmt=".k", capsize=0)

    pl.plot(x , model(fitparams,x ) , color='red')
    pl.ylabel(r"$y$")
    pl.xlabel(r"$t$")
    pl.xlim(t.min(),t.max())
    pl.show()

    labels = ["jitter","rvsys", "k", "w", "ecc", "t0", "period"]
    fig = corner.corner(samples[:, :], truths=truth_par, labels=labels)
    fig.show()
