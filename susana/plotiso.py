import matplotlib.pyplot as plt
import numpy as np

#from isochrones import StarModel
from isochrones.dartmouth import Dartmouth_Isochrone


#spectroscopic properties (value, uncertainty)
Teff = (5770, 80)
logg = (4.44, 0.08)
feh = (0.00, 0.10)

ltsun = 3.76178
teffsun = 5777.

dar = Dartmouth_Isochrone()


ages = np.linspace(3,10.,200)
# give
#mass,log10 (age),feh
track1 = dar(0.5,ages,feh[0], return_df=False) #return a dictionary instead of DataFrame
track2 = dar(1.0,ages,feh[0], return_df=False)
track3 = dar(1.5,ages,feh[0], return_df=False)

#radius = 0.5*logl -2*log (teff) *lts1un
#radius[i,*]=10.^( 0.5*data[2,i*140: (i+1)*140-1 ]  -2.*data[1,i*140: (i+1)*140-1]+2.*ltsun)

# this works and can be used in the interpolator maybe with better teff
radius = (teffsun/track1['Teff'])**2 *np.sqrt( 10**track1['logL'] )




plt.plot(track1['Teff'],track1['logg'],label='M=0.5')
plt.plot( track2['Teff'],track2['logg']  ,label='M=1')
plt.plot(track3['Teff'],track3['logg'],label='M=1.5')
plt.xlabel('Teff')
plt.ylabel('logg')
plt.legend(loc='lower right')
plt.errorbar(Teff[0], logg[0], xerr=Teff[1], yerr=logg[1])
plt.show()


density1 = 0.5 /track1['radius']**3.
density2 = 1.0 /track2['radius']**3.
density3 = 1.5 /track3['radius']**3.








plt.plot(track1['Teff'],density1,label='M=0.5')
plt.plot( track2['Teff'],density2   ,label='M=1')
plt.plot(track3['Teff'], density3,label='M=1.5')
plt.xlabel('Teff')
plt.ylabel('density')
plt.legend(loc='upper right')
plt.show()

g = 6.67428e-11
gm = 1.32712440041e20
msun = gm/g
msunjup = 1.047348644e3
mjup = msun/msunjup
rsun = 6.95508e8

mass = 1
mp = mjup*0.46
P =  4.32250024 *24.*3600.


help = (P/(2.*np.pi ))**2.

aoverr = ( help*g*( msun*mass+mp)   ) **(1./3.) / (radius * rsun)
