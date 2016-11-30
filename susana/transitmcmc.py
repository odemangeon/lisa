import emcee
import corner
import numpy as np
import matplotlib.pyplot as pl
from scipy import stats





# model

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






def lnlike_ind(p, x, y, yerr):
    jitter = p[4]
    inv_sigma2 = 1.0/(yerr**2 + model(p, x) **2*np.exp(2*jitter))
    return -0.5*(np.sum( (y - model(p, x)) **2 *inv_sigma2 - np.log(inv_sigma2)) )



# calculculate uniform prioirs for the parameters
def lnprior_ind(p):
    t0, rp, a , inc , jitter = p

    if not -0.01 < t0 < 0.01:
        return -np.inf
    if not  0 < rp < 0.5:
        return -np.inf
    if not  70 < inc < 90.0:
        return -np.inf

    if not  -50.0 < jitter < 1.0:
        return -np.inf

    prior_a = stats.reciprocal(0.1, 5.)
    pa = prior_a.logpdf(a)

    return pa




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
    p0, _, _ = sampler.run_mcmc(p0, 1000)
    sampler.reset()

    print("Running production")
    p0, _, _ = sampler.run_mcmc(p0, 2000)

    return sampler



if __name__ == "__main__":

    #read data
    ts, ys , yerrs = np.genfromtxt('act3_tran.txt', unpack=True)

    t = ts.astype("float64")
    y = ys.astype("float64")
    yerr = yerrs.astype("float64")

    #true parameters or close initial parameters
    #truth_par =  [t0, rp, a , inc ]

    print("Fitting transit")
    data = (t, y, yerr)
    truth_par =  [0, 0.1093, 2.978, 86.3, 1.0]

    '''
    pl.figure()
    pl.errorbar(t, y, yerr=yerr, fmt=".k", capsize=0)
    pl.plot(t , model(truth_par ,t  ) , color='red')
    pl.show()
    '''

    sampler = fit_ind(truth_par, data)

    samples = sampler.flatchain

    #plot the chains
    nwalkers=32
    for i in range(0,nwalkers-1): pl.plot(sampler.chain[i,:, 0])
    pl.show()



    #fitparams[ t0, rp, a , inc ]
    fitparams = [ np.median(samples[:,0]),np.median(samples[:,1]), np.median(samples[:,2]), np.median(samples[:,3]) , np.median(samples[:,4]) ]

    print('fitted parameters')
    print(fitparams)

    # Plot the samples in data space.
    print("Making plots")
    samples = sampler.flatchain
    x = np.linspace(t.min(),t.max() , 500)
    pl.figure()
    pl.errorbar(t, y, yerr=yerr, fmt=".k", capsize=0)

    pl.plot(t , model(fitparams[0:4],t  ) , color='red')
    pl.ylabel(r"$y$")
    pl.xlabel(r"$t$")
    pl.xlim(t.min(),t.max())
    pl.show()


    labels = ["t0","rp", "a", "inc", "jitter"]
    fig = corner.corner(samples[:, :], truths=truth_par, labels=labels)
    fig.show()

    sampler.acceptance_fraction

#fitted parameters
#[-2.7131709165640811e-05, 0.10941545982684069, 2.9595189144579481, 85.683615499256405, -30.405381532809884]
