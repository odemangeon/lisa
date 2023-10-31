"""
paramcontainer_database module.

The objective of this module is to manage the Paramcontainers database.

@DONE:
    -
@TODO:
    - update nb_of_paramcontainers to properly take into account the instruments
"""
from loguru import logger
from collections import OrderedDict

from ..paramcontainer import Core_ParamContainer


class ParamContainerDatabase(object):
    """docstring for ParamContainerDatabase."""
    def __init__(self):
        # super(ParamContainerDatabase, self).__init__()
        self._paramcontainers = OrderedDict()
        self._store_name_rules = OrderedDict()

    @property
    def name(self):
        """Return "ParamContainerDatabase" should be overloaded by subclass."""
        return "ParamContainerDatabase"

    @property
    def paramcontainers(self):
        """ParamContainers contained in the models sorted into categorie."""
        return self._paramcontainers

    @property
    def store_name_rules_db(self):
        """ParamContainers contained in the models sorted into categorie."""
        return self._store_name_rules

    def add_a_paramcontainer(self, paramcontainer, force=False):
        """Add a paramcontainer to the model.

        :param Core_ParamContainer paramcontainer: Paramcontainer to add to the database.
        :param bool force: If True the paramcontainer is added to the database even if a paramcontainer
            with the same store name already exists (it will be overwriten).
        """
        if not(isinstance(paramcontainer, Core_ParamContainer)):
            raise ValueError("paramcontainer should be an instance of a subclass of "
                             "Core_ParamContainer.")
        parcont_name = paramcontainer.store_name
        parcont_cat = paramcontainer.category
        # Check if the category of the param container already exist in the database. If not add it
        if parcont_cat not in self.paramcontainers:
            self.paramcontainers.update({parcont_cat: OrderedDict()})
            self.store_name_rules_db.update({parcont_cat: paramcontainer.store_name_rules})
        # Check if the
        if not(self.store_name_rules_db[parcont_cat] == paramcontainer.store_name_rules):
            raise ValueError("This param container ({}) doesn't not have the same store name rules "
                             "than previous ones of the same category.")
        if parcont_name in self.paramcontainers[parcont_cat]:
            if not(force):
                logger.error("paramcontainer {} already exist in the model, it will not be "
                             "added.".format(parcont_cat + '_' + parcont_name))
                raise ValueError("The paramcontainer named {} alredy exist in the model"
                                 "".format(parcont_name))
            else:
                logger.error("paramcontainer {} already exist in the model, it will be replaced."
                             "".format(parcont_cat + '_' + parcont_name))
        self.paramcontainers[parcont_cat].update({parcont_name: paramcontainer})

    def isavailable_paramcontainer(self, name, category):
        """Return True if filename correspond to a dataset that is in the database.
        ----
        Arguments:
            name : string,
                Storage name of the paramcontainer.
            category : string,
                category of the paramcontainer
        """
        if category not in self.paramcontainers:
            return False
        else:
            return name in self.paramcontainers[category]

    def rm_paramcontainer(self, name, category):
        """Remove a dataset from the the dataset database.
        ----
        Arguments:
            name : string,
                name of the paramcontainer.
            category : string,
                category of the paramcontainer
        """
        res = self.paramcontainers[category].pop(name)
        if res is None:
            logger.warning("The deletion of the paramcontainer {} from the model has failed "
                           "because it was not found was not found.".format(category + '_' + name))
        else:
            logger.info("The paramcontainer {} has been removed from the model."
                        "".format(category + '_' + name))
        if len(self.paramcontainers[category]) == 0:
            self.paramcontainers.pop(category)

    @property
    def nb_of_paramcontainers(self):
        """Returns the dict giving the number of paramcontainers in each category."""
        result = dict()
        for key, dico_cat in self.paramcontainers.items():
            result[key] = len(dico_cat)
        return result

    @property
    def paramcont_categories(self):
        """ParamContainers contained in the models sorted into categorie."""
        return list(self.paramcontainers.keys())

    @property
    def paramcontainers_categories(self):
        """Return the list of the paramcontainer categories in this ParamContainerDatabase."""
        return list(self.paramcontainers.keys())

    def get_list_params(self, model_instance, main=False, free=False, no_duplicate=True, **kwargs):
        """Return the list of all parameters.

        TODO: This doesn't seems right. Check why would you need model_instance here and if this function is actually used.

        :param Core_Model model_instance: Model instance which is used for the default value of
            some SpecificParamContainerCategory .
        :param bool main: If true (default false) returns only the main parameters
        :param bool free: If true (default false) returns only the free parameters

        Keyword arguments are arguments specific to a certain type of parameter containers (like the
         instruments). See get_list_params of these parameter container for more information.

        :return list_of_param result: list of Parameter instances
        """
        result = []
        for paramcont_cat in self.paramcontainers_categories:  # Categories of param containers, like instruments.
            if isinstance(self.paramcontainers[paramcont_cat], SpecificParamContainerCategory):
                selectedkwargs = (self.paramcontainers[paramcont_cat].
                                  get_subkwargs_4_get_list_params(model_instance, **kwargs))
                result_param_cont = self.paramcontainers[paramcont_cat].get_list_params(main=main, free=free,
                                                                                        no_duplicate=no_duplicate,
                                                                                        **selectedkwargs)
                if no_duplicate:
                    result_param_name = [param_in_res.get_name(include_prefix=True, recursive=True, force_no_duplicate=False) for param_in_res in result]
                    for param in result_param_cont:
                        if param.get_name(include_prefix=True, recursive=True, force_no_duplicate=False) not in result_param_name:
                            result.append(param)
                else:
                    result.extend(result_param_cont)
            else:
                for param_cont in self.paramcontainers[paramcont_cat].values():
                    result_param_cont = param_cont.get_list_params(main=main, free=free, no_duplicate=no_duplicate)
                    if no_duplicate:
                        result_param_name = [param_in_res.get_name(include_prefix=True, recursive=True) for param_in_res in result]
                        for param in result_param_cont:
                            if param.get_name(include_prefix=True, recursive=True) not in result_param_name:
                                result.append(param)
                    else:
                        result.extend(result_param_cont)
        return result

    def get_list_paramnames(self, model_instance=None, main=False, free=False, no_duplicate=True, **kwargs):
        """Return the list of all parameters.

        :param bool main: If true (default false) returns only the main parameters
        :param bool free: If true (default false) returns only the free parameters
        :param Core_Model model_instance: Model instance which is used for the default value of
            some SpecificParamContainerCategory (optional).

        Keyword arguments are passed to the Named.get_name methods (see docstring for details).

        :return list_of_string l_paramnames: List of names or full names of the parameters specified
            by args and kwargs.
        """
        result = []
        for param in self.get_list_params(model_instance=model_instance, main=main, free=free, no_duplicate=no_duplicate):
            result.append(param.get_name(**kwargs))
        return result


class SpecificParamContainerCategoryContainer(MutableMapping):
    """docstring for SpecificParamContainerCategory."""

    def __init__(self, ordered=False):
        """
        """
        self.__ordered = ordered
        if self.__ordered:
            self.__data = OrderedDict()
        else:
            self.__data = dict()

    @property
    def category(self):
        raise NotImplementedError("You need to overload this method in the subclass.")

    @property
    def ordered(self):
        """True if the container is based on an Ordereddict else it is a dict"""
        return self.__ordered

    @ordered.setter
    def ordered(self, boolean):
        if isinstance(boolean, bool):
            self.__ordered = boolean
        else:
            raise ValueError("ordered has to be a boolean.")

    def __copy__(self):
        res = type(self)(ordered=self.ordered)
        res.update(self.__data)
        return res

    @property
    def _data(self):
        return self.__data

    def __len__(self):
        return len(self.__data)

    def __iter__(self):
        return iter(self.__data)

    def __setitem__(self, key, value):
        self.__data[full_name] = value

    def __delitem__(self, full_name):
        del self.__data[full_name]

    def __getitem__(self, full_name):
        if full_name in self.__data:
            return self.__data[full_name]
        if hasattr(self, "__missing__"):
            return self.__missing__(full_name)
        else:
            raise KeyError(full_name)

    def __contains__(self, full_name):
        return full_name in self.__data

    @property
    def l_param_container_fullname(self):
        return list(self.keys())

    @property
    def l_param_container(self):
        return list(self.values())

    def get_list_params(self, main=False, free=False, no_duplicate=True, l_param_container_fullname=None):
        """Return the list of all parameters.

        Arguments
        ---------
        main : Boolean
            If true (default false) returns only the main parameters
        free : Boolean
            If true (default false) returns only the free parameters
        l_param_container_fullname : list of strings
            list of the names of param containers for which you want the params.

        Returns
        -------
        list_of_param: list of Parameter instances
        """
        result = []
        if l_param_container_fullname is None:
            l_param_container_fullname = self.l_param_container_fullname
        for param_container_fullname in l_param_container_fullname:
            param_container = self[param_container_fullname]
            result_param_container = param_container.get_list_params(main=main, free=free, no_duplicate=no_duplicate)
            if no_duplicate:
                result_param_name = [param_in_res.get_name(include_prefix=True, recursive=True, force_no_duplicate=False) for param_in_res in result_param_container]
                for param in result_param_container:
                    if param.get_name(include_prefix=True, recursive=True, force_no_duplicate=False) not in result_param_name:
                        result.append(param)
            else:
                result.extend(result_param_container)
        return result

    def get_subkwargs_4_get_list_params(self, model_instance, **kwargs):
        """Select the keyword arguments for the get_list_params method.

        Argument
        --------
        model_instance  : Core_Model
            Model instance which is used for the default value of kwargs, see below (optional).

        Keyword argument that are used by the get_list_params method of InstrumentContainer

        Return
        ------
        selected_kwargs : dict
            Dictionary providing the kwargs required by get_list_params
        """
        raise NotImplementedError("You need to overload this method in the subclass.")

    @property    
    def dico_prior_config(self):
        """Return the dictionary for the configuration of the priors of the parameters of the parameter containers
        located in this container.
        """
        text = ""
        result = {}
        for param_container in self.l_param_container:
            result[param_container.full_name] = param_container.dico_prior_config
        return result

    def load_prior_config(self, dico_prior_config, model_instance, available_joint_priors={}):
        """Load the configuration for the prior of the parameters of the parameter containers
        located in this container.
        """
        for param_container_fullname in dico_prior_config:
            param_container = self[param_container_fullname]
            param_container.load_prior_config(dico_prior_config=dico_prior_config[param_container_fullname], model_instance=model_instance, available_joint_priors=available_joint_priors)

