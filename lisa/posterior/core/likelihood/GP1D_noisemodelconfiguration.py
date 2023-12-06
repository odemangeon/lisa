"""Provides the Core_GP1DModel, QPGeorgeModel, QPCGeorgeModel, QPCeleriteModel, RotationCeleriteModel

The instance of the subclasses Core_GP1DModel is use to store the configuration of 1 GP1D model used in the Model instance.
It contain the configuration of a GP1D instance.
These instances are stored in GP1D_Noise_Models
There can be several Core_GP1DModel subclass instances in a Model instances.

The other classes are subclassed of Core_GP1DModel and are each used to store the configuration of 1 specific type of GP1D model.
There can be several instances of each of these subclasses in a Model instance.
Beside the configuration these subclasses also provide the function to create the likelihood and GP simulators
"""
from loguru import logger

from collections import defaultdict
from numpy import concatenate, sqrt
from math import log, pi

try:
    from george import GP
    from george.kernels import ExpSquaredKernel, ExpSine2Kernel, CosineKernel
    george_imported = True
except:
    george_imported = False

try:
    from celerite2 import GaussianProcess
    from celerite2.terms import Term
    celerite_imported = True
except:
    celerite_imported = False

from ..core_1modelconfiguration import Core_1ModelConfig
from .GP1D import GP1D


class Core_GP1DModel(Core_1ModelConfig):

    # Define the likelihood computation and GP simualtor functions

    ##############
    # Main methods
    ##############

    def __init__(self, model_name, model_instance, dico_config_model=None):
        super(Core_GP1DModel, self).__init__(model_name=model_name)
        if model_name in model_instance.l_GP1D_fullname:
            GP1D_paramcontainer = model_instance.GP1Ds[model_name]
        else:
            GP1D_paramcontainer = GP1D(name=model_name)
            model_instance.add_a_GP1D(GP=GP1D_paramcontainer, name=model_name)
        self._object_categories = {'GP': GP1D_paramcontainer}  # This are parameter containers required by the model that host the model parameters
        self.load_config(dico_config=dico_config_model)

    def create_parameters_and_set_main(self, object_category=None):
        super(Core_GP1DModel, self).create_parameters_and_set_main(object_category=object_category)

    #####################
    # Convenience methods
    #####################

    @property
    def GP(self):
        """GP param container"""
        return self.object_categories["GP"]
    
    def log10(self, param_basename):
        """True if the jumping of name param_basename should be log10"""
        if param_basename not in self._get_l_parameter_basename_GP():
            raise ValueError(f"param_basename shoud be in {self._get_l_parameter_basename_GP()}")
        return self.parametrisation["log10"][param_basename]
    
    ############################################################
    # Dealing with the parametrisation, param_extension and args
    ############################################################

    def _set_parametrisation(self, parametrisation=None):
        """ """
        self.parametrisation.update({"log10": {param_basename: False for param_basename in self._get_l_parameter_basename_GP()}})
        if parametrisation is not None:
            for key in parametrisation:
                if key not in ["log10"]:
                    raise ValueError(f"The only possible keys to the 'parametrisation' are 'log10'. You provided {key}.")
                if key == "log10":
                    if not(isinstance(parametrisation[key], dict)):
                        raise ValueError(f"'log10' in parametrisation should be a dictionary. You provided a {type(parametrisation[key])}.")
                    for param_basename in parametrisation[key]:
                        if param_basename not in self._get_l_parameter_basename_GP():
                            raise ValueError(f"The only possible keys to the 'log10' dictionary are {self._get_l_parameter_basename_GP()}. You provided {key}.")
                    if not(isinstance(parametrisation[key][param_basename], bool)):
                        raise ValueError(f"Value of parametrisation[{key}][{param_basename}] should be a bool (got {parametrisation[key][param_basename]})")
                    self.parametrisation[key][param_basename] = parametrisation[key][param_basename]
        super(Core_GP1DModel, self)._set_parametrisation(parametrisation=parametrisation)
    
    ############################################################
    ## Dealing with the parameters and their names for the model
    ############################################################

    # Dealing with parameter basenames
    ##################################

    def _get_function_get_l_parameter_basename(self, object_category):
        if object_category == 'GP':
            return self._get_l_parameter_basename_GP
        super(Core_GP1DModel, self)._get_function_get_l_parameter_basename(object_category=object_category)
    
    def _get_function_get_kwargs_4_get_l_parameter_basename(self, object_category):
        if object_category == 'GP':
            return self._get_kwargs_4_get_l_parameter_basename_default
        super(Core_GP1DModel, self)._get_function_get_kwargs_4_get_l_parameter_basename(object_category=object_category)

    # Dealing with parameter names
    ##############################

    def _get_function_get_parameter_name(self, object_category):
        if object_category == 'GP':
            return self._get_parameter_name_GP
        super(Core_GP1DModel, self)._get_function_get_parameter_name(object_category=object_category)
    
    def _get_function_get_kwargs_4_get_parameter_name(self, object_category):
        if object_category == 'GP':
            return self._get_kwargs_4_get_parameter_name_default
        super(Core_GP1DModel, self)._get_function_get_kwargs_4_get_parameter_name(object_category=object_category)

    def _get_parameter_name_GP(self, param_basename, object_category):
        param_name = param_basename
        if self.log10(param_basename=param_basename):
            param_name = 'log10' + param_name            
        return f"{param_name}{self._get_param_extension(param_basename=param_basename, object_category=object_category)}"
    
    # Deal with creating parameters
    ###############################

    def _get_function_create_parameter(self, object_category):
        if object_category == 'GP':
            return self._create_parameter_default
        super(Core_GP1DModel, self)._get_function_create_parameter(object_category=object_category)

        
    def _get_function_get_kwargs_4_create_parameter(self, object_category):
        if object_category == 'GP':
            return self._get_kwargs_4_create_parameter_default
        super(Core_GP1DModel, self)._get_function_get_kwargs_4_create_parameter(object_category=object_category)

    # Deal with getting parameter
    #############################

    def _get_function_get_parameter(self, object_category):
        if object_category == 'GP':
            return self._get_parameter_default
        super(Core_GP1DModel, self)._get_function_get_parameter(object_category=object_category)

        
    def _get_function_get_kwargs_4_get_parameter(self, object_category):
        if object_category == 'GP':
            return self._get_kwargs_4_get_parameter_default
        super(Core_GP1DModel, self)._get_function_get_kwargs_4_get_parameter(object_category=object_category)
    
    ######################################
    # Dealing with the likelihood creation
    ######################################

    def add_text_compute_lnlike(self, function_builder_allGP1D, function_shortname_allGP1D, function_builder_GP1D, function_shortname_GP1D):
        """Return the text of the GP kernel, the list of all parameters and list of the idx of the noise model parameters

        Parameters
        ----------
        noise_models_GP1D       : GP1D_Noise_Models
        l_params                : list of str
            Current list of parameters full names for the whole likelihood function
        l_params_noisemod       : list of str
            Current list of parameters full names for the noise model part of the likelihood (not the datasimulators)
        l_idx_param_noisemod    : list of int
            Current list of indexes of the the parameters in l_params_noisemod in l_params
        params_noisemod_name    : str
        ldict                   : dict
        function_builder        : 
        function_shortname      :
        """
        raise NotImplementedError("You need to implement this method in each Core_GP1DModel subclass")


class QPGeorgeModel(Core_GP1DModel):

    ## Defined in Rasmussen & Williams 2006: https://ui.adsabs.harvard.edu/abs/2006gpml.book.....R/abstract
    # and Roberts et al 2013: https://ui.adsabs.harvard.edu/abs/2012RSPTA.37110550R/abstract
    # See also amongs others: Nicholson & Aigrain 2022: https://ui.adsabs.harvard.edu/abs/2022MNRAS.515.5251N/abstract"

    __category__ = "QPGeorge"

    # kernel_text = "{amp}**2 * ExpSquaredKernel(metric={tau}) * ExpSine2Kernel(gamma=1/(2 * {gamma}**2), log_period={log_period}) + WhiteKernel(value={jitter}**2)"
    # ldict_kernel = {'ExpSquaredKernel': ExpSquaredKernel, 'ExpSine2Kernel': ExpSine2Kernel}

    ############################################################
    ## Dealing with the parameters and their names for the model
    ############################################################

    # Dealing with parameter basenames
    ##################################
    
    def _get_l_parameter_basename_GP(self):
        return ['A', 'P', 'tau', 'gamma']
    
    ######################################
    # Dealing with the likelihood creation
    ######################################
    
    def add_text_compute_lnlike(self, function_builder_allGP1D, function_shortname_allGP1D, function_builder_GP1D, function_shortname_GP1D):
        """Return the text of the GP kernel, the list of all parameters and list of the idx of the noise model parameters

        Parameters
        ----------
        noise_models_GP1D       : GP1D_Noise_Models
        l_params                : list of str
            Current list of parameters full names for the whole likelihood function
        l_params_noisemod       : list of str
            Current list of parameters full names for the noise model part of the likelihood (not the datasimulators)
        l_idx_param_noisemod    : list of int
            Current list of indexes of the the parameters in l_params_noisemod in l_params
        params_noisemod_name    : str
        ldict                   : dict
        function_builder        : 
        function_shortname      :
        """
        dico = {}
        dico_param = self.get_parameters(object_category=None)
        for param_basename, param in dico_param['GP'].items():
            function_builder_allGP1D.add_parameter(parameter=param, function_shortname=function_shortname_allGP1D, exist_ok=True)
            function_builder_GP1D.add_parameter(parameter=param, function_shortname=function_shortname_GP1D, exist_ok=True)
            dico[param_basename] = function_builder_GP1D.get_text_4_parameter(parameter=param, function_shortname=function_shortname_GP1D)
            if param_basename in ["A", "tau", "gamma"]:
                if self.log10(param_basename=param_basename):
                    dico[param_basename] = f"10**{dico[param_basename]}"
            if param_basename == "P":
                if self.log10(param_basename=param_basename):
                    dico[param_basename] = f"{dico[param_basename]} * log(10)"
                else:
                    dico[param_basename] = f"log({dico[param_basename]})"
        function_builder_GP1D.add_variable_to_ldict(variable_name='log', variable_content=log, function_shortname=function_shortname_GP1D , exist_ok=False, overwrite=False)
        kernel = 1**2 * ExpSquaredKernel(metric=20) * ExpSine2Kernel(gamma=1/(2 * 0.5**2), log_period=log(10))
        gp = GP(kernel, fit_kernel=True, mean=0, fit_mean=False)
        function_builder_GP1D.add_variable_to_ldict(variable_name='gp', variable_content=gp, function_shortname=function_shortname_GP1D , exist_ok=False, overwrite=False)
        tab = "    " 
        # text_return += f"{tab}import pdb; pdb.set_trace()"
        # Result of gp.get_parameter_names()
        # 'kernel:k1:k1:log_constant', 'kernel:k1:k2:metric:log_M_0_0', 'kernel:k2:gamma', 'kernel:k2:log_period'
        text_return = f"{tab}gp.set_parameter_vector([{dico['A']}**2, {dico['tau']}**2, 1/(2 * {dico['gamma']}**2), {dico['P']}], include_frozen=False)\n"
        text_return += f"{tab}gp.compute(concatenate(dict_datakwargs['time']), concatenate(dict_datakwargs['data_err']))\n"
        text_return += f"{tab}return gp.lnlikelihood((concatenate(dict_datakwargs['data']) - concatenate(sim_data)).reshape((-1)), quiet=True)\n"
        function_builder_GP1D.add_to_body_text(text=text_return, function_shortname=function_shortname_GP1D)
        function_builder_GP1D.add_variable_to_ldict(variable_name='concatenate', variable_content=concatenate, function_shortname=function_shortname_GP1D , exist_ok=False, overwrite=False)


class QPCGeorgeModel(Core_GP1DModel):

    ## Defined in Perger et al 2021: https://ui.adsabs.harvard.edu/abs/2021A%26A...645A..58P/abstract
    # However we addopted a parameterisation closer but not exactly equal to Nicholson & Aigrain 2022: https://ui.adsabs.harvard.edu/abs/2022MNRAS.515.5251N/abstract"
    __category__ = "QPCGeorge"

    kernel_text = "{A}**2 * ExpSquaredKernel(metric={tau}) * (ExpSine2Kernel(gamma=1/(2 * {gamma}**2), log_period={log_period}) + {f} * CosineKernel(log_period={log_period} - log(2)))"
    ldict_kernel = {'ExpSquaredKernel': ExpSquaredKernel, 'ExpSine2Kernel': ExpSine2Kernel, 'CosineKernel': CosineKernel}

    ############################################################
    ## Dealing with the parameters and their names for the model
    ############################################################

    # Dealing with parameter basenames
    ##################################

    def _get_l_parameter_basename_GP(self):
        return ['A', 'f', 'P', 'tau', 'gamma']
    
    ######################################
    # Dealing with the likelihood creation
    ######################################
    
    def add_text_compute_lnlike(self, function_builder_allGP1D, function_shortname_allGP1D, function_builder_GP1D, function_shortname_GP1D):
        """Return the text of the GP kernel, the list of all parameters and list of the idx of the noise model parameters

        Parameters
        ----------
        noise_models_GP1D       : GP1D_Noise_Models
        l_params                : list of str
            Current list of parameters full names for the whole likelihood function
        l_params_noisemod       : list of str
            Current list of parameters full names for the noise model part of the likelihood (not the datasimulators)
        l_idx_param_noisemod    : list of int
            Current list of indexes of the the parameters in l_params_noisemod in l_params
        params_noisemod_name    : str
        ldict                   : dict
        function_builder_allGP1D        : 
        function_shortname_allGP1D      :
        """
        dico = {}
        dico_param = self.get_parameters(object_category=None).values()
        for param_basename, param in dico_param['GP'].items():
            function_builder_allGP1D.add_parameter(parameter=param, function_shortname=function_shortname_allGP1D, exist_ok=True)
            function_builder_GP1D.add_parameter(parameter=param, function_shortname=function_shortname_GP1D, exist_ok=True)
            dico[param_basename] = function_builder_GP1D.get_text_4_parameter(parameter=param, function_shortname=function_shortname_GP1D)
            if param_basename in ["A", "tau", "gamma", "f"]:
                if self.log10(param_basename=param_basename):
                    dico[param_basename] = f"10**{dico[param_basename]}"
            if param_basename == "P":
                if self.log10(param_basename=param_basename):
                    dico[param_basename] = f"{dico[param_basename]} * log(10)"
                else:
                    dico[param_basename] = f"log{dico[param_basename]}"
        function_builder_GP1D.add_variable_to_ldict(variable_name='log', variable_content=log, function_shortname=function_shortname_GP1D , exist_ok=False, overwrite=False)
        kernel = 1**2 * ExpSquaredKernel(metric=20) * (ExpSine2Kernel(gamma=1/(2 * 0.5**2), log_period=log(10)) + 0.1 * CosineKernel(log_period=log(10) - log(2)))
        gp = GP(kernel, fit_kernel=True, mean=0, fit_mean=False)
        function_builder_GP1D.add_variable_to_ldict(variable_name='gp', variable_content=gp, function_shortname=function_shortname_GP1D , exist_ok=False, overwrite=False)
        tab = "    " 
        # text_return += f"{tab}import pdb; pdb.set_trace()"
        # Result of gp.get_parameter_names()
        # 'kernel:k1:k1:log_constant', 'kernel:k1:k2:metric:log_M_0_0', 'kernel:k2:k1:gamma','kernel:k2:k1:log_period','kernel:k2:k2:k1:log_constant','kernel:k2:k2:k2:log_period'
        text_return = f"{tab}gp.set_parameter_vector([{dico['A']}**2, {dico['tau']}**2, 1/(2 * {dico['gamma']}**2), {dico['P']}, {dico['f']}, {dico['P']}], include_frozen=False)\n"
        text_return += f"{tab}gp.compute(concatenate(dict_datakwargs['time']), concatenate(dict_datakwargs['data_err']))\n"
        text_return += f"{tab}return gp.lnlikelihood((concatenate(dict_datakwargs['data']) - concatenate(sim_data)).reshape((-1)))\n"
        function_builder_GP1D.add_to_body_text(text=text_return, function_shortname=function_shortname_GP1D)
        function_builder_GP1D.add_variable_to_ldict(variable_name='GP', variable_content=GP, function_shortname=function_shortname_GP1D , exist_ok=False, overwrite=False)
        function_builder_GP1D.add_variable_to_ldict(variable_name='concatenate', variable_content=concatenate, function_shortname=function_shortname_GP1D , exist_ok=False, overwrite=False)


class QPCeleriteModel(Core_GP1DModel):

    __category__ = "QPCelerite"

    # Source Foreman-Mackey et al. 2017. AJ, 154, 220 (equation 56) - https://iopscience.iop.org/article/10.3847/1538-3881/aa9332/meta
    # See also: in Radvel the CeleriteKernel: https://radvel.readthedocs.io/en/latest/gp.html?highlight=jitter#radvel.gp.CeleriteKernel.compute_covmatrix
    # In Celerite the example: https://celerite.readthedocs.io/en/stable/python/kernel/
    # In Celerite2 the example: https://celerite.readthedocs.io/en/stable/python/kernel/
    # The parameterisation is the one of the Foreman-Mackey et al. 2017 paper
    # The implementation is based on the celerite example except that I remove the log in front of the parameters
    
    ############################################################
    ## Dealing with the parameters and their names for the model
    ############################################################

    # Dealing with parameter basenames
    ##################################

    def _get_l_parameter_basename_GP(self):
        return ['B', 'C', 'P', 'L']
    
    ######################################
    # Dealing with the likelihood creation
    ######################################

    class CustomTerm(Term):
        parameter_names = ("B", "C", "L", "P")

        def get_real_coefficients(self, params):
            B, C, L, P = params
            return (
                B * (1.0 + C) / (2.0 + C), 1/L,
            )

        def get_complex_coefficients(self, params):
            B, C, L, P = params
            return (
                B / (2.0 + C), 0.0,
                1/L, 2 * pi / P,
            )
    
    def add_text_compute_lnlike(self, function_builder_allGP1D, function_shortname_allGP1D, function_builder_GP1D, function_shortname_GP1D):
        """Return the text of the GP kernel, the list of all parameters and list of the idx of the noise model parameters

        Parameters
        ----------
        noise_models_GP1D       : GP1D_Noise_Models
        l_params                : list of str
            Current list of parameters full names for the whole likelihood function
        l_params_noisemod       : list of str
            Current list of parameters full names for the noise model part of the likelihood (not the datasimulators)
        l_idx_param_noisemod    : list of int
            Current list of indexes of the the parameters in l_params_noisemod in l_params
        params_noisemod_name    : str
        ldict                   : dict
        function_builder_allGP1D        : 
        function_shortname_allGP1D      :
        """
        dico = {}
        dico_param = self.get_parameters(object_category=None).values()
        for param_basename, param in dico_param['GP'].items():
            function_builder_allGP1D.add_parameter(parameter=param, function_shortname=function_shortname_allGP1D, exist_ok=True)
            function_builder_GP1D.add_parameter(parameter=param, function_shortname=function_shortname_GP1D, exist_ok=True)
            dico[param_basename] = function_builder_GP1D.get_text_4_parameter(parameter=param, function_shortname=function_shortname_GP1D)
            if param_basename in ["A", "tau", "gamma", "f"]:
                if self.log10(param_basename=param_basename):
                    dico[param_basename] = f"10**{dico[param_basename]}"
            if param_basename == "P":
                if self.log10(param_basename=param_basename):
                    dico[param_basename] = f"{dico[param_basename]} * log(10)"
                else:
                    dico[param_basename] = f"log{dico[param_basename]}"
        function_builder_GP1D.add_variable_to_ldict(variable_name='log', variable_content=log, function_shortname=function_shortname_GP1D , exist_ok=False, overwrite=False)
        kernel = self.CustomTerm(B=1, C=1.5, L=20, P=10.0)
        gp = GaussianProcess(kernel, mean=0.0)
        function_builder_GP1D.add_variable_to_ldict(variable_name='gp', variable_content=gp, function_shortname=function_shortname_GP1D , exist_ok=False, overwrite=False)
        tab = "    " 
        # text_return += f"{tab}import pdb; pdb.set_trace()"
        # text_return += f"{tab}import pdb; pdb.set_trace()"
        # Result of gp.get_parameter_names()
        # 
        text_return = f"{tab}gp.set_parameter_vector([{dico['A']}**2, {dico['tau']}**2, 1/(2 * {dico['gamma']}**2), {dico['P']}, {dico['f']}, {dico['P']}], include_frozen=False)\n"
        text_return += f"{tab}gp.compute(t=concatenate(dict_datakwargs['time']), yerr=concatenate(dict_datakwargs['data_err']))\n"
        text_return += f"{tab}return gp.lnlikelihood((concatenate(dict_datakwargs['data']) - concatenate(sim_data)).reshape((-1)))\n"
        function_builder_GP1D.add_to_body_text(text=text_return, function_shortname=function_shortname_GP1D)
        function_builder_GP1D.add_variable_to_ldict(variable_name='GaussianProcess', variable_content=GaussianProcess, function_shortname=function_shortname_GP1D , exist_ok=False, overwrite=False)
        function_builder_GP1D.add_variable_to_ldict(variable_name='concatenate', variable_content=concatenate, function_shortname=function_shortname_GP1D , exist_ok=False, overwrite=False)


class RotationCeleriteModel(Core_GP1DModel):

    __category__ = "RotationCelerite"


    ############################################################
    ## Dealing with the parameters and their names for the model
    ############################################################

    # Dealing with parameter basenames
    ##################################

    def _get_l_parameter_basename_GP(self):
        return ['sigma', 'P', 'Q', 'dQ', 'f']


class SHOCeleriteModel(Core_GP1DModel):

    __category__ = "SHOCelerite"

    ############################################################
    # Dealing with the parametrisation, param_extension and args
    ############################################################

    def _set_parametrisation(self, parametrisation=None):
        """ """
        self.parametrisation.update({'use_rho': True, 'use_Q': True, 'use_sigma': True, 'log10': {'rho/omega0': False, 'Q/tau': False, 'sigma/S0': False}})
        if parametrisation is not None:
            for key in parametrisation:
                if key not in ['use_rho', 'use_Q', 'use_sigma', 'log10']:
                    raise ValueError(f"The only possible keys to the 'parametrisation' are ['use_rho', 'use_Q', 'use_sigma', 'log10']. You provided {key}.")
                if key in ['use_rho', 'use_Q', 'use_sigma']:
                    if not(isinstance(parametrisation[key], bool)):
                        raise ValueError(f"Value of parametrisation[{key}] should be a bool (got {parametrisation[key]})")
                    self.parametrisation[key] = parametrisation[key]
                if key == 'log10':
                    if not(isinstance(parametrisation[key], dict)):
                        raise ValueError(f"'log10' in parametrisation should be a dictionary. You provided a {type(parametrisation[key])}.")
                    for param_basename in parametrisation[key]:
                        if param_basename not in ['rho/omega0', 'Q/tau', 'sigma/S0']:
                            raise ValueError(f"The only possible keys to the 'log10' dictionary are ['rho/omega0', 'Q/tau', 'sigma/S0']. You provided {key}.")
                    if not(isinstance(parametrisation[key][param_basename], bool)):
                        raise ValueError(f"Value of parametrisation[{key}][{param_basename}] should be a bool (got {parametrisation[key][param_basename]})")
                    self.parametrisation[key][param_basename] = parametrisation[key][param_basename]
        super(QPGeorgeModel, self)._set_parametrisation(parametrisation=parametrisation)

    ############################################################
    ## Dealing with the parameters and their names for the model
    ############################################################

    # Dealing with parameter basenames
    ##################################

    def _get_l_parameter_basename_GP(self):
        res = []
        if self.use_sigma:
            res.append('sigma')
        else:
            res.append('S0')
        if self.use_rho:
            res.append('rho')
        else:
            res.append('omega0')
        if self.use_Q:
            res.append('Q')
        else:
            res.append('tau')
        return res

    ######################
    # Convenience function
    ######################

    @property
    def use_sigma(self):
        return self.parameterisation['use_sigma']

    @property
    def use_rho(self):
        return self.parameterisation['use_rho']
    
    @property
    def use_Q(self):
        return self.parameterisation['use_Q']

    def log10(self, param_basename):
        """True if the jumping of name param_basename should be log10"""
        if param_basename not in self._get_l_parameter_basename_GP():
            raise ValueError(f"param_basename shoud be in {self._get_l_parameter_basename_GP()}")
        if param_basename in ["sigma", "S0"]:
            return self.parametrisation["log10"]['sigma/S0']
        elif param_basename in ["rho", "omega0"]:
            return self.parametrisation["log10"]['rho/omega0']
        elif param_basename in ["Q", "tau"]:
            return self.parametrisation["log10"]['Q/tau']


class Matern32Model(Core_GP1DModel):

    __category__ = "Matern32Celerite"

    ############################################################
    ## Dealing with the parameters and their names for the model
    ############################################################

    # Dealing with parameter basenames
    ##################################

    def _get_l_parameter_basename_GP(self):
        return ['sigma', 'rho']
