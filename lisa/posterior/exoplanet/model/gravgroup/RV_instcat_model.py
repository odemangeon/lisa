"""
RV_instcat_model module.

The objective of this package is to provides the RV_InstCat_Model class to handle the RV instrument class
for the GravGroup class.

@DONE:
    -

@TODO:
    - self.stars is used here but it's only define in GravGroup that makes the code a bit difficult to
    understand and follow. Is there a solution ? same thing for self.paramfile4instcat
"""
from loguru import logger
from textwrap import dedent
from pprint import pformat
# from os.path import basename
# import os

from .planetstarmodel_parametrisation import RVKeplerianModels
from .datasim_creator_rv import create_datasimulator_RV
from ..decorrelation.linear_decorrelation import LinearDecorrelation
from ...dataset_and_instrument.rv import RV_inst_cat
from ...likelihood.decorrelation.spline_decorrelation import SplineDecorrelation
from ...likelihood.decorrelation.bispline_decorrelation import BiSplineDecorrelation
from ....core.model.core_instcat_model import Core_InstCat_Model
from ....core.dataset_and_instrument.manager_dataset_instrument import Manager_Inst_Dataset
from .....tools.miscellaneous import spacestring_like


mgr_inst_dst = Manager_Inst_Dataset()
mgr_inst_dst.load_setup()


class RV_InstCat_Model(Core_InstCat_Model):
    """docstring for LC_InstCat_Model, interface class of GravGroup."""

    # Mandatory attributes for a sublass of Core_InstCat_Model
    __inst_cat__ = RV_inst_cat
    __datasim_creator_name__ = "sim_RV"
    __l_decorrelation_class__ = [LinearDecorrelation, SplineDecorrelation, BiSplineDecorrelation]

    allowed_what2decorrelate_strs = ['add_2_totalrv', 'multiply_2_totalrv']

    ## List of available rv models, the 1st element is used as default
    _rv_models = ["radvel", ]  # ["radvel", "ajplanet"] Temporarily? remove ajplanet from the available rv_models

    def __init__(self, model_instance, run_folder, config_file):
        super(RV_InstCat_Model, self).__init__(model_instance=model_instance, run_folder=run_folder, config_file=config_file)
        self.keplerian_rv_model = RVKeplerianModels(l_planet=[planet for planet in self.model_instance.planets.values()],
                                                    host_star=self.model_instance.stars[list(self.model_instance.stars.keys())[0]],
                                                    orbital_models=self.model_instance.orbital_model
                                                    )
        # Set the dictionaries for the polynomial models
        for star in self.model_instance.stars.values():
            star.set_dico_config_polymodel(inst_cat=self.inst_cat, dico_config={'do': True})
        for ii, instmod_obj in enumerate(self.model_instance.get_instmodel_objs(inst_fullcat=self.__inst_cat__)):
            if ii == 0:
                dico_config = {'do': False}
            else:
                dico_config = {'do': True}
            instmod_obj.set_dico_config_polymodel(dico_config=dico_config)  # Defined in lisa.posterior.exoplanet.dataset_and_instrument.rv.Instrument_RV and accessed through lisa.posterior.core.dataset_and_instrument.instrument.Instrument_Model.__getattr__

    def _init_decorrelation_model_config(self):
        # Get list of inst model full name for the inst cat
        l_instcat_instmod = self.model_instance.get_instmodel_objs(inst_fullcat=self.__inst_cat__)
        for inst_mod_obj in l_instcat_instmod:
            self.decorrelation_model_config[inst_mod_obj.full_name] = {"do": False, "what to decorrelate": {}}
            for model_part in self.allowed_what2decorrelate_strs:
                self.decorrelation_model_config[inst_mod_obj.full_name]["what to decorrelate"][model_part] = {}
                for decorr_model_cat in self.l_decorrelation_model_category:
                    self.decorrelation_model_config[inst_mod_obj.full_name]["what to decorrelate"][model_part][decorr_model_cat] = {}

    ######################################
    ## Dealing with the configuration file
    ######################################

    def _configure_instcat_model(self):
        """Configure the inst cat model
        """
        super(RV_InstCat_Model, self)._configure_instcat_model()

        logger.info("Load keplerian rv model and instrument model configuration")
        self._load_config(config2load='rvinstcatmod')

    # Function that get the function required by ConfigFileAttr._load_config
    ########################################################################

    def _get_function_config(self, function_type, config2load):
        if function_type == 'add_default_config':
            if config2load == 'rvinstcatmod':
                return self.__add_default_config_rvinstcatmod
        elif function_type == 'check_config_exists':
            if config2load == 'rvinstcatmod':
                return self.__config_var_exist_rvinstcatmod
        elif function_type == 'load_config_content':
            if config2load == 'rvinstcatmod':
                return self.__load_config_var_content_rvinstcatmod
        return super(RV_InstCat_Model, self)._get_function_config(function_type=function_type, config2load=config2load)
    
    # Dealing with the configuration of the keplerian RV and instrumental models
    ############################################################################

    def __add_default_config_rvinstcatmod(self, file):
        """Add the default config for the parametrisation of the instrument categories

        This function is stored in Core_Model.get_function_config and used by Core_Model._load_config
        """
        text_RV_param = """

        # Keplerian RV model
        ####################
        keplerian_rv_model = {keprv_model}

        # Instrumental model for RV
        ###########################

        # Polynomial trend models for RV
        ################################
        polynomial_model_RV = {poly_models}
        """
        text_RV_param = dedent(text_RV_param)  # Remove undesired indentation

        # Create some of the easy content of the file
        tab_keprvmod = spacestring_like("keplerian_rv_model = ")
        tab_poly = spacestring_like("polynomial_model_RV = ")

        # Create the dictionary for the polynomial models
        dico_poly = {}
        for star_name, star in self.model_instance.stars.items():
            dico_poly[star_name] = star.get_dico_config_polymodel(inst_cat=self.inst_cat, notexist_ok=False)
        for instmod_obj in self.model_instance.get_instmodel_objs(inst_fullcat=self.__inst_cat__):
            dico_poly[instmod_obj.full_name] = instmod_obj.get_dico_config_polymodel(notexist_ok=False)  # Defined in lisa.posterior.exoplanet.dataset_and_instrument.rv.Instrument_RV and accessed through lisa.posterior.core.dataset_and_instrument.instrument.Instrument_Model.__getattr__

        # Fill the whole text_LC_param string
        text_RV_param = text_RV_param.format(object_name=self.model_instance.get_name(),
                                             keprv_model=pformat(self.keplerian_rv_model.dict2print, compact=True).replace("\n", f"\n{tab_keprvmod}"),
                                             poly_models=pformat(dico_poly, compact=True).replace("\n", f"\n{tab_poly}"),
                                             )

        file.write(text_RV_param)

    def __config_var_exist_rvinstcatmod(self, dico_config_file):
        """Check if the variable(s) required for the parametrisation of the instrument categories

        This function is stored in Core_Model.get_function_config and used by Core_Model._load_config
        """
        return all([var in dico_config_file for var in ['keplerian_rv_model', f'polynomial_model_{self.inst_cat}']])

    def __load_config_var_content_rvinstcatmod(self, dico_config_file):
        """Load the variable(s) required for the parametrisation of the instrument categories

        This function is stored in Core_Model.get_function_config and used by Core_Model._load_config
        """
        # Check the keplerian_rv_model
        l_dico_model_name = ["keplerian_rv_model", ]
        l_config_model_instance = [self.keplerian_rv_model, ]
        for dict_name, config_model_instance in zip(l_dico_model_name, l_config_model_instance):
            dico_model = dico_config_file[dict_name]
            config_model_instance.load_config(dico_config=dico_model)

        # Check and load the polynomial models
        # Check that all the keys in dico_config_file["polynomial_model_RV"] are valid (star namnes or LC instruments name)
        l_valid_keys = list(self.model_instance.stars.keys())
        for instmod_obj in self.model_instance.get_instmodel_objs(inst_fullcat=self.__inst_cat__):
            l_valid_keys.append(instmod_obj.full_name)
        if len(set(dico_config_file["polynomial_model_RV"].keys()) - set(l_valid_keys)) > 0:
            raise ValueError(f"Some keys of the polynomial_model_RV dictionary are not valid: {set(dico_config_file['polynomial_model_RV'].keys()) - set(l_valid_keys)}.\n"
                                f"Valid keys are star short names or RV instrument model full names ({l_valid_keys})")
        # Load polynomial model for star if provided.
        for star_name, star in self.model_instance.stars.items():
            if star_name in dico_config_file["polynomial_model_RV"]:
                star.set_dico_config_polymodel(inst_cat=self.inst_cat, dico_config=dico_config_file["polynomial_model_RV"][star_name])
        # Load polynomial model for RV instruments if provided.
        for instmod_obj in self.model_instance.get_instmodel_objs(inst_fullcat=self.__inst_cat__):
            if instmod_obj.full_name in dico_config_file["polynomial_model_RV"]:
                instmod_obj.set_dico_config_polymodel(dico_config=dico_config_file["polynomial_model_RV"][instmod_obj.full_name])  # Defined in lisa.posterior.exoplanet.dataset_and_instrument.rv.Instrument_RV and accessed through lisa.posterior.core.dataset_and_instrument.instrument.Instrument_Model.__getattr__
        
    #######################################
    ## Dealing with the data simulator file
    #######################################

    def datasim_creator(self, inst_models, datasets, get_times_from_datasets):
        """
        Arguments
        ---------
        inst_models : List of Instrument_Model instances
            List of intrument models corresponding to each datasets in datasets
        datasets    : List of IND_Dataset instances
            List of datasets
        get_times_from_datasets  : bool
            If True the times at which the LC model is computed is taken from the datasets.
            Else it is an input of the datasimulator function produced.
        """
        return create_datasimulator_RV(star=list(self.model_instance.stars.values())[0], planets=self.model_instance.planets,
                                       keplerian_rv_model=self.keplerian_rv_model, dataset_db=self.model_instance.dataset_db,
                                       RVcat_model=self, inst_models=inst_models, datasets=datasets,
                                       get_times_from_datasets=get_times_from_datasets
                                       )
    
    #################################
    ## Dealing with the decorrelation
    #################################
            
    def load_config_decorrelation_model(self, decorr_config):
        """Load the dict in any inst_cat specific param_file about to choosen the decorrelation models
        for each dataset.

        This function should be used in load_instcat_paramfile to load the configuration of the decorrelation
        models.

        Arguments
        ---------
        decorr_config : dict
            Dictionary which contain the content of the decorrelation configuration
        """
        # TODO: Check that the decorrelation dictionary has on entry per instrument model object of
        # the current instrument category
        for instmod_obj_name, decorr_dict_instmod in decorr_config.items():
            instmod_name_info = mgr_inst_dst.interpret_instmod_fullname(instmod_fullname=instmod_obj_name, raise_error=True)
            instmod_obj = self.model_instance.get_instmodel_objs(inst_fullcat=instmod_name_info["inst_fullcategory"],
                                                                 inst_model=instmod_name_info["inst_model"],
                                                                 inst_name=instmod_name_info["inst_name"])[0]
            # Check that the dictionary of each instrument model object has a "do" key
            assert "do" in decorr_dict_instmod.keys()
            if instmod_obj_name not in self.decorrelation_model_config:
                self.decorrelation_model_config[instmod_obj_name] = {}
            self.decorrelation_model_config[instmod_obj_name]["do"] = decorr_dict_instmod["do"]
            # Check that the "what to decorrelate" is in the dictionary
            if "what to decorrelate" not in decorr_dict_instmod:
                raise ValueError(f"The dictionary for the configuration of the linear decorrelation of {instmod_obj_name}"
                                 f" must include the key 'what to decorrelate'.")
            if 'what to decorrelate' not in self.decorrelation_model_config[instmod_obj_name]:
                self.decorrelation_model_config[instmod_obj_name]['what to decorrelate'] = {}
            for model_part, decorr_dict_instmod_modpart in decorr_dict_instmod['what to decorrelate'].items():
                # Check that the "what to decorrelate" value is valid
                if model_part not in self.allowed_what2decorrelate_strs:
                    raise ValueError(f"Keys of 'what to decorrelate' for the configuration of the {instmod_obj_name}"
                                     f" must be in {self.allowed_what2decorrelate_strs}.")
                if model_part not in self.decorrelation_model_config[instmod_obj_name]['what to decorrelate']:
                    self.decorrelation_model_config[instmod_obj_name]['what to decorrelate'][model_part] = {}
                for decorr_mod in self.l_decorrelation_model_class:
                    # Check that the dictionary of each instrument model object has a key for each decorrelation models
                    assert decorr_mod.category in decorr_dict_instmod_modpart.keys()
                    decorr_dict_instmod_modpart_decorrmod = decorr_dict_instmod_modpart[decorr_mod.category]
                    if decorr_mod.category not in self.decorrelation_model_config[instmod_obj_name]['what to decorrelate']:
                        self.decorrelation_model_config[instmod_obj_name]['what to decorrelate'][model_part][decorr_mod.category] = {}
                    decorr_mod.load_text_decorr_paramfile(inst_mod_obj=instmod_obj,
                                                          decorrelation_config_inst_decorr_paramfile=decorr_dict_instmod_modpart_decorrmod,
                                                          decorrelation_config_inst_decorr=self.decorrelation_model_config[instmod_obj_name]['what to decorrelate'][model_part][decorr_mod.category],
                                                          )

    def require_model_decorrelation(self, instmod_fullname):
        """True if any of the instrument models of the instrument category require model decorrelation

        Argument
        --------
        instmod_fullname    : str
            Intrument model full name

        Return
        ------
        require : bool
            True if the instrument model requires model decorelation
        """
        require = False
        if self.do_decorrelate_model_instmod(instmod_fullname=instmod_fullname):
            for model_part, dico_decor_model_part_config in self.decorrelation_model_config[instmod_fullname]['what to decorrelate'].items():
                for decor_cat, dico_decor_cat_config in dico_decor_model_part_config.items():
                    if len(dico_decor_cat_config) > 0:
                        require = True
                        break
        return require
    
    ####################################
    # Deadling with the parameterisation
    ####################################

    def set_parametrisation(self, **kwargs):
        """Set the parametrisation for the instrument category

        This method is called by Core_Parametrisation.set_instcat_parameterisation
        """
        # Apply the Core_InstCat_Model.set_parametrisation
        super(RV_InstCat_Model, self).set_parametrisation()

        # Apply the parametrisation to the star and planets parameters
        self.set_star_planet_parametrisation()

    def set_star_planet_parametrisation(self):
        """Set the parametrisation to the star and planet objects.
        """
        ##################################################
        # Apply the parametrisation to the star parameters
        ##################################################
        # Systemic velocity (RVs)
        for star in self.model_instance.stars.values():
            star.set_polymodel_parametrisation(inst_cat=RV_inst_cat)

        ##############################################################################
        # Apply the parametrisation for the RV keplerian models
        ##############################################################################
        l_inst_fullcat = self.model_instance.instruments.get_inst_fullcat4inst_cat(inst_cat=RV_inst_cat)
        l_inst_model_fullname = []
        for inst_fullcat_i in l_inst_fullcat:
            for inst_model in self.model_instance.get_instmodel_objs(inst_fullcat=inst_fullcat_i):
                l_inst_model_fullname.append(inst_model.full_name)

        # Apply the parametrisation to the planets parameters
        for planet in self.model_instance.planets.values():
            planet_name = planet.get_name()
            # RV keplerian model
            if self.keplerian_rv_model.get_do(planet_name=planet_name):
                for inst_model_fullname in l_inst_model_fullname:
                    model = self.keplerian_rv_model.get_model(planet_name=planet_name)
                    model.create_parameters_and_set_main(inst_model_fullname=inst_model_fullname)

    def set_instmod_parametrisation_decorrelation_models(self, inst_mod_obj):
        """Apply the parametrisation for the decorrelation to an instrument model object.

        Arguments
        ---------
        inst_mod_obj : Instrument_Model
            Instrument_Model instance providing the instrument model to be parametrised.
        """
        # Decorrelation model
        if self.do_decorrelate_model_instmod(instmod_fullname=inst_mod_obj.full_name):
            for model_part in self.decorrelation_model_config[inst_mod_obj.full_name]['what to decorrelate'].keys():
                for DecorModel in self.l_decorrelation_model_class:
                    DecorModel.set_parametrisation(inst_mod_obj=inst_mod_obj,
                                                   model_part=model_part,
                                                   decorrelation_config_inst_decorr=self.decorrelation_model_config[inst_mod_obj.full_name]['what to decorrelate'][model_part][DecorModel.category])
