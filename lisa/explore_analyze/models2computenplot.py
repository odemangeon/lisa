from __future__ import annotations
from collections import Sequence
from typing import Dict
from loguru import logger
from numpy.typing import NDArray
from numpy import float_, isfinite, ndarray
from numbers import Number
from copy import deepcopy


def get_default_model_name(seq_current_model_name: Sequence[int|str]):
    name = 0
    while name in seq_current_model_name:
        name += 1
    return name


class Models2plot(object):
    """Class to specifiy which model to plot in each row of the plot

    If there is several columns in the plot the same models are shown in all columns of the same row
    """

    def __init__(self, nb_rows: int, same4allrows: bool, nb_cols:int, same4allcols: bool):
        """"""
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
        if (self.nb_rows == 1) and not(same4allrows):
            same4allrows = True
        self.__same4allrows: bool = same4allrows
        if not(isinstance(same4allcols, bool)):
            raise TypeError(f"same4allcols should be a bool, got {same4allcols}")
        if (self.nb_cols == 1) and not(same4allcols):
            same4allcols = True
        self.__same4allcols: bool = same4allcols
        # Init models2plot
        self.__models2plot: Dict[int, Dict[int, list[str|int]]] = {i_row: {i_col: [] for i_col in range(self.nb_cols)} for i_row in range(self.nb_rows)}
        # Init modelspecs
        self.__modelspecs: Dict[str|int, ModelSpecification] = {}
        # Init pl_kwargs
        self.__pl_kwargs: Dict[str|int, Dict[tuple[Number,int]|str, Dict]] = {}

    def __repr__(self):
        return f"{self.__models2plot}"

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
    def name2modelspec(self) -> Dict[str|int, ModelSpecification]:
        """Dictionary providing the conversion from names to model specifications (what the model is composed of in terms of model component added and removed and the dataset used)"""
        return self.__modelspecs.copy()
    
    def __check_idx(self, row_or_col:str, idx: int|None, allow_idx_w_same4all=False) -> tuple[int|None, int, bool]:
        """"""
        if row_or_col not in ['col', 'row']:
            raise ValueError(f"row_or_col should be either 'row' or 'col', you provided {row_or_col}.")
        same4all = self.same4allrows if row_or_col == 'row' else self.same4allcols
        nb = self.nb_rows if row_or_col == 'row' else self.nb_cols
        if (idx is None):
            if nb == 1:
                idx = 0
            else:
                if not(same4all):
                    raise ValueError(f"{row_or_col}_idx should not be None when same4all{row_or_col}s is False.")
        else:
            if same4all and not(allow_idx_w_same4all):
                raise ValueError(f"When same4all{row_or_col}s is True and allow_idx_w_same4all if False, you should not provide a {row_or_col}_idx. You provided {row_or_col}_idx={idx}")
            if not(isinstance(idx, int)):
                raise TypeError(f"{row_or_col}_idx should be an int")
            if idx < 0:
                raise ValueError(f"{row_or_col}_idx should not be negative")
            if idx >= nb:
                raise ValueError(f"{row_or_col}_idx is out of range for nb_{row_or_col}={nb}")
        return idx, nb, same4all
    
    def __get_l_idx(self, row_or_col:str, idx: int|None) -> Sequence[int]:
        """Return l_row_idx from row_idx argument and produce warning message is needed"""
        idx, nb, same4all = self.__check_idx(row_or_col=row_or_col, idx=idx, allow_idx_w_same4all=False)
        if same4all:
            l_idx = list(range(nb))
        else:
            l_idx = [idx, ]
        return l_idx

    def __find_modelspec(self, modelspec: ModelSpecification):
        name_found = None
        for name_i, modelspec_i in self.name2modelspec.items():
            if modelspec == modelspec_i:
                name_found = name_i
                break
        return name_found

    def add_model_2_plot(self, modelspec: ModelSpecification, name: str|int|None, row_idx: int|None = None, col_idx: int|None = None, pl_kwargs:Dict[tuple[Number,int]|str, Dict]|None=None):
        """Add model to show for a given row.
        
        Arguments
        ---------
        modelspec   :
        """
        # Check modelspec
        if not(isinstance(modelspec, ModelSpecification)):
            raise TypeError(f"modelspec should be a ModelSpecification instance, got a {type(modelspec)}")
        # Check row_idx and col_idx:
        # Check if the modelspec already exists
        name_found = self.__find_modelspec(modelspec=modelspec)
        if name_found:
            if name is None:
                name = name_found
            elif name != name_found:
                logger.info(f"The same modelspec with a different name ({name_found}) already exist. The new name provided ({name}) will be ignored")
                name = name_found
        # If check the name
        else:
            if name is None or (name in self.name2modelspec):
                if name in self.name2modelspec:
                    logger.info(f"The name {name} already exists for another model spec and an automatic name will be assigned")
                name = get_default_model_name(seq_current_model_name=self.__modelspecs.keys())
                logger.info(f"name automatically assigned to {name}.")
        # Add the model name to models2 plot
        for i_row in self.__get_l_idx(row_or_col='row', idx=row_idx):
            for i_col in self.__get_l_idx(row_or_col='col', idx=col_idx):
                self.__models2plot[i_row][i_col].append(name)
        # Add the modelspecs to modelspecs
        if name not in self.name2modelspec:
            self.__modelspecs[name] = modelspec
            # Init pl_kwargs for the model
            self.__pl_kwargs[name] = {}
            if pl_kwargs is not None:
                self.update_pl_kwargs(name=name, pl_kwargs_4_name=pl_kwargs)

    def update_pl_kwargs(self, name: str|int, pl_kwargs_4_name: Dict[tuple[Number,int]|str, Dict]):
        """"""
        # Check name
        if name not in self.__pl_kwargs.keys():
            raise ValueError(f"{name} is not the name of an existing modelspec. Existing names are {list(self.name2modelspec.keys())}")
        # Check pl_kwargs
        if not(isinstance(pl_kwargs_4_name, dict)) or any([not(isinstance(tuple_exptimebin_supersamp, tuple) and (isinstance(tuple_exptimebin_supersamp[0], Number)) and (isinstance(tuple_exptimebin_supersamp[1], int))) and
            not(tuple_exptimebin_supersamp == 'default') for tuple_exptimebin_supersamp in pl_kwargs_4_name.keys()]):
            raise TypeError(f"pl_kwargs should be a dict and its keys should be either 'default' or a tuple[Number, int], got {pl_kwargs_4_name}.")
        for tuple_exptimebin_supersamp, pl_kwargs_i in pl_kwargs_4_name.items():
            if not(isinstance(pl_kwargs_i, dict)):
                raise TypeError(f"Value for key {tuple_exptimebin_supersamp} of pl_kwargs_4_name should be a Dict, got a {type(pl_kwargs_i)}")
        # Create the tuple_exptimebin_supersamp if needed and then update
        for tuple_exptimebin_supersamp in pl_kwargs_4_name:
            if tuple_exptimebin_supersamp not in self.__pl_kwargs[name]:
                self.__pl_kwargs[name][tuple_exptimebin_supersamp] = {}
            self.__pl_kwargs[name][tuple_exptimebin_supersamp].update(pl_kwargs_4_name[tuple_exptimebin_supersamp])

    def reset_pl_kwargs(self, name: str|int, tuple_exptimebin_supersamp: tuple[Number,int]|str|None=None):
        # Check name
        if name not in self.__pl_kwargs.keys():
            raise ValueError(f"{name} is not the name of an existing modelspec. Existing names are {list(self.name2modelspec.keys())}")
        # Check tuple_exptimebin_supersamp and pop
        if tuple_exptimebin_supersamp is not None:
            if tuple_exptimebin_supersamp not in self.__pl_kwargs[name]:
                raise KeyError(f"{tuple_exptimebin_supersamp} is not a key of self.__pl_kwargs[{name}], existing keys are {list(self.__pl_kwargs[name].keys())}")
            else:
                self.__pl_kwargs[name].pop(tuple_exptimebin_supersamp)
        else:
            self.__pl_kwargs[name] = {}
    
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

    def get_pl_kwargs(self, name: int|str, tuple_exptimebin_supersamp: tuple[Number, int]|str) -> Dict:
        # Check name
        if name not in self.__pl_kwargs.keys():
            raise KeyError(f"{name} is not the name of an existing modelspec. Existing names are {list(self.name2modelspec.keys())}")
        # Check tuple_exptimebin_supersamp
        # if not(isinstance(tuple_exptimebin_supersamp, tuple) and (isinstance(tuple_exptimebin_supersamp[0], Number)) and (isinstance(tuple_exptimebin_supersamp[1], int))) and
        #     not(tuple_exptimebin_supersamp == 'default'):
        #     raise TypeError(f"tuple_exptimebin_supersamp should be either 'default' or a tuple[Number, int], got {tuple_exptimebin_supersamp}")
        if tuple_exptimebin_supersamp not in self.__pl_kwargs[name].keys():
            raise KeyError(f"{tuple_exptimebin_supersamp} is not available in self.__pl_kwargs[{name}]. Available keys are {self.__pl_kwargs[name].keys()}")
        return self.__pl_kwargs[name][tuple_exptimebin_supersamp]

    # def get_pl_kwargs(self, exptime_bin: Number, supersamp: int) -> Dict:
    #     """Return the dictionary of the kwargs for ploting the specified model"""
    #     if (self.__pl_kwargs is None) or (exptime_bin not in self.__pl_kwargs) or (supersamp not in self.__pl_kwargs[exptime_bin]):
    #         return self.default_pl_kwargs
    #     else:
    #         return self.__pl_kwargs[exptime_bin][supersamp]s
                    

    def add_models_2_plot(self, tuples_name_modelspec: Sequence[tuple[str|int|None, ModelSpecification]], row_idx: int|None = None, col_idx: int|None = None):
        """Add multiple models to show for a given row.
        
        Arguments
        ---------

        """
        if not(isinstance(tuples_name_modelspec, Sequence)) or not(all([isinstance(tuple_name_modelspec_i, tuple) for tuple_name_modelspec_i in tuples_name_modelspec])) or not(all([len(tuple_name_modelspec_i) == 2 for tuple_name_modelspec_i in tuples_name_modelspec])):
            raise TypeError(f"modelspecs should be a Sequence types of 2 elements , got {tuples_name_modelspec}")
        for name_i, modelspec_i in tuples_name_modelspec:
            self.add_model_2_plot(modelspec=modelspec_i, name=name_i, row_idx=row_idx, col_idx=col_idx)
    
    def get_models_2_plot(self, row_idx: int|None=None, col_idx: int|None=None) -> Dict[str|int, ModelSpecification]:
        """Return the list of models to show for a given row index
        
        If you only want to return models to show for a given model name, you can specify the model argument.

        Argument
        --------
        row_idx : Specifies the row of the plot for which you want the set of models to show

        Return
        ------
        models  : Set of model names to show for the row
        """
        # Check row_idx and col_idx
        checked_idx = {}
        for row_or_col, idx in zip(["row", "col"], [row_idx, col_idx]):
            checked_idx[row_or_col], nb, same4all = self.__check_idx(row_or_col=row_or_col, idx=idx, allow_idx_w_same4all=True)
            if checked_idx[row_or_col] is None:
                raise ValueError(f"{row_or_col}_idx should not be None.")
        return {name_i: self.name2modelspec[name_i] for name_i in self.__models2plot[checked_idx['row']][checked_idx['col']]}
    

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


class Models2plotTS(Models2plot):
    """Class to specifiy which model to plot in each row of the plot for the TS plots"""

    def __init__(self, nb_rows: int):
        """"""
        super(self.__class__, self).__init__(nb_rows=nb_rows, same4allrows=True, nb_cols=1, same4allcols=True)


class Models2plotiTS(Models2plot):
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


class ModelSpecification(object):
    """Class that defines the specification for a model computation in terms of components to add and or remove"""

    def __init__(self, datasetname: str|None=None, add: list[str]|str|None=None, remove: list[str]|str|None=None, model2computenplot: Model2computeNplot|None=None):
        """"""
        # Init and Set model2computenplot
        self.__model2computenplot: None|Model2computeNplot = None
        if model2computenplot is not None:
            self.model2computenplot =  model2computenplot
        # Init and set datasetname
        self.__datasetname = None
        self.datasetname = datasetname
        # Init add and remove
        self.__add: list[str] = []
        self.__remove: list[str] = []
        # Check add and remove inputs and store them into self.__add and self.__remove
        for add_or_remove, input in zip(["add", "remove"], [add, remove]):
            self.add_model_components(model_components=input, add_or_remove=add_or_remove)
    
    def __eq__(self, other:ModelSpecification) -> bool:
        """Overrides the default implementation"""
        if isinstance(other, ModelSpecification):
            return (self.__add == other.add) and (self.__remove == other.remove) and (self.datasetname == other.datasetname)
        else:
            return False
    
    def __repr__(self):
        """"""
        return f"{self.__class__.__name__}(datasetname={self.datasetname}, add={self.add}, remove={self.remove}, model2computenplot={self.model2computenplot})"

    @property
    def model2computenplot(self):
        """"""
        return self.__model2computenplot
    
    @model2computenplot.setter
    def model2computenplot(self, new_model2computenplot):
        """"""
        if self.__model2computenplot is not None:
            raise ValueError("model2computenplot has already been set. You cannot change it.")
        if not(isinstance(new_model2computenplot, Model2computeNplot)):
            raise TypeError(f"model2computenplot should a Model2computeNplot instance, got {type(new_model2computenplot)}")
        return self.__model2computenplot

    @property
    def datasetname(self) -> None|str:
        """Name of the dataset to be used to compute the model"""
        return self.__datasetname
    
    @datasetname.setter
    def datasetname(self, new_datasetname: None|str):
        """Name of the dataset to be used to compute the model"""
        if self.model2computenplot is not None:
            if self.model2computenplot.model_stored:
                raise ValueError(f"A model has already been stored. You can no longer change the datasetname")
        if (new_datasetname is not None) and not(isinstance(new_datasetname, str)):
            raise TypeError(f"datasetname should be None or a str")
        self.__datasetname = new_datasetname
    
    @property             
    def add_and_remove(self) -> Dict[str, list[str]]:
        """Return a dictionary with 2 keys, 'add' and 'remove' whose values are lists of str (model component name)"""
        return {'add': self.add, 'remove': self._remove}
    
    @property             
    def add(self) -> list[str]:
        """Return the list of model component name to add"""
        return self.__add.copy()
    
    @property             
    def remove(self) -> list[str]:
        """Return the list of model component name to remove"""
        return self.__remove.copy()
    
    def __check_add_or_remove_input(self, add_or_remove: str):
        """"""
        # Check the add_or_remove
        if add_or_remove not in ['add', 'remove']:
            raise ValueError(f"add_or_remove should be either 'add' or 'remove', got {add_or_remove}")
    
    def __check_model_components(self, model_components: list[str]|str|None, model_components_input_name: str):
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

    def add_model_components(self, model_components: list[str]|str, add_or_remove: str):
        """Add one or several model components to the list of model components to add or remove"""
        self.__check_add_or_remove_input(add_or_remove=add_or_remove)
        model_components = self.__check_model_components(model_components=model_components, model_components_input_name=f'{add_or_remove} model_components')
        if add_or_remove == 'add': 
            self.__add += model_components
        else:
            self.__remove += model_components

    def remove_model_components(self, model_components: list[str]|str, add_or_remove: str):
        """Remove one or several model components to the list of model components to add or remove"""
        self.__check_add_or_remove_input(add_or_remove=add_or_remove)
        model_components = self.__check_model_components(model_components=model_components, model_components_input_name=f'{add_or_remove} model_components')
        for model_component in model_components:
            if add_or_remove == 'add':
                self.__add.remove(model_component)
            else:
                self.__remove.remove(model_component)

    def __eq__(self, other: ModelSpecification) -> bool:
        """Overrides the default implementation"""
        if isinstance(other, ModelSpecification):
            return (self.add == other.add) and (self.remove == other.remove) and (self.datasetname == other.datasetname)
        else:
            return False
    

class Model2computeNplot(object):
    """Class to use inside Models2plot to specify the model to plot 
    """
    __err_msg_model_already_computed = "The model has already been computed, you can no longer modify {}."
    
    def __init__(self, modelspec: ModelSpecification):
        """"""
        # Check modelspec and set modelspec
        if not(isinstance(modelspec, ModelSpecification)):
            raise ValueError(f"modelspec should be a ModelSpecification instance, got {type(ModelSpecification)}")
        self.__modelspec: ModelSpecification = modelspec
        # Set the model2computenplot attribute on modelspec
        self.__modelspec.model2computenplot = self
        # Init the times, model and model_err values
        self.__time_values: Dict[tuple[Number, int], list[NDArray[float_]]] = {}
        self.__model_values: Dict[tuple[Number, int], list[NDArray[float_]]] = {}
        self.__model_values_err: Dict[tuple[Number, int], list[NDArray[float_]]] = {}
        
    @property
    def modelspec(self) -> ModelSpecification:
        """Model name"""
        return self.__modelspec
    
    @property
    def model_stored(self) -> bool:
        """Return True if the model has been computed and stored"""
        return len(self.__time_values) > 0
    
    @property
    def datasetname(self) -> str:
        """Model name"""
        return self.__datasetname
    
    @datasetname.setter
    def datasetname(self, new_datasetname: str):
        """Dataset name for to used for the model (not in terms of time samples but in terms of model)"""
        if self.model_stored:
            raise ValueError(self.__err_msg_model_already_computed.format("datasetname"))
        if not(isinstance(new_datasetname, str)):
            raise ValueError(f"datasetnames should be a str (dataset names), got {new_datasetname}")
        self.__datasetname = new_datasetname

    @property
    def computed_exptime_supersamp(self) -> set[tuple[Number, int]]:
        """"""
        return set(self.__times_values.keys())

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


class Database_Model2computeNplot(object):
    """Database to store the Model2computeNplot model and access them easily
    """

    def __init__(self, tuples_name_model2computenplot: Sequence[tuple[str|int|None, Model2computeNplot]]|None=None, overwrite=False):
        """"""
        # Init models2computenplot
        self.__models2computenplot: Dict[str|int, Model2computeNplot] = {}
        # Add models2computenplot to the database
        self.add_models2computenplot(tuples_name_model2computenplot=tuples_name_model2computenplot, overwrite=overwrite)

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

    def add_model2computenplot(self, model2computenplot: Model2computeNplot, name: None|int|str=None, overwrite=False):
        """"""
        # Check the type of model2computenplot
        if not(isinstance(model2computenplot, Model2computeNplot)):
            raise TypeError(f"model2computenplot should be a Model2computeNplot instance, got a {type(model2computenplot)}")
        # Check the type of name
        if name is None:
            name = 0
            while name in self.__models2computenplot:
                name += 1
        if not(isinstance(name, int)) and not(isinstance(name, str)):
            raise TypeError(f"name should be either an int, a str or None, got {name}")
        # Check if a model2computenplot with the same ModelSpecification already exists
        name_found = self.__find_modelspec(modelspec=model2computenplot.modelspec)
        if name_found:
            if overwrite:
                logger.warning(f"A Model2computeNplot instance with the same ModelSpecification and name {name_found} was found in the Database_Model2computeNplot. It will be replaced by a the provided model2computenplot with name {name}")
                if name_found != name:
                    self.__models2computenplot.pop(name_found)
        self.__models2computenplot[name] = model2computenplot

    def add_models2computenplot(self, tuples_name_model2computenplot: Sequence[tuple[str|int|None, Model2computeNplot]], overwrite=False):
        """"""
        for name, model2computenplot in tuples_name_model2computenplot:
            self.add_model2computenplot(name=name, model2computenplot=model2computenplot, overwrite=overwrite)

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
        
