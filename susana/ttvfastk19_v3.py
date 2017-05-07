
import numpy as np
import matplotlib.pyplot as pl
from fttvfast_v3 import fttvfast_v3

'''
Depending on what type of input you want to give (the options are Jacobi elements, Astrocentric elements, Astrocentric cartesian) the form of the input parameter array will be either
For elements:
G Mstar Mplanet Period E I LongNode Argument Mean Anomaly (at t=t0, the reference time)....
repeated for each planet
: 2+nplanets*7 in length
or, for Cartesian:
G Mstar Mplanet X Y Z VX VY VZ (at t=t0, the reference time)....
repeated for each planet
: 2+nplanets*7 in length

G is in units of AU^3/day^2/M_sun, all masses are in units of M_sun, the Period is in units of days, and the angles are in DEGREES. Cartesian coordinates are in AU and AU/day. The coordinate system is as described in the paper text. One can use different units, as long as G is converted accordingly.
* mass: Mplanet in units of M_sun
* period: Period in days
* eccentricity: E between 0 and 1
* inclination: I in units of degrees
* longnode: Longnode in units of degrees
* argument: Argument in units of degrees
* mean_anomaly: mean anomaly in units of degrees

'''

'''
Parametrisatons Huber et al. (2013)
page 38
 do we need to fit the mean anomaly or we calculate it?
 the mean anomaly for the referene time depends on the eccentricity, omega, knowing a transit time , period
 I dont think we fit the mean anomaly


q_plus = (mb + mc) /stellar_mass
q_p = mb/mc

h_minus = (Pb/Pc)**(2.0/3.0) * eb * np.cos( np.deg2rad(wb)) − ec *np.cos (  np.deg2rad(wc))
h_plus = (Pb/Pc)**(2.0/3.0) * eb * np.cos( np.deg2rad(wb)) + ec *np.cos (  np.deg2rad(wc))
k_minus = (Pb/Pc)**(2.0/3.0) * eb * np.sin( np.deg2rad(wb)) − ec *np.sin (  np.deg2rad(wc))
k_plus = (Pb/Pc)**(2.0/3.0) * eb * np.sin( np.deg2rad(wb)) + ec *np.sin (  np.deg2rad(wc))



mb = stellar_mass * q_plus/ (1.0 + 1.0/q_p )
mc = stellar_mass * q_plus/(1.0 + q_p )

eb =  np.sqrt (  ( (h_minus + h_plus)**2.0 +  (k_minus + k_plus)**2.0 ) )/(2.0 * (Pb/Pc)**(2.0/3.0)   )
ec =  np.sqrt ( (h_plus-h_minus)**2  + (k_plus-k_minus)**2   )/2.0

wb = np.arccos ( (h_plus + h_minus)/(2.0*eb*(Pb/Pc)**(2.0/3.0) ) )
wc = np.arccos ( (h_plus-h_minus)/(2.0*ec) )


'''




p_parameters = [0.00014932535033861051,
                  7.919354717427596, 0.08695861035152036, 88.74540570700838,
                  180.0,   214.09963960544101, 227.0106215751976,
                  6.3494930075318071e-05,
                  11.906442780144104, 0.1124375085494681, 88.95595877430457,
                  167.5154616287283,250.7761358353399,   74.670769462202]



#p_parameters = [ Mplanet1,  Pb,  eb,  inc1,  LongNode1, wb,  MeanAnomaly1,
#                 Mplanet2,  Pc,  ec,  inc2,  LongNode2, wc,  MeanAnomaly2]

#All of the parameters are fitted expected LongNode1 =180


stellar_mass = 0.97061886114722451

dt = 0.01




ts, rvdyms , rvs1, rvs2 = np.genfromtxt('/Users/sbarros/Documents/work/mercury/k350/predicted_rvsdym.txt', unpack=True)

rv_times = ts.astype("float64")[1:100000:10]
rvdym = rvdyms.astype("float64")[1:100000:10]


tmidsb = np.genfromtxt('/Users/sbarros/Documents/work/mercury/k350/derived_times_test7_plb.txt')
tmidb = tmidsb.astype("float64")[0:26]

tmidsc = np.genfromtxt('/Users/sbarros/Documents/work/mercury/k350/derived_times_test7_plc.txt')
tmidc = tmidsc.astype("float64")[0:17]

time_ttv = [tmidb, tmidc ]

ttv1,ttv2 , outrvs = fttvfast_v3(p_parameters,stellar_mass, dt, time_ttv, rv_times=rv_times )

#ttv1,ttv2  = fttvfast_v3(p_parameters,stellar_mass, dt, time_ttv)#, rv_times=rv_times )

pl.plot(ttv1)
pl.plot(tmidb)
pl.show()

pl.plot( (ttv1-tmidb)*24*60*60, '.' )
pl.show()

pl.plot(ttv2)
pl.plot(tmidc)
pl.show()

pl.plot( (ttv2-tmidc)*24*60*60, '.' )
pl.show()


pl.plot( (ttv1-tmidb)*24*60*60, '.' )
pl.plot( (ttv2-tmidc)*24*60*60, '.' )
pl.show()




'''
pl.plot(rv_times, outrvs)
pl.plot(rv_times,rvdym, color='red' )
pl.show()

pl.plot(rv_times, outrvs-rvdym)
pl.show()
'''
