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
from os import getcwd, chdir
from logging import getLogger
from pprint import pformat
from os.path import basename


from .core_decorrelation_model import Core_DecorrelationModel
from ..likelihood.core_decorrelation_likelihood import Core_DecorrelationLikelihood
from ..dataset_and_instrument.indicator import IND_inst_cat
from ..dataset_and_instrument.manager_dataset_instrument import Manager_Inst_Dataset
from ....tools.metaclasses import MandatoryReadOnlyAttrAndMethod
from ....tools.miscellaneous import spacestring_like


mgr_inst_dst = Manager_Inst_Dataset()
mgr_inst_dst.load_setup()


## Logger object
logger = getLogger()


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
    __mandatoryattrs__ = ["inst_cat", "has_instcat_paramfile", "default_paramfile_name",
                          "datasim_creator_name", "l_decorrelation_class"]
    # inst_cat: string specifiying the instrument category that the InstCat_Model will handle
    # has_instcat_paramfile: bool that says if there is an instcat specific param_file
    # default_paramfile_path: Default name for the parameter file of the instrument category
    #   If no param file put None
    # datasim_creator_name: str giving the name of the datasim creator function.
    #   If the same name is used for several inst_cat then the Model will use the same datasimcreator method
    #   for several inst_cat meaning that the datasim_creator function needs to handle them all.
    # decorrelation_models: list of Decorrelation_Model classes implemented for the InstCat_Model

    _decorr_model_dict_name = 'decorrelation_model'

    _decorr_likelihood_dict_name = 'decorrelation_likelihood'

    def __init__(self, model_instance):
        self.__model_instance = model_instance
        if self.has_instcat_paramfile:
            self.paramfile_instcat = None
        if self.decorrelation_model_available:
            self.__decorrelation_model_config = {}
            self._init_decorrelation_model_config()
        if self.decorrelation_likelihood_available:
            self.__decorrelation_likelihood_config = {}
            self._init_decorrelation_likelihood_config()

    @property
    def model_instance(self):
        """Return True is the param_file of the instrument category has been defined."""
        return self.__model_instance

    @property
    def isdefined_paramfile_instcat(self):
        """Return True is the param_file of the instrument category has been defined."""
        return self.paramfile_instcat is not None

    @property
    def l_decorrelation_model_class(self):
        """Return True is the param_file of the instrument category has been defined."""
        return [DecorrClass for DecorrClass in self.l_decorrelation_class if issubclass(DecorrClass, Core_DecorrelationModel)]

    @property
    def l_decorrelation_likelihood_class(self):
        """Return True is the param_file of the instrument category has been defined."""
        return [DecorrClass for DecorrClass in self.l_decorrelation_class if issubclass(DecorrClass, Core_DecorrelationLikelihood)]

    @property
    def l_decorrelation_model_category(self):
        """Return the list of available decorrelation model name
        """
        return [Decor_Model.category for Decor_Model in self.l_decorrelation_model_class]

    @property
    def l_decorrelation_likelihood_category(self):
        """Return the list of available decorrelation model name
        """
        return [Decor_Model.category for Decor_Model in self.l_decorrelation_likelihood_class]

    @property
    def decorrelation_model_available(self):
        """Indicate if any type of decorrelation model is available for this instrument category.
        """
        return len(self.l_decorrelation_model_class) > 0

    @property
    def decorrelation_likelihood_available(self):
        """Indicate if any type of decorrelation model is available for this instrument category.
        """
        return len(self.l_decorrelation_likelihood_class) > 0

    @property
    def decorrelation_model_config(self):
        """Dictionary which stores the content of the decorrelation model configuration set in the param_files.

        The structure of this dictionary is:

        """
        return self.__decorrelation_model_config

    @property
    def decorrelation_likelihood_config(self):
        """Dictionary which stores the content of the decorrelation likelihood configuration set in all the param_files.

        The structure of this dictionary is:

        """
        return self.__decorrelation_likelihood_config

    def get_decorrelation_likelihood_class(self, category):
        """
        Argument
        --------
        category    : str
            Category of likelihood decorrelation model

        Return
        ------
        decorr_like_class   : Subclass of Core_DecorrelationLikelihood
        """
        if category in self.l_decorrelation_likelihood_category:
            return self.l_decorrelation_likelihood_class[self.l_decorrelation_likelihood_category.index(category)]
        else:
            raise ValueError(f"{category} is not an available decorrelation model category")

    def _init_decorrelation_model_config(self):
        """
        WARNING: This is overwritten by both LC_InstCat_Model and RV_InstCat_Model. Should there be a default
        implementation ?
        """
        # Get list of inst model full name for the inst cat
        l_instcat_instmod = self.model_instance.get_instmodel_objs(inst_fullcat=self.__inst_cat__)
        for inst_mod_obj in l_instcat_instmod:
            self.decorrelation_model_config[inst_mod_obj.full_name] = {"do": False}
            for decorr_model_cat in self.l_decorrelation_model_category:
                self.decorrelation_model_config[inst_mod_obj.full_name][decorr_model_cat] = {}

    def _init_decorrelation_likelihood_config(self):
        self.decorrelation_likelihood_config.update({"do": False, 'order_models': [], 'model_definitions': {}})

    def do_decorrelate_model_instmod(self, instmod_fullname):
        """Indicate if the user activated the decorrelation (do = True) in the param_file for a given instrument model.
        """
        if self.decorrelation_model_available:
            return self.decorrelation_model_config[instmod_fullname]['do']
        else:
            return False

    @property
    def do_decorrelate_likelihood(self):
        """Indicate if the user activated the decorrelation (do = True) in the instrument category param_file.
        """
        if self.decorrelation_likelihood_available:
            return self.decorrelation_likelihood_config['do']
        else:
            return False

    @property
    def order_models_decorrelate_likelihood(self):
        """Return the list of decorrelation model names used
        """
        return self.decorrelation_likelihood_config['order_models']

    def get_decorrelation_likelihood_model_config(self, model_name):
        """Return the dictionary providing the configuration of the likelihood decorrelation model requested
        """
        if model_name not in self.decorrelation_likelihood_config['model_definitions']:
            raise ValueError(f"There is no likelihood decorrelation model named {model_name}")
        return self.decorrelation_likelihood_config['model_definitions'][model_name]

    def get_decorrelation_likelihood_model_category(self, model_name):
        """Return the category of the likelihood decorrelation model requested
        """
        return self.get_decorrelation_likelihood_model_config(model_name=model_name)['category']

    def get_decorrelation_likelihood_model_datasets(self, model_name):
        """Return the list of the dataset that the likelihood decorrelation model decorrelates (not the indicators datasets)
        """
        return list(self.get_decorrelation_likelihood_model_config(model_name=model_name)['match datasets'].keys())

    def require_model_decorrelation(self, instmod_fullname):
        """True if any of there is the need to do a decorrelation model for the instrument model provided

        WARNING: This is overwritten by both LC_InstCat_Model and RV_InstCat_Model. Should there be a default
        implementation ?

        Argument
        --------
        instmod_fullname    : str
            Intrument model full name

        Return
        ------
        require : bool
            True if the instrument model requires model decorelation
        """
        require = False
        if self.do_decorrelate_model_instmod(instmod_fullname=instmod_fullname):
            dico_decorr_instmod = self.decorrelation_model_config[instmod_fullname].copy()
            dico_decorr_instmod.pop('do')
            for decor_cat, dico_decor_cat_config in dico_decorr_instmod.items():
                if len(dico_decor_cat_config) > 0:
                    require = True
                    break
        return require

    def require_likelihood_decorrelation(self, dataset_name):
        """True if there is the need for a decorrelation likelihood for the dataset

        Argument
        --------
        dataset_name    : str
            Dataset name

        Return
        ------
        require : bool
            True if the dataset requires a likelihood decorelation
        """
        require = False
        if self.do_decorrelate_likelihood:
            for model_name in self.order_models_decorrelate_likelihood:
                if dataset_name in self.get_decorrelation_likelihood_model_datasets(model_name=model_name):
                    require = True
                    break
        return require

    def get_DecorrClass(self, decorrmodel_cat):
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
        for DecorModel in self.l_decorrelation_class:
            if decorrmodel_cat == DecorModel.category:
                return DecorModel
        raise ValueError(f"Decorrelation model of category {decorrmodel_cat} not found in InstCat_Model {self.inst_cat}")

    def create_instcat_paramfile(self, file_path):
        """Create a parameter file for the light-curve parametrisation.

        Arguments
        ---------
        file_path           : string
            Path to the param_file.
        """
        with open(file_path, 'w') as f:
            # Write the header
            f.write("#!/usr/bin/python\n# -*- coding:  utf-8 -*-\n")

            f.write(self.create_text_instcat_paramfile_model(model_instance=self.model_instance))

            if self.decorrelation_model_available or self.decorrelation_likelihood_available:
                f.write(self.create_text_paramfile_decorrelation(model_instance=self.model_instance))

        logger.info(f"Parameter file for LC inst cat created at path: {file_path}")
        self.paramfile_instcat = basename(file_path)

    def create_text_instcat_paramfile_model(self, model_instance):
        """Return the text to be written to parametrise the model for the instrument category

        This function is called create_instcat_paramfile to create the text for the configuration
        of the models.

        You need to overwrite it in the child class if you want it to actually do something.

        Arguments
        ---------
        model_instance  : Model instance

        Returns
        -------
        text_paramfile  : str
            Text to put in the inst_cat specific param_file for the general configuration of the model
        """
        return ""

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
        # {dict_listdatasetname4instcatinstmod}
        #
        # The list of datasets for each IND instrument model are:
        # {dict_listdatasetname4INDinstmod}
        #
        # The format of decorrelation_model_options dictionary depends on the decorrelation model used
        {format_decorr_options}
        """
        text_decorrelation = dedent(text_decorrelation)
        # Get the list of available indicator instrument model name
        list_IND_instmod_names = [instmod_obj.get_name(include_prefix=True, code_version=False, recursive=True)
                                  for instmod_obj in model_instance.get_instmodel_objs()
                                  if instmod_obj.instrument.category == IND_inst_cat]
        # Get the list of datasets for each IND instrument model are:
        dict_listdatasetname4INDinstmod = {}
        for IND_instmod_fullname in list_IND_instmod_names:
            dict_listdatasetname4INDinstmod[IND_instmod_fullname] = self.model_instance.get_ldatasetname4instmodfullname(instmod_fullname=IND_instmod_fullname)
        # Get list of inst model full name for the inst cat
        l_instcat_instmod = model_instance.get_instmodel_objs(inst_fullcat=self.__inst_cat__)
        # Get the list of datasets for each LC instrument model are:
        dict_listdatasetname4instcatinstmod = {}
        for LC_instmod in l_instcat_instmod:
            dict_listdatasetname4instcatinstmod[LC_instmod.full_name] = self.model_instance.get_ldatasetname4instmodfullname(instmod_fullname=LC_instmod.full_name)
        # Create the text for the format of the decorrelation model options dictionary for each decorrelation model
        text_format_decorr_options = ""
        for decorr_model in self.l_decorrelation_class:
            text_format_decorr_options += f"# {decorr_model.category}: {decorr_model.format_config_dict}\n"
        # Fill the introduction of the decorrelation text
        text_decorrelation = text_decorrelation.format(dict_listdatasetname4instcatinstmod=dict_listdatasetname4instcatinstmod,
                                                       dict_listdatasetname4INDinstmod=dict_listdatasetname4INDinstmod,
                                                       format_decorr_options=text_format_decorr_options,
                                                       )
        # Define variable for Decorrelation model
        if self.decorrelation_model_available:
            tab_decorr_model_dict = spacestring_like(f"{self._decorr_model_dict_name} = ")
            # template_instmodel_decorr_model_dict = "{tab}'{instmodel_name}': {{'do': {instmod_decorr_do},\n{tab_decorr_dict}{tab_instmodel_name}{instmod_decorr_dict}\n{tab_decorr_dict}{tab_instmodel_name}}},\n"
            decor_model_dict_content = {}
        # Define variable for Decorrelation likelihood
        # if self.decorrelation_likelihood_available:
        #     tab_decorr_likelihood_dict = spacestring_like(f"{self._decorr_likelihood_dict_name} = ")
        #     # template_instmodel_decorr_model_dict = "{tab}'{instmodel_name}': {{'do': {instmod_decorr_do},\n{tab_decorr_dict}{tab_instmodel_name}'order': {order_list}\n{tab_decorr_dict}{tab_instmodel_name}{instmod_decorr_dict}\n{tab_decorr_dict}{tab_instmodel_name}}},\n"
        #     decor_like_dict_content = {'do': False, 'order': [], 'model_definitions': {}}
        # Create the text for the default content of the decorrelation dictionary
        for instmod_obj in l_instcat_instmod:
            instmodel_name = instmod_obj.full_name
            # tab_instmodel_name = spacestring_like(f"'{instmodel_name}':  ")
            # Decorrelation model
            if self.decorrelation_model_available:
                # tab_pre_instmodel_name_decorrmodel_dict = "" if len(decor_model_dict_content) == 0 else tab_decorr_model_dict
                decor_model_dict_content[instmodel_name] = {"do": self.decorrelation_model_config[instmodel_name]['do']}
                decor_model_dict_content[instmodel_name].update(self.get_dicoconfig_decorrelation_model(instmod_obj=instmod_obj))
            # Decorrelation likelihood (With the new format/definition this is no longer needed)
            # if self.decorrelation_likelihood_available:
            #     # tab_pre_instmodel_name_decorrlike_dict = "" if len(decor_like_dict_content) == 0 else tab_decorr_likelihood_dict
            #     decor_like_dict_content[instmodel_name] = {"do": self.decorrelation_likelihood_config[instmodel_name]['do'],
            #                                                "order": self.decorrelation_likelihood_config[instmodel_name]['order']
            #                                                }
            #     decor_like_dict_content[instmodel_name].update(self.get_dicoconfig_decorrelation_likelihood(instmod_obj=instmod_obj))

        if self.decorrelation_model_available:
            text_decor_model_config = pformat(decor_model_dict_content, compact=True)
            text_decor_model_config = text_decor_model_config.replace('\n', '\n' + tab_decorr_model_dict)
            text_decorrelation += f"\n{self._decorr_model_dict_name} = {text_decor_model_config}"  # .replace('\n', '\n' + tab_decorr_model_dict)}
        if self.decorrelation_likelihood_available:
            text_decor_likelihood_config = pformat(self.decorrelation_likelihood_config, compact=True)
            text_decorrelation += f"\n{self._decorr_likelihood_dict_name} = {text_decor_likelihood_config}"  # .replace('\n', '\n' + tab_decorr_likelihood_dict)
        return text_decorrelation

    def get_dicoconfig_decorrelation_model(self, instmod_obj):
        """Returns the dictionary provide the configuration of the model decorrelation of an instrument model object.

        Arguments
        ---------
        instmod_obj : Instrument_Model instance
            Instrument model object for which you want to create the text to configure the decorrelation

        Returns
        -------
        dico_decorr  : dict
        """
        dico_decorr = self.decorrelation_model_config[instmod_obj.full_name].copy()
        dico_decorr.pop("do")
        return dico_decorr

    # The likelihood decorrelation is not defined instrument per instrument anymore.
    # def get_dicoconfig_decorrelation_likelihood(self, instmod_obj):
    #     """Returns the dictionary provide the configuration of the model decorrelation of an instrument model object.
    #
    #     Arguments
    #     ---------
    #     instmod_obj : Instrument_Model instance
    #         Instrument model object for which you want to create the text to configure the decorrelation
    #     tab         : str
    #         White spaces giving the tabulation to use
    #
    #     Returns
    #     -------
    #     text_instmod_decorr_models_content  : str
    #         Text to configure the decorrelation for instmod_obj
    #     """
    #     dico_decorr = self.decorrelation_likelihood_config[instmod_obj.full_name].copy()
    #     dico_decorr.pop("do")
    #     dico_decorr.pop("order")
    #     return dico_decorr

    def load_instcat_paramfile(self):
        """Load LC_param_file."""
        dico_config = self.read_param_file()
        self.load_config(dico_config)
        if self.decorrelation_model_available or self.decorrelation_likelihood_available:
            self.load_config_decorrelations(dico_config)

    def read_param_file(self):
        """Read the content of the inst cat parameter file."""
        if self.isdefined_paramfile_instcat:
            paramfile_instcat = self.paramfile_instcat
            cwd = getcwd()
            chdir(self.model_instance.run_folder)
            with open(paramfile_instcat) as f:
                exec(f.read())
            chdir(cwd)
            dico = locals().copy()
            for var_name in ["self", "cwd", "f", "paramfile_instcat"]:
                dico.pop(var_name)
            logger.debug(f"{self.inst_cat} parameter file read.\nContent of the parameter file: {dico.keys()}")
            return dico
        else:
            raise IOError(f"Impossible to read {self.inst_cat} parameter file: {self.paramfile_instcat} in directory {self.model_instance.run_folder}")

    def load_config(self, dico_config):
        """
        """
        raise NotImplementedError(f"You need to overwrite the load_config method in the children class for instrument category {self.inst_cat} to use a specific parameter file.")

    def load_config_decorrelations(self, dico_config):
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
        self.load_config_decorrelation_model(dico_config=dico_config)
        self.load_config_decorrelation_likelihood(dico_config=dico_config)

    def load_config_decorrelation_model(self, dico_config):
        """
        Arguments
        ---------
        dico_config             :
        """
        for instmod_obj_name, decorr_dict_instmod in dico_config.get(self._decorr_model_dict_name, {}).items():
            instmod_name_info = mgr_inst_dst.interpret_instmod_fullname(instmod_fullname=instmod_obj_name, raise_error=True)
            instmod_obj = self.model_instance.get_instmodel_objs(inst_fullcat=instmod_name_info["inst_fullcategory"],
                                                                 inst_model=instmod_name_info["inst_model"],
                                                                 inst_name=instmod_name_info["inst_name"])[0]
            # Check that the dictionary of each instrument model object has a "do" key
            assert "do" in decorr_dict_instmod.keys()
            if instmod_obj_name not in self.decorrelation_model_config:
                self.decorrelation_model_config[instmod_obj_name] = {}
            self.decorrelation_model_config[instmod_obj_name]["do"] = decorr_dict_instmod["do"]
            for decorr_mod in self.l_decorrelation_model_class:
                # Check that the dictionary of each instrument model object has a key for each decorrelation models
                assert decorr_mod.category in decorr_dict_instmod.keys()
                decorr_dict_instmod_decorrmod = decorr_dict_instmod[decorr_mod.category]
                if decorr_mod.category not in self.decorrelation_model_config[instmod_obj_name]:
                    self.decorrelation_model_config[instmod_obj_name][decorr_mod.category] = {}
                decorr_mod.load_text_decorr_paramfile(inst_mod_obj=instmod_obj,
                                                      decorrelation_config_inst_decorr_paramfile=decorr_dict_instmod_decorrmod,
                                                      decorrelation_config_inst_decorr=self.decorrelation_modelconfig[instmod_obj_name][decorr_mod.category],
                                                      )

    def load_config_decorrelation_likelihood(self, dico_config):
        """
        Arguments
        ---------
        dico_config             :
        """
        # Check if the dictionary specifying the likelihood decorrelation is provided
        if self._decorr_likelihood_dict_name not in dico_config:
            logger.warning("The dictionary specifying the decorrelation likelihood is not provided ! The current configuration is conserved.")
            return None
        dico_config_decorr_like = dico_config[self._decorr_likelihood_dict_name]
        # Check if the dictionary specifying the likelihood decorrelation has the right keys
        set_keys = {'do', 'order_models', 'model_definitions'}
        if set_keys != set(dico_config_decorr_like.keys()):
            raise ValueError(f"If the {self._decorr_likelihood_dict_name} is specified, its keys should be {set_keys}")
        # load the do value
        self.decorrelation_likelihood_config["do"] = dico_config_decorr_like["do"]
        # Check that all models in order_models are specified in model_definitions
        if not(set(dico_config_decorr_like['order_models']).issubset(set(dico_config_decorr_like['model_definitions'].keys()))):
            raise ValueError("All likelihood decorrelation model names in 'order_models' have to be specified in 'model_definitions'")
        # Init the content of order_models and model_definitions
        self.decorrelation_likelihood_config["order_models"] = []
        self.decorrelation_likelihood_config["model_definitions"] = {}
        # Check the definition of each model in order_models:
        for model_name in dico_config_decorr_like['order_models']:
            dico_config_model = dico_config_decorr_like['model_definitions'][model_name]
            # Check the category is a key of the dictionary specifying the model
            if any([key not in dico_config_model.keys() for key in ['category', 'match datasets']]):
                raise ValueError(f"category and 'match datasets' have to be keys of the likelihood decorrelation model definitions (in part. {model_name})")
            # Check that the category is an existing decorelation model category
            if dico_config_model['category'] not in self.l_decorrelation_likelihood_category:
                raise ValueError(f"{dico_config_model['category']} is not an available likelihood decorrelation model category ({self.l_decorrelation_likelihood_category}).")
            # Check the match datasets keys (values depends on the category of likelihood decorrelation)
            for dataset_name in dico_config_model['match datasets'].keys():
                # Check that dataset is the name of an existing dataset and that its cateogry is the current instrument category
                if self.model_instance.dataset_db.isavailable_dataset(dataset=dataset_name):
                    if self.model_instance.dataset_db[dataset_name].instrument.category != self.inst_cat:
                        raise ValueError(f"Decorrelation likelihood model definition {model_name}: Dataset {dataset_name} is not a dataset of a {self.inst_cat} instrument.")
                else:
                    raise ValueError(f"Decorrelation likelihood model definition {model_name}: Dataset {dataset_name} is not an existing dataset.")
            decorr_cat_class = self.get_decorrelation_likelihood_class(category=dico_config_model['category'])
            self.decorrelation_likelihood_config["model_definitions"][model_name] = {}
            decorr_cat_class.load_text_decorr_paramfile(config_model_paramfile=dico_config_model,
                                                        config_model_storage=self.decorrelation_likelihood_config["model_definitions"][model_name],
                                                        )
            self.decorrelation_likelihood_config["order_models"].append(model_name)

        # for instmod_obj_name, decorr_dict_instmod in dico_config.get(self._decorr_likelihood_dict_name, {}).items():
        #     instmod_name_info = mgr_inst_dst.interpret_instmod_fullname(instmod_fullname=instmod_obj_name, raise_error=True)
        #     instmod_obj = self.model_instance.get_instmodel_objs(inst_fullcat=instmod_name_info["inst_fullcategory"],
        #                                                          inst_model=instmod_name_info["inst_model"],
        #                                                          inst_name=instmod_name_info["inst_name"])[0]
        #     if instmod_obj_name not in self.decorrelation_likelihood_config:
        #         self.decorrelation_likelihood_config[instmod_obj_name] = {}
        #     # Check that the dictionary of each instrument model object has a "do" key
        #     assert "do" in decorr_dict_instmod.keys()
        #     self.decorrelation_likelihood_config[instmod_obj_name]["do"] = decorr_dict_instmod["do"]
        #     # Check that the dictionary of each instrument model object has a "order" key
        #     assert "order" in decorr_dict_instmod.keys()
        #     self.decorrelation_likelihood_config[instmod_obj_name]["order"] = decorr_dict_instmod["order"]
        #     # Load configuration for every decorrelation likelihood category
        #     for decorr_mod in self.l_decorrelation_likelihood_class:
        #         # Check that the dictionary of each instrument model object has a key for each decorrelation models
        #         assert decorr_mod.category in decorr_dict_instmod.keys()
        #         decorr_dict_instmod_decorrmod = decorr_dict_instmod[decorr_mod.category]
        #         if decorr_mod.category not in self.decorrelation_likelihood_config[instmod_obj_name]:
        #             self.decorrelation_likelihood_config[instmod_obj_name][decorr_mod.category] = {}
        #         decorr_mod.load_text_decorr_paramfile(inst_mod_obj=instmod_obj,
        #                                               decorrelation_config_inst_decorr_paramfile=decorr_dict_instmod_decorrmod,
        #                                               decorrelation_config_inst_decorr=self.decorrelation_likelihood_config[instmod_obj_name][decorr_mod.category],
        #                                               )

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
            DecorModel = self.get_DecorrClass(decorrmodel_cat=decorrmodel_cat)
            if issubclass(DecorModel, Core_DecorrelationModel) and (len(decorrelation_config_instmod[decorrmodel_cat]) > 0):
                text_decorr += DecorModel.get_text_decorrelation(multi=multi, inst_mod_obj=inst_mod_obj, idx_inst_mod_obj=idx_inst_mod_obj,
                                                                 l_dataset_name_inst_mod=l_dataset_name_instmod,
                                                                 dataset_db=dataset_db, decorrelation_config=decorrelation_config_instmod[decorrmodel_cat],
                                                                 time_arg_name=time_arg_name, function_builder=function_builder,
                                                                 function_shortname=function_shortname, model_part=model_part)
        return text_decorr

    def _get_required_dataset(self, d_required_datasetkwargkeys_4_dataset, d_required_datasetkwargkeys_4_inddataset,
                              dico_decorr_4_instmod, l_dataset_name, instmod_fullname, dataset_name):
        """
        """
        def defdic_decorr_indinst_func():
            return {"l_idx_simdata": [],
                    "l_datasetkwargs_req": [],
                    "l_inddataset_name": [],
                    "l_inddatasetkwargs_req": [],
                    }

        decorr_instmod_dict = self.decorrelation_likelihood_config[instmod_fullname]
        if decorr_instmod_dict["do"]:
            # Check if there is a spline decorrelation
            if len(decorr_instmod_dict['order']) > 0:
                if instmod_fullname not in dico_decorr_4_instmod:
                    dico_decorr_4_instmod[instmod_fullname] = {"l_dataset_name": [], "order": decorr_instmod_dict['order'], "decorr_cat": {}}
                dico_decorr_4_instmod[instmod_fullname]["l_dataset_name"].append(dataset_name)
                for decorr_cat, decorr_name in decorr_instmod_dict['order']:
                    DecorrModel = self.get_DecorrClass(decorrmodel_cat=decorr_cat)
                    (dico_decorr_4_instmod[instmod_fullname]["decorr_cat"],
                     d_required_datasetkwargkeys_4_dataset,
                     d_required_datasetkwargkeys_4_inddataset
                     ) = DecorrModel.get_required_dataset(decorr_config_instmod_decorr_cat=decorr_instmod_dict[decorr_cat],
                                                          dico_decorr_instmod_decorr_cat=dico_decorr_4_instmod[instmod_fullname]["decorr_cat"],
                                                          decorr_name=decorr_name,
                                                          d_required_datasetkwargkeys_4_dataset=d_required_datasetkwargkeys_4_dataset,
                                                          d_required_datasetkwargkeys_4_inddataset=d_required_datasetkwargkeys_4_inddataset,
                                                          l_dataset_name=l_dataset_name
                                                          )
        return d_required_datasetkwargkeys_4_dataset, d_required_datasetkwargkeys_4_inddataset, dico_decorr_4_instmod

    def create_decorrelation_likelihood(self, function_builder, l_function_shortname, inst_model_obj, dico_decorr_instmod,
                                        l_dataset_name, l_paramsfullname_likelihood, dataset_kwargs, inddataset_kwargs,
                                        datasim_has_multioutputs, plot_functionshortname=None):
        """Create the text for the likelihood decorrelation for a given instrument model

        It had the required text in the body of the function and return the text for the decorrelation
        for the different datasets associated with the instrument model.

        Arguments
        ---------
        function_builder            :
        l_function_shortname        :
        inst_model_obj              :
        dico_decorr_instmod         :
        l_dataset_name              :
        l_paramsfullname_likelihood :
        dataset_kwargs              :
        inddataset_kwargs           :
        datasim_has_multioutputs    :
        plot_functionshortname      :

        Return
        ------
        simdata_decorr_4_dataset_4_indinstmod           :
        decorr_body_text_4_decorrcat_4_indinstmod       :
        plotdecorr_body_text_4_decorrcat_4_indinstmod   :
        l_paramsfullname_likelihood                     :
        """
        simdata_decorr_4_dataset_4_decorr_name = {dst_name: {} for dst_name in dico_decorr_instmod["l_dataset_name"]}
        decorr_body_text_4_decorrcat_4_indinstmod = {}
        plotdecorr_body_text_4_decorrcat_4_indinstmod = {}
        for decorr_cat, dico_decorr_cat in dico_decorr_instmod["decorr_cat"].items():
            DecorrClass = self.get_DecorrClass(decorrmodel_cat=decorr_cat)
            if decorr_cat not in decorr_body_text_4_decorrcat_4_indinstmod:
                decorr_body_text_4_decorrcat_4_indinstmod[decorr_cat] = {}
            if decorr_cat not in plotdecorr_body_text_4_decorrcat_4_indinstmod:
                plotdecorr_body_text_4_decorrcat_4_indinstmod[decorr_cat] = {}
            for decorr_name, dico_decorr in dico_decorr_cat.items():
                # indinstmod_obj = self.model_instance.instruments[ind_inst_model_fullname]
                dico_decorr_config = self.decorrelation_likelihood_config[inst_model_obj.full_name][decorr_cat][decorr_name]
                (simdata_decorr_4_dataset_indinstmod,
                 decorr_body_text_4_decorrcat_4_indinstmod[decorr_cat][decorr_name],
                 plotdecorr_body_text_4_decorrcat_4_indinstmod[decorr_cat][decorr_name],
                 l_paramsfullname_likelihood
                 ) = DecorrClass.create_decorrelation_likelihood(function_builder=function_builder,
                                                                 l_function_shortname=l_function_shortname,
                                                                 inst_model_obj=inst_model_obj,
                                                                 decorr_name=decorr_name,
                                                                 dico_decorr=dico_decorr,
                                                                 dico_decorr_config=dico_decorr_config,
                                                                 l_dataset_name_4_instmod=dico_decorr_instmod["l_dataset_name"],
                                                                 l_dataset_name=l_dataset_name,
                                                                 l_paramsfullname_likelihood=l_paramsfullname_likelihood,
                                                                 dataset_kwargs=dataset_kwargs,
                                                                 inddataset_kwargs=inddataset_kwargs,
                                                                 datasim_has_multioutputs=datasim_has_multioutputs,
                                                                 plot_functionshortname=plot_functionshortname)
                for dataset_name, decorrtext_dataset_indinstmod in simdata_decorr_4_dataset_indinstmod.items():
                    simdata_decorr_4_dataset_4_decorr_name[dataset_name][decorr_name] = decorrtext_dataset_indinstmod

        return simdata_decorr_4_dataset_4_decorr_name, decorr_body_text_4_decorrcat_4_indinstmod, plotdecorr_body_text_4_decorrcat_4_indinstmod, l_paramsfullname_likelihood

    def get_l_dataset_obj_4_decorrelation(self, instmod_obj):
        """Return the list of dataset name

        Arguments
        ---------
        instmod_obj : Instrument_Model object

        Returns
        -------
        l_dataset_name  : List of string
        """
        l_dataset_name = []
        decorr_config_instmod = self.decorrelation_likelihood_config[instmod_obj.full_name]
        if decorr_config_instmod['do']:
            for decorr_cat, ind_instmod_fullname in decorr_config_instmod["order"]:
                for dataset_name in decorr_config_instmod[decorr_cat][ind_instmod_fullname]["match datasets"].keys():
                    if dataset_name not in l_dataset_name:
                        l_dataset_name.append(dataset_name)
        return [self.model_instance.dataset_db[dst_name] for dst_name in l_dataset_name]

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
