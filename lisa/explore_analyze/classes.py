from __future__ import annotations
from numbers import Number
from numpy import float_, ndarray
from numpy.typing import NDArray
from typing import Dict
from collections import Sequence
from loguru import logger


class ModelSpecification(object):
    """Class that defines the specification for a model computation in terms of components to add and or remove and dataset to use"""

    def __init__(self, datasetname: str|None=None, add: list[str]|str|None=None, remove: list[str]|str|None=None, freeze: bool=False):
        """"""
        # Init datasetname - property can only be set once
        self.__datasetname = None
        if datasetname is not None:
            self.datasetname = datasetname
        # Init add and remove properties which can be changed with the add_model_components, remove_model_components
        self.__add: tuple[str] = ()
        self.__remove: tuple[str] = ()
        # Check add and remove inputs and store them into self.__add and self.__remove
        for add_or_remove, input in zip(["add", "remove"], [add, remove]):
            self.add_model_components(model_components=input, add_or_remove=add_or_remove)
        # Init freeze - read-only property
        self.__frozen = False
    
    def __eq__(self, other:ModelSpecification) -> bool:
        """Overrides the default implementation"""
        if isinstance(other, ModelSpecification):
            return (self.__add == other.add) and (self.__remove == other.remove) and (self.datasetname == other.datasetname)
        else:
            return False
    
    def __repr__(self) -> str:
        """"""
        return f"{self.__class__.__name__}(datasetname={self.datasetname}, add={self.add}, remove={self.remove}, model2computenplot={self.model2computenplot})"

    @property
    def datasetname(self) -> None|str:
        """Name of the dataset to be used to compute the model"""
        return self.__datasetname
    
    @datasetname.setter
    def datasetname(self, new_datasetname: str) -> None:
        """Name of the dataset to be used to compute the model"""
        if self.__datasetname is not None:
            raise ValueError("datasetname has already been set and cannot be changed.")
        if not(isinstance(new_datasetname, str)):
            raise TypeError(f"datasetname should be a str")
        self.__datasetname = new_datasetname
    
    @property             
    def add_and_remove(self) -> Dict[str, list[str]]:
        """Return a dictionary with 2 keys, 'add' and 'remove' whose values are lists of str (model component name)"""
        return {'add': self.add, 'remove': self._remove}
    
    @property             
    def add(self) -> tuple[str]:
        """Return the list of model component name to add"""
        return self.__add
    
    @property             
    def remove(self) -> tuple[str]:
        """Return the list of model component name to remove"""
        return self.__remove
    
    def __check_add_or_remove_input(self, add_or_remove: str):
        """"""
        # Check the add_or_remove
        if add_or_remove not in ['add', 'remove']:
            raise ValueError(f"add_or_remove should be either 'add' or 'remove', got {add_or_remove}")
    
    def __check_model_components(self, model_components: list[str]|str|None, model_components_input_name: str) -> list[str]:
        """"""
        if model_components is None:
            checked_model_components = []
        else:
            checked_model_components = None
            if isinstance(model_components, str):
                checked_model_components = [model_components]
            elif isinstance(model_components, list) and all([isinstance(model_component, str) for model_component in model_components]):
                checked_model_components = model_components.copy()
            if checked_model_components is None:
                raise ValueError(f"{model_components_input_name} should be either None, or a str (model component name) or a list of strs (list of model component names), got {model_components}")
        return checked_model_components

    def add_model_components(self, model_components: list[str]|str, add_or_remove: str) -> None:
        """Add one or several model components to the list of model components to add or remove"""
        if self.frozen:
            raise ValueError("add or remove cannot be changed as frozen is {self.frozen}")
        self.__check_add_or_remove_input(add_or_remove=add_or_remove)
        model_components = self.__check_model_components(model_components=model_components, model_components_input_name=f'{add_or_remove} model_components')
        if add_or_remove == 'add': 
            self.__add = list(self.add) + model_components
        else:
            self.__remove = list(self.remove) + model_components

    def remove_model_components(self, model_components: list[str]|str, add_or_remove: str) -> None:
        """Remove one or several model components to the list of model components to add or remove"""
        if self.frozen:
            raise ValueError("add or remove cannot be changed as frozen is {self.frozen}")
        self.__check_add_or_remove_input(add_or_remove=add_or_remove)
        model_components = self.__check_model_components(model_components=model_components, model_components_input_name=f'{add_or_remove} model_components')
        for model_component in model_components:
            if add_or_remove == 'add':
                list_current_models = self.__add
            else:
                list_current_models = self.__remove
            list_current_models.remove(model_component)
            if add_or_remove == 'add':
                self.__add = tuple(list_current_models)
            else:
                self.__remove = tuple(list_current_models)

    def reset_model_components(self, add_or_remove: str) -> None:
        """Reset the add or remove properties"""
        if self.frozen:
            raise ValueError("add or remove cannot be changed as frozen is {self.frozen}")
        self.__check_add_or_remove_input(add_or_remove=add_or_remove)
        if add_or_remove == 'add':
            self.__add = ()
        else:
            self.__remove = ()

    @property
    def frozen(self) -> bool:
        return self.__frozen
    
    def freeze_switch(self) -> None:
        self.__frozen = not(self.__frozen)


class Model2compute(object):
    """Class that specifies one model to plot (for one times vector and one couple exptime bin and supersampling)."""

    def __init__(self, modelspec: ModelSpecification, exptimeNsupersamp: tuple[Number, int], times:NDArray[float_]|None=None) -> None:
        # Set modelspec - read-only property
        if not(isinstance(modelspec, ModelSpecification)):
            raise TypeError(f"modelspec should be a ModelSpecification, got a {type(modelspec)}.")
        else:
            self.__modelspec = modelspec
        # Set exptimeNsupersamp - read-only property
        if not(isinstance(exptimeNsupersamp, tuple)) or not(len(exptimeNsupersamp) == 2) or not(isinstance(exptimeNsupersamp[0], Number)) or not(isinstance(exptimeNsupersamp[1], int)):
            raise TypeError(f"exptimeNsupersamp should be a tuple with two elements, first a Number and then an int, got {exptimeNsupersamp}")
        else:
            self.__exptimeNsupersamp = exptimeNsupersamp
        # Initialise times - property can only be set once
        self.__times = None
        if times is not None:
            self.times = times
        

    @property
    def modelspec(self) -> ModelSpecification:
        return self.__modelspec
    
    @property
    def exptimeNsupersamp(self) -> tuple[Number, int]:
        return self.__exptimeNsupersamp
    
    @property
    def times(self) -> NDArray[float_]|None:
        return self.__times
    
    @times.setter
    def times(self, new_times: NDArray[float_]) -> None:
        if self.__times is not None:
            raise ValueError("times has already been set and cannot be changed.")
        if not(isinstance(new_times, NDArray[float_])):
            raise TypeError(f"times should be a NDArray[float_], got a {type(new_times)}")
        self.__times = new_times


class Model2compute(object):
    """Class that specifies one model to plot (for one times vector and one couple exptime bin and supersampling))"""

    def __init__(self, modelspec: ModelSpecification, exptimeNsupersamp: tuple[Number, int], times:NDArray[float_]|None=None, pl_kwargs: Dict|None=None) -> None:
        super(self.__class__, self).__init__(modelspec=modelspec, exptimeNsupersamp=exptimeNsupersamp, times=times)
        # Initialise pl_kwargs - property
        self.__pl_kwargs = {}
        if pl_kwargs is not None:
            self.pl_kwargs.update(pl_kwargs)
    
    @property
    def pl_kwargs(self) -> Dict:
        return self.__pl_kwargs
    
    def reset_pl_kwargs(self) -> None:
        self.__pl_kwargs = {}


class ComputedModel(object):
    """Class to store the values computed for a model.
    
    It is made to stored values for only on model but several exptime+supersamp combination and several times samples.
    """

    def __init__(self, modelspec: ModelSpecification) -> None:
        """"""
        # Set modelspec - read-only property
        if not(isinstance(modelspec, ModelSpecification)):
            raise TypeError(f"modelspec should be a ModelSpecification, got a {type(modelspec)}.")
        else:
            self.__modelspec = modelspec
            # Freeze the modelspec has you don't which it to change (especially after you have stored model values)
            if not(self.modelspec.frozen):
                self.modelspec.freeze_switch()
        # Init the times, model and model_err values
        self.__time_values: Dict[tuple[Number, int], list[NDArray[float_]]] = {}
        self.__model_values: Dict[tuple[Number, int], list[NDArray[float_]]] = {}
        self.__model_values_err: Dict[tuple[Number, int], list[NDArray[float_]]] = {}

    @property
    def modelspec(self) -> ModelSpecification:
        return self.__modelspec
    
    @property
    def computed_exptime_supersamp(self) -> set[tuple[Number, int]]:
        """"""
        return set(self.__times_values.keys())

    @property
    def model_stored(self) -> bool:
        """Return True if the model has been computed and stored"""
        return len(self.__time_values) > 0
    
    def __find_times_index(self, times:NDArray[float_], exptime_bin: Number, supersamp: int) -> None|int:
        """"""
        tup_exptime_supersamp = (exptime_bin, supersamp)
        i_times_found = None 
        if tup_exptime_supersamp not in self.__time_values:
            raise ValueError(f"No model has been computed for ")
        for i_times, times_i in enumerate(self.__time_values[tup_exptime_supersamp]):
            if all(times_i == times):
                i_times_found = i_times
        return i_times_found

    def get_computed_model(self, times:NDArray[float_], exptime_bin: Number, supersamp: int) -> tuple[NDArray, NDArray, NDArray|None]:
        """Dictionary with two keys 'times', 'values' with the computed time and model values."""
        tup_exptime_supersamp = (exptime_bin, supersamp)
        if tup_exptime_supersamp not in self.__model_values:
            raise KeyError(f"There is no model stored with exptime_bin={exptime_bin} and supersamp={supersamp}. The set of available exptime_bin, supersamp is {self.computed_exptime_supersamp}.")
        i_times_found = self.__find_times_index(times=times)
        if i_times_found:
            return (self.__model_values[tup_exptime_supersamp][i_times_found].copy(), 
                    self.__model_values_err[tup_exptime_supersamp][i_times_found].copy() if self.__model_values_err[tup_exptime_supersamp][i_times_found] is not None else None
                    )
        
    def set_computed_model(self, times:NDArray[float_], values:NDArray[float_], values_err: NDArray[float_]|None=None, exptime_bin: Number=0, supersamp: int=1, overwrite: bool=False):
        """Set the computed model (times and values).
        
        If npt and/or t_lims have been set, the times and values arguments will be check against those.
        If they were not set alreay they will be set using the times and values arguments.

        Once a computed model has been set it cannot be overwritten.
        """
        # Checking the times, values and values_err input are proper
        if not(isinstance(times, ndarray)) or not(isinstance(values, ndarray)) or not((values_err is None) or isinstance(values_err, ndarray)):
            raise TypeError(f"times, values and values_err should be numpy.ndarray, got {type(times)}, {type(values)} and {type(values_err)} respectively.")
        if (times.ndim != 1) or (values.ndim != 1) or ((values_err is not None) and (values.ndim != 1)):
            raise ValueError(f"times, values and values_err (if not None) should be ndarray with 1 dimension. The number of dimension of times is {times.ndim}, the one of values is {values.ndim} and {'values_err is None' if values_err is None else f'the one of values_err is {values_err.ndim}'}")
        if (times.size != values.size) or ((values_err is not None) and (times.size != values_err.size)):
            raise ValueError(f"times, values and values_err (if not None) should have the same size. times' size is {times.size}, values' size is {values.size} and {'values_err is None' if values_err is None else f'values_err size is {values_err.size}'}")
        # Checking the exptime_bin and supersamp inputs
        if not(isinstance(exptime_bin, Number)) or (exptime_bin < 0):
            raise ValueError(f"exptime_bin should be a positive (or zero) float, got {exptime_bin}")
        if not(isinstance(supersamp, int)) or (supersamp < 1):
            raise ValueError(f"supersamp should be an int superior or equal to 1, got {supersamp}")
        tup_exptime_supersamp = (exptime_bin, supersamp)
        # Create time values entry for the specified (exptime_bin, supersamp) pair if needed
        if tup_exptime_supersamp not in self.__time_values:
            self.__time_values[tup_exptime_supersamp] = []
        # Check if there is already a model stored
        i_times_found = self.__find_times_index(times=times, exptime_bin=exptime_bin, supersamp=supersamp)
        if i_times_found:
            if not(overwrite):
                raise ValueError(f"A computed model already exists for exptime_bin={exptime_bin} and supersamp={supersamp} and overwrite is False. Set overwrite to True or reconsider.")
            else:
                self.__model_values[tup_exptime_supersamp][i_times_found] = values
                self.__model_values_err[tup_exptime_supersamp][i_times_found] = values_err
        else:
            self.__time_values[exptime_bin].append(times)
            self.__model_values[exptime_bin].append(values)
            self.__model_values_err[exptime_bin].append(values_err)


class DatabaseComputedModels(object):

    def __init__(self, tuples_name_model2computenplot: Sequence[tuple[str|int|None, ComputedModel]]|None=None, overwrite=False) -> None:
        """"""
        # Init models2computenplot
        self.__computedmodels: Dict[str|int, ComputedModel] = {}
        # Add models2computenplot to the database
        self.add_computedmodels(tuples_name_model2computenplot=tuples_name_model2computenplot, overwrite=overwrite)

    @property
    def computedmodels(self) -> Dict[str|int, ComputedModel]:
        return self.__computedmodels.copy()

    @property
    def name2modelspec(self) -> Dict[str|int, ModelSpecification]:
        """Dictionary providing the conversion from names to model specifications (what the model is composed of in terms of model component added and removed and the dataset used)"""
        return {name: model2computenplot.modelspec for name, model2computenplot in self.__models2computenplot.items()}
    
    def __find_modelspec(self, modelspec: ModelSpecification):
        name_found = None
        for name_i, modelspec_i in self.name2modelspec.items():
            if modelspec == modelspec_i:
                name_found = name_i
                break
        return name_found

    def add_computedmodel(self, computedmodel: ComputedModel, name: None|int|str=None, overwrite=False):
        """"""
        # Check the type of model2computenplot
        if not(isinstance(computedmodel, ComputedModel)):
            raise TypeError(f"computedmodel should be a ComputedModel instance, got a {type(computedmodel)}")
        # Check the type of name
        if name is None:
            name = 0
            while name in self.__computedmodels:
                name += 1
        if not(isinstance(name, int)) and not(isinstance(name, str)):
            raise TypeError(f"name should be either an int, a str or None, got {name}")
        # Check if a computedmodel with the same ModelSpecification already exists
        name_found = self.__find_modelspec(modelspec=computedmodel.modelspec)
        if name_found:
            if overwrite:
                logger.warning(f"A ComputedModel instance with the same ModelSpecification and name ({name_found}) was found. It will be replaced by a the provided computedmodel with name {name}")
                if name_found != name:
                    self.__computedmodels.pop(name_found)
        self.__computedmodels[name] = computedmodel

    def add_models2computenplot(self, tuples_name_computedmodel: Sequence[tuple[str|int|None, ComputedModel]], overwrite=False):
        """"""
        for name, computedmodel in tuples_name_computedmodel:
            self.add_computedmodel(name=name, computedmodel=computedmodel, overwrite=overwrite)

    def get_models2computenplot(self, modelspec: ModelSpecification|None, name: str|int|None) -> tuple[Model2computeNplot|None, str|int|None]:
        """"""
        if (name is None) == (modelspec is None):
            raise ValueError(f"You need to provide either name or modelspec (and not both), you provided name={name} and modelspec={modelspec}")
        if name is None:
            name_found = self.__find_modelspec(modelspec=modelspec)
        else:
            name_found = name
        if name_found:
            return self.__models2computenplot[name_found], name_found
        else:
            return None, name_found

