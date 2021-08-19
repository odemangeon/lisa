#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Indicator model module.
"""
from logging import getLogger
from collections import OrderedDict, Counter, defaultdict
from unittest import TestCase

from .polynomial_model import PolynomialIndicatorInterface
from ...dataset_and_instrument.indicator import IND_inst_cat, IND_Instrument
from ..datasim_docfunc import DatasimDocFunc
from ..datasimulator_toolbox import check_datasets_and_instmodels
from .....tools.miscellaneous import spacestring_like
from .....tools.human_machine_interface.QCM import QCM_utilisateur


## Logger object
logger = getLogger()


class IND_InstCat_Model(PolynomialIndicatorInterface):
    """docstring for LC_InstCat_Model, interface class for a subclass of Core_Model."""

    # Mandatory attributes for a sublass of Core_InstCat_Model
    __inst_cat__ = IND_inst_cat
    __has_instcat_paramfile__ = True
    __datasim_creator_name__ = "sim_IND"

    # models available for the indicators
    __available_models_4_indicators__ = [PolynomialIndicatorInterface._polynomial_method_name, ]  # The first one is the default one

    # Define the dictionary providing the default parameters values for each model
    _default_param_values_4_indicator_model = {PolynomialIndicatorInterface._polynomial_method_name: PolynomialIndicatorInterface._default_param_values}

    # String giving the name of the dictionary used to define the model to use for each indicator in the parameter file
    __name_model_4_indicator_dict = "model_4_indicator"

    def __init__(self):
        # Define the dictionary giving the function to use to create the text of the dictionaries to defined the paremeters of each model for the parameter file
        self.__create_text_indicator_methods = {self._polynomial_method_name: self.__create_text_polynomial_model}
        # Define the dictionary giving the function to use to load the text of the dictionaries to defined the paremeters of each model for the parameter file
        self.__load_text_indicator_methods = {self._polynomial_method_name: self.__load_text_polynomial_model}

        # Define the dictionary giving the name of the dictionary to use in the parameter file in which the parameters of each model are going to be defined
        self.__dictname_4_model_indicator = {self._polynomial_method_name: self._polynomial_method_name + "_models"}

        # Define the checker functions for the dictionary use to define each model in the parameter file.
        self.__checker_4_indicator_model_dict = {self.__dictname_4_model_indicator[self._polynomial_method_name]: self.__check_polynomial_model}

        # Initialise the dictionary model_4_indicator
        self.__model_4_indicator = {inst_subcat: self.__available_models_4_indicators__[0] for inst_subcat in self.indicator_subcategories}

        # Define the dictionary datasimcreator4indmodel
        self.__datasimcreator4indmodel = {self._polynomial_method_name: self._create_datasimulator_IND_Poly}
        self.__kwargs_datasimcreator4indmodel = {self._polynomial_method_name: {"polynomial_order_name": self._polynomial_order_name}}  # For each indicator method the dictionary will be passed to the datasim creator function pointed by self.__datasimcreator4indmodel
        self.__init_indmodel4indmodel = {self._polynomial_method_name: self._init_polynomialind_model}

        # Initialise the params_indicator_models
        self.__params_indicator_models = {}
        for model, l_inst_subcat in self.indicator_subcategories_4_model_used.items():
            self.__params_indicator_models[model] = {
                inst_subcat: self._default_param_values_4_indicator_model[self.model_4_indicator[inst_subcat]].copy() for inst_subcat in l_inst_subcat}

        # Check that there is a key for each model in _default_param_values_4_indicator_model
        TestCase().assertSequenceEqual(list(self._default_param_values_4_indicator_model.keys()), self.__available_models_4_indicators__)

        # Check that there is a create_text_methods for each model
        TestCase().assertSequenceEqual(list(self.__create_text_indicator_methods.keys()), self.__available_models_4_indicators__)

        # Check that there is a load_text_methods for each model
        TestCase().assertSequenceEqual(list(self.__load_text_indicator_methods.keys()), self.__available_models_4_indicators__)

        # Check that there is a dictionary name for each model
        TestCase().assertSequenceEqual(list(self.__dictname_4_model_indicator.keys()), self.__available_models_4_indicators__)

        # Check that there is a datasim creator for each model
        TestCase().assertSequenceEqual(list(self.__datasimcreator4indmodel.keys()), self.__available_models_4_indicators__)
        # Check that there is a kwargs for the datasim creator for each model
        TestCase().assertSequenceEqual(list(self.__kwargs_datasimcreator4indmodel.keys()), self.__available_models_4_indicators__)

        # Check that there is a checker for each dictionary of each model
        TestCase().assertSequenceEqual(list(self.__dictname_4_model_indicator.values()), list(self.__checker_4_indicator_model_dict.keys()))

    @property
    def datasimcreator4indmodel(self):
        """Dictionary giving the datasim creator function for each model
        """
        return self.__datasimcreator4indmodel

    def __datasim_allindmodels_creator(self, l_datasim, l_params_idx, params_model, mand_kwargs, opt_kwargs,
                                       inst_fullcat, inst_model_fullname=None, dataset=None):
        """Return the datasimulator for all indicator models

        WARNING/TODO eventually: For now *args, **kwargs of the datasim_alldatasets are passed to all the datasim function.
        This might not be always desired.

        Arguments
        ---------
        l_datasim           : List of DatasimDocFunc
            list of datasimulators
        l_params_idx        : List of list of int
            List of list of indexes in the param array for each datasim function in l_datasim.
        params_model        : List of string
            Ordered list of parameters full name for the datasimulator being created
        mand_kwargs         : String
            String giving the mandatory keyword arguments for the datasimulator being created
        opt_kwargs          : String
            String giving the optional keyword arguments along with their default values
        inst_fullcat        : String or List of string or None
            Gives instrument full categories of the instrument models used
        inst_model_fullname : String or List of string
            Gives the full name of the instrument models used
        dataset             : String or list of string or None
            Gives the names of the datasets simulated

        Returns
        -------
        datasim_alldatasets: DatasimDocFunc
            Datasimulator for all datasets
        """
        def datasim_allindmodels(p, *args, **kwargs):
            l_res = []
            for datasim, idxs in zip(l_datasim, l_params_idx):
                l_res.extend(datasim(p[idxs], *args, **kwargs))
            return l_res

        return DatasimDocFunc(function=datasim_allindmodels,
                              params_model=params_model,
                              inst_cat=inst_fullcat,
                              mand_kwargs=mand_kwargs,
                              opt_kwargs=opt_kwargs,
                              include_dataset_kwarg=l_datasim[0].include_dataset_kwarg,
                              inst_model_fullname=inst_model_fullname,
                              dataset=dataset)

    def datasim_creator(self, inst_models=None, datasets=None):
        """Create the data simulator to be used for the indicators.

        Arguments
        ---------
        inst_models : List of Instrument_Model instances
            List of intrument models corresponding to each datasets in datasets
        datasets    : List of IND_Dataset instances
            List of datasets

        Returns
        -------
        datasimulator : DatasimDocFunc
            Datasimulator simulating the list of datasets provided.
        """
        # Check the content of inst_models and datasets argument and convert them into lists if only one instrument model/dataset is provided.
        # The check_datasets_and_instmodels does much more than that but here I just need that
        (l_dataset, l_inst_model, _, _, _, _, _) = check_datasets_and_instmodels(datasets, inst_models)

        # 1. Separate the instrument models and datasets depending on the model of indicator to use (whatever the indicator subcategory)
        def defdictfunc():
            return {"datasets": [], "instmodels": []}
        datsimC_inputs = defaultdict(defdictfunc)

        # For each dataset, ...
        for inst_mod_obj, dst in zip(l_inst_model, l_dataset):
            # ... get the indicator model to be used
            ind_mod = inst_mod_obj.indicator_model
            # ... store the dataset and instrument model object in datsimC_inputs
            datsimC_inputs[ind_mod]["datasets"].append(dst)
            datsimC_inputs[ind_mod]["instmodels"].append(inst_mod_obj)
        # 2. Compute a datasimulator for each indicator model (just one even if there is different indicators subcategories). Going to the right function
        datsimC = OrderedDict()
        l_indmod = []
        # For each indicator model, ...
        for ind_mod in datsimC_inputs.keys():
            # ... add the name of the indicator model to l_ind_mod
            l_indmod.append(ind_mod)
            # ... create the datasim function with all the datasets using this indicator model
            datsimC[ind_mod] = self.datasimcreator4indmodel[ind_mod](key_whole=self.key_whole,   # self.key_whole comes from Core_Model
                                                                     key_param=self.key_param,  # self.key_param comes from DatasimulatorCreator
                                                                     key_mand_kwargs=self.key_mand_kwargs,  # self.key_param comes from DatasimulatorCreator
                                                                     key_opt_kwargs=self.key_opt_kwargs,   # self.key_param comes from DatasimulatorCreator
                                                                     **self.__kwargs_datasimcreator4indmodel[ind_mod],
                                                                     inst_models=datsimC_inputs[ind_mod]["instmodels"], datasets=datsimC_inputs[ind_mod]["datasets"]
                                                                     )  # self.key_whole is defined in Core_Model
            dico_inputs_allind = {}
            for obj_key in datsimC[ind_mod].keys():
                dico_inputs_allind[obj_key] = {"l_params": [],
                                               "l_allparams": [],
                                               "l_allmand_kwargs": [],
                                               "l_allopt_kwargs": [],
                                               "l_params_idx": [],
                                               "inst_fullcats": [],
                                               "l_inst_model_fullnames_res_datasim": [],
                                               "l_datasets_res_datasim": []
                                               }
                # ... get the ordered list of instrument categories for this function
                dico_inputs_allind[obj_key]["inst_fullcats"] = dico_inputs_allind[obj_key]["inst_fullcats"] + list(datsimC[ind_mod][obj_key].inst_cat)
                # ... get the ordered list of instrument model full names for this function
                dico_inputs_allind[obj_key]["l_inst_model_fullnames_res_datasim"] = dico_inputs_allind[obj_key]["l_inst_model_fullnames_res_datasim"] + list(datsimC[ind_mod][obj_key].instmodel_fullname)
                # ... get the ordered list of dataset names for this function
                dico_inputs_allind[obj_key]["l_datasets_res_datasim"] = dico_inputs_allind[obj_key]["l_datasets_res_datasim"] + list(datsimC[ind_mod][obj_key].dataset)
                # ... create the list of indexes for the function parameters and the list of all the
                # model parameter for the all datasets function
                idx_par = []
                # For each parameter in the list of this function, ...
                dico_inputs_allind[obj_key]["l_params"].append(datsimC[ind_mod][obj_key].params_model)
                # WARNING/TODO: This two lines are a quick and very dirty way to pass the mand and opt kwargs to the __datasim_alldatasets_creator
                # and after the DatasimDocFunc init because if several functions use the same kwargs, it will then appear several times
                dico_inputs_allind[obj_key]["l_allmand_kwargs"].append(datsimC[ind_mod][obj_key].mand_kwargs_list)
                dico_inputs_allind[obj_key]["l_allopt_kwargs"].append(datsimC[ind_mod][obj_key].opt_kwargs_list)
                for par in datsimC[ind_mod][obj_key].params_model:
                    # ... if the param is not in the list of all parameters already, add it
                    if par not in dico_inputs_allind[obj_key]["l_allparams"]:
                        dico_inputs_allind[obj_key]["l_allparams"].append(par)
                    # ... get the index of this parameter in the list of all the parameters
                    idx_par.append(dico_inputs_allind[obj_key]["l_allparams"].index(par))
                dico_inputs_allind[obj_key]["l_params_idx"].append(idx_par)

        # 3. If needed merge the different datasimulators from different indicator models into one datasimulator using something similar to what is done in DatasimulatorCreator.create_datasimulator_alldatasets
        # Create the datasim_alldatasets
        if len(datsimC) > 1:
            dico_docf = {}
            for obj_key in datsimC[ind_mod].keys():
                logger.debug("Creation of datasimulator for all indicator models.\nList of parameters names:\n{}\n"
                             "Input for the creation of the individual datasimulators:\n{}\n"
                             "List of indicator models simulated: {}\n"
                             "Dictionary of datasim functions obtained: {}\n"
                             "List of parameter names for each individual datasimulator:\n{}\n"
                             "List of param indexes for each individual datasimulator:\n{}\n"
                             "List of instrument categories: {}\n"
                             "List of instrument instrument model full names: {}\n"
                             "List of datasets: {}"
                             "".format(dico_inputs_allind[obj_key]["l_allparams"], datsimC_inputs,
                                       l_indmod, datsimC,
                                       dico_inputs_allind[obj_key]["l_params"], dico_inputs_allind[obj_key]["l_params_idx"],
                                       dico_inputs_allind[obj_key]["inst_fullcats"], dico_inputs_allind[obj_key]["l_inst_model_fullnames_res_datasim"],
                                       dico_inputs_allind[obj_key]["l_datasets_res_datasim"]))
                dico_docf[obj_key] = self.__datasim_alldatasets_creator(l_datasim=[datsimC[ind_mod][obj_key] for ind_mod in l_indmod],
                                                                        l_params_idx=dico_inputs_allind[obj_key]["l_params"],
                                                                        params_model=dico_inputs_allind[obj_key]["l_allparams"], mand_kwargs=str(dico_inputs_allind[obj_key]["l_allmand_kwargs"]), opt_kwargs=str(dico_inputs_allind[obj_key]["l_allopt_kwargs"]),
                                                                        instfull_cat=dico_inputs_allind[obj_key]["inst_fullcats"],
                                                                        inst_model_fullname=dico_inputs_allind[obj_key]["l_inst_model_fullnames_res_datasim"],
                                                                        dataset=dico_inputs_allind[obj_key]["l_datasets_res_datasim"])
            return dico_docf
        else:
            ind_mod, = list(datsimC.keys())
            return datsimC[ind_mod]

    def _init_indmodel(self, inst_model_obj, indicator_model, kwargs_indicator_model):
        """Initialise the indicator model for a given instrument model

        Create the required parameters in the instrument model object and define the associated attributes

        Arguments
        ---------
        inst_model_obj         : Instrument_Model
            Instance of the Instrument_Model class
        indicator_model        : str
            String giving the indicator model to be used for this instrument
        kwargs_indicator_model : dictionary
            Dictionary giving the arguments required by the indicator model
        """
        for ind_model, init_indmod_func in self.__init_indmodel4indmodel.items():
            if indicator_model == ind_model:
                init_indmod_func(inst_model_obj=inst_model_obj, kwargs_indicator_model=kwargs_indicator_model)
                return
        # If not ind_model match indicator model then raise an error
        raise ValueError(f"Indicator model {indicator_model} is not implemented.")

    def create_instcat_paramfile(self, paramfile_path=None, answer_overwrite=None, answer_create=None):
        """Create the param file for definition of the indicators models.

        Arguments
        ---------
        paramfile_path   : str
            Path to the indicator parameter file (IND_param_file).
        answer_overwrite : str
            If the IND_param_file already exists, do you want to
            overwrite it ? "y" or "n". If this is not provided the program will ask you interactively.
        answer_create    : str
            If the IND_param_file doesn't exists already, where do you want
            to create it ? "absolute", "run_folder" or "error". If this not provide the program will ask you interactively.
        """
        # Choose the parameter file path _choose_parameter_file_path is from Core_Model
        file_path, reply = self._choose_parameter_file_path(default_paramfile_path='IND_param_file.py', paramfile_path=paramfile_path, answer_overwrite=answer_overwrite, answer_create=answer_create)
        if reply == "y":
            with open(file_path, 'w') as f:
                # Write the header
                f.write("#!/usr/bin/python\n# -*- coding:  utf-8 -*-\n")
                # Put model_4_indicator dictionary
                f.write(f"# Define the model to use for each indicator category. Available models are {[None, ] + self.available_models_4_indicators}\n")
                f.write(self.__create_text_model_4_indicator())
                # Put the model parametrisation directories
                f.write("\n# Define the parameters of each models used.")
                for model in self.indicator_models_used:
                    f.write(f"\n\n# Define the parameters for model {model}.\n")
                    f.write(self.__create_text_indicator_methods[model]())
            logger.info("Parameter file created at path: {}".format(file_path))
        else:
            logger.info("Parameter file already existing and not overwritten: {}".format(file_path))
        self.paramfile4instcat[IND_inst_cat] = file_path  # paramfile4instcat is from Core_Model

    def read_IND_param_file(self):
        """Read the content of the IND parameter file."""
        if self.isdefined_INDparamfile:
            with open(self.paramfile4instcat[IND_inst_cat]) as f:
                exec(f.read())
            dico = locals().copy()
            dico.pop("self")
            dico.pop("f")
            logger.debug("IND parameter file read.\nContent of the parameter file: {}"
                         "".format(dico.keys()))
            return dico
        else:
            raise IOError("Impossible to read IND parameter file: {}".format(self.paramfile4instcat[IND_inst_cat]))

    def __create_text_model_4_indicator(self):
        """Create the string giving the model_4_indicator dictionary for the parameter file.

        Returns
        -------
        text : str
            String giving the text for the model_4_indicator dictionary for the indicator parameter file
        """
        text = f"{self.__name_model_4_indicator_dict} = {{"
        tab = spacestring_like(text)
        for ii, inst_subcat in enumerate(self.indicator_subcategories):
            if ii != 0:
                text += f"\n{tab}"
            text += f"'{inst_subcat}': '{self.model_4_indicator[inst_subcat]}',"
        text += f"\n{tab}}}\n"
        return text

    def __check_IND_param_file(self, dico_config):
        """Check that the content of the param file for indicators.

        Check that all the necessary object are here, that they are properly defined and that all is consistent.
        1. Check that the model_4_indicator dictionary is there (if not -> AssertionError)
        2. Check its content (if content not valid -> AssertionError):
        3. Check if all used models have there definition dictionary. If not return in missing_usedmodel_dict the list of missing model directories
        4. Check if there is additional dictionaries or variables that should not be here. If yes return the list in unnecessary_model_dict
        5. Check that each used models dictionary is correctly defined.
            a. Check that all indicator sub categories modeled by this model and only these are keys
            b. Check that the associated dictionaries contain the necessary keys and only these and that their values are valid.
            c. If any of these checks is not satisfied raise an AssertionError

        Arguments
        ---------
        dico_config : dictionary
            Dictionary providing the content of the indicator parameter file.

        Returns
        -------
        missing_usedmodel_dict_name : list of strings
            Name of the missing dictionary definitions
        unnecessary_model_dict_name : list of strings
            Name of the unnecessary variables defined
        dict_valid            : dictionary of boolean
            keys are model names or self.__name_model_4_indicator_dict and values boolean which indicates is the if the definition is valid.
        error_list                  : list of string
            List of errors detected
        """
        error_list = []
        dict_valid = {}
        # 1.
        if not(self.__name_model_4_indicator_dict in dico_config):
            error_list.append(f"{self.__name_model_4_indicator_dict} should be defined in the indicator parameter file. Defined objects are {list(dico_config.keys())}.")
        # 2
        dict_valid[self.__name_model_4_indicator_dict], errors = self.__check_model_4_indicator_dict(dico_config[self.__name_model_4_indicator_dict])
        error_list.extend(errors)
        # 3 and 4.
        used_models = list(set(dico_config[self.__name_model_4_indicator_dict].values()))
        if None in used_models:
            used_models.remove(None)
        missing_usedmodel_dict_name = [self.__dictname_4_model_indicator[model] for model in used_models]
        model_name_4_model_dict_name = {self.__dictname_4_model_indicator[model]: model for model in used_models}
        model_dict_names_defined = list(dico_config.keys())
        model_dict_names_defined.remove(self.__name_model_4_indicator_dict)
        unnecessary_model_dict_name = []
        nessecary_model_dict_name = []
        for model_dict in model_dict_names_defined:
            if model_dict in missing_usedmodel_dict_name:
                missing_usedmodel_dict_name.remove(model_dict)
                nessecary_model_dict_name.append(model_dict)
            else:
                unnecessary_model_dict_name.append(model_dict)
        # 5.
        for model_dict_name in nessecary_model_dict_name:
            dict_valid[model_name_4_model_dict_name[model_dict_name]], errors = self.__checker_4_indicator_model_dict[model_dict_name](dict_model=dico_config[model_dict_name], dict_model_4_indicator=dico_config[self.__name_model_4_indicator_dict])
            error_list.extend(errors)
        return missing_usedmodel_dict_name, unnecessary_model_dict_name, dict_valid, error_list

    def __check_model_4_indicator_dict(self, model_4_indicator):
        """Validate the model_4_indicator dictionary of the parameter file.

        1. Check that all used indicators sub categories and only these are keys of this dictionary
        2. Check that the associated values are valid models.

        Arguments
        ---------
        model_4_indicator : Dictionary
            Dictionary model_4_indicator as read from the indicator parameter file.

        Returns
        -------
        valid      : boolean
            Say if the content of model_4_indicator is valid
        error_list : list of string
            List of error detected
        """
        error_list = []
        # 1.
        if Counter(list(model_4_indicator.keys())) != Counter(self.indicator_subcategories):
            error_list.append(f"There is an inconsistency in between the list of indicator subcategories ({self.indicator_subcategories}) and the list of keys in the dictionary {self.__name_model_4_indicator_dict}.")
        # 2.
        for inst_subcat, model in model_4_indicator.items():
            if not self.is_valid_indicator_model(model=model):
                error_list.append(f"{model} provided for indicator {inst_subcat} is not a valid indicator model.")
        return len(error_list) == 0, error_list

    def __load_model_4_indicator_dict(self, model_4_indicator):
        """Load the model_4_indicator dictionary of the parameter file.

        Arguments
        ---------
        model_4_indicator : Dictionary
            Dictionary model_4_indicator as read from the indicator parameter file.
        """
        self.__model_4_indicator = model_4_indicator

    def load_instcat_paramfile(self, answer_recreate=None):
        """Load the param file for indicators.
        """
        assert len(self.indicator_models_used) > 0, "There should be a model used by default."
        missing_usedmodel_dict_name = self.indicator_models_used
        unnecessary_model_dict_name = []
        while (len(missing_usedmodel_dict_name) > 0) or (len(unnecessary_model_dict_name)):
            dico_config = self.read_IND_param_file()
            missing_usedmodel_dict_name, unnecessary_model_dict_name, dict_valid, error_list = self.__check_IND_param_file(dico_config)
            if len(error_list) > 0:
                inconsistency = True
                logger.warning(f"The following errors have been spotted in the indicator parameter file: {error_list}")
            else:
                inconsistency = False
            if dict_valid[self.__name_model_4_indicator_dict]:
                self.__load_model_4_indicator_dict(dico_config[self.__name_model_4_indicator_dict])
            dict_valid.pop(self.__name_model_4_indicator_dict)
            for model, valid in dict_valid.items():
                if valid:
                    self.__load_text_indicator_methods[model](dico_config[self.__dictname_4_model_indicator[model]])
            if len(missing_usedmodel_dict_name) > 0:
                logger.warning(f"The dictionary to parametrize the following indicator models are missing in the indicator parameter file: {missing_usedmodel_dict_name}")
                inconsistency = True
            if len(unnecessary_model_dict_name) > 0:
                logger.warning(f"There is unnecessary objects defined in the indicator parameter file: {unnecessary_model_dict_name}")
                inconsistency = True
            if inconsistency:
                l_answers = ['y', 'n']
                if answer_recreate is None:
                    rep = QCM_utilisateur("There is some inconsistencies in the indicator parameter file (see warnings above). Do you want to recreate it from current valid inputs. 'n' would mean triggering an error\n", l_answers)
                else:
                    if answer_recreate not in l_answers:
                        raise ValueError(f"The provided answer_recreate is not valid. Should be in {l_answers}, got {answer_recreate}")
                    else:
                        rep = answer_recreate
            else:
                rep = "n"
            if inconsistency and (rep == "n"):
                raise ValueError(f"The content of the indicator parameter file is not valid. Here is the list of detected errors: {error_list}")
            elif inconsistency and (rep == "y"):
                self.create_IND_param_file(paramfile_path=self.paramfile4instcat[IND_inst_cat], answer_overwrite="y", answer_create=None)
                input("Modify the IND specific paramerisation file: {}".format(self.paramfile4instcat[IND_inst_cat]))

    @property
    def model_4_indicator(self):
        """Dictionary giving the model to use for each indicator.

        keys are indicator sub categories, values are indicator models.

        It is initialised in __init__ of IndicatorModelInterface and updated in __load_model_4_indicator_dict called by load_IND_param_file
        """
        return self.__model_4_indicator

    @property
    def isdefined_INDparamfile(self):
        """Return True is the attribute param_file has been defined."""
        return self.isdefined_paramfile_instcat(inst_cat=IND_inst_cat)

    @property
    def indicator_fullcategories(self):
        """Return all indicator full categories in the current model.
        """
        list_indicator_fullcategories = []
        for inst_fullcat in self.inst_fullcategories:  # self.instfullcategories is from InstrumentContainerInterface Interface class of Core_Model
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

    def is_valid_indicator_model(self, model):
        """Validate a model as an indidator model

        Arguments
        ---------
        model : str or None
            String giving the model that you want to validate

        Returns
        -------
        valid : boolean
            True is model is a valid indicator model, False otherwise
        """
        return (model in self.available_models_4_indicators) or (model is None)

    @property
    def available_models_4_indicators(self):
        """Return all indicator full categories in the current model.
        """
        return self.__available_models_4_indicators__

    @property
    def indicator_subcategories_4_model_used(self):
        """Dictionary giving the indicator subcategories modeled by each model.

        Keys are indicator models
        Values are a list of indicator sub categories
        """
        res = OrderedDict()
        for model in self.indicator_models_used:
            res[model] = []
        for inst_subcat, model in self.model_4_indicator.items():
            res[model].append(inst_subcat)
        return res

    @property
    def indicator_models_used(self):
        """List of indicator model used.
        """
        ll = list(set(self.model_4_indicator.values()))
        ll.sort()
        return ll

    @property
    def params_indicator_models(self):
        """Dictionary giving the parameters for each indicator model used

        Keys: Indicator model name
        Values: Dictionary giving the parameter of this model for each indicator sub category using this model§
            Keys: Indicator sub category
            Values: Dictionary giving the parameter of the model for this indicator sub category
                Keys: Parameter name
                Values: Parameter value

        Initialised in __init__ of IndicatorModelInterface
        Updated in __load_model_4_indicator_dict and all methods in __load_text_indicator_methods
        """
        return self.__params_indicator_models

    def __create_text_polynomial_model(self):
        """Create the string giving the polynomial dictionary for the parameter file.
        """
        text = f"{self.__dictname_4_model_indicator[self._polynomial_method_name]} = {{"
        tab = spacestring_like(text)
        for ii, inst_subcat in enumerate(self.indicator_subcategories_4_model_used[self._polynomial_method_name]):
            if ii != 0:
                text += f"\n{tab}"
            text += f"'{inst_subcat}': {{'{self._polynomial_order_name}': {self.params_indicator_models[self._polynomial_method_name][inst_subcat][self._polynomial_order_name]}}},"
        text += f"\n{tab}}}\n"
        return text

    def __check_polynomial_model(self, dict_model, dict_model_4_indicator):
        """Check the content of polynomial model dictionary from the indicator parameter file.

        1. Check that all indicator sub categories modeled by this model and only these are keys
        2. Check that the associated dictionaries contain the necessary keys and only these and that their values are valid.

        Arguments
        ---------
        dict_model             : dictionary
            Dictionary parametrizing the polynomial models as read from the indicator parameter file.
        dict_model_4_indicator :
            Model_4_indicator diction as read from the indicator parameter file.

        Returns
        -------
        valid      : boolean
            Say if the content of Dictionary parametrizing the polynomial models (dict_model) is valid
        error_list : list of string
            List of error detected
        """
        error_list = []
        # 1.
        indicators_using_model = []
        for indicator_subcat, model in dict_model_4_indicator.items():
            if model == self._polynomial_method_name:
                indicators_using_model.append(indicator_subcat)
        if Counter(indicators_using_model) != Counter(list(dict_model.keys())):
            error_list.append(f"There is an inconsistency between the indicators using the polynomial model ({indicators_using_model}) and the list of keys in the dictionary to parameter the polynomial models ({list(dict_model.keys())})")
        # 2.
        for indicator_subcat in indicators_using_model:
            # Check the presence of all parameters
            dict_indicator = dict_model[indicator_subcat]
            if Counter(list(dict_indicator.keys())) != Counter(self._default_param_values_4_indicator_model[self._polynomial_method_name].keys()):
                error_list.append(f"There is an inconsistency between the parameters provided for the polynomial model of {indicator_subcat} ({list(dict_indicator.keys())}) and the expected list of parameters ({self._default_param_values_4_indicator_model[self._polynomial_method_name].keys()})")
            # Check values of all parameters
            if not isinstance(dict_indicator[self._polynomial_order_name], int):
                error_list.append(f"Parameter {dict_indicator[self._polynomial_order_name]} for the polynomial model of {indicator_subcat} should be an int.")
            elif dict_indicator[self._polynomial_order_name] < 0:
                error_list.append(f"Parameter {dict_indicator[self._polynomial_order_name]} for the polynomial model of {indicator_subcat} should be positive or null.")
        return len(error_list) == 0, error_list

    def __load_text_polynomial_model(self, dict_model):
        """Load the polynomail model

        Arguments
        ---------
        dict_model : dictionary
            Dictionary parametrizing the polynomial models as read from the indicator parameter file.
        """
        self.params_indicator_models[self._polynomial_method_name] = dict_model
