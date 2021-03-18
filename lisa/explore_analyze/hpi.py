from numpy import argsort, ceil


def highest_probability_chains(param_chains, probability_chain, percentage, kwargs_argsort=None):
    """Return subset of input chains containing only the highest probability iterations.

    Arguments
    ---------
    param_chains        : array
        flat chains of the parameters. Dimensions: Nb_iteration, Nb_parameters
    probability_chain  : array
        flat chains of the probability. Dimensions: Nb_iteration
    percentage          : float
        Percentage of chains that you want to return in percent (between 0 and 100)
    kwargs_argsort      : dict
        keyword arguments passed to the numpy.argsort function

    Returns
    -------
    res_param_chains        : array
        Flat parameters chains containing only the iteration of highest probability.
        Dimensions: Nb_iteration * percentage / 100, Nb_parameters
    res_probability_chains  : array
        Flat probability chain containing only the iteration of highest probability.
        Dimensions: Nb_iteration * percentage / 100
    """
    kwargs_argsort = {} if kwargs_argsort is None else kwargs_argsort
    # Get the indices that would sort the probability chains
    idx_sort = argsort(probability_chain, **kwargs_argsort)
    # Select only the top percentage
    top_perc = int(ceil(len(probability_chain) * percentage / 100))
    return param_chains[idx_sort[-top_perc:], :], probability_chain[idx_sort[-top_perc:]]
