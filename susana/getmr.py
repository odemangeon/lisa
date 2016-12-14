import matplotlib.pyplot as plt
import numpy as np

from isochrones import StarModel
from isochrones.dartmouth import Dartmouth_Isochrone

from scipy import stats


import sys
sys.path.append('/Users/sbarros/Documents/work/python/photodynamic/lisa/')

#from source.tools.stats.loc_scale_estimator import  rob_mom

from source.tools.distribution_anali  import getconfi

#spectroscopic properties (value, uncertainty)
Teff = (5770, 80)
logg = (4.44, 0.08)
feh = (0.00, 0.10)

dar = Dartmouth_Isochrone()
#dar = Dartmouth_Isochrone(minage=9

model  = StarModel(dar, Teff=Teff, logg=logg, feh=feh)
model.fit()

# should ignore the maxlike and do our own analysis of the samples
#model.maxlike()

# thesea are the same as below but we have the samples
#model.plot_samples('radius')
#model.plot_samples('mass')


rad, sta = model.prop_samples('radius')
'''
s1  =   np.percentile(rad, [16, 50, 84], axis=0)
mrad = np.asarray(rob_mom(rad))[0]
rad_right, rad_left =  s1[2]-mrad,  mrad-s1[0]
#map(lambda v: (v[1], v[2]-v[1], v[1]-v[0]),
                             #zip(*np.percentile(rad, [16, 50, 84], axis=0))
the following line is equavalent to the lines comeneted above
'''
rad_right, mrad, rad_left = getconfi(rad, 1)

print('rob mom radius condifence')
print('%.2f^{+%.2f}_{-%.2f}' % (mrad, rad_right,rad_left))
print('mode', stats.mode( rad))
sigma =  np.std(rad)
print('sigma', sigma)
model.plot_samples('radius')
plt.show()


mass, sta = model.prop_samples('mass')
'''
s1  =   np.percentile(mass, [16, 50, 84], axis=0)
mmas = np.asarray(rob_mom(mass))[0]
mas_right, mas_left =  s1[2]-mmas,  mmas-s1[0]
the following line is equavalent to the lines comeneted above
'''
mas_right,mmas ,  mas_left = getconfi(mass, 1)

print('rob mom mass condifence')
print('%.2f^{+%.2f}_{-%.2f}' % (mmas, mas_right, mas_left))
print('mode')
print(stats.mode(mass))
sigma =  np.std(mass)
print('sigam', sigma)
model.plot_samples('mass')
plt.show()



density = mass/rad**3.
'''
s1  =   np.percentile(density, [16, 50, 84], axis=0)
mdens = np.asarray(rob_mom(density))[0]
dens_right, dens_left =  s1[2]-mdens,  mdens-s1[0]
the following line is equavalent to the lines comeneted above
'''
dens_right, mdens ,dens_left  = getconfi(density, 1)
print('rob mom density condifence')
print('%.2f^{+%.2f}_{-%.2f}' % (mdens, dens_right, dens_left))


plt.hist(density, bins=50,normed=True, histtype='step', lw=3)
plt.xlabel('density')
plt.ylabel('Normalized count')
plt.show()
print('mean', np.mean(density))
print('median', np.median(density))
print('stddev', np.std(density))
print('mode', stats.mode(density))


#this one shows mass , age, feh
#model.triangle()
#plt.show()


# this one has mass radius feff feh age and logg, feh teff
#model.triangle_plots()
#plt.show()

# this one has mass radius age
model.triangle(params=['mass','radius','age']);
plt.show()
