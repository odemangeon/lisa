"""
Decorrelation model module.

TODO:
- If I want several decorrelation methods beside the Linear Decorrelation and do not want to have to
modify this module than I will need to implement a decorrelation method manager.
"""
from loguru import logger

from ....tools.metaclasses import MandatoryReadOnlyAttrAndMethod
from ....tools.miscellaneous import spacestring_like
from ..dataset_and_instrument.manager_dataset_instrument import Manager_Inst_Dataset


mgr_inst_dst = Manager_Inst_Dataset()
mgr_inst_dst.load_setup()


class Core_DecorrelationModel(object, metaclass=MandatoryReadOnlyAttrAndMethod):
    """docstring for Core_DecorrelationModel class, Parent class of all Decorrelation Model Class"""

    ## List of mandatory arguments which have to be defined in the subclasses.
    # For example "category" is in this list. It has to be defined in the subclass as a class
    # attribute like this:
    # __category__ = "ModelCategory"
    # It then be read as self.category
    __mandatoryattrs__ = ["category", "format_config_dict"]
    # category: String which designate the decorrelation model (for example: "linear"). To choose the
    #   decorrelation model to be used, the user will use this string.
    # format_config_dict is a strong to be used as the example of how to specify the dictionary in the
    #   Instrument specific parameter file
    __mandatorymeths__ = ["apply_parametrisation", "get_text_decorrelation"]
    # apply_parametrisation: Method that creates the parameters necessary for the decorrelation model
    #  for each instrument model object of the instrument category to which this decorrelation model applies
    #  The arguments must be inst_mod_obj, the Instrument model object and decorrelation_config_inst_decorr
    #  the dictionary that contains the configuration of the decorrelation model for the instrument model object
    #  considered
    # get_text_decorrelation: This function produces the text for the decorrelation model for all decorrelation
    #  variable using a given decorrelation category

    @classmethod
    def load_text_decorr_paramfile(cls, inst_mod_obj, decorrelation_config_inst_decorr_paramfile, decorrelation_config_inst_decorr,
                                   skip_load=False):
        """load the parametrisation for the decorrelation of the instrument model from the inst cat param file.

        Method which load the dictionary written in an instrument category
        specific paramfile and which contains the parameterisation of the decorrelation models for each
        for each instrument model of the category.

        This function is used by Core_InstCat_Model.load_config_decorrelation
        It is advised to overload this function in the child Core_DecorrelationModel class to at make
        some additional checks on the content of decorrelation_config_inst_decorr_paramfile.

        Arguments
        ---------
        inst_mod_obj                                : Core_InstrumentModel
            Instrument model object of which you want to load the decorrelation parameterisation
        decorrelation_config_inst_decorr_paramfile  : dict
            Dictionary providing the configuration of the decorrelation for the instrument model inst_mod_obj
            and the current decorrelation method.
            The expected format is
        decorrelation_config_inst_decorr            : dict
            Dictionary where the decorrelation configuration is stored for the instrument model inst_mod_obj
            and the current decorrelation method.
        skip_load                                   : bool
            If True the function will not load into decorrelation_config_inst_decorr. This option is to
            be used when you are overloading this function to performed the loading in the overloading function
            while keeping the checl
        """
        # Check that each instrument model object of the decorrelation variable exists
        for inst_mod_obj_decorr_var_name in decorrelation_config_inst_decorr_paramfile.keys():
            inst_mod_obj_decorr_var_name_info = mgr_inst_dst.interpret_instmod_fullname(instmod_fullname=inst_mod_obj_decorr_var_name, raise_error=True)
        if not(skip_load):
            decorrelation_config_inst_decorr = decorrelation_config_inst_decorr_paramfile
