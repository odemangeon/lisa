
# coding: utf-8

# In[3]:

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
import emcee
import batman
import sys


# In[4]:

# you need to have exonailer installed
# append to sys.path the directory where you find the file 'ajplanet.so'
from utilities.ajplanet import pl_rv_array as rv_curve


# In[5]:

fix_ecc = True


# In[6]:

class Planet(object):
    def __init__(self):
        # transit parameters
        self.rp = 0.          # planet radius (in units of stellar radii)
        self.a = 0.           # semi-major axis (in units of stellar radii)
        self.inc = 0.         # orbital inclination (in degrees)
        self.t0 = 0.          # time of inferior conjunction
        self.jitter_lc = 0.
        
        # these are fixed
        self.limb_dark = "quadratic" # limb darkening model
        self.u = [.4983, 0.2042]     # limb darkening coefficients

        # rv parameters
        self.rvsys = 0.      # radial velocity systematic velocity
        self.K = 0.          # semi-amplitude
        self.T0 = 0.         # time of periastron (function of self.t0, not a free parameter)
        self.jitter_rv = 0.

        # parameters shared between transit and rv
        self.period = 0. # orbital period
        self.ecc = 0.    # eccentricity
        self.w = 0.      # longitude of periastron (in degrees)


        
        self.N_free_parameters = 9 if fix_ecc else 11


        ## build the batman model
        self.params = batman.TransitParams()
        self.params.limb_dark = self.limb_dark  # limb darkening model
        self.params.u = self.u                  # limb darkening coefficients

        self.labels = [r'$R_p / R_*$',
                       r'$a/R_*$',
                       r'$i$',
                       r'$t_0$',
                       r'$s_{\rm lc}$',
                       'vsys',
                       r'$K$',
                       r'$s_{\rm RV}$',
                       r'$P$',
                       r'$e$',
                       r'$\omega$']
        if fix_ecc:
            self.labels.pop(10)
            self.labels.pop(9)


    def set_rv_parameters(self, pars):
        """ pars should be [rvsys, K, jitter_rv] """
        self.rvsys, self.K, self.jitter_rv = pars


    def set_transit_parameters(self, pars):
        """ pars should be [rp, a, inc, t0, jitter_lc] """
        self.rp, self.a, self.inc, self.t0, self.jitter_lc = pars

    def set_shared_parameters(self, pars):
        """ pars should be [period, (ecc, w)] """
        if fix_ecc:
            self.period = pars
            self.ecc = 0.
            self.w = 90.
        else:
            self.period, self.ecc, self.w = pars
        self.T0 = self.t0 # get_tp(self.period, self.ecc, self.w, self.t0)
        

    def get_rv_curve(self, time, debug=False):
        # print self.w
        return rv_curve(time,
                        self.rvsys, self.K, np.deg2rad(self.w), 
                        self.ecc, self.T0, self.period)

    def get_transit_curve(self, time, debug=False):
        self.params.t0 = self.t0
        self.params.per = self.period
        self.params.rp = self.rp
        self.params.a = self.a
        self.params.inc = self.inc
        self.params.ecc = self.ecc
        self.params.w = self.w

        self.batman_model = batman.TransitModel(self.params, time)
        light_curve = self.batman_model.light_curve(self.params)
        
        return light_curve


    def set_priors(self):
        """ Define the prior distributions """
        
        self.prior_rp = stats.uniform(0.13, 0.02)       # planet radius (in units of stellar radii)
        self.prior_a = stats.norm(10.7259218, 1)           # semi-major axis (in units of stellar radii)
        self.prior_inc = stats.norm(86.66, 0.1)        # orbital inclination (in degrees)
        self.prior_t0 = stats.norm(57064.4327, 1e-3)  # time of inferior conjunction
        self.prior_jitter_lc = stats.reciprocal(0.001, 0.1)

        # rv parameters
        self.prior_rvsys = stats.uniform(32.86, .02)    #
        self.prior_K = stats.uniform(80, 50)      #
        self.prior_jitter_rv = stats.reciprocal(0.1, 30.)
 
        # parameters shared between transit and rv
        #self.prior_period = stats.uniform(3.23, 0.04)   # orbital period
        self.prior_period = stats.norm(3.25883, 1e-5)   # orbital period
        
        if not fix_ecc:
            self.prior_ecc = stats.uniform(0, 1)  # eccentricity
            self.prior_w = stats.uniform(0, 360)  # longitude of periastron (in degrees)


    def get_from_prior(self, nwalkers):

        self.set_priors()

        pars_from_prior = []
        for i in range(nwalkers):
            random_rp = self.prior_rp.rvs() # planet radius (in units of stellar radii)
            random_a = self.prior_a.rvs() # semi-major axis (in units of stellar radii)
            random_inc = self.prior_inc.rvs() # orbital inclination (in degrees)
            random_t0 = self.prior_t0.rvs() # time of inferior conjunction
            random_jitter_lc = self.prior_jitter_lc.rvs()
            
            # rv parameters
            random_rvsys = self.prior_rvsys.rvs()
            random_K = self.prior_K.rvs()
            random_jitter_rv = self.prior_jitter_rv.rvs()

            # parameters shared between transit and rv
            random_period = self.prior_period.rvs() # orbital period
            
            pars_from_prior.append([random_rp,random_a, random_inc, random_t0, random_jitter_lc,
                                    random_rvsys, random_K, random_jitter_rv,
                                    random_period])

            if not fix_ecc:
                random_ecc = self.prior_ecc.rvs()       # eccentricity
                random_w = self.prior_w.rvs()           # longitude of periastron (in degrees)
                
                pars_from_prior.append(random_ecc, random_w)

            
        return pars_from_prior


# In[7]:

class Data(object):
    def __init__(self, rv_file, lc_file, skip_rv_rows=2, skip_lc_rows=0):
        
        self.rv_file = rv_file
        self.lc_file = lc_file

        # read RVs
        self.RVtime, self.RV, self.RVerror = np.loadtxt(rv_file, 
                                                        unpack=True, skiprows=skip_rv_rows)

        # read light curve
        self.LCtime, self.LC, self.LCerror = np.loadtxt(lc_file,
                                                        unpack=True, skiprows=skip_lc_rows)

        self.N_rvs = self.RVtime.size
        self.N_lc = self.LCtime.size


# In[30]:

def lnlike(pars, planet, data, debug=False):
    """ pars should be
    # [rp, a, inc, t0, jitter_lc,
    #  rvsys, K, jitter_rv,
    #  period, ecc, w]
    """
    log2pi = np.log(2*np.pi)


    # set the transit params
    planet.set_transit_parameters(pars[:5])
    # set the RV params
    planet.set_rv_parameters(pars[5:8])
    # set the shared params
    planet.set_shared_parameters(pars[8:])

    if debug: print planet.t0, planet.T0
        
    # calculate the lnlike for transit
    transit_model = planet.get_transit_curve(data.LCtime)
    if (transit_model == 1.).all():
        print 'Error!! transit_model=1'

    sigma = data.LCerror**2 + planet.jitter_lc**2
    chi2 = np.log(sigma)/2. + (data.LC - transit_model)**2 / (2. * (sigma))
    log_like_transit = - data.N_lc/2.0 * np.log(2*np.pi) - np.sum(chi2)

    log_like_transit2 = stats.norm(loc=transit_model, scale=np.sqrt(sigma)).logpdf(data.LC).sum()
    
    if debug: print log_like_transit, log_like_transit2
    assert np.allclose(log_like_transit, log_like_transit2)
    
    if debug: print 'log_like_transit', log_like_transit

    # calculate the lnlike for RVs
    rv_model = planet.get_rv_curve(data.RVtime)
    assert not (rv_model == 1.).all()
    
    sigma = data.RVerror**2 + planet.jitter_rv**2
    chi2 = np.log(sigma)/2. + (data.RV - rv_model)**2 / (2. * (sigma))
    log_like_rv = - data.N_rvs/2.0 * np.log(2*np.pi) - np.sum(chi2)

    log_like_rv2 = stats.norm(loc=rv_model, scale=np.sqrt(sigma)).logpdf(data.RV).sum()
    
    if debug: print log_like_rv, log_like_rv2
    assert np.allclose(log_like_rv, log_like_rv2)
    if debug: print 'log_like_rv', log_like_rv

    # sum lnlikes
    log_like = log_like_transit + log_like_rv
    if debug: print log_like

    if not np.isfinite(log_like):
        return -np.inf
    else:
        return log_like


# In[31]:

def lnprior(pars, planet, data, debug=False, fix_ecc=fix_ecc):
    """ pars should be
    # [rp, a, inc, t0, jitter_lc,
    #  rvsys, K, jitter_rv,
    #  period, ecc, w]
    """

    # transit parameters
    prior_rp = planet.prior_rp.logpdf(pars[0]) # planet radius (in units of stellar radii)
    prior_a = planet.prior_a.logpdf(pars[1]) # semi-major axis (in units of stellar radii)
    prior_inc = planet.prior_inc.logpdf(pars[2]) # orbital inclination (in degrees)
    prior_t0 = planet.prior_t0.logpdf(pars[3]) # time of inferior conjunction
    prior_jitter_lc = planet.prior_jitter_lc.logpdf(pars[4])
    
    # rv parameters
    prior_rvsys = planet.prior_rvsys.logpdf(pars[5])
    prior_K = planet.prior_K.logpdf(pars[6])
    # prior_T0 = 0.
    prior_jitter_rv = planet.prior_jitter_rv.logpdf(pars[7])

    # parameters shared between transit and rv
    prior_period = planet.prior_period.logpdf(pars[8]) # orbital period

    ln_prior = prior_rp + prior_a + prior_inc + prior_t0 + prior_jitter_lc                 + prior_rvsys + prior_K + prior_jitter_rv                 + prior_period

    
    if not fix_ecc:
        prior_ecc = planet.prior_ecc.logpdf(pars[9]) # eccentricity
        prior_w = planet.prior_w.logpdf(pars[10])    # longitude of periastron (in degrees)

        ln_prior += prior_ecc + prior_w
        
    if debug:
        print prior_rp, '\n', prior_a, '\n', prior_inc, '\n', prior_t0, '\n', prior_jitter_lc                , '\n', prior_rvsys, '\n', prior_K, '\n', prior_jitter_rv                , '\n', prior_period, '\n', prior_ecc, '\n', prior_w

    
    if debug: print ln_prior

    return ln_prior


# In[32]:

def lnprob(pars, planet, data, debug=True):
    lp = lnprior(pars, planet, data)
    ll = lnlike(pars, planet, data)
    return lp + ll


# In[34]:

planet = Planet()
data = Data(rv_file='EPIC-9792_SOPHIE.rdb', 
            lc_file='cuttransits.txt')


# In[54]:

ndim, nwalkers = planet.N_free_parameters, 30

# get random starting positions from the priors
pos = planet.get_from_prior(nwalkers)


# In[46]:

import emcee

sampler = emcee.EnsembleSampler(nwalkers, ndim, lnprob, args=(planet, data), threads=1)
out = sampler.run_mcmc(pos, 5000)


# In[47]:

burnin = 0
samples = sampler.chain[:, burnin:, :].reshape((-1, ndim))


# In[48]:

samples.shape


# In[49]:

plt.figure(figsize=(10, 12))
n = samples.shape[1]
for i in range(n):
    plt.subplot(n, 1, i+1)
    plt.plot(samples[::10, i])

plt.tight_layout()
plt.show()


# In[40]:

plt.figure(figsize=(10, 12))
for i in range(nwalkers):
    plt.plot(sampler.chain[i, :, 0])

plt.tight_layout()
plt.show()


# In[23]:

print sampler.lnprobability.shape
plt.plot(sampler.lnprobability[:,burnin:].T)
plt.show()


# In[45]:

import corner

fig = corner.corner(samples[:, :], labels=planet.labels)
#fig.savefig('samples.png')
plt.show()


# In[50]:

median_pars = np.median(samples, axis=0)

print ['%8s' % s.replace('$', '').replace('_', '').replace('\\rm', '').replace('\\','') for s in planet.labels]
print ['%8.4f' % s for s in median_pars]


# In[51]:

def random_RVcurve(time, ncurves=10):
    ind = np.random.choice(range(samples.shape[0]), size=ncurves, replace=False)
    
    curves = []
    
    for i in ind:
        planet.set_transit_parameters(samples[i, :5])
        # set the RV params
        planet.set_rv_parameters(samples[i, 5:8])
        # set the shared params
        planet.set_shared_parameters(samples[i, 8:])
        
        curves.append(planet.get_rv_curve(time))
    return curves

def random_LCcurve(time, ncurves=10):
    ind = np.random.choice(range(samples.shape[0]), size=ncurves, replace=False)
    
    curves = []
    
    for i in ind:
        planet.set_transit_parameters(samples[i, :5])
        # set the RV params
        planet.set_rv_parameters(samples[i, 5:8])
        # set the shared params
        planet.set_shared_parameters(samples[i, 8:])
        
        curves.append(planet.get_transit_curve(time))
    return curves



# In[52]:

# set the transit params
#median_pars[2] = 85
#median_pars[3] = 57064.43
planet.set_transit_parameters(median_pars[:5])
# set the RV params
planet.set_rv_parameters(median_pars[5:8])
# set the shared params
planet.set_shared_parameters(median_pars[8:])

print planet.T0


# In[53]:

fig = plt.figure()
ax = fig.add_subplot(311)

time = np.linspace(data.LCtime.min(), data.LCtime.max(), 5000)
lc = planet.get_transit_curve(time)

ax.plot(time, lc, lw=2)
#for curve in random_LCcurve(time, ncurves=10):
#    ax.plot(time, curve*1e-3, 'k', alpha=0.1)
ax.plot(data.LCtime, data.LC, 'o', ms=2)


ax = fig.add_subplot(312)

phase0 = (data.LCtime - planet.t0) / planet.period
phase = phase0 % 1
phase[np.where(phase>0.5)[0]]-=1

ax.plot(phase, data.LC, 'o')

phase = ((time - planet.t0) / planet.period) % 1
phase[np.where(phase>0.5)[0]]-=1

LCfold = lc[np.argsort(phase)]
ax.plot(np.sort(phase), LCfold, '-')

ax.set_xlim([-0.1, 0.1])


ax = fig.add_subplot(313)

time = np.linspace(data.RVtime.min(), data.RVtime.max(), 1000)
rv = planet.get_rv_curve(time)
ax.errorbar(data.RVtime, data.RV - median_pars[5], data.RVerror, fmt='o')
ax.plot(time, rv*1e-3, 'k', alpha=0.7)

#for curve in random_RVcurve(time, ncurves=50):
#    ax.plot(time, curve*1e-3, 'k', alpha=0.1)

#ax.set_xlim(data.LCtime.min(), data.RVtime.max())

plt.show()


# In[ ]:



