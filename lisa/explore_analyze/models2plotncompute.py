from collections import Sequence
from typing import Dict
from loguru import logger
from numpy.typing import NDArray
from numpy import float_, isfinite, ndarray


class Models2plot(object):
    """Class to specifiy which model to plot in each row of the plot

    If there is several columns in the plot the same models are shown in all columns of the same row
    """

    def __init__(self, nb_rows: int, same4allrows: bool):
        """"""
        self.__nb_rows: int = nb_rows
        self.__same4allrows: bool = same4allrows
        self._models2plot: Dict[int, Sequence[Model2computeNplot]] = {i_row: list() for i_row in range(self.__nb_rows)}

    def __repr__(self):
        return f"{self._models2plot}"

    @property
    def nb_rows(self):
        """numbers of rows in the plot"""
        return self.__nb_rows
    
    property
    def same4allrows(self):
        """numbers of rows in the plot"""
        return self.__same4allrows
    
    def __get_l_row_idx(self, row_idx: int|None) -> Sequence[int]:
        """Return l_row_idx from row_idx argument and produce warning message is needed"""
        if self.__same4allrows:
            if row_idx is not None:
                logger.warning(f"You should not provide row_idx when same4allrows is True. The value that you provided ({row_idx}) was ignored.")
            l_row_ix = list(range(self.nb_rows))
        else:
            if row_idx is None:
                raise ValueError("row_idx should not be None as same4allrows is False")
            if row_idx >= self.nb_rows:
                raise ValueError(f"row_idx={row_idx} is out of range for Show_model with nb_rows={self.nb_rows}")
            l_row_ix = [row_idx, ]
        return l_row_ix

    def add_model_2_plot(self, model: str, row_idx: int|None = None, datasetname: str|None=None, npt: int|None=None, tlims: tuple[float, float]|None=None, pl_kwargs: Dict|None=None):
        """Add model to show for a given row.
        
        Arguments
        ---------
        model   : One model name
        row_idx : If same4allrows is True this should not be provided.
            Otherwise this specifies the row of the plot for which you want to add model to show
        """
        for ii in self.__get_l_row_idx(row_idx=row_idx):
            self._models2plot[ii].append(Model2computeNplot(model=model, datasetname=datasetname, npt=npt, tlims=tlims, pl_kwargs=pl_kwargs))

    def add_models_2_plot(self, models: Sequence[str], row_idx: int|None = None, datasetnames: Sequence[str|None]|None=None, npts: Sequence[int|None]|None=None, tlims: Sequence[tuple[float, float]|None]|None=None, pl_kwargs: Sequence[Dict|None]|None=None):
        """Add multiple models to show for a given row.
        
        Arguments
        ---------
        models  : Several models to show. Be careful that if you provide on model name (a str), instead of a Sequence of model names (Sequence[str]).
            The function will not work.
        row_idx : If same4allrows is True this should not be provided.
            Otherwise this specifies the row of the plot for which you want to add model to show
        """
        if (datasetnames is not None) or not(isinstance(datasetnames, Sequence)) or not(len(datasetnames) == len(models)):
            raise TypeError(f"datasetnames should be None or a Sequence of either Nones or Sequences of datasetnames which should have the same length as models, got {datasetnames} while models is {models}")
        if datasetnames is None:
            datasetnames = [None for model_i in models]
        if (npts is not None) or not(isinstance(npts, Sequence)) or not(len(npts) == len(models)):
            raise TypeError(f"npts should be None or a Sequence of either Nones or strictly positive int which should have the same length as models, got {datasetnames} while models is {models}")
        if npts is None:
            npts = [None for model_i in models]
        if (tlims is not None) or not(isinstance(tlims, Sequence)) or not(len(tlims) == len(models)):
            raise TypeError(f"tlims should be None or a Sequence of either Nones or tuples of 2 floats which should have the same length as models, got {datasetnames} while models is {models}")
        if tlims is None:
            tlims = [None for model_i in models]
        if (pl_kwargs is not None) or not(isinstance(pl_kwargs, Sequence)) or not(len(pl_kwargs) == len(models)):
            raise TypeError(f"pl_kwargs should be None or a Sequence of either Nones or dictionaries which should have the same length as models, got {pl_kwargs} while models is {models}")
        if pl_kwargs is None:
            pl_kwargs = [None for model_i in models]
        for ii in self.__get_l_row_idx(row_idx=row_idx):
            for model_i, datasetname_i, npt_i, tlims_i, pl_kwargs_i in zip([models, datasetnames, npts, tlims, pl_kwargs]):
                self.add_model_2_plot(model=model_i, row_idx=row_idx, datasetname=datasetname_i, npt=npt_i, tlims=tlims_i, pl_kwargs=pl_kwargs_i)
    
    def get_model2show(self, row_idx: int, model: str|None=None) -> set[Model2computeNplot]:
        """Return the list of models to show.
        
        If you only want to return models to show for a given model name, you can specify the model argument.

        Argument
        --------
        row_idx : Specifies the row of the plot for which you want the set of models to show

        Return
        ------
        models  : Set of model names to show for the row
        """
        if row_idx >= self.nb_rows:
            raise ValueError(f"row_idx={row_idx} is out of range for Show_model with nb_rows={self.nb_rows}")
        if model is None:
            return self._models2plot[row_idx]
        else:
            models = set()
            for model_i in self._models2plot[row_idx]:
                if model_i.model == model:
                    models.add(model_i)
            return models


class Models2plotTSNGLSP(Models2plot):
    """Class to specifiy which model to plot in each row of the plot for the TSNGLSP plots"""

    def __init__(self, nb_rows: int):
        """"""
        super(Models2plotTSNGLSP, self).__init__(nb_rows=nb_rows, same4allrows=True)


class Models2plotiTSNGLSP(Models2plot):
    """Class to specifiy which model to plot in each row of the plot for the iTSNGLSP plots"""

    def __init__(self, l_iterative_model_2_remove: list[Sequence[str]], plot_removed_in_previousrow: bool=True):
        """"""
        super(Models2plotiTSNGLSP, self).__init__(nb_rows=len(l_iterative_model_2_remove) + 1, same4allrows=False)
        if plot_removed_in_previousrow:
            for i_row, seq_model in enumerate(l_iterative_model_2_remove):
                for model_i in seq_model:
                    self.add_model_2_plot(model=model_i, row_idx=i_row)


class ComputedModels(object):
    """Class to store and retireve all the computed models.
    
    Each model is stored in the form a Model2computeNplot instance.

    In principle, it would be best if this can be used by all plotting function TSNGLSP, iTSNGLSP, PhaseFolded.

    The use case are the plotting functions TSNGLSP, iTSNGLSP, PhaseFolded
    """
    #TODO: Design and implement this class
    # Could store the Model2computeNplot in dictionaries inside nested dictionaries with the 1st level being tlims, the second, npt, the third datasetname
    # It's proably better to have the first two levels as tlims and npt, as it's sure that one cannot use a model that is not with the right sampling.
    # The lower level dictionaries, that store the Model3computeNplot will have model name as keys. At this level I should have raw extensions
    pass


class Model2computeNplot(object):
    """Class to use inside Models2plot to specify the model to plot 
    """
    __err_msg_model_already_computed = "The model has already been computed, you can no longer modify {}."
    
    def __init__(self, model: str, datasetname: str|None=None, times: NDArray[float_]|None=None, pl_kwargs: Dict|None=None):
        """"""
        self.__model: str = model
        self.__time_values: NDArray[float_]|None = times
        self.__model_values: Dict[float, Dict[int, NDArray[float_]]]|None= None
        self.__model_values_err: Dict[float, Dict[int, NDArray[float_]|None]]|None= None
        self.__datasetname: str|None = None
        if datasetname is not None:
            self.datasetname = datasetname
        self.pl_kwargs = pl_kwargs

    @property
    def model(self):
        """Model name"""
        return self.__model
    
    @property
    def model_stored(self) -> bool:
        """Return True if the model has been computed and stored"""
        return self.__model_values is not None
    
    # @property
    # def npt(self):
    #     """Number of point in the model"""
    #     if self.__time_values is not None:
    #         return len(self.__time_values)
    #     else:
    #         raise ValueError(f"The times for the model are not set, so you cannot get a number of points")
    
    @property
    def datasetname(self):
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
    def tlims(self):
        """Tuple giving the min and max values for the model"""
        if self.__time_values is not None:
            return (min(self.__time_values), max(self.__time_values))
        else:
            raise ValueError(f"The times for the model are not set, so you cannot get the times limits")

    def get_computed_model(self, exptime_bin=0, supersamp=0):
        """Dictionary with two keys 'times', 'values' with the computed time and model values."""
        if not(self.model_stored):
            raise ValueError(f"No model have been stored")
        if exptime_bin not in self.__model_values:
            raise KeyError(f"There is no model stored with exptime_bin={exptime_bin}")
        if supersamp not in self.__model_values[exptime_bin]:
            raise KeyError(f"There is no model stored with supersamp={supersamp} for exptime_bin = {exptime_bin}")
        return {'times': self.__time_values.copy(), 
                'values': self.__model_values[exptime_bin][supersamp].copy(), 
                'values_err': self.__model_values_err[exptime_bin][supersamp].copy() if self.__model_values_err[exptime_bin][supersamp].copy() is not None else None
                }
    
    def set_computed_model(self, times:NDArray[float_], values:NDArray[float_], values_err: NDArray[float_]|None=None, exptime_bin: float=0, supersamp: int=0):
        """Set the computed model (times and values).
        
        If npt and/or t_lims have been set, the times and values arguments will be check against those.
        If they were not set alreay they will be set using the times and values arguments.

        Once a computed model has been set it cannot be overwritten.
        """
        if (self.__time_values is not None) or (self.__model_values is not None):
            raise ValueError("A computed model already exists you cannot overwrite it. Create a new PlotModelDef instance")
        if not(isinstance(times, ndarray)) or not(isinstance(times, ndarray)):
            raise TypeError(f"times and values should be numpy.ndarray, got {type(times)} and {type(values)}")
        if (times.ndim != 1) or (values.ndim != 1) or ((values_err is not None) and (values.ndim != 1)):
            raise ValueError(f"times, values and values_err (if not None) should be ndarray with 1 dimension. The number of dimension of times is {times.ndim}, the one of values is {values.ndim} and {'values_err is None' if values_err is None else f'the one of values_err is {values_err.ndim}'}")
        if (times.size != values.size) or ((values_err is not None) and (times.size != values_err.size)):
            raise ValueError(f"times, values and values_err (if not None) should have the same size. times' size is {times.size}, values' size is {values.size} and {'values_err is None' if values_err is None else f'values_err size is {values_err.size}'}")
        if self.tlims is not None:
            # tlims is already set
            if (self.tlims[0] != times[0]) or (self.tlims[1] != times[-1]):
                raise ValueError(f"The set tlims ({self.tlims}) do not agree with the first and last values of times ({times[0]}, {times[-1]})")
        else:
            self.tlims = (times[0], times[-1])
        if self.npt is not None:
            # npt is already set
            if self.npt != times.size:
                raise ValueError(f"The set npt ({self.npt}) do not agree with the size of times and values ({times.size})")
            else:
                self.npt = times.size
        self.__time_values = times
        if self.__model_values is None:
            self.__model_values = {}
        if not(isinstance(exptime_bin, float)) or (exptime_bin < 0):
            raise ValueError(f"exptime_bin should be a positive (or zero) float, got {exptime_bin}")
        if exptime_bin not in self.__model_values:
            self.__model_values[exptime_bin] = {}
            self.__model_values_err[exptime_bin] = {}
        if not(isinstance(supersamp, int)) or (supersamp < 0):
            raise ValueError(f"supersamp should be a positive (or zero) int, got {supersamp}")
        self.__model_values[exptime_bin][supersamp] = values
        self.__model_values_err[exptime_bin][supersamp] = values_err