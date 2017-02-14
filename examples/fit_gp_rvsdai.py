

#!/usr/bin/env python
# -*- coding: utf-8 -*-

#from __future__ import division, print_function
# copied on the 13 of fereuary from the code fit_gp_rvsquasinorwn2.py
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
    rv_model =  pl_rv_array(time, rvsys , k, np.deg2rad(w), ecc, t0, period)
    return rv_model

def model(params, time):
    ngp = 4
    return get_rv(params[0+ngp:6+ngp], time) + get_rv( np.append([0,], params[6+ngp:11+ngp ]), time)



# calculate likelihood of gp
def lnlike_gp(p, t, y, yerr):
    # fiting lna, lntau instead of a and tau so we need to transform

    a  = np.exp(p[0])**2.0
    gamma = p[1]
    period = p[2]
    tau =  p[3]
    # define the kernal
    kernel = a * kernels.ExpSquaredKernel(tau**2) * kernels.ExpSine2Kernel(2./(gamma)**2.0, period)
    gp = george.GP( kernel )
    #gp = george.GP(a * kernels.ExpSine2Kernel(gamma, period) + kernels.WhiteKernel(sigma)  )
    #Pre-compute the factorization of the matrix.
    gp.compute(t, yerr)
    # Compute the log likelihood
    gptotal = gp.lnlikelihood(y - model(p, t) )
    return gptotal


# define the prioirs of the gp
def lnprior_gp(p):
    lna, lngamma, lnperiod, lntau = p[:4]


    #if not -10 < lna <  3.0: # 4 give weird results
    if not -10 < lna <  -9: # 4 give weird results
        return -np.inf

    if not 10 < lntau <  19:
        return -np.inf

    #prior_lngamma = stats.norm(0.59575, 0.04)
    prior_lngamma = stats.norm(0.59575, 0.00004)
    plngamma = prior_lngamma.logpdf(lngamma)

    #prior_lntau = stats.norm(14.39904, 2.5)
    #prior_lntau = stats.norm(14.39904, 0.05)
    prior_lntau = stats.norm(14.39904, 0.00005)
    plntau = prior_lntau.logpdf(lntau)

    #prior_lnperiod = stats.norm(20.36978, 0.05)
    prior_lnperiod = stats.norm(20.36978, 0.00005)
    plnperiod = prior_lnperiod.logpdf(lnperiod)



    return plnperiod + plngamma + plntau   + lnprior_ind(p)


# for the granualtaion one I changed the priors maximum value to 10 instead of 5

# calculculate priors for the parameters
def lnprior_ind(p):
    ngp = 4
    rvsys, k, w, ecc, t0, period1 , k2, w2, ecc2, t02, period2  = p[ngp+0:ngp+11]



    if not -10 < rvsys < 10:
        return -np.inf

    '''
    prior_k = stats.norm(14.4, 5.0)
    pk1 = prior_k.logpdf(k)

    prior_w = stats.norm(179, 0.1)
    pw1 = prior_w.logpdf(w)

    prior_ecc = stats.norm(0.119, 0.0001)
    pecc1 = prior_ecc.logpdf(ecc)

    prior_t0 = stats.norm(7399.46948, 0.08)
    pt01 = prior_t0.logpdf(t0)

    prior_period = stats.norm(7.92008, 0.0013)
    pperiod1 = prior_period.logpdf(period1)
    '''

    if not 0 < k < 40.0:
        return -np.inf
    if not  0 <= w < 360:
        return -np.inf
    if not  0 <= ecc < 0.5: # 0.5 seams to be better then 0.3
        return -np.inf

    if not  66.8503 - 0.00184*5 < t0 < 66.8503 +0.00153*5.0:  # extrapolation gives 7399.46948  0.08 is an error of 2 hours
        return -np.inf

    prior_period1 = stats.norm(7.92008 ,  0.0013)
    pperiod1= prior_period1.logpdf(period1)
    #prior_w = stats.norm(179, 1.0)
    #pw = prior_w.logpdf(w)

    #prior_t0 = stats.norm(66.8503 ,0.00184)
        #prior_t02 = stats.norm(24.27004, 0.01)
    #pt0 = prior_t0.logpdf(t0)

    if not 0 <= k2 < 40.0:
        return -np.inf
    if not  -180 <= w2 < 180:
        return -np.inf
    if not  0 <= ecc2 < 0.5:
        return -np.inf
    '''
    if not  7400.7064 - 0.08 < t02 < 7400.7064 +0.08:  # extrapolation gives 7400.7064  0.08 is an error of 2 hours
            return -np.inf
    if not  11.9068-  0.0026 < period2 < 11.9068 + 0.0026: # error in the apper is 1.8 minutes i am allowng 4 minutes
            return -np.inf
    '''
    #prior_k2 = stats.norm(4.8, 0.1)
    #pk2 = prior_k2.logpdf(k2)


    #prior_w2 = stats.norm(16.3, 1.0)
    #pw2 = prior_w2.logpdf(w2)

    #prior_ecc2 = stats.norm(0.095, 0.1)
    #pecc2 = prior_ecc2.logpdf(ecc2)

    prior_t02 = stats.norm(67.19487, 0.04)
    #prior_t02 = stats.norm(24.27004, 0.01)
    pt02 = prior_t02.logpdf(t02)

    #if not  24.27004 - 0.15345*3.0 < t02 < 24.27004 +0.15345*3.0:  # extrapolation gives 7399.46948  0.08 is an error of 2 hours
    #    return -np.inf

    #prior_period2 = stats.norm(11.9068, 0.000026)
    prior_period2 = stats.norm(11.9068, 0.0026)
    pperiod2 = prior_period2.logpdf(period2)



    #return pk1 + pw1 + pecc1 + pt01 + pperiod1 + pk2 + pw2 + pecc2 + pt02 + pperiod2
    return  pperiod2 + pt02 + pperiod1  #+pk2 #pw2 +  pw2 + pecc2  +
# log probability = log prior+ log like  data given the model
def lnprob_gp(p, t, y, yerr):
    lp = lnprior_gp(p)
    if not np.isfinite(lp):
        return -np.inf
    lplike = lnlike_gp(p, t, y, yerr)
    if not np.isfinite(lplike):
        return -np.inf
    return lp + lplike


def fit_gp(initial, data, nwalkers=32):
    ndim = len(initial)
    p0 = [np.array(initial) + 1e-6 * np.random.randn(ndim)
          for i in range(nwalkers)]
    p0 = np.array(p0)
    p0[:, 11] = np.random.rand(nwalkers)*360.0-180.0
    p0[:, 6] = np.random.rand(nwalkers)*360.0
    p0[:, 5] = np.random.rand(nwalkers)*40.0
    p0[:, 10] = np.random.rand(nwalkers)*40.0

    sampler = emcee.EnsembleSampler(nwalkers, ndim, lnprob_gp, args=data)


    print("Running burn-in")
    p0, lnp, _ = sampler.run_mcmc(p0, 1000)

    sampler.reset()

    print("Running second burn-in")
    p = p0[np.argmax(lnp)]
    p0 = [p + 1e-8 * np.random.randn(ndim) for i in range(nwalkers)]
    p0, _, _ = sampler.run_mcmc(p0, 3000)
    sampler.reset()

    print("Running production")
    p0, _, _ = sampler.run_mcmc(p0, 3000)

    return sampler





if __name__ == "__main__":


    #read data
    #ts, ys , yerrs = np.genfromtxt('act3_tran_incibin.txt', unpack=True)
    ts, ys , yerrs = np.genfromtxt('/Users/sbarros/Documents/work/python/photodynamic/lisa/data/K2-19/all_dai.txt', unpack=True)

    # data already in meters per second but with full time
    t = ts.astype("float64")- 2457000.0
    y = ys.astype("float64")
    yerr = yerrs.astype("float64")

    #pl.figure()
    #pl.errorbar(t, y, yerr=yerr, fmt=".k", capsize=0)
    #pl.show()
    #true parameters or close initial parameters
    #truth_par =  [t0, rp, a , inc ]

    print("Fitting transit + GP ")
    data = (t, y, yerr)


    #truth_gp = [ np.log(0.9), 0.59575, 20.36978 , 14.39904,  40.0,  14.4,179,0.119,  23.26918,  7.92008, 4.8, 237, 0.095 , 24.27004 ,11.9068    ]
    truth_gp = [ 0.1, 0.59575, 20.36978 , 14.39904,  0.0,  14.4,90.0,0.119,  66.8503,  7.92008, 4.8, 16.3, 0.095 , 67.19487 ,11.9068    ]
    truth_gp = [-9.5, 0.59575, 20.36978 , 14.39904,  0.0,  14.4,90.0,0.119,  66.8503,  7.92008, 4.8, 16.3, 0.095 , 67.19487 ,11.9068    ]
    #truth_gp = [ -9.5, 0.59575, 20.36978 , 14.39904,  40.0,  14.4,90.0,0.119,  23.26918,  7.92008, 4.8, 16.3, 0.095 , 24.27004 ,11.9068    ]

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

    #pl.plot((samples[:,3], sampler.flatlnprobability, '.')

    samples = sampler.flatchain

    pickle.dump(sampler, open("rvs1_gp_dairun5.pkl", 'wb'),  4)

    #a, gamma, period

    ampfit = np.median(samples[:,0])
    gammafit = np.median(samples[:,1])
    periodfit = np.median(samples[:,2])
    taufit  = np.median(samples[:,3])
    print('par', ampfit,gammafit, periodfit, taufit)
    print('exp par', np.exp(ampfit),gammafit, periodfit, taufit )

    #fitparams[ trvsys, k, w, ecc, t0, period  ]
    fitpar1 = [ np.median(samples[:,4]),np.median(samples[:,5]), np.median(samples[:,6]), np.median(samples[:,7]), np.median(samples[:,8]), np.median(samples[:,9])]
    fitpar2 = [ np.median(samples[:,10]),np.median(samples[:,11]), np.median(samples[:,12]), np.median(samples[:,13]), np.median(samples[:,14])]
    offsetfit = np.median(samples[:,4])

    print('fitted parameters')
    print(fitpar1, fitpar2)


    result =[ampfit, gammafit, periodfit, taufit]
    result.extend(fitpar1)
    result.extend(fitpar2)

    #np.concatenate(([sigmafit, ampfit, gammafit, periodfit], fitpar1, fitpar2))

    # Plot the samples in data space.
    print("Making plots")
    x = np.linspace(t.min(),t.max() , 500)
    pl.figure()
    pl.errorbar(t, y, yerr=yerr, fmt=".k", capsize=0)

    pl.plot(x, model( result , x),color='green')


    #for s in samples[np.random.randint(len(samples), size=24)]:
    #    gp = george.GP(np.exp(s[0]) * kernels.ExpSine2Kernel(np.exp(s[1]),np.exp(s[2])))
    #    gp.compute(t, yerr)
    #    #m = gp.sample_conditional(y , x) #+ model(s[2:], x)
    #    m = gp.sample_conditional(y - model( fitparams[0:4] , t), x) + model(fitparams[0:4], x)
    #    pl.plot(x, m, color="#4682b4", alpha=0.3)

    kernel = np.exp(ampfit)**2  * kernels.ExpSquaredKernel(taufit**2) * kernels.ExpSine2Kernel(2./(gammafit**2.0),periodfit)
    gp = george.GP(kernel   )

    gp.compute(t, yerr)
    # Compute the prediction conditioned on the observations and plot it.
    m = gp.sample_conditional(y -  model(result , t) , x)
    #m = gp.sample_conditional(y - model( truth_gp[3:7] , t), x) + model(truth_gp[3:7], x)

    pl.plot(x , m + offsetfit , color='blue')
    pl.plot(x , m + model(result , x), color='red')

    print('red',gp.lnlikelihood(y))


    pl.ylabel(r"$y$")
    pl.xlabel(r"$t$")
    pl.xlim(t.min(),t.max())
    pl.title("results with Gaussian process noise model")
    #pl.savefig("../_static/model/gp-results.png", dpi=150)
    #pl.show()
    pl.savefig("rvs1_gp_pl_dairun5.png", dpi=150)




    #samples.shape   (32000, 5)


    # Make the corner plot.
    labels = ["amp","gamma", "period","tau", "trvsys", "k", "w", "ecc", "t0", "period1", "k2", "w2", "ecc2", "t02", "period2" ]
    #truth_gp the gps are not real but the others ones are
    fig = corner.corner(samples[:, :], truths=truth_gp[ :], labels=labels[ :])
    #fig.show()

    fig.savefig("rvs1_gp_corner_dairun5.png", dpi=150)


    sampler.acceptance_fraction

    #fitparams = [ ampfit, gammafit, periodfit, taufit]


    for i in range(4,14):
        s1  =   np.percentile(samples[:,i], [16, 50, 84], axis=0)
        t0_right, t0_left =  s1[2]-result[i] ,  result[i] -s1[0]
        print(labels[i])
        print('%.5f^{+%.5f}_{-%.5f}' % ( result[i], t0_right,t0_left))
