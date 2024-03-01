"""
core_noise_model module.

The objective of this module is to define the Core_NoiseModel Class. This module also provide
the GaussianNoiseModel.
The noise model has to set the parameterisation (add new parameters if needed, for example the
jitter parameters or the GP parameters) and provide the way the likelihood is computed.

@DONE:
    -

@TODO:
    -
"""
from loguru import logger
from collections.abc import Iterable
from numpy import sum as npsum
from numpy import log as nplog
from collections import defaultdict

from ..config_file import ConfigFileAttr, ConfigFile
from ....tools.metaclasses import MandatoryReadOnlyAttr
from ....tools.default_folders_data_run import RunFolderAttr, RunFolder
from ....tools.metaclasses import MandatoryReadOnlyAttr


class Core_Noise_Model(RunFolderAttr, ConfigFileAttr, metaclass=MandatoryReadOnlyAttr):

    # should provide the way to compute the likelihood somehow
    __mandatoryattrs__ = ["noise_cat", "has_GP", "has_jitter", "l_model_class", "l_required_datasetkwarg_keys"]


    def __init__(self, model_instance, run_folder, config_file):
        # Init the run_folder
        if not(isinstance(run_folder, RunFolder)):
            raise ValueError("run_folder should be a RunFolder instance, the one defined for the Posterior intance (Posterior.run_folder)")
        RunFolderAttr.__init__(self, run_folder=run_folder)
        # Init the config_folder
        if not(isinstance(config_file, ConfigFile)):
            raise ValueError("config_file should be a ConfigFile instance, the one defined for the Posterior intance (Posterior.config_file)")
        ConfigFileAttr.__init__(self, config_file=config_file)
        # set model_instannce
        self.__model_instance = model_instance
        # Define the classes of noise models available
        self.__model_classes = {model.category: model for model in self.l_model_class}
        # set the configuration. 
        # If None it that there is nothing to configure otherwise you should create a configuration dictionary
        self._models_config = None

    @property
    def model_instance(self):
        """Return True is the param_file of the instrument category has been defined."""
        return self.__model_instance

    @property
    def model_classes(self):
        """Dictionary with defines the available models. Keys are model_category and value are the
        model classes (subclasses of PlanetStarModel)"""
        return self.__model_classes

    @property
    def l_available_model_category(self):
        """List of available model category (list of str or None)"""
        return list(self.model_classes.keys())

    def _is_available_model_category(self, model_category):
        """Return True if the model_category provided is amongst the available model categories.

        If no list of available model categories have been provided, this function always returns True.

        Argument
        --------
        model_category  : str

        Return
        ------
        isavailable : bool
        """
        return model_category in self.l_available_model_category
    
    ######################################
    ## Dealing with the configuration file
    ######################################

    def _configure_noisemodcat_model(self, ask_before_adding=False, **kwargs):
        """Apply the parametrisation for the noise model

        This method is called by Core_Model._configure_noisemodel
        """
        raise NotImplementedError("You need to overload this function in the sub class")
        
    ###################################################################
    ## Dealing with the instrument model using the noise model category
    ###################################################################

    def get_instmod(self, sortby_instfullcat=False):
        """Return the list of instrument model object that uses the noise model category
        """
        l_instmod = self.model_instance.get_instmodobjs_using_noisemod(noisemod_cat=self.noise_cat)
        if sortby_instfullcat:
            d_instmod = defaultdict(list)
            for instmod in l_instmod:
                d_instmod[instmod.instrument.full_category].append(instmod)
            return d_instmod
        else:
            return l_instmod
        
    @property
    def l_inst_model_fullname(self):
        """List of instrument full names that use the noise model category"""
        return [instmod_obj.full_name for instmod_obj in self.get_instmod(sortby_instfullcat=False)]

    ###################################
    ## Dealing with the parametrisation
    ###################################

    def set_parametrisation(self):
        """Add in the model the necessary main parameters for the noise model.

        This function is called by Core_Model._set_noisemodelcat_parameterisation which is called by Core_Model.set_parametrisation.
        """
        raise NotImplementedError("You need to implement a set_parametrisation method for your "
                                  f"noise model {self.__class__}.")

    def check_parametrisation(self):
        """Check the parameteristion for the noise model.

        :param Core_Model model_instance: Instance of Core_Model or a subclass of it. Mandatory for
            noise model which requires parameter of the object studied (like GP and stellar
            activity)
        :param string instmod_fullname: Full name of the instrument involved in the noise model and
            for which you want to apply the parametrisation for the noise modelling.
        """
        raise NotImplementedError("You need to implement a check_parametrisation method for your "
                                  "noise model.")
    
    #######################################
    ## Dealing with the likelihood function
    #######################################

    def create_lnlikelihood_and_formatinputs(self, l_idx_simdata, l_instmod_obj, l_dataset_obj,
                                             l_datasetkwargs_req, dataset_kwargs, datasim_has_multioutputs,
                                             function_builder, function_shortname, l_paramsfullname_datasim):
        """Create the prefilled lnlikehood function (without the datasim) for the noise model and provide the function to format the inputs and provide the dataset_kwargs

        This function might not be convenient for your noise model, in wich case you should overload it.

        The these output are then used by Core_likelihood.__likelihood_creator
        to finalise the lnlikelihood. In this function the pre-filled lnlikelihood for each noise model is used as follow:
        lnlike_function(sim_data=f_format_simdata(sim_data),
                        param_noisemod=f_format_param(p),
                        l_datakwargs=datasets_kwargs)

        Arguments
        ---------
        model_instance              : Core Model subclass
        l_idx_simdata               : list of Integers
            List of indexes in the sim_data list (output of the datasimulator function this likelihood function is associated with) which correspond to dataset that should be modeled with this noise model
        l_instmod_obj               : list of Instrument_Model instances
            List of instrument model objects that are used for the sim_data elements using this noise model (whose indexes are given by l_idx_datasim).
        l_dataset_obj               : list of Dataset instances
            List of dataset objects that are simulated by the sim_data elements using this noise model (whose indexes are given by l_idx_datasim).
        l_datasetkwargs_req         : list of list of string
            Give for each dataset obj, the list of datasetkwarg required
        dataset_kwargs              : dict of dict or array
            Dictionnary providing the content of all datasets
            Format: {<dataset_name>: {<kwarg like "time", or "flux", etc>: vector corresponding to the kwarg}}
            Some noise models (like GPs) require some kwarg vectors (like time) to be sorted. This argument is there to allow the function
            to perform this sorting prior to the creation of the likelihood function and hardcode the result.
        l_likelihood_param_fullname : list of String
            Current list of parameter full names for the likelihood.
        datasim_has_multioutputs    : bool
            Indicate if the datasim has multiple outputs: Yes (True) or No (False). This can impact the f_format_simdata function.

        Returns
        -------
        lnlike_function                 : function
            function with the following arguments
                sim_data         : sim_data using this noise model, and only these, the exact format is defined by f_format_simdata
                param_noisemodel : param of the current noise model, and only these, the exact format is defined by f_format_param
                dataset_kwargs   : dataset keyword arguments used by this noise model, and only these, the exact format is defined by this function.
        f_format_param                  : function
            Function to extract and format the parameter of this noise model from the vector of all the parameters of the likelihood function
        f_format_simdata                : function
            Function extract and format the simulated data of the datasets using this noise model.
        f_format_dataset_kwargs         : function
            Dataset keyword arguments of the datasets using this noise model
        l_likelihood_param_fullname_new : list of String
            New list of parameter full names for the likelihood which the l_likelihood_param_fullname +  the parameters for this noise model
        """
        lnlike_all, dico_params_noisemod, dico_idx_datasim, dico_idx_l_dataset_obj = self._get_prefilledlnlike(l_instmod_obj=l_instmod_obj, l_idx_simdata=l_idx_simdata, function_builder_all=function_builder, 
                                                                                                               function_shortname_all=function_shortname, l_paramsfullname_datasim=l_paramsfullname_datasim)
        dico_idx_param_noisemod = {}
        for inst_mod_fullname, l_param in dico_params_noisemod.items():
            dico_idx_param_noisemod[inst_mod_fullname] = [function_builder.get_index_4_parameter(parameter=param, function_shortname=function_shortname) for param in l_param]

        def f_format_param(param_likelihood):
            return {inst_mod_fullname: param_likelihood[l_idx_param_inst_mod] for inst_mod_fullname, l_idx_param_inst_mod in dico_idx_param_noisemod.items()}

        if datasim_has_multioutputs:
            def f_format_simdata(sim_data):
                return {inst_mod_fullname: [sim_data[ii] for ii in idx_simdata_inst_mod] for inst_mod_fullname, idx_simdata_inst_mod in dico_idx_datasim.items()}
        else:
            def f_format_simdata(sim_data):
                return {inst_mod_fullname: [sim_data, ] for inst_mod_fullname in dico_idx_datasim.keys()}

        def f_format_dataset_kwargs(dataset_kwargs):
            return {inst_mod_fullname: [{datasetkwarg: dataset_kwargs[l_dataset_obj[jj].dataset_name][datasetkwarg] for datasetkwarg in l_datasetkwargs_req[jj]} for jj in indexes_l_dataset_obj_inst_mod] for inst_mod_fullname, indexes_l_dataset_obj_inst_mod in dico_idx_l_dataset_obj.items()}

        return lnlike_all, f_format_param, f_format_simdata, f_format_dataset_kwargs

    def create_gpsimulator_and_formatinputs(self, l_instmod_obj, l_dataset_obj, l_datasim_param_fullname):
        """Create the prefilled gp_simulator function (without the datasim) for the dataset provided and provide the function to format the inputs

        WARNING: This function doesn't seem to be required as this is usefull only of one try to do a gp
        simulator for a list of instrument model that are not modeled by the same GP model. Which I didn't had
        to do. 

        This function might not be convenient for your noise model, in wich case you should overload it.

        The these output are then used by emcee_tools.compute_model function
        to compute the model of the dataset. In this function the gp simulator is used as follow:
        gp_sim_function(sim_data=sim_data,
                        param_noisemodel=f_format_param(p),
                        datasets_kwargs=datasets_kwargs,
                        tsim=tsim)

        Arguments
        ---------
        model_instance            : Core Model subclass
        l_instmod_obj             : list of Instrument_Model instances
            List of instrument model objects that are used for the sim_data elements using this noise model (whose indexes are given by l_idx_datasim).
        l_dataset_obj             : list of Dataset instances
            List of dataset objects that are simulated by the sim_data elements using this noise model (whose indexes are given by l_idx_datasim).
        l_datasim_param_fullname  : list of String
            Current list of parameter full names for the likelihood.

        Returns
        -------
        gpsimulator_function  : function
            function with the following arguments
                sim_data         : sim_data using this noise model, and only these, the exact format is defined by f_format_simdata
                param_noisemodel : param of the current noise model, and only these, the exact format is defined by f_format_param
                dataset_kwargs   : dataset keyword arguments used by this noise model, and only these, the exact format is defined by this function.
        f_format_param   : function
            Function to extract and format the parameter of this noise model from the vector of all the parameters of the likelihood function
        datasets_kwargs  : ??
            Dataset keyword arguments of the datasets using this noise model
        l_datasim_param_fullname_new : list of String
            New list of parameter full names for the likelihood which the l_likelihood_param_fullname +  the parameters for this noise model
        """
        if self.has_GP:
            raise NotImplementedError("You need to implement create_gpsimulator_and_formatinputs in your Noise model subclass has it involves a GP.")
        else:
            raise ValueError("This noise model doesn't include a GP, you should not call this method for this noise model.")

    def _get_prefilledlnlike(self, l_instmod_obj, l_idx_simdata, function_builder_all, function_shortname_all):
        """Return a ln likelihood function prefilled with the fixed parameters.

        This function is used by LikelihoodCreator.Core_model._create_lnlikelihood()

        Arguments
        ---------
        l_instmod_obj           : Instrument_Model/list_of_InstrumentModel
            instrument model for the ln likelihood to produce.
        l_idx_simdata           :
        function_builder_all    :
        function_shortname_all  :

        Returns  l_params_new, l_params_noisemod, l_idx_param_noisemod
        -------
        prefilled_lnlike        : function
            Prefilled ln likelihood function with as arguments:
                - sim_data: the simulated data required (the format can be anything as it is specified by
                    the f_format_simdata generated by create_lnlikelihood_and_formatinputs)
                - param_noisemod: the values for free parameters of the noise model required (the format
                    can be anything as it is specified by the f_format_simdata generated by create_lnlikelihood_and_formatinputs)
                - datasets_kwargs: the dataset kwargs required (the format can be anything as it is
                    specified by the f_format_simdata generated by create_lnlikelihood_and_formatinputs)
            and returns the ln posterior value
        l_params_new            : list_of_string
            Updated list of parameters full names.
        l_params_noisemod       : list_of_string
            list of the parameters full names for the noise model only.
        l_idx_param_noisemod    : list_of_int
            List of the index of the noise model parameters in the updated list of parameters (l_params_new).
        """
        raise NotImplementedError("You need to ovewrite the _get_prefilledlnlike method for your "
                                  "noise model.")

    def _check_l_instmod_obj(self, l_instmod_obj):
        """Check the l_instmod_obj parameter.

        :param Instrument_Model/list_of_InstrumentModel l_instmod_obj: Instument model or list of
            instrument model for the ln likelihood to produce.
        :return list_of_InstrumentModel l_instmod_obj_new: Return a checked list of instrument model
            object
        """
        from ..dataset_and_instrument.instrument import Instrument_Model
        if isinstance(l_instmod_obj, Instrument_Model):
            return [l_instmod_obj]
        elif isinstance(l_instmod_obj, Iterable):
            if isinstance(l_instmod_obj[0], Instrument_Model):
                return l_instmod_obj
        raise ValueError("l_instmod_obj should be an Instrument_Model or an Iterable of "
                         "Instrument_Models")
    
    def get_jitter_model(self, inst_model_fullname):
        """Get the jitter model for a given instrument model full name.
        Argument
        --------
        inst_model_fullname :

        Return
        ------
        jitter_model    : GaussianModel instance
        """
        if self.has_jitter:
            raise NotImplementedError("You need to override this method in the SubClass !")
        else:
            raise NotImplementedError("This noise model subclass doesn't have jitter. You should not be calling this function")

    # def _update_lists_params(self, l_params_lnlike, l_params_noisemod, l_idx_param_noisemod,
    #                          param_obj):
    #     """Update the list of parameters of the lnlike and the noise model adding the parameter if necessary.

    #     This is a convenience function to be used in the subclass and especially in the _get_prefilledlnlike methods to properly update the list of parameters.

    #     Arguments
    #     ---------
    #     l_params_lnlike      : list of String
    #         Current list of parameters full names for the lnlikehood function.
    #     l_params_noisemod    : list of String
    #         Current list of parameters full names for the noise model only.
    #     l_idx_param_noisemod : List of Integer
    #         List of the index of the noise model parameters in the updated list of parameters (l_params_new).
    #     param_obj            : Parameter
    #         Parameter object that might be added to the lists of parameters

    #     Returns
    #     -------
    #     l_params_lnlike_new      : list of String
    #         Updated list of parameters full names for the lnlikehood function.
    #     l_params_noisemod_new    : list of String
    #         Updated list of parameters full names for the noise model only.
    #     l_idx_param_noisemod_new : List of Integer
    #         Updated List of the index of the noise model parameters in the updated list of parameters (l_params_new).
    #     """
    #     if param_obj.free:
    #         if param_obj.full_name not in l_params_lnlike:
    #             l_params_lnlike_new = l_params_lnlike.copy()
    #             l_params_lnlike_new.append(param_obj.full_name)
    #         else:
    #             l_params_lnlike_new = l_params_lnlike
    #         if param_obj.full_name not in l_params_noisemod:
    #             l_params_noisemod_new = l_params_noisemod.copy()
    #             l_params_noisemod_new.append(param_obj.full_name)
    #             l_idx_param_noisemod_new = l_idx_param_noisemod.copy()
    #             l_idx_param_noisemod_new.append(l_params_lnlike_new.index(param_obj.full_name))
    #         else:
    #             l_idx_param_noisemod_new = l_idx_param_noisemod
    #             l_params_noisemod_new = l_params_noisemod
    #     else:
    #         l_params_lnlike_new = l_params_lnlike
    #         l_idx_param_noisemod_new = l_idx_param_noisemod
    #         l_params_noisemod_new = l_params_noisemod
    #     return l_params_lnlike_new, l_params_noisemod_new, l_idx_param_noisemod_new