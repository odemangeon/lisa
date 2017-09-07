import rebound
import numpy as np
import matplotlib.pyplot as pl
import astropy.constants as const




def getttv_reb(p_parameters,stellar_mass,stellar_radius, N, planet, treference,first, precision=1e-7 ):
    """
    Calculates transit times and durations from a simulation given the orbital paramters of the system for one of the planet
    It calculated the ingress and egreess times when distance between the stellar centres is rp+rs and then the time is the midle of this and the duration is the diference
    Integrator is the ias15' to better deal with adaptive step

    call getttv_reb(p_parameters,stellar_mass,stellar_radius, N, planet, treference, precision=1e-7 )

    planet =1 for the b
    planet =2 for the c
    planet =0 DOESNOT WORK

    stellar mass is in solar masses
    stellar radius is in solar radius
    treference is the time at which the parameters are given
    precision in not needed and precision of 1 sec is 1.1574074074074073e-05


    The p_parameters are
    Mplanet P E I LongNode Argument Mean Anomaly rp/rs (at t=t0, the reference time)....
    repeated for each planet
    : nplanets*8 in length , any number of planets is allowed. multiplanets transis are ok unless the planets pass in front of each other
    all masses are in units of M_sun, P is in days, and the angles are in radians. rp is divided by rs, leghts are in AU
    All times are expected to be in days

    outputs : [transitimes, duration] in days

    important
    Old version of the code stars to search for TTVs from the reference.
    It can miss the first transit if stars in transit but it will work for starting in transit.
    This version asks for extra input which is the time of the first transit making sure that the first transit is always that one.
    If this is wrong it might get into an infinite loop

    """

    rsun = const.R_sun.value
    au = const.au.value
    rstar = stellar_radius * rsun / au
    nplanets = np.int(len(p_parameters)/8.0)
    m0 = stellar_mass
    rp = np.zeros(nplanets)

    sim = rebound.Simulation()
    sim.t = treference
    sim.units = ('d', 'AU', 'Msun')

    #add a star
    sim.add( m = m0)
    # add planets
    for jj in range(0, nplanets):
        sim.add( m = p_parameters[0 + jj*8] , P = p_parameters[1+jj*8], e = p_parameters[2+jj*8] , inc = p_parameters[3+jj*8],
                Omega = p_parameters[4+jj*8], omega =p_parameters[5+jj*8], M=p_parameters[6+jj*8], primary=sim.particles[0])
        # get radius ratio
        rp[jj] = p_parameters[7 + jj*8]

    #sim.integrate(first)
    sim.move_to_com()

    dcentres = rstar*(1+rp[planet-1])
    gresstimes = np.zeros(N*2)
    particles = sim.particles
    i = 0

    while  i < N*2:
        d_old = ( np.sqrt((particles[planet].x-particles[0].x)**2 + (particles[planet].y-particles[0].y)**2)  ) /dcentres
        t_old = sim.t
        sim.integrate(sim.t+0.05) # check for transits every 0.5 time units. Note that 0.5 is shorter than one orbit
        t_new = sim.t
        d_new = ( np.sqrt((particles[planet].x-particles[0].x)**2 + (particles[planet].y-particles[0].y)**2)  ) /dcentres
        #print(d_old, d_new)
        if (d_old - 1)*(d_new -1) <0. and (particles[planet].z-particles[0].z) > 0.:  # sign changed (y_old*y<0), planet in front of star (x>0)
            #if i == 0: start_intransit = (d_old -1) < 0
            while t_new-t_old > precision:   # bisect until prec of 1e-5 reached
                d_new = ( np.sqrt((particles[planet].x-particles[0].x)**2 + (particles[planet].y-particles[0].y)**2)  ) /dcentres
                if (d_old-1)*(d_new-1)<0.:
                    t_new = sim.t
                else:
                    t_old = sim.t
                sim.integrate( (t_new+t_old)/2.)
            gresstimes[i] = sim.t
            i += 1
            sim.integrate(sim.t+0.05)       # integrate 0.05 to be past the transit
            if i==1:
                #print(gresstimes[0])
                if (gresstimes[0]- first) > 0.5*p_parameters[1+(planet-1)*8] or (d_old -1) < 0:
                    print('big',sim.t)
                    sim.t = gresstimes[0] - 0.5*p_parameters[1+(planet-1)*8]
                    sim.t = first - 0.5*p_parameters[1+(planet-1)*8]
                    print('big',sim.t,p_parameters[1+(planet-1)*8])
                    sim.integrate(sim.t)
                    i = 0
                elif (gresstimes[0]- first) <  -0.5*p_parameters[1+(planet-1)*8]:
                    print('small',sim.t)
                    sim.t = gresstimes[0] + 0.5*p_parameters[1+(planet-1)*8]
                    print('small',sim.t,p_parameters[1+(planet-1)*8])
                    sim.integrate(sim.t)
                    i = 0


    '''
    if start_intransit:
        ingresstimes = gresstimes[1:2*N-1:2]
        egresstimes  = gresstimes[2:2*N-1:2]
    else:
        ingresstimes = gresstimes[0::2]
        egresstimes  = gresstimes[1::2]
    '''

    ingresstimes = gresstimes[0::2]
    egresstimes  = gresstimes[1::2]
    duration = (egresstimes- ingresstimes )
    transitimes = ingresstimes + duration*0.5

    return [transitimes, duration]
