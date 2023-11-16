"""
Interface class to handle prior in the Parameter class
"""
from loguru import logger

from .core_prior import Manager_Prior

## Prior manager
manager = Manager_Prior()
manager.load_setup()


## Joint prior category String
# joint_prior_cat = "joint"


class Parameter_Prior(object):
    """docstring for Parameter_Prior. Interface for the Parameter class to handle priors"""

    ## Prior function: function (TODO: Doesn't seems to be used, suppress ?)
    # prior_func = None

    ## Arguments of the prior function: dictionnary, for example for a gaussian {"mean": 0, "std":0}
    # (TODO: Doesn't seems to be used, suppress ?)
    # prior_args = None

    ## Position of this parameter value in the list of parameter of the joint prior fucntion: int
    # (TODO: Doesn't seems to be used, suppress ?)
    # joint_prior_pos = None

    def __init__(self, paramfile_info, prior_category=None, prior_args=None, joint_prior_ref=None,
                 available_joint_priors={}):
        """Initialise the information related to the Prior for the Parameter instance.

        This should be called from the Parameter.__init__ method.
        This class is not meant to be instanciated directly (except for test purposes).

        :param dict paramfile_info: Dictionary containing the name of information that the parameter
            file provides for each parameter
        :param string prior_category: (default: None), Gives the category of prior probability to
            use for this parameter, eg: gaussian, uniform, ...
            If you want the prior for this parameter to be a joint prior with another parameter
            the category should be "joint".
        :param dict prior_args: (default: None), Dictionnary which gives the value of the parameter
            of the prior probability function that you want to use. The number of elements depends
            on the prior_category.
        :param string joint_prior_ref: (default: None), True if the prior probability associated to
            the value of parameter is defined by a joint prior probability function that depends on
            at least another parameter. False if this parameter is considered as independant of the
            other free parameter a priori.
        :param dict available_joint_priors: Dictionnary which contain all the joint priors available
        """
        # Initialise the prior_info dict
        self.__prior_info = {"joint_prior_ref": None, "category": None, "args": {}}
        if prior_category is None:  # Give the default.
            self.set_prior(prior_category="uniform", vmin=0., vmax=1.)
        else:
            self.set_prior(prior_category=prior_category, joint_prior_ref=joint_prior_ref,
                           available_joint_priors=available_joint_priors, **prior_args)
        # Update paramfile_info with the name of the information related to the Prior
        paramfile_info["prior"] = ["category", "args", "joint_prior_ref"]

    @property
    def prior_info(self):
        """Returns the prior info dict."""
        if self.duplicate is None:
            return self.__prior_info
        else:
            return self.duplicate.prior_info

    @property
    def prior_category(self):
        """Type of prior associated to the parameter (str)."""
        if self.duplicate is None:
            return self.prior_info["category"]
        else:
            return self.duplicate.prior_category

    @property
    def prior_args(self):
        """Arguments of the prior."""
        if self.duplicate is None:
            return self.prior_info["args"]
        else:
            return self.duplicate.prior_args

    @property
    def joint(self):
        """Return True if the prior of the parameter is described by a joint prior."""
        if self.duplicate is None:
            return self.prior_info["joint_prior_ref"] is not None
        else:
            return self.duplicate.joint

    @property
    def joint_prior_ref(self):
        """Reference to the joint prior used for this parameter.

        If the prior is not joint this value is irrelevant.
        """
        if self.duplicate is None:
            return self.prior_info["joint_prior_ref"]
        else:
            return self.duplicate.joint_prior_ref

    def set_prior(self, prior_category=None, joint_prior_ref=None, available_joint_priors={}, **kwargs):
        """Set the prior parameters: category and args, joint prior name if needed.

        :param string prior_category: (default: None), Gives the category of prior probability to
            use for this parameter, eg: gaussian, uniform, ...
            If you want the prior for this parameter to be a joint prior with another parameter
            the category should be "joint".
        :param string joint_prior_ref: (default: None), True if the prior probability associated to
            the value of parameter is defined by a joint prior probability function that depends on
            at least another parameter. False if this parameter is considered as independant of the
            other free parameter a priori.
        :param dict available_joint_priors: Dictionnary which contain all the joint priors available

        Keyword arguments are argument for the prior function (only for marginal priors). They
        depend on the prior function used.
        """
        # IN PRINCIPLE DO NOT NEED TO HAVE ALL THIS WITHIN AN if self.duplicate is None, BECAUSE self.prior_info refers to self.duplicate
        if isinstance(prior_category, str):
            if joint_prior_ref is not None:
                # Check of the joint prior ref has been defined in the param file and is thus available
                if joint_prior_ref in available_joint_priors:
                    self.prior_info["joint_prior_ref"] = joint_prior_ref
                else:
                    raise ValueError("Joint prior {} is not defined. If it's not a typo you "
                                     "have to define it in the joint prior section of the "
                                     "parameter file".format(joint_prior_ref))
                # Set category to None for no confusion
                self.prior_info["category"] = None
                # Check that the parameter is indeed mentioned as parameter of the joint prior
                for param_name_or_l_param_name in available_joint_priors[joint_prior_ref]["params"].values():
                    if isinstance(param_name_or_l_param_name, list):  # For Joint param with multiple params parameters, the contant of "params" can be a list of parameter names
                        l_param_name = param_name_or_l_param_name
                    else:
                        l_param_name = [param_name_or_l_param_name, ]
                    for param_name in l_param_name:
                        found = self.name.is_name(param_name)
                        if found:
                            break
                    if found:
                        break
                if not(found):
                    raise ValueError("{} is indicated has joint prior for Parameter {}. However, "
                                     "it doesn't appear has a joint prior parameter.".format(joint_prior_ref, self.get_name(include_prefix=True, recursive=True)))
                logger.debug("The Prior for param {} is joint and called {}."
                             "".format(self.get_name(include_prefix=True, recursive=True), self.joint_prior_ref))
            ## Give the category of prior: string, for example 'normal', 'uniform'
            else:
                if manager.is_available_priortype(prior_category):
                    priorfunction_subclass = manager.get_priorfunc_subclass(prior_category)
                    priorfunction_subclass.check_args(list(kwargs.keys()))
                    if prior_category != self.prior_info["category"]:
                        logger.debug("Prior category attribute of param {} changed from {} to {}"
                                     "".format(self.get_name(include_prefix=True, recursive=True), self.prior_info["category"],
                                               prior_category))
                        self.prior_info["category"] = prior_category
                        logger.debug("New prior args for param {}: {}"
                                     "".format(self.get_name(include_prefix=True, recursive=True), kwargs))
                        self.prior_info["args"] = kwargs
                    else:
                        for arg in priorfunction_subclass.all_args:
                            if (arg in self.prior_info["args"]) and (arg not in kwargs):
                                logger.debug("Prior arg {} of param {} changed from {} to None"
                                             "".format(arg, self.get_name(include_prefix=True, recursive=True),
                                                       self.prior_info["args"][arg]))
                                self.prior_info["args"].pop(arg)
                            elif (arg not in self.prior_info["args"]) and (arg in kwargs):
                                logger.debug("Prior arg {} of param {} changed from None to {}"
                                             "".format(arg, self.get_name(include_prefix=True, recursive=True), kwargs[arg]))
                                self.prior_info["args"][arg] = kwargs[arg]
                            elif (arg in self.prior_info["args"]) and (arg in kwargs):
                                if self.prior_info["args"][arg] != kwargs[arg]:
                                    logger.debug("Prior arg {} of param {} changed from {} to {}"
                                                 "".format(arg, self.get_name(include_prefix=True, recursive=True),
                                                           self.prior_info["args"][arg], kwargs[arg]))
                                    self.prior_info["args"][arg] = kwargs[arg]
                else:
                    raise ValueError("prior_category {} is not in the list of available prior types: {}"
                                     "".format(prior_category, manager.get_available_priors()))
        else:
            raise ValueError("prior_category should be a str.")

    @property
    def prior_config_dict(self):
        """
        """
        res = {}
        res['category'] = self.prior_category
        res['args'] = self.prior_args
        res['joint_prior_ref'] = self.joint_prior_ref
        return res

    def load_prior_config(self, dico_config, available_joint_priors={}, load_setup=False):
        """Load the configuration specified by the parameter dictionnary.

        :param dict dico_config : Dictionnary giving the configuration.
        :param dict available_joint_priors: Dictionnary which contain all the joint priors available
        :param bool load_setup: If True the manager load the setup file to update the available
            prior functions.
        """
        if load_setup:
            manager.load_setup()
        dico_prior = dico_config["prior"]
        self.set_prior(prior_category=dico_prior["category"],
                       joint_prior_ref=dico_prior.get("joint_prior_ref", None),
                       available_joint_priors=available_joint_priors,
                       **dico_prior["args"])
