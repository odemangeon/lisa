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
    from celerite2.terms import Term, RotationTerm, SHOTerm, Matern32Term
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

    ###################################################################################
    # Dealing with adding the GP parameter to a functions created by a function builder
    ###################################################################################
        
    def _add_GP_parameter_and_get_parameter_text(self, function_builder, l_function_shortname):
        """Add the GP parameters to functions created by a function_builder

        Arguments
        ---------
        function_builder        : FunctionBuilder 
        l_function_shortname    : List of str

        Return
        ------
        dico_text_param : Dict of dict
            Keys are function short names in function_builder (elements of l_function_shortname) values are dictionaries
            whose keys are parameter names and values are text of the parameters to use in the function
        """
        dico = {func_shortname: {} for func_shortname in l_function_shortname}
        dico_param = self.get_parameters(object_category=None)
        for param_basename, param in dico_param['GP'].items():
            for func_shortname in l_function_shortname:
                function_builder.add_parameter(parameter=param, function_shortname=func_shortname, exist_ok=True)
                dico[func_shortname][param_basename] = function_builder.get_text_4_parameter(parameter=param, function_shortname=func_shortname)
                if self.log10(param_basename=param_basename):
                    dico[func_shortname][param_basename] = f"10**{dico[param_basename]}"
                    function_builder.add_variable_to_ldict(variable_name='log', variable_content=log, function_shortname=func_shortname , exist_ok=True, overwrite=False)
        return dico
    
    ######################################
    # Dealing with the likelihood creation
    ######################################
    
    def add_text_lnlike(self, function_builder, l_function_shortname, l_function_shortname_add_param_only=None):
        """Add the text of the GP kernel and the text to return the lnlikelihood

        Parameters
        ----------
        function_builder                    : 
        l_function_shortname                :
        l_function_shortname_add_param_only :
        """
        # Set defautl value for l_function_shortname_add_param_only
        if l_function_shortname_add_param_only is None:
            l_function_shortname_add_param_only = []

        dico_text_param = self._add_GP_parameter_and_get_parameter_text(function_builder=function_builder, l_function_shortname=l_function_shortname + l_function_shortname_add_param_only)
        self._add_text_GP_kernel(dico_text_param=dico_text_param, function_builder=function_builder, l_function_shortname=l_function_shortname)
        self._add_text_compute_lnlike(function_builder=function_builder, l_function_shortname=l_function_shortname)

    def _add_text_compute_lnlike(self, function_builder, l_function_shortname):
        """Add the text of the GP kernel and the text to return the GP simulation/prediction
        """
        raise NotImplementedError(f"You need to implement _add_text_compute_lnlike in class {self.__class__}")
    
    ##################################################
    # Dealing with the GP simulator creation for plots
    ##################################################

    def add_text_gp_simulator(self, function_builder, l_function_shortname):
        """
        """
        dico_text_param = self._add_GP_parameter_and_get_parameter_text(function_builder=function_builder, l_function_shortname=l_function_shortname)
        self._add_text_GP_kernel(dico_text_param=dico_text_param, function_builder=function_builder, l_function_shortname=l_function_shortname)
        self._add_text_compute_gpsim(function_builder=function_builder, l_function_shortname=l_function_shortname)

    def _add_text_compute_gpsim(self, function_builder, l_function_shortname):
        """Add the text of the GP kernel and the text to return the GP simulation/prediction
        """
        raise NotImplementedError(f"You need to implement _add_text_compute_gpsim in class {self.__class__}")

    #############################################
    # Dealing with this the text of the GP kernel
    #############################################

    def _add_text_GP_kernel(self, dico_text_param, function_builder, l_function_shortname):
        """Add the text of the GP kernel and the text to return the GP simulation/prediction
        """
        raise NotImplementedError("You need to implement _add_text_GP_kernel in class {self.__class__}")


class Core_GP1DModel_George(Core_GP1DModel):

    def _add_text_compute_lnlike(self, function_builder, l_function_shortname):
        """Add the text of the GP kernel and the text to return the GP simulation/prediction
        """
        tab = "    " 
        for func_shortname in l_function_shortname:
            text_return = f"\n{tab}gp.compute(t=concatenate(dict_datakwargs['time']), yerr=concatenate(dict_datakwargs['data_err']), quiet=True)\n"
            text_return += f"{tab}return gp.log_likelihood((concatenate(dict_datakwargs['data']) - concatenate(sim_data)).reshape((-1)))\n"
            function_builder.add_to_body_text(text=text_return, function_shortname=func_shortname)
            function_builder.add_variable_to_ldict(variable_name='concatenate', variable_content=concatenate, function_shortname=func_shortname , exist_ok=False, overwrite=False)
    
    def _add_text_compute_gpsim(self, function_builder, l_function_shortname):
        """Add the text of the GP kernel and the text to return the GP simulation/prediction
        """
        tab = "    " 
        for func_shortname in l_function_shortname:
            text_return = f"\n{tab}gp.compute(t=concatenate(dict_datakwargs['time']), yerr=concatenate(dict_datakwargs['data_err']), quiet=True)\n"
            text_return += f"{tab}return gp.predict((concatenate(dict_datakwargs['data']) - concatenate(sim_data)).reshape((-1)), tsim, return_var=True)\n"
            function_builder.add_to_body_text(text=text_return, function_shortname=func_shortname)
            function_builder.add_variable_to_ldict(variable_name='concatenate', variable_content=concatenate, function_shortname=func_shortname , exist_ok=False, overwrite=False)


class QPGeorgeModel(Core_GP1DModel_George):

    ## Defined in Rasmussen & Williams 2006: https://ui.adsabs.harvard.edu/abs/2006gpml.book.....R/abstract
    # and Roberts et al 2013: https://ui.adsabs.harvard.edu/abs/2012RSPTA.37110550R/abstract
    # See also amongs others: Nicholson & Aigrain 2022: https://ui.adsabs.harvard.edu/abs/2022MNRAS.515.5251N/abstract"

    __category__ = "QPGeorge"

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
    
    def _add_GP_parameter_and_get_parameter_text(self, function_builder, l_function_shortname):
        """Add the GP parameters to functions created by a function_builder

        Arguments
        ---------
        function_builder        : FunctionBuilder 
        l_function_shortname    : List of str

        Return
        ------
        dico_text_param : Dict of dict
            Keys are function short names in function_builder (elements of l_function_shortname) values are dictionaries
            whose keys are parameter names and values are text of the parameters to use in the function
        """
        if l_function_shortname_add_param_only is None:
            l_function_shortname_add_param_only = []

        dico = {func_shortname: {} for func_shortname in l_function_shortname}
        dico_param = self.get_parameters(object_category=None)
        for param_basename, param in dico_param['GP'].items():
            for func_shortname in l_function_shortname:
                function_builder.add_parameter(parameter=param, function_shortname=func_shortname, exist_ok=True)
                dico[func_shortname][param_basename] = function_builder.get_text_4_parameter(parameter=param, function_shortname=func_shortname)
                if param_basename in ["A", "tau", "gamma"]:
                    if self.log10(param_basename=param_basename):
                        dico[param_basename] = f"10**{dico[param_basename]}"
                if param_basename == "P":
                    if self.log10(param_basename=param_basename):
                        dico[param_basename] = f"{dico[param_basename]} * log(10)"
                    else:
                        dico[param_basename] = f"log({dico[param_basename]})"
                    function_builder.add_variable_to_ldict(variable_name='log', variable_content=log, function_shortname=func_shortname , exist_ok=True, overwrite=False)
        return dico

    def _add_text_GP_kernel(self, dico_text_param, function_builder, l_function_shortname):
        """Add the text of the GP kernel and the text to return the GP simulation/prediction
        """
        tab = "    " 
        for func_shortname in l_function_shortname:
            kernel = 1**2 * ExpSquaredKernel(metric=20) * ExpSine2Kernel(gamma=1/(2 * 0.5**2), log_period=log(10))
            gp = GP(kernel, fit_kernel=True, mean=0, fit_mean=False)
            function_builder.add_variable_to_ldict(variable_name='gp', variable_content=gp, function_shortname=func_shortname , exist_ok=False, overwrite=False)
            # text_return += f"{tab}import pdb; pdb.set_trace()"
            text_GP_kernel = f"\n{tab}gp.set_parameter_vector([{dico_text_param[func_shortname]['A']}**2, {dico_text_param[func_shortname]['tau']}**2, 1/(2 * {dico_text_param[func_shortname]['gamma']}**2), {dico_text_param[func_shortname]['P']}], include_frozen=False)\n"
            function_builder.add_to_body_text(text=text_GP_kernel, function_shortname=func_shortname)
            function_builder.add_variable_to_ldict(variable_name='ExpSquaredKernel', variable_content=ExpSquaredKernel, function_shortname=func_shortname , exist_ok=True, overwrite=False)
            function_builder.add_variable_to_ldict(variable_name='ExpSine2Kernel', variable_content=ExpSine2Kernel, function_shortname=func_shortname , exist_ok=True, overwrite=False)


class QPCGeorgeModel(Core_GP1DModel_George):

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
    
    def _add_GP_parameter_and_get_parameter_text(self, function_builder, l_function_shortname):
        """Add the GP parameters to functions created by a function_builder

        Arguments
        ---------
        function_builder        : FunctionBuilder 
        l_function_shortname    : List of str

        Return
        ------
        dico_text_param : Dict of dict
            Keys are function short names in function_builder (elements of l_function_shortname) values are dictionaries
            whose keys are parameter names and values are text of the parameters to use in the function
        """
        if l_function_shortname_add_param_only is None:
            l_function_shortname_add_param_only = []

        dico = {func_shortname: {} for func_shortname in l_function_shortname}
        dico_param = self.get_parameters(object_category=None)
        for param_basename, param in dico_param['GP'].items():
            for func_shortname in l_function_shortname:
                function_builder.add_parameter(parameter=param, function_shortname=func_shortname, exist_ok=True)
                dico[func_shortname][param_basename] = function_builder.get_text_4_parameter(parameter=param, function_shortname=func_shortname)
                if param_basename in ["A", "tau", "gamma", "f"]:
                    if self.log10(param_basename=param_basename):
                        dico[param_basename] = f"10**{dico[param_basename]}"
                if param_basename == "P":
                    if self.log10(param_basename=param_basename):
                        dico[param_basename] = f"{dico[param_basename]} * log(10)"
                    else:
                        dico[param_basename] = f"log({dico[param_basename]})"
                    function_builder.add_variable_to_ldict(variable_name='log', variable_content=log, function_shortname=func_shortname , exist_ok=True, overwrite=False)
        return dico

    def _add_text_GP_kernel(self, dico_text_param, function_builder, l_function_shortname):
        """Add the text of the GP kernel and the text to return the GP simulation/prediction
        """
        tab = "    " 
        for func_shortname in l_function_shortname:
            kernel = 1**2 * ExpSquaredKernel(metric=20) * (ExpSine2Kernel(gamma=1/(2 * 0.5**2), log_period=log(10)) + 0.1 * CosineKernel(log_period=log(10) - log(2)))
            gp = GP(kernel, fit_kernel=True, mean=0, fit_mean=False)
            function_builder.add_variable_to_ldict(variable_name='gp', variable_content=gp, function_shortname=func_shortname , exist_ok=False, overwrite=False)
            # text_return += f"{tab}import pdb; pdb.set_trace()"
            text_GP_kernel = f"\n{tab}gp.set_parameter_vector([{dico_text_param[func_shortname]['A']}**2, {dico_text_param[func_shortname]['tau']}**2, 1/(2 * {dico_text_param[func_shortname]['gamma']}**2), {dico_text_param[func_shortname]['P']},  {dico_text_param[func_shortname]['f']}, {dico_text_param[func_shortname]['P']}], include_frozen=False)\n"
            function_builder.add_to_body_text(text=text_GP_kernel, function_shortname=func_shortname)
            function_builder.add_variable_to_ldict(variable_name='ExpSquaredKernel', variable_content=ExpSquaredKernel, function_shortname=func_shortname , exist_ok=True, overwrite=False)
            function_builder.add_variable_to_ldict(variable_name='ExpSine2Kernel', variable_content=ExpSine2Kernel, function_shortname=func_shortname , exist_ok=True, overwrite=False)
            function_builder.add_variable_to_ldict(variable_name='CosineKernel', variable_content=CosineKernel, function_shortname=func_shortname , exist_ok=True, overwrite=False)


class Core_GP1DModel_Celerite(Core_GP1DModel):

    def _add_text_compute_lnlike(self, function_builder, l_function_shortname):
        """Add the text of the GP kernel and the text to return the GP simulation/prediction
        """
        tab = "    " 
        for func_shortname in l_function_shortname:
            text_return = f"\n{tab}gp.compute(t=concatenate(dict_datakwargs['time']), yerr=concatenate(dict_datakwargs['data_err']), quiet=True)\n"
            text_return += f"{tab}return gp.log_likelihood((concatenate(dict_datakwargs['data']) - concatenate(sim_data)).reshape((-1)))\n"
            function_builder.add_to_body_text(text=text_return, function_shortname=func_shortname)
            function_builder.add_variable_to_ldict(variable_name='concatenate', variable_content=concatenate, function_shortname=func_shortname , exist_ok=False, overwrite=False)
    
    def _add_text_compute_gpsim(self, function_builder, l_function_shortname):
        """Add the text of the GP kernel and the text to return the GP simulation/prediction
        """
        tab = "    " 
        for func_shortname in l_function_shortname:
            text_return = f"\n{tab}gp.compute(t=concatenate(dict_datakwargs['time']), yerr=concatenate(dict_datakwargs['data_err']), quiet=True)\n"
            text_return += f"{tab}return gp.predict((concatenate(dict_datakwargs['data']) - concatenate(sim_data)).reshape((-1)), tsim, return_var=True)\n"
            function_builder.add_to_body_text(text=text_return, function_shortname=func_shortname)
            function_builder.add_variable_to_ldict(variable_name='concatenate', variable_content=concatenate, function_shortname=func_shortname , exist_ok=False, overwrite=False)
    

class QPCeleriteModel(Core_GP1DModel_Celerite):

    __category__ = "QPCelerite"

    # Source Foreman-Mackey et al. 2017. AJ, 154, 220 (equation 56) - https://iopscience.iop.org/article/10.3847/1538-3881/aa9332/meta
    # See also: in Radvel the CeleriteKernel: https://radvel.readthedocs.io/en/latest/gp.html?highlight=jitter#radvel.gp.CeleriteKernel.compute_covmatrix
    # In Celerite the example: https://celerite.readthedocs.io/en/stable/python/kernel/
    # In Celerite2 the example: https://celerite2.readthedocs.io/en/stable/python/kernel/
    # The parameterisation is the one of the Foreman-Mackey et al. 2017 paper
    # The implementation is based on the celerite example (adapted to celerite2 mimicking https://celerite2.readthedocs.io/en/latest/_modules/celerite2/terms/#Term)
    # except that I remove the log in front of the parameters
    
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

        @staticmethod
        def get_test_parameters():
            return dict(B=1, C=1.5, L=20, P=10.0)

        def __init__(self, *, B, C, L, P):
            self.B = float(B)
            self.C = float(C)
            self.L = float(L)
            self.P = float(P)

        def get_coefficients(self):
            
            return (self.B * (1.0 + self.C) / (2.0 + self.C), 1/self.L, 
                    self.B / (2.0 + self.C), 0.0, 1/self.L, 2 * pi / self.P,
                    )
        
    def _add_text_GP_kernel(self, dico_text_param, function_builder, l_function_shortname):
        """Add the text of the GP kernel and the text to return the GP simulation/prediction
        """
        tab = "    " 
        for func_shortname in l_function_shortname:
            kernel = self.CustomTerm(B=1, C=1.5, L=20, P=10.0)
            gp = GaussianProcess(kernel, mean=0.0)
            function_builder.add_variable_to_ldict(variable_name='gp', variable_content=gp, function_shortname=func_shortname , exist_ok=False, overwrite=False)
            text_GP_kernel = f"\n{tab}gp.kernel = CustomTerm(B={dico_text_param[func_shortname]['B']}, C={dico_text_param[func_shortname]['C']}, L={dico_text_param[func_shortname]['L']}, P={dico_text_param[func_shortname]['P']})\n"
            function_builder.add_to_body_text(text=text_GP_kernel, function_shortname=func_shortname)
            function_builder.add_variable_to_ldict(variable_name='CustomTerm', variable_content=CustomTerm, function_shortname=func_shortname , exist_ok=False, overwrite=False)


class RotationCeleriteModel(Core_GP1DModel_Celerite):

    __category__ = "RotationCelerite"

    # Source Foreman-Mackey et al. 2017. AJ, 154, 220 (equation 56) - https://iopscience.iop.org/article/10.3847/1538-3881/aa9332/meta
    # In Celerite2 the example: https://celerite.readthedocs.io/en/stable/python/kernel/
    # The implementation and parameterisation is based on the celerite2 description: https://celerite2.readthedocs.io/en/latest/api/python/#celerite2.terms.RotationTerm
    # I have just changed the name of the sigma parameter into A

    ############################################################
    ## Dealing with the parameters and their names for the model
    ############################################################

    # Dealing with parameter basenames
    ##################################

    def _get_l_parameter_basename_GP(self):
        return ['A', 'P', 'Q0', 'dQ', 'f']

    ######################################
    # Dealing with the likelihood creation
    ######################################

    def _add_text_GP_kernel(self, dico_text_param, function_builder, l_function_shortname):
        """Add the text of the GP kernel and the text to return the GP simulation/prediction
        """
        tab = "    " 
        for func_shortname in l_function_shortname:
            kernel = RotationTerm(sigma=1, period=10, Q0=0.1, dQ=0, f=0.1)
            gp = GaussianProcess(kernel, mean=0.0)
            function_builder.add_variable_to_ldict(variable_name='gp', variable_content=gp, function_shortname=func_shortname , exist_ok=False, overwrite=False)
            text_GP_kernel = f"\n{tab}gp.kernel = RotationTerm(A={dico_text_param[func_shortname]['A']}, P={dico_text_param[func_shortname]['P']}, Q0={dico_text_param[func_shortname]['Q0']}, dQ={dico_text_param[func_shortname]['dQ']}, f={dico_text_param[func_shortname]['f']})\n"
            function_builder.add_to_body_text(text=text_GP_kernel, function_shortname=func_shortname)
            function_builder.add_variable_to_ldict(variable_name='RotationTerm', variable_content=RotationTerm, function_shortname=func_shortname , exist_ok=False, overwrite=False)


class SHOCeleriteModel(Core_GP1DModel_Celerite):

    __category__ = "SHOCelerite"

    # Source Foreman-Mackey et al. 2017. AJ, 154, 220 (equation 56) - https://iopscience.iop.org/article/10.3847/1538-3881/aa9332/meta
    # In Celerite2 the example: https://celerite.readthedocs.io/en/stable/python/kernel/
    # The implementation and parameterisation is based on the celerite2 description: https://celerite2.readthedocs.io/en/latest/api/python/#celerite2.terms.SHOTerm
    # I have just changed the name of the sigma parameter into A

    ############################################################
    # Dealing with the parametrisation, param_extension and args
    ############################################################

    def _set_parametrisation(self, parametrisation=None):
        """ """
        self.parametrisation.update({'use_rho': True, 'use_Q': True, 'use_A': True, 'log10': {'rho/omega0': False, 'Q/tau': False, 'A/S0': False}})
        if parametrisation is not None:
            for key in parametrisation:
                if key not in ['use_rho', 'use_Q', 'use_A', 'log10']:
                    raise ValueError(f"The only possible keys to the 'parametrisation' are ['use_rho', 'use_Q', 'use_A', 'log10']. You provided {key}.")
                if key in ['use_rho', 'use_Q', 'use_A']:
                    if not(isinstance(parametrisation[key], bool)):
                        raise ValueError(f"Value of parametrisation[{key}] should be a bool (got {parametrisation[key]})")
                    self.parametrisation[key] = parametrisation[key]
                if key == 'log10':
                    if not(isinstance(parametrisation[key], dict)):
                        raise ValueError(f"'log10' in parametrisation should be a dictionary. You provided a {type(parametrisation[key])}.")
                    for param_basename in parametrisation[key]:
                        if param_basename not in ['rho/omega0', 'Q/tau', 'A/S0']:
                            raise ValueError(f"The only possible keys to the 'log10' dictionary are ['rho/omega0', 'Q/tau', 'A/S0']. You provided {key}.")
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
        if self.use_A:
            res.append('A')
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
    def use_A(self):
        return self.parameterisation['use_A']

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
        if param_basename in ["A", "S0"]:
            return self.parametrisation["log10"]['A/S0']
        elif param_basename in ["rho", "omega0"]:
            return self.parametrisation["log10"]['rho/omega0']
        elif param_basename in ["Q", "tau"]:
            return self.parametrisation["log10"]['Q/tau']

    ######################################
    # Dealing with the likelihood creation
    ######################################
        
    def _add_text_GP_kernel(self, dico_text_param, function_builder, l_function_shortname):
        """Add the text of the GP kernel and the text to return the GP simulation/prediction
        """
        tab = "    " 
        for func_shortname in l_function_shortname:
            kwargs = {}
            arguments_text = ""
            if self.use_A:
                kwargs["sigma"] = 1
                arguments_text += f"sigma={dico_text_param[func_shortname]['A']}, "
            else:
                kwargs["S0"] = 1
                arguments_text += f"S0={dico_text_param[func_shortname]['S0']}, "
            if self.use_rho:
                kwargs["rho"] = 10
                arguments_text += f"rho={dico_text_param[func_shortname]['rho']}, "
            else:
                kwargs["omega0"] = 2 * pi / 10
                arguments_text += f"omega0={dico_text_param[func_shortname]['omega0']}, "
            if self.use_Q:
                kwargs["Q"] = 1 / 2
                arguments_text += f"Q={dico_text_param[func_shortname]['Q']}, "
            else:
                kwargs["tau"] = 20
                arguments_text += f"tau={dico_text_param[func_shortname]['tau']}, "
            kernel = SHOTerm(**kwargs)
            gp = GaussianProcess(kernel, mean=0.0)
            function_builder.add_variable_to_ldict(variable_name='gp', variable_content=gp, function_shortname=func_shortname , exist_ok=False, overwrite=False)
            text_GP_kernel = f"\n{tab}gp.kernel = SHOTerm({arguments_text})\n"
            function_builder.add_to_body_text(text=text_GP_kernel, function_shortname=func_shortname)
            function_builder.add_variable_to_ldict(variable_name='SHOTerm', variable_content=SHOTerm, function_shortname=func_shortname , exist_ok=False, overwrite=False)

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
        dico_param = self.get_parameters(object_category=None)
        for param_basename, param in dico_param['GP'].items():
            function_builder_allGP1D.add_parameter(parameter=param, function_shortname=function_shortname_allGP1D, exist_ok=True)
            function_builder_GP1D.add_parameter(parameter=param, function_shortname=function_shortname_GP1D, exist_ok=True)
            dico[param_basename] = function_builder_GP1D.get_text_4_parameter(parameter=param, function_shortname=function_shortname_GP1D)
            if self.log10(param_basename=param_basename):
                dico[param_basename] = f"10**{dico[param_basename]}"
        
        function_builder_GP1D.add_variable_to_ldict(variable_name='gp', variable_content=gp, function_shortname=function_shortname_GP1D , exist_ok=False, overwrite=False)
        tab = "    " 
        # text_return += f"{tab}import pdb; pdb.set_trace()"


class Matern32CeleriteModel(Core_GP1DModel_Celerite):

    __category__ = "Matern32Celerite"

    # Source Foreman-Mackey et al. 2017. AJ, 154, 220 (equation 56) - https://iopscience.iop.org/article/10.3847/1538-3881/aa9332/meta
    # In Celerite the example: https://celerite.readthedocs.io/en/stable/python/kernel/
    # The implementation and parameterisation is based on the celerite2 description: https://celerite2.readthedocs.io/en/latest/api/python/#celerite2.terms.Matern32Term
    # I have just changed the name of the sigma parameter into A

    ############################################################
    ## Dealing with the parameters and their names for the model
    ############################################################

    # Dealing with parameter basenames
    ##################################

    def _get_l_parameter_basename_GP(self):
        return ['A', 'rho']

    ######################################
    # Dealing with the likelihood creation
    ######################################

    def _add_text_GP_kernel(self, dico_text_param, function_builder, l_function_shortname):
        """Add the text of the GP kernel and the text to return the GP simulation/prediction
        """
        tab = "    " 
        for func_shortname in l_function_shortname:
            kernel = Matern32Term(sigma=1, rho=10)
            gp = GaussianProcess(kernel, mean=0.0)
            function_builder.add_variable_to_ldict(variable_name='gp', variable_content=gp, function_shortname=func_shortname , exist_ok=False, overwrite=False)
            text_GP_kernel = f"\n{tab}gp.kernel = Matern32Term(sigma={dico_text_param[func_shortname]['A']}, rho={dico_text_param[func_shortname]['rho']})\n"
            function_builder.add_to_body_text(text=text_GP_kernel, function_shortname=func_shortname)
            function_builder.add_variable_to_ldict(variable_name='Matern32Term', variable_content=Matern32Term, function_shortname=func_shortname , exist_ok=False, overwrite=False)
    
    
    
