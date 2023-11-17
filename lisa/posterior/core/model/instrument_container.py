"""The objective of this module is to provide the interface InstrumentContainerInterface. It upgrades
a ParamContainerDatabase with the possibility to handle an instruments database.
"""
from loguru import logger
from pprint import pformat

from .paramcontainers_database import SpecificParamContainerCategoryContainer
from ..dataset_and_instrument.instrument import instrument_model_category, Core_Instrument
from ..dataset_and_instrument.manager_dataset_instrument import Manager_Inst_Dataset
from ....tools.database_with_instrument_level import DatabaseInstLevel, check_args_instruments


mgr_inst_dst = Manager_Inst_Dataset()

string4datasetdico = "Dataset"
key_inst = "inst_dic"
key_misc = "misc"


class InstrumentContainerInterface(object):
    """docstring for InstrumentContainerInterface and interface of core_model.Core_Model.

    It has to be in the list of parent classes of Model before ParamContainerDatabase.
    It's an Interface of core_model.Core_Model which allows the model to properly handle instrument
    models.
    """
    def __init__(self):
        # Init the instruments
        self.paramcontainers.update({instrument_model_category: InstrumentContainer()})

    @property
    def instruments(self):
        """Return an Orderedict with the instrument models currently in the instance.

        Database of instrument models
        1st lvl: Keys: are instrument full categories:
                 Values: Orderedict
            2nd lvl: Keys: Instrument name
                     Values: Orderedict
                3nd lvl: Keys: Model name
                         Values: Instrument_Model instances
        """
        return self.paramcontainers[instrument_model_category]

    @property
    def inst_model_objects(self):
        """Return the list of instruments model object in the instruments container."""
        return list(set(self.get_instmodel_objs()))

    @property
    def inst_model_fullnames(self):
        """Return the list of instruments model full names in the instruments container."""
        return [instmod_obj.get_name(recursive=True, include_prefix=True) for instmod_obj in self.inst_model_objects]

    @property
    def inst_fullcategories(self):
        """Return the list of instruments full categories in this ParamContainerDatabase."""
        return self.instruments.inst_fullcategories

    @property
    def inst_categories(self):
        """Return the list of instruments categories in this ParamContainerDatabase."""
        return list(set([mgr_inst_dst.interpret_inst_fullcat(inst_fullcat=inst_fullcat)[0] for inst_fullcat in self.inst_fullcategories]))

    @property
    def noisemodel_categories(self):
        """Return the list of noise model categories used."""
        l_noisemodels_used = list(set([instmod_obj.noise_model_category for instmod_obj in self.inst_model_objects]))
        # Remove None in case it is used.
        if None in l_noisemodels_used:
            l_noisemodels_used.remove(None)
        return l_noisemodels_used

    def get_inst_fullcat4inst_cat(self, inst_cat):
        """Return the list of unique instrument full category that correspond to a provided instrument category.

        Equivalent to self.instruments.get_inst_fullcat4inst_cat(inst_cat)

        Arguments
        ---------
        inst_cat : str
            Instrument category for which you want the list of instrument full categories

        Returns
        -------
        l_inst_fullcat : list of instrument full categories
            List of instrument full categories for the provided instrument category
        """
        return self.instruments.get_inst_fullcat4inst_cat(inst_cat=inst_cat)

    def add_an_instrument_model(self, instrument, name, force=False):
        """Add an instrument model to the paramcontainers of this model."""
        if not(isinstance(instrument, Core_Instrument)):
            raise ValueError("instrument should be an instance of a subclass of "
                             "Core_Instrument.")
        inst_fullcat = instrument.full_category
        inst_name = instrument.get_name()
        inst_model_obj = instrument.create_model_instance(name=name, kwargs_getname_4_storename={"include_prefix": True, "recursive": True},
                                                          kwargs_getname_4_codename={"include_prefix": False, "code_version": True})
        self.instruments[inst_fullcat][inst_name][name] = inst_model_obj

    def rm_an_instrument_model(self, inst_model, inst_name, inst_fullcat, **kwargs):
        """Remove an instrument model to the paramcontainers of this model."""
        inst_model, inst_name, inst_fullcat = check_args_instruments(inst_model=inst_model, inst_name=inst_name,
                                                                     inst_fullcat=inst_fullcat, **kwargs)
        self.instruments[inst_fullcat][inst_name].pop(inst_model)

    def get_instmodel_objs(self, inst_model=None, inst_name=None, inst_fullcat=None,
                           sortby_instfullcat=False, sortby_instname=False, sortby_instmodel=False,
                           **kwargs):
        """Return instrument model objects."""
        return self.instruments.get_objects(inst_model=inst_model, inst_name=inst_name,
                                            inst_fullcat=inst_fullcat, sortby_instfullcat=sortby_instfullcat,
                                            sortby_instname=sortby_instname,
                                            sortby_instmodel=sortby_instmodel, **kwargs)

    def get_instmodel_names(self, inst_name=None, inst_fullcat=None,
                            sortby_instname=False, sortby_instfullcat=False):
        """Return instrument model names."""
        return self.instruments.get_instmodels(inst_name=inst_name, inst_fullcat=inst_fullcat,
                                               sortby_instname=sortby_instname,
                                               sortby_instfullcat=sortby_instfullcat)

    def get_inst_names(self, inst_fullcat=None, sortby_instfullcat=False):
        """Return the list of instrument names."""
        return self.instruments.get_instnames(inst_fullcat=inst_fullcat, sortby_instfullcat=sortby_instfullcat)

    def get_instmodobjs_using_noisemod(self, noisemod_cat):
        """Return the list of instrument model objects using a giving noise model category."""
        res = []
        for instmod_obj in self.get_instmodel_objs():
            if instmod_obj.noise_model_category == noisemod_cat:
                res.append(instmod_obj)
        return res

    def get_instmodfullnames_using_noisemod(self, noisemod_cat):
        """Return the list of instrument model objects using a giving noise model category."""
        return [instmod_obj.get_name(include_prefix=True, recursive=True) for instmod_obj in self.get_instmodobjs_using_noisemod(noisemod_cat=noisemod_cat)]

    def instrumenthasatleast1model(self, inst_name, inst_fullcat=None):
        """Return True if there is at least one instrument model for the instrument."""
        return self.instruments.hasatleast1instmod(inst_name=inst_name, inst_fullcat=inst_fullcat)


class InstrumentContainer(DatabaseInstLevel, SpecificParamContainerCategoryContainer):
    """docstring for InstrumentContainer."""

    def __init__(self):
        super(InstrumentContainer, self).__init__(object_stored="instmodobj",
                                                  database_name="instrument container",
                                                  ordered=True)

    def get_list_params(self, main=False, free=False, no_duplicate=True, only_duplicates=False, l_inst_model_names=[]):
        """Return the list of all parameters.

         Arguments
        ---------
        main            : bool
            If true (default false) returns only the main parameters. If False all parameters are returned.
        free            : bool
            If true (default false) returns only the free parameters. If False, wether or the parameter
            is not free is not used to return it or not. the free argument only makes sense for main parameters,
            so it's ignored if main is not True.
        no_duplicate    : bool
            If True, the output list will not include the duplicate parameters, only the orignals
            no_duplicate and only_duplicates cannot be True at the same time
        only_duplicates : bool
            If True, the output list will only include duplicate parameters (not the original of these duplicates)
            no_duplicate and only_duplicates cannot be True at the same time
        l_inst_model_names : list of strings
            list of the names of instrument models for which you want the params.

        Returns
        -------
        list_of_param: list of Parameter instances
        """
        result = []
        for inst_mod_name in l_inst_model_names:
            mod = self[inst_mod_name]
            result_mod = mod.get_list_params(main=main, free=free, no_duplicate=no_duplicate, only_duplicates=only_duplicates)
            if no_duplicate:
                result_param_name = [param_in_res.get_name(include_prefix=True, recursive=True, force_no_duplicate=False) for param_in_res in result]
                for param in result_mod:
                    if param.get_name(include_prefix=True, recursive=True, force_no_duplicate=False) not in result_param_name:
                        result.append(param)
            else:
                result.extend(result_mod)
        return result

    def get_inst_fullcat4inst_cat(self, inst_cat):
        """Return the list of unique instrument full category that correspond to a provided instrument category.

        Arguments
        ---------
        inst_cat : str
            Instrument category for which you want the list of instrument full categories

        Returns
        -------
        l_inst_fullcat : list of instrument full categories
            List of instrument full categories for the provided instrument category
        """
        res = []
        for inst_fullcat_i in self.inst_fullcategories:
            inst_cat_i, inst_subcat_i = mgr_inst_dst.interpret_inst_fullcat(inst_fullcat_i)
            if (inst_cat_i == inst_cat) and (inst_fullcat_i not in res):
                res.append(inst_fullcat_i)
        return res

    def get_subkwargs_4_get_list_params(self, model_instance=None, **kwargs):
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
        selected_kwargs = {}
        # Get the specific arguments for InstrumentContainer get_param function
        for kwarg_name in ["l_inst_model_names"]:
            selected_kwargs[kwarg_name] = kwargs.get(kwarg_name, None)
        # Set the default value if not provided
        if selected_kwargs["l_inst_model_names"] is None:
            selected_kwargs["l_inst_model_names"] = model_instance.name_instmodels_used()  # name_instmodels_used is defined in Instmodel4Dataset
        return selected_kwargs
    
    @property
    def priors_dict(self):
        res = {}
        for inst_fullcat in self.inst_fullcategories:
            res[inst_fullcat] = {}
            for inst_name in self[inst_fullcat]:
                res[inst_fullcat][inst_name] = {}
                for inst_model in self[inst_fullcat][inst_name].values():
                    res[inst_fullcat][inst_name][inst_model.get_name()] = inst_model.priors_dict
        return res

    def load_priors_config(self, dico_priors_config, available_joint_priors={}):
        """Update the paramfile_info for an instrument category.

        It updates things introduced by get_allinst_paramfilesection in paramfile_info.
        """
        if set(self.inst_fullcategories) != set(dico_priors_config.keys()):
            raise ValueError(f"The priors['instruments'] dictionary in the configuration files doesn't hae the expected keys. Expected {self.inst_fullcategories}, got {dico_priors_config.keys()}")
        for inst_fullcat in self.inst_fullcategories:
            if set(self[inst_fullcat].keys()) != set(dico_priors_config[inst_fullcat].keys()):
                raise ValueError(f"The priors['instruments'][{inst_fullcat}] dictionary in the configuration files doesn't hae the expected keys. Expected {self[inst_fullcat].keys()}, got {dico_priors_config[inst_fullcat].keys()}")
            for inst_name in self[inst_fullcat]:
                if set(self[inst_fullcat][inst_name].keys()) != set(dico_priors_config[inst_fullcat][inst_name].keys()):
                    raise ValueError(f"The priors['instruments'][{inst_fullcat}][{inst_name}] dictionary in the configuration files doesn't hae the expected keys. Expected {self[inst_fullcat][inst_name].keys()}, got {dico_priors_config[inst_fullcat][inst_name].keys()}")
                for inst_model in self[inst_fullcat][inst_name].values():
                    self[inst_fullcat][inst_name][inst_model.get_name()].load_priors_config(dico_priors_config=dico_priors_config[inst_fullcat][inst_name][inst_model.get_name()],
                                                                                            available_joint_priors=available_joint_priors)
