


import sys

sys.path.append('/Users/sbarros/Documents/work/python/ttvfast-python')

import ttvfast
import numpy as np




def fttvfast(p_parameters,stellar_mass, dt, time_ttv, rv_times=None ):
    """
    Get the transit times for a set of planet p_parameters
    call fttvfast(p_parameters,stellar_mass, dt, time_ttv, rv_times=None)
    stellar mass is in solar masses
    dt is time step for the integration (days) should be < 1/20 of shorter planet orbit
    time_ttv are times for a duration of which you want the ttvs to be calculated
    rv_times: rv measurement times
    The code will calculate TTVs between [ min (time_ttv,rv_time ) - 0.0001, max (time_ttv,rv_time ) + 0.0001]
    The p_parameters are
    Mplanet Period E I LongNode Argument Mean Anomaly (at t=t0, the reference time)....
    repeated for each planet
    : 2+nplanets*7 in length
    all masses are in units of M_sun, the Period is in units of days, and the angles are in DEGREES. Cartesian coordinates are in AU and AU/day. The coordinate system is as described in the paper text. One can use different units, as long as G is converted accordingly.
    '''

    For now the code works for 2 or 3 planets, 3 planets not tested

    outputs : epoch,ttvs for each planet and rvs for the requested times if asked

    TODO:
    program not happy with != None :

    """



    nplanets = len(p_parameters)/7.0

    if nplanets == 2 :
        planet1_params = p_parameters[0:7]
        planet2_params = p_parameters[7:14]
        planet1 = ttvfast.models.Planet(*planet1_params)
        planet2 = ttvfast.models.Planet(*planet2_params)
        allplanets = [planet1, planet2]
    elif nplanets  == 3 :
        planet1_params = p_parameters[0:7]
        planet2_params = p_parameters[7:14]
        planet3_params = p_parameters[14:21]
        planet1 = ttvfast.models.Planet(*planet1_params)
        planet2 = ttvfast.models.Planet(*planet2_params)
        planet3 = ttvfast.models.Planet(*planet3_params)
        allplanets = [planet1, planet2, planet3]

    if rv_times != None :
        fulltime = np.concatenate( (time_ttv , rv_times) )

        Time = np.min(fulltime) - 0.5
        Total = np.max(fulltime) + 0.5


        results = ttvfast.ttvfast(allplanets, stellar_mass, Time, dt, Total, rv_times=list(rv_times), input_flag=1)

    else :
        Time = np.min(time_ttv) - 0.5
        Total = np.max(time_ttv) + 0.5

        results = ttvfast.ttvfast(allplanets, stellar_mass, Time, dt, Total,  input_flag=1)


    index = np.asarray( results['positions'][0])
    epoch = np.asarray( results['positions'][1])
    outimes = np.asarray( results['positions'][2])
    rsky =np.asarray( results['positions'][3])
    vsky =np.asarray( results['positions'][4])

    p1 = np.where(np.logical_and( index ==0 , outimes > 0 ))
    p2 = np.where(np.logical_and( index ==1 , outimes > 0 ))

    if nplanets == 2 :
        if rv_times != None :
            day1 = 86400.0
            au= 1.495978707e11
            outrvs = np.asarray( results['rv']) *au /(day1)

            # return epoch of p1, ttvs p1, epoch of p2, ttvs of p2, rvs
            return [epoch[p1],outimes[p1],epoch[p2],outimes[p2] , outrvs ]

        else:
            # return epoch of p1, ttvs p1, epoch of p2, ttvs of p2
            return [epoch[p1],outimes[p1],epoch[p2],outimes[p2]  ]

    elif nplanets == 3 :
        p3 = np.where(np.logical_and( index ==2 , outimes > 0 ))

        if rv_times != None :
            day1 = 86400.0
            au= 1.495978707e11
            outrvs = np.asarray( results['rv']) *au /(day1)


            # return  ttvs p1, ttvs of p2, rvs
            return  [epoch[p1],outimes[p1],epoch[p2],outimes[p2] , epoch[p3],outimes[p3] ,outrvs ]

        else:
        # return ttvs p1, ttvs of p2, rvs
            return  [epoch[p1],outimes[p1],epoch[p2],outimes[p2] ,epoch[p3],outimes[p3]  ]




'''
important
the lenght of positions is always 5000 and the number of transits needs to fit here
there will be lots of zeros to cut and if we have more then 5000 transits we are fu!!


'''
