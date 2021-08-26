#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Decorrelation model module.
"""
from logging import getLogger

from ....core.model.core_decorrelation_model import Core_DecorrelationModel
## Logger object
logger = getLogger()


class LinearDecorrelation_LC(Core_DecorrelationModel):
    """docstring for LinearDecorrelation_LC."""

    # Mandatory attributes from Core_DecorrelationModel
    __category__ = "linear"
    __name_dict_paramfile__ = "linear_decorr"
    __format_config_dict__ = "{'quantity': 'raw'}"

    # def __init__(self, arg):
    #     super(LinearDecorrelation_LC, self).__init__()
    #     self.arg = arg

    # Mandatory method from Core_DecorrelationModel
    def create_text_decorr_paramfile(self):
        raise NotImplementedError

    # Mandatory method from Core_DecorrelationModel
    def load_text_decorr_paramfile(self):
        raise NotImplementedError

    @classmethod
    def apply_parametrisation(cls, inst_mod_obj, dico_config):
        """Apply the parametrisation for the decorrelation to an instrument model

        Arguments
        ---------
        inst_mod_obj    : Instrument_Model instance
            Instrument model object to which you want to apply the parametrisation associated to the
            decorrelation model
        dico_config     : dict
            dictionary which contain the configuration of the decorrelation for this instrument model
        """
        inst_mod_obj.
        inst_mod_obj.add_parameter()
        raise NotImplementedError()
