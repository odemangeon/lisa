"""Provides the GP1D, GP1DContainer and GP1DContainerInterface classes.

Each instance of GP1D class is used to store the parameters of one GP1D noise model used in the Model instance.
There can be several instances of GP1D in a model instance.

The instance of GP1DContainer is used to store all the GP1D instances of a Model instance.
There is only on GP1DContainer instance in a Model instance.

The GP1DContainerInterface class in an Interface class that is meant to be a parent class of the Model class
and provide convenience function to interact with the GP1DContainer instance.
"""
from ..paramcontainer import Core_ParamContainer
from ..model.paramcontainers_database import SpecificParamContainerCategoryContainer


class GP1D(Core_ParamContainer):
    
    __category__ = "GP1D"


class GP1DContainer(SpecificParamContainerCategoryContainer):

    def __init__(self):
        """
        """
        super(GP1DContainer, self).__init__(ordered=False)

    def get_subkwargs_4_get_list_params(self, model_instance=None, **kwargs):
        """Select the keyword arguments for the get_list_params method.

        Argument
        --------
        model_instance  : Core_Model
            Model instance which is used for the default value of kwargs, see below (optional).

        Keyword argument that are used by the get_list_params method

        Return
        ------
        selected_kwargs : dict
            Dictionary providing the kwargs required by get_list_params
        """
        selected_kwargs = {}
        # Get the specific arguments for InstrumentContainer get_param function
        for kwarg_name in ["l_param_container_fullname"]:
            selected_kwargs[kwarg_name] = kwargs.get(kwarg_name, None)
        # Set the default value if not provided
        if selected_kwargs["l_param_container_fullname"] is None:
            selected_kwargs["l_param_container_fullname"] = self.l_param_container_fullname  # name_GP1D_used is defined in GP1DNoiseModels
        return selected_kwargs
    

class GP1DContainerInterface(object):
    """An interface of core_model.Core_Model.

    It has to be in the list of parent classes of Model before ParamContainerDatabase.
    It's an Interface of core_model.Core_Model which allows the model to properly handle
    GP models.
    """

    def __init__(self):
        # Init the instruments
        self.paramcontainers.update({GP1D.category: GP1DContainer()})

    @property
    def GP1Ds(self):
        """Return an OrderedDict with the GP models currently in the instance.
        """
        return self.paramcontainers[GP1D.category]

    @property
    def l_GP1D(self):
        """Return the list of GP1D object in the GP1D container."""
        return self.GP1Ds.l_param_container

    @property
    def l_GP1D_fullname(self):
        """Return the list of the name of the GP1D object in the GP1D container"""
        return self.GP1Ds.l_param_container_fullname

    def add_a_GP1D(self, GP, name, force=False):
        """Add an GP1D to the GP1D container."""
        if not(isinstance(GP, GP1D)):
            raise ValueError("GP should be an instance of class GP1D")
        self.GP1Ds[name] = GP

    def rm_a_GP1D(self, name, **kwargs):
        """Remove an instrument model to the paramcontainers of this model."""
        self.GP1Ds.pop(name)





    
    