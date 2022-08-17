#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
instrument container module.

The objective of this module is to provide the interface InstrumentContainerInterface. It upgrades
a ParamContainerDatabase with the possibility to handle an instruments database.
"""
from logging import getLogger

from .paramcontainers_database import SpecificParamContainerCategory
from ..dataset_and_instrument.instrument import instrument_model_category, Core_Instrument
from ..dataset_and_instrument.manager_dataset_instrument import Manager_Inst_Dataset
from ....tools.database_with_instrument_level import DatabaseInstLevel, check_args
from ....tools.miscellaneous import spacestring_like


## Logger object
logger = getLogger()

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
        # super(ParamContainerDatabase, self).__init__()
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
        l_noisemodels_used = list(set([instmod_obj.noise_model for instmod_obj in self.inst_model_objects]))
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
        inst_model, inst_name, inst_fullcat = check_args(inst_model=inst_model, inst_name=inst_name,
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
        for instmod_objs in self.get_instmodel_objs():
            if instmod_objs.noise_model == noisemod_cat:
                res.append(instmod_objs)
        return res

    def get_instmodfullnames_using_noisemod(self, noisemod_cat):
        """Return the list of instrument model objects using a giving noise model category."""
        return [instmod_obj.get_name(include_prefix=True, recursive=True) for instmod_obj in self.get_instmodobjs_using_noisemod(noisemod_cat=noisemod_cat)]

    def instrumenthasatleast1model(self, inst_name, inst_fullcat=None):
        """Return True if there is at least one instrument model for the instrument."""
        return self.instruments.hasatleast1instmod(inst_name=inst_name, inst_fullcat=inst_fullcat)


class InstrumentContainer(DatabaseInstLevel, SpecificParamContainerCategory):
    """docstring for InstrumentContainer."""

    def __init__(self):
        super(InstrumentContainer, self).__init__(object_stored="instmodobj",
                                                  database_name="instrument container",
                                                  ordered=True)

    def get_list_params(self, main=False, free=False, no_duplicate=True, l_inst_model_names=[]):
        """Return the list of all parameters.

        Arguments
        ---------
        main : Boolean
            If true (default false) returns only the main parameters
        free : Boolean
            If true (default false) returns only the free parameters
        l_inst_model_names : list of strings
            list of the names of instrument models for which you want the params.

        Returns
        -------
        list_of_param: list of Parameter instances
        """
        result = []
        for inst_mod_name in l_inst_model_names:
            mod = self[inst_mod_name]
            result_mod = mod.get_list_params(main=main, free=free, no_duplicate=no_duplicate)
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

        :param Core_Model model_instance: Model instance which is used for the default value of
            inst_models, see below (optional).

        Keyword argument that are used by the get_list_params method of InstrumentContainer
        only:
        :param dict inst_models : Dictionnary which for each instrument name give the list of the
                names of instrument models for which you want the params.
                key = isntrument name, value = list of instrument model name
                If not provided, we return all the instrument models used by the model.

        :return dict selected_kwargs: Dictionary with key = argument name, value = argument value
        """
        selected_kwargs = {}
        # Get the specific arguments for InstrumentContainer get_param function
        for kwarg_name in ["l_inst_model_names"]:
            selected_kwargs[kwarg_name] = kwargs.get(kwarg_name, None)
        # Set the default value for inst_models, if not provided
        if selected_kwargs["l_inst_model_names"] is None:
            selected_kwargs["l_inst_model_names"] = model_instance.name_instmodels_used()  # name_instmodels_used is defined in Instmodel4Dataset
        return selected_kwargs

    def get_paramfile_section(self, model_instance, text_tab="", entete_symb=" = ", quote_name=False):
        """Return the paramfile section for every instrument category.

        Arguments
        ---------
        model_instance : Core_Model
            Core_Model subclass instance
        text_tab       : str
            text giving the tabulation that needs to be added to this the text to obtain the good alignment
            in the input file.
        entete_symb    : str
            Symbol to use after the instrument name
        quote_name     : bool
            If True the name of the instrument names will be quoted in the text

        """
        text = ""
        for inst_fullcat in self.inst_fullcategories:
            inst_cat, inst_subcat = mgr_inst_dst.interpret_inst_fullcat(inst_fullcat)
            inst_subclass = mgr_inst_dst.get_inst_subclass(inst_cat)
            inst_fullcat_code = inst_subclass.inst_fullcat_to_code(inst_fullcat=inst_fullcat)
            text += f"{text_tab}# {instrument_model_category} {inst_fullcat}\n"
            if quote_name:
                entete_inst_fullcat = f"'{inst_fullcat_code}'{entete_symb}" + "{"
            else:
                entete_inst_fullcat = f"{inst_fullcat_code}{entete_symb}" + "{"
            text += f"{text_tab}{entete_inst_fullcat}"
            extra_tab = spacestring_like(entete_inst_fullcat)
            first_instrument_name = True
            for inst_name in self[inst_fullcat]:
                entete_inst_name = f"'{inst_name}': " + "{"
                if first_instrument_name:
                    text += entete_inst_name
                    first_instrument_name = False
                else:
                    text += text_tab + extra_tab + entete_inst_name
                extra_tab2 = spacestring_like(entete_inst_name)
                texttab_1tline = False
                for inst_model in self[inst_fullcat][inst_name].values():
                    text += inst_model.get_paramfile_section(text_tab=text_tab + extra_tab + extra_tab2,
                                                             texttab_1tline=texttab_1tline,
                                                             entete_symb=": ",
                                                             quote_name=True)
                    texttab_1tline = True
                    text += ",\n"
                text_instmod4dataset = ""
                for datasetname in model_instance.dataset_db.get_datasetnames(inst_name=inst_name, inst_fullcat=inst_fullcat):
                    number = mgr_inst_dst.interpret_data_filename(datasetname)["number"]
                    model_name = model_instance.instmodel4dataset[datasetname]
                    text_instmod4dataset += "{}: '{}', ".format(number, model_name)
                text += (f"{text_tab + extra_tab + extra_tab2}'{string4datasetdico}': {{{text_instmod4dataset}}},"
                         )
                if hasattr(inst_subclass, "_get_inst_paramfilesection"):
                    text += "\n\n"
                    func = getattr(inst_subclass, "_get_inst_paramfilesection")
                    text += func(text_tab=text_tab + extra_tab + extra_tab2, model_instance=model_instance,
                                 inst_name=inst_name)
                text += f"\n{text_tab + extra_tab + extra_tab2}}},\n"
            if hasattr(inst_subclass, "_get_instcat_paramfilesection"):
                func = getattr(inst_subclass, "_get_instcat_paramfilesection")
                text += func(text_tab=text_tab + extra_tab, model_instance=model_instance)
            text += f"\n{text_tab + extra_tab}" + "}\n\n"
        return text

    def update_paramfile_info(self, inst_db_info):
        """Update the paramfile_info for an instrument category.

        It updates things introduced by get_instcat_paramfilesection in paramfile_info.

        Arguments
        ---------
        inst_db_info: dictionary
            This is a subset of the self.paramfile_info (self.paramfile_info[instmod_cat]) of the model
            instance (instance of a subclass of Core_Model) which is filled by this function.
            self.paramfile_info is defined in Core_ParamContainer. It's a dictionary which describes the
            expected content of the parameter file.
        """
        for inst_fullcat in self.inst_fullcategories:
            inst_cat, inst_subcat = mgr_inst_dst.interpret_inst_fullcat(inst_fullcat)
            inst_subclass = mgr_inst_dst.get_inst_subclass(inst_cat)
            inst_db_info[inst_fullcat] = {}
            inst_db_info[inst_fullcat][key_inst] = {}
            inst_db_info[inst_fullcat][key_misc] = []
            for inst_name in self[inst_fullcat]:
                inst_db_info[inst_fullcat][key_inst][inst_name] = []
                for inst_model in self[inst_fullcat][inst_name].keys():
                    inst_db_info[inst_fullcat][key_inst][inst_name].append(inst_model)
                    self[inst_fullcat][inst_name][inst_model].update_paramfile_info()
                inst_db_info[inst_fullcat][key_inst][inst_name].append(string4datasetdico)
                if hasattr(inst_subclass, "_update_inst_paramfile_info"):
                    func = getattr(inst_subclass, "_update_inst_paramfile_info")
                    func(inst_db_info[inst_fullcat][key_inst][inst_name])
            if hasattr(inst_subclass, "_update_instcat_paramfile_info"):
                func = getattr(inst_subclass, "_update_instcat_paramfile_info")
                func(inst_db_info[inst_fullcat][key_misc])

    def load_config(self, dico_config, inst_db_info, model_instance, available_joint_priors={}):
        """Update the paramfile_info for an instrument category.

        It updates things introduced by get_allinst_paramfilesection in paramfile_info.
        """
        logger.debug("Categories of instruments in the param_file_info: {}"
                     "".format(list(inst_db_info.keys())))
        for inst_fullcat in inst_db_info.keys():
            inst_cat, inst_subcat = mgr_inst_dst.interpret_inst_fullcat(inst_fullcat)
            inst_subclass = mgr_inst_dst.get_inst_subclass(inst_cat)
            inst_fullcat_code = inst_subclass.inst_fullcat_to_code(inst_fullcat=inst_fullcat)
            logger.debug("Content of param_file_info for {} {}: {}"
                         "".format(instrument_model_category, inst_fullcat,
                                   inst_db_info[inst_fullcat]))
            for inst_name in inst_db_info[inst_fullcat][key_inst].keys():
                logger.debug("Content of param_file_info for {} {}: {}"
                             "".format(instrument_model_category, inst_name,
                                       inst_db_info[inst_fullcat][key_inst][inst_name]))
                logger.debug("Content of dico_config for {} {}: {}"
                             "".format(instrument_model_category, inst_name,
                                       dico_config[inst_fullcat_code][inst_name]))
                # Load config of instrument models
                set_paramfile_info = set(inst_db_info[inst_fullcat][key_inst][inst_name])
                set_dico_config = set(dico_config[inst_fullcat_code][inst_name].keys())
                instcat_hasspecifickeys = False
                if hasattr(inst_subclass, "_load_config_listspecifickeys_inst"):
                    fun = getattr(inst_subclass, "_load_config_listspecifickeys_inst")
                    listspecifickeys = fun()
                    instcat_hasspecifickeys = True
                for set_obj in [set_paramfile_info, set_dico_config]:
                    set_obj.remove(string4datasetdico)
                    if instcat_hasspecifickeys:
                        for key in listspecifickeys:
                            set_obj.remove(key)
                logger.debug("Set of inst model before the loading: {}\n"
                             "Set of inst model in the paramfile: {}".format(set_paramfile_info,
                                                                             set_dico_config))
                # Load config of already existing instrument model
                for inst_model in (set_paramfile_info & set_dico_config):
                    logger.debug("Instmodel to be updated: {}".format(inst_model))
                    paramcont_dico = dico_config[inst_fullcat_code][inst_name][inst_model]
                    self[inst_fullcat][inst_name][inst_model].load_config(dico_config=paramcont_dico,
                                                                          model_instance=model_instance,
                                                                          available_joint_priors=available_joint_priors)
                # Remove instrument model that are not in the param_file anymore
                for inst_model in (set_paramfile_info.difference(set_dico_config)):
                    logger.debug("Instmodel to be suppressed: {}".format(inst_model))
                    model_instance.rm_an_instrument_model(inst_model=inst_model, inst_name=inst_name,
                                                          inst_fullcat=inst_fullcat)
                    model_instance.update_paramfile_info()
                # Add instrument model are in the param_file but not yet in the model
                for inst_model in (set_dico_config.difference(set_paramfile_info)):
                    logger.debug("Instmodel to be added: {}".format(inst_model))
                    paramcont_dico = dico_config[inst_fullcat_code][inst_name][inst_model]
                    instrument = mgr_inst_dst.get_instrument(inst_name)
                    model_instance.add_an_instrument_model(instrument=instrument, name=inst_model)
                    model_instance.update_paramfile_info()
                    self[inst_fullcat][inst_name][inst_model].load_config(dico_config=paramcont_dico,
                                                                          model_instance=model_instance,
                                                                          available_joint_priors=available_joint_priors)
                # Load which instrument model to use for which dataset
                for dataset in model_instance.dataset_db.get_datasetnames(inst_name=inst_name, inst_fullcat=inst_fullcat):
                    number = mgr_inst_dst.interpret_data_filename(dataset)["number"]
                    inst_model = dico_config[inst_fullcat_code][inst_name][string4datasetdico][number]
                    if model_instance.instmodel4dataset[dataset] != inst_model:
                        logger.debug("Instrument model to use for dataset {} changed from "
                                     "{} to {}.".format(dataset,
                                                        model_instance.instmodel4dataset[dataset],
                                                        inst_model))
                        model_instance.instmodel4dataset[dataset] = inst_model
                # Load specific keys of the instrument category
                if instcat_hasspecifickeys:
                    inst_subclass._load_config_specifickeys_inst(dico_config[inst_fullcat_code][inst_name],
                                                                 inst_name=inst_name,
                                                                 model_instance=model_instance)
            if len(inst_db_info[inst_fullcat][key_misc]) > 0:
                inst_subclass._load_config_instcat(dico_config_fullcat=dico_config[inst_fullcat_code],
                                                   model_instance=model_instance)
