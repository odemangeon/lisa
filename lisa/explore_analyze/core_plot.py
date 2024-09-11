from __future__ import annotations
from collections import Sequence
from typing import Dict
from loguru import logger
from numpy.typing import NDArray
from numpy import float_, isfinite, ndarray, equal
from numbers import Number
from copy import deepcopy, copy
import re



def get_default_model_name(seq_current_model_name: Sequence[int|str]):
    name = 0
    while name in seq_current_model_name:
        name += 1
    return name


class ModelBinning(object):
    """Class to set the parameters for the binning of a model
    
    It is define by an exposure time and a supersampling factor
    """

    def __init__(self, exptime:Number|None=None, supersampling:int|None=None):
        if exptime is None:
            exptime = 0
        if supersampling is None:
            supersampling = 1
        self.__set_binning(exptime=exptime, supersampling=supersampling)

    @property
    def exptime(self) -> Number:
        return self.__exptime

    @property
    def supersampling(self) -> int:
        return self.__supersampling

    def __set_binning(self, exptime: Number, supersampling:int):
        if not(exptime >= 0):
            raise ValueError(f"exptime should be a number superior or equal to 0")
        if not(supersampling >= 1) or not(isinstance(supersampling, int)):
            raise ValueError(f"supersampling should be an int superior or equal to 1")
        if (equal(exptime, 0) and not(equal(supersampling, 1))):
            raise ValueError(f"if supersampling is > 1 then exptime should not be 0.")
        self.__exptime = exptime
        self.__supersampling = int(supersampling)


class ModelExpression(object):
    """Class that defines the expression of the model to plot in terms of basic operations and base components
    """
    
    def __init__(self, expression:str):
        if not(isinstance(expression, str)):
            raise TypeError(f"expression should be a string with the expression to be used to compute the model")
        self.__expression = expression
        self.__terms = []
        
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

    def __eq__(self, other: object) -> bool:
        """Overrides the default implementation"""
        if isinstance(other, ModelExpression):
            return self.expression == other.expression
        else:
            return False

# class ModelDescription(object):
#     """Class that defines the components of a model in terms of base model components to add and or remove
#     """

#     def __init__(self, description:str):
#         """"""
        
#         # Init add and remove
#         self.__add: list[str] = []
#         self.__remove: list[str] = []
#         # Check add and remove inputs and store them into self.__add and self.__remove
#         for add_or_remove, input in zip(["add", "remove"], [add, remove]):
#             self.add_model_components(model_components=input, add_or_remove=add_or_remove)
    
#     def __eq__(self, other:ModelSpecification) -> bool:
#         """Overrides the default implementation"""
#         if isinstance(other, ModelSpecification):
#             return (self.__add == other.add) and (self.__remove == other.remove) and (self.datasetname == other.datasetname)
#         else:
#             return False
    
#     def __repr__(self):
#         """"""
#         return f"{self.__class__.__name__}(datasetname={self.datasetname}, add={self.add}, remove={self.remove}, model2computenplot={self.model2computenplot})"

#     @property
#     def model2computenplot(self):
#         """"""
#         return self.__model2computenplot
    
#     @model2computenplot.setter
#     def model2computenplot(self, new_model2computenplot):
#         """"""
#         if self.__model2computenplot is not None:
#             raise ValueError("model2computenplot has already been set. You cannot change it.")
#         if not(isinstance(new_model2computenplot, Model2computeNplot)):
#             raise TypeError(f"model2computenplot should a Model2computeNplot instance, got {type(new_model2computenplot)}")
#         return self.__model2computenplot

#     @property
#     def datasetname(self) -> None|str:
#         """Name of the dataset to be used to compute the model"""
#         return self.__datasetname
    
#     @datasetname.setter
#     def datasetname(self, new_datasetname: None|str):
#         """Name of the dataset to be used to compute the model"""
#         if self.model2computenplot is not None:
#             if self.model2computenplot.model_stored:
#                 raise ValueError(f"A model has already been stored. You can no longer change the datasetname")
#         if (new_datasetname is not None) and not(isinstance(new_datasetname, str)):
#             raise TypeError(f"datasetname should be None or a str")
#         self.__datasetname = new_datasetname
    
#     @property             
#     def add_and_remove(self) -> Dict[str, list[str]]:
#         """Return a dictionary with 2 keys, 'add' and 'remove' whose values are lists of str (model component name)"""
#         return {'add': self.add, 'remove': self.remove}
    
#     @property             
#     def add(self) -> list[str]:
#         """Return the list of model component name to add"""
#         return self.__add.copy()
    
#     @property             
#     def remove(self) -> list[str]:
#         """Return the list of model component name to remove"""
#         return self.__remove.copy()
    
#     def __check_add_or_remove_input(self, add_or_remove: str):
#         """"""
#         # Check the add_or_remove
#         if add_or_remove not in ['add', 'remove']:
#             raise ValueError(f"add_or_remove should be either 'add' or 'remove', got {add_or_remove}")
    
#     def __check_model_components(self, model_components: list[str]|str|None, model_components_input_name: str) -> list[str]:
#         """"""
#         if model_components is None:
#             checked_model_components: list[str] = []
#         else:
#             if isinstance(model_components, str):
#                 checked_model_components = [model_components]
#             elif isinstance(model_components, list) and all([isinstance(model_component, str) for model_component in model_components]):
#                 checked_model_components = model_components.copy()
#             else:
#                 raise ValueError(f"{model_components_input_name} should be either None, or a str (model component name) or a list of strs (list of model component names), got {model_components}")
#         return checked_model_components

#     def add_model_components(self, model_components: list[str]|str, add_or_remove: str):
#         """Add one or several model components to the list of model components to add or remove"""
#         self.__check_add_or_remove_input(add_or_remove=add_or_remove)
#         model_components = self.__check_model_components(model_components=model_components, model_components_input_name=f'{add_or_remove} model_components')
#         if add_or_remove == 'add': 
#             self.__add += model_components
#         else:
#             self.__remove += model_components

#     def remove_model_components(self, model_components: list[str]|str, add_or_remove: str):
#         """Remove one or several model components to the list of model components to add or remove"""
#         self.__check_add_or_remove_input(add_or_remove=add_or_remove)
#         model_components = self.__check_model_components(model_components=model_components, model_components_input_name=f'{add_or_remove} model_components')
#         for model_component in model_components:
#             if add_or_remove == 'add':
#                 self.__add.remove(model_component)
#             else:
#                 self.__remove.remove(model_component)

#     def __eq__(self, other: object) -> bool:
#         """Overrides the default implementation"""
#         if isinstance(other, ModelSpecification):
#             return (self.add == other.add) and (self.remove == other.remove) and (self.datasetname == other.datasetname)
#         else:
#             return False


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
    
    def __init__(self, expression:str, times:NDArray[float_]|None=None, exptime:Number|None=None, supersampling:int|None=None, 
                 datasetname:str|None=None, pl_kwargs:Dict|None=None):
        self.__expression:ModelExpression = ModelExpression(expression=expression)
        self.__times:NDArray[float_]|None = None
        if times is not None:
            self.set_times(times=times)
        self.__binning:ModelBinning = ModelBinning(exptime=exptime, supersampling=supersampling)
        self.__datasetname:str|None = None
        if datasetname is not None:
            self.set_datasetname(datasetname=datasetname)
        self.__pl_kwargs: Dict = {}
        if pl_kwargs is not None:
            if not(isinstance(pl_kwargs, dict)):
                raise TypeError(f"pl_kwargs should be a dict or None, got {type(pl_kwargs)}")
            else:
                self.pl_kwargs.update(pl_kwargs)


    @property
    def expression(self) -> ModelExpression:
        # Return a list of unique terms (removing duplicates)
        return self.__expression

    @property
    def times(self) -> NDArray[float_]|None:
        return copy(self.__times)
    
    def set_times(self, times:NDArray[float_]):
        if not(isinstance(times, ndarray)):
            raise TypeError(f"times should be numpy.ndarray of float, got {type(times)}.")
        self.__times = copy(times)

    @property
    def binning(self) -> ModelBinning:
        return self.__binning
    
    @property
    def exptime(self) -> Number:
        return self.__binning.exptime
    
    @property
    def supersampling(self) -> int:
        return self.__binning.supersampling

    def set_binning(self, exptime:Number, supersampling:int):
        self.__binning = ModelBinning(exptime=exptime, supersampling=supersampling)

    @property
    def datasetname(self) -> str|None:
        return self.__datasetname

    def set_datasetname(self, datasetname:str):
        if not(isinstance(datasetname, str)):
            raise TypeError(f"datasetname be a string, got {type(datasetname)}.")
        self.__datasetname = datasetname

    @property
    def pl_kwargs(self) -> Dict:
        return self.__pl_kwargs
   
class ComputedModel(object):
    """Class to store computed models values: expression, binning, datasetname, times, values, errors
    """
    def __init__(self, expression:str, datasetname:str, exptime:Number, supersampling:int,
                 times:NDArray[float_], values:NDArray[float_], errors:NDArray[float_]):
        self.__expression:ModelExpression = ModelExpression(expression=expression)
        self.__set_datasetname(datasetname=datasetname)
        self.__binning:ModelBinning = ModelBinning(exptime=exptime, supersampling=supersampling)
        self.__set_computed_model(times=times, values=values, errors=errors)

    @property
    def expression(self) -> ModelExpression:
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
    def exptime(self) -> Number:
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

    def find_computed_model(self, expression:str, datasetname:str, exptime:Number, supersampling:int,
                            times:NDArray[float_]) -> tuple[ComputedModel|None, int|None, NDArray[float_]|None]:
        model_found:ComputedModel|None = None
        times_found:NDArray[float_]|None = None
        i_model_found:list[int] = []
        for ii, computed_model in enumerate(self.stored_models):
            if all(computed_model.times == times):
                times_found = computed_model.times
            if ((computed_model.expression == expression) and 
                (computed_model.datasetname == datasetname) and 
                (computed_model.binning == ModelBinning(exptime=exptime, supersampling=supersampling)) and
                all(computed_model.times == times)
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
    
    def store_computed_model(self, expression:str, datasetname:str, exptime:Number, supersampling:int,
                             times:NDArray[float_], values:NDArray[float_], errors:NDArray[float_],
                             overwrite: bool=False):
        """Set the computed model (times and values).
        
        If npt and/or t_lims have been set, the times and values arguments will be check against those.
        If they were not set alreay they will be set using the times and values arguments.

        Once a computed model has been set it cannot be overwritten.
        """
        model_found, _, times_found = self.find_computed_model(expression=expression, datasetname=datasetname, exptime=exptime, supersampling=supersampling,
                                                               times=times)
        if not((model_found is not None) and not(overwrite)):
            if (model_found is not None) and overwrite:
                logger.info("Such model is already in the database, but it will be overwritten.")
            if times_found is not None:
                times = times_found
            self.stored_models.append(ComputedModel(expression=expression, datasetname=datasetname, exptime=exptime, supersampling=supersampling,
                                                           times=times, values=values, errors=errors))
        else:
           logger.warning("Such model is already in the database and overwrite is False. The store command will be ignored.")


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
    """Class to specifiy which models to plot in which axis of figure that contains of a subplots grid with N rows and M columns.

    At creation you can specify the number of rows and columns of the grid and if you want the same models
    to be plots in all rows or in all columns.

    For each plot in the grid this class allows to define which model(s) to plot and the way to plot them (pl_kwargs).
    You can also want to plot different sampling and or binning 

    Internally this information is stored in 3 class attribute:
    - models2plot: a dictionary of dictionary that contains the list of "names" of the models to be plotted for each row and each columns.
    - modelspecs: a dictionary of ModelSpecification which the class that defines how to compute a model. The keys in this dictionary are 
        the "names" of the models used in models2plot
    - pl_kwargs: ??
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
        self.__grid:tuple[tuple[list[str|int], ...], ...] = tuple([tuple([[] for _ in range(nb_cols)]) for _ in range(nb_rows)])
        # Init models2plot_database
        self.__models: Dict[str|int, Model2plot] = {}

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
    def grid(self) -> tuple[tuple[list[str|int], ...], ...]:
        """Grid (in the form of a tuple of tuple) with the list of what to plot in each element of the grid"""
        return deepcopy(self.__grid)

    @property
    def models(self) -> Dict[str|int, Model2plot]:
        """Dictionary providing the conversion from names to Model2plot instance"""
        return self.__models.copy()
    
    # def __check_idx(self, row_or_col:str, idx: int|None, allow_idx_w_same4all=False) -> tuple[int|None, int, bool]:
    #     """"""
    #     if row_or_col not in ['col', 'row']:
    #         raise ValueError(f"row_or_col should be either 'row' or 'col', you provided {row_or_col}.")
    #     same4all = self.same4allrows if row_or_col == 'row' else self.same4allcols
    #     nb = self.nb_rows if row_or_col == 'row' else self.nb_cols
    #     if (idx is None):
    #         if nb == 1:
    #             idx = 0
    #         else:
    #             if not(same4all):
    #                 raise ValueError(f"{row_or_col}_idx should not be None when same4all{row_or_col}s is False.")
    #     else:
    #         if same4all and not(allow_idx_w_same4all):
    #             raise ValueError(f"When same4all{row_or_col}s is True and allow_idx_w_same4all if False, you should not provide a {row_or_col}_idx. You provided {row_or_col}_idx={idx}")
    #         if not(isinstance(idx, int)):
    #             raise TypeError(f"{row_or_col}_idx should be an int")
    #         if idx < 0:
    #             raise ValueError(f"{row_or_col}_idx should not be negative")
    #         if idx >= nb:
    #             raise ValueError(f"{row_or_col}_idx is out of range for nb_{row_or_col}={nb}")
    #     return idx, nb, same4all
    
    def __get_l_i(self, idx, roworcol):
        """Return a list of idx depending on idx and colorrow"""
        if roworcol == 'row':
            size = len(self.grid)
        elif roworcol == 'col':
            size = len(self.grid[0])
        else:
            raise ValueError(f"roworcol should be in ['col', 'row'], got {colorrow}")
        # If you don't provide i_row it means that you want to add to all rows
        if idx is None:
            l_idx = range(size)
        else:
            l_idx = [idx, ]
        return l_idx

    # def __find_modelspec(self, modelspec: ModelSpecification):
    #     name_found = None
    #     for name_i, modelspec_i in self.name2modelspec.items():
    #         if modelspec == modelspec_i:
    #             name_found = name_i
    #             break
    #     return name_found

    def addexistingtogrid(self, i_row:int|None=None, i_col:int|None=None, name:str):
        """Add a model that is already in the models2plot in the grid."""
        # Check that name is in models
        if not(name in self.models):
            raise ValueError(f"There is no model2plot with name {name}.")
        # Make sure that i_row and i_col are correct
        if i_row is None:
            if self.same4allrows:
                i_row = 0
            else:
                raise ValueError("You need to provide i_row (as same4allrows is False)")
        else:
            if self.same4allrows and (i_row != 0):
                raise ValueError("same4allrows is True, so you don't need to provide i_row. If you do it must be 0.")
        if i_col is None:
            if self.same4allcols:
                i_col = 0
            else:
                raise ValueError("You need to provide i_col (as same4allcols is False)")
        else:
            if self.same4allcols and (i_col != 0):
                raise ValueError("same4allcols is True, so you don't need to provide i_col. If you do it must be 0.")
        # Add the name to the grid
        self.grid[i_row][i_col].append(name)

    def removefromgrid(self, i_row:int, i_col:int, name:str):
        """Remove a model from the grid"""
        self.grid[i_row][i_col].remove(name)
        
    def addtomodels(self, expression:str, name:str|None=None, overwrite:bool=False, **kwargs_model2plot):
        """Add a model to plot in the grid.

        This function can work 
        
        Arguments
        ---------
        modelspec   :
        """
        # Check if name already exists
        if (name is not None) and (name in self.models) and not(overwrite):
            raise ValueError(f"There is already a model2plot with this name ({name}). Please choose another name")
        elif (name is not None) and (name in self.models) and not(overwrite):
            logger.info(f"There is already a model2plot with this name ({name}). It will be overwritten")
        elif name is None:
            basename = expression
            if ('datasetname' in kwargs_model2plot) and (kwargs_model2plot['datasetname'])
                basename += f"_{kwargs_model2plot['datasetname']}" 
            ii = 0
            name = f"{basename}"
            while name in self.models:
                ii += 1
                name = f"{basename}_{ii}"
        # Add Model2plot instance to models
        self.models[name] = Model2plot(expression=expression, **kwargs_model2plot)
        return name
    
    def getmodel(self, name:str) -> Model2plot|None:
        """Get a Model2plot from models"""
        # Check that name is in models
        if not(name in self.models):
            raise ValueError(f"There is no model2plot with name {name}.")
        return self.models[name]
    
    def addtogrid(self, i_row:int|None=None, i_col:int|None=None, name:str|None=None, expression:str|None=None, overwrite:bool=False, **kwargs_model2plot):
        """Add a model that is already in the grid.
        
        This function is a wrapper around addtogrid and addtomodels for the user convenience.
        There is two use cases:
        1. Adding a model which already exists in models to the grid (exactly like addexistingtogrid)
        2. Adding a model to models and to grid in one function call
        """
        # If you don't provide i_row it means that you want to add to all rows
        l_i_rows = self.__get_l_i(idx=i_row, roworcol='row')
        l_i_cols = self.__get_l_i(idx=i_col, roworcol='col')
        # Add
        if (name is not None) and (expression is None):  # Use case 1
            for i_row in l_i_rows:
                for i_col in l_i_cols:
                    self.addexistingtogrid(i_row=i_row, i_col=i_col, name=name)
        else:  # Use case 2
            name = self.addtomodels(expression=expression, name=name, overwrite=overwrite, **kwargs_model2plot)
            for i_row in l_i_rows:
                for i_col in l_i_cols:
                    self.addexistingtogrid(i_row=i_row, i_col=i_col, name=name)

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
                    raise TypeError(f"name should be either None, or a str or a list of str")
                for name in l_name:
                    if name not in self.grid[i_row][i_col]:
                        logger.info(f"No model with name {name} in the grid at row {i_row} and col {i_col}")
                    else:
                        model2plot = self.getmodel(name=name)
                    if model2plot.datasetname is None:
                        model2plot.set_datasetname(datasetname=datasetname)
                    else:
                        logger.info(f"model2plot {name} (found in the grid at row {i_row} and col {i_col}) already as a datasetname ({model2plot.datasetname}) it will not be changed")
                        

        
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
    

def check_Models2plot(models2plot: Models2plot|None, datasetnames4rowidx: Sequence[Sequence[str]], l_model_1_per_row: Sequence[str]) -> Models2plot:
    """

    Arguments
    ---------
    datasetnames4rowidx : Output of check_row4datasetname
    l_model_1_per_row   : List of the models which by default should be plotted just once per row, instead of for each dataset.

    Return
    ------
    models2plot : The only difference is if it the models2plot input there was model with their datasetname attribute to None
    """
    # models2plot_user = models2plot if datasetnames4model4row is not None else {}
    if not isinstance(models2plot, Models2plot):
        raise ValueError(f"models2plot should be an instance of Models2plot, got {type(models2plot)}.")
    # Check that all the row mentioned is user input exits
    if models2plot.nb_rows != len(datasetnames4rowidx):
        raise ValueError(f"The number of rows in models2plot ({models2plot.nb_rows}) doesn't match the one in datasetnames4rowidx ({len(datasetnames4rowidx)})")
    # For each row
    for i_row in range(models2plot.nb_rows):
        # For each model of each model is datasetname attribute is specified.
        initial_set_models = models2plot.get_models_2_plot(row_idx=i_row)
        for name_i, modelspec_i in initial_set_models.items():
            if modelspec_i.datasetname is None:
                modelspec_i.datasetname = datasetnames4rowidx[i_row][0]
                if any([model_name_i not in l_model_1_per_row for model_name_i in modelspec_i.add + modelspec_i.remove]):
                    set_models_of_currentmodel = models2plot.get_model2show(row_idx=i_row, model=model_i.model)
                    datasetname_4_currentmodel = [model_j.datasetname for model_j in set_models_of_currentmodel]
                    for datasetname_i in datasetnames4rowidx[i_row][1:]:
                        if datasetname_i not in datasetname_4_currentmodel:
                            models2plot.add_model_2_plot(model=model_i.model, row_idx=i_row, datasetname=datasetname_i)
    return models2plot


class PlotsDefinitionTS(PlotsDefinition):
    """Class to specifiy which model to plot in each row of the plot for the TS plots"""

    def __init__(self, nb_rows: int):
        """"""
        super(self.__class__, self).__init__(nb_rows=nb_rows, same4allrows=True, nb_cols=1, same4allcols=True)


class PlotsDefinitioniTS(PlotsDefinition):
    """Class to specifiy which model to plot in each row of the plot for the iTS plots"""

    def __init__(self, l_iterative_models_2_remove: list[Sequence[tuple[str, ModelSpecification]]], plot_removed_in_previousrow: bool=True):
        """"""
        # Checking plot_removed_in_previousrow.
        if not(isinstance(plot_removed_in_previousrow, bool)):
            raise TypeError(f"plot_removed_in_previousrow should be a bool")
        # Checking l_iterative_model_2_remove.
        if not(isinstance(l_iterative_models_2_remove, list)):
            raise TypeError(f"l_iterative_models_2_remove should be a list, got a {type(l_iterative_models_2_remove)}")
        super(self.__cls__, self).__init__(nb_rows=len(l_iterative_models_2_remove) + 1, same4allrows=False, nb_cols=1, same4allcols=True)
        if plot_removed_in_previousrow:
            for i_row, seq_tuple_name_model_spec in enumerate(l_iterative_models_2_remove):
                if not(isinstance(seq_tuple_name_model_spec, Sequence)):
                    raise TypeError(f"l_iterative_models_2_remove should be a list of sequences. Element {i_row} is a {type(seq_tuple_name_model_spec)}")
                for name_i, modelspec_i in seq_tuple_name_model_spec:
                    self.add_model_2_plot(modelspec=modelspec_i, name=name_i, row_idx=i_row)


class PlotsDefinitionPF(PlotsDefinition):
    """Class to specifiy which model to plot in each row of the plot for the TS plots"""

    def __init__(self, nb_rows: int):
        """"""
        super(self.__class__, self).__init__(nb_rows=nb_rows, same4allrows=True, nb_cols=1, same4allcols=True)
    


    


        
