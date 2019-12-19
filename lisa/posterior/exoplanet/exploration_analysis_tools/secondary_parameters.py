"""Module to compute the secondary parameters chains.
"""
from collections import Counter
from numbers import Number
from numpy import ndarray, stack, arcsin, sqrt, rad2deg, mean, array
from numpy import random

from ..model import convert as cv
from ....tools.human_machine_interface.QCM import QCM_utilisateur
from ....tools.human_machine_interface.standard_questions import Ask4Number, Ask4PositiveNumber
from ....tools.chain_interpreter import ChainsInterpret
from logging import getLogger


logger = getLogger()


def get_secondary_chains(model, chaininterpret, star_kwargs=None, planet_kwargs=None, units=None):
    """Return ChainInterpret isntance with the computed chain of the secondary parameters.

    :param dict units: Dictionary specifying the unit of some of the parameter. Possible parameters:
        "K": value can be "kms" or "ms".
    """
    # Create a dictionary with the main parameter values either chain (if free) or one value
    dico_par = {}
    for param in model.get_list_params(main=True, recursive=True):
        if param.free:
            dico_par[param.get_name(include_prefix=True, recursive=True)] = chaininterpret[..., param.get_name(include_prefix=True, recursive=True)]
        else:
            dico_par[param.get_name(include_prefix=True, recursive=True)] = param.value

    # Compute the chains for secondary parameters.
    # Initialise the results object
    l_parname_sec_chain = []
    l_parname_sec_fixed = []

    star = list(model.stars.values())[0]

    # Decide if you use rho or R as main stellar physical parameter
    if star.rho.main:
        l_param_star = [star.M, star.rho, star.Teff]
        Rstar_infered = True
    else:
        if ("rho" not in star_kwargs) and ("R" not in star_kwargs):
            intitule_question = ("Do you want to provide the stellar density or radius ? ['rho', "
                                 "'R']\n")
            reply = QCM_utilisateur(intitule_question, l_reponses_possibles=['rho', 'R'])
        elif ("rho" in star_kwargs) and ("R" in star_kwargs):
            raise ValueError("You should not provide both rho and R of the star.")
        else:
            reply = None
        if reply == "rho":
            Rstar_infered = True
            l_param_star = [star.M, star.rho, star.Teff]
        elif reply == "R":
            Rstar_infered = False
            l_param_star = [star.M, star.R, star.Teff]
        else:
            if "rho" in star_kwargs:
                Rstar_infered = True
                l_param_star = [star.M, star.rho, star.Teff]
            else:
                Rstar_infered = False
                l_param_star = [star.M, star.R, star.Teff]

    # Simulate stellar Mass, Teff, radius or rho chains if needed
    for param in l_param_star:
        if param.main is False:
            ask_param_value = True
            ask_param_error = True
            if param.get_name() in star_kwargs:
                if "value" in star_kwargs[param.get_name()]:
                    param_value = star_kwargs[param.get_name()]["value"]
                    ask_param_value = False
                if "error" in star_kwargs[param.get_name()]:
                    param_error = star_kwargs[param.get_name()]["error"]
                    ask_param_error = False
            if ask_param_value:
                # Ask to provide a stellar mass value
                intitule_question = ("Enter a {} value. If you just press enter 1 "
                                     "is assumed.\n".format(param.get_name(include_prefix=True, recursive=True)))
                param_value, answered = Ask4Number(intitule_question, default_value=1.)
            else:
                dico_par[param.get_name(include_prefix=True, recursive=True)] = param.value
                answered = False
            # If replied ask to provide and mass error value, otherwise assume no error
            if ask_param_error and not(ask_param_value and not(answered)):
                intitule_question = ("Enter a {} error (1 sigma). If you just press enter "
                                     "no uncertainty is assumed.\n".format(param.get_name(include_prefix=True, recursive=True)))
                param_error, _ = Ask4PositiveNumber(intitule_question, default_value=0.)
            else:
                if ask_param_value and not(answered):
                    param_error = 0.

            # if provided simulated a stellar mass chains else only give a fixed value.
            if param_error == 0.:
                dico_par[param.get_name(include_prefix=True, recursive=True)] = param_value
            else:
                dico_par[param.get_name(include_prefix=True, recursive=True)] = random.normal(loc=param_value,
                                                                                              scale=param_error,
                                                                                              size=chaininterpret.shape[:-1])

    # Compute R star from rho if needed
    if Rstar_infered:
        dico_par[star.R.get_name(include_prefix=True, recursive=True)] = cv.getRstar(dico_par[star.rho.get_name(include_prefix=True, recursive=True)],
                                                                                     dico_par[star.M.get_name(include_prefix=True, recursive=True)])
        l_parname_sec_chain.append(star.R.get_name(include_prefix=True, recursive=True))

    # Define units of parameter for which the unit can vary depending on the dataset.
    if units is None:
        units = {}
    K_unit = units.get("K", "kms")
    if K_unit == "kms":
        Kfact = 1000
    elif K_unit == "ms":
        Kfact = 1
    else:
        raise ValueError("Unit of K can be 'kms' or 'ms'.")

    if Counter(["LC", "RV"]) == Counter(model.dataset_db.inst_categories):
        # Iterate over planet related secondary
        for planet in model.planets.values():
            # Prepare the list of tuples secondary parameter name, function, parameters
            l_tup_planet = []
            # Transit depth
            l_tup_planet.append((planet.Trdepth.get_name(include_prefix=True, recursive=True), cv.get_transit_depth, [],
                                 [planet.Rrat.get_name(include_prefix=True, recursive=True)]))
            # Inclination
            l_tup_planet.append((planet.inc.get_name(include_prefix=True, recursive=True), cv.getinc, [],
                                 [planet.cosinc.get_name(include_prefix=True, recursive=True)]))
            # eccentricity
            l_tup_planet.append((planet.ecc.get_name(include_prefix=True, recursive=True), cv.getecc, [],
                                 [planet.ecosw.get_name(include_prefix=True, recursive=True), planet.esinw.get_name(include_prefix=True, recursive=True)]))
            # omega : argument of periastron in degrees
            l_tup_planet.append((planet.omega.get_name(include_prefix=True, recursive=True), cv.getomega_deg, [],
                                 [planet.ecosw.get_name(include_prefix=True, recursive=True), planet.esinw.get_name(include_prefix=True, recursive=True)]))

            if model.parametrisation == "EXOFAST":
                # b: impact parameter
                l_tup_planet.append((planet.b.get_name(include_prefix=True, recursive=True), cv.getb, [],
                                     [planet.inc.get_name(include_prefix=True, recursive=True), planet.aR.get_name(include_prefix=True, recursive=True),
                                      planet.ecc.get_name(include_prefix=True, recursive=True), planet.omega.get_name(include_prefix=True, recursive=True)]))
            elif model.parametrisation == "Multis":
                l_tup_planet.append((planet.aR.get_name(include_prefix=True, recursive=True), cv.getaoverr, [],
                                     [planet.P.get_name(include_prefix=True, recursive=True), star.rho.get_name(include_prefix=True, recursive=True)]))
                l_tup_planet.append((planet.b.get_name(include_prefix=True, recursive=True), cv.getb, [],
                                     [planet.inc.get_name(include_prefix=True, recursive=True), planet.aR.get_name(include_prefix=True, recursive=True),
                                      planet.ecc.get_name(include_prefix=True, recursive=True), planet.omega.get_name(include_prefix=True, recursive=True)]))
            # Rp: planetary radius
            l_tup_planet.append((planet.R.get_name(include_prefix=True, recursive=True), cv.getRp, [],
                                 [planet.Rrat.get_name(include_prefix=True, recursive=True), star.R.get_name(include_prefix=True, recursive=True)]))
            # D14: full transit duration
            l_tup_planet.append((planet.D14.get_name(include_prefix=True, recursive=True), cv.getD14, [],
                                 [planet.P.get_name(include_prefix=True, recursive=True), planet.inc.get_name(include_prefix=True, recursive=True), planet.aR.get_name(include_prefix=True, recursive=True),
                                  planet.ecc.get_name(include_prefix=True, recursive=True), planet.omega.get_name(include_prefix=True, recursive=True),
                                  planet.Rrat.get_name(include_prefix=True, recursive=True)]))
            # D12: ingress/egress duration
            l_tup_planet.append((planet.D23.get_name(include_prefix=True, recursive=True), cv.getD23, [],
                                 [planet.P.get_name(include_prefix=True, recursive=True), planet.inc.get_name(include_prefix=True, recursive=True), planet.aR.get_name(include_prefix=True, recursive=True),
                                  planet.ecc.get_name(include_prefix=True, recursive=True), planet.omega.get_name(include_prefix=True, recursive=True),
                                  planet.Rrat.get_name(include_prefix=True, recursive=True)]))
            # Mp: Planetary mass
            l_tup_planet.append((planet.M.get_name(include_prefix=True, recursive=True), cv.getMp, [Kfact, ],
                                 [planet.P.get_name(include_prefix=True, recursive=True), planet.K.get_name(include_prefix=True, recursive=True), star.M.get_name(include_prefix=True, recursive=True),
                                  planet.ecc.get_name(include_prefix=True, recursive=True), planet.inc.get_name(include_prefix=True, recursive=True)]))
            # a: semi major axis
            l_tup_planet.append((planet.a.get_name(include_prefix=True, recursive=True), cv.geta, [],
                                 [planet.P.get_name(include_prefix=True, recursive=True), star.M.get_name(include_prefix=True, recursive=True), planet.M.get_name(include_prefix=True, recursive=True)]))
            # rhostar: Density of the star
            l_tup_planet.append((planet.rhostar.get_name(include_prefix=True, recursive=True), cv.getrhostar, [],
                                 [planet.P.get_name(include_prefix=True, recursive=True), planet.aR.get_name(include_prefix=True, recursive=True)]))
            # loggstar: logg of the star
            l_tup_planet.append((planet.loggstar.get_name(include_prefix=True, recursive=True), cv.getloggstar, [],
                                 [planet.P.get_name(include_prefix=True, recursive=True), planet.aR.get_name(include_prefix=True, recursive=True), star.R.get_name(include_prefix=True, recursive=True)]))
            # circtime: circularisation timescale of the planet
            l_tup_planet.append((planet.circtime.get_name(include_prefix=True, recursive=True), cv.getcirctime, [],
                                 [planet.P.get_name(include_prefix=True, recursive=True), star.M.get_name(include_prefix=True, recursive=True), star.R.get_name(include_prefix=True, recursive=True),
                                  planet.M.get_name(include_prefix=True, recursive=True), planet.Rrat.get_name(include_prefix=True, recursive=True)]))
            # rhoplanet: Density of the planet
            l_tup_planet.append((planet.rho.get_name(include_prefix=True, recursive=True), cv.getrhopl, [],
                                 [planet.M.get_name(include_prefix=True, recursive=True), planet.R.get_name(include_prefix=True, recursive=True)]))
            # Teq: Equilibrium temperature
            l_tup_planet.append((planet.Teq.get_name(include_prefix=True, recursive=True), cv.getTeqpl, [],
                                 [star.Teff.get_name(include_prefix=True, recursive=True), planet.aR.get_name(include_prefix=True, recursive=True), planet.ecc.get_name(include_prefix=True, recursive=True)]))

            # L: Stellar luminosity
            l_tup_planet.append((star.L.get_name(include_prefix=True, recursive=True), cv.getLs, [],
                                 [star.R.get_name(include_prefix=True, recursive=True), star.Teff.get_name(include_prefix=True, recursive=True)]))

            # Fi: Planetary insolation flux
            l_tup_planet.append((planet.Fi.get_name(include_prefix=True, recursive=True), cv.getFi, [],
                                 [star.L.get_name(include_prefix=True, recursive=True), planet.a.get_name(include_prefix=True, recursive=True)]))

            # H: Scale Height
            l_tup_planet.append((planet.H.get_name(include_prefix=True, recursive=True), cv.getscaleheigh, [],
                                 [planet.M.get_name(include_prefix=True, recursive=True), planet.R.get_name(include_prefix=True, recursive=True), planet.Teq.get_name(include_prefix=True, recursive=True)]))

            # Compute the secondary parameter
            for sec_paraname, func, args, param_list in l_tup_planet:
                logger.debug("Computing secondary parameter: {}".format(sec_paraname))
                values = func(*[dico_par[param] for param in param_list], *args)
                if isinstance(values, Number) or isinstance(values, ndarray):
                    dico_par[sec_paraname] = values
                    if isinstance(values, Number):
                        l_parname_sec_fixed.append(sec_paraname)
                    else:
                        if values.size == 1:
                            l_parname_sec_fixed.append(sec_paraname)
                        elif values.size > 1:
                            l_parname_sec_chain.append(sec_paraname)
                        else:
                            raise ValueError("Secondary parameter computation {} didn't return "
                                             "any result: {}".format(sec_paraname, values))
                else:
                    raise ValueError("Secondary parameter computation {} return an unexpected "
                                     "object type: {}".format(sec_paraname, type(values)))
        chainIsec = ChainsInterpret(stack([dico_par[param] for param in l_parname_sec_chain],
                                          axis=-1),
                                    l_parname_sec_chain)
        return chainIsec, l_parname_sec_chain

    elif Counter(["RV", ]) == Counter(model.dataset_db.inst_categories):
        # Default value for planet_kwargs and simulate if needed
        dico_def_value = {"inc": rad2deg(arcsin(sqrt(3 / 4)))}
        if planet_kwargs is None:
            planet_kwargs = {}
        for planet in model.planets.values():
            pl_name = planet.get_name()
            if planet.get_name() not in planet_kwargs:
                planet_kwargs[pl_name] = {}
            # Simulate planet inclination if needed.
            for param in [planet.inc]:
                if param.main is False:
                    ask_param_value = True
                    ask_param_error = True
                    if param.get_name() in planet_kwargs[pl_name]:
                        if "value" in planet_kwargs[pl_name][param.get_name()]:
                            param_value = planet_kwargs[pl_name][param.get_name()]["value"]
                            ask_param_value = False
                        if "error" in planet_kwargs[pl_name][param.get_name()]:
                            param_error = planet_kwargs[pl_name][param.get_name()]["error"]
                            ask_param_error = False
                    if ask_param_value:
                        # Ask to provide a stellar mass value
                        intitule_question = ("Enter a {} value. If you just press enter {}"
                                             " is assumed.\n".format(param.get_name(include_prefix=True, recursive=True),
                                                                     dico_def_value[param.get_name()]))
                        param_value, answered = Ask4Number(intitule_question,
                                                           default_value=dico_def_value[param.get_name()])
                    else:
                        answered = False
                    # If replied ask to provide and mass error value, otherwise assume no error
                    if ask_param_error and not(ask_param_value and not(answered)):
                        intitule_question = ("Enter a {} error (1 sigma). If you just press enter "
                                             "no uncertainty is assumed.\n".format(param.get_name(include_prefix=True, recursive=True)))
                        param_error, _ = Ask4PositiveNumber(intitule_question, default_value=0.)
                    else:
                        if ask_param_value and not(answered):
                            param_error = 0.
                    # if provided simulated a stellar mass chains else only give a fixed value.
                    if param_error == 0.:
                        dico_par[param.get_name(include_prefix=True, recursive=True)] = param_value
                    else:
                        dico_par[param.get_name(include_prefix=True, recursive=True)] = random.normal(loc=param_value,
                                                                                                      scale=param_error,
                                                                                                      size=chaininterpret.shape[:-1])

        # Iterate over planet related secondary
        for planet in model.planets.values():
            # Prepare the list of tuples secondary parameter name, function, parameters
            l_tup_planet = []
            # Time of periastron passage
            l_tup_planet.append((planet.tp.get_name(include_prefix=True, recursive=True), cv.gettp, [],
                                 [planet.P.get_name(include_prefix=True, recursive=True), planet.tic.get_name(include_prefix=True, recursive=True),
                                  planet.ecosw.get_name(include_prefix=True, recursive=True), planet.esinw.get_name(include_prefix=True, recursive=True)]))
            # eccentricity
            l_tup_planet.append((planet.ecc.get_name(include_prefix=True, recursive=True), cv.getecc, [],
                                 [planet.ecosw.get_name(include_prefix=True, recursive=True), planet.esinw.get_name(include_prefix=True, recursive=True)]))
            # omega : argument of periastron in degrees
            l_tup_planet.append((planet.omega.get_name(include_prefix=True, recursive=True), cv.getomega_deg, [],
                                 [planet.ecosw.get_name(include_prefix=True, recursive=True), planet.esinw.get_name(include_prefix=True, recursive=True)]))
            # Mpsini: Planetary mass sinus inclination
            l_tup_planet.append((planet.Msini.get_name(include_prefix=True, recursive=True), cv.getMpsininc, [Kfact, ],
                                 [planet.P.get_name(include_prefix=True, recursive=True), planet.K.get_name(include_prefix=True, recursive=True), star.M.get_name(include_prefix=True, recursive=True),
                                  planet.ecc.get_name(include_prefix=True, recursive=True)]))
            # Mp: Planetary mass
            if planet.inc.get_name(include_prefix=True, recursive=True) in dico_par:
                l_tup_planet.append((planet.M.get_name(include_prefix=True, recursive=True), cv.getMp, [Kfact, ],
                                     [planet.P.get_name(include_prefix=True, recursive=True), planet.K.get_name(include_prefix=True, recursive=True), star.M.get_name(include_prefix=True, recursive=True),
                                      planet.ecc.get_name(include_prefix=True, recursive=True), planet.inc.get_name(include_prefix=True, recursive=True)]))
            # a: semi major axis
            if planet.inc.get_name(include_prefix=True, recursive=True) in dico_par:
                l_tup_planet.append((planet.a.get_name(include_prefix=True, recursive=True), cv.geta, [],
                                     [planet.P.get_name(include_prefix=True, recursive=True), star.M.get_name(include_prefix=True, recursive=True),
                                      planet.M.get_name(include_prefix=True, recursive=True)]))
            else:
                l_tup_planet.append((planet.a.get_name(include_prefix=True, recursive=True), cv.geta, [],
                                     [planet.P.get_name(include_prefix=True, recursive=True), star.M.get_name(include_prefix=True, recursive=True),
                                      planet.Msini.get_name(include_prefix=True, recursive=True)]))
            # aR: semi major axis in stellar radius
            l_tup_planet.append((planet.aR.get_name(include_prefix=True, recursive=True), cv.getaoverr_fromRstar, [],
                                 [planet.a.get_name(include_prefix=True, recursive=True), star.R.get_name(include_prefix=True, recursive=True)]))
            # Teq: Equilibrium temperature
            l_tup_planet.append((planet.Teq.get_name(include_prefix=True, recursive=True), cv.getTeqpl, [],
                                 [star.Teff.get_name(include_prefix=True, recursive=True), planet.aR.get_name(include_prefix=True, recursive=True), planet.ecc.get_name(include_prefix=True, recursive=True)]))
            # L: Stellar luminosity
            l_tup_planet.append((star.L.get_name(include_prefix=True, recursive=True), cv.getLs, [],
                                 [star.R.get_name(include_prefix=True, recursive=True), star.Teff.get_name(include_prefix=True, recursive=True)]))
            # Fi: Planetary insolation flux
            l_tup_planet.append((planet.Fi.get_name(include_prefix=True, recursive=True), cv.getFi, [],
                                 [star.L.get_name(include_prefix=True, recursive=True), planet.a.get_name(include_prefix=True, recursive=True)]))
            # Compute the secondary parameter
            for sec_paraname, func, args, param_list in l_tup_planet:
                logger.debug("Computing secondary parameter: {}".format(sec_paraname))
                values = func(*[dico_par[param] for param in param_list], *args)
                if isinstance(values, Number) or isinstance(values, ndarray):
                    dico_par[sec_paraname] = values
                    if isinstance(values, Number):
                        l_parname_sec_fixed.append(sec_paraname)
                    else:
                        if values.size == 1:
                            l_parname_sec_fixed.append(sec_paraname)
                        elif values.size > 1:
                            l_parname_sec_chain.append(sec_paraname)
                        else:
                            raise ValueError("Secondary parameter computation {} didn't return "
                                             "any result: {}".format(sec_paraname, values))
                else:
                    raise ValueError("Secondary parameter computation {} return an unexpected "
                                     "object type: {}".format(sec_paraname, type(values)))
        if Rstar_infered:
            l_parname_sec_chain.append(star.R.get_name(include_prefix=True, recursive=True))
        chainIsec = ChainsInterpret(stack([dico_par[param] for param in l_parname_sec_chain],
                                          axis=-1),
                                    l_parname_sec_chain)
        return chainIsec, l_parname_sec_chain
    else:
        raise ValueError("For now this function only handles LC and RV parametrisation.")
