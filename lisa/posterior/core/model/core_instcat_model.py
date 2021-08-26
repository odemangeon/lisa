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

from ..dataset_and_instrument.indicator import IND_inst_cat
from ....tools.metaclasses import MandatoryReadOnlyAttrAndMethod
from ....tools.miscellaneous import spacestring_like


class Core_InstCat_Model(metaclass=MandatoryReadOnlyAttrAndMethod):

    __mandatorymeths__ = ["datasim_creator", "create_instcat_paramfile", "load_instcat_paramfile"]
    # datasim_creator: Methods that creates the datasimulator functions
    # create_instcat_paramfile: Methods to create the param file specific to the instrument category
    #   This methods needs to be defined even if there is no specific instcat_paramfile.
    #   Just make a function that raises an error
    # load_instcat_paramfile: Methods to load the param file specific to the instrument category
    #   This methods needs to be defined even if there is no specific instcat_paramfile.
    #   Just make a function that raises an error
    __mandatoryattrs__ = ["inst_cat", "has_instcat_paramfile", "datasim_creator_name", "decorrelation_models"]
    # inst_cat: string specifiying the instrument category that the InstCat_Model will handle
    # has_instcat_paramfile: bool that says if there is an instcat specific param_file
    # datasim_creator_name: str giving the name of the datasim creator function.
    #   If the same name is used for several inst_cat then the Model will use the same datasimcreator method
    #   for several inst_cat meaning that the datasim_creator function needs to handle them all.
    # decorrelation_models: list of Decorrelation_Model classes implemented for the InstCat_Model

    _decorr_dict_name = 'decorrelation'

    __decorrelation_config = {}

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
        """
        return self.__decorrelation_config

    def do_decorrelate_instmod(self, inst_mod_obj):
        """Indicate if the user activated the decorrelation (do = True) in the param_file for a given instrument model.
        """
        if self.decorrelate_available:
            return self.decorrelation_config[self.inst_cat][inst_mod_obj.full_name]['do']
        else:
            return False

    def create_text_paramfile_decorrelation(self):
        """Return the text to be written in any inst_cat specific param_file for to choose the decorrelation models
        for each dataset.

        This function should be used in create_instcat_paramfile to create the text for the configuration
        of the decorrelation models.

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
        # The list of Indicator instrument model names available are:
        # {list_IND_instmod_names}
        #
        # The format of decorrelation_model_options dictionary depends on the decorrelation model used
        {format_decorr_options}
        {decorr_dict_name} = {{{decor_dict_content}
        {tab_decorr_dict}}}
        """
        text_decorrelation = dedent(text_decorrelation)
        tab_decorr_dict = spacestring_like(f"{self._decorr_dict_name} =  ")
        # Get the list of available indicator instrument model name
        list_IND_instmod_names = [instmod_obj.get_name(include_prefix=True, code_version=True, recursive=True)
                                  for instmod_obj in self.get_instmodel_objs()
                                  if instmod_obj.instrument.category == IND_inst_cat]
        # Create the text for the format of the decorrelation options dictionary for each decorrelation model
        text_format_decorr_options = ""
        for decorr_model in self.decorrelation_models:
            text_format_decorr_options += f"# {decorr_model.category}: {decorr_model.format_config_dict}\n"
        # Create the text for the default content of the decorrelation dictionary
        text_decorr_dict = ""
        for instmod_obj in self.get_instmodel_objs(inst_fullcat=self.__inst_cat__):
            instmodel_name = instmod_obj.get_name(include_prefix=True, code_version=True, recursive=True)
            template_instmodel_dict = "{tab}'{instmodel_name}': {{'do': {instmod_decorr_do},\n{tab_decorr_dict}{tab_instmodel_name}{instmod_decorr_models}\n{tab_decorr_dict}{tab_instmodel_name}}}\n"
            tab_pre_instmodel_name = "" if len(text_decorr_dict) == 0 else tab_decorr_dict
            tab_instmodel_name = spacestring_like(f"'{instmodel_name}':  ")
            text_instmod_decorr_models_content = ""
            for decorr_model_name in self.available_decorrelationmodel_names:
                decorr_model_dict = self.decorrelation_config.get(self.inst_cat, {}).get(instmodel_name, {}).get(decorr_model_name, {})
                text_instmod_decorr_models_content += f"'{decorr_model_name}': {decorr_model_dict},"
            do = self.decorrelation_config.get(self.inst_cat, {}).get(instmodel_name, {}).get('do', False)
            text_decorr_dict += template_instmodel_dict.format(tab=tab_pre_instmodel_name, instmodel_name=instmodel_name,
                                                               instmod_decorr_do=do,
                                                               instmod_decorr_models=text_instmod_decorr_models_content,
                                                               tab_decorr_dict=tab_decorr_dict, tab_instmodel_name=tab_instmodel_name)
        return text_decorrelation.format(decorr_dict_name=self._decorr_dict_name,
                                         list_IND_instmod_names=list_IND_instmod_names,
                                         format_decorr_options=text_format_decorr_options,
                                         decor_dict_content=text_decorr_dict, tab_decorr_dict=tab_decorr_dict)

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
        decorr_dict = dico_config.get(self._decorr_dict_name, {})
        self.decorrelation_config[self.inst_cat] = decorr_dict
