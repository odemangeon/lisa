
import sys

sys.path.append('/Users/sbarros/Documents/work/python/ttvfast-python')

import ttvfast
import numpy as np
import matplotlib.pyplot as pl
import astropy.constants as const

au = const.au.value

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
'''



def planets():
    planet1_params = [0.00014932535033861051,
                      7.919354717427596, 0.08695861035152036, 88.74540570700838,
                      180.0,   214.09963960544101, 227.0106215751976 ]

    planet2_params = [6.3494930075318071e-05,
                      11.906442780144104, 0.1124375085494681, 88.95595877430457,
                      167.5154616287283,250.7761358353399,   74.670769462202]

    planet1 = ttvfast.models.Planet(*planet1_params)
    planet2 = ttvfast.models.Planet(*planet2_params)
    return [planet1, planet2]


if __name__ == "__main__":

    ts, rvdyms , rvs1, rvs2 = np.genfromtxt('/Users/sbarros/Documents/work/mercury/k350/predicted_rvsdym.txt', unpack=True)

    rv_times = ts.astype("float64")[1:100000:10]
    rvdym = rvdyms.astype("float64")[1:100000:10]
    rvs1 =  rvs1.astype("float64")[1:100000:10]
    rvs2 =  rvs2.astype("float64")[1:100000:10]




    stellar_mass = 0.97061886114722451


    Time = 6813.0
    dt = 0.01
    Total = 7013.0
    n_plan = 2



    results = ttvfast.ttvfast(planets(), stellar_mass, Time, dt, Total, rv_times=list(rv_times), input_flag=1)
    #results = ttvfast.ttvfast(planets(), stellar_mass, Time, dt, Total,  input_flag=1)

    #results['positions'][0]

    index = np.asarray( results['positions'][0])
    epoch = np.asarray( results['positions'][1])
    outimes = np.asarray( results['positions'][2])
    rsky =np.asarray( results['positions'][3])
    vsky =np.asarray( results['positions'][4])



    p1 = np.where(np.logical_and( index ==0 , outimes > 0 ))

    p2 = np.where(np.logical_and( index ==1 , outimes > 0 ))


    pl.plot(outimes[p1], vsky[p1], '.')
    pl.xlim(Time,Total)
    pl.show()


    ttv1 = outimes[p1]
    ttv2 = outimes[p2]

    nt1= len(ttv1)
    nt2= len(ttv2)

    tmidsb = np.genfromtxt('/Users/sbarros/Documents/work/mercury/k350/derived_times_test7_plb.txt')
    tmidb = tmidsb.astype("float64")[0:nt1]

    tmidsc = np.genfromtxt('/Users/sbarros/Documents/work/mercury/k350/derived_times_test7_plc.txt')
    tmidc = tmidsc.astype("float64")[0:nt2]


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
    important
    the lenght of positions is always 5000 and the number of transits needs to fit here
    there will be lots of zeros to cut and if we have more then 5000 transits we are fu!!


    '''

    '''
    comparison of the RVs is going very well
    to get the RVs the input times need to be a list of times
    and the rvs need to be included in the span of the simulations. it cannot be even the same value as the staring point
    and I assume the last point of the simulations.

    day1 = 86400.0
    au= 1.495978707e11
    outrvs = np.asarray( results['rv']) *au /(day1)

    pl.plot(rv_times, outrvs)
    pl.plot(rv_times,rvdym, color='red' )
    pl.show()

    pl.plot(rv_times, outrvs-rvdym)
    pl.show()
    '''
