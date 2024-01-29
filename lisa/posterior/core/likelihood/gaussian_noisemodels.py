"""
noise_model module.

The objective of this module is to define the Core_NoiseModel Class and the standard noise models.

@DONE:
    -

@TODO:
    -
"""
from loguru import logger
from pprint import pformat
from textwrap import dedent
from numpy import sqrt
from collections import defaultdict, OrderedDict

from .core_noise_model import Core_Noise_Model
from .gaussian_noisemodelconfiguration import GaussianModel
from ....tools.miscellaneous import spacestring_like
from ....tools.function_from_text_toolbox import FunctionBuilder


class Gaussian_Noise_Models(Core_Noise_Model):
    """A instance of this class will be created in the Model instance to store the configuration
    of the gaussian noise models used
    """

    __noise_cat__ = "gaussian"
    __has_GP__ = False
    __has_jitter__ = True

    __l_model_class__ = [GaussianModel]

    __l_required_datasetkwarg_keys__ = ["data", "data_err"]

    ################
    # Main functions
    ################
    def __init__(self, model_instance, run_folder, config_file):
        super(Gaussian_Noise_Models, self).__init__(model_instance=model_instance, run_folder=run_folder, config_file=config_file)
        self._models_config = self._init_models_config()

    @property
    def dict2print(self):
        """Used to print the content in the configuration file."""
        dict2print = self._models_config.copy()
        for inst_model_fullname in dict2print:
            dict2print[inst_model_fullname] = dict2print[inst_model_fullname].dict2print
        return dict2print
    
    def get_model(self, inst_model_fullname):
        """Get the model for a given instrument model full name.
        """
        if inst_model_fullname not in self.l_inst_model_fullname:
            raise ValueError(f"The instrument model name provided ({inst_model_fullname}) doesn't exist or is not defined to be modeled with a gaussian noise model")
        return self._models_config[inst_model_fullname]
    
    def get_jitter_model(self, inst_model_fullname):
        """Same than get_model with a different name for consistency across noise models with a jitter term
        """
        return self.get_model(inst_model_fullname=inst_model_fullname)
    
    ################################
    # Dealing with the configuration
    ################################

    # Init the configuration dictionary
    ###################################

    def _init_models_config(self):
        return {instmodfullname: GaussianModel(model_name='', instrument=self.model_instance.instruments[instmodfullname], dico_config_model=None) 
                for instmodfullname in self.l_inst_model_fullname
                }

    # Configure the gaussian noise models
    #####################################
    def _configure_noisemodcat_model(self, ask_before_adding=False, **kwargs):
        """Apply the configuration for the noise model

        This method is called by Core_Model._configure_noisemodel
        """
        self._load_config(config2load='gaussian', ask_before_adding=ask_before_adding)

    # Function that get the function required by  ConfigFileAttr._load_config
    #########################################################################

    def _get_function_config(self, function_type, config2load):
        if function_type == 'add_default_config':
            if config2load == 'gaussian':
                return self.__add_default_config_var_gaussian
        elif function_type == 'check_config_exists':
            if config2load == 'gaussian':
                return self.__config_var_exist_gaussian
        elif function_type == 'load_config_content':
            if config2load == 'gaussian':
                return self.__load_config_var_content_gaussian
        raise ValueError(f"Either the function_type (you provided {function_type}) or the config2load (you provided {config2load}) is invalid")

    # Methods for the noise model definition part of the config file
    ################################################################
    def __add_default_config_var_gaussian(self, file):
        file.write("\n# Gaussian noise models"
                   "\n#######################\n"
                   )
        tab = spacestring_like('gaussian_models' + " = ")
        file.write("{var} = {content}\n".format(var='gaussian_models',
                                                content=pformat(self.dict2print, compact=True).replace('\n', f'\n{tab}')
                                                )
                   )
        
    def __config_var_exist_gaussian(self, dico_config_file):
        return 'gaussian_models' in dico_config_file

    def __load_config_var_content_gaussian(self, dico_config_file, **kwargs):
        gaussian_models_config = dico_config_file['gaussian_models']
        assert isinstance(gaussian_models_config, dict)
        assert set(gaussian_models_config.keys()) == set(self.l_inst_model_fullname)
        for instmod_fullname in gaussian_models_config:
            gaussian_model = self.get_model(inst_model_fullname=instmod_fullname)
            gaussian_model.load_config(dico_config=gaussian_models_config[instmod_fullname])

    #############################################
    # Dealing with the parameters/parametrisation
    #############################################

    def set_parametrisation(self):
        for instmodfullname in self.l_inst_model_fullname:  # l_inst_model_fullname is defined in Core_Noise_Model
            gaussian_model_config = self.get_model(inst_model_fullname=instmodfullname)
            gaussian_model_config.create_parameters_and_set_main()

    ######################################
    # Dealing with the likelihood creation
    ######################################

    def _get_prefilledlnlike(self, l_instmod_obj, l_idx_simdata, function_builder_all, function_shortname_all, l_paramsfullname_datasim):
        """Return a ln likelihood function prefilled with the fixed parameters for all stellar activity model.

        Arguments
        ---------
        l_instmod_obj           : list_of_InstrumentModel
            list of instrument model for the ln likelihood to produce.
        l_idx_simdata           :
        function_builder_all    :
        function_shortname_all  :

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
        nparam_datasim=len(l_paramsfullname_datasim)

        # Function builder for the individual functions of each GP1D
        function_builder_1inst = FunctionBuilder() 

        # Go through the instrument models and sort them
        dico_instmodobj4instmodfullname = OrderedDict()
        dico_idx_datasim = {}
        dico_idx_l_dataset_obj = {}
        for jj, (ii, instmod_obj) in enumerate(zip(l_idx_simdata, l_instmod_obj)):
            if instmod_obj.full_name in dico_instmodobj4instmodfullname:
                dico_idx_datasim[instmod_obj.full_name].append(ii)
                dico_idx_l_dataset_obj[instmod_obj.full_name].append(jj)
            else:
                dico_instmodobj4instmodfullname[instmod_obj.full_name] = instmod_obj
                dico_idx_datasim[instmod_obj.full_name] = [ii, ]
                dico_idx_l_dataset_obj[instmod_obj.full_name] = [jj, ]

        # Produce a prefilled likelihood for each instrument model
        dico_func = {}
        dico_params_noisemod = {}

        lnlikefunc_text = """
        dict_datakwargs = defaultdict(list)
        for datakwargs in l_datakwargs:
            dict_datakwargs["data"].append(datakwargs["data"])
            dict_datakwargs["data_err"].append(sqrt(compute_jitteredvar(data_err=datakwargs["data_err"], jitter={jitter})))
        """
        lnlikefunc_text = dedent(lnlikefunc_text).replace('\n', '\n    ')

        for inst_mod_fullname, instmod_obj in dico_instmodobj4instmodfullname.items():
            function_shortname_1inst = f"lnlike_1inst_{inst_mod_fullname}"
            function_builder_1inst.add_new_function(shortname=function_shortname_1inst, parameters=None, mandatory_args=['sim_data', 'l_datakwargs'],
                                                    optional_args=None, full_function_name=None)
            # Do jitter and compute_jitteredvar
            jitter_model = self.get_model(inst_model_fullname=instmod_obj.full_name)
            jitter_param = jitter_model.get_parameters(object_category=None)['instrument']['jitter']
            function_builder_all.add_parameter(parameter=jitter_param, function_shortname=function_shortname_all, exist_ok=True)
            function_builder_1inst.add_parameter(parameter=jitter_param, function_shortname=function_shortname_1inst, exist_ok=True)
            jitter = function_builder_1inst.get_text_4_parameter(parameter=jitter_param, function_shortname=function_shortname_1inst)
            compute_jitteredvar = jitter_model.get_compute_jitteredvar()
            function_builder_1inst.add_to_body_text(text=lnlikefunc_text.format(jitter=jitter), function_shortname=function_shortname_1inst)
            function_builder_1inst.add_variable_to_ldict(variable_name='defaultdict', variable_content=defaultdict, function_shortname=function_shortname_1inst , exist_ok=False, overwrite=False)
            function_builder_1inst.add_variable_to_ldict(variable_name='sqrt', variable_content=sqrt, function_shortname=function_shortname_1inst , exist_ok=False, overwrite=False)
            function_builder_1inst.add_variable_to_ldict(variable_name='compute_jitteredvar', variable_content=compute_jitteredvar, function_shortname=function_shortname_1inst , exist_ok=False, overwrite=False)
            # Do and return the computation of the ln likelihood
            jitter_model.add_text_compute_lnlike(nparam_datasim=nparam_datasim, function_builder_1inst=function_builder_1inst, function_shortname_1inst=function_shortname_1inst)
            logger.debug(f"Likelihood of the inst model {instmod_obj.full_name}:\n {function_builder_1inst.get_full_function_text(shortname=function_shortname_1inst)}")
            exec(function_builder_1inst.get_full_function_text(shortname=function_shortname_1inst), function_builder_1inst._get_ldict(function_shortname=function_shortname_1inst))
            dico_func[instmod_obj.full_name] = function_builder_1inst._get_ldict(function_shortname=function_shortname_1inst)[function_builder_1inst.get_function_fullname(shortname=function_shortname_1inst)]
            dico_params_noisemod[instmod_obj.full_name] = function_builder_1inst.get_free_parameter_vector(function_shortname=function_shortname_1inst)
        
        l_inst_mod_fullname = list(dico_instmodobj4instmodfullname.keys())

        def lnlike_alljitter(sim_data, param_noisemodel, datasets_kwargs):
            """Gaussian Ln likelihood including all instrument models provided

            The instrument model provided are: {l_inst_mod_name}

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
            """.format(l_inst_mod_name=l_inst_mod_fullname)
            res = 0
            for inst_mod_fullname in l_inst_mod_fullname:
                res += dico_func[inst_mod_fullname](p_vect=param_noisemodel[inst_mod_fullname], sim_data=sim_data[inst_mod_fullname], l_datakwargs=datasets_kwargs[inst_mod_fullname])
            return res

        return lnlike_alljitter, dico_params_noisemod, dico_idx_datasim, dico_idx_l_dataset_obj