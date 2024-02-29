"""Provides the GP1D_Noise_Models classes.

The instance of GP1D_Noise_Models class is used to store the informations of all the GP1D noise models
that are going to be defined in the Model instance.
It stores the Core_GP1DModel subclasses.
There is only on GP1D_Noise_Models instance in a Model instance
"""

from loguru import logger
from numpy import sqrt
from collections import defaultdict, OrderedDict
from pprint import pformat
from textwrap import dedent

# from ..model.celestial_bodies import Star
from ....tools.function_from_text_toolbox import FunctionBuilder
from .core_noise_model import Core_Noise_Model
from ....tools.miscellaneous import spacestring_like
# from ....tools.function_w_doc import DocFunction
from .GP1D_noisemodelconfiguration import george_imported, QPGeorgeModel, QPCGeorgeModel, celerite_imported, QPCeleriteModel, RotationCeleriteModel, SHOCeleriteModel, Matern32CeleriteModel
from .gaussian_noisemodelconfiguration import GaussianModel


class GP1D_Noise_Models(Core_Noise_Model):
    """docstring for GP1D_Noise_Models."""

    __noise_cat__ = "GP1D"
    __has_GP__ = True
    __has_jitter__ = True

    __l_model_class__ = []
    if george_imported:
        __l_model_class__.extend([QPGeorgeModel, QPCGeorgeModel])
    if celerite_imported:
        __l_model_class__.extend([QPCeleriteModel, RotationCeleriteModel, SHOCeleriteModel, Matern32CeleriteModel])

    __l_required_datasetkwarg_keys__ = ["data", "data_err", "time"]

    ################
    # Main functions
    ################
    def __init__(self, model_instance, run_folder, config_file):
        super(GP1D_Noise_Models, self).__init__(model_instance=model_instance, run_folder=run_folder, config_file=config_file)
        self._models_config = self._init_models_config()
        self._define_default_GPmodel()

    @property
    def dict2print(self):
        """Used to print the content in the parametrisation file."""
        dict2print = self._models_config.copy()
        dict2print['GPmodel_definitions'] = dict2print['GPmodel_definitions'].copy()
        for model_name in dict2print['GPmodel_definitions']:
            dict2print['GPmodel_definitions'][model_name] = dict2print['GPmodel_definitions'][model_name].dict2print            
        dict2print['jittermodel_definitions'] = dict2print['jittermodel_definitions'].copy()
        for inst_model_fullname in dict2print['jittermodel_definitions']:
            dict2print['jittermodel_definitions'][inst_model_fullname] = dict2print['jittermodel_definitions'][inst_model_fullname].dict2print
        return dict2print

    def get_GP_model(self, inst_model_fullname):
        """Get the model for a given instrument model full name.
        """
        if inst_model_fullname not in self.l_inst_model_fullname:
            raise ValueError(f"The instrument model name provided ({inst_model_fullname}) doesn't exist or is not defined to be modeled with a GP1D noise model")
        model_name = self._models_config['GPmodel4instrument'][inst_model_fullname]
        return self._models_config['GPmodel_definitions'][model_name], model_name
    
    def get_jitter_model(self, inst_model_fullname):
        """Get the model for a given instrument model full name.
        """
        if inst_model_fullname not in self.l_inst_model_fullname:
            raise ValueError(f"The instrument model name provided ({inst_model_fullname}) doesn't exist or is not defined to be modeled with a GP1D noise model")
        return self._models_config['jittermodel_definitions'][inst_model_fullname]
    
    def get_l_datasetname_4_GP_name(self, GP_name):
        """ Get the list of dataset names that are modelled by a given GP

        Argument
        --------
        GP_name : str
            Name given to the GP that you are insterested in

        Return
        ------
        l_datasetname   : list of str
            List of the names of the datasets that are modelled by the GP designated by GP_name
        """
        # Get the list of the instrument model full name that are modelled by the GP
        l_inst_model_fullname = []
        for inst_mod_fullname_i, GP_name_i in self._models_config['GPmodel4instrument'].items():
            if GP_name_i == GP_name:
                l_inst_model_fullname.append(inst_mod_fullname_i)
        if len(l_inst_model_fullname) == 0:
            if GP_name in self._models_config['GPmodel_definitions']:
                raise ValueError(f"The GP1D model named {GP_name} is defined but it is not used by any instrument model.")
            else:
                raise ValueError(f"There is no GP1D model named.")
        # From l_inst_model_fullname get the list of dataset name that uses the instrument models in the list and thus the GP
        l_dataset_name = []
        for inst_mod_fullname in l_inst_model_fullname:
            l_dataset_name.extend(self.model_instance.get_ldatasetname4instmodfullname(instmod_fullname=inst_mod_fullname)) # get_ldatasetname4instmodfullname is a method of Instmodel4DatasetAttr Parent class of Core_Model
        return l_dataset_name
    
    ################################
    # Dealing with the configuration
    ################################

    # Required by the __init__ method
    #################################

    def _init_models_config(self):
        return  {'GPmodel4instrument': {instmodfullname: '' for instmodfullname in self.l_inst_model_fullname},
                 'GPmodel_definitions': {},
                 'jittermodel_definitions': {instmodfullname: GaussianModel(model_name='', instrument=self.model_instance.instruments[instmodfullname], dico_config_model=None) for instmodfullname in self.l_inst_model_fullname},
                 }

    def _define_default_GPmodel(self):
        # By default all instruments of a given inst_fullcat are modeled by one QPGeorge model.
        for inst_fullcat, l_instmod in self.get_instmod(sortby_instfullcat=True).items():
            model_name = f"{inst_fullcat}"
            for instmod in l_instmod:
                self._models_config['GPmodel4instrument'][instmod.full_name] = model_name
            self._define_GPmodel(model_name=model_name, model_category=self.l_model_class[0].category, dico_config_model=None, overwrite=False)
    
    def _define_GPmodel(self, model_name, model_category, dico_config_model=None, overwrite=False):
        """Define the model for the planet

        Arguments
        ---------
        model_name                     : str
            Name of the GP1D model that you want to define
        model_category                  : str
            GP1D Category
        dico_config_model               : dict
            Dictionary provide arguments for the GP1D model.
        overwrite                       : bool
            Wheter or not you wish to overwrite if the model is already defined
        """
        if not(overwrite) and (model_name in self._models_config["GPmodel_definitions"]):
            raise ValueError(f"A model of name {model_name} already exists and overwrite is False.")
        if not(self._is_available_model_category(model_category=model_category)):
            raise ValueError(f"{model_category} is not in the list of available model categories ({self.l_available_model_category}).")
        (self._models_config["GPmodel_definitions"]
         [model_name]) = self.model_classes[model_category](model_name=model_name, model_instance=self.model_instance, dico_config_model=dico_config_model)
        
    def _delete_GPmodel(self, model_name):
        """Define the model for the planet

        Arguments
        ---------
        model_name                     : str
            Name of the GP1D model that you want to define
        """
        self._models_config["GPmodel_definitions"].pop(model_name)
        self.model_instance.rm_a_GP1D(name=model_name)


    # Configure the gaussian noise models
    #####################################
    def _configure_noisemodcat_model(self, ask_before_adding=False, **kwargs):
        """Apply the parametrisation for the noise model

        This method is called by Core_Model._configure_noisemodel
        """
        self._load_config(config2load='gp', ask_before_adding=ask_before_adding)

    # Function that get the function required by  ConfigFileAttr._load_config
    #########################################################################

    def _get_function_config(self, function_type, config2load):
        if function_type == 'add_default_config':
            if config2load == 'gp':
                return self.__add_default_config_var_gp
        elif function_type == 'check_config_exists':
            if config2load == 'gp':
                return self.__config_var_exist_gp
        elif function_type == 'load_config_content':
            if config2load == 'gp':
                return self.__load_config_var_content_gp
        raise ValueError(f"Either the function_type (you provided {function_type}) or the config2load (you provided {config2load}) is invalid")

    # Methods for the noise model definition part of the config file
    ################################################################
    def __add_default_config_var_gp(self, file):
        file.write("\n# GP1D noise models"
                   "\n###################\n"
                   )
        tab = spacestring_like('GP1D_models' + " = ")
        file.write("{var} = {content}\n".format(var='GP1D_models',
                                                content=pformat(self.dict2print, compact=True).replace('\n', f'\n{tab}')
                                                )
                   )
        
    def __config_var_exist_gp(self, dico_config_file):
        return 'GP1D_models' in dico_config_file

    def __load_config_var_content_gp(self, dico_config_file, **kwargs):
        GP1D_models_config = dico_config_file['GP1D_models']
        # Check that GP1D_models_config is a dict
        assert isinstance(GP1D_models_config, dict)
        # Check that GP1D_models_config has all the required First level keys.
        if set(GP1D_models_config.keys()) != set(['GPmodel4instrument', 'GPmodel_definitions', 'jittermodel_definitions']):
            raise ValueError(f"The keys of the 'GP1D_models' dictionary should be ['GPmodel4instrument', 'GPmodel_definitions', 'jittermodel_definitions']. You provided {set(GP1D_models_config.keys())}")
        # Check that all the instrument models that were to be associated to a GP1D noise model are in 'GPmodel4instrument'.
        if set(GP1D_models_config['GPmodel4instrument'].keys()) != set(self.l_inst_model_fullname):
            raise ValueError(f"The list of instrument models using a GP1D noise model is {self.l_inst_model_fullname}. It should be the same as the list of instrument model full name in GP1D_models['GPmodel4instrument'] ({GP1D_models_config['GPmodel4instrument']})")
        # Check that all the GP1D models named in the values of 'GPmodel4instrument' are defined in 'GPmodel_definitions'.
        if set(GP1D_models_config['GPmodel4instrument'].values()) != set(GP1D_models_config['GPmodel_definitions'].keys()):
            raise ValueError(f"The list of GP1D model names provided in GP1D_models['GPmodel4instrument'] should match the list of the names of the GP1D models defined in GP1D_models['GPmodel_definitions'].")
        # Check that GP1D_models_config['jittermodel_definitions'] is a dict
        assert isinstance(GP1D_models_config['jittermodel_definitions'], dict)
        # Check that all the instrument models that were to be associated to a GP1D noise model are in 'jittermodel_definitions'.
        assert set(GP1D_models_config['jittermodel_definitions'].keys()) == set(self.l_inst_model_fullname)
        # Load the 'GPmodel4instrument'
        self._models_config['GPmodel4instrument'] = GP1D_models_config['GPmodel4instrument'].copy()
        # Clean the GP1D Container of model instance
        for GP1D_model_name in self.model_instance.l_GP1D_fullname:
            if GP1D_model_name not in GP1D_models_config['GPmodel_definitions'].keys():
                self._delete_GPmodel(model_name=GP1D_model_name)
        # load the config of the GP1D models defined in the configuration
        for GP1D_model_name in GP1D_models_config['GPmodel_definitions']:
            model_category = GP1D_models_config['GPmodel_definitions'][GP1D_model_name].pop("category")
            self._define_GPmodel(model_name=GP1D_model_name, model_category=model_category, dico_config_model=GP1D_models_config['GPmodel_definitions'][GP1D_model_name], overwrite=True)
        # load the jitter model definition
        for instmod_fullname in GP1D_models_config['jittermodel_definitions']:
            jitter_model = self.get_jitter_model(inst_model_fullname=instmod_fullname)
            jitter_model.load_config(dico_config=GP1D_models_config['jittermodel_definitions'][instmod_fullname])
    
    #############################################
    # Dealing with the parameters/parametrisation
    #############################################

    def set_parametrisation(self):
        l_model_done = []
        for instmodfullname in self.l_inst_model_fullname:  # l_inst_model_fullname is defined in Core_Noise_Model
            GP1D_config, _ = self.get_GP_model(inst_model_fullname=instmodfullname)
            if GP1D_config not in l_model_done:
                GP1D_config.create_parameters_and_set_main()
            jitter_config = self.get_jitter_model(inst_model_fullname=instmodfullname)
            jitter_config.create_parameters_and_set_main()       

    ######################################
    # Dealing with the likelihood creation
    ######################################

    def create_lnlikelihood_and_formatinputs(self, l_idx_simdata, l_instmod_obj, l_dataset_obj,
                                             l_datasetkwargs_req, dataset_kwargs, datasim_has_multioutputs,
                                             function_builder, function_shortname, l_paramsfullname_datasim):
        """Create the prefilled lnlikehood function (without the datasim) for the noise model and provide the function to format the inputs and provide the dataset_kwargs

        For a detailed docstring look at Core_NoiseModel.create_lnlikelihood_and_formatinputs

        l_paramsfullname_datasim is not need in this function but is only here for compatibility with other function
        in other subclasses of Core_noise_Models
        """
        (lnlike_allGP1D, dico_params_noisemod, dico_idx_datasim, dico_idx_l_dataset_obj
         ) = self._get_prefilledlnlike(l_instmod_obj=l_instmod_obj, l_idx_simdata=l_idx_simdata, dataset_kwargs=dataset_kwargs, function_builder=function_builder,
                                       function_shortname_allGP1D=function_shortname)

        dico_idx_param_noisemod = {}
        for GP1D_name, l_param in dico_params_noisemod.items():
            dico_idx_param_noisemod[GP1D_name] = [function_builder.get_index_4_parameter(parameter=param, function_shortname=function_shortname) for param in l_param]

        def f_format_param(param_likelihood):
            return {GP1D_name: param_likelihood[l_idx_param_GP1D_mod] for GP1D_name, l_idx_param_GP1D_mod in dico_idx_param_noisemod.items()}

        if datasim_has_multioutputs:
            def f_format_simdata(sim_data):
                return {GP1D_name: [sim_data[ii] for ii in idx_simdata_GP1D_mod] for GP1D_name, idx_simdata_GP1D_mod in dico_idx_datasim.items()}
        else:
            def f_format_simdata(sim_data):
                return {GP1D_name: [sim_data, ] for GP1D_name in dico_idx_datasim.keys()}

        def f_format_dataset_kwargs(dataset_kwargs):
            return {GP1D_name: [{datasetkwarg: dataset_kwargs[l_dataset_obj[jj].dataset_name][datasetkwarg] for datasetkwarg in l_datasetkwargs_req[jj]} for jj in indexes_l_dataset_obj_GP1D_mod] for GP1D_name, indexes_l_dataset_obj_GP1D_mod in dico_idx_l_dataset_obj.items()}

        return lnlike_allGP1D, f_format_param, f_format_simdata, f_format_dataset_kwargs
    
    def _get_prefilledlnlike(self, l_instmod_obj, l_idx_simdata, dataset_kwargs, function_builder, function_shortname_allGP1D):
        """Return a ln likelihood function prefilled with the fixed parameters for all stellar activity model.

        Arguments
        ---------
        l_instmod_obj    : list_of_InstrumentModel
            list of instrument model for the ln likelihood to produce.
        l_idx_simdata            : list of Integers
            List of indexes in the sim_data list (output of the datasimulator function this likelihood function is associated with) which correspond to dataset that should be modeled with this noise model
        dataset_kwargs              : dict of dict or array
            Dictionnary providing the content of all datasets
            Format: {<dataset_name>: {<kwarg like "time", or "flux", etc>: vector corresponding to the kwarg}}
        function_builder     :
        function_shortname_allGP1D   :

        Returns
        -------
        prefilled_lnlike        : function
            Prefilled ln likelohood function with as input parameters
            model the simulated data (array), param_noisemod the free parameters value for the noise
            model, the list of dataset kwargs and returns the ln posterior value
        dico_params_noisemod    : Dictionary of list of String
            Dictionary giving the list of parameter full names for each stellar activity noise model
            keys : Stellar activity model names (as defined in the stellar activity parameter file)
            values : List of the full names of the parameters for each stellar activity noise model.
        dico_idx_datasim        :  Dictionary of list of Integer
            Dictionary giving the indexes of the simulated data in the full sim_data (output of the datasimulator associated with this likelihood) for stellar activity noise model
            keys : Stellar activity model names (as defined in the stellar activity parameter file)
            values : List of the indexes of the simulated data in the full sim_data (output of the datasimulator associated with this likelihood) for stellar activity noise model\
        dico_idx_l_dataset_obj  :  Dictionary of list of Integer
            Dictionary giving the indexes of the dataset_obj in the list of dataset object (l_dataset_obj) for stellar activity noise model
            keys : Stellar activity model names (as defined in the stellar activity parameter file)
            values : List of the indexes of the dataset_obj in the list of dataset object.
        """

        # Go through the instrument models and sort them into GP1D models
        dico_linstmodobj4GP1Dmodname = OrderedDict()
        dico_idx_datasim = {}
        dico_idx_l_dataset_obj = {}
        for jj, (ii, instmod_obj) in enumerate(zip(l_idx_simdata, l_instmod_obj)):
            GP1D_mod, GP1D_mod_name = self.get_GP_model(inst_model_fullname=instmod_obj.full_name)
            if GP1D_mod_name in dico_linstmodobj4GP1Dmodname:
                dico_linstmodobj4GP1Dmodname[GP1D_mod_name].append(instmod_obj)
                dico_idx_datasim[GP1D_mod_name].append(ii)
                dico_idx_l_dataset_obj[GP1D_mod_name].append(jj)
            else:
                dico_linstmodobj4GP1Dmodname[GP1D_mod_name] = [instmod_obj, ]
                dico_idx_datasim[GP1D_mod_name] = [ii, ]
                dico_idx_l_dataset_obj[GP1D_mod_name] = [jj, ]
        
        # Produce a prefilled likelihood for each GP1D noise model
        dico_func = {}
        dico_params_noisemod = {}
        for GP1D_mod_name, l_instmod_obj_GP1D_mod in dico_linstmodobj4GP1Dmodname.items():
            function_shortname_GP1D = f"lnlike_GP1D_{GP1D_mod_name}"
            function_builder.add_new_function(shortname=function_shortname_GP1D, parameters=None, mandatory_args=['sim_data', 'l_datakwargs'],
                                              optional_args=None, full_function_name=None)
            # Add text to account for the impact of the jitters to the error bars
            self.add_text_jitter(l_instmod_obj=l_instmod_obj_GP1D_mod, function_builder=function_builder, l_function_shortname=[function_shortname_GP1D, ], l_function_shortname_add_param_only=[function_shortname_allGP1D, ])
            # Sort the time vector if needed. Most GP framework require a sorted time vector.
            self.sort_time_vector(dataset_kwargs=dataset_kwargs, l_instmod_obj=l_instmod_obj_GP1D_mod, function_builder=function_builder, l_function_shortname=[function_shortname_GP1D, ], l_function_shortname_add_param_only=[function_shortname_allGP1D, ])
            # Do the kernel text, do and return the computation of the ln likelihood and add the corresponding parameters
            GP1D, _ = self.get_GP_model(inst_model_fullname=l_instmod_obj_GP1D_mod[0].full_name)
            # Add the parameters required by the GP model
            GP1D.add_text_lnlike(function_builder=function_builder, l_function_shortname=[function_shortname_GP1D, ], l_function_shortname_add_param_only=[function_shortname_allGP1D, ])
            logger.debug(f"Likelihood of the GP1D model {GP1D_mod_name}:\n {function_builder.get_full_function_text(shortname=function_shortname_GP1D)}")
            exec(function_builder.get_full_function_text(shortname=function_shortname_GP1D), function_builder._get_ldict(function_shortname=function_shortname_GP1D))
            dico_func[GP1D_mod_name] = function_builder._get_ldict(function_shortname=function_shortname_GP1D)[function_builder.get_function_fullname(shortname=function_shortname_GP1D)]
            dico_params_noisemod[GP1D_mod_name] = function_builder.get_free_parameter_vector(function_shortname=function_shortname_GP1D)

        l_GP1D_mod_name = list(dico_linstmodobj4GP1Dmodname.keys())

        def lnlike_allGP1D(sim_data, param_noisemodel, datasets_kwargs):
            """GP1D Ln likelihood including all GP1D models provided

            The GP1D models provided are: {l_GP1D_mod_name}

            Arguments
            ---------
            sim_data                : Dictionary of list of np.array
                dictionary of list of arrays giving the sim_data (simulated data) for each stellar activity noise model
                keys : Stellar activity model names (as defined in the stellar activity parameter file)
                values : list of simulated data array of each datasets simulated by each stellar activity noise model
            param_noisemodel  : Dictionary of np.array
                dictionary of array giving the parameters values for the parameters of each stellar activity noise model
                keys : Stellar activity model names (as defined in the stellar activity parameter file)
                values : array of parameter values for each stellar activity noise model
            datasets_kwargs : dictionary of list of dictionaries
                dictionary of list of dictionaries giving the dataset keyword arguments of the dataset associated with each stellar activity noise model.
                keys : Stellar activity model names (as defined in the stellar activity parameter file)
                values : list of dictionaries of datasets values.
                    keys: "data", "data_err", "t"
                    values: list of array giving these values for each datasets associated with each stellar activity noise model
            """.format(l_GP1D_mod_name=l_GP1D_mod_name)
            res = 0
            for GP1D_mod_name in l_GP1D_mod_name:
                res += dico_func[GP1D_mod_name](p_vect=param_noisemodel[GP1D_mod_name], sim_data=sim_data[GP1D_mod_name], l_datakwargs=datasets_kwargs[GP1D_mod_name])
            return res

        return lnlike_allGP1D, dico_params_noisemod, dico_idx_datasim, dico_idx_l_dataset_obj

    def _get_prefilledgpsim(self, l_instmod_obj, l_dataset_obj):
        """Create the prefilled GP simulator function (without the datasim) for the datasets provided and provide the function to format the inputs.

        All the instrument model provided in l_instmod_obj must use the same GP1D model.
        
        The these output are then used by emcee_tools.compute_model function
        to compute the model of the dataset. In this function the gp simulator is used as follow:
        gp_sim_function(sim_data=sim_data,
                        param_noisemod=param[l_idx_param_gpsim],
                        l_datakwargs=datasets_kwargs,
                        tsim=tsim)
        l_idx_param_gpsim has to be created based in 

        Arguments
        ---------
        l_instmod_obj             : list of Instrument_Model instances
            List of instrument model objects that are used for the sim_data elements using this noise model (whose indexes are given by l_idx_datasim).
        l_dataset_obj             : list of Dataset instances
            List of dataset objects that are simulated by the sim_data elements using this noise model (whose indexes are given by l_idx_datasim).

        Returns
        -------
        gpsim_function  : function
            function with the following arguments
                sim_data         : sim_data using this noise model, and only these, the exact format is defined by f_format_simdata
                param_noisemodel : param of the current noise model, and only these, the exact format is defined by f_format_param
                dataset_kwargs   : dataset keyword arguments used by this noise model, and only these, the exact format is defined by this function.
        datasets_kwargs  : ??
            Dataset keyword arguments of the datasets using this noise model
        l_gp_sim_param_full_name : list of String
            list of parameter full names for the GP simulator
        """
        # Check that all instrument model use the same GP1D model
        l_GP1D_mod_name = []
        for instmod_obj in l_instmod_obj:
            GP1D_mod_config, GP1D_mod_name = self.get_GP_model(inst_model_fullname=instmod_obj.full_name)
            l_GP1D_mod_name.append(GP1D_mod_name)
        if len(set(l_GP1D_mod_name)) != 1:
            raise ValueError(f"Not all instrument models provided and using the same GP1D model. The list GP1D models used is {l_GP1D_mod_name}.")
        
        # Create the function builder for the GP simulator 
        func_builder = FunctionBuilder()
        func_shortname = f"GPsim_{GP1D_mod_name}"
        # Get the list of the parameters instances used by the datasimulator to create the function in the FunctionBuilder
        func_builder.add_new_function(shortname=func_shortname, parameters=None, mandatory_args=['sim_data', 'l_datakwargs', 'tsim'], optional_args=None,
                                      full_function_name=None)
        
        # Add the text to account for the effect of the jitter on the error bars
        self.add_text_jitter(l_instmod_obj=l_instmod_obj, function_builder=func_builder, l_function_shortname=[func_shortname, ])
        # Do the kernel text, do and return the computation of the gp simulation and add the required parameters
        GP1D_mod_config.add_text_gp_simulator(function_builder=func_builder, l_function_shortname=[func_shortname, ])
        logger.debug(f"GP simulator of the GP1D model {GP1D_mod_name}:\n {func_builder.get_full_function_text(shortname=func_shortname)}")
        exec(func_builder.get_full_function_text(shortname=func_shortname), func_builder._get_ldict(function_shortname=func_shortname))
        gpsim_function = func_builder._get_ldict(function_shortname=func_shortname)[func_builder.get_function_fullname(shortname=func_shortname)]
        l_gp_sim_param = func_builder.get_free_parameter_vector(function_shortname=func_shortname)
        l_gp_sim_param_full_name = [param.full_name for param in l_gp_sim_param]

        dataset_kwargs = []
        for dataset in l_dataset_obj:
            dataset_kwargs.append({datasetkwarg: dataset.get_datasetkwarg(datasetkwarg) for datasetkwarg in self.l_required_datasetkwarg_keys})

        return gpsim_function, dataset_kwargs, l_gp_sim_param_full_name

    def add_text_jitter(self, l_instmod_obj, function_builder, l_function_shortname, l_function_shortname_add_param_only=None):
        """Add the text that compute the jitter contribution to the error bars.
        """
        # Set defautl value for l_function_shortname_add_param_only
        if l_function_shortname_add_param_only is None:
            l_function_shortname_add_param_only = []

        # Add the text for to take the jitter into account
        jitter_text = """
        dict_datakwargs = defaultdict(list)
        for datakwargs, compute_jitteredvar, jitter in zip(l_datakwargs, l_compute_jitteredvar, l_jitter):
            dict_datakwargs["time"].append(datakwargs["time"])
            dict_datakwargs["data"].append(datakwargs["data"])
            dict_datakwargs["data_err"].append(sqrt(compute_jitteredvar(data_err=datakwargs["data_err"], jitter=jitter)))
        """
        jitter_text = dedent(jitter_text).replace('\n', '\n    ')

        # Do l_jitter and l_compute_jitteredvar 
        l_jitter = {function_shortname: [] for function_shortname in l_function_shortname + l_function_shortname_add_param_only}
        l_compute_jitteredvar = []
        for instmod_obj in l_instmod_obj:
            jitter_model = self.get_jitter_model(inst_model_fullname=instmod_obj.full_name)
            jitter_param = jitter_model.get_parameters(object_category=None)['instrument']['jitter']
            for function_shortname in l_function_shortname + l_function_shortname_add_param_only:
                function_builder.add_parameter(parameter=jitter_param, function_shortname=function_shortname, exist_ok=True)
                l_jitter[function_shortname].append(function_builder.get_text_4_parameter(parameter=jitter_param, function_shortname=function_shortname))
            l_compute_jitteredvar.append(jitter_model.get_compute_jitteredvar())
        for function_shortname in l_function_shortname:
            function_builder.add_to_body_text(text=f"    l_jitter = [{', '.join(l_jitter[function_shortname])}]", function_shortname=function_shortname)
            function_builder.add_to_body_text(text=jitter_text, function_shortname=function_shortname)
            function_builder.add_variable_to_ldict(variable_name='defaultdict', variable_content=defaultdict, function_shortname=function_shortname , exist_ok=False, overwrite=False)
            function_builder.add_variable_to_ldict(variable_name='sqrt', variable_content=sqrt, function_shortname=function_shortname , exist_ok=False, overwrite=False)
            function_builder.add_variable_to_ldict(variable_name='l_compute_jitteredvar', variable_content=l_compute_jitteredvar, function_shortname=function_shortname , exist_ok=False, overwrite=False)

    def sort_time_vector(self, dataset_kwargs, l_instmod_obj, function_builder, l_function_shortname, l_function_shortname_add_param_only=None):
        """Add the text that compute the jitter contribution to the error bars.


        Arguments
        ----------
        dataset_kwargs              : dict of dict or array
            Dictionnary providing the content of all datasets
            Format: {<dataset_name>: {<kwarg like "time", or "flux", etc>: vector corresponding to the kwarg}}
        """
        # Set defautl value for l_function_shortname_add_param_only
        if l_function_shortname_add_param_only is None:
            l_function_shortname_add_param_only = []

        # Add the text for to take the jitter into account
        jitter_text = """
        dict_datakwargs = defaultdict(list)
        for datakwargs, compute_jitteredvar, jitter in zip(l_datakwargs, l_compute_jitteredvar, l_jitter):
            dict_datakwargs["time"].append(datakwargs["time"])
            dict_datakwargs["data"].append(datakwargs["data"])
            dict_datakwargs["data_err"].append(sqrt(compute_jitteredvar(data_err=datakwargs["data_err"], jitter=jitter)))
        """
        jitter_text = dedent(jitter_text).replace('\n', '\n    ')

        # Do l_jitter and l_compute_jitteredvar 
        l_jitter = {function_shortname: [] for function_shortname in l_function_shortname + l_function_shortname_add_param_only}
        l_compute_jitteredvar = []
        for instmod_obj in l_instmod_obj:
            jitter_model = self.get_jitter_model(inst_model_fullname=instmod_obj.full_name)
            jitter_param = jitter_model.get_parameters(object_category=None)['instrument']['jitter']
            for function_shortname in l_function_shortname + l_function_shortname_add_param_only:
                function_builder.add_parameter(parameter=jitter_param, function_shortname=function_shortname, exist_ok=True)
                l_jitter[function_shortname].append(function_builder.get_text_4_parameter(parameter=jitter_param, function_shortname=function_shortname))
            l_compute_jitteredvar.append(jitter_model.get_compute_jitteredvar())
        for function_shortname in l_function_shortname:
            function_builder.add_to_body_text(text=f"    l_jitter = [{', '.join(l_jitter[function_shortname])}]", function_shortname=function_shortname)
            function_builder.add_to_body_text(text=jitter_text, function_shortname=function_shortname)
            function_builder.add_variable_to_ldict(variable_name='defaultdict', variable_content=defaultdict, function_shortname=function_shortname , exist_ok=False, overwrite=False)
            function_builder.add_variable_to_ldict(variable_name='sqrt', variable_content=sqrt, function_shortname=function_shortname , exist_ok=False, overwrite=False)
            function_builder.add_variable_to_ldict(variable_name='l_compute_jitteredvar', variable_content=l_compute_jitteredvar, function_shortname=function_shortname , exist_ok=False, overwrite=False)