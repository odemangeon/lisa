import emcee
import corner
import numpy as np
import matplotlib.pyplot as pl

import george
from george import kernels

import pickle

def lnprob_gp(p, t, y, yerr):
    lp = lnprior_gp(p)
    if not np.isfinite(lp):
        return -np.inf
    lplike = lnlike_gp(p, t, y, yerr)
    if not not np.isfinite(lplike):
        return -np.inf
    return lp + lplike



if __name__ == "__main__":
    # read data

    ts, ys , yerrs = np.genfromtxt('/Users/sbarros/Documents/work/python/photodynamic/k2_19RVs.txt', unpack=True)

    t = ts.astype("float64")-7400.0
    y = ys.astype("float64")*1e3-7300.0
    yerr = yerrs.astype("float64")*1e3



    y = y - np.mean(y)


    truth_gp = [ np.log(0.9), 0.59575, 20.36978 , 14.39904,  40.0,  14.4,90,0.119,  23.26918,  7.92008, 4.8, 237-90., 0.095 , 24.27004 ,11.9068    ]

    data = (t, y, yerr)


    nwalkers=32


    sampler = pickle.load(open("rvs1_gp_run3.pkl", 'rb'))

    samples = sampler.flatchain

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
    #pl.savefig("rvs1_gp_pl_run4.png", dpi=150)




    #samples.shape   (32000, 5)


    # Make the corner plot.
    labels = ["amp","gamma", "period","tau", "trvsys", "k", "w", "ecc", "t0", "period1", "k2", "w2", "ecc2", "t02", "period2" ]
    #truth_gp the gps are not real but the others ones are
    fig = corner.corner(samples[:, :], truths=truth_gp[ :], labels=labels[ :])
    #fig.show()

    #fig.savefig("rvs1_gp_corner_run4.png", dpi=150)


    sampler.acceptance_fraction

    #fitparams = [ ampfit, gammafit, periodfit, taufit]


    for i in range(4,14):
        s1  =   np.percentile(samples[:,i], [16, 50, 84], axis=0)
        t0_right, t0_left =  s1[2]-result[i] ,  result[i] -s1[0]
        print(labels[i])
        print('%.5f^{+%.5f}_{-%.5f}' % ( result[i], t0_right,t0_left))
