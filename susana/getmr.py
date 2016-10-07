import matplotlib.pyplot as plt
import numpy as np

from isochrones import StarModel
from isochrones.dartmouth import Dartmouth_Isochrone

from scipy import stats

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
model.plot_samples('radius')
plt.show()


med=sta[0]
print('med radius')
print('%.2f^{+%.2f}_{-%.2f}' % (med, sta[1],sta[2]))
print('mode', stats.mode( rad))
sigma =  np.std(rad)
print('sigam', sigma)

mass, sta = model.prop_samples('mass')
model.plot_samples('mass')

med=sta[0]
print('med mass')
print('%.2f^{+%.2f}_{-%.2f}' % (sta[0], sta[1],sta[2]))
print('mode')
print(stats.mode(mass))
sigma =  np.std(mass)
print('sigam', sigma)


density = mass/rad**3.
plt.hist(density, bins=50,normed=True, histtype='step', lw=3)
plt.xlabel('density')
plt.ylabel('Normalized count')
plt.show()
print('mean', np.mean(density))
print('median', np.median(density))
print('stddev', np.std(density))
#print('mode', stats.mode(density))


#this one shows mass , age, feh
model.triangle()
plt.show()


# this one has mass radius feff feh age and logg, feh teff
model.triangle_plots()
plt.show()

# this one has mass radius age
model.triangle(params=['mass','radius','age']);
plt.show()
