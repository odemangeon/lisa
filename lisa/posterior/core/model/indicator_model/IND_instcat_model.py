#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Indicator model module.
"""
from logging import getLogger
from textwrap import dedent
from pprint import pformat

from collections.abc import Iterable
from collections import defaultdict

from .datasim_creator_ind import create_datasimulator_IND, template_function_whole_shortname_ind_cat
from .polynomial_model import PolynomialIndicatorModel
from .. import par_vec_name
from ..core_instcat_model import Core_InstCat_Model
from ..datasimulator_toolbox import check_datasets_and_instmodels
from ..datasim_docfunc import DatasimDocFunc
from ... import function_whole_shortname
from ...dataset_and_instrument.indicator import IND_inst_cat, IND_Instrument
from .....tools.miscellaneous import spacestring_like
from .....tools.function_from_text_toolbox import FunctionBuilder


## Logger object
logger = getLogger()

tab = "    "


class IND_InstCat_Model(Core_InstCat_Model):
    """docstring for LC_InstCat_Model, interface class for a subclass of Core_Model."""

    # Mandatory attributes for a sublass of Core_InstCat_Model
    __inst_cat__ = IND_inst_cat
    __datasim_creator_name__ = "sim_IND"
    __l_decorrelation_class__ = []

    # models available for the indicators
    __models_available__ = [PolynomialIndicatorModel, ]  # The first one is the default one

    # # Define the dictionary providing the default parameters values for each model
    # _default_param_values_4_indicator_model = {PolynomialIndicatorInterface._polynomial_method_name: PolynomialIndicatorInterface._default_param_values}

    # # String giving the name of the dictionary used to define the model to use for each indicator in the parameter file
    # __name_model_4_indicator_dict = "model_4_indicator"

    def __init__(self, model_instance, run_folder, config_file):
        super(IND_InstCat_Model, self).__init__(model_instance=model_instance, run_folder=run_folder, config_file=config_file)

        # Define and init the variable that will store whether of not an indicator instrument model is
        # associated to a model
        self.__indinst_model_is_modeled = {}
        for instmod_obj in self.get_l_instmod():
            self.__indinst_model_is_modeled[instmod_obj.full_name] = False

        # Define the dictionary giving the function to use to create the text of the dictionaries to defined the paremeters of each model for the parameter file
        # self.__create_text_indicator_methods = {self._polynomial_method_name: self.__create_text_polynomial_model}
        # # Define the dictionary giving the function to use to load the text of the dictionaries to defined the paremeters of each model for the parameter file
        # self.__load_text_indicator_methods = {self._polynomial_method_name: self.__load_text_polynomial_model}
        #
        # # Define the dictionary giving the name of the dictionary to use in the parameter file in which the parameters of each model are going to be defined
        # self.__dictname_4_model_indicator = {self._polynomial_method_name: self._polynomial_method_name + "_models"}
        #
        # # Define the checker functions for the dictionary use to define each model in the parameter file.
        # self.__checker_4_indicator_model_dict = {self.__dictname_4_model_indicator[self._polynomial_method_name]: self.__check_polynomial_model}
        #
        # # Initialise the dictionary model_4_indicator
        # self.__model_4_indicator = {inst_subcat: self.__available_models_4_indicators__[0] for inst_subcat in self.indicator_subcategories}
        #
        # # Define the dictionary datasimcreator4indmodel
        # self.__datasimcreator4indmodel = {self._polynomial_method_name: self._create_datasimulator_IND_Poly}
        # self.__kwargs_datasimcreator4indmodel = {self._polynomial_method_name: {"polynomial_order_name": self._polynomial_order_name,
        #                                                                         }
        #                                          }  # For each indicator method the dictionary will be passed to the datasim creator function pointed by self.__datasimcreator4indmodel
        # self.__init_indmodel4indmodel = {self._polynomial_method_name: self._init_polynomialind_model}

        # # Initialise the params_indicator_models
        # self.__params_indicator_models = {}
        # for model, l_inst_subcat in self.indicator_subcategories_4_model_used.items():
        #     self.__params_indicator_models[model] = {
        #         inst_subcat: self._default_param_values_4_indicator_model[self.model_4_indicator[inst_subcat]].copy() for inst_subcat in l_inst_subcat}

        # # Check that there is a key for each model in _default_param_values_4_indicator_model
        # TestCase().assertSequenceEqual(list(self._default_param_values_4_indicator_model.keys()), self.__available_models_4_indicators__)
        #
        # # Check that there is a create_text_methods for each model
        # TestCase().assertSequenceEqual(list(self.__create_text_indicator_methods.keys()), self.__available_models_4_indicators__)
        #
        # # Check that there is a load_text_methods for each model
        # TestCase().assertSequenceEqual(list(self.__load_text_indicator_methods.keys()), self.__available_models_4_indicators__)
        #
        # # Check that there is a dictionary name for each model
        # TestCase().assertSequenceEqual(list(self.__dictname_4_model_indicator.keys()), self.__available_models_4_indicators__)
        #
        # # Check that there is a datasim creator for each model
        # TestCase().assertSequenceEqual(list(self.__datasimcreator4indmodel.keys()), self.__available_models_4_indicators__)
        # # Check that there is a kwargs for the datasim creator for each model
        # TestCase().assertSequenceEqual(list(self.__kwargs_datasimcreator4indmodel.keys()), self.__available_models_4_indicators__)
        #
        # # Check that there is a checker for each dictionary of each model
        # TestCase().assertSequenceEqual(list(self.__dictname_4_model_indicator.values()), list(self.__checker_4_indicator_model_dict.keys()))

    # @property
    # def datasimcreator4indmodel(self):
    #     """Dictionary giving the datasim creator function for each model
    #     """
    #     return self.__datasimcreator4indmodel

    @property
    def indinst_model_is_modeled(self):
        """Return all indicator full categories in the current model.
        """
        return self.__indinst_model_is_modeled

    @property
    def indicator_fullcategories(self):
        """Return all indicator full categories in the current model.
        """
        list_indicator_fullcategories = []
        for inst_fullcat in self.model_instance.inst_fullcategories:  # self.instfullcategories is from InstrumentContainerInterface Interface class of Core_Model
            if IND_Instrument.validate_inst_fullcat(inst_fullcat):
                list_indicator_fullcategories.append(inst_fullcat)
        return list_indicator_fullcategories

    @property
    def indicator_subcategories(self):
        """Return all indicator full categories in the current model.
        """
        list_indicator_subcategories = []
        for inst_fullcat in self.indicator_fullcategories:
            inst_cat, inst_subcat = IND_Instrument.interpret_inst_fullcat(inst_fullcat)
            list_indicator_subcategories.append(inst_subcat)
        return list_indicator_subcategories

    @property
    def models_available(self):
        """Return the list indicator model classes available
        """
        return self.__models_available__

    @property
    def name_models_available(self):
        """Return the list indicator model classes available
        """
        return [model.model_name for model in self.__models_available__]

    def get_modelclass_4_modelname(self, model_name):
        """Return the model Class associated with the model name provided
        """
        for model in self.models_available:
            if model.model_name == model_name:
                return model
        raise ValueError(f"{model_name} is not a existing indicator model name")

    def is_valid_indicator_model(self, model_name):
        """Validate a model as an indidator model

        Arguments
        ---------
        model_name : str
            String giving the model that you want to validate

        Returns
        -------
        valid : boolean
            True is model is a valid indicator model, False otherwise
        """
        return model_name in self.name_models_available

    # def __datasim_allindmodels_creator(self, l_datasim, l_params_idx, params_model, mand_kwargs, opt_kwargs,
    #                                    inst_fullcat, inst_model_fullname=None, dataset=None):
    #     """Return the datasimulator for all indicator models
    #
    #     WARNING/TODO eventually: For now *args, **kwargs of the datasim_alldatasets are passed to all the datasim function.
    #     This might not be always desired.
    #
    #     Arguments
    #     ---------
    #     l_datasim           : List of DatasimDocFunc
    #         list of datasimulators
    #     l_params_idx        : List of list of int
    #         List of list of indexes in the param array for each datasim function in l_datasim.
    #     params_model        : List of string
    #         Ordered list of parameters full name for the datasimulator being created
    #     mand_kwargs         : String
    #         String giving the mandatory keyword arguments for the datasimulator being created
    #     opt_kwargs          : String
    #         String giving the optional keyword arguments along with their default values
    #     inst_fullcat        : String or List of string or None
    #         Gives instrument full categories of the instrument models used
    #     inst_model_fullname : String or List of string
    #         Gives the full name of the instrument models used
    #     dataset             : String or list of string or None
    #         Gives the names of the datasets simulated
    #
    #     Returns
    #     -------
    #     datasim_alldatasets: DatasimDocFunc
    #         Datasimulator for all datasets
    #     """
    #     def datasim_allindmodels(p, *args, **kwargs):
    #         l_res = []
    #         for datasim, idxs in zip(l_datasim, l_params_idx):
    #             l_res.extend(datasim(p[idxs], *args, **kwargs))
    #         return l_res
    #
    #     return DatasimDocFunc(function=datasim_allindmodels,
    #                           params_model=params_model,
    #                           inst_cat=inst_fullcat,
    #                           mand_kwargs=mand_kwargs,
    #                           opt_kwargs=opt_kwargs,
    #                           include_dataset_kwarg=l_datasim[0].include_dataset_kwarg,
    #                           inst_model_fullname=inst_model_fullname,
    #                           dataset=dataset)

    ######################################
    ## Dealing with the configuration file
    ######################################

    def _configure_instcat_model(self, ask_before_adding=False):
        """Configure the inst cat model
        """
        logger.info(f"Start configuration of the {self.inst_cat} models.")

        logger.info("Load IND instrumental model configuration")
        self._load_config(config2load='indinstcatmod', ask_before_adding=ask_before_adding)

    # Function that get the function required by ConfigFileAttr._load_config
    ########################################################################

    def _get_function_config(self, function_type, config2load):
        if function_type == 'add_default_config':
            if config2load == 'indinstcatmod':
                return self.__add_default_config_indinstcatmod
        elif function_type == 'check_config_exists':
            if config2load == 'indinstcatmod':
                return self.__config_var_exist_indinstcatmod
        elif function_type == 'load_config_content':
            if config2load == 'indinstcatmod':
                return self.__load_config_var_content_indinstcatmod
        return super(IND_InstCat_Model, self)._get_function_config(function_type=function_type, config2load=config2load)

    # Dealing with the configuration of the transit, phase curve, occultation and instrumental models
    #################################################################################################

    def __add_default_config_indinstcatmod(self, file):
        """Add the default config for the parametrisation of the instrument categories

        This function is stored in Core_Model.get_function_config and used by Core_Model._load_config
        """
        file.write(self._get_intro_instcat_text())
        file.write("# Polynomial trend models for IND\n")
        file.write("#################################\n")
        file.write(f"# Define the model to use for each indicator category. Available models are {self.name_models_available}\n")
        # Create the dictionary for the polynomial models
        main_dict = {}
        for ii, inst_fullcat in enumerate(self.indicator_fullcategories):
            inst_cat, inst_subcat = IND_Instrument.interpret_inst_fullcat(inst_fullcat)
            main_dict[inst_subcat] = {"all": {}}
            for model in self.__models_available__:
                main_dict[inst_subcat]["all"][model.model_name] = model.get_dico_config(param_container=self.model_instance,
                                                                                        prefix=inst_subcat,
                                                                                        notexist_ok=True,
                                                                                        )
            for indinst_model in self.get_l_instmod(inst_fullcat=inst_fullcat):
                main_dict[inst_subcat][indinst_model.full_name] = {}
                for model in self.__models_available__:
                    main_dict[inst_subcat][indinst_model.full_name][model.model_name] = model.get_dico_config(param_container=indinst_model,
                                                                                                              prefix=None,
                                                                                                              notexist_ok=True,
                                                                                                              )
        text_main_dict = ""
        for ind_category, dico_config in main_dict.items():
            tab_ind_category = spacestring_like(f"{ind_category} = ")
            text_main_dict += f"{ind_category} = " + pformat(dico_config, compact=True).replace('\n', f'\n{tab_ind_category}') + "\n"
        file.write(text_main_dict)

    def __config_var_exist_indinstcatmod(self, dico_config_file):
        """Check if the variable(s) required for the parametrisation of the instrument categories

        This function is stored in Core_Model.get_function_config and used by Core_Model._load_config
        """
        return all([var in dico_config_file for var in self.indicator_subcategories])
    
    def __load_config_var_content_indinstcatmod(self, dico_config_file):
        """Load the variable(s) required for the parametrisation of the instrument categories

        This function is stored in Core_Model.get_function_config and used by Core_Model._load_config
        """
        # For each indication category ...
        for ind_fullcat in self.indicator_fullcategories:
            ind_cat = IND_Instrument.interpret_inst_fullcat(ind_fullcat)[1]
            dico_config_ind_cat = dico_config_file[ind_cat]
            # Check that each instrument model of each indicator category has been defined
            l_indcat_model = self.get_l_instmod(inst_fullcat=ind_fullcat)
            assert set(dico_config_ind_cat.keys()) == set(["all", ] + [indinst.full_name for indinst in l_indcat_model])
            # Set all the indicator instrument model has not modeled
            for indinst_model in l_indcat_model:
                self.indinst_model_is_modeled[indinst_model.full_name] = False
            # Load config for the whole system
            for model_name, dico_config_model in dico_config_ind_cat["all"].items():
                model = self.get_modelclass_4_modelname(model_name=model_name)
                model.set_dico_config(param_container=self.model_instance, prefix=ind_cat,
                                      dico_config=dico_config_model)
                # Update self.indinst_model_is_modeled
                for indinst_model in l_indcat_model:
                    self.indinst_model_is_modeled[indinst_model.full_name] = self.indinst_model_is_modeled[indinst_model.full_name] or dico_config_model["do"]
            # Load config per_instrument
            for indinst_model in l_indcat_model:
                for model_name, dico_config_model in dico_config_ind_cat[indinst_model.full_name].items():
                    model = self.get_modelclass_4_modelname(model_name=model_name)
                    model.set_dico_config(param_container=indinst_model, prefix=None,
                                          dico_config=dico_config_model)
                    # Update self.indinst_model_is_modeled
                    self.indinst_model_is_modeled[indinst_model.full_name] = self.indinst_model_is_modeled[indinst_model.full_name] or dico_config_model["do"]

    ##########
    ## To sort
    ##########

    def datasim_creator(self, inst_models, datasets, get_times_from_datasets, dataset_db):
        """Create the data simulator to be used for the indicators.

        Arguments
        ---------
        inst_models : List of Instrument_Model instances
            List of intrument models corresponding to each datasets in datasets
        datasets    : List of IND_Dataset instances
            List of datasets
        get_times_from_datasets  : bool
            If True the times at which the LC model is computed is taken from the datasets.
            Else it is an input of the datasimulator function produced.
        dataset_db  : DatasetDatabase
            Dataset database, this will not be used. It there to comply to the standard datasim_creator call.
            For other data types it used to access the indicator dataset for the decorrelation.
            However currently we are not decorrelating the indicators.
            Technically it's provided to get_polymodel, but get_polymodel doesn't actually use it. (TODO)

        Returns
        -------
        datasimulator : DatasimDocFunc
            Datasimulator simulating the list of datasets provided.
        """
        ##########################################################
        # Separate the inst_models in different indicator category
        ##########################################################
        (l_dataset, l_inst_model, multi, inst_model_full_name, dst_ext, instcat_docf, instmod_docf,
         dtsts_docf) = check_datasets_and_instmodels(datasets, inst_models)

        def init_defdict():
            return {"datasets": [], "inst_models": [], "indexes": []}

        dico_d_l_dataset_inst_model_4_ind_cat = defaultdict(init_defdict)
        for idx, (dst, instmod) in enumerate(zip(l_dataset, l_inst_model)):
            ind_cat = instmod.instrument.indicator_category
            dico_d_l_dataset_inst_model_4_ind_cat[ind_cat]['datasets'].append(dst)
            dico_d_l_dataset_inst_model_4_ind_cat[ind_cat]['inst_models'].append(instmod)
            dico_d_l_dataset_inst_model_4_ind_cat[ind_cat]['indexes'].append(idx)

        ########################################################
        # create the indicator model for each indicator category
        ########################################################
        d_d_docfunc_4_ind_cat = {}
        for ind_cat, d_l_dataset_inst_model in dico_d_l_dataset_inst_model_4_ind_cat.items():
            d_d_docfunc_4_ind_cat[ind_cat] = create_datasimulator_IND(model_instance=self.model_instance,
                                                                      indicator_models=self.models_available,
                                                                      dataset_db=dataset_db,
                                                                      INDcat_model=self, indicator_category=ind_cat,
                                                                      inst_models=d_l_dataset_inst_model['inst_models'],
                                                                      datasets=d_l_dataset_inst_model['datasets'],
                                                                      get_times_from_datasets=get_times_from_datasets
                                                                      )

        #################################################################
        # create the datasimulator that combines all indicator categories
        #################################################################
        ######################################################################################################
        ## Initialise the function in the function builder for the whole system and for all indicator category
        ######################################################################################################
        # Create the FunctionBuilder
        func_builder = FunctionBuilder(parameter_vector_name=par_vec_name)

        func_builder.add_new_function(shortname=function_whole_shortname)
        if multi:
            func_full_name_MultiOrDst_ext = "_multi"
        else:
            func_full_name_MultiOrDst_ext = f"{l_dataset[0].dataset_code_name}"
        func_builder.set_function_fullname(full_name=f"IND_sim_{function_whole_shortname}_{func_full_name_MultiOrDst_ext}", shortname=function_whole_shortname)

        #############################################################################
        ## Piece the different whole functions from the different indicators together
        #############################################################################
        if multi:
            func_builder.add_to_body_text(text=f"{tab}res=[{', '.join(['None' for ii in range(len(l_dataset))])}]\n",
                                          function_shortname=function_whole_shortname)
        for ind_cat, d_docfunc in d_d_docfunc_4_ind_cat.items():
            function_whole_shortname_ind_cat = template_function_whole_shortname_ind_cat.format(indicator_category=ind_cat,
                                                                                                function_whole_shortname=function_whole_shortname)
            if function_whole_shortname_ind_cat in d_docfunc:
                docfunc_ind_cat = d_docfunc[function_whole_shortname_ind_cat]
                # Add the model parameters
                l_idx_param_in_whole_func = []
                for param_fullname in docfunc_ind_cat.param_model_names_list:
                    param = self.model_instance.get_parameter(name=param_fullname, notexist_ok=False,
                                                              kwargs_get_list_params={'main': True, 'free': True, 'no_duplicate': True, 'recursive': True},
                                                              kwargs_get_name={'recursive': True, 'include_prefix': True, 'force_no_duplicate': False})
                    if not(func_builder.is_parameter(parameter=param, function_shortname=function_whole_shortname)):
                        func_builder.add_parameter(parameter=param, function_shortname=function_whole_shortname, exist_ok=False)
                    l_idx_param_in_whole_func.append(func_builder.get_index_4_parameter(parameter=param,
                                                                                        function_shortname=function_whole_shortname
                                                                                        )
                                                     )
                # Add the mandatory kwargs
                mand_kwargs_list = docfunc_ind_cat.mand_kwargs_list
                mand_kwargs_list.remove(docfunc_ind_cat.param_model_vect_name)
                for mand_arg in mand_kwargs_list:
                    if mand_arg not in func_builder.get_l_mandatory_argument(function_shortname=function_whole_shortname):
                        func_builder.add_mandatory_argument(argument_name=mand_arg, function_shortname=function_whole_shortname,
                                                            exist_ok=False)
                # Add the optional kwargs
                opt_kwargs_dict = docfunc_ind_cat.opt_kwargs_dict
                for opt_arg, def_val in opt_kwargs_dict.items():
                    if opt_arg not in func_builder.get_d_optional_argument(function_shortname=function_whole_shortname):
                        func_builder.add_optional_argument(argument_name=opt_arg, default_value=def_val, function_shortname=function_whole_shortname,
                                                           exist_ok=False)
                    else:
                        if func_builder.get_d_optional_argument(function_shortname=function_whole_shortname)[opt_arg] != def_val:
                            raise ValueError(f"Optional argument {opt_arg} already exists in function_builder (function_shortname={function_whole_shortname}) with a different value.")

                # Add datasimulator to whole indicator function
                if len(mand_kwargs_list) > 0:
                    mand_arg_text = ", "
                    mand_arg_text += ", ".join(mand_kwargs_list)
                else:
                    mand_arg_text = ""
                if len(opt_kwargs_dict) > 0:
                    opt_arg_text = ", "
                    opt_arg_text += ", ".join(opt_kwargs_dict.keys())
                else:
                    opt_arg_text = ""
                if multi:
                    if docfunc_ind_cat.multi_output:
                        l_text_res = [f"res[{idx}]" for idx in dico_d_l_dataset_inst_model_4_ind_cat[ind_cat]['indexes']]
                        func_builder.add_to_body_text(text=f"{tab}({', '.join(l_text_res)}) = datasim_{ind_cat}({par_vec_name}[{l_idx_param_in_whole_func}]{mand_arg_text}{opt_arg_text})\n",
                                                      function_shortname=function_whole_shortname)
                    else:
                        func_builder.add_to_body_text(text=f"{tab}res[{dico_d_l_dataset_inst_model_4_ind_cat[ind_cat]['indexes'][0]}] = datasim_{ind_cat}({par_vec_name}[{l_idx_param_in_whole_func}]{mand_arg_text}{opt_arg_text})\n",
                                                      function_shortname=function_whole_shortname)
                else:
                    func_builder.add_to_body_text(text=f"{tab}return datasim_{ind_cat}({par_vec_name}[{l_idx_param_in_whole_func}]{mand_arg_text}{opt_arg_text})",
                                                  function_shortname=function_whole_shortname)
                func_builder.add_variable_to_ldict(variable_name=f"datasim_{ind_cat}", variable_content=docfunc_ind_cat.function,
                                                   function_shortname=function_whole_shortname, exist_ok=False, overwrite=False)
        if multi:
            func_builder.add_to_body_text(text=f"{tab}return res",
                                          function_shortname=function_whole_shortname)

        #########################################
        # Execute the text of the whole functions
        #########################################
        # Create and fill the output dictionnary containing the datasimulators functions.
        # dico_docf = dict.fromkeys(text_def_func.keys(), None)
        dico_docf = {}
        for func_shortname in func_builder.l_function_shortname:
            if func_builder.get_body_text(function_shortname=func_shortname) != "":
                logger.debug(f"text of {func_shortname} all INDs simulator function :\n{func_builder.get_full_function_text(shortname=func_shortname)}")
                exec(func_builder.get_full_function_text(shortname=func_shortname), func_builder._get_ldict(function_shortname=func_shortname))
                params_model = [param.full_name for param in func_builder.get_free_parameter_vector(function_shortname=func_shortname)]
                dico_param_nb = {nb: param for nb, param in enumerate(params_model)}
                if len(func_builder.get_l_mandatory_argument(function_shortname=func_shortname)) > 0:
                    mand_kwargs = func_builder.get_l_mandatory_argument(function_shortname=func_shortname)
                else:
                    mand_kwargs = None
                if len(func_builder.get_d_optional_argument(function_shortname=func_shortname)) > 0:
                    opt_kwargs = func_builder.get_d_optional_argument(function_shortname=func_shortname)
                else:
                    opt_kwargs = None
                logger.debug(f"Parameters for {func_shortname} all INDs simulator function :\n{dico_param_nb}")
                dico_docf[func_shortname] = DatasimDocFunc(function=func_builder._get_ldict(function_shortname=func_shortname)[func_builder.get_function_fullname(shortname=func_shortname)],
                                                           param_model_names_list=params_model,
                                                           params_model_vect_name=par_vec_name,
                                                           inst_cats_list=instcat_docf,
                                                           inst_model_fullnames_list=instmod_docf,
                                                           dataset_names_list=dtsts_docf,
                                                           include_dataset_kwarg=get_times_from_datasets,
                                                           mand_kwargs_list=mand_kwargs,
                                                           opt_kwargs_dict=opt_kwargs,
                                                           )

        ##################################
        # Gather the rest of the functions
        ##################################
        for ind_cat, d_docfunc in d_d_docfunc_4_ind_cat.items():
            dico_docf.update(d_docfunc)

        return dico_docf

    def get_l_instmod(self, inst_model=None, inst_name=None, inst_fullcat=None):
        """Return the list of instrument model object for the instrument category
        """
        format_not_recognised = False
        if inst_fullcat is None:
            l_inst_fullcat = self.model_instance.get_inst_fullcat4inst_cat(inst_cat=self.inst_cat)
        elif isinstance(inst_fullcat, str):
            l_inst_fullcat = [inst_fullcat, ]
        elif isinstance(inst_fullcat, Iterable):
            if not(all([isinstance(inst_fullcat_i, str) for inst_fullcat_i in inst_fullcat])):
                format_not_recognised = True
            else:
                l_inst_fullcat = inst_fullcat
        else:
            format_not_recognised = True
        if format_not_recognised:
            raise ValueError("inst_fullcat should be a str, an interable of str or None")
        res = []
        for inst_fullcat_i in l_inst_fullcat:
            res.extend(self.model_instance.get_instmodel_objs(inst_model=None, inst_name=None, inst_fullcat=inst_fullcat_i,
                                                              sortby_instfullcat=False, sortby_instname=False, sortby_instmodel=False,
                                                              )
                       )
        return res

    def get_l_instmod_full_name(self, inst_model=None, inst_name=None, inst_fullcat=None):
        """Return the list of instrument model full name for the instrument category
        """
        return [inst_mod.full_name for inst_mod in self.get_l_instmod(inst_model=inst_model, inst_name=inst_name,
                                                                      inst_fullcat=inst_fullcat
                                                                      )
                ]

    # def _init_indmodel(self, inst_model_obj, indicator_model, kwargs_indicator_model):
    #     """Initialise the indicator model for a given instrument model
    #
    #     Create the required parameters in the instrument model object and define the associated attributes
    #
    #     Arguments
    #     ---------
    #     inst_model_obj         : Instrument_Model
    #         Instance of the Instrument_Model class
    #     indicator_model        : str
    #         String giving the indicator model to be used for this instrument
    #     kwargs_indicator_model : dictionary
    #         Dictionary giving the arguments required by the indicator model
    #     """
    #     for ind_model, init_indmod_func in self.__init_indmodel4indmodel.items():
    #         if indicator_model == ind_model:
    #             init_indmod_func(inst_model_obj=inst_model_obj, kwargs_indicator_model=kwargs_indicator_model)
    #             return
    #     # If not ind_model match indicator model then raise an error
    #     raise ValueError(f"Indicator model {indicator_model} is not implemented.")

    # def create_text_instcat_paramfile_model(self, model_instance):
    #     """Create the param file for definition of the indicators models.

    #     Arguments
    #     ---------
    #     file_path           : string
    #         Path to the param_file.
    #     """
    #     main_dict = {}
    #     for ii, inst_fullcat in enumerate(self.indicator_fullcategories):
    #         inst_cat, inst_subcat = IND_Instrument.interpret_inst_fullcat(inst_fullcat)
    #         main_dict[inst_subcat] = {"all": {}}
    #         for model in self.__models_available__:
    #             main_dict[inst_subcat]["all"][model.model_name] = model.get_dico_config(param_container=self.model_instance,
    #                                                                                     prefix=inst_subcat,
    #                                                                                     notexist_ok=True,
    #                                                                                     )
    #         for indinst_model in self.get_l_instmod(inst_fullcat=inst_fullcat):
    #             main_dict[inst_subcat][indinst_model.full_name] = {}
    #             for model in self.__models_available__:
    #                 main_dict[inst_subcat][indinst_model.full_name][model.model_name] = model.get_dico_config(param_container=indinst_model,
    #                                                                                                           prefix=None,
    #                                                                                                           notexist_ok=True,
    #                                                                                                           )
    #     text = """
    #     # Define the model to use for each indicator category. Available models are {model_available}
    #     {main_dict}
    #     """
    #     text = dedent(text)  # Remove undesired indentation

    #     text_main_dict = ""
    #     for ind_category, dico_config in main_dict.items():
    #         tab_ind_category = spacestring_like(f"{ind_category} = ")
    #         text_main_dict += f"{ind_category} = " + pformat(dico_config, compact=True).replace('\n', f'\n{tab_ind_category}') + "\n"

    #     text = text.format(model_available=self.name_models_available, main_dict=text_main_dict)
    #     return text

    # def read_IND_param_file(self):
    #     """Read the content of the IND parameter file."""
    #     if self.isdefined_paramfile_instcat:
    #         with open(self.paramfile_instcat) as f:
    #             exec(f.read())
    #         dico = locals().copy()
    #         dico.pop("self")
    #         dico.pop("f")
    #         logger.debug("IND parameter file read.\nContent of the parameter file: {}"
    #                      "".format(dico.keys()))
    #         return dico
    #     else:
    #         raise IOError("Impossible to read IND parameter file: {}".format(self.paramfile_instcat))

    # def __create_text_model_4_indicator(self):
    #     """Create the string giving the model_4_indicator dictionary for the parameter file.
    #
    #     Returns
    #     -------
    #     text : str
    #         String giving the text for the model_4_indicator dictionary for the indicator parameter file
    #     """
    #     text = f"{self.__name_model_4_indicator_dict} =" + " {"
    #     tab = spacestring_like(text)
    #     for ii, inst_subcat in enumerate(self.indicator_subcategories):
    #         if ii != 0:
    #             text += f"\n{tab}"
    #         text += f"'{inst_subcat}': '{self.model_4_indicator[inst_subcat]}',"
    #     text += f"\n{tab}" + "}\n"
    #     return text

    # def __check_IND_param_file(self, dico_config):
    #     """Check that the content of the param file for indicators.
    #
    #     Check that all the necessary object are here, that they are properly defined and that all is consistent.
    #     1. Check that the model_4_indicator dictionary is there (if not -> AssertionError)
    #     2. Check its content (if content not valid -> AssertionError):
    #     3. Check if all used models have there definition dictionary. If not return in missing_usedmodel_dict the list of missing model directories
    #     4. Check if there is additional dictionaries or variables that should not be here. If yes return the list in unnecessary_model_dict
    #     5. Check that each used models dictionary is correctly defined.
    #         a. Check that all indicator sub categories modeled by this model and only these are keys
    #         b. Check that the associated dictionaries contain the necessary keys and only these and that their values are valid.
    #         c. If any of these checks is not satisfied raise an AssertionError
    #
    #     Arguments
    #     ---------
    #     dico_config : dictionary
    #         Dictionary providing the content of the indicator parameter file.
    #
    #     Returns
    #     -------
    #     missing_usedmodel_dict_name : list of strings
    #         Name of the missing dictionary definitions
    #     unnecessary_model_dict_name : list of strings
    #         Name of the unnecessary variables defined
    #     dict_valid            : dictionary of boolean
    #         keys are model names or self.__name_model_4_indicator_dict and values boolean which indicates is the if the definition is valid.
    #     error_list                  : list of string
    #         List of errors detected
    #     """
    #     error_list = []
    #     dict_valid = {}
    #     # 1.
    #     if not(self.__name_model_4_indicator_dict in dico_config):
    #         error_list.append(f"{self.__name_model_4_indicator_dict} should be defined in the indicator parameter file. Defined objects are {list(dico_config.keys())}.")
    #     # 2
    #     dict_valid[self.__name_model_4_indicator_dict], errors = self.__check_model_4_indicator_dict(dico_config[self.__name_model_4_indicator_dict])
    #     error_list.extend(errors)
    #     # 3 and 4.
    #     used_models = list(set(dico_config[self.__name_model_4_indicator_dict].values()))
    #     if None in used_models:
    #         used_models.remove(None)
    #     missing_usedmodel_dict_name = [self.__dictname_4_model_indicator[model] for model in used_models]
    #     model_name_4_model_dict_name = {self.__dictname_4_model_indicator[model]: model for model in used_models}
    #     model_dict_names_defined = list(dico_config.keys())
    #     model_dict_names_defined.remove(self.__name_model_4_indicator_dict)
    #     unnecessary_model_dict_name = []
    #     nessecary_model_dict_name = []
    #     for model_dict in model_dict_names_defined:
    #         if model_dict in missing_usedmodel_dict_name:
    #             missing_usedmodel_dict_name.remove(model_dict)
    #             nessecary_model_dict_name.append(model_dict)
    #         else:
    #             unnecessary_model_dict_name.append(model_dict)
    #     # 5.
    #     for model_dict_name in nessecary_model_dict_name:
    #         dict_valid[model_name_4_model_dict_name[model_dict_name]], errors = self.__checker_4_indicator_model_dict[model_dict_name](dict_model=dico_config[model_dict_name], dict_model_4_indicator=dico_config[self.__name_model_4_indicator_dict])
    #         error_list.extend(errors)
    #     return missing_usedmodel_dict_name, unnecessary_model_dict_name, dict_valid, error_list

    # def __check_model_4_indicator_dict(self, model_4_indicator):
    #     """Validate the model_4_indicator dictionary of the parameter file.
    #
    #     1. Check that all used indicators sub categories and only these are keys of this dictionary
    #     2. Check that the associated values are valid models.
    #
    #     Arguments
    #     ---------
    #     model_4_indicator : Dictionary
    #         Dictionary model_4_indicator as read from the indicator parameter file.
    #
    #     Returns
    #     -------
    #     valid      : boolean
    #         Say if the content of model_4_indicator is valid
    #     error_list : list of string
    #         List of error detected
    #     """
    #     error_list = []
    #     # 1.
    #     if Counter(list(model_4_indicator.keys())) != Counter(self.indicator_subcategories):
    #         error_list.append(f"There is an inconsistency in between the list of indicator subcategories ({self.indicator_subcategories}) and the list of keys in the dictionary {self.__name_model_4_indicator_dict}.")
    #     # 2.
    #     for inst_subcat, model in model_4_indicator.items():
    #         if not self.is_valid_indicator_model(model=model):
    #             error_list.append(f"{model} provided for indicator {inst_subcat} is not a valid indicator model.")
    #     return len(error_list) == 0, error_list
    #
    # def __load_model_4_indicator_dict(self, model_4_indicator):
    #     """Load the model_4_indicator dictionary of the parameter file.
    #
    #     Arguments
    #     ---------
    #     model_4_indicator : Dictionary
    #         Dictionary model_4_indicator as read from the indicator parameter file.
    #     """
    #     self.__model_4_indicator = model_4_indicator

    # def load_instcat_paramfile(self, answer_recreate=None):
    #     """Load the param file for indicators.
    #     """
    #     assert len(self.indicator_models_used) > 0, "There should be a model used by default."
    #     missing_usedmodel_dict_name = self.indicator_models_used
    #     unnecessary_model_dict_name = []
    #     while (len(missing_usedmodel_dict_name) > 0) or (len(unnecessary_model_dict_name)):
    #         dico_config = self.read_IND_param_file()
    #         missing_usedmodel_dict_name, unnecessary_model_dict_name, dict_valid, error_list = self.__check_IND_param_file(dico_config)
    #         if len(error_list) > 0:
    #             inconsistency = True
    #             logger.warning(f"The following errors have been spotted in the indicator parameter file: {error_list}")
    #         else:
    #             inconsistency = False
    #         if dict_valid[self.__name_model_4_indicator_dict]:
    #             self.__load_model_4_indicator_dict(dico_config[self.__name_model_4_indicator_dict])
    #         dict_valid.pop(self.__name_model_4_indicator_dict)
    #         for model, valid in dict_valid.items():
    #             if valid:
    #                 self.__load_text_indicator_methods[model](dico_config[self.__dictname_4_model_indicator[model]])
    #         if len(missing_usedmodel_dict_name) > 0:
    #             logger.warning(f"The dictionary to parametrize the following indicator models are missing in the indicator parameter file: {missing_usedmodel_dict_name}")
    #             inconsistency = True
    #         if len(unnecessary_model_dict_name) > 0:
    #             logger.warning(f"There is unnecessary objects defined in the indicator parameter file: {unnecessary_model_dict_name}")
    #             inconsistency = True
    #         if inconsistency:
    #             l_answers = ['y', 'n']
    #             if answer_recreate is None:
    #                 rep = QCM_utilisateur("There is some inconsistencies in the indicator parameter file (see warnings above). Do you want to recreate it from current valid inputs. 'n' would mean triggering an error\n", l_answers)
    #             else:
    #                 if answer_recreate not in l_answers:
    #                     raise ValueError(f"The provided answer_recreate is not valid. Should be in {l_answers}, got {answer_recreate}")
    #                 else:
    #                     rep = answer_recreate
    #         else:
    #             rep = "n"
    #         if inconsistency and (rep == "n"):
    #             raise ValueError(f"The content of the indicator parameter file is not valid. Here is the list of detected errors: {error_list}")
    #         elif inconsistency and (rep == "y"):
    #             self.create_IND_param_file(paramfile_path=self.paramfile_instcat, answer_overwrite="y", answer_create=None)
    #             input("Modify the IND specific paramerisation file: {}".format(self.paramfile_instcat))

    # def load_config(self, dico_config):
    #     """load the configuration specified by the dictionnary"""
    #     # Check that each indication category has been defined
    #     l_ind_fullcat = self.indicator_fullcategories
    #     indfullcat_4_indsubcat = {IND_Instrument.interpret_inst_fullcat(inst_fullcat)[1]: inst_fullcat for inst_fullcat in l_ind_fullcat}
    #     assert set(dico_config.keys()) == set(self.indicator_subcategories)
    #     # For each indication category ...
    #     for ind_cat, dico_config_ind_cat in dico_config.items():
    #         # Check that each instrument model of each indicator category has been defined
    #         l_indcat_model = self.get_l_instmod(inst_fullcat=indfullcat_4_indsubcat[ind_cat])
    #         assert set(dico_config_ind_cat.keys()) == set(["all", ] + [indinst.full_name for indinst in l_indcat_model])
    #         # Set all the indicator instrument model has not modeled
    #         for indinst_model in l_indcat_model:
    #             self.indinst_model_is_modeled[indinst_model.full_name] = False
    #         # Load config for the whole system
    #         for model_name, dico_config_model in dico_config_ind_cat["all"].items():
    #             model = self.get_modelclass_4_modelname(model_name=model_name)
    #             model.set_dico_config(param_container=self.model_instance, prefix=ind_cat,
    #                                   dico_config=dico_config_model)
    #             # Update self.indinst_model_is_modeled
    #             for indinst_model in l_indcat_model:
    #                 self.indinst_model_is_modeled[indinst_model.full_name] = self.indinst_model_is_modeled[indinst_model.full_name] or dico_config_model["do"]
    #         # Load config per_instrument
    #         for indinst_model in l_indcat_model:
    #             for model_name, dico_config_model in dico_config_ind_cat[indinst_model.full_name].items():
    #                 model = self.get_modelclass_4_modelname(model_name=model_name)
    #                 model.set_dico_config(param_container=indinst_model, prefix=None,
    #                                       dico_config=dico_config_model)
    #                 # Update self.indinst_model_is_modeled
    #                 self.indinst_model_is_modeled[indinst_model.full_name] = self.indinst_model_is_modeled[indinst_model.full_name] or dico_config_model["do"]

    # @property
    # def model_4_indicator(self):
    #     """Dictionary giving the model to use for each indicator.
    #
    #     keys are indicator sub categories, values are indicator models.
    #
    #     It is initialised in __init__ of IndicatorModelInterface and updated in __load_model_4_indicator_dict called by load_IND_param_file
    #     """
    #     return self.__model_4_indicator

    # @property
    # def indicator_subcategories_4_model_used(self):
    #     """Dictionary giving the indicator subcategories modeled by each model.
    #
    #     Keys are indicator models
    #     Values are a list of indicator sub categories
    #     """
    #     res = OrderedDict()
    #     for model in self.indicator_models_used:
    #         res[model] = []
    #     for inst_subcat, model in self.model_4_indicator.items():
    #         res[model].append(inst_subcat)
    #     return res

    # @property
    # def indicator_models_used(self):
    #     """List of indicator model used.
    #     """
    #     ll = list(set(self.model_4_indicator.values()))
    #     # ll.sort()  # Cannot sort like that since a possible model is None. I Don't think that it really needs to be sorted anyway.
    #     return ll

    # @property
    # def params_indicator_models(self):
    #     """Dictionary giving the parameters for each indicator model used
    #
    #     Keys: Indicator model name
    #     Values: Dictionary giving the parameter of this model for each indicator sub category using this model§
    #         Keys: Indicator sub category
    #         Values: Dictionary giving the parameter of the model for this indicator sub category
    #             Keys: Parameter name
    #             Values: Parameter value
    #
    #     Initialised in __init__ of IndicatorModelInterface
    #     Updated in __load_model_4_indicator_dict and all methods in __load_text_indicator_methods
    #     """
    #     return self.__params_indicator_models

    # def __create_text_polynomial_model(self):
    #     """Create the string giving the polynomial dictionary for the parameter file.
    #     """
    #     text = f"{self.__dictname_4_model_indicator[self._polynomial_method_name]} = {{"
    #     tab = spacestring_like(text)
    #     for ii, inst_subcat in enumerate(self.indicator_subcategories_4_model_used[self._polynomial_method_name]):
    #         if ii != 0:
    #             text += f"\n{tab}"
    #         text += f"'{inst_subcat}': {{'{self._polynomial_order_name}': {self.params_indicator_models[self._polynomial_method_name][inst_subcat][self._polynomial_order_name]}}},"
    #     text += f"\n{tab}}}\n"
    #     return text

    # def __check_polynomial_model(self, dict_model, dict_model_4_indicator):
    #     """Check the content of polynomial model dictionary from the indicator parameter file.
    #
    #     1. Check that all indicator sub categories modeled by this model and only these are keys
    #     2. Check that the associated dictionaries contain the necessary keys and only these and that their values are valid.
    #
    #     Arguments
    #     ---------
    #     dict_model             : dictionary
    #         Dictionary parametrizing the polynomial models as read from the indicator parameter file.
    #     dict_model_4_indicator :
    #         Model_4_indicator diction as read from the indicator parameter file.
    #
    #     Returns
    #     -------
    #     valid      : boolean
    #         Say if the content of Dictionary parametrizing the polynomial models (dict_model) is valid
    #     error_list : list of string
    #         List of error detected
    #     """
    #     error_list = []
    #     # 1.
    #     indicators_using_model = []
    #     for indicator_subcat, model in dict_model_4_indicator.items():
    #         if model == self._polynomial_method_name:
    #             indicators_using_model.append(indicator_subcat)
    #     if Counter(indicators_using_model) != Counter(list(dict_model.keys())):
    #         error_list.append(f"There is an inconsistency between the indicators using the polynomial model ({indicators_using_model}) and the list of keys in the dictionary to parameter the polynomial models ({list(dict_model.keys())})")
    #     # 2.
    #     for indicator_subcat in indicators_using_model:
    #         # Check the presence of all parameters
    #         dict_indicator = dict_model[indicator_subcat]
    #         if Counter(list(dict_indicator.keys())) != Counter(self._default_param_values_4_indicator_model[self._polynomial_method_name].keys()):
    #             error_list.append(f"There is an inconsistency between the parameters provided for the polynomial model of {indicator_subcat} ({list(dict_indicator.keys())}) and the expected list of parameters ({self._default_param_values_4_indicator_model[self._polynomial_method_name].keys()})")
    #         # Check values of all parameters
    #         if not isinstance(dict_indicator[self._polynomial_order_name], int):
    #             error_list.append(f"Parameter {dict_indicator[self._polynomial_order_name]} for the polynomial model of {indicator_subcat} should be an int.")
    #         elif dict_indicator[self._polynomial_order_name] < 0:
    #             error_list.append(f"Parameter {dict_indicator[self._polynomial_order_name]} for the polynomial model of {indicator_subcat} should be positive or null.")
    #     return len(error_list) == 0, error_list

    # def __load_text_polynomial_model(self, dict_model):
    #     """Load the polynomail model
    #
    #     Arguments
    #     ---------
    #     dict_model : dictionary
    #         Dictionary parametrizing the polynomial models as read from the indicator parameter file.
    #     """
    #     self.params_indicator_models[self._polynomial_method_name] = dict_model

    def set_parametrisation(self, **kwargs):
        """Set the parametrisation for the instrument category

        This method is called by Core_Parametrisation.set_instcat_parameterisation
        """
        # Set the parametrisation to the star and planets parameters
        self.set_system_parametrisation()

        # Set the parametrisation to the instrument models parameters
        self.set_instmodel_parametrisation()

    def set_system_parametrisation(self):
        """
        """
        for ind_cat in self.indicator_subcategories:
            for model in self.models_available:
                model.set_parametrisation(param_container=self.model_instance, indicator_category=ind_cat,
                                          instrument_per_instrument=False, prefix=ind_cat
                                          )

    def set_instmodel_parametrisation(self):
        """
        """
        for indinst_fullcat in self.indicator_fullcategories:
            for inst_model in self.model_instance.get_instmodel_objs(inst_fullcat=indinst_fullcat):
                for model in self.models_available:
                    model.set_parametrisation(param_container=inst_model, indicator_category=inst_model.instrument.indicator_category,
                                              instrument_per_instrument=True, prefix=None
                                              )
