import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
# from isochrones import StarModel
from isochrones.dartmouth import Dartmouth_Isochrone


# spectroscopic properties (value, uncertainty)
Teff = (5770, 80)
logg = (4.44, 0.08)
feh = (0.00, 0.10)

ltsun = 3.76178
teffsun = 5777.

dar = Dartmouth_Isochrone()

ages = np.linspace(0, 12., 200)
masses = np.linspace(0.5, 1.5, 10)# [0.5, 1.0, 1.5]
# give
# mass,log10 (age),feh

l_track = []
l_radius = []
l_density = []
for mass in masses:
    track = dar(mass, ages, feh[0], return_df=False)
    l_track.append(track)  # return a dictionary instead of DataFrame
    # radius = 0.5*logl -2*log (teff) *lts1un
    # radius[i,*]=10.^( 0.5*data[2,i*140: (i+1)*140-1 ]  -2.*data[1,i*140: (i+1)*140-1]+2.*ltsun)
    # this works and can be used in the interpolator maybe with better teff
    # we dont need to calculate the radius because it is alredy available in the dictionary I
    #was just tryign to see if the equations were ok so that we can use them in a fiting code if we need
    # In this code it does mater because we dont use the radius anyway
    #
    l_radius.append((teffsun / track['Teff'])**2 * np.sqrt(10**track['logL']))
    l_density.append(mass / track['radius']**3.)


df = pd.DataFrame(data={"Mass": masses, "Track": l_track, "Radius": l_radius, "Density": l_density})

plt.figure()
for index, row in df.iterrows():
    plt.plot(row["Track"]['Teff'], row["Track"]['logg'], label="M={:.1f}".format(row["Mass"]))
plt.xlabel('Teff')
plt.ylabel('logg')
plt.ylim((5,0))
plt.legend(loc='upper right')
plt.errorbar(Teff[0], logg[0], xerr=Teff[1], yerr=logg[1])
plt.show()

plt.figure()
for index, row in df.iterrows():
    plt.plot(row["Track"]['Teff'], row["Density"], label="M={:.1f}".format(row["Mass"]))

plt.xlabel('Teff')
plt.ylabel('density')
plt.ylim((3,0))
plt.legend(loc='upper left')
plt.show()

g = 6.67428e-11
gm = 1.32712440041e20
msun = gm / g
msunjup = 1.047348644e3
mjup = msun / msunjup
rsun = 6.95508e8

mass = 1
mp = mjup * 0.46
P = 4.32250024 * 24. * 3600.


helps = (P / (2. * np.pi))**2.

# aoverr = (helps * g * (msun * mass + mp))**(1. / 3.) / (radius * rsun)
