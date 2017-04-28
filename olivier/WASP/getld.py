import numpy as np
from IPython.display import display, Latex

from ldtk import LDPSetCreator, BoxcarFilter, TabulatedFilter


import ldtk
# when I need to dowload a new file
# ldtk.client.Client(update_server_file_list=True)


#set filter example of box filters transmission as a function of wavelenght in nanometers.
'''
filters = [BoxcarFilter('a',450,550),
           BoxcarFilter('b',650,750),
           BoxcarFilter('c',850,950)]
'''

# kepler
wl_Kepler, T_Kepler = np.genfromtxt('kepler_response_hires1.txt', unpack=True)
wl_z, T_z = np.genfromtxt('Sloanz.txt', unpack=True)
wl_i, T_i = np.genfromtxt('Sloani.txt', unpack=True)
wl_R, T_R = np.genfromtxt('JohnsonR.txt', unpack=True)

wl_R = wl_R / 10.  # Conversion  angstrom to nm

# filters = [amp, tran ]

# use this function
# ldtk.filters.TabulatedFilter
# check this
# ldtk.filters.TabulatedFilter?
filt_Kepler = TabulatedFilter('Kepler', wl_Kepler, tm=T_Kepler, tmf=1.0)
filt_z = TabulatedFilter('Sloan z', wl_z, tm=T_z, tmf=1e-2)
filt_i = TabulatedFilter('Sloan i', wl_i, tm=T_i, tmf=1e-2)
filt_R = TabulatedFilter('Johnson R', wl_R, tm=T_R, tmf=1.0)
filt_NG = BoxcarFilter('NGTS', 520, 890)

filters = [filt_Kepler, filt_z, filt_i, filt_R, filt_NG]

# set stellar parameters or read them
teff_WASP151 = (5871, 57)
logg_WASP151 = (4.30, 0.11)
z_WASP151 = (0.10, 0.10)


# Download the model spectra for the filter set
sc = LDPSetCreator(teff=teff_WASP151, logg=logg_WASP151, z=z_WASP151, filters=filters)


# create the limb darkening profiles with their uncertainties for each filter, all contained in an
# LDPSet object using an MCMC
ps = sc.create_profiles(nsamples=2000)
ps.resample_linear_z()

# not sure we need this line
# cp = cm.spectral(linspace(0.1,1.0,6))

# get quadratic limb darkening coeficients and errors
qc, qe = ps.coeffs_qd()

print(qc)
print(qe)

# other options are
# linear ps.coeffs_ln()
# nonlinear ps.coeffs_nl()
# general model ps.coeffs_ge()


# print in the nice way the resutls
# this doesnt work but the next line does
for i, (c, e) in enumerate(zip(qc, qe)):
    display(Latex('u$_{i:d} = {c[0]:5.4f} \pm {e[0]:5.4f}\quad$'
                  'v$_{i:d} = {c[1]:5.4f} \pm {e[1]:5.4f}$'.format(i=i + 1, c=c, e=e)))

for i, (c, e) in enumerate(zip(qc, qe)):
    print('u$_{%.d} = %.4f \pm +%.4f$' % (i, c[0], e[0]))
    print('v$_{%.d} = %.4f \pm +%.4f$' % (i, c[1], e[1]))


# if we wasnt to use mcmc and a multipliver for the errors
# set multiplier or not
ps.set_uncertainty_multiplier(2)

# run mcmc
qc, qe = ps.coeffs_qd(do_mc=True, n_mc_samples=10000)

#  print in the same way
for i, (c, e) in enumerate(zip(qc, qe)):
    display(Latex('u$_{i:d} = {c[0]:5.4f} \pm {e[0]:5.4f}\quad$'
                  'v$_{i:d} = {c[1]:5.4f} \pm {e[1]:5.4f}$'.format(i=i + 1, c=c, e=e)))


for i, (c, e) in enumerate(zip(qc, qe)):
    print('u$_{%.d} = %.4f \pm +%.4f$' % (i, c[0], e[0]))
    print('v$_{%.d} = %.4f \pm +%.4f$' % (i, c[1], e[1]))


'''
compare with the result using IDL kepler and same stellar values
0.47500001      0.21798000
'''
