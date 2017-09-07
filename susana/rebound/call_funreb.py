import rebound
import numpy as np

import matplotlib.pyplot as pl


import funrebound




if __name__ == "__main__":
    """
    Example how to call the funrebound that produces the model of the light curve and RVs
    """
    #ts, xs , ys, = np.genfromtxt('/Users/sbarros/Documents/work/transit_routines/K350/k350_v1/lc_jose/k350p1_tr01.txt', unpack=True)
    ts, xs , ys, = np.genfromtxt('/Users/sbarros/Documents/work/transit_routines/K350/k350_v3/jose_transits/k2.txt', unpack=True)
    ttt = ts.astype("float64")-2400000.0
    flux = xs.astype("float64")
    fluxerr =  ys.astype("float64")


    ts, rvdyms , rvs1, rvs2 = np.genfromtxt('/Users/sbarros/Documents/work/mercury/k350/predicted_rvsdym.txt', unpack=True)
    rv_times = ts.astype("float64")[1:100000:10]+50000.0 + 0.0001
    rvdym = rvdyms.astype("float64")[1:100000:10]



    npoints = len(ttt)

    stellar_mass = 0.97061886114722451
    stellar_radius =  0.926
    limb_dark = [0.460, 0.210]
    treference = 56813.0
    supersample = 20
    dt = 0.01
    exptime = 0.02043402778
    a1=0.0769897231391472
    period1 = np.sqrt (a1**3/(stellar_mass))*365.2422
    print(period1)
    a2= 0.1010372336036388
    period2 = np.sqrt (a2**3/(stellar_mass))*365.2422
    print(period2)

    # convertion of periods to a works


    supersample = 1

    # it is not working with period maybe because it is not the exacly right one but looks very bad
    #7.92008,11.9068

    #Mplanet P E I Omega omega Meananomaly, radius ratio
    p_parameters = [ 0.00014932535033861051 , period1 , 0.0869586103515203, np.radians(88.74540570700838), np.radians(180.0), np.radians(214.09963960544101), np.radians(227.0106215751976), 0.07451,
                     6.3494930075318071e-05, period2 , 0.1124375085494681 , np.radians(88.95595877430457), np.radians(167.5154616287283)  ,  np.radians(250.7761358353399) , np.radians(74.670769462202),0.04515 ]
    #t1=ttt
    #ttt= np.concatenate( (ttt , rv_times) )

    #light curve and RVs
    [model,rvmodel] = funrebound.funrebound(p_parameters,stellar_mass, stellar_radius,limb_dark, treference, dt, supersample, exptime,  lc_time=ttt, rv_times=rv_times)

    # light curve only
    #model = funrebound.funrebound(p_parameters,stellar_mass, stellar_radius,limb_dark, treference, dt, supersample, exptime, lc_time=ttt)

    #RV only
    #rvmodel = funrebound.funrebound(p_parameters,stellar_mass, stellar_radius,limb_dark, treference,dt, supersample, exptime, rv_times=rv_times)



    pl.plot(ttt,flux, '.')
    pl.plot(ttt,model, '.', color='r')
    pl.title("flux")
    pl.show()


    pl.plot(rv_times,rvdym, '.')
    pl.plot(rv_times,-rvmodel, '.', color='r')
    pl.title("rv")
    pl.show()
