import rebound
import numpy as np
import sys
sys.path.append("/Users/sbarros/Documents/work/python/photodynamic/lisa/")
from lisa.emcee_tools.emcee_tools import get_time_supersampled
from lisa.emcee_tools.emcee_tools import average_supersampled_values


def transitpy(z, rp, u):
    '''
    Function to calculate the flux given the normalised planet to star distance, the radius ratio and quadratic limb darkening
    Uses pytransit package
    '''
    from pytransit import MandelAgol
    '''
    Args:
    z: Array of normalised projected distances
    k: Planet to star radius ratio
    u: Array of limb darkening coefficients.
    c: Array of contamination values as [c1, c2, ... c_npb]
    '''

    lc = MandelAgol._eval_quadratic(z, rp, u[0],u[1],c=0,  update=True)
    return lc

def transitbat(z, rp, u):
    '''
    Function to calculate the flux given the normalised planet to star distance, the radius ratio and quadratic limb darkening
    Uses the batman package
    '''

    from  batman import _quadratic_ld
    '''
    _quadratic_ld._quadratic_ld(self.ds, params.rp, params.u[0], params.u[1], self.nthreads)
    '''

    '''
		if self.supersample_factor > 1:  # IJMC: now do it quicker, with no loops:
			t_offsets = np.linspace(-self.exp_time/2., self.exp_time/2., self.supersample_factor)
			self.t_supersample = (t_offsets + self.t.reshape(self.t.size, 1)).flatten()
		else: self.t_supersample = self.t
    '''

    lc = _quadratic_ld._quadratic_ld(z,  rp, u[0], u[1], 1)
    return lc

def funrebound(p_parameters,stellar_mass, stellar_radius,limb_dark, treference,
              dt=0.01, supersample=1, exptime = 0.02043402778, lc_time=None, rv_times=None ):
    """
    Get the photodynamical model for photometry and/or radial velocity points


    call funrebound(p_parameters,stellar_mass, stellar_radius,limb_dark, treference,
                  dt=0.01, supersample=1, exptime = 0.02043402778, lc_time=None, rv_times=None ):
    stellar mass is in solar masses
    stellar radius is in solar radius
    limb_dark is the quadratic law
    treference is the time at which the parameters are given
    dt is time step for the integration (days) should be < 1/20 of shorter planet orbit
    It allows supersampling the light curve by given a supersample factor > 1 and an exposure time whose default is kepler long cadence
    if lc_times the program outputs the photodynamical model
    if rv_times the program outputs the rv dynamical model
    when both are given the output is [lcmodel, rvmodel]

    The p_parameters are
    Mplanet P E I LongNode Argument Mean Anomaly rp/rs (at t=t0, the reference time)....
    repeated for each planet
    : nplanets*8 in length , any number of planets is allowed. multiplanets transis are ok unless the planets pass in front of each other
    all masses are in units of M_sun, P is in days, and the angles are in radians. rp is divided by rs, lenghts are in AU
    All times are expected to be in days

    outputs : model of photometry normalised or/ and  model of the radial velocity (m/s) for the times requested

    TODO:
    transitpy not working
    """



    #convert stellar radius to au
    import astropy.constants as const
    day1 = 86400.0 # days in seconds
    rsun = const.R_sun.value
    au = const.au.value
    rstar = stellar_radius * rsun / au



    u = limb_dark

    if lc_time is not None :
        # supersample light curve
        if supersample > 1:
            ltimes = get_time_supersampled(lc_time ,supersample, exptime)
        else :
            ltimes = lc_time
        np_lc = len(ltimes)

    if rv_times is not None :
        if lc_time is not None :
            np_rv = len(rv_times)
            ttimes = np.concatenate( (ltimes , rv_times) )

            sorte = np.argsort(ttimes)
            ffsorte = np.argsort(sorte)
            sorte_lc = ffsorte[:np_lc]
            sorte_rv = ffsorte[np_lc:]
            ltimes = ttimes[sorte]
        else:
            ltimes = rv_times



    # calculate the number of planets
    #Mplanet Period E I Omega omega Meananomaly, radius ratio
    nplanets = np.int(len(p_parameters)/8.0)
    npoints = len(ltimes)

    rp = np.zeros(nplanets)


    sim = rebound.Simulation()
    sim.integrator =  'whfast'#'ias15'#
    sim.t = treference
    sim.units = ('d', 'AU', 'Msun')
    #sim.dt = stepdt # Sets the timestep (will change for adaptive integrators such as IAS15).
    sim.dt = dt
    m0 = stellar_mass

    #add a star
    sim.add( m = m0)
    # add planets
    for jj in range(0, nplanets):
        sim.add( m = p_parameters[0 + jj*8] , P = p_parameters[1+jj*8], e = p_parameters[2+jj*8] , inc = p_parameters[3+jj*8],
                Omega = p_parameters[4+jj*8], omega =p_parameters[5+jj*8], M=p_parameters[6+jj*8], primary=sim.particles[0])
        # get radius ratio
        rp[jj] = p_parameters[7 + jj*8]

    #sim.status()

    # moves to centre of momentum
    sim.move_to_com()
    particles = sim.particles

    #addrvs and fluxes

    distance = np.zeros((npoints, nplanets),dtype=float)
    rvs = np.zeros_like(ltimes)


    for i, time in enumerate(ltimes):
        sim.integrate(time, exact_finish_time=1)
        for jj in range(0, nplanets):
            distance[i,jj] = np.sqrt((particles[jj+1].x-particles[0].x)**2 + (particles[jj+1].y-particles[0].y)**2)

        #bug fixed on the 7sep 2018. Rebound gives already the velocity of the star so it is negative relative to the osberved RVs
        rvs[i] = -particles[0].vz*au /(day1)

    # separate rvs and flux

    if lc_time is not None :
        mflux = transitbat(distance[:,0]/rstar, rp[0] , u)
        for jj in range(1, nplanets):
            mflux = mflux + transitbat(distance[:,jj]/rstar, rp[jj] , u) - 1
    else:
         return rvs

    if rv_times is not None :
        sortflux = mflux[sorte_lc]
        sortrvs = rvs[sorte_rv]
        if supersample > 1:
            totalflux = average_supersampled_values( sortflux , supersample)
        else :
            totalflux = sortflux
        return [totalflux, sortrvs]

    else :
        if supersample > 1:
            totalflux = average_supersampled_values( mflux , supersample)
        else :
            totalflux = mflux
        return totalflux
