#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Datasim creator for the polynomial model of indicator
"""
from logging import getLogger

from .core_indicator_model import Core_Indicator_Model
from ..polynomial_model import set_polymodel_parametrisation, set_dico_config, get_dico_config, get_polymodel
# from ....core.parameter import Parameter


## Logger object
logger = getLogger()


tab = "    "


class PolynomialIndicatorModel(Core_Indicator_Model):
    """docstring for PolynomialIndicatorModel."""

    # Define name of indicator models
    __model_name__ = "polynomial"

    __drift_basename__ = "drift"
    __name_coeff_const_inst__ = "C0"
    __name_coeff_const_sys__ = "{indicator}0"
    # # Define name of polynomial model parameters
    # _polynomial_order_name = "order"

    # # Default parameter values
    # _default_param_values = {_polynomial_order_name: 0}

    @classmethod
    def set_parametrisation(cls, param_container, indicator_category, instrument_per_instrument=True, prefix=None):
        """Set the parametrisation for the polynomial modelling of a given instrument category.

        Arguments
        ---------
        param_container             : Param_Container
        indicator_category          : str
        instrument_per_instrument   : bool
        prefix                      : str
        """
        if instrument_per_instrument:
            name_coeff_const = cls.__name_coeff_const_inst__
        else:
            name_coeff_const = cls.__name_coeff_const_sys__.format(indicator=indicator_category)
        set_polymodel_parametrisation(param_container=param_container, name_coeff_const=name_coeff_const,
                                        func_param_name=lambda order: cls.get_param_name(order=order, prefix=prefix),
                                        full_category_4_unit=indicator_category,
                                        prefix=prefix)

    @classmethod
    def get_param_name(cls, order, prefix):
        """Return the parameter name of the coefficient of the RV drift model."""
        if prefix is None:
            return f"{cls.__drift_basename__}{order}"
        else:
            return f"{prefix}{cls.__drift_basename__}{order}"

    @classmethod
    def set_dico_config(cls, param_container, prefix, dico_config=None):
        """Get the dictionary that configures the polynomial model for a given instrument category
        Proxy for lisa.posterior.core.model.polynomial_model.set_dico_config

        Arguments
        ---------
        param_container     : Param_Container
        prefix  : str
        dico_config         : dict
            Updates that you might want to do to the dico that configure the polynomial model
        """
        set_dico_config(param_container=param_container, prefix=prefix, dico_config=dico_config)

    @classmethod
    def get_dico_config(cls, param_container, prefix, notexist_ok=False, return_None_if_notexist=False):
        """Get the dictionary that configures the polynomial model for a given instrument category
        Proxy for lisa.posterior.core.model.polynomial_model.set_dico_config

        Arguments
        ---------
        inst_cat        : str
            Instrument category
        dico_config     : dict
            Updates that you might want to do to the dico that configure the polynomial model
        """
        return get_dico_config(param_container=param_container, prefix=prefix, notexist_ok=notexist_ok,
                               return_None_if_notexist=return_None_if_notexist)

    @classmethod
    def create_datasimulator(cls, model_instance, multi, l_inst_model, l_dataset, get_times_from_datasets,
                             tab, time_vec_name, l_time_vec_name, INDcat_model, indicator_category,
                             dataset_db, function_builder, l_function_shortname, ext_func_fullname):
        """Create a datasimulator for indicators using the polynomial model

        Arguments
        ---------
        model_instance
        multi
        l_inst_model   :
        l_dataset
        get_times_from_datasets  : bool
            If True the times at which the LC model is computed is taken from the datasets.
            Else it is an input of the datasimulator function produced.
        tab
        time_vec_name
        l_time_vec_name
        INDcat_model                 : IND_InstCat_Model
            Instance of the IND_InstCat_Model
        indicator_category          : str
        dataset_db                  : DatasetDatabase
            Dataset database, this will be used by the function to access the all the dataset of a given instrument model,
            not only the datasets to be simulated.
        function_builder
        l_function_shortname
        ext_func_fullname

        Returns
        -------
        d_dico_docf : dict_of_dict_of_DatasimDocFunc
            A dictionary with DocFunctions containing the data
            simulator function for the whole system ("whole") and for the each planet individually
            ("planet_name")
        """
        #######################################################
        # Produce instrumental variations models per instrument
        #######################################################
        d_l_instvar = get_polymodel(multi=multi, l_inst_model=l_inst_model, l_dataset=l_dataset, get_times_from_datasets=get_times_from_datasets,
                                    tab=tab, time_vec_name=time_vec_name, l_time_vec_name=l_time_vec_name, inst_cat_model=INDcat_model,
                                    dataset_db=dataset_db, function_builder=function_builder, l_function_shortname=l_function_shortname,
                                    polyonly_func_shortname=f"{indicator_category}_inst_var", ext_func_fullname=ext_func_fullname,
                                    name_coeff_const=cls.__name_coeff_const_inst__,
                                    func_param_name=lambda order: cls.get_param_name(order=order, prefix=None),
                                    instrument_per_instrument_model=True, param_container=None, prefix_config=None,
                                    )

        #######################################################
        # Produce instrumental variations models per instrument
        #######################################################
        d_l_sysvar = get_polymodel(multi=multi, l_inst_model=l_inst_model, l_dataset=l_dataset, get_times_from_datasets=get_times_from_datasets,
                                   tab=tab, time_vec_name=time_vec_name, l_time_vec_name=l_time_vec_name, inst_cat_model=INDcat_model,
                                   dataset_db=dataset_db, function_builder=function_builder, l_function_shortname=l_function_shortname,
                                   polyonly_func_shortname=f"{indicator_category}_sys_var", ext_func_fullname=ext_func_fullname,
                                   name_coeff_const=cls.__name_coeff_const_sys__.format(indicator=indicator_category),
                                   func_param_name=lambda order: cls.get_param_name(order=order, prefix=indicator_category),
                                   instrument_per_instrument_model=False, param_container=model_instance, prefix_config=indicator_category,
                                   )

        return {f"{indicator_category}_poly_instvar": d_l_instvar, f"{indicator_category}_poly_sysvar": d_l_sysvar}
