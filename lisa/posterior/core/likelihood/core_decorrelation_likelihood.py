"""
Decorrelation model module.

TODO:
- If I want several decorrelation methods beside the Linear Decorrelation and do not want to have to
modify this module than I will need to implement a decorrelation method manager.
"""
from loguru import logger
from copy import deepcopy

from ....tools.metaclasses import MandatoryReadOnlyAttrAndMethod
# from ....tools.miscellaneous import spacestring_like
from ..dataset_and_instrument.manager_dataset_instrument import Manager_Inst_Dataset


mgr_inst_dst = Manager_Inst_Dataset()
mgr_inst_dst.load_setup()


class Core_DecorrelationLikelihood(object, metaclass=MandatoryReadOnlyAttrAndMethod):
    """docstring for Core_DecorrelationLikelihood class, Parent class of all Decorrelation likelihood Class"""

    ## List of mandatory arguments which have to be defined in the subclasses.
    # For example "category" is in this list. It has to be defined in the subclass as a class
    # attribute like this:
    # __category__ = "ModelCategory"
    # It then be read as self.category
    __mandatoryattrs__ = ["category", "format_config_dict", "l_required_inddatasetkwarg_keys",
                          "l_required_datasetkwarg_keys", ]
    # category: String which designate the decorrelation model (for example: "linear"). To choose the
    #   decorrelation model to be used, the user will use this string.
    # format_config_dict is a strong to be used as the example of how to specify the dictionary in the
    #   Instrument specific parameter file
    __mandatorymeths__ = ["create_decorrelation_likelihood"]
    # apply_parametrisation: Method that creates the parameters necessary for the decorrelation model
    #  for each instrument model object of the instrument category to which this decorrelation model applies
    #  The arguments must be inst_mod_obj, the Instrument model object and decorrelation_config_inst_decorr
    #  the dictionary that contains the configuration of the decorrelation model for the instrument model object
    #  considered
    # get_text_decorrelation: This function produces the text for the decorrelation model for all decorrelation
    #  variable using a given decorrelation category

    @classmethod
    def load_text_decorr_paramfile(cls, model_name, config_model_paramfile, config_model_storage, model_instance):
        """load the parametrisation for the decorrelation of the instrument model from the inst cat param file.

        Method which load the dictionary written in an instrument category  specific paramfile and which
        contains the parameterisation of the decorrelation models for an likelihood decorrelation model

        This function is used by Core_InstCat_Model.load_config_decorrelation
        It is advised to overload this function in the child Core_DecorrelationLikelihood class to make
        some additional checks on the specific content required by the likelihood decorrelation model

        Arguments
        ---------
        model_name              : str
            Name of the likelihood decorrelation model being loaded
        config_model_paramfile  : dict
            Dictionary providing the configuration one the decorrelation likelihood model
        config_model_storage    : dict
            Dictionary where the decorrelation likelihood model configuration will be stored.
        model_instance          : Subclass of Core_Model
        """
        config_model_storage = deepcopy(config_model_paramfile)

    @classmethod
    def get_required_dataset(cls, match_datasets, d_required_datasetkwargkeys_4_dataset, d_required_datasetkwargkeys_4_inddataset,
                             l_dataset_name
                             ):
        """Fill the dictionary d_required_datasetkwargkeys_4_dataset, d_required_datasetkwargkeys_4_inddataset
        for a given likelihood decorrelation model.

        The only necessary input from this decorrelation model configuration is the 'match datasets'
        info.

        d_required_datasetkwargkeys_4_dataset provides the required simulated datasets and their dataset keys
        d_required_datasetkwargkeys_4_inddataset provides the required indicator datasets and their dataset keys

        This function is called by Core_InstCat_Model._get_required_dataset

        Arguments
        ---------
        match_datasets                              :
        d_required_datasetkwargkeys_4_dataset       :
        d_required_datasetkwargkeys_4_inddataset    :
        l_dataset_name                              :

        Returns
        -------
        d_required_datasetkwargkeys_4_dataset       :
        d_required_datasetkwargkeys_4_inddataset    :
        """
        for dataset_name, ind_dataset_name in match_datasets.items():
            for datasetkwarg in cls.l_required_datasetkwarg_keys:
                if datasetkwarg not in d_required_datasetkwargkeys_4_dataset[dataset_name]:
                    d_required_datasetkwargkeys_4_dataset[dataset_name].append(datasetkwarg)
            for datasetkwarg in cls.l_required_inddatasetkwarg_keys:
                if datasetkwarg not in d_required_datasetkwargkeys_4_inddataset[ind_dataset_name]:
                    d_required_datasetkwargkeys_4_inddataset[ind_dataset_name].append(datasetkwarg)

        return d_required_datasetkwargkeys_4_dataset, d_required_datasetkwargkeys_4_inddataset

    # @classmethod
    # def get_likelihood_elements(cls, match_datasets, l_dataset_name):
    #     """Return the elements required to build the likelihood decorrelation of a given decorrelation
    #     model.
    #
    #     The only necessary input from this decorrelation model configuration is the 'match datasets'
    #     info.
    #
    #     This function is called by
    #
    #     Arguments
    #     ---------
    #     match_datasets      : dict
    #         Dictionary that match the simulated datasets names to the indicator datasets names used for
    #         the likelihood decorrelation model
    #     l_dataset_name      : list of str
    #         list of datasets name in the final datasimulator used in the likelihood computation
    #
    #     Returns
    #     -------
    #     d_likelihood_element    : dict
    #
    #     """
    #     d_likelihood_element = cls.defdic_decorr_func()
    #     for dataset_name, ind_dataset_name in match_datasets.items():
    #         d_likelihood_element["l_idx_simdata"].append(l_dataset_name.index(dataset_name))
    #         d_likelihood_element["l_datasetkwargs_req"].append(cls.l_required_datasetkwarg_keys)
    #         d_likelihood_element["l_inddataset_name"].append(ind_dataset_name)
    #         d_likelihood_element["l_inddatasetkwargs_req"].append(cls.l_required_inddatasetkwarg_keys)
    #     return d_likelihood_element

    @classmethod
    def defdic_decorr_func(cls):
        return {"l_idx_simdata": [],
                "l_datasetkwargs_req": [],
                "l_inddataset_name": [],
                "l_inddatasetkwargs_req": [],
                }

    @classmethod
    def apply_parametrisation(cls, decorr_model_config):
        """Apply the parametrisation for the decorrelation to an instrument model.

        This function is used by parametrisation_gravgroup.apply_instmodel_parametrisation.
        For now there is no parameters for this type of decorrelation

        Arguments
        ---------
        decorr_model_config    : dict
            Dictionary where the decorrelation configuration is stored for the model
        """
        raise NotImplementedError(f"You need to implement the function apply_parametrisation for the"
                                  f"likelihood decorrelation class {cls.__class__}."
                                  )
