import rebound
import numpy as np

import matplotlib.pyplot as pl

'''
http://rebound.readthedocs.io/en/latest/python_api.html#rebound.Orbit


Attributes

d	(float) radial distance from reference
v	(float) velocity relative to central object’s velocity
h	(float) specific angular momentum
P	(float) orbital period (negative if hyperbolic)
n	(float) mean motion (negative if hyperbolic)
a	(float) semimajor axis
e	(float) eccentricity
inc	(float) inclination
Omega	(float) longitude of ascending node
omega	(float) argument of pericenter
pomega	(float) longitude of pericenter
f	(float) true anomaly
M	(float) mean anomaly
l	(float) mean longitude = Omega + omega + M
theta	(float) true longitude = Omega + omega + f
T	(float) time of pericenter passage

#all angles are in radians
'''

#this one for sure is made with test7

#predicted_rvsdym_new.txt

ts, rvdyms , rvs1, rvs2 = np.genfromtxt('/Users/sbarros/Documents/work/mercury/k350/predicted_rvsdym_new.txt', unpack=True)

rv_times = ts.astype("float64")[1:100000:10]-ts[1]
rvdym = rvdyms.astype("float64")[1:100000:10]
rvs1 =  rvs1.astype("float64")[1:100000:10]
rvs2 =  rvs2.astype("float64")[1:100000:10]


npoints = len(rv_times)

Total = 7013.0
stepdt =  0.54
sim = rebound.Simulation()
sim.integrator = 'whfast'
#sim.G = 6.674e-11
sim.units = ('d', 'AU', 'Msun')
#sim.dt = stepdt # Sets the timestep (will change for adaptive integrators such as IAS15).

m0= 0.97061886114722451
m1= 0.00014932535033861051
m2= 6.3494930075318071e-05
#add a star
sim.add(m=m0)
# add planets
sim.add(m=m1, a= 0.0769897231391472 ,e=0.08695861035152036,omega=np.radians(214.09963960544101),
         M= np.radians(227.0106215751976)   , inc=np.radians(88.74540570700838), Omega=np.radians(180.0), primary=sim.particles[0])
sim.add(m=m2, a=0.1010372336036388 , e=0.1124375085494681,omega = np.radians(250.7761358353399),
         M =  np.radians(74.670769462202), inc =  np.radians(88.95595877430457),  Omega=np.radians(167.5154616287283) ,primary=sim.particles[0] )


sim.dt = 0.01
sim.move_to_com() # moves the zero point
#sim.convert_particle_units('m', 's', 'kg')
rv_out=np.zeros_like(rv_times)
particles = sim.particles

day1 = 86400.0 # days in seconds
au= 1.495978707e11 # AU in meters

for i, time in enumerate(rv_times):
    sim.integrate(time)
    # corrected on the 7 september 2018 due to an error with the sign of the RVs
    rv_out[i] = -particles[0].vz*au /(day1)
    #rv_out[i] = ( particles[2].vz * m2/m0  )*au /(day1)


pl.plot(rv_times,rvdym , '.' )
#pl.plot(rv_times,rvs2 , '.' )
pl.plot(rv_times,-rv_out, '.', color='r' )
pl.show()
