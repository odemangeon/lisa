from __future__ import annotations

import re
from collections import OrderedDict
from collections.abc import Iterable, Sequence
from copy import copy, deepcopy
from numbers import Number
from pprint import pprint

from loguru import logger
from numpy import array_equal, equal, linspace, ndarray
from numpy.typing import NDArray
from pandas import DataFrame

from ..posterior.core.posterior import Posterior


def get_default_model_name(seq_current_model_name: Sequence[int | str]):
    name = 0
    while name in seq_current_model_name:
        name += 1
    return name


def plot_data_and_resi(
    x: NDArray,
    data: NDArray,
    data_err: NDArray,
    data_err_jitter: NDArray,
    residuals: NDArray,
    dataormulitdata2plot: Data2Plot | MultiData2Plot,
    axe_data: Axe,
    axe_resi: Axe | None,
):
    pl_kwarg = copy(dataormulitdata2plot.pl_kwargs)
    show_error = pl_kwarg.get("show_error", True)
    if "show_error" in pl_kwarg:
        pl_kwarg.pop("show_error")
    if not (show_error) or (data_err is None):
        ebcont = axe_data.errorbar(x, y=data, **pl_kwarg)
        if "color" not in pl_kwarg:
            pl_kwarg["color"] = ebcont[0].get_color()
        ebcont = axe_resi.errorbar(x, y=residuals, **pl_kwarg)
    else:
        ebcont = axe_data.errorbar(x, y=data, yerr=data_err, **pl_kwarg)
        if "color" not in pl_kwarg:
            pl_kwarg["color"] = ebcont[0].get_color()
        ebcont = axe_resi.errorbar(x, y=residuals, yerr=data_err, **pl_kwarg)
    color = ebcont[0].get_color()
    alpha = ebcont[0].get_alpha()
    if "color" not in pl_kwarg:
        pl_kwarg["color"] = color
    if "alpha" not in pl_kwarg:
        pl_kwarg["alpha"] = alpha
    if pl_kwarg["alpha"] is None:
        pl_kwarg["alpha"] = 1
    if not (not (show_error) or (data_err_jitter is None)):
        pl_kwarg["alpha"] /= 3
        if "label" in pl_kwarg:
            label = pl_kwarg.pop("label")
        _ = axe_data.errorbar(x, y=data, yerr=data_err_jitter, **pl_kwarg)
        _ = axe_resi.errorbar(x, y=residuals, yerr=data_err_jitter, **pl_kwarg)
        pl_kwarg["alpha"] *= 3
    return pl_kwarg


class DataBinning:
    """Class to set the parameters for the binning

    It defines the exposure time and the binning method
    """

    def __init__(self, exptime: float | int | None = None, method: str | None = None):
        exptime = self._default_exptime(exptime=exptime)
        self._set_exptime(exptime=exptime)
        method = self._default_method(method=method)
        self._set_method(method=method)

    @property
    def exptime(self) -> float | int:
        return self.__exptime

    def _default_exptime(self, exptime: float | int | None = None) -> float | int:
        if exptime is None:
            exptime = 0
        return exptime

    def _set_exptime(self, exptime: float | int):
        if not (exptime >= 0):
            raise ValueError("exptime should be a number superior or equal to 0")
        self.__exptime = exptime

    @property
    def method(self) -> str:
        return self.__method

    def _default_method(self, method: str | None = None) -> str:
        if method is None:
            method = "mean"
        return method

    def _set_method(self, method: str):
        if not (isinstance(method, str)):
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

    def __init__(self, exptime: float | int | None = None, supersampling: int | None = None):
        exptime = self._default_exptime(exptime=exptime)
        self._set_exptime(exptime=exptime)
        supersampling = self._default_supersampling(supersampling=supersampling)
        self._set_supersampling(exptime=self.exptime, supersampling=supersampling)

    @property
    def supersampling(self) -> int:
        return self.__supersampling

    def _default_supersampling(self, supersampling: int | None) -> int:
        if supersampling is None:
            supersampling = 1
        return supersampling

    def _set_supersampling(self, exptime: float | int, supersampling: int):
        if not (exptime >= 0):
            raise ValueError("exptime should be a number superior or equal to 0")
        if not (supersampling >= 1) or not (isinstance(supersampling, int)):
            raise ValueError("supersampling should be an int superior or equal to 1")
        if ((exptime > 0.0) and equal(supersampling, 1)) or (
            (supersampling > 1) and equal(exptime, 0)
        ):
            raise ValueError("if supersampling is > 1 then exptime should not be 0 and vice versa.")
        self.__supersampling = int(supersampling)

    def __eq__(self, other: object) -> bool:
        """Overrides the default implementation"""
        if isinstance(other, ModelBinning):
            return (self.exptime == other.exptime) and (self.supersampling == other.supersampling)
        else:
            return False


class Expression:
    """Class that defines the expression of the model or data to plot in terms of basic operations and base components"""

    def __init__(self, expression: str):
        if not (isinstance(expression, str)):
            raise TypeError(
                "expression should be a string with the expression to be used to compute the model"
            )
        self.__expression = expression
        self.__terms: list[str] = []

        self._parse_expression()

    def _parse_expression(self):
        # Extract terms using regular expressions (assume terms are variables with letters/numbers/underscores)
        self.__terms = re.findall(r"[a-zA-Z_]\w*", self.expression)

        # Extract operations (for now we consider only +, -, *, /, parentheses are ignored)
        self.__operations = re.findall(r"[+\-*/]", self.expression)

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


class Pl_factors:
    def __init__(self, time_factor: float | None = None, value_factor: float | None = None):
        self.__time_factor: float = 1.0
        if time_factor is not None:
            self.time_factor = time_factor
        self.__value_factor: float = 1.0
        if value_factor is not None:
            self.value_factor = value_factor

    @property
    def time_factor(self) -> float:
        return self.__time_factor

    @time_factor.setter
    def time_factor(self, new_time_factor: float):
        if not (isinstance(new_time_factor, float)):
            raise TypeError(f"new_time_factor should be a float. Got {type(new_time_factor)}")
        self.__time_factor = new_time_factor

    @property
    def value_factor(self) -> float:
        return self.__value_factor

    @value_factor.setter
    def value_factor(self, new_value_factor: float):
        if not (isinstance(new_value_factor, float)):
            raise TypeError(f"new_value_factor should be a float. Got {type(new_value_factor)}")
        self.__value_factor = new_value_factor


class Model2plot:
    """Class to specify a model to plot

    A model to plot is defined by
    - its components (base components to add or remove)
    - its datasetname
    - its time vector at which the model is evaluated
    - its exposure time
    - its supersampling factor
    - its plot kwargs
    """

    def __init__(
        self,
        expression: str,
        times: NDArray[float] | None = None,
        time_limits: tuple[float, float] | None = None,
        npt: int | None = None,
        exptime: float | int | None = None,
        supersampling: int | None = None,
        datasetname: str | None = None,
        time_factor: float | None = None,
        value_factor: float | None = None,
        pl_kwargs: dict | None = None,
        pl_kwargs_error: dict | None = None,
        show_error: bool = True,
        df_param_value: DataFrame | None = None,
    ):
        self._init_expression(expression=expression)
        self._check_expression_4_data(expression=self.expression)
        self.__times: NDArray[float] | None = None
        if times is not None:
            self.set_times(times=times)
        self.__time_limits: tuple[float, float] | None = None
        if time_limits is not None:
            self.set_time_limits(time_limits=time_limits)
        self.__npt: int | None = None
        if npt is not None:
            self.set_npt(npt=npt)
        self._init_ModelBinning(exptime=exptime, supersampling=supersampling)
        self._init_datasetname(datasetname=datasetname)
        self._init_pl_factors(time_factor=time_factor, value_factor=value_factor)
        self._init_pl_kwargs(pl_kwargs=pl_kwargs)
        self._init_pl_kwargs_err(pl_kwargs_error=pl_kwargs_error)
        self._init_df_param_value(df_param_value=df_param_value)
        self.show_error = show_error

    @property
    def expression(self) -> Expression:
        # Return a list of unique terms (removing duplicates)
        return self.__expression

    def _init_expression(self, expression: str):
        self.__expression = Expression(expression=expression)

    def _check_expression_4_data(self, expression: Expression):
        if "data" in expression.components:
            raise ValueError("expression cannot involve data")

    @property
    def times(self) -> NDArray[float] | None:
        return copy(self.__times)

    def set_times(self, times: NDArray[float]):
        if not (isinstance(times, ndarray)):
            raise TypeError(f"times should be numpy.ndarray of float, got {type(times)}.")
        self.__times = copy(times)

    def get_times_dataset(self, post_instance: Posterior) -> NDArray[float]:
        """Return the times vector of the dataset"""
        return copy(post_instance.dataset_db[self.datasetname].get_datasetkwarg("time"))

    def get_times(
        self,
        post_instance: Posterior | None = None,
        time_limits: tuple[float, float] | None = None,
        npt: int | None = None,
        extra_dt: float | None = None,
    ) -> NDArray[float]:
        """Return the times vector define by the user or return a default one using the"""
        if self.times is not None:
            return self.times
        else:
            if time_limits is None:
                if self.time_limits is None:
                    if post_instance is None:
                        raise ValueError(
                            "You didn't specify times, nor time_limits. To be able to compute a default time vector you need to provide post_instance !"
                        )
                    times_dataset = self.get_times_dataset(post_instance=post_instance)
                    time_limits = (min(times_dataset), max(times_dataset))
                else:
                    time_limits = self.time_limits
            if npt is None:
                if self.npt is None:
                    raise ValueError(
                        "You didn't specify times, nor npt. You need to provide at least one."
                    )
                else:
                    npt = self.npt
            if extra_dt is None:
                extra_dt = 0.0
            return linspace(
                time_limits[0] - extra_dt, time_limits[1] + extra_dt, npt, endpoint=False
            )

    def get_errors_datasets(self, post_instance: Posterior) -> NDArray[float]:
        """Return the data errors vector of the dataset"""
        return copy(post_instance.dataset_db[self.datasetname].get_datasetkwarg("data_err"))

    @property
    def time_limits(self) -> tuple[float, float] | None:
        return copy(self.__time_limits)

    def set_time_limits(self, time_limits: tuple[float, float]):
        if not (isinstance(time_limits, tuple)) or not (
            all([isinstance(time_limits_i, Number) for time_limits_i in time_limits])
        ):
            raise TypeError(f"time_limits should be a tuple of floats, got {time_limits}.")
        self.__time_limits = copy(time_limits)

    @property
    def npt(self) -> int | None:
        return self.__npt

    def set_npt(self, npt: int):
        if self.times is not None:
            raise ValueError("You cannot set both times and npt.")
        if not (isinstance(npt, int)) or not (npt > 1):
            raise TypeError(f"npt should be int > 1, got {type(npt)}.")
        self.__npt = npt

    def _init_ModelBinning(self, exptime: float | int | None, supersampling: int | None):
        self.__modelbinning = ModelBinning(exptime=exptime, supersampling=supersampling)

    @property
    def binning(self):
        return self.__modelbinning

    @property
    def exptime(self) -> float | int:
        return self.binning.exptime

    @property
    def supersampling(self) -> int:
        return self.binning.supersampling

    @property
    def datasetname(self) -> str | None:
        return self.__datasetname

    def _init_datasetname(self, datasetname: str | None):
        self.__datasetname: str | None = None
        if datasetname is not None:
            self.set_datasetname(datasetname=datasetname)

    def set_datasetname(self, datasetname: str):
        if not (isinstance(datasetname, str)):
            raise TypeError(f"datasetname should be a string, got {type(datasetname)}.")
        self.__datasetname = datasetname

    @property
    def pl_factors(self) -> Pl_factors:
        return self.__pl_factors

    def _init_pl_factors(self, time_factor: float | None, value_factor: float | None):
        self.__pl_factors = Pl_factors(time_factor=time_factor, value_factor=value_factor)

    @property
    def pl_kwargs(self) -> dict:
        return self.__pl_kwargs

    def _init_pl_kwargs(self, pl_kwargs: dict | None):
        self.__pl_kwargs: dict = {}
        if pl_kwargs is not None:
            if not (isinstance(pl_kwargs, dict)):
                raise TypeError(f"pl_kwargs should be a dict or None, got {type(pl_kwargs)}")
            else:
                self.pl_kwargs.update(pl_kwargs)

    @property
    def pl_kwargs_error(self) -> dict:
        return self.__pl_kwargs_err

    def _init_pl_kwargs_err(self, pl_kwargs_error: dict | None):
        self.__pl_kwargs_err: dict = {}
        if pl_kwargs_error is not None:
            if not (isinstance(pl_kwargs_error, dict)):
                raise TypeError(f"pl_kwargs should be a dict or None, got {type(pl_kwargs_error)}")
            else:
                self.pl_kwargs_error.update(pl_kwargs_error)

    @property
    def show_error(self) -> bool:
        return self.__show_error

    @show_error.setter
    def show_error(self, show_error: bool):
        if not (isinstance(show_error, bool)):
            raise TypeError(f"show_error should be a bool, got {type(show_error)}")
        self.__show_error = show_error

    def _init_df_param_value(self, df_param_value: DataFrame | None):
        self.__df_param_value: DataFrame | None = None
        if df_param_value is not None:
            self.df_param_value = df_param_value

    @property
    def df_param_value(self) -> DataFrame | None:
        return self.__df_param_value

    @df_param_value.setter
    def df_param_value(self, new: DataFrame):
        if not (isinstance(new, DataFrame)):
            raise TypeError(f"df_param_value should be a pandas.DataFrame, got {type(new)}")
        if "value" not in new.columns:
            raise ValueError(
                "df_param_value should have a column called 'value' with the value of the parameters."
            )
        self.__df_param_value = new


class Data2plot(Model2plot):
    def __init__(
        self,
        expression: str,
        exptime: float | int | None = None,
        method: str | None = None,
        datasetname: str | None = None,
        time_factor: float | None = None,
        value_factor: float | None = None,
        pl_kwargs: dict | None = None,
        pl_kwargs_error: dict | None = None,
        show_error: bool = True,
        df_param_value: DataFrame | None = None,
    ):
        self._init_expression(expression=expression)
        self._check_expression_4_data(expression=self.expression)
        self._init_DataBinning(exptime=exptime, method=method)
        self._init_datasetname(datasetname=datasetname)
        self._init_pl_factors(time_factor=time_factor, value_factor=value_factor)
        self._init_pl_kwargs(pl_kwargs=pl_kwargs)
        self._init_pl_kwargs_err(pl_kwargs_error=pl_kwargs_error)
        self._init_df_param_value(df_param_value=df_param_value)
        self.show_error = show_error

    def _check_expression_4_data(self, expression: Expression):
        if "data" not in expression.components:
            raise ValueError("expression needs to involve data")

    def _init_DataBinning(self, exptime: float | int | None, method: str | None):
        self.__databinning = DataBinning(exptime=exptime, method=method)

    @property
    def binning(self):
        return self.__databinning

    @property
    def exptime(self) -> float | int:
        return self.binning.exptime

    @property
    def method(self) -> str:
        return self.binning.method


class MultiData2plot(Data2plot):
    def __init__(
        self,
        l_expression_and_datasetname: list[tuple[str, str]],
        exptime: float | int | None = None,
        method: str | None = None,
        time_factor: float | None = None,
        value_factor: float | None = None,
        pl_kwargs: dict | None = None,
        pl_kwargs_error: dict | None = None,
        show_error: bool = True,
        df_param_value: DataFrame | None = None,
    ):
        self._init_l_data2plot(
            l_expression_and_datasetname=l_expression_and_datasetname,
            exptime=exptime,
            method=method,
            time_factor=time_factor,
            value_factor=value_factor,
            df_param_value=df_param_value,
        )
        self._init_DataBinning(exptime=exptime, method=method)
        self._init_pl_kwargs(pl_kwargs=pl_kwargs)
        self._init_pl_kwargs_err(pl_kwargs_error=pl_kwargs_error)
        self.show_error = show_error

    @property
    def l_data2plot(self):
        return self.__l_data2plot

    def _init_l_data2plot(
        self,
        l_expression_and_datasetname: list[tuple[str, str]],
        exptime: float | int | None = None,
        method: str | None = None,
        time_factor: float | None = None,
        value_factor: float | None = None,
        df_param_value: DataFrame | None = None,
    ):
        self.__l_data2plot = [
            Data2plot(
                expression=expression_i,
                datasetname=datasetname_i,
                time_factor=time_factor,
                value_factor=value_factor,
                df_param_value=df_param_value,
            )
            for expression_i, datasetname_i in l_expression_and_datasetname
        ]

    @property
    def df_param_value(self) -> DataFrame | None:
        return self.l_data2plot[0].df_param_value

    @df_param_value.setter
    def df_param_value(self, new: DataFrame):
        if not (isinstance(new, DataFrame)):
            raise TypeError(f"df_param_value should be a pandas.DataFrame, got {type(new)}")
        if "value" not in new.columns:
            raise ValueError(
                "df_param_value should have a column called 'value' with the value of the parameters."
            )
        for data2plot_i in self.l_data2plot:
            data2plot_i.df_param_value = new


class MultiModel2plot(Model2plot):
    def __init__(
        self,
        l_expression_and_datasetname: list[tuple[str, str]],
        exptime: float | int | None = None,
        supersampling: int | None = None,
        pl_kwargs: dict | None = None,
        pl_kwargs_error: dict | None = None,
        show_error: bool = True,
        df_param_value: DataFrame | None = None,
    ):
        self._init_l_model2plot(
            l_expression_and_datasetname=l_expression_and_datasetname,
            exptime=exptime,
            supersampling=supersampling,
            df_param_value=df_param_value,
        )
        self._init_ModelBinning(exptime=exptime, supersampling=supersampling)
        self._init_pl_kwargs(pl_kwargs=pl_kwargs)
        self._init_pl_kwargs_err(pl_kwargs_error=pl_kwargs_error)
        self.show_error = show_error

    @property
    def l_model2plot(self):
        return self.__l_model2plot

    def _init_l_model2plot(
        self,
        l_expression_and_datasetname: list[tuple[str, str]],
        exptime: float | int | None = None,
        supersampling: int | None = None,
        df_param_value: DataFrame | None = None,
    ):
        self.__l_model2plot = [
            Model2plot(
                expression=expression_i,
                exptime=exptime,
                supersampling=supersampling,
                datasetname=datasetname_i,
                pl_kwargs=None,
                pl_kwargs_error=None,
                show_error=False,
                df_param_value=df_param_value,
            )
            for expression_i, datasetname_i in l_expression_and_datasetname
        ]

    @property
    def df_param_value(self) -> DataFrame | None:
        return self.l_model2plot[0].df_param_value

    @df_param_value.setter
    def df_param_value(self, new: DataFrame):
        if not (isinstance(new, DataFrame)):
            raise TypeError(f"df_param_value should be a pandas.DataFrame, got {type(new)}")
        if "value" not in new.columns:
            raise ValueError(
                "df_param_value should have a column called 'value' with the value of the parameters."
            )
        for model2plot_i in self.l_model2plot:
            model2plot_i.df_param_value = new


class ComputedModel:
    """Class to store computed models values: expression, binning, datasetname, times, values, errors"""

    def __init__(
        self,
        expression: str,
        datasetname: str,
        binning: ModelBinning | DataBinning,
        df_param_value: DataFrame,
        times: NDArray[float],
        values: NDArray[float],
        errors: NDArray[float],
    ):
        self.__expression: Expression = Expression(expression=expression)
        self.__set_datasetname(datasetname=datasetname)
        self.__binning: ModelBinning | DataBinning = binning
        self.__df_param_value: DataFrame = df_param_value.copy()
        self.__set_computed_model(times=times, values=values, errors=errors)

    @property
    def expression(self) -> Expression:
        # Return a list of unique terms (removing duplicates)
        return self.__expression

    @property
    def datasetname(self) -> str:
        return self.__datasetname

    def __set_datasetname(self, datasetname: str):
        if not (isinstance(datasetname, str)):
            raise TypeError(f"datasetname be a string, got {type(datasetname)}.")
        self.__datasetname = datasetname

    @property
    def binning(self) -> ModelBinning | DataBinning:
        return self.__binning

    @property
    def exptime(self) -> float | int:
        return self.__binning.exptime

    @property
    def supersampling(self) -> int:
        if isinstance(self.binning, ModelBinning):
            return self.binning.supersampling
        else:
            raise ValueError(
                "binning is of type Databinning and thus doesn't have a supersampling attribute."
            )

    @property
    def df_param_value(self) -> DataFrame:
        return self.__df_param_value.copy()

    @property
    def times(self) -> NDArray[float]:
        """Return original time vector stored"""
        return self.__times

    @property
    def values(self) -> NDArray[float]:
        """Return original model values vector stored"""
        return self.__values

    @property
    def errors(self) -> NDArray[float] | None:
        """Return original model errors vector stored"""
        return self.__errors

    def __set_computed_model(
        self, times: NDArray[float], values: NDArray[float], errors: NDArray[float] | None = None
    ):
        """Set the computed model (times and values).

        If npt and/or t_lims have been set, the times and values arguments will be check against those.
        If they were not set alreay they will be set using the times and values arguments.

        Once a computed model has been set it cannot be overwritten.
        """
        # Checking the times, values and values_err input are proper
        if (
            not (isinstance(times, ndarray))
            or not (isinstance(values, ndarray))
            or not ((errors is None) or isinstance(errors, ndarray))
        ):
            raise TypeError(
                f"times, values and values_err should be numpy.ndarray, got {type(times)}, {type(values)} and {type(errors)} respectively."
            )
        if (times.ndim != 1) or (values.ndim != 1) or ((errors is not None) and (values.ndim != 1)):
            raise ValueError(
                f"times, values and values_err (if not None) should be ndarray with 1 dimension. The number of dimension of times is {times.ndim}, the one of values is {values.ndim} and {'values_err is None' if errors is None else f'the one of values_err is {errors.ndim}'}"
            )
        if (times.size != values.size) or ((errors is not None) and (times.size != errors.size)):
            raise ValueError(
                f"times, values and values_err (if not None) should have the same size. times' size is {times.size}, values' size is {values.size} and {'values_err is None' if errors is None else f'values_err size is {errors.size}'}"
            )
        self.__times: NDArray[float] = times
        self.__values: NDArray[float] = values
        self.__errors: NDArray[float] | None = errors

    def get_computed_model(self):
        """Return copies of the times, values and errors stored"""
        return self.times.copy(), self.values.copy(), copy(self.errors)


class ComputedModels_Database:
    """Class to store the computed models (for all model expressions, all datasets, all times, all binning)"""

    __err_msg_model_already_computed = (
        "The model has already been computed, you can no longer modify {}."
    )

    def __init__(self):
        self.__stored_models: list[ComputedModel] = []

    @property
    def stored_models(self) -> list[ComputedModel]:
        return self.__stored_models

    def __df_param_value_equal(self, df_param_value_1, df_param_value_2):  # Sample Series
        # Align the Series to their common indexes
        common_indexes = df_param_value_1["value"].index.intersection(
            df_param_value_2["value"].index
        )
        aligned_series1 = df_param_value_1["value"][common_indexes]
        aligned_series2 = df_param_value_2["value"][common_indexes]

        # Check if the aligned Series are equal
        return aligned_series1.equals(aligned_series2)

    def find_computed_model(
        self,
        expression: str,
        datasetname: str,
        binning: DataBinning | ModelBinning,
        times: NDArray[float],
        df_param_value: DataFrame,
    ) -> tuple[ComputedModel | None, int | None, NDArray[float] | None]:
        model_found: ComputedModel | None = None
        times_found: NDArray[float] | None = None
        i_model_found: list[int] = []
        for ii, computed_model in enumerate(self.stored_models):
            if array_equal(computed_model.times, times):
                times_found = computed_model.times
            if (
                (computed_model.expression.expression == expression)
                and (computed_model.datasetname == datasetname)
                and (computed_model.binning == binning)
                and array_equal(computed_model.times, times)
                and self.__df_param_value_equal(computed_model.df_param_value, df_param_value)
            ):
                i_model_found.append(ii)
                model_found = computed_model
        if len(i_model_found) > 1:
            print(
                f"Warning: The model has been found multiple times in the database at indexes {i_model_found}"
            )
        if len(i_model_found) > 0:
            return deepcopy(model_found), i_model_found[-1], deepcopy(times_found)
        else:
            return None, None, deepcopy(times_found)

    def find_models(
        self,
        expression: str | None = None,
        datasetname: str | None = None,
        binning: DataBinning | ModelBinning | None = None,
        times: NDArray[float] | None = None,
    ) -> dict[int, dict]:
        res: dict[int, dict] = {}
        for ii, computed_model in enumerate(self.stored_models):
            good_model = True
            if expression is not None:
                good_model = computed_model.expression.expression == expression
            if good_model and (datasetname is not None):
                good_model = computed_model.datasetname == datasetname
            if good_model and (binning is not None):
                good_model = computed_model.binning == binning
            if good_model and (times is not None):
                good_model = array_equal(computed_model.times, times)
            if good_model:
                res[ii] = self._get_show_model_dict(idx=ii)
        return res

    def store_computed_model(
        self,
        expression: str,
        datasetname: str,
        binning: ModelBinning | DataBinning,
        df_param_value: DataFrame,
        times: NDArray[float],
        values: NDArray[float],
        errors: NDArray[float],
        overwrite: bool = False,
    ):
        """Set the computed model (times and values).

        If npt and/or t_lims have been set, the times and values arguments will be check against those.
        If they were not set alreay they will be set using the times and values arguments.

        Once a computed model has been set it cannot be overwritten.
        """
        model_found, _, times_found = self.find_computed_model(
            expression=expression,
            datasetname=datasetname,
            binning=binning,
            times=times,
            df_param_value=df_param_value,
        )
        if (model_found is None) or overwrite:
            if (model_found is not None) and overwrite:
                logger.info("Such model is already in the database, but it will be overwritten.")
            if times_found is not None:
                times = times_found
            self.stored_models.append(
                ComputedModel(
                    expression=expression,
                    datasetname=datasetname,
                    binning=binning,
                    df_param_value=df_param_value,
                    times=deepcopy(times),
                    values=deepcopy(values),
                    errors=deepcopy(errors),
                )
            )
        else:
            logger.warning(
                "Such model is already in the database and overwrite is False. The store command will be ignored."
            )

    def _get_show_model_dict(self, idx: int):
        return {
            "expression": self.stored_models[idx].expression.expression,
            "datasetname": self.stored_models[idx].datasetname,
            "binning": self.stored_models[idx].binning,
            "times": {
                "size": self.stored_models[idx].times.size,
                "min": min(self.stored_models[idx].times),
                "max": max(self.stored_models[idx].times),
            },
        }

    def show_stored_models(self):
        dico = OrderedDict()
        for ii in range(len(self.stored_models)):
            dico[ii] = self._get_show_model_dict(idx=ii)
        pprint(dico)


class Axis_Properties:
    """Class to specify the properties of an axis to be used in plot properties"""

    def __init__(
        self,
        name: str | None = None,
        unit: str | None = None,
        lims: tuple[None | float, None | float] | None = None,
        show_label: bool | None = None,
        show_ticklabels: bool | None = None,
        logscale: bool | None = None,
    ):
        self.__name: str | None = None
        if name is not None:
            self.name = name
        self.__unit: str | None = None
        if unit is not None:
            self.unit = unit
        self.__lims: tuple[None | float, None | float] = (None, None)
        if lims is not None:
            self.lims = lims
        self.__show_label = True
        if show_label is not None:
            self.show_label = show_label
        self.__show_ticklabels = True
        if show_ticklabels is not None:
            self.__show_ticklabels = show_ticklabels
        self.__logscale = False
        if logscale is not None:
            self.logscale = logscale

    @property
    def name(self) -> str | None:
        return self.__name

    @name.setter
    def name(self, new_name: str):
        if isinstance(new_name, str):
            self.__name = new_name
        else:
            TypeError(f"name should be a str, got {type(new_name)}")

    @property
    def unit(self) -> str | None:
        return self.__unit

    @unit.setter
    def unit(self, new_unit: str):
        if isinstance(new_unit, str):
            self.__unit = new_unit
        else:
            TypeError(f"unit should be a str, got {type(new_unit)}")

    @property
    def lims(self) -> tuple[None | float, None | float]:
        return self.__lims

    @lims.setter
    def lims(self, new_lims: Iterable[None | float]):
        if (
            not (isinstance(new_lims, tuple))
            or not (len(new_lims) == 2)
            or not (
                all(
                    [isinstance(new_lim_i, Number) or (new_lim_i is None) for new_lim_i in new_lims]
                )
            )
        ):
            raise TypeError(
                f"lims should be an Iterable of two elements that are either None or float, got {new_lims}"
            )
        else:
            self.__lims = (new_lims[0], new_lims[1])

    @property
    def label(self) -> str:
        """Return the label for the axis constructed from name and unit"""
        res = ""
        if self.name is not None:
            res += self.name
        if self.unit is not None:
            if len(res) > 0:
                res += " "
            res += f"[{self.unit}]"
        return res

    @property
    def show_label(self) -> bool:
        return self.__show_label

    @show_label.setter
    def show_label(self, new: bool):
        if isinstance(new, bool):
            self.__show_label = new
        else:
            TypeError(f"show_label should be a bool, got {type(new)}")

    @property
    def show_ticklabels(self) -> bool:
        return self.__show_ticklabels

    @show_ticklabels.setter
    def show_ticklabels(self, new: bool):
        if isinstance(new, bool):
            self.__show_ticklabels = new
        else:
            TypeError(f"show_ticklabels should be a bool, got {type(new)}")

    @property
    def logscale(self) -> bool:
        return self.__logscale

    @logscale.setter
    def logscale(self, new: bool):
        if isinstance(new, bool):
            self.__logscale = new
        else:
            TypeError(f"logscale should be a bool, got {type(new)}")


class YAxis_Properties(Axis_Properties):
    def __init__(
        self,
        name: str | None = None,
        unit: str | None = None,
        lims: tuple[None | float, None | float] | None = None,
        pad: tuple[float, float] | None = None,
        indicate_outliers: bool | None = None,
    ):
        super(self.__class__, self).__init__(name=name, unit=unit, lims=lims)
        self.__indicate_outliers = False
        if indicate_outliers is not None:
            self.indicate_outliers = indicate_outliers
        self.__pad: tuple[float, float] = (0.1, 0.1)
        if pad is not None:
            self.pad = pad

    @property
    def indicate_outliers(self) -> bool:
        return self.__indicate_outliers

    @indicate_outliers.setter
    def indicate_outliers(self, new: bool):
        if isinstance(new, bool):
            self.__indicate_outliers = new
        else:
            raise TypeError(f"indicate_outliers should be a bool. Got {type(new)}.")

    @property
    def pad(self) -> tuple[float, float]:
        return self.__pad

    @pad.setter
    def pad(self, new: tuple[float, float]):
        if isinstance(new, tuple) and (len(new) == 2) and all([ii > 0 for ii in new]):
            self.__pad = (float(new[0]), float(new[1]))
        else:
            raise ValueError(f"pad should be a tuple of two strictly positive number. Got {new}.")


class Axes_Properties:
    """Class to specify the properties of a plot to be used in plot definition"""

    def __init__(self):
        self.__title: str = ""
        self.__show_title: bool = True
        self.__legend_kwargs: dict = {}
        self.__do_legend: bool = True
        self.__x = Axis_Properties()
        self.__text_kwargs: list[dict] = []
        self._init_axes()

    @property
    def title(self) -> str:
        return self.__title

    @title.setter
    def title(self, new):
        if isinstance(new, str):
            self.__title = new
        else:
            raise TypeError(f"title should be a str. Got {type(new)}")

    @property
    def show_title(self) -> bool:
        return self.__show_title

    @property
    def legend_kwargs(self) -> dict:
        return self.__legend_kwargs

    @property
    def do_legend(self) -> bool:
        return self.__do_legend

    @do_legend.setter
    def do_legend(self, new: bool) -> bool:
        if not (isinstance(new, bool)):
            raise TypeError(f"do_legend should be a bool. Got {type(new)}")
        self.__do_legend = new

    def _init_axes(self):
        self.__y = YAxis_Properties()

    @property
    def x(self) -> Axis_Properties:
        return self.__x

    @property
    def y(self) -> YAxis_Properties:
        if type(self) == Axes_Properties:
            return self.__y
        else:
            raise TypeError(f"{type(self)} doesn't have attribute y")

    @property
    def text_kwargs(self) -> list[dict]:
        return self.__text_kwargs


class Axes_Properties_GLSP(Axes_Properties):
    """Class to specify the properties of a plot to be used in plot definition"""

    def __init__(self, WF: bool = False):
        self.__WF = False
        super().__init__()

    @property
    def WF(self):
        return self.__WF

    @WF.setter
    def WF(self, new):
        if not (isinstance(new, bool)):
            raise TypeError(f"WF should be a bool. Got {type(new)}")
        self.__WF = new

    def _init_axes(self):
        self.__yglsp = YAxis_Properties()
        if self.WF:
            self.__ywf = YAxis_Properties()

    @property
    def yglsp(self) -> YAxis_Properties:
        return self.__yglsp

    @property
    def ywf(self) -> YAxis_Properties:
        if self.WF:
            return self.__ywf
        else:
            raise ValueError("Axes_Properties_GLSP with WF=False doesn't have a ywf attribute")


class PlotsDefinition:
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

    def __init__(
        self,
        nb_rows: int | None = None,
        same4allrows: bool = False,
        nb_cols: int | None = None,
        same4allcols: bool = False,
    ):
        """"""
        # Default nb_rows and nb_cols
        if nb_rows is None:
            nb_rows = 1
        if nb_cols is None:
            nb_cols = 1
        # Check and set nb_rows and nb_cols
        if not (isinstance(nb_rows, int)) or (nb_rows < 1):
            raise TypeError(f"nb_rows should be a strictly positive int, got {nb_rows}")
        self.__nb_rows: int = nb_rows
        if not (isinstance(nb_cols, int)) or (nb_cols < 1):
            raise TypeError(f"nb_cols should be a strictly positive int, got {nb_cols}")
        self.__nb_cols: int = nb_cols
        # Check and set same4allrows, same4allcols
        if not (isinstance(same4allrows, bool)):
            raise TypeError(f"same4allrows should be a bool, got {same4allrows}")
        self.__same4allrows: bool = same4allrows
        if self.same4allrows:
            nb_rows = 1
        if not (isinstance(same4allcols, bool)):
            raise TypeError(f"same4allcols should be a bool, got {same4allcols}")
        self.__same4allcols: bool = same4allcols
        if self.same4allcols:
            nb_cols = 1
        # Init grid
        self.__grid: tuple[tuple[list[str], ...], ...] = tuple(
            [tuple([[] for _ in range(nb_cols)]) for _ in range(nb_rows)]
        )
        # Init models2plot_database
        self.__things2plot: dict[str, Model2plot | Data2plot | MultiData2plot] = {}
        # Init Axes_Properties
        self._init_axes_properties(nb_rows=nb_rows, nb_cols=nb_cols)

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

    # Init axes_properties
    def _init_axes_properties(self, nb_rows: int, nb_cols: int):
        self.__axes_properties: tuple[tuple[Axes_Properties, ...], ...] = tuple(
            [tuple([Axes_Properties() for _ in range(nb_cols)]) for _ in range(nb_rows)]
        )

    def get_axes_properties(
        self, i_row: int | None = None, i_col: int | None = None
    ) -> Axes_Properties:
        """Grid (in the form of a tuple of tuple) of Axes_Properties instances"""
        return self.__axes_properties[self._get_i(idx=i_row, roworcol="row")][
            self._get_i(idx=i_col, roworcol="col")
        ]

    @property
    def things2plot(self) -> dict[str, Model2plot | Data2plot | MultiData2plot]:
        """Dictionary providing the conversion from names to Model2plot, Data2plot or MultiData2plot instances"""
        return self.__things2plot.copy()

    def _get_l_i(self, idx: int | None, roworcol: str) -> list[int]:
        """Return a list of idx depending on idx and colorrow"""
        if roworcol == "row":
            size = len(self.grid)
        elif roworcol == "col":
            size = len(self.grid[0])
        else:
            raise ValueError(f"roworcol should be in ['col', 'row'], got {roworcol}")
        # If you don't provide i_row it means that you want to add to all rows
        if idx is None:
            l_idx = list(range(size))
        else:
            l_idx = [
                idx,
            ]
        return l_idx

    def _get_i(self, idx: int | None, roworcol: str) -> int:
        if roworcol == "row":
            size = len(self.grid)
        elif roworcol == "col":
            size = len(self.grid[0])
        if idx is None:
            if size == 1:
                idx = 0
            else:
                raise ValueError(
                    f"There are multiple {roworcol}s, so you need to provide i_{roworcol}."
                )
        return idx

    def add_existing_to_grid(self, name: str, i_row: int | None = None, i_col: int | None = None):
        """Add a model that is already in the models2plot in the grid."""
        # Check that name is in models
        if name not in self.things2plot:
            raise ValueError(f"There is no model2plot with name {name}.")
        l_i_row = self._get_l_i(idx=i_row, roworcol="row")
        l_i_col = self._get_l_i(idx=i_col, roworcol="col")
        # Make sure that i_row and i_col are correct
        for i_row in l_i_row:
            for i_col in l_i_col:
                # Add the name to the grid
                self.__grid[i_row][i_col].append(name)

    def removefromgrid(self, i_row: int, i_col: int, name: str):
        """Remove a model from the grid"""
        self.__grid[i_row][i_col].remove(name)

    def _check_namealreadyexists(self, name: str | None = None, overwrite: bool = False):
        if (name is not None) and (name in self.things2plot) and not (overwrite):
            raise ValueError(
                f"There is already a model2plot with this name ({name}). Please choose another name"
            )
        elif (name is not None) and (name in self.things2plot) and not (overwrite):
            logger.info(
                f"There is already a model2plot with this name ({name}). It will be overwritten"
            )

    def _modelordata(self, expression: Expression) -> str:
        if "data" in expression.components:
            return "data"
        else:
            return "model"

    def _create_modelordata2plot(self, expression: str, **kwargs) -> Data2plot | Model2plot:
        expression_instance = Expression(expression=expression)
        dataormodel = self._modelordata(expression=expression_instance)
        if dataormodel == "data":
            return Data2plot(expression=expression, **kwargs)
        else:
            return Model2plot(expression=expression, **kwargs)

    def add_modelordata2plot(
        self, expression: str, name: str | None = None, overwrite: bool = False, **kwargs
    ) -> str:
        """Add a Model2plot or Data2plot to things2plot"""
        self._check_namealreadyexists(name=name, overwrite=overwrite)
        modelordata2plot = self._create_modelordata2plot(expression=expression, **kwargs)
        if name is None:
            basename = expression
            if ("datasetname" in kwargs) and (kwargs["datasetname"]):
                basename += f"_{kwargs['datasetname']}"
            ii = 0
            name = f"{basename}"
            while name in self.things2plot:
                ii += 1
                name = f"{basename}_{ii}"
        # Add instance to models
        self.__things2plot[name] = modelordata2plot
        return name

    def _create_multimodelordata2plot(
        self, l_expression_and_datasetname: list[tuple[str, str]], **kwargs
    ) -> MultiData2plot | MultiModel2plot:
        l_modelordata = []
        for expression_i, _ in l_expression_and_datasetname:
            expression_instance_i = Expression(expression=expression_i)
            l_modelordata.append(self._modelordata(expression=expression_instance_i))
        if all([[modelordata_i == "data" for modelordata_i in l_modelordata]]):
            return MultiData2plot(
                l_expression_and_datasetname=l_expression_and_datasetname, **kwargs
            )
        elif all([[modelordata_i == "model" for modelordata_i in l_modelordata]]):
            return MultiModel2plot(
                l_expression_and_datasetname=l_expression_and_datasetname, **kwargs
            )
        else:
            raise ValueError(
                "l_expression_and_datasetname contains both expression for data and for model. You need to provide only data or only model"
            )

    def add_multimodelordata2plot(
        self,
        l_expression_and_datasetname: list[tuple[str, str]],
        name: str | None = None,
        overwrite: bool = False,
        **kwargs,
    ) -> str:
        """Add a MultiData2plot to things2plot"""
        self._check_namealreadyexists(name=name, overwrite=overwrite)
        multidataormodel2plot = self._create_multimodelordata2plot(
            l_expression_and_datasetname=l_expression_and_datasetname, **kwargs
        )
        if name is None:
            if type(multidataormodel2plot) == MultiData2plot:
                basename = "multidata"
            else:
                basename = "multimodel"
            ii = 0
            name = f"{basename}"
            while name in self.things2plot:
                ii += 1
                name = f"{basename}_{ii}"
        # Add instance to models
        self.__things2plot[name] = multidataormodel2plot
        return name

    def getthing2plot(self, name: str) -> Model2plot | Data2plot | MultiData2plot:
        """Get a Model2plot from models"""
        # Check that name is in models
        if name not in self.things2plot:
            raise ValueError(f"There is nothing to plot with name {name}.")
        return self.things2plot[name]

    def add_modelordata_to_grid(
        self,
        expression: str,
        i_row: int | None = None,
        i_col: int | None = None,
        name: str | None = None,
        overwrite: bool = False,
        **kwargs,
    ):
        """Add a model that is already in the grid.

        This function is a wrapper around addtogrid and addtomodels for the user convenience.
        There is two use cases:
        2. Adding a model to models and to grid in one function call
        """
        # If you don't provide i_row it means that you want to add to all rows
        l_i_rows = self._get_l_i(idx=i_row, roworcol="row")
        l_i_cols = self._get_l_i(idx=i_col, roworcol="col")
        # Add
        name = self.add_modelordata2plot(
            expression=expression, name=name, overwrite=overwrite, **kwargs
        )
        for i_row in l_i_rows:
            for i_col in l_i_cols:
                self.add_existing_to_grid(i_row=i_row, i_col=i_col, name=name)

    def add_multimodelordata_to_grid(
        self,
        l_expression_and_datasetname: list[tuple[str, str]],
        i_row: int | None = None,
        i_col: int | None = None,
        name: str | None = None,
        overwrite: bool = False,
        **kwargs,
    ):
        """Add a model that is already in the grid.

        This function is a wrapper around addtogrid and addtomodels for the user convenience.
        There is two use cases:
        2. Adding a model to models and to grid in one function call
        """
        # If you don't provide i_row it means that you want to add to all rows
        l_i_rows = self._get_l_i(idx=i_row, roworcol="row")
        l_i_cols = self._get_l_i(idx=i_col, roworcol="col")
        name = self.add_multimodelordata2plot(
            l_expression_and_datasetname=l_expression_and_datasetname,
            name=name,
            overwrite=overwrite,
            **kwargs,
        )
        for i_row in l_i_rows:
            for i_col in l_i_cols:
                self.add_existing_to_grid(i_row=i_row, i_col=i_col, name=name)

    def set_datasetname(
        self,
        datasetname: str,
        i_row: int | None = None,
        i_col: int | None = None,
        name: str | list[str] | None = None,
    ):
        """Set the datasetname for the model2plot or data2plot that do not have it already defined."""
        # If you don't provide i_row it means that you want to add to all rows
        l_i_rows = self._get_l_i(idx=i_row, roworcol="row")
        l_i_cols = self._get_l_i(idx=i_col, roworcol="col")
        # Set datasetname:
        for i_row in l_i_rows:
            for i_col in l_i_cols:
                # If you don't provide name it is that you want to set all models in the current location of the grid
                if name is None:
                    l_name = self.grid[i_row][i_col]
                elif isinstance(name, str):
                    l_name = [
                        name,
                    ]
                elif isinstance(name, list) and all([isinstance(name_i, str) for name_i in name]):
                    l_name = copy(name)
                else:
                    raise TypeError(
                        f"name should be either None, or a str or a list of str, got {name}"
                    )
                for name_i in l_name:
                    if name_i not in self.grid[i_row][i_col]:
                        logger.info(
                            f"No model with name {name_i} in the grid at row {i_row} and col {i_col}"
                        )
                    else:
                        thing2plot = self.getthing2plot(name=name_i)
                        if isinstance(thing2plot, Data2plot) or isinstance(thing2plot, Model2plot):
                            if thing2plot.datasetname is None:
                                thing2plot.set_datasetname(datasetname=datasetname)
                            else:
                                logger.info(
                                    f"{name_i} (found in the grid at row {i_row} and col {i_col}) already as a datasetname ({thing2plot.datasetname}) it will not be changed"
                                )
                        else:
                            pass

    def get_models2plot(self, i_row: int, i_col: int) -> OrderedDict[str, Model2plot]:
        """For a given axis of the grid (designated by i_row and i_col), return an OrderedDict with the Model2plot instances for this axis"""
        res = OrderedDict()
        for name in self.grid[i_row][i_col]:
            if type(self.things2plot[name]) is Model2plot:
                res[name] = self.things2plot[name]
        return res

    def get_datas2plot(self, i_row: int, i_col: int) -> OrderedDict[str, Data2plot]:
        """For a given axis of the grid (designated by i_row and i_col), return an OrderedDict with the Model2plot instances for this axis"""
        res = OrderedDict()
        for name in self.grid[i_row][i_col]:
            if type(self.things2plot[name]) is Data2plot:
                res[name] = self.things2plot[name]
        return res

    def get_multidatas2plot(self, i_row: int, i_col: int) -> OrderedDict[str, MultiData2plot]:
        """For a given axis of the grid (designated by i_row and i_col), return an OrderedDict with the Model2plot instances for this axis"""
        res = OrderedDict()
        for name in self.grid[i_row][i_col]:
            if type(self.things2plot[name]) is MultiData2plot:
                res[name] = self.things2plot[name]
        return res

    def get_multimodels2plot(self, i_row: int, i_col: int) -> OrderedDict[str, MultiModel2plot]:
        """For a given axis of the grid (designated by i_row and i_col), return an OrderedDict with the Model2plot instances for this axis"""
        res = OrderedDict()
        for name in self.grid[i_row][i_col]:
            if type(self.things2plot[name]) is MultiModel2plot:
                res[name] = self.things2plot[name]
        return res

    def get_used_datasetnames(self, i_row: int, i_col: int) -> list[str]:
        """Return the list of all datasetnames used in a given axis of the grid (designated by i_row and i_col)."""
        datasetnames = []
        for data2plot_i in self.get_datas2plot(i_row=i_row, i_col=i_col).values():
            datasetnames.append(data2plot_i.datasetname)
        return list(set(datasetnames))

    def set_axis_property(
        self, value, property: str, axis: str, i_row: int | None = None, i_col: int | None = None
    ):
        l_i_row = self._get_l_i(idx=i_row, roworcol="row")
        l_i_col = self._get_l_i(idx=i_col, roworcol="col")
        # Make sure that i_row and i_col are correct
        for i_row in l_i_row:
            for i_col in l_i_col:
                axe_properties = getattr(self.get_axes_properties(i_row=i_row, i_col=i_col), axis)
                if hasattr(axe_properties, property):
                    setattr(axe_properties, property, value)
                else:
                    raise AttributeError(f"{axe_properties} doesn't have attribute {property}")

    def set_axes_property(
        self, value, property: str, i_row: int | None = None, i_col: int | None = None
    ):
        l_i_row = self._get_l_i(idx=i_row, roworcol="row")
        l_i_col = self._get_l_i(idx=i_col, roworcol="col")
        # Make sure that i_row and i_col are correct
        for i_row in l_i_row:
            for i_col in l_i_col:
                if hasattr(self.get_axes_properties(i_row=i_row, i_col=i_col), property):
                    setattr(self.get_axes_properties(i_row=i_row, i_col=i_col), property, value)
                else:
                    raise ValueError(f"Property {property} doesn't exist.")

    def set_df_param_value(
        self,
        df_param_value: DataFrame,
        i_row: int | None = None,
        i_col: int | None = None,
        name: str | list[str] | None = None,
    ):
        """Set the value of the df_param_value attribute of the thing2plot instances that do not have it already defined."""
        # If you don't provide i_row it means that you want to add to all rows
        l_i_row = self._get_l_i(idx=i_row, roworcol="row")
        l_i_col = self._get_l_i(idx=i_col, roworcol="col")
        for i_row in l_i_row:
            for i_col in l_i_col:
                # If you don't provide name it is that you want to set all models in the current location of the grid
                if name is None:
                    l_name = self.grid[i_row][i_col]
                elif isinstance(name, str):
                    l_name = [
                        name,
                    ]
                elif isinstance(name, list) and all([isinstance(name_i, str) for name_i in name]):
                    l_name = copy(name)
                else:
                    raise TypeError(
                        f"name should be either None, or a str or a list of str, got {name}"
                    )
                for name_i in l_name:
                    if name_i not in self.grid[i_row][i_col]:
                        logger.info(
                            f"No model with name {name_i} in the grid at row {i_row} and col {i_col}"
                        )
                    else:
                        thing2plot = self.getthing2plot(name=name_i)
                        if thing2plot.df_param_value is None:
                            thing2plot.df_param_value = df_param_value
                        else:
                            logger.info(
                                f"{name_i} (found in the grid at row {i_row} and col {i_col}) already as a df_param_value it will not be changed"
                            )

    def has_something2plot(self, i_row: int, i_col: int):
        return len(self.grid[i_row][i_col]) > 0

    # def get_all_modelnames(self) -> list[str]:
    #     """Return the list of all the names of the Model2plot instances used in the grid."""
    #     l_i_rows = self._get_l_i(roworcol='row')
    #     l_i_cols = self._get_l_i(roworcol='col')
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
    # for i_row in self._get_l_idx(row_or_col='row', idx=row_idx):
    #     for i_col in self._get_l_idx(row_or_col='col', idx=col_idx):
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


class PlotsDefinition_GLSP(PlotsDefinition):
    def __init__(
        self,
        nb_rows: int | None = None,
        same4allrows: bool = False,
        nb_cols: int | None = None,
        same4allcols: bool = False,
    ):
        super().__init__(
            nb_rows=nb_rows, same4allrows=same4allrows, nb_cols=nb_cols, same4allcols=same4allcols
        )

    # Init axes_properties
    def _init_axes_properties(self, nb_rows: int, nb_cols: int):
        self.__axes_properties: tuple[tuple[Axes_Properties_GLSP, ...], ...] = tuple(
            [tuple([Axes_Properties_GLSP() for _ in range(nb_cols)]) for _ in range(nb_rows)]
        )

    def get_axes_properties(
        self, i_row: int | None = None, i_col: int | None = None
    ) -> Axes_Properties_GLSP:
        """Grid (in the form of a tuple of tuple) of Axes_Properties_GLSP instances"""
        return self.__axes_properties[self._get_i(idx=i_row, roworcol="row")][
            self._get_i(idx=i_col, roworcol="col")
        ]

    def set_WF(self, value, i_row: int | None = None, i_col: int | None = None):
        l_i_row = self._get_l_i(idx=i_row, roworcol="row")
        l_i_col = self._get_l_i(idx=i_col, roworcol="col")
        # Make sure that i_row and i_col are correct
        for i_row in l_i_row:
            for i_col in l_i_col:
                self.get_axes_properties(i_row=i_row, i_col=i_col).WF = value


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
