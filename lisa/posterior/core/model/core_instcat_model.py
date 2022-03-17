#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
core_instcat_model module.

The objective of this package is to provides the core Core_InstCat_Model class.
It is a Parent meant to be subclassed and which defines what the subclasses needs to implement.
These subclasses will be used as interface classes for a Core_Model subclass to provide the necessary
methods and attributes to model a data of a given insttument category.

@DONE:
    -

@TODO:
    - __available_decorrelation_quantities__ = ["raw", "residuals", "model"]. This choice will have to
    be made indicator by indicator
    - The load_config_decorrelation
"""
from textwrap import dedent
from collections import Iterable

from ..dataset_and_instrument.indicator import IND_inst_cat
from ....tools.metaclasses import MandatoryReadOnlyAttrAndMethod
from ....tools.miscellaneous import spacestring_like
from ..dataset_and_instrument.manager_dataset_instrument import Manager_Inst_Dataset


mgr_inst_dst = Manager_Inst_Dataset()
mgr_inst_dst.load_setup()


class Core_InstCat_Model(metaclass=MandatoryReadOnlyAttrAndMethod):

    __mandatorymeths__ = ["datasim_creator", "create_instcat_paramfile", "load_instcat_paramfile"]
    # datasim_creator: Methods that creates the datasimulator functions
    #   The inputs of this method need to be (inst_models, datasets=None)
    # create_instcat_paramfile: Methods to create the param file specific to the instrument category
    #   This methods needs to be defined even if there is no specific instcat_paramfile.
    #   Just make a function that raises an error
    # load_instcat_paramfile: Methods to load the param file specific to the instrument category
    #   This methods needs to be defined even if there is no specific instcat_paramfile.
    #   This function needs to have a model_instance argument
    #   Just make a function that raises an error
    __mandatoryattrs__ = ["inst_cat", "has_instcat_paramfile", "default_paramfile_path",
                          "datasim_creator_name", "decorrelation_models"]
    # inst_cat: string specifiying the instrument category that the InstCat_Model will handle
    # has_instcat_paramfile: bool that says if there is an instcat specific param_file
    # default_paramfile_path: Default name for the parameter file of the instrument category
    #   If no param file put None
    # datasim_creator_name: str giving the name of the datasim creator function.
    #   If the same name is used for several inst_cat then the Model will use the same datasimcreator method
    #   for several inst_cat meaning that the datasim_creator function needs to handle them all.
    # decorrelation_models: list of Decorrelation_Model classes implemented for the InstCat_Model

    _decorr_dict_name = 'decorrelation'

    __decorrelation_config = {}

    def __init__(self, model_instance):
        self.__model_instance = model_instance
        if self.has_instcat_paramfile:
            self.paramfile_instcat = None

    @property
    def model_instance(self):
        """Return True is the param_file of the instrument category has been defined."""
        return self.__model_instance

    @property
    def isdefined_paramfile_instcat(self):
        """Return True is the param_file of the instrument category has been defined."""
        return self.paramfile_instcat is not None

    @property
    def available_decorrelationmodel_names(self):
        """Return the list of available decorrelation model name
        """
        return [Decor_Model.category for Decor_Model in self.decorrelation_models]

    @property
    def decorrelate_available(self):
        """Indicate if any type of decorrelation model is available for this instrument category.
        """
        return len(self.decorrelation_models) > 0

    @property
    def decorrelation_config(self):
        """Dictionary which stores the content of the decorrelation configuration set in all the param_files.

        The structure of this dictionary is:
         1. key: Instrument model full name
            value: Dict
            2. key0: do
               value0: bool, say if the decorelation should be performed
               Keyn: decorrelation model name
               valuen: dict, parameters of the decorrelation model
        """
        return self.__decorrelation_config

    def do_decorrelate_instmod(self, inst_mod_obj):
        """Indicate if the user activated the decorrelation (do = True) in the param_file for a given instrument model.
        """
        if self.decorrelate_available:
            return self.decorrelation_config[inst_mod_obj.full_name]['do']
        else:
            return False

    def get_DecorrModel(self, decorrmodel_cat):
        """Return the Core_DecorrelationModel subclass whose category is decorrmodel_cat

        Arguments
        ---------
        decorrmodel_cat : str
            Category of the decorration model that you are looking for

        Returns
        -------
        DecorModel  : Core_DecorrelationModel
            Core_DecorrelationModel subclass whose category is decorrmodel_cat
        """
        for DecorModel in self.decorrelation_models:
            if decorrmodel_cat == DecorModel.category:
                return DecorModel
        raise ValueError(f"Decorrelation model of category {decorrmodel_cat} not found in InstCat_Model {self.inst_cat}")

    def create_text_paramfile_decorrelation(self, model_instance):
        """Return the text to be written in any inst_cat specific param_file for to choose the decorrelation models
        for each dataset.

        This function should be used in create_instcat_paramfile to create the text for the configuration
        of the decorrelation models.

        Arguments
        ---------
        model_instance  : Model instance

        Returns
        -------
        text_paramfile  : str
            Text to put in the inst_cat specific param_file for the general configuration of the decorrelation
        """
        text_decorrelation = """
        # Decorrelation
        #
        # Define if you want to include decorrelation models.
        # In the dictionary below, each key corresponds to an instrument model and has for value a dictionary with the following structure:
        # {{"do": True/False,
        #  "<decorrelation_model_name>": {{"<Indicator instrument model name>": {{decorrelation_model_options}},  ...}}
        # If "do" is False no decorrelation is performed for the data taken with the instrument model.
        # Otherwise, for each available decorrelation model you need to provide the name of the instrument
        # model of the indicators that you want to use and the options for the decorrelation method
        #
        # The list of datasets for each LC instrument model are:
        # {dict_listdatasetname4LCinstmod}
        #
        # The list of datasets for each IND instrument model are:
        # {dict_listdatasetname4INDinstmod}
        #
        # The format of decorrelation_model_options dictionary depends on the decorrelation model used
        {format_decorr_options}
        {decorr_dict_name} = {{{decor_dict_content}
        {tab_decorr_dict}}}
        """
        text_decorrelation = dedent(text_decorrelation)
        tab_decorr_dict = spacestring_like(f"{self._decorr_dict_name} =  ")
        # Get the list of available indicator instrument model name
        list_IND_instmod_names = [instmod_obj.get_name(include_prefix=True, code_version=False, recursive=True)
                                  for instmod_obj in model_instance.get_instmodel_objs()
                                  if instmod_obj.instrument.category == IND_inst_cat]
        # Get the list of datasets for each IND instrument model are:
        dict_listdatasetname4INDinstmod = {}
        for IND_instmod_fullname in list_IND_instmod_names:
            dict_listdatasetname4INDinstmod[IND_instmod_fullname] = self.model_instance.get_ldatasetname4instmodfullname(instmod_fullname=IND_instmod_fullname)
        # Get list of LC inst model full name
        l_LC_instmod = model_instance.get_instmodel_objs(inst_fullcat=self.__inst_cat__)
        # Get the list of datasets for each LC instrument model are:
        dict_listdatasetname4LCinstmod = {}
        for LC_instmod in l_LC_instmod:
            dict_listdatasetname4LCinstmod[LC_instmod.full_name] = self.model_instance.get_ldatasetname4instmodfullname(instmod_fullname=LC_instmod.full_name)
        # Create the text for the format of the decorrelation options dictionary for each decorrelation model
        text_format_decorr_options = ""
        for decorr_model in self.decorrelation_models:
            text_format_decorr_options += f"# {decorr_model.category}: {decorr_model.format_config_dict}\n"
        # Create the text for the default content of the decorrelation dictionary
        text_decorr_dict = ""
        for instmod_obj in l_LC_instmod:
            instmodel_name = instmod_obj.get_name(include_prefix=True, code_version=True, recursive=True)
            template_instmodel_dict = "{tab}'{instmodel_name}': {{'do': {instmod_decorr_do},\n{tab_decorr_dict}{tab_instmodel_name}{instmod_decorr_models}\n{tab_decorr_dict}{tab_instmodel_name}}},\n"
            tab_pre_instmodel_name = "" if len(text_decorr_dict) == 0 else tab_decorr_dict
            tab_instmodel_name = spacestring_like(f"'{instmodel_name}':  ")
            text_instmod_decorr_models_content = self.create_text4paramfile_decorrmodels(instmod_obj=instmod_obj, tab=tab_decorr_dict + tab_instmodel_name)
            do = self.decorrelation_config.get(instmodel_name, {}).get('do', False)
            text_decorr_dict += template_instmodel_dict.format(tab=tab_pre_instmodel_name, instmodel_name=instmodel_name,
                                                               instmod_decorr_do=do,
                                                               instmod_decorr_models=text_instmod_decorr_models_content,
                                                               tab_decorr_dict=tab_decorr_dict, tab_instmodel_name=tab_instmodel_name)
        return text_decorrelation.format(decorr_dict_name=self._decorr_dict_name,
                                         dict_listdatasetname4LCinstmod=dict_listdatasetname4LCinstmod,
                                         dict_listdatasetname4INDinstmod=dict_listdatasetname4INDinstmod,
                                         format_decorr_options=text_format_decorr_options,
                                         decor_dict_content=text_decorr_dict, tab_decorr_dict=tab_decorr_dict)

    def create_text4paramfile_decorrmodels(self, instmod_obj, tab):
        """This function creates the text for the decorrelation of an instrument model object.

        Arguments
        ---------
        instmod_obj : Instrument_Model instance
            Instrument model object for which you want to create the text to configure the decorrelation
        tab         : str
            White spaces giving the tabulation to use

        Returns
        -------
        text_instmod_decorr_models_content  : str
            Text to configure the decorrelation for instmod_obj
        """
        text_instmod_decorr_models_content = ""
        for decorr_model_name in self.available_decorrelationmodel_names:
            decorr_model = self.get_DecorrModel(decorrmodel_cat=decorr_model_name)
            decorr_model_current_config_dict = self.decorrelation_config.get(instmod_obj.full_name, {}).get(decorr_model_name, {})
            text_instmod_decorr_models_content += decorr_model.create_text_decorr_paramfile(inst_mod_obj=instmod_obj,
                                                                                            decorrelation_config_inst=decorr_model_current_config_dict,
                                                                                            tab=tab)
            text_instmod_decorr_models_content += ",\n"
        return text_instmod_decorr_models_content

    def load_config_decorrelation(self, dico_config):
        """Load the dict in any inst_cat specific param_file about to choosen the decorrelation models
        for each dataset.

        This function should be used in load_instcat_paramfile to load the configuration of the decorrelation
        models.

        Arguments
        ---------
        dico_config : dict
            Dictionary which contain the content of the inst_cat specific param_file
        """
        # TODO: Check that the decorrelation dictionary has on entry per instrument model object of
        # the current instrument category
        for instmod_obj_name, decorr_dict_instmod in dico_config.get(self._decorr_dict_name, {}).items():
            instmod_name_info = mgr_inst_dst.interpret_instmod_fullname(instmod_fullname=instmod_obj_name, raise_error=True)
            instmod_obj = self.model_instance.get_instmodel_objs(inst_fullcat=instmod_name_info["inst_fullcategory"],
                                                                 inst_model=instmod_name_info["inst_model"],
                                                                 inst_name=instmod_name_info["inst_name"])[0]
            # Check that the dictionary of each instrument model object has a "do" key
            assert "do" in decorr_dict_instmod.keys()
            if instmod_obj_name not in self.decorrelation_config:
                self.decorrelation_config[instmod_obj_name] = {}
            self.decorrelation_config[instmod_obj_name]["do"] = decorr_dict_instmod["do"]
            for decorr_mod in self.decorrelation_models:
                # Check that the dictionary of each instrument model object has a key for each decorrelation models
                assert decorr_mod.category in decorr_dict_instmod.keys()
                decorr_dict_instmod_decorrmod = decorr_dict_instmod[decorr_mod.category]
                if decorr_mod.category not in self.decorrelation_config[instmod_obj_name]:
                    self.decorrelation_config[instmod_obj_name][decorr_mod.category] = {}
                decorr_mod.load_text_decorr_paramfile(inst_mod_obj=instmod_obj,
                                                      decorrelation_config_inst_decorr_paramfile=decorr_dict_instmod_decorrmod,
                                                      decorrelation_config_inst_decorr=self.decorrelation_config[instmod_obj_name][decorr_mod.category],
                                                      allowed_what2decorrelate_strs=self.allowed_what2decorrelate_strs
                                                      )

    def create_text_decorr(self, multi, inst_mod_obj, idx_inst_mod_obj, l_dataset_name_instmod, dataset_db,
                           decorrelation_config_instmod, time_arg_name, function_builder, function_shortname,
                           model_part=""):
        """Create the text for the decorrelation to be used for the creation of the datasimulators

        To be used in the datasimulator functions for the decorrelation.

        This function has to produce the decorrelation_model text for a given part of the model with one
        intrument model.
        This text should include several decorrelation variables and several decorrelation types
        (e.g. linear) if there are several.

        To do that, this function calls the get_decorrelated_model method of the decorrelation models

        Arguments
        ---------
        multi                           : bool
            If True the datasimulator being created is simulating multiple instruments and/or datasets
            and the time is a list of time arrays. Otherwise only one instrument/dataset is simulated
            and time is time array.
        inst_mod_obj                    : Instrument_Model instance
            Instrument model object to which you want to apply the decorrelation model
        idx_inst_mod_obj                : int
            Index of the instrument model object (inst_mod_obj) in the list of instrument model object
            simulated by the datasimulator function. This is use when multi is True to know what is the
            index of the corresponding time array in the list of time arrays.
        l_dataset_name_inst_mod         : List of dataset names (list of strings)
            Dataset being simulated for the instrument model (inst_mod_obj)
        dataset_db                      : DatasetDatabase
            Dataset database to access the dataset for the decorrelation.
        decorrelation_config_instmod    : dict
            Dictionary providing the decorrelation configuration for the instrument model inst_mod_obj
            and a model part
            Format:
                - keyn: dict providing the parameters for the decorrelation model
        time_arg_name                   : str
            Str used to designate the time vector(s)
        function_builder        : FunctionBuilder
            Function builder instance
        function_shortname      : str
            Short name of the function for which you want to add the decorrelation model
        model_part                      : str
            String giving the model part concerned

        Returns
        -------
        text_decorr : str
        """
        l_decorr_model_name = list(decorrelation_config_instmod.keys())
        text_decorr = ""
        for decorrmodel_cat in l_decorr_model_name:
            DecorModel = self.get_DecorrModel(decorrmodel_cat=decorrmodel_cat)
            text_decorr += DecorModel.get_text_decorrelation(multi=multi, inst_mod_obj=inst_mod_obj, idx_inst_mod_obj=idx_inst_mod_obj,
                                                             l_dataset_name_inst_mod=l_dataset_name_instmod,
                                                             dataset_db=dataset_db, decorrelation_config=decorrelation_config_instmod[decorrmodel_cat],
                                                             time_arg_name=time_arg_name, function_builder=function_builder,
                                                             function_shortname=function_shortname, model_part=model_part)
        return text_decorr

    def get_l_instmod(self, inst_model=None, inst_name=None, sortby_instname=False, sortby_instmodel=False):
        """Return the list of instrument model object for the instrument category
        """
        return self.model_instance.get_instmodel_objs(inst_model=inst_model, inst_name=inst_name, inst_fullcat=self.inst_cat,
                                                      sortby_instfullcat=False, sortby_instname=sortby_instname, sortby_instmodel=sortby_instmodel,
                                                      )

    def get_l_instmod_full_name(self, inst_model=None, inst_name=None, sortby_instname=False, sortby_instmodel=False):
        """Return the list of instrument model full name for the instrument category
        """
        return [inst_mod.full_name for inst_mod in self.get_l_instmod(inst_model=inst_model, inst_name=inst_name,
                                                                      sortby_instname=sortby_instname,
                                                                      sortby_instmodel=sortby_instmodel
                                                                      )
                ]

    def get_l_datasetname(self, instmod_fullnames=None):
        """Return the list of dataset names for a given instrument model
        """
        format_not_recognised = False
        if instmod_fullnames is None:
            instmod_fullnames = self.get_l_instmod_full_name()
        elif isinstance(instmod_fullnames, str):
            instmod_fullnames = [instmod_fullnames, ]
        elif isinstance(instmod_fullnames, Iterable):
            if not(all([isinstance(instmod_fullname, str) for instmod_fullname in instmod_fullnames])):
                format_not_recognised = True
        else:
            format_not_recognised = True
        if format_not_recognised:
            raise ValueError("instmod_fullnames should be a str, an interable of str or None")
        res = []
        for instmod_fullname in instmod_fullnames:
            if instmod_fullname not in self.get_l_instmod_full_name():
                raise ValueError(f"{instmod_fullname} is not the full name of an existing instrument model of category {self.inst_cat}")
            else:
                res.extend(self.model_instance.get_ldatasetname4instmodfullname(instmod_fullname=instmod_fullname))
        return res
