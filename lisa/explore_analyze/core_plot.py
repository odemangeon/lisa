from __future__ import annotations
from collections import Sequence, OrderedDict
from typing import Dict
from loguru import logger
from numpy.typing import NDArray
from numpy import float_, isfinite, ndarray, equal, linspace, array_equal, size
from numbers import Number
from copy import deepcopy, copy
from pprint import pprint
import re

from ..posterior.core.posterior import Posterior


def get_default_model_name(seq_current_model_name: Sequence[int|str]):
    name = 0
    while name in seq_current_model_name:
        name += 1
    return name


class DataBinning(object):
    """Class to set the parameters for the binning
    
    It defines the exposure time and the binning method
    """
    def __init__(self, exptime:float|int|None=None, method:str|None=None):
        exptime = self._default_exptime(exptime=exptime)
        self._set_exptime(exptime=exptime)
        method = self._default_method(method=method)
        self._set_method(method=method)

    @property
    def exptime(self) -> float|int:
        return self.__exptime

    def _default_exptime(self, exptime:float|int|None=None) -> float|int:
        if exptime is None:
            exptime = 0
        return exptime

    def _set_exptime(self, exptime:float|int):
        if not(exptime >= 0):
            raise ValueError(f"exptime should be a number superior or equal to 0")
        self.__exptime = exptime

    @property
    def method(self) -> str:
        return self.__method

    def _default_method(self, method:str|None=None) -> str:
        if method is None:
            method = 'mean'
        return method
    
    def _set_method(self, method:str):
        if not(isinstance(method, str)):
            raise TypeError(f"method should be str, got {type(method)}")
        self.__method = method

    def __eq__(self, other: object) -> bool:
        """Overrides the default implementation"""
        if isinstance(other, DataBinning):
            return (self.exptime == other.exptime) and (self.method == other.method)
        else:
            return False


class ModelBinning(DataBinning):
    """Class to set the parameters for the binning
    
    It is define by an exposure time and a supersampling factor
    """

    def __init__(self, exptime:float|int|None=None, supersampling:int|None=None):
        exptime = self._default_exptime(exptime=exptime)
        self._set_exptime(exptime=exptime)
        supersampling = self._default_supersampling(supersampling=supersampling)
        self._set_supersampling(exptime=self.exptime, supersampling=supersampling)

    @property
    def supersampling(self) -> int:
        return self.__supersampling

    def _default_supersampling(self, supersampling:int|None) -> int:
        if supersampling is None:
            supersampling = 1
        return supersampling

    def _set_supersampling(self, exptime:float|int, supersampling:int):
        if not(exptime >= 0):
            raise ValueError(f"exptime should be a number superior or equal to 0")
        if not(supersampling >= 1) or not(isinstance(supersampling, int)):
            raise ValueError(f"supersampling should be an int superior or equal to 1")
        if ((exptime > 0.) and equal(supersampling, 1)) or ((supersampling > 1) and equal(exptime, 0)):
            raise ValueError(f"if supersampling is > 1 then exptime should not be 0 and vice versa.")
        self.__supersampling = int(supersampling)

    def __eq__(self, other: object) -> bool:
        """Overrides the default implementation"""
        if isinstance(other, ModelBinning):
            return (self.exptime == other.exptime) and (self.supersampling == other.supersampling)
        else:
            return False


class Expression(object):
    """Class that defines the expression of the model or data to plot in terms of basic operations and base components
    """
    
    def __init__(self, expression:str):
        if not(isinstance(expression, str)):
            raise TypeError(f"expression should be a string with the expression to be used to compute the model")
        self.__expression = expression
        self.__terms:list[str] = []
        
        self._parse_expression()
    
    def _parse_expression(self):
        # Extract terms using regular expressions (assume terms are variables with letters/numbers/underscores)
        self.__terms = re.findall(r'[a-zA-Z_]\w*', self.expression)
        
        # Extract operations (for now we consider only +, -, *, /, parentheses are ignored)
        self.__operations = re.findall(r'[+\-*/]', self.expression)
        
        # Handle cases where there's only one term and no operations
        if len(self.__terms) == 1 and not self.__operations:
            self.__operations = []
    
    @property
    def components(self):
        # Return a list of unique terms (removing duplicates)
        return list(set(self.__terms))
    
    @property
    def operations(self):
        # Return the sequence of operations found in the expression
        return copy(self.__operations)
    
    @property
    def expression(self):
        # Return a list of unique terms (removing duplicates)
        return self.__expression
    
    @property
    def expression_err(self):
        # Return a list of unique terms (removing duplicates)
        return f"sqrt({' + '.join([f'{component_i}**2' for component_i in self.components])})"

    def __eq__(self, other: object) -> bool:
        """Overrides the default implementation"""
        if isinstance(other, Expression):
            return self.expression == other.expression
        else:
            return False


class Model2plot(object):
    """Class to specify a model to plot

    A model to plot is defined by
    - its components (base components to add or remove)
    - its datasetname
    - its time vector at which the model is evaluated
    - its exposure time
    - its supersampling factor
    - its plot kwargs
    """
    
    def __init__(self, expression:str, times:NDArray[float_]|None=None, npt:int|None=None, exptime:float|int|None=None, supersampling:int|None=None, 
                 datasetname:str|None=None, pl_kwargs:Dict|None=None, pl_kwargs_error:Dict|None=None, show_error:bool=True):
        self._init_expression(expression=expression)
        self._check_expression_4_data(expression=self.expression)
        self.__times:NDArray[float_]|None = None
        if times is not None:
            self.set_times(times=times)
        self.__npt:int|None = None  
        if npt is not None:
            self.set_npt(npt=npt)
        self._init_ModelBinning(exptime=exptime, supersampling=supersampling)
        self._init_datasetname(datasetname=datasetname)
        self._init_pl_kwargs(pl_kwargs=pl_kwargs)
        self._init_pl_kwargs_err(pl_kwargs_error=pl_kwargs_error)
        self.show_error = show_error

    @property
    def expression(self) -> Expression:
        # Return a list of unique terms (removing duplicates)
        return self.__expression
    
    def _init_expression(self, expression:str):
        self.__expression = Expression(expression=expression)
            
    def _check_expression_4_data(self, expression:Expression):
        if "data" in expression.components:
            raise ValueError("expression cannot involve data")

    @property
    def times(self) -> NDArray[float_]|None:
        return copy(self.__times)
    
    def set_times(self, times:NDArray[float_]):
        if not(isinstance(times, ndarray)):
            raise TypeError(f"times should be numpy.ndarray of float, got {type(times)}.")
        self.__times = copy(times)

    def get_times(self, post_instance:Posterior|None=None, npt_default:int=1000, extra_dt:float=0.) -> NDArray[float_]:
        """Return the times vector define by the user or return a default one using the """
        if self.times is not None:
            return self.times
        else:
            if post_instance is None:
                raise ValueError("You didn't specify times. To be able to compute a default time vector you need to provide post_instance !")
            times_dataset = copy(post_instance.dataset_db[self.datasetname].get_datasetkwarg("time"))
            if self.npt is None:
                npt = npt_default
            else:
                npt = self.npt
            return linspace(min(times_dataset) - extra_dt, max(times_dataset) + extra_dt, 
                            npt, endpoint=True)
            
    @property
    def npt(self) -> int|None:
        return self.__npt
    
    def set_npt(self, npt:int):
        if self.times is not None:
            raise ValueError("You cannot set both times and npt.")
        if not(isinstance(npt, int)) or not(npt >1):
            raise TypeError(f"npt should be int > 1, got {type(npt)}.")
        self.__npt = npt

    def _init_ModelBinning(self, exptime:float|int|None, supersampling:int|None):
        self.__modelbinning = ModelBinning(exptime=exptime, supersampling=supersampling)

    @property
    def binning(self):
        return self.__modelbinning
    
    @property
    def exptime(self) -> float|int:
        return self.binning.exptime
    
    @property
    def supersampling(self) -> int:
        return self.binning.supersampling

    @property
    def datasetname(self) -> str|None:
        return self.__datasetname
            
    def _init_datasetname(self, datasetname:str|None):
        self.__datasetname:str|None = None
        if datasetname is not None:
            self.set_datasetname(datasetname=datasetname)

    def set_datasetname(self, datasetname:str):
        if not(isinstance(datasetname, str)):
            raise TypeError(f"datasetname be a string, got {type(datasetname)}.")
        self.__datasetname = datasetname

    @property
    def pl_kwargs(self) -> Dict:
        return self.__pl_kwargs

    def _init_pl_kwargs(self, pl_kwargs:dict|None):
        self.__pl_kwargs: Dict = {}
        if pl_kwargs is not None:
            if not(isinstance(pl_kwargs, dict)):
                raise TypeError(f"pl_kwargs should be a dict or None, got {type(pl_kwargs)}")
            else:
                self.pl_kwargs.update(pl_kwargs)
    
    @property
    def pl_kwargs_error(self) -> Dict:
        return self.__pl_kwargs_err
    
    def _init_pl_kwargs_err(self, pl_kwargs_error:dict|None):
        self.__pl_kwargs_err: Dict = {}
        if pl_kwargs_error is not None:
            if not(isinstance(pl_kwargs_error, dict)):
                raise TypeError(f"pl_kwargs should be a dict or None, got {type(pl_kwargs_error)}")
            else:
                self.pl_kwargs_error.update(pl_kwargs_error)
    
    @property
    def show_error(self) -> bool:
        return self.__show_error
    
    @show_error.setter
    def show_error(self, show_error:bool):
        if not(isinstance(show_error, bool)):
            raise TypeError(f"show_error should be a bool, got {type(show_error)}")
        self.__show_error = show_error
    

class Data2plot(Model2plot):

    def __init__(self, expression:str, exptime:float|int|None=None, method:str|None=None,
                 datasetname:str|None=None, pl_kwargs:Dict|None=None, pl_kwargs_error:Dict|None=None, show_error:bool=True):
        self._init_expression(expression=expression)
        self._check_expression_4_data(expression=self.expression)
        self._init_DataBinning(exptime=exptime, method=method)
        self._init_datasetname(datasetname=datasetname)
        self._init_pl_kwargs(pl_kwargs=pl_kwargs)
        self._init_pl_kwargs_err(pl_kwargs_error=pl_kwargs_error)
        self.show_error = show_error

    def _check_expression_4_data(self, expression:Expression):
        if "data" not in expression.components:
            raise ValueError("expression needs to involve data")
        
    def _init_DataBinning(self, exptime:float|int|None, method:str|None):
        self.__databinning = DataBinning(exptime=exptime, method=method)

    @property
    def binning(self):
        return self.__databinning
    
    @property
    def exptime(self) -> float|int:
        return self.binning.exptime
    
    @property
    def method(self) -> str:
        return self.binning.method

    def get_times_dataset(self, post_instance:Posterior) -> NDArray[float_]:
        """Return the times vector of the dataset"""
        return copy(post_instance.dataset_db[self.datasetname].get_datasetkwarg("time"))
    

class MultiDataBin2plot(Data2plot):

    def __init__(self, l_expression_and_datasetname:list[tuple[str, str]], exptime:float|int|None=None, method:str|None=None,
                 pl_kwargs:Dict|None=None, pl_kwargs_error:Dict|None=None, show_error:bool=True):
        self._init_l_data2plot(l_expression_and_datasetname=l_expression_and_datasetname, exptime=exptime, method=method)
        self._init_DataBinning(exptime=exptime, method=method)
        self._init_pl_kwargs(pl_kwargs=pl_kwargs)
        self._init_pl_kwargs_err(pl_kwargs_error=pl_kwargs_error)
        self.show_error = show_error
    
    @property
    def l_data2plot(self):
        return self.__l_data2plot

    def _init_l_data2plot(self, l_expression_and_datasetname:list[tuple[str, str]], exptime:float|int|None=None, method:str|None=None):
        self.__l_data2plot = [Data2plot(expression=expression_i, exptime=exptime, method=method, datasetname=datasetname_i, 
                                        pl_kwargs=None, pl_kwargs_error=None, show_error=False)
                              for expression_i, datasetname_i in l_expression_and_datasetname]
        

class ComputedModel(object):
    """Class to store computed models values: expression, binning, datasetname, times, values, errors
    """
    def __init__(self, expression:str, datasetname:str, binning:ModelBinning|DataBinning,
                 times:NDArray[float_], values:NDArray[float_], errors:NDArray[float_]):
        self.__expression:Expression = Expression(expression=expression)
        self.__set_datasetname(datasetname=datasetname)
        self.__binning:ModelBinning|DataBinning = binning
        self.__set_computed_model(times=times, values=values, errors=errors)

    @property
    def expression(self) -> Expression:
        # Return a list of unique terms (removing duplicates)
        return self.__expression
    
    @property
    def datasetname(self) -> str:
        return self.__datasetname

    def __set_datasetname(self, datasetname:str):
        if not(isinstance(datasetname, str)):
            raise TypeError(f"datasetname be a string, got {type(datasetname)}.")
        self.__datasetname = datasetname

    @property
    def binning(self) -> ModelBinning:
        return self.__binning
    
    @property
    def exptime(self) -> float|int:
        return self.__binning.exptime
    
    @property
    def supersampling(self) -> int:
        return self.__binning.supersampling

    @property
    def times(self) -> NDArray[float_]:
        """Return original time vector stored"""
        return self.__times
    
    @property
    def values(self) -> NDArray[float_]:
        """Return original model values vector stored"""
        return self.__values
    
    @property
    def errors(self) -> NDArray[float_]|None:
        """Return original model errors vector stored"""
        return self.__errors
    
    def __set_computed_model(self, times:NDArray[float_], values:NDArray[float_], errors: NDArray[float_]|None=None):
        """Set the computed model (times and values).
        
        If npt and/or t_lims have been set, the times and values arguments will be check against those.
        If they were not set alreay they will be set using the times and values arguments.

        Once a computed model has been set it cannot be overwritten.
        """
        # Checking the times, values and values_err input are proper
        if not(isinstance(times, ndarray)) or not(isinstance(values, ndarray)) or not((errors is None) or isinstance(errors, ndarray)):
            raise TypeError(f"times, values and values_err should be numpy.ndarray, got {type(times)}, {type(values)} and {type(errors)} respectively.")
        if (times.ndim != 1) or (values.ndim != 1) or ((errors is not None) and (values.ndim != 1)):
            raise ValueError(f"times, values and values_err (if not None) should be ndarray with 1 dimension. The number of dimension of times is {times.ndim}, the one of values is {values.ndim} and {'values_err is None' if errors is None else f'the one of values_err is {errors.ndim}'}")
        if (times.size != values.size) or ((errors is not None) and (times.size != errors.size)):
            raise ValueError(f"times, values and values_err (if not None) should have the same size. times' size is {times.size}, values' size is {values.size} and {'values_err is None' if errors is None else f'values_err size is {errors.size}'}")
        self.__times:NDArray[float_] = times
        self.__values:NDArray[float_] = values
        self.__errors:NDArray[float_]|None = errors

    def get_computed_model(self):
        """Return copies of the times, values and errors stored"""
        return self.times.copy(), self.values.copy(), copy(self.errors)

    
class ComputedModels_Database(object):
    """Class to store the computed models (for all model expressions, all datasets, all times, all binning)
    """

    __err_msg_model_already_computed = "The model has already been computed, you can no longer modify {}."
    
    def __init__(self):
        self.__stored_models:list[ComputedModel] = []

    @property
    def stored_models(self) -> list[ComputedModel]:
        return self.__stored_models

    def find_computed_model(self, expression:str, datasetname:str, binning:DataBinning|ModelBinning,
                            times:NDArray[float_]) -> tuple[ComputedModel|None, int|None, NDArray[float_]|None]:
        model_found:ComputedModel|None = None
        times_found:NDArray[float_]|None = None
        i_model_found:list[int] = []
        for ii, computed_model in enumerate(self.stored_models):
            if array_equal(computed_model.times, times):
                times_found = computed_model.times
            if ((computed_model.expression.expression == expression) and 
                (computed_model.datasetname == datasetname) and 
                (computed_model.binning == binning) and
                array_equal(computed_model.times, times)
                ):
                if model_found is not None:
                    i_model_found.append(ii)
                model_found = computed_model
        if len(i_model_found) > 1:
            print(f"Warning: The model has been found multiple times in the database at indexes {i_model_found}")
        if len(i_model_found) > 0:
            return model_found, i_model_found[-1], times_found
        else:
            return None, None, times_found
    
    def store_computed_model(self, expression:str, datasetname:str, binning:ModelBinning|DataBinning,
                             times:NDArray[float_], values:NDArray[float_], errors:NDArray[float_],
                             overwrite: bool=False):
        """Set the computed model (times and values).
        
        If npt and/or t_lims have been set, the times and values arguments will be check against those.
        If they were not set alreay they will be set using the times and values arguments.

        Once a computed model has been set it cannot be overwritten.
        """
        model_found, _, times_found = self.find_computed_model(expression=expression, datasetname=datasetname, binning=binning,
                                                               times=times)
        if not((model_found is not None) and not(overwrite)):
            if (model_found is not None) and overwrite:
                logger.info("Such model is already in the database, but it will be overwritten.")
            if times_found is not None:
                times = times_found
            self.stored_models.append(ComputedModel(expression=expression, datasetname=datasetname, binning=binning,
                                                    times=times, values=values, errors=errors))
        else:
           logger.warning("Such model is already in the database and overwrite is False. The store command will be ignored.")

    def show_stored_models(self):
        dico = OrderedDict()
        for ii, stored_model_i in enumerate(self.stored_models):
            dico[ii] = {'expression': stored_model_i.expression.expression,
                        'datasetname': stored_model_i.datasetname,
                        'binning': stored_model_i.binning,
                        'times': {'size': stored_model_i.times.size, 
                                  'min': min(stored_model_i.times),
                                  'max': max(stored_model_i.times),
                                  },
                        }
        pprint(dico)


# class Database_Model2computeNplot(object):
#     """Database to store the Model2computeNplot model and access them easily
#     """

#     def __init__(self, tuples_name_model2computenplot: Sequence[tuple[str|int|None, Model2computeNplot]]|None=None, overwrite=False):
#         """"""
#         # Init models2computenplot
#         self.__models2computenplot: Dict[str|int, Model2computeNplot] = {}
#         # Add models2computenplot to the database
#         self.add_models2computenplot(tuples_name_model2computenplot=tuples_name_model2computenplot, overwrite=overwrite)

#     @property
#     def name2modelspec(self) -> Dict[str|int, ModelSpecification]:
#         """Dictionary providing the conversion from names to model specifications (what the model is composed of in terms of model component added and removed and the dataset used)"""
#         return {name: model2computenplot.modelspec for name, model2computenplot in self.__models2computenplot.items()}
    
#     def __find_modelspec(self, modelspec: ModelSpecification):
#         name_found = None
#         for name_i, modelspec_i in self.name2modelspec.items():
#             if modelspec == modelspec_i:
#                 name_found = name_i
#                 break
#         return name_found

#     def add_model2computenplot(self, model2computenplot: Model2computeNplot, name: None|int|str=None, overwrite=False):
#         """"""
#         # Check the type of model2computenplot
#         if not(isinstance(model2computenplot, Model2computeNplot)):
#             raise TypeError(f"model2computenplot should be a Model2computeNplot instance, got a {type(model2computenplot)}")
#         # Check the type of name
#         if name is None:
#             name = 0
#             while name in self.__models2computenplot:
#                 name += 1
#         if not(isinstance(name, int)) and not(isinstance(name, str)):
#             raise TypeError(f"name should be either an int, a str or None, got {name}")
#         # Check if a model2computenplot with the same ModelSpecification already exists
#         name_found = self.__find_modelspec(modelspec=model2computenplot.modelspec)
#         if name_found:
#             if overwrite:
#                 logger.warning(f"A Model2computeNplot instance with the same ModelSpecification and name {name_found} was found in the Database_Model2computeNplot. It will be replaced by a the provided model2computenplot with name {name}")
#                 if name_found != name:
#                     self.__models2computenplot.pop(name_found)
#         self.__models2computenplot[name] = model2computenplot

#     def add_models2computenplot(self, tuples_name_model2computenplot: Sequence[tuple[str|int|None, Model2computeNplot]], overwrite=False):
#         """"""
#         for name, model2computenplot in tuples_name_model2computenplot:
#             self.add_model2computenplot(name=name, model2computenplot=model2computenplot, overwrite=overwrite)

#     def get_models2computenplot(self, modelspec: ModelSpecification|None, name: str|int|None) -> tuple[Model2computeNplot|None, str|int|None]:
#         """"""
#         if (name is None) == (modelspec is None):
#             raise ValueError(f"You need to provide either name or modelspec (and not both), you provided name={name} and modelspec={modelspec}")
#         if name is None:
#             name_found = self.__find_modelspec(modelspec=modelspec)
#         else:
#             name_found = name
#         if name_found:
#             return self.__models2computenplot[name_found], name_found
#         else:
#             return None, name_found
    
    
class PlotsDefinition(object):
    """Class to specifiy which models to plot in which axis of a figure that contains of a subplots grid with N rows and M columns.

    At creation you can specify the number of rows and columns of the grid and if you want the same models
    to be plots in all rows or in all columns.

    For each axis in the grid this class allows to define which model(s) to plot, the way to plot them (pl_kwargs),
    and the x and y limits for the axis.

    Internally this information is stored in 3 class attribute:
    - grid: a tuple of tuple of lists of name such that grid[i_row][i_col] gives the list of models names that you want to plot in the
        axis located at row i_row and at column i_col.
    - models: a dictionary of Model2plot that match the names used in grid with a model instance.
    - lims: a tuple of tuple of dict of tuple of float such that lims[i_row][i_col]['x'] give the xlims 
        and lims[i_row][i_col]['y'] give the ylims
    """

    def __init__(self, nb_rows:int|None=None, same4allrows:bool=False, nb_cols:int|None=None, same4allcols:bool=False):
        """"""
        # Default nb_rows and nb_cols
        if nb_rows is None:
            nb_rows = 1
        if nb_cols is None:
            nb_cols = 1
        # Check and set nb_rows and nb_cols
        if not(isinstance(nb_rows, int)) or (nb_rows < 1):
            raise TypeError(f"nb_rows should be a strictly positive int, got {nb_rows}")
        self.__nb_rows: int = nb_rows
        if not(isinstance(nb_cols, int)) or (nb_cols < 1):
            raise TypeError(f"nb_cols should be a strictly positive int, got {nb_cols}")
        self.__nb_cols: int = nb_cols
        # Check and set same4allrows, same4allcols
        if not(isinstance(same4allrows, bool)):
            raise TypeError(f"same4allrows should be a bool, got {same4allrows}")
        self.__same4allrows: bool = same4allrows
        if self.same4allrows:
            nb_rows = 1
        if not(isinstance(same4allcols, bool)):
            raise TypeError(f"same4allcols should be a bool, got {same4allcols}")
        self.__same4allcols: bool = same4allcols
        if self.same4allcols:
            nb_cols = 1
        # Init grid
        self.__grid:tuple[tuple[list[str], ...], ...] = tuple([tuple([[] for _ in range(nb_cols)]) for _ in range(nb_rows)])
        # Init lims
        self.__lims:tuple[tuple[dict[str,tuple[float|None,float|None]], ...], ...] = tuple([tuple([{"x":(None, None),"y_data":(None, None), "y_resi":(None, None)} for _ in range(nb_cols)]) for _ in range(nb_rows)])
        # Init models2plot_database
        self.__things2plot: Dict[str, Model2plot|Data2plot|MultiDataBin2plot] = {}

    def __repr__(self):
        return f"{self.__grid}"

    @property
    def nb_rows(self) -> int:
        """numbers of rows in the plot"""
        return self.__nb_rows
    
    @property
    def nb_cols(self) -> int:
        """numbers of rows in the plot"""
        return self.__nb_cols
    
    @property
    def same4allrows(self) -> bool:
        """If True, all rows have the same models to plot"""
        return self.__same4allrows
    
    @property
    def same4allcols(self) -> bool:
        """If True, all columns have the same models to plot"""
        return self.__same4allcols
    
    @property
    def grid(self) -> tuple[tuple[list[str], ...], ...]:
        """Grid (in the form of a tuple of tuple) with the list of what to plot in each element of the grid"""
        return deepcopy(self.__grid)
    
    @property
    def lims(self) -> tuple[tuple[dict[str,tuple[float|None,float|None]], ...], ...]:
        """Grid (in the form of a tuple of tuple) with a dict with three keys 'x', 'y_data', 'y_resi' whose values are tuples which give the x and y limits for the axis."""
        return deepcopy(self.__lims)

    @property
    def things2plot(self) -> Dict[str, Model2plot|Data2plot|MultiDataBin2plot]:
        """Dictionary providing the conversion from names to Model2plot, Data2plot or MultiDataBin2plot instances"""
        return self.__things2plot.copy()
    
    def __get_l_i(self, idx:int|None, roworcol:str) -> list[int]:
        """Return a list of idx depending on idx and colorrow"""
        if roworcol == 'row':
            size = len(self.grid)
        elif roworcol == 'col':
            size = len(self.grid[0])
        else:
            raise ValueError(f"roworcol should be in ['col', 'row'], got {roworcol}")
        # If you don't provide i_row it means that you want to add to all rows
        if idx is None:
            l_idx = list(range(size))
        else:
            l_idx = [idx, ]
        return l_idx

    def add_existing_to_grid(self, name:str, i_row:int|None=None, i_col:int|None=None):
        """Add a model that is already in the models2plot in the grid."""
        # Check that name is in models
        if not(name in self.things2plot):
            raise ValueError(f"There is no model2plot with name {name}.")
        l_i_row = self.__get_l_i(idx=i_row, roworcol='row')
        l_i_col = self.__get_l_i(idx=i_col, roworcol='col')
        # Make sure that i_row and i_col are correct
        for i_row in l_i_row:
            for i_col in l_i_col:
                # Add the name to the grid
                self.__grid[i_row][i_col].append(name)

    def removefromgrid(self, i_row:int, i_col:int, name:str):
        """Remove a model from the grid"""
        self.__grid[i_row][i_col].remove(name)
        
    def add_modelordata2plot(self, expression:str, name:str|None=None, overwrite:bool=False, **kwargs) -> str:
        """Add a Model2plot or Data2plot to things2plot
        """
        # Check if name already exists
        if (name is not None) and (name in self.things2plot) and not(overwrite):
            raise ValueError(f"There is already a model2plot with this name ({name}). Please choose another name")
        elif (name is not None) and (name in self.things2plot) and not(overwrite):
            logger.info(f"There is already a model2plot with this name ({name}). It will be overwritten")
        elif name is None:
            basename = expression
            if ('datasetname' in kwargs) and (kwargs['datasetname']):
                basename += f"_{kwargs['datasetname']}" 
            ii = 0
            name = f"{basename}"
            while name in self.things2plot:
                ii += 1
                name = f"{basename}_{ii}"
        # Add instance to models
        expression_instance = Expression(expression=expression)
        if "data" in expression_instance.components:
            self.__things2plot[name] = Data2plot(expression=expression, **kwargs)
        else:
            self.__things2plot[name] = Model2plot(expression=expression, **kwargs)
        return name
    
    def add_multidatab2plot(self, l_expression_and_datasetname:list[tuple[str, str]], name:str|None=None, overwrite:bool=False, **kwargs) -> str:
        """Add a MultiDataBin2plot to things2plot
        """
        # Check if name already exists
        if (name is not None) and (name in self.things2plot) and not(overwrite):
            raise ValueError(f"There is already a model2plot with this name ({name}). Please choose another name")
        elif (name is not None) and (name in self.things2plot) and not(overwrite):
            logger.info(f"There is already a model2plot with this name ({name}). It will be overwritten")
        elif name is None:
            basename = "multidatabin"
            ii = 0
            name = f"{basename}"
            while name in self.things2plot:
                ii += 1
                name = f"{basename}_{ii}"
        # Add instance to models
        self.__things2plot[name] = MultiDataBin2plot(l_expression_and_datasetname=l_expression_and_datasetname, **kwargs)
        return name
    
    def getthing2plot(self, name:str) -> Model2plot|Data2plot|MultiDataBin2plot:
        """Get a Model2plot from models"""
        # Check that name is in models
        if not(name in self.things2plot):
            raise ValueError(f"There is nothing to plot with name {name}.")
        return self.things2plot[name]
    
    def add_modelordata_to_grid(self, expression:str, i_row:int|None=None, i_col:int|None=None, name:str|None=None, overwrite:bool=False, **kwargs):
        """Add a model that is already in the grid.
        
        This function is a wrapper around addtogrid and addtomodels for the user convenience.
        There is two use cases:
        2. Adding a model to models and to grid in one function call
        """
        # If you don't provide i_row it means that you want to add to all rows
        l_i_rows = self.__get_l_i(idx=i_row, roworcol='row')
        l_i_cols = self.__get_l_i(idx=i_col, roworcol='col')
        # Add
        name = self.add_modelordata2plot(expression=expression, name=name, overwrite=overwrite, **kwargs)
        for i_row in l_i_rows:
            for i_col in l_i_cols:
                self.add_existing_to_grid(i_row=i_row, i_col=i_col, name=name)

    def add_multidatabin_to_grid(self, l_expression_and_datasetname:list[tuple[str, str]], i_row:int|None=None, i_col:int|None=None, name:str|None=None, overwrite:bool=False, **kwargs):
        """Add a model that is already in the grid.
        
        This function is a wrapper around addtogrid and addtomodels for the user convenience.
        There is two use cases:
        2. Adding a model to models and to grid in one function call
        """
        # If you don't provide i_row it means that you want to add to all rows
        l_i_rows = self.__get_l_i(idx=i_row, roworcol='row')
        l_i_cols = self.__get_l_i(idx=i_col, roworcol='col')
        name = self.add_multidatab2plot(l_expression_and_datasetname=l_expression_and_datasetname, name=name, overwrite=overwrite, **kwargs)
        for i_row in l_i_rows:
            for i_col in l_i_cols:
                self.add_existing_to_grid(i_row=i_row, i_col=i_col, name=name)

    def setdatasetname(self, datasetname:str, i_row:int|None=None, i_col:int|None=None, name:str|list[str]|None=None):
        """Set the datasetname for the models2plot that do not have a dataset"""
        # If you don't provide i_row it means that you want to add to all rows
        l_i_rows = self.__get_l_i(idx=i_row, roworcol='row')
        l_i_cols = self.__get_l_i(idx=i_col, roworcol='col')
        # Set datasetname:
        for i_row in l_i_rows:
            for i_col in l_i_cols:
                # If you don't provide name it is that you want to set all models in the current location of the grid
                if name is None:
                    l_name = self.grid[i_row][i_col]
                elif isinstance(name, str):
                    l_name = [name, ]
                elif isinstance(name, list) and all([isinstance(name_i, str) for name_i in name]):
                    l_name = copy(name)
                else:
                    raise TypeError(f"name should be either None, or a str or a list of str, got {name}")
                for name in l_name:
                    if name not in self.grid[i_row][i_col]:
                        logger.info(f"No model with name {name} in the grid at row {i_row} and col {i_col}")
                    else:
                        thing2plot = self.getthing2plot(name=name)
                        if isinstance(thing2plot, MultiDataBin2plot):
                            pass
                        else:
                            if thing2plot.datasetname is None:
                                thing2plot.set_datasetname(datasetname=datasetname)
                            else:
                                logger.info(f"{name} (found in the grid at row {i_row} and col {i_col}) already as a datasetname ({thing2plot.datasetname}) it will not be changed")
        
    def get_models2plot(self, i_row:int, i_col:int) -> OrderedDict[str,Model2plot]:
        """For a given axis of the grid (designated by i_row and i_col), return an OrderedDict with the Model2plot instances for this axis
        """
        res = OrderedDict()
        for name in self.grid[i_row][i_col]:
            if type(self.things2plot[name]) is Model2plot:
                res[name] = self.things2plot[name]
        return res

    def get_datas2plot(self, i_row:int, i_col:int) -> OrderedDict[str,Data2plot]:
        """For a given axis of the grid (designated by i_row and i_col), return an OrderedDict with the Model2plot instances for this axis
        """
        res = OrderedDict()
        for name in self.grid[i_row][i_col]:
            if type(self.things2plot[name]) is Data2plot:
                res[name] = self.things2plot[name]
        return res

    def get_multidatabins2plot(self, i_row:int, i_col:int) -> OrderedDict[str, MultiDataBin2plot]:
        """For a given axis of the grid (designated by i_row and i_col), return an OrderedDict with the Model2plot instances for this axis
        """
        res = OrderedDict()
        for name in self.grid[i_row][i_col]:
            if type(self.things2plot[name]) is MultiDataBin2plot:
                res[name] = self.things2plot[name]
        return res
    
    def get_used_datasetnames(self, i_row:int, i_col:int) -> list[str]:
        """Return the list of all datasetnames used in a given axis of the grid (designated by i_row and i_col)."""
        datasetnames = []
        for data2plot_i in self.get_datas2plot(i_row=i_row, i_col=i_col).values():
            datasetnames.append(data2plot_i.datasetname)
        return list(set(datasetnames))
    
    def get_axis_xlims(self, i_row:int, i_col:int) -> tuple[float|None,float|None]:
        """Return a tuple giving the xlims for one axis of the grid designated by i_row and i_col."""
        return self.lims[i_row][i_col]['x']
    
    def set_axis_xlims(self, lims:tuple[float|None, float|None], i_row:int, i_col:int):
        """Set the xlims for one axis of the grid designated by i_row and i_col."""
        self.lims[i_row][i_col]['x'] = lims
    
    def get_axis_ylims_data(self, i_row:int, i_col:int) -> tuple[float|None,float|None]:
        """Return a tuple giving the xlims for one axis of the grid designated by i_row and i_col."""
        return self.lims[i_row][i_col]['y_data']
    
    def set_axis_ylims_data(self, lims:tuple[float|None, float|None], i_row:int, i_col:int):
        """Set the ylims for the data plot of one axis of the grid designated by i_row and i_col."""
        self.lims[i_row][i_col]['y_data'] = lims
    
    def get_axis_ylims_resi(self, i_row:int, i_col:int) -> tuple[float|None,float|None]:
        """Return a tuple giving the xlims for one axis of the grid designated by i_row and i_col."""
        return self.lims[i_row][i_col]['y_resi']
    
    def set_axis_ylims_resi(self, lims:tuple[float|None, float|None], i_row:int, i_col:int):
        """Set the ylims for the resi plot of one axis of the grid designated by i_row and i_col."""
        self.lims[i_row][i_col]['y_resi'] = lims
        
    # def get_all_modelnames(self) -> list[str]:
    #     """Return the list of all the names of the Model2plot instances used in the grid."""
    #     l_i_rows = self.__get_l_i(roworcol='row')
    #     l_i_cols = self.__get_l_i(roworcol='col')
    #     model_names = []
    #     for i_row in l_i_rows:
    #         for i_col in l_i_cols:
    #             model_names.extend(self.grid[i_row][i_col])
    #     return list(set(model_names))

    # def get_all_datasetnames(self) -> list[str]:
    #     """Return the list of all datasetnames of the Model2plot instances used in the grid."""
    #     model_names = self.get_all_modelnames()
    #     datasetnames = []
    #     for name in model_names:
    #         datasetnames.append(self.models[name].datasetname)
    #     return list(set(datasetnames))
        
        # if name_found:
        #     if name is None:
        #         name = name_found
        #     elif name != name_found:
        #         logger.info(f"The same modelspec with a different name ({name_found}) already exist. The new name provided ({name}) will be ignored")
        #         name = name_found
        # # If check the name
        # else:
        #     if name is None or (name in self.name2modelspec):
        #         if name in self.name2modelspec:
        #             logger.info(f"The name {name} already exists for another model spec and an automatic name will be assigned")
        #         name = get_default_model_name(seq_current_model_name=self.__modelspecs.keys())
        #         logger.info(f"name automatically assigned to {name}.")
        # # Add the model name to models2 plot
        # for i_row in self.__get_l_idx(row_or_col='row', idx=row_idx):
        #     for i_col in self.__get_l_idx(row_or_col='col', idx=col_idx):
        #         self.__models2plot[i_row][i_col].append(name)
        # # Add the modelspecs to modelspecs
        # if name not in self.name2modelspec:
        #     self.__modelspecs[name] = modelspec
        #     # Init pl_kwargs for the model
        #     self.__pl_kwargs[name] = {}
        #     if pl_kwargs is not None:
        #         self.update_pl_kwargs(name=name, pl_kwargs_4_name=pl_kwargs)

    # def update_pl_kwargs(self, name: str|int, pl_kwargs_4_name: Dict[tuple[Number,int]|str, Dict]):
    #     """"""
    #     # Check name
    #     if name not in self.__pl_kwargs.keys():
    #         raise ValueError(f"{name} is not the name of an existing modelspec. Existing names are {list(self.name2modelspec.keys())}")
    #     # Check pl_kwargs
    #     if not(isinstance(pl_kwargs_4_name, dict)) or any([not(isinstance(tuple_exptimebin_supersamp, tuple) and (isinstance(tuple_exptimebin_supersamp[0], Number)) and (isinstance(tuple_exptimebin_supersamp[1], int))) and
    #         not(tuple_exptimebin_supersamp == 'default') for tuple_exptimebin_supersamp in pl_kwargs_4_name.keys()]):
    #         raise TypeError(f"pl_kwargs should be a dict and its keys should be either 'default' or a tuple[Number, int], got {pl_kwargs_4_name}.")
    #     for tuple_exptimebin_supersamp, pl_kwargs_i in pl_kwargs_4_name.items():
    #         if not(isinstance(pl_kwargs_i, dict)):
    #             raise TypeError(f"Value for key {tuple_exptimebin_supersamp} of pl_kwargs_4_name should be a Dict, got a {type(pl_kwargs_i)}")
    #     # Create the tuple_exptimebin_supersamp if needed and then update
    #     for tuple_exptimebin_supersamp in pl_kwargs_4_name:
    #         if tuple_exptimebin_supersamp not in self.__pl_kwargs[name]:
    #             self.__pl_kwargs[name][tuple_exptimebin_supersamp] = {}
    #         self.__pl_kwargs[name][tuple_exptimebin_supersamp].update(pl_kwargs_4_name[tuple_exptimebin_supersamp])

    # def reset_pl_kwargs(self, name: str|int, tuple_exptimebin_supersamp: tuple[Number,int]|str|None=None):
    #     # Check name
    #     if name not in self.__pl_kwargs.keys():
    #         raise ValueError(f"{name} is not the name of an existing modelspec. Existing names are {list(self.name2modelspec.keys())}")
    #     # Check tuple_exptimebin_supersamp and pop
    #     if tuple_exptimebin_supersamp is not None:
    #         if tuple_exptimebin_supersamp not in self.__pl_kwargs[name]:
    #             raise KeyError(f"{tuple_exptimebin_supersamp} is not a key of self.__pl_kwargs[{name}], existing keys are {list(self.__pl_kwargs[name].keys())}")
    #         else:
    #             self.__pl_kwargs[name].pop(tuple_exptimebin_supersamp)
    #     else:
    #         self.__pl_kwargs[name] = {}
    
    # def set_pl_kwargs(self, pl_kwargs: Dict, exptime_bin: Number|None=None, supersamp: int|None=None, overwrite: bool=False, update: bool=True):
    #     """Set the dictionary of the kwargs for ploting the specified model.
        
    #     If no exptime_bin and supersamp is provided you will set the default pl_kwargs
    #     """
    #     # Check the pl_kwargs input
    #     if not(isinstance(pl_kwargs, dict)):
    #         raise ValueError(f"pl_kwargs should be a dictionary. You provided a {type(pl_kwargs)}.")
    #     # Check the exptime_bin and supersamp input
    #     if (exptime_bin is None) != (supersamp is None):
    #         raise ValueError(f"You should either provide both exptime_bin and supersamp or none of them. You provided exptime_bin={exptime_bin} and supersamp={supersamp}.")
    #     # If both exptime_bin and supersamp is None, set the default_pl_kwargs
    #     if (exptime_bin is None) and (supersamp is None):
    #         self.__default_pl_kwargs = pl_kwargs
    #     else:
    #         # Checking exptime_bin and supersamp
    #         if not(isinstance(exptime_bin, Number)) or (exptime_bin < 0):
    #             raise ValueError(f"exptime_bin should be a positive (or zero) Number, got {exptime_bin}")
    #         if not(isinstance(supersamp, int)) or (supersamp < 1):
    #             raise ValueError(f"supersamp should be an int superior or equal to 1, got {supersamp}")
    #         # Setting the pl_kwargs
    #         if (self.__pl_kwargs is None):
    #             self.__pl_kwargs = {}
    #         if exptime_bin not in self.__pl_kwargs:
    #             self.__pl_kwargs[exptime_bin] = {}
    #         self.__pl_kwargs[exptime_bin][supersamp] = pl_kwargs

    # def get_pl_kwargs(self, name: int|str, tuple_exptimebin_supersamp: tuple[Number, int]|str) -> Dict:
    #     # Check name
    #     if name not in self.__pl_kwargs.keys():
    #         raise KeyError(f"{name} is not the name of an existing modelspec. Existing names are {list(self.name2modelspec.keys())}")
    #     # Check tuple_exptimebin_supersamp
    #     # if not(isinstance(tuple_exptimebin_supersamp, tuple) and (isinstance(tuple_exptimebin_supersamp[0], Number)) and (isinstance(tuple_exptimebin_supersamp[1], int))) and
    #     #     not(tuple_exptimebin_supersamp == 'default'):
    #     #     raise TypeError(f"tuple_exptimebin_supersamp should be either 'default' or a tuple[Number, int], got {tuple_exptimebin_supersamp}")
    #     if tuple_exptimebin_supersamp not in self.__pl_kwargs[name].keys():
    #         raise KeyError(f"{tuple_exptimebin_supersamp} is not available in self.__pl_kwargs[{name}]. Available keys are {self.__pl_kwargs[name].keys()}")
    #     return self.__pl_kwargs[name][tuple_exptimebin_supersamp]

    # def get_pl_kwargs(self, exptime_bin: Number, supersamp: int) -> Dict:
    #     """Return the dictionary of the kwargs for ploting the specified model"""
    #     if (self.__pl_kwargs is None) or (exptime_bin not in self.__pl_kwargs) or (supersamp not in self.__pl_kwargs[exptime_bin]):
    #         return self.default_pl_kwargs
    #     else:
    #         return self.__pl_kwargs[exptime_bin][supersamp]s
                    

    # def add_models_2_plot(self, tuples_name_modelspec: Sequence[tuple[str|int|None, ModelSpecification]], row_idx: int|None = None, col_idx: int|None = None):
    #     """Add multiple models to show for a given row.
        
    #     Arguments
    #     ---------

    #     """
    #     if not(isinstance(tuples_name_modelspec, Sequence)) or not(all([isinstance(tuple_name_modelspec_i, tuple) for tuple_name_modelspec_i in tuples_name_modelspec])) or not(all([len(tuple_name_modelspec_i) == 2 for tuple_name_modelspec_i in tuples_name_modelspec])):
    #         raise TypeError(f"modelspecs should be a Sequence types of 2 elements , got {tuples_name_modelspec}")
    #     for name_i, modelspec_i in tuples_name_modelspec:
    #         self.add_model_2_plot(modelspec=modelspec_i, name=name_i, row_idx=row_idx, col_idx=col_idx)
    
    # def get_models_2_plot(self, row_idx: int|None=None, col_idx: int|None=None) -> Dict[str|int, ModelSpecification]:
    #     """Return the list of models to show for a given row index
        
    #     If you only want to return models to show for a given model name, you can specify the model argument.

    #     Argument
    #     --------
    #     row_idx : Specifies the row of the plot for which you want the set of models to show

    #     Return
    #     ------
    #     models  : Set of model names to show for the row
    #     """
    #     # Check row_idx and col_idx
    #     checked_idx = {}
    #     for row_or_col, idx in zip(["row", "col"], [row_idx, col_idx]):
    #         checked_idx[row_or_col], nb, same4all = self.__check_idx(row_or_col=row_or_col, idx=idx, allow_idx_w_same4all=True)
    #         if checked_idx[row_or_col] is None:
    #             raise ValueError(f"{row_or_col}_idx should not be None.")
    #     return {name_i: self.name2modelspec[name_i] for name_i in self.__models2plot[checked_idx['row']][checked_idx['col']]}
    

# def check_Models2plot(models2plot: Models2plot|None, datasetnames4rowidx: Sequence[Sequence[str]], l_model_1_per_row: Sequence[str]) -> Models2plot:
#     """

#     Arguments
#     ---------
#     datasetnames4rowidx : Output of check_row4datasetname
#     l_model_1_per_row   : List of the models which by default should be plotted just once per row, instead of for each dataset.

#     Return
#     ------
#     models2plot : The only difference is if it the models2plot input there was model with their datasetname attribute to None
#     """
#     # models2plot_user = models2plot if datasetnames4model4row is not None else {}
#     if not isinstance(models2plot, Models2plot):
#         raise ValueError(f"models2plot should be an instance of Models2plot, got {type(models2plot)}.")
#     # Check that all the row mentioned is user input exits
#     if models2plot.nb_rows != len(datasetnames4rowidx):
#         raise ValueError(f"The number of rows in models2plot ({models2plot.nb_rows}) doesn't match the one in datasetnames4rowidx ({len(datasetnames4rowidx)})")
#     # For each row
#     for i_row in range(models2plot.nb_rows):
#         # For each model of each model is datasetname attribute is specified.
#         initial_set_models = models2plot.get_models_2_plot(row_idx=i_row)
#         for name_i, modelspec_i in initial_set_models.items():
#             if modelspec_i.datasetname is None:
#                 modelspec_i.datasetname = datasetnames4rowidx[i_row][0]
#                 if any([model_name_i not in l_model_1_per_row for model_name_i in modelspec_i.add + modelspec_i.remove]):
#                     set_models_of_currentmodel = models2plot.get_model2show(row_idx=i_row, model=model_i.model)
#                     datasetname_4_currentmodel = [model_j.datasetname for model_j in set_models_of_currentmodel]
#                     for datasetname_i in datasetnames4rowidx[i_row][1:]:
#                         if datasetname_i not in datasetname_4_currentmodel:
#                             models2plot.add_model_2_plot(model=model_i.model, row_idx=i_row, datasetname=datasetname_i)
#     return models2plot


# class PlotsDefinitionTS(PlotsDefinition):
#     """Class to specifiy which model to plot in each row of the plot for the TS plots"""

#     def __init__(self, nb_rows: int):
#         """"""
#         super(self.__class__, self).__init__(nb_rows=nb_rows, same4allrows=True, nb_cols=1, same4allcols=True)


# class PlotsDefinitioniTS(PlotsDefinition):
#     """Class to specifiy which model to plot in each row of the plot for the iTS plots"""

#     def __init__(self, l_iterative_models_2_remove: list[Sequence[tuple[str, ModelSpecification]]], plot_removed_in_previousrow: bool=True):
#         """"""
#         # Checking plot_removed_in_previousrow.
#         if not(isinstance(plot_removed_in_previousrow, bool)):
#             raise TypeError(f"plot_removed_in_previousrow should be a bool")
#         # Checking l_iterative_model_2_remove.
#         if not(isinstance(l_iterative_models_2_remove, list)):
#             raise TypeError(f"l_iterative_models_2_remove should be a list, got a {type(l_iterative_models_2_remove)}")
#         super(self.__cls__, self).__init__(nb_rows=len(l_iterative_models_2_remove) + 1, same4allrows=False, nb_cols=1, same4allcols=True)
#         if plot_removed_in_previousrow:
#             for i_row, seq_tuple_name_model_spec in enumerate(l_iterative_models_2_remove):
#                 if not(isinstance(seq_tuple_name_model_spec, Sequence)):
#                     raise TypeError(f"l_iterative_models_2_remove should be a list of sequences. Element {i_row} is a {type(seq_tuple_name_model_spec)}")
#                 for name_i, modelspec_i in seq_tuple_name_model_spec:
#                     self.add_model_2_plot(modelspec=modelspec_i, name=name_i, row_idx=i_row)


# class PlotsDefinitionPF(PlotsDefinition):
#     """Class to specifiy which model to plot in each row of the plot for the TS plots"""

#     def __init__(self, nb_rows: int):
#         """"""
#         super(self.__class__, self).__init__(nb_rows=nb_rows, same4allrows=True, nb_cols=1, same4allcols=True)
    


    


        
