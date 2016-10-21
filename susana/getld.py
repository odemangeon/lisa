import numpy as np
from IPython.display import display, Latex

from ldtk import LDPSetCreator, BoxcarFilter



#set filter example of box filters transmission as a function of wavelenght in nanometers.
'''
filters = [BoxcarFilter('a',450,550),
           BoxcarFilter('b',650,750),
           BoxcarFilter('c',850,950)]
'''
# kepler
filters = np.genfromtxt('kepler_response_hires1.txt', unpack=True)


#set stellar parameters or read them
teff = (5400,50)
logg = (4.5,0.1)
z = (0.0,0.05)


#Download the model spectra for the filter set
sc = LDPSetCreator(teff=teff,logg=logg , z=z, filters=filters)


#create the limb darkening profiles with their uncertainties for each filter, all contained in an LDPSet object.
ps = sc.create_profiles(nsamples=2000)
ps.resample_linear_z()

# not sure we need this line
cp = cm.spectral(linspace(0.1,1.0,6))



# get quadratic limb darkening coeficients are errors
qc,qe = ps.coeffs_qd()

#other options are
# linear ps.coeffs_ln()
# nonlinear ps.coeffs_nl()
# general model ps.coeffs_ge()


# print in the nice way the resutls
for i,(c,e) in enumerate(zip(qc,qe)):
    display(Latex('u$_{i:d} = {c[0]:5.4f} \pm {e[0]:5.4f}\quad$'
                  'v$_{i:d} = {c[1]:5.4f} \pm {e[1]:5.4f}$'.format(i=i+1,c=c,e=e)))


# if we wasnt to use mcmc and a multipliver for the errors
# set multiplier or not
ps.set_uncertainty_multiplier(2)

# run mcmc
qc,qe = ps.coeffs_qd(do_mc=True, n_mc_samples=10000)

#  print in the same way
for i,(c,e) in enumerate(zip(qc,qe)):
    display(Latex('u$_{i:d} = {c[0]:5.4f} \pm {e[0]:5.4f}\quad$'
                  'v$_{i:d} = {c[1]:5.4f} \pm {e[1]:5.4f}$'.format(i=i+1,c=c,e=e)))
