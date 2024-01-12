"""
model_prior module.

The objective of this module is to define the Model_Prior class which will generate the prior functions.

@DONE:
    -

@TODO:
    -
"""
from loguru import logger
from collections import OrderedDict
from copy import deepcopy

from .core_prior import Manager_Prior
from ..model import par_vec_name
from ..database_func import DatabaseInstLvlDataset
from .prior_docfunc import PriorDocFunc
from ....tools.miscellaneous import spacestring_like


## manager object
manager = Manager_Prior()
manager.load_setup()


class Model_Prior(object):
    """docstring for Model_Prior."""

    ## Name of the joint prior dictionary for the parameter file
    joint_prior_name = 'joint_priors'

    def __init__(self):
        """Initialise the information related to the Prior for the Model instance.

        This should be called from the Core_Model.__init__ method.
        This class is not meant to be instanciated directly (except for test purposes).

        :param dict paramfile_info: Dictionary containing the name of information that the parameter
            file provides for each parameter
        """
        # Initialise the joint_prior_container
        self.__joint_priors = OrderedDict()

    @property
    def joint_prior_container(self):
        """Container where the information regarding the joint priors are stored.

        It's an OrderedDict with as keys the joint prior reference used in the parameter file and as
        values a dictionary with three keys: "category" which contain the joint prior category,
        "args": which contains the arguments to use for the initialisation of the joint prior instance,
        "params": with a dictionary which associate its keys which are the param keys define in the
        Joint prior class, to its value which the name of the parameter chosen for these param keys.
        """
        return self.__joint_priors

    @property
    def jointprior_config_dict(self):
        return dict(deepcopy(self.__joint_priors))

    def load_jointprior_config(self, dico_jointprior_config):
        """load the configuration for joint priors specified by the dictionary into joint_prior_container

        :param dict dico_config: Dictionnary containing the joint priors information.
        """
        self.joint_prior_container.clear()
        logger.debug("joint prior container cleared.")
        for joint_prior_ref, dico_jointprior in dico_jointprior_config.items():
            # Check that the joint prior category is available
            if manager.is_available_priortype(dico_jointprior["category"]):
                priorfunction_subclass = manager.get_priorfunc_subclass(dico_jointprior["category"])
                # Check that this is a joint prior
                if not priorfunction_subclass.joint:
                    raise ValueError("Prior category {} is not a joint prior category".format(dico_jointprior["category"]))
                # Check that the arguments are fine
                priorfunction_subclass.check_args(list(dico_jointprior["args"].keys()))
                # Check the parameters
                priorfunction_subclass.check_params(dico_jointprior["params"], self)
            else:
                raise ValueError("prior_category {} is not in the list of available prior types: {}"
                                 "".format(dico_jointprior["category"], manager.get_available_priors()))
            # Add the joint prior to the joint_prior_container
            self.joint_prior_container[joint_prior_ref] = {"category": dico_jointprior["category"],
                                                           "args": dico_jointprior["args"],
                                                           "params": dico_jointprior["params"]}
            logger.info("Joint prior {} of category {} added to the joint prior container."
                        "".format(joint_prior_ref, dico_jointprior["category"]))
            # Set the joint_prior attribute of the parameter of this joint prior to joint_prior_ref
            priorfunction_subclass.set_params_jointprior_ref(params=dico_jointprior["params"], joint_prior_ref=joint_prior_ref, 
                                                             available_joint_priors=self.joint_prior_container, model_instance=self)

    def create_individual_lnpriors(self):
        """Return a dictionnary providing the individual prior probability density functions.

        Returns
        -------
        priors  : dict
            Return the dictionary containing all the elementary priors (marginal and joints)
            for all the main and free parameters of the model.
            The format of this dictionary is:
            {"marginal" : {"<param_name>": prior_logpdf_function},
             "joint"    : {"logpdf": {"<joint_prior_ref>": {"function": joint_logprior_function, "nb_param": nb_of_parameter}, ...},
                           "param_names": {"<param_name>": {"ref": "<joint_prior_ref>", "idx": index_of_param_in_jointprior_argument_list}, ...}}
        """
        # Look for all the main free parameters in the model (self) and put them in two dict
        # marginal and joint dependending on wether they have a marginal or joint prior.
        marginal = OrderedDict()  # format: {"param_name": param_instance, ...}
        joint = OrderedDict()  # format: {"param_name": param_instance, ...}
        for param in self.get_list_params(main=True, free=True, recursive=True, no_duplicate=True):
            if param.joint:
                joint[param.get_name(include_prefix=True, recursive=True)] = param
            else:
                marginal[param.get_name(include_prefix=True, recursive=True)] = param
        # Create a dict to receive the priors with two keys: marginal and joint
        priors = {"marginal": {},  # format:  {"<param_name>": prior_logpdf_function, ...}
                  "joint": {"logpdf": {},  # format: {"<joint_prior_ref>": {"function": joint_logprior_function, "nb_param": nb_of_parameter}, ...}
                            "param_names": {}  # format: {"<param_name>": {"ref": "joint_prior_ref", "idx": index_of_param_in_jointprior_argument_list}, ...}
                            }
                  }
        # For each parameter in the list of marginal (step 1): Create an entry in
        # "marginal" (see step 2) which to the full name of the parameter associate the
        # marginal prior function.
        logger.info("Creating marginal priors")
        for full_name, param in marginal.items():
            logger.info("Creating marginal priors for {}".format(full_name))
            prior_func = manager.get_priorfunc_subclass(param.prior_category)(**param.prior_args)
            priors["marginal"][full_name] = prior_func.create_logpdf()
        # For each parameter in the list of joint (step 1):
        # Check if the joint prior references is already in the priors["joint"] dictionary meaning
        # that it has already been created for another parameter.
        # If not, get the info from self.joint_prior_container, create the joint prior instance
        # Create the logpdf
        logger.info("Creating joint priors")
        for full_name, param in joint.items():
            logger.info("looking into joint priors of param {}".format(full_name))
            joint_prior_info = self.joint_prior_container[param.joint_prior_ref]
            joint_prior_func = manager.get_priorfunc_subclass(joint_prior_info["category"])(joint_prior_info["params"], **joint_prior_info["args"])
            if param.joint_prior_ref not in priors["joint"]["logpdf"]:
                logger.info("Creating joint priors reference {}".format(param.joint_prior_ref))
                params = {}
                for param_ref, param_name_or_l_param_name in joint_prior_info["params"].items():
                    if isinstance(param_name_or_l_param_name, list):  # If joint prior has multiple parameters param_name_or_l_param_name is a list of parameter names
                        params[param_ref] = [self.get_parameter(param_name, kwargs_get_list_params={'recursive': True},
                                                                kwargs_get_name={'include_prefix': True, 'recursive': True, 'force_no_duplicate': True})
                                             for param_name in param_name_or_l_param_name]
                    else:
                        params[param_ref] = self.get_parameter(param_name_or_l_param_name, kwargs_get_list_params={'recursive': True},
                                                               kwargs_get_name={'include_prefix': True, 'recursive': True, 'force_no_duplicate': True})
                priors["joint"]["logpdf"][param.joint_prior_ref] = {"function": joint_prior_func.create_logpdf(params),
                                                                    "nb_param": joint_prior_func.get_params_nb()}
            idx = None
            for ii, param_name in enumerate(joint_prior_func.param_name_fulllist):
                if param.name.is_name(param_name):
                    idx = ii
                    break
            if idx is None:
                raise ValueError("Parameter {} not found in joint prior info dictionary: {}"
                                 "".format(full_name, joint_prior_info["params"]))
            else:
                priors["joint"]["param_names"][full_name] = {"ref": param.joint_prior_ref, "idx": idx}
        return priors

    def __joint_lnprior_creator(self, lnpriors_and_indexes, param_prior_names_list, mand_kwargs_list=None, opt_kwargs_dict=None):
        """Create and return the joint prior function.

        :param list_of_tuple lnpriors_and_indexes: List of tuples of 2 elements. Each element
            contain the a prior function as its element 0 and an index or a list of indexes as its element 1.
            If there the prior function is the marginal prior of a parameter, the second element is
            be one int giving the index of the parameter in the input array. If the prior function is
            a joint prior of several parameters, the second element is a list of int giving the indexes
            of these parameters in the input array.
        :return DocFunction func: Joint prior function.
        """
        logger.debug(f"Creating joint prior with the following lnpriors_and_indexes:\n{lnpriors_and_indexes}"
                     f"\nand the following param_prior_names_list {param_prior_names_list}"
                     f"\nand the following mand_kwargs_list {mand_kwargs_list}"
                     f"\nand the following opt_kwargs_dict {opt_kwargs_dict}")

        def joint_lnprior(p_vect):
            res = 0
            # logger.debug("paramnames prior ({}): {}".format(len(arg_list["param"]),
            #                                                 arg_list["param"]))
            # logger.debug("params prior ({}): {}".format(len(p), p))
            for ln_prior, ii in lnpriors_and_indexes:
                res += ln_prior(p_vect[ii])
            return res
        return PriorDocFunc(function=joint_lnprior, param_prior_names_list=param_prior_names_list, params_prior_vect_name=par_vec_name,
                            mand_kwargs_list=mand_kwargs_list, opt_kwargs_dict=opt_kwargs_dict)

    def create_joint_lnprior(self, list_paramnames, individual_priors=None):
        """Return a joint prior function for the list of parameter provided.

        Argument
        --------
        list_paramnames     : list_of_str
            List of parameters full names (include_prefix and recursive)
        individual_priors   : dict
            Dictionary produced by the create_individual_lnpriors method. If None it will created within
            this method.

        Returns
        -------
        docf : DocFunction or None
            DocFunction giving the joint ln prior. This functions can return None if on of the individual
            joint prior used doesn't have access to all the parameters that it requires in list_paramnames
        """
        logger.debug(f"Creating joint prior for the following list of parameters {list_paramnames}.")
        # Create the individual priors if needed
        if individual_priors is None:
            individual_priors = self.create_individual_lnpriors()

        # Create two structures to receive the marginal priors and the joint priors that needed to be
        # used for the list of provided parameters and also stores the information of the idx of their
        # parameters in the provided list of parameters
        marginal_lnpriors = []  # format: [(marginal_prior_function_of_param_ii, idx_of_param_ii), ...]
        joint_lnpriors = OrderedDict()  # format: {"joint_prior_ref": (joint_prior_function, [idx_param_ii, idx_param_jj]), ...}
        for ii, param_name in enumerate(list_paramnames):
            if param_name in individual_priors["marginal"]:
                marginal_lnpriors.append((individual_priors['marginal'][param_name], ii))
            elif param_name in individual_priors["joint"]["param_names"]:
                joint_prior_ref = individual_priors["joint"]["param_names"][param_name]["ref"]
                idx_in_jointprior = individual_priors["joint"]["param_names"][param_name]["idx"]
                if joint_prior_ref not in joint_lnpriors:
                    joint_lnpriors[joint_prior_ref] = (individual_priors["joint"]["logpdf"][joint_prior_ref]["function"],
                                                       [None for par in range(individual_priors["joint"]["logpdf"][joint_prior_ref]["nb_param"])])
                joint_lnpriors[joint_prior_ref][1][idx_in_jointprior] = ii
            else:
                raise ValueError("Parameter {} doesn't exist in the individual priors dictionary."
                                 "".format(param_name))
        logger.debug(f"individual marginal priors and index of the parameters required {marginal_lnpriors}.")
        logger.debug(f"individual joint priors and index of the parameters required {joint_lnpriors}.")
        # Check if all parameters required by the joint priors have been found in list_paramnames
        for joint_prior_ref, (joint_prior_func, l_param_idx) in joint_lnpriors.items():
            if any([ii is None for ii in l_param_idx]):
                logger.warning(f"It was not possible to create the joint prior because joint prior {joint_prior_ref}"
                               " doesn't have access to all his required parameters.")
                return None
        # Call __joint_lnprior_creator to create the Docfunction of the joint lnprior function from
        # marginal_lnpriors, joint_lnpriors and arg_list.
        docf = self.__joint_lnprior_creator(lnpriors_and_indexes=marginal_lnpriors + list(joint_lnpriors.values()),
                                            param_prior_names_list=list_paramnames.copy())
        return docf

    def create_lnpriors(self, lnlike_db, individual_priors=None, affectinstmodel4dataset=False,
                        lock_db=False):
        """Create the joint prior functions
        """
        if individual_priors is None:
            individual_priors = self.create_individual_lnpriors()
        if affectinstmodel4dataset:
            instmodel4dataset = self.instmodel4dataset.copy()
        else:
            instmodel4dataset = None
        db = DatabaseInstLvlDataset(object_stored="lnpriors", database_name=self.object_name,
                                    instmodel4dataset=instmodel4dataset, ordered=False)
        db.database_unlock()
        for inst_cat in lnlike_db:
            for inst_name in lnlike_db[inst_cat]:
                for inst_model in lnlike_db[inst_cat][inst_name]:
                    db[inst_cat][inst_name][inst_model] = {}
                    for obj in lnlike_db[inst_cat][inst_name][inst_model]:
                        joint_prior = self.create_joint_lnprior(list_paramnames=lnlike_db[inst_cat][inst_name][inst_model][obj].param_model_names_list,
                                                                individual_priors=individual_priors)
                        if joint_prior is not None:
                            db[inst_cat][inst_name][inst_model][obj] = joint_prior
                        else:
                            logger.warning(f"Joint log prior of instrument model {inst_cat}_{inst_name}_{inst_model}"
                                           f" could not be created.")
        if lock_db:
            db.lock()
        return db

    def create_lnpriors_perdataset(self, individual_priors, lnlike_db_dtst):
        """Create the ln prior functions associated to the lnlikelihood of each dataset.

        Arguments
        ---------
        individual_priors : dict
            Dictionary produced by the create_individual_lnpriors method.
        lnlike_db_dtst    : dict
            Dictionary with key = dataset name, value = LikelihoodDocFunc giving the likelihood doc
            function for the dataset

        Returns
        -------
        db  : dict
            Dictionary with key = dataset name, value = DocFunction giving the likelihood doc function
            for the dataset
        """
        db = {}
        for dataset_name, lnlike_docfunc in lnlike_db_dtst.items():
            # For IND dataset you might not want to model them. In this case the lnlike_docfunc should be None
            if lnlike_docfunc is not None:
                logger.info(f"Creating lnpriors for dataset {dataset_name}")
                joint_prior = self.create_joint_lnprior(list_paramnames=lnlike_docfunc.param_model_names_list,
                                                        individual_priors=individual_priors)
                if joint_prior is not None:
                    db[dataset_name] = joint_prior
                else:
                    logger.warning(f"Joint log prior of dataset {dataset_name} could not be created.")
        return db
