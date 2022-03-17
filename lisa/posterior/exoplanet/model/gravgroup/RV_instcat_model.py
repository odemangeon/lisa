#!/usr/bin/python
# -*- coding:  utf-8 -*-
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
from logging import getLogger
from textwrap import dedent
from pprint import pformat

from .datasim_creator_rv import create_datasimulator_RV
from ..decorrelation_model.linear_decorrelation import LinearDecorrelation
from ...dataset_and_instrument.rv import RV_inst_cat
from ....core.model.core_instcat_model import Core_InstCat_Model
from ....core.dataset_and_instrument.manager_dataset_instrument import Manager_Inst_Dataset
from .....tools.miscellaneous import spacestring_like


## Logger object
logger = getLogger()

mgr_inst_dst = Manager_Inst_Dataset()
mgr_inst_dst.load_setup()


class RV_InstCat_Model(Core_InstCat_Model):
    """docstring for LC_InstCat_Model, interface class of GravGroup."""

    # Mandatory attributes for a sublass of Core_InstCat_Model
    __inst_cat__ = RV_inst_cat
    __has_instcat_paramfile__ = True
    __default_paramfile_path__ = "RV_param_file.py"
    __datasim_creator_name__ = "sim_RV"
    __decorrelation_models__ = [LinearDecorrelation]

    allowed_what2decorrelate_strs = ['add_2_totalrv', 'multiply_2_totalrv']

    ## List of available rv models, the 1st element is used as default
    _rv_models = ["radvel", ]  # ["radvel", "ajplanet"] Temporarily? remove ajplanet from the available rv_models

    def __init__(self, model_instance):
        super(RV_InstCat_Model, self).__init__(model_instance=model_instance)
        self.rv_model = {planet.get_name(): {"do": True,
                                             "model": "radvel"
                                             }
                         for planet in self.model_instance.planets.values()
                         }
        # Initialise the dictionary giving the RV zero point RV_references
        self.__RV_references = dict.fromkeys(model_instance.get_inst_names(inst_fullcat=RV_inst_cat), None)
        logger.debug("RV instruments names: {}".format(list(self.__RV_references.keys())))
        self.__RV_references["global"] = list(self.__RV_references.keys())[0]
        for key in self.__RV_references:
            if key != "global":
                self.__RV_references[key] = model_instance.get_instmodel_names(inst_name=key,
                                                                               inst_fullcat=RV_inst_cat)[0]

    @property
    def RV_references(self):
        return self.__RV_references

    @property
    def RV_globalref_instname(self):
        return self.__RV_references["global"]

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
        return create_datasimulator_RV(star=list(self.model_instance.stars.values())[0],
                                       planets=self.model_instance.planets,
                                       RV_globalref_instname=self.RV_globalref_instname,
                                       RV_instref_modnames=self.RV_references,
                                       RV_inst_db=self.model_instance.instruments[RV_inst_cat],
                                       rv_model=self.rv_model,
                                       decorrelation_config=self.decorrelation_config,
                                       dataset_db=self.model_instance.dataset_db,
                                       RVcat_model=self.model_instance.instcat_models[self.inst_cat],
                                       inst_models=inst_models, datasets=datasets,
                                       get_times_from_datasets=get_times_from_datasets
                                       )

    def create_instcat_paramfile(self, file_path):
        """Create a parameter file for the light-curve parametrisation.

        Arguments
        ---------
        file_path           : string
            Path to the param_file.
        model_instance      : Model instance
        """
        with open(file_path, 'w') as f:
            # Write the header
            f.write("#!/usr/bin/python\n# -*- coding:  utf-8 -*-\n")

            # Define the global structure of the file
            text_RV_param = """
            # Radial Velocity parametrisation file of {object_name}

            # Which model do you want to use for the rv keplerian ?
            keplerian_rv_model = {keprv_model}

            {text_general_decorrelation}
            """
            text_RV_param = dedent(text_RV_param)  # Remove undesired indentation

            # Create some of the easy content of the file
            tab_keprvmod = spacestring_like("keplerian_rv_model = ")

            # Fill the whole text_LC_param string
            text_RV_param = text_RV_param.format(object_name=self.model_instance.get_name(),
                                                 keprv_model=pformat(self.rv_model, compact=True).replace("\n", f"\n{tab_keprvmod}"),
                                                 text_general_decorrelation=self.create_text_paramfile_decorrelation(model_instance=self.model_instance)  # Comes from Core_InstCat_Model
                                                 )

            # Write the file
            f.write(text_RV_param)
        logger.info("Parameter file created at path: {}".format(file_path))
        self.paramfile_instcat = file_path

    def load_instcat_paramfile(self):
        """Load LC_param_file."""
        dico_config = self.read_RV_param_file()
        self.load_RV_config(dico_config)
        self.load_config_decorrelation(dico_config)

    def read_RV_param_file(self):
        """Read the content of the LC parameter file."""
        if self.isdefined_paramfile_instcat:
            with open(self.paramfile_instcat) as f:
                exec(f.read())
            dico = locals().copy()
            dico.pop("self")
            logger.debug("RV parameter file read.\nContent of the parameter file: {}"
                         "".format(dico.keys()))
            return dico
        else:
            raise IOError("Impossible to read RV parameter file: {}".format(self.paramfile4instcat[self.__inst_cat__]))

    def load_RV_config(self, dico_config):
        """load the configuration specified by the dictionnary"""
        # Check the rv_model
        dict_name = "keplerian_rv_model"
        if dict_name not in dico_config:
            raise ValueError(f"In file {self.paramfile_instcat}: Missing {dict_name} dictionary.")
        dico_model = dico_config[dict_name]
        for planet in self.model_instance.planets.values():
            planet_name = planet.get_name()
            # Check that there is a key for each planet
            if planet_name not in dico_model:
                raise ValueError(f"In file {self.paramfile_instcat}: Dictionary {dict_name} is missing a key for planet {planet_name}.")
            # Check that there is a 'do' key with a boolean value for each planet dictionary
            if 'do' not in dico_model[planet_name]:
                raise ValueError(f"In file {self.paramfile_instcat}: Dictionary {dict_name}[{planet_name}] is missing the 'do' key.")
            else:
                if not(isinstance(dico_model[planet_name]["do"], bool)):
                    raise ValueError(f"In file {self.paramfile_instcat}: {dict_name}[{planet_name}]['do'] has to be a boolean.")
            if dico_model[planet_name]['do']:
                # Check that there is a key each planet dictionary
                key = "model"
                if key not in dico_model[planet_name]:
                    raise ValueError(f"In file {self.paramfile_instcat}: Dictionary {dict_name}[{planet_name}] is missing the '{key}' key.")
                # Check and load the rv_model dictionary
                # TODO?: Make checks on the content of each model in 'model_definitions'
                self.rv_model[planet_name] = dico_config["keplerian_rv_model"][planet_name]

    def set_RV_globalref_instname(self, inst_name):
        self.__RV_references["global"] = inst_name

    def get_RVref4inst_modname(self, inst_name):
        return self.__RV_references[inst_name]

    def set_RVref4inst_modname(self, inst_name, inst_model_name):
        self.__RV_references[inst_name] = inst_model_name

    def create_text4paramfile_decorrmodels(self, instmod_obj, tab):
        """This function creates the text for the decorrelation of an instrument model object.

        Arguments
        ---------
        instmod_obj : Instrument_Model instance
            Instrument model object for which you want to create the text to configure the decorrelation
        tab         : str
            White spaces giving the tabulation to use

        Returns
        -------
        text_instmod_decorr_models_content  : str
            Text to configure the decorrelation for instmod_obj
        """
        tab_what2decorrdict = spacestring_like("'what to decorrelate':  ")
        # template_decorrmethoddict = "{decorr_category}: " + "{" + "{dictdecorrcat_content}\n{tab}" + "}"
        dictmodelpart_content = ""
        for modelpart2decor in self.allowed_what2decorrelate_strs:
            if len(dictmodelpart_content) > 0:
                dictmodelpart_content += f"\n{tab + tab_what2decorrdict}"
            modelpart_1stline = f"'{modelpart2decor}': " + "{"
            tab_modelpart = spacestring_like(modelpart_1stline)
            dictmodelpart_content += modelpart_1stline
            dictdecorrcat_content = ""
            for decorr_model_name in self.available_decorrelationmodel_names:
                if len(dictdecorrcat_content) > 0:
                    dictdecorrcat_content += f"\n{tab + tab_what2decorrdict + tab_modelpart}"
                decorr_model = self.get_DecorrModel(decorrmodel_cat=decorr_model_name)
                decorr_model_current_config_dict = self.decorrelation_config.get(instmod_obj.full_name, {}).get(decorr_model_name, {})
                dictdecorrcat_content += decorr_model.create_text_decorr_paramfile(inst_mod_obj=instmod_obj,
                                                                                   decorrelation_config_inst=decorr_model_current_config_dict,
                                                                                   tab=tab + tab_what2decorrdict + tab_modelpart)
            dictmodelpart_content += dictdecorrcat_content + f"\n{tab + tab_what2decorrdict + tab_modelpart}" + "},"

        return "'what to decorrelate': {" + f"{dictmodelpart_content}\n{tab + tab_what2decorrdict}" + "},"

    def load_config_decorrelation(self, dico_config):
        """Load the dict in any inst_cat specific param_file about to choosen the decorrelation models
        for each dataset.

        This function should be used in load_instcat_paramfile to load the configuration of the decorrelation
        models.

        Arguments
        ---------
        dico_config : dict
            Dictionary which contain the content of the inst_cat specific param_file
        """
        # TODO: Check that the decorrelation dictionary has on entry per instrument model object of
        # the current instrument category
        for instmod_obj_name, decorr_dict_instmod in dico_config.get(self._decorr_dict_name, {}).items():
            instmod_name_info = mgr_inst_dst.interpret_instmod_fullname(instmod_fullname=instmod_obj_name, raise_error=True)
            instmod_obj = self.model_instance.get_instmodel_objs(inst_fullcat=instmod_name_info["inst_fullcategory"],
                                                                 inst_model=instmod_name_info["inst_model"],
                                                                 inst_name=instmod_name_info["inst_name"])[0]
            # Check that the dictionary of each instrument model object has a "do" key
            assert "do" in decorr_dict_instmod.keys()
            if instmod_obj_name not in self.decorrelation_config:
                self.decorrelation_config[instmod_obj_name] = {}
            self.decorrelation_config[instmod_obj_name]["do"] = decorr_dict_instmod["do"]
            # Check that the "what to decorrelate" is in the dictionary
            if "what to decorrelate" not in decorr_dict_instmod:
                raise ValueError(f"The dictionary for the configuration of the linear decorrelation of {instmod_obj_name}"
                                 f" must include the key 'what to decorrelate'.")
            if 'what to decorrelate' not in self.decorrelation_config[instmod_obj_name]:
                self.decorrelation_config[instmod_obj_name]['what to decorrelate'] = {}
            for model_part, decorr_dict_instmod_modpart in decorr_dict_instmod['what to decorrelate'].items():
                # Check that the "what to decorrelate" value is valid
                if model_part not in self.allowed_what2decorrelate_strs:
                    raise ValueError(f"Keys of 'what to decorrelate' for the configuration of the {instmod_obj_name}"
                                     f" must be in {self.allowed_what2decorrelate_strs}.")
                if model_part not in self.decorrelation_config[instmod_obj_name]['what to decorrelate']:
                    self.decorrelation_config[instmod_obj_name]['what to decorrelate'][model_part] = {}
                for decorr_mod in self.decorrelation_models:
                    # Check that the dictionary of each instrument model object has a key for each decorrelation models
                    assert decorr_mod.category in decorr_dict_instmod_modpart.keys()
                    decorr_dict_instmod_modpart_decorrmod = decorr_dict_instmod_modpart[decorr_mod.category]
                    if decorr_mod.category not in self.decorrelation_config[instmod_obj_name]['what to decorrelate']:
                        self.decorrelation_config[instmod_obj_name]['what to decorrelate'][model_part][decorr_mod.category] = {}
                    decorr_mod.load_text_decorr_paramfile(inst_mod_obj=instmod_obj,
                                                          decorrelation_config_inst_decorr_paramfile=decorr_dict_instmod_modpart_decorrmod,
                                                          decorrelation_config_inst_decorr=self.decorrelation_config[instmod_obj_name]['what to decorrelate'][model_part][decorr_mod.category],
                                                          allowed_what2decorrelate_strs=self.allowed_what2decorrelate_strs
                                                          )

    def apply_instmod_parametrisation(self, inst_mod_obj):
        """Apply the parametrisation to an instrument model object.

        This parametrisation should not include the decorrelation

        Arguments
        ---------
        inst_mod_obj : Instrument_Model
            Instrument_Model instance providing the instrument model to be parametrised.
        """
        # instrumental variation parametrisation
        # For I have not implemented how the use can define inst_var for RVs but once it's done
        # It only needs to be provided here
        inst_mod_obj.init_inst_var_parameters(with_inst_var=False, inst_var_order=1)

    def apply_instmod_parametrisation_decorrelation(self, inst_mod_obj):
        """Apply the parametrisation for the decorrelation to an instrument model object.

        Arguments
        ---------
        inst_mod_obj : Instrument_Model
            Instrument_Model instance providing the instrument model to be parametrised.
        """
        if self.do_decorrelate_instmod(inst_mod_obj=inst_mod_obj):
            for model_part in self.decorrelation_config[inst_mod_obj.full_name]['what to decorrelate'].keys():
                for DecorModel in self.decorrelation_models:
                    DecorModel.apply_parametrisation(inst_mod_obj=inst_mod_obj,
                                                     model_part=model_part,
                                                     decorrelation_config_inst_decorr=self.decorrelation_config[inst_mod_obj.full_name]['what to decorrelate'][model_part][DecorModel.category])
