#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
LC_instcat_model module.

The objective of this package is to provides the LC_InstCat_Model class to handle the LC instrument class
for the GravGroup class

@DONE:
    -

@TODO:
    - self.stars is used here but it's only define in GravGroup that makes the code a bit difficult to
    understand and follow. Is there a solution ? same thing for self.paramfile4instcat and self._ext_plonly
"""
from logging import getLogger
from textwrap import dedent
from collections import OrderedDict

from .supersamp_exptime import SuperSampExpTimeAttr, _supersamp_key, _exptime_key
from .limb_darkening import Manager_LD, CoreLD
from .datasim_creator_lc import create_datasimulator_LC
from ...dataset_and_instrument.lc import LC_inst_cat
from ....core.dataset_and_instrument.manager_dataset_instrument import Manager_Inst_Dataset
from ....core.model.core_instcat_model import Core_InstCat_Model
from .....tools.miscellaneous import spacestring_like
from ..decorrelation_model.linear_decorrelation import LinearDecorrelation_LC

## Logger object
logger = getLogger()

mgr_LD = Manager_LD()
mgr_inst_dst = Manager_Inst_Dataset()
mgr_inst_dst.load_setup()


class LC_InstCat_Model(Core_InstCat_Model, SuperSampExpTimeAttr):
    """docstring for LC_InstCat_Model, interface class of GravGroup."""

    # Mandatory attributes for a sublass of Core_InstCat_Model
    __inst_cat__ = LC_inst_cat
    __has_instcat_paramfile__ = True
    __default_paramfile_path__ = "LC_param_file.py"
    __datasim_creator_name__ = "sim_LC"
    __decorrelation_models__ = [LinearDecorrelation_LC]

    allowed_what2decorrelate_strs = ['stellarflux', ]

    ## List of available transit models, the 1st element is used as default
    _transit_models = ["batman", ]  # ["batman", "pytransit-MandelAgol", "pytransit-Gimenez"] Temporarily? remove pytransit from the available transit_models

    ## List of available phase curve models, the 1st element is used as default
    _phasecurve_models = ["spiderman", ]  # ["spiderman", ]

    ## List of available occultation models, the 1st element is used as default
    _occultation_models = ["spiderman", ]  # ["spiderman", ]

    ## List of available limb-darkening models for each lc_models, the 1st element is used as
    ## default
    _ld_models = {"batman": ["quadratic", "nonlinear", "exponential", "logarithmic", "squareroot",
                             "linear", "uniform", "custom"],
                  "pytransit-MandelAgol": ["quadratic", "linear", "uniform"],
                  "pytransit-Gimenez": ["quadratic", "linear", "uniform"]
                  }

    # Strings used in the inst_cat param_file
    __ld_dict_name = "LDs"
    __ldmod_dict_name = "LD_models"

    _key_inst_variable_LC_models = 'instrument_variable'
    _key_allinst_dict_LC_models = 'all_instruments'
    _key_instspecific_dict_LC_models = 'instrument_specific'

    __supersamp_dict = "SuperSamps"

    def __init__(self, model_instance):
        super(LC_InstCat_Model, self).__init__(model_instance=model_instance)
        self.transit_model = {"do": True,
                              self._key_inst_variable_LC_models: False,
                              self._key_allinst_dict_LC_models: {'model': 'batman'},
                              self._key_instspecific_dict_LC_models: {}}
        self.phasecurve_model = {"do": False,
                                 self._key_inst_variable_LC_models: False,
                                 self._key_allinst_dict_LC_models: [{"model": "spiderman",
                                                                     "args": {"ModelParams_kwargs": {"brightness_model": "zhang", },
                                                                              "attributes": {}
                                                                              }
                                                                     },
                                                                    ],
                                 self._key_instspecific_dict_LC_models: {}}
        self.occultation_model = {"do": False,
                                  self._key_inst_variable_LC_models: False,
                                  self._key_allinst_dict_LC_models: [{'model': 'batman'}, ],
                                  self._key_instspecific_dict_LC_models: {}}
        self.__ldmodel4instmodfname = OrderedDict()  # Limb darkening model for each instrument
        SuperSampExpTimeAttr.__init__(self)
        # self.spiderman_model = {"brightness_model": "zhang"}
        # instrument
        # Limb darkening model
        # self.ld_model = ld_model
        # TODO: Create the LC_param_file and create a function to load its content and build the
        # Associated LD param containers.

    @property
    def ldmodel4instmodfname(self):
        """Return the dictionary giving the LD object to use for each LC instrument model."""
        return self.__ldmodel4instmodfname

    @property
    def LDs(self):
        return self.model_instance.paramcontainers[CoreLD.category]

    def datasim_creator(self, inst_models, datasets, get_times_from_datasets):
        """
        Arguments
        ---------
        get_times_from_datasets  : bool
            If True the times at which the LC model is computed is taken from the datasets.
            Else it is an input of the datasimulator function produced.
        """
        return create_datasimulator_LC(star=list(self.model_instance.stars.values())[0],
                                       planets=self.model_instance.planets,
                                       key_whole=self.model_instance.key_whole,
                                       key_param=self.model_instance.key_param,
                                       key_mand_kwargs=self.model_instance.key_mand_kwargs,
                                       key_opt_kwargs=self.model_instance.key_opt_kwargs,
                                       ext_plonly=self.model_instance._ext_plonly,
                                       parametrisation=self.model_instance.parametrisation,
                                       ldmodel4instmodfname=self.ldmodel4instmodfname,
                                       LDs=self.LDs,
                                       transit_model=self.transit_model,
                                       SSE4instmodfname=self.SSE4instmodfname,
                                       phasecurve_model=self.phasecurve_model,
                                       inst_models=inst_models,
                                       datasets=datasets,
                                       get_times_from_datasets=get_times_from_datasets,
                                       decorrelation_config=self.decorrelation_config,
                                       dataset_db=self.model_instance.dataset_db,
                                       LCcat_model=self.model_instance.instcat_models[self.inst_cat])

    def create_instcat_paramfile(self, file_path):
        """Create a parameter file for the light-curve parametrisation.

        Arguments
        ---------
        file_path           : string
            Path to the param_file.
        """
        with open(file_path, 'w') as f:
            # Write the header
            f.write("#!/usr/bin/python\n# -*- coding:  utf-8 -*-\n")

            # Define the global structure of the file
            text_LC_param = """
            # Light-curve parametrisation file of {object_name}

            # Which model do you want to use for the transit ?
            transit_model = {{'do': True,
                             '{key_inst_variable_LC_models}': False,
                             '{key_allinst_dict_LC_models}': {{'model': 'batman'}},
                             '{key_instspecific_dict_LC_models}': {{{instspec_trmodel_dict}
            {tab_trmod}}}
                             }}

            # Limb-darkening.
            # Associate LC instrument models with LD param containers.
            # Available limb-darkening models are:
            # {available_lds}
            {ld_dict_name} = {{{star_ld_dict}
            {tab_ld}}}

            # Supersampling and exposure_time
            {supersamp_dict} = {{{inst_ss_dict}
            {tab_ss}}}

            # Which model do you want to use for the phase curve ?
            phasecurve_model = {{'do': False,
                                '{key_inst_variable_LC_models}': False,
                                '{key_allinst_dict_LC_models}': [{{"model": "spiderman", "args": {{"ModelParams_kwargs": {{"brightness_model": "zhang", }},
                                                                                                "attributes": {{}}
                                                                                                }}
                                                                 }},
                                                                ],
                                '{key_instspecific_dict_LC_models}': {{{instspec_pcmodel_dict}
            {tab_pcmod}}}
                                }}


            # Which model do you want to use for the occultation ?
            # WARNING: Some phasecurve models already include the occultation. No need to add it twice in these cases.
            occultation_model = {{'do': False,
                                 '{key_inst_variable_LC_models}': False,
                                 '{key_allinst_dict_LC_models}': [{{"model": "batman", "args": {{}}}},
                                                                ],
                                 '{key_instspecific_dict_LC_models}': {{{instspec_occmodel_dict}
            {tab_occmod}}}
                                 }}
            {text_general_decorrelation}
            """
            text_LC_param = dedent(text_LC_param)  # Remove undesired indentation

            # Create some of the easy content of the file
            available_lds = self._ld_models["batman"]  # For now I am providing the ld models available with batman
            tab_ld = spacestring_like(f"{self.__ld_dict_name} =  ")
            tab_ss = spacestring_like(f"{self.__supersamp_dict} =  ")
            tab_trmod = spacestring_like(f"transit_model =  '{self._key_instspecific_dict_LC_models}':  ")
            tab_pcmod = spacestring_like(f"phasecurve_model =  '{self._key_instspecific_dict_LC_models}':  ")
            tab_occmod = spacestring_like(f"occultation_model =  '{self._key_instspecific_dict_LC_models}':  ")

            # Create the structure of the star_ld_dict
            star_ld_dict = """
            '{star_name}': {{{inst_ld_dict}

            {tab_star_ld}'{LD_dict_name}': {{{LDmodels}}}
            {tab_star_ld}}}
            """
            star_ld_dict = dedent(star_ld_dict)[1:-1]  # Remove undesired indentation

            # Create some of the easy content of the star_ld_dict
            default_parcontname = 'default'
            star = self.model_instance.stars[list(self.model_instance.stars.keys())[0]]
            tab_star_ld = tab_ld + spacestring_like(f"'{star.get_name()}':  ")  # I put an extra space instead of the curly braket because the color algorithm of atom
            LDmodels = (f"'{default_parcontname}': 'quadratic'")

            # Create the content related to LC instruments (inst_ld_dict and inst_ss_dict)
            inst_ld_dict = ""
            inst_ss_dict = ""
            inst_tr_dict = ""
            inst_pc_dict = ""
            inst_occ_dict = ""
            ss_dict = "'{instmod_fullname}': {{'{supersamp_key}': {default_supersamp}, '{exptime_key}': {default_exptime}}},"
            ld_dict = "'{instmod_fullname}': '{def_LDparcont}',"
            tr_dict = "'{instmod_fullname}': '{def_trmodel}'"
            pc_dict = "'{instmod_fullname}': '{def_pcmodel}'"
            occ_dict = "'{instmod_fullname}': '{def_occmodel}'"
            default_supersamp = 1
            default_exptime = 0.02043402778  # Kepler long cadence exposure time in days
            first_instmodel = True
            default_tr_model = self._key_allinst_dict_LC_models
            default_pc_model = self._key_allinst_dict_LC_models
            default_occ_model = self._key_allinst_dict_LC_models
            for instmod_obj in self.model_instance.get_instmodel_objs(inst_fullcat=self.__inst_cat__):
                ld_tab = ""
                ss_tab = ""
                tr_tab = ""
                pc_tab = ""
                occ_tab = ""
                if not(first_instmodel):
                    ld_tab = "\n{tab_star_ld}"
                    ss_tab = "\n{tab_ss}"
                    tr_tab = "\n{tab_trmod}"
                    pc_tab = "\n{tab_pcmod}"
                    occ_tab = "\n{tab_occmod}"
                else:
                    first_instmodel = False
                inst_ld_dict += (ld_tab +
                                 ld_dict).format(tab_star_ld=tab_star_ld,
                                                 instmod_fullname=instmod_obj.get_name(include_prefix=True, code_version=True, recursive=True),
                                                 def_LDparcont=default_parcontname)
                inst_ss_dict += (ss_tab +
                                 ss_dict).format(tab_ss=tab_ss,
                                                 instmod_fullname=instmod_obj.get_name(include_prefix=True, code_version=True, recursive=True),
                                                 supersamp_key=_supersamp_key,
                                                 default_supersamp=default_supersamp,
                                                 exptime_key=_exptime_key,
                                                 default_exptime=default_exptime)
                inst_tr_dict += (tr_tab +
                                 tr_dict).format(tab_trmod=tab_trmod,
                                                 instmod_fullname=instmod_obj.get_name(include_prefix=True, code_version=True, recursive=True),
                                                 def_trmodel=default_tr_model)
                inst_pc_dict += (pc_tab +
                                 pc_dict).format(tab_pcmod=tab_pcmod,
                                                 instmod_fullname=instmod_obj.get_name(include_prefix=True, code_version=True, recursive=True),
                                                 def_pcmodel=default_pc_model)
                inst_occ_dict += (occ_tab +
                                  occ_dict).format(tab_occmod=tab_occmod,
                                                   instmod_fullname=instmod_obj.get_name(include_prefix=True, code_version=True, recursive=True),
                                                   def_occmodel=default_occ_model)

            # Fill the structures of star_ld_dict
            star_ld_dict = star_ld_dict.format(star_name=star.get_name(), inst_ld_dict=inst_ld_dict,
                                               tab_star_ld=tab_star_ld, LDmodels=LDmodels,
                                               LD_dict_name=self.__ldmod_dict_name)

            # Fill the whole text_LC_param string
            text_LC_param = text_LC_param.format(object_name=self.model_instance.get_name(),
                                                 tab_trmod=tab_trmod,
                                                 instspec_trmodel_dict=inst_tr_dict,
                                                 key_inst_variable_LC_models=self._key_inst_variable_LC_models,
                                                 key_allinst_dict_LC_models=self._key_allinst_dict_LC_models,
                                                 key_instspecific_dict_LC_models=self._key_instspecific_dict_LC_models,
                                                 available_lds=available_lds,
                                                 ld_dict_name=self.__ld_dict_name,
                                                 tab_ld=tab_ld, star_ld_dict=star_ld_dict,
                                                 supersamp_dict=self.__supersamp_dict,
                                                 tab_ss=tab_ss, inst_ss_dict=inst_ss_dict,
                                                 tab_pcmod=tab_pcmod, tab_occmod=tab_occmod,
                                                 instspec_pcmodel_dict=inst_pc_dict,
                                                 instspec_occmodel_dict=inst_occ_dict,
                                                 text_general_decorrelation=self.create_text_paramfile_decorrelation(model_instance=self.model_instance)  # Comes from Core_InstCat_Model
                                                 )

            # Write the file
            f.write(text_LC_param)
        logger.info("Parameter file created at path: {}".format(file_path))
        self.paramfile_instcat = file_path

    def load_instcat_paramfile(self):
        """Load LC_param_file."""
        dico_config = self.read_LC_param_file()
        self.load_LC_config(dico_config)
        self.load_config_decorrelation(dico_config)

    def read_LC_param_file(self):
        """Read the content of the LC parameter file."""
        if self.isdefined_paramfile_instcat:
            with open(self.paramfile_instcat) as f:
                exec(f.read())
            dico = locals().copy()
            dico.pop("self")
            logger.debug("LC parameter file read.\nContent of the parameter file: {}"
                         "".format(dico.keys()))
            return dico
        else:
            raise IOError("Impossible to read LC parameter file: {}".format(self.paramfile_instcat))

    def load_LC_config(self, dico_config):
        """load the configuration specified by the dictionnary"""
        # Check and load the content of the LDs and Supersamps dict
        for star in self.model_instance.stars.values():
            star = self.model_instance.stars[list(self.model_instance.stars.keys())[0]]
            LD_models = dico_config[self.__ld_dict_name][star.code_name][self.__ldmod_dict_name]
            l_LC_instmod_name = list(dico_config[self.__ld_dict_name][star.code_name].keys())
            l_LC_instmod_name.remove(self.__ldmod_dict_name)
            for instmod_name in l_LC_instmod_name:
                ld_name = dico_config[self.__ld_dict_name][star.code_name][instmod_name]
                if instmod_name not in self.ldmodel4instmodfname:
                    self.ldmodel4instmodfname[instmod_name] = {}
                self.ldmodel4instmodfname[instmod_name][star.code_name] = ld_name
            for ld_name, ld_type in LD_models.items():
                # Create the LD paramcontainer with
                self.add_a_LD(star=star, ld_type=ld_type, name=ld_name)
        supersamp_dict = dico_config[self.__supersamp_dict]
        for instmod_name, dico in supersamp_dict.items():
            self.SSE4instmodfname.add_instmodel_SSEdict(instmod_name, dico)
        # Check the transit_model, phasecurve_model and occultation_model
        # A big part of structure of these dictionary are the same where are going to check that
        l_key_modeldicts = ['do', self._key_inst_variable_LC_models, self._key_allinst_dict_LC_models, self._key_instspecific_dict_LC_models]
        l_dico_model_name = ["transit_model", "phasecurve_model", "occultation_model"]
        for dict_name in l_dico_model_name:
            if dict_name not in dico_config:
                raise ValueError(f"The file {self.paramfile_instcat} is missing the {dict_name} dictionary.")
            dico_model = dico_config[dict_name]
            if 'do' not in dico_model:
                raise ValueError(f"The file {self.paramfile_instcat}: The dictionary {dict_name} is missing the 'do' key.")
            if dico_model['do']:
                if not(set(l_key_modeldicts) == set(dico_model.keys())):
                    raise ValueError(f"In file {self.paramfile_instcat}: the keys of the {dict_name} dictionary have to be {l_key_modeldicts}.")
                if not(isinstance(dico_model[self._key_inst_variable_LC_models], bool)):
                    raise ValueError(f"In file {self.paramfile_instcat}: {dict_name}[{self._key_inst_variable_LC_models}] has to be a boolean.")
                if not(isinstance(dico_model[self._key_instspecific_dict_LC_models], dict)):
                    raise ValueError(f"In file {self.paramfile_instcat}: {dict_name}[{self._key_instspecific_dict_LC_models}] has to be a dict.")
        # Check and load the transit_model dictionary
        self.transit_model["do"] = dico_config["transit_model"]["do"]
        if dico_config["transit_model"]["do"]:
            transit_model = dico_config["transit_model"]
            # At the moment the code is not handling different transit model for different instruments
            if transit_model[self._key_inst_variable_LC_models]:
                raise NotImplementedError("The use of different transit models per instrument is not currently implemented.")
            self.transit_model[self._key_inst_variable_LC_models] = False
            # Check and load the model for all instruments
            if "model" not in transit_model[self._key_allinst_dict_LC_models]:
                raise ValueError(f"In file {self.paramfile_instcat}: the transit_model[{self._key_allinst_dict_LC_models}] dictionary is missing the 'model' key.")
            if transit_model[self._key_allinst_dict_LC_models]['model'] not in self._transit_models:
                raise ValueError(f"In file {self.paramfile_instcat}: {transit_model[self._key_allinst_dict_LC_models]['model']} is not an available transit model.")
            self.transit_model[self._key_allinst_dict_LC_models]['model'] = transit_model[self._key_allinst_dict_LC_models]['model']
        else:
            raise NotImplementedError("At the moment you cannot not model the transit.")

        # Check and load the phasecurve_model dictionary
        self.phasecurve_model["do"] = dico_config["phasecurve_model"]["do"]
        if dico_config["phasecurve_model"]["do"]:
            phasecurve_model = dico_config["phasecurve_model"]
            # At the moment the code is not handling different phasecurve model for different instruments
            if phasecurve_model[self._key_inst_variable_LC_models]:
                raise NotImplementedError("The use of different phase curve models per instrument is not currently implemented.")
            self.phasecurve_model[self._key_inst_variable_LC_models] = False
            # At the moment the code is not handling multiple components for the phasecurve model
            if len(phasecurve_model[self._key_allinst_dict_LC_models]) != 1:
                raise NotImplementedError("The use of multiple phase curve components is not currently implemented there should be one and only one.")
            # Check and load the model for all instruments
            l_key_mandatory = ["model", "args"]
            if not(set(l_key_mandatory) == set(phasecurve_model[self._key_allinst_dict_LC_models][0].keys())):
                raise ValueError(f"In file {self.paramfile_instcat}: the keys of phasecurve_model[{self._key_allinst_dict_LC_models}][0] should be {l_key_mandatory}.")
            if phasecurve_model[self._key_allinst_dict_LC_models][0]['model'] not in self._phasecurve_models:
                raise ValueError(f"In file {self.paramfile_instcat}: {phasecurve_model[{self._key_allinst_dict_LC_models}][0]['model']} is not an available phasecurve model.")
            if phasecurve_model[self._key_allinst_dict_LC_models][0]['model'] == "spiderman":
                l_arg_mand_sp = ["ModelParams_kwargs", "attributes", "lightcurve_kwargs"]
                if not(set(l_arg_mand_sp) == set(phasecurve_model[self._key_allinst_dict_LC_models][0]['args'].keys())):
                    raise ValueError(f"In file {self.paramfile_instcat}: the keys of phasecurve_model[{self._key_allinst_dict_LC_models}][0]['args'] should be {l_arg_mand_sp}.")
                if not("brightness_model" in phasecurve_model[self._key_allinst_dict_LC_models][0]['args']['ModelParams_kwargs']):
                    raise ValueError(f"In file {self.paramfile_instcat}: the keys of phasecurve_model[{self._key_allinst_dict_LC_models}][0]['args']['ModelParams_kwargs'] is missing the 'brightness_model' key")
            else:
                raise NotImplementedError("Checking the content of the phasecurve dictionary for the phasecurve model {phasecurve_model[self._key_allinst_dict_LC_models][0]['model']} is not Implemented.")
            self.phasecurve_model[self._key_allinst_dict_LC_models][0] = phasecurve_model[self._key_allinst_dict_LC_models][0]

        # Check and load the occultation_model dictionary
        if dico_config["occultation_model"]["do"]:
            raise NotImplementedError("The use of an occultation only model is not curretnly implemented.")

    def add_a_LD(self, star, ld_type, name, kwargs_getname_4_storename={"include_prefix": True, "code_version": True},
                 kwargs_getname_4_codename={"include_prefix": True, "code_version": True}):
        """Add a Planet in the GravGroup.

        :param Star star: Star instance the limb darkening refers to.
        :param str ld_type: Type of the limb darkening model.
        :param str name: Name of the limb darkening param container to be created.

        Arguments kwargs_getname_4_storename and kwargs_getname_4_codename are passed to a Core_LD.__init__
        method (see Core_LD.__init__ docstring for more info). Only the default values are
        modified.
        """
        LDparcont_class = mgr_LD.get_LD_parcont_subclass(ld_type)
        LD = LDparcont_class(star=star, name=name, kwargs_getname_4_storename=kwargs_getname_4_storename,
                             kwargs_getname_4_codename=kwargs_getname_4_codename)
        if self.model_instance.isavailable_paramcontainer(LD.store_name, category="LD"):
            raise ValueError("Names provided already exists ({}). LD cannot be added".format(LD.store_name))
        else:
            self.model_instance.add_a_paramcontainer(LD)

    def get_list_LD_parconts(self):
        return self.model_instance.paramcontainers[CoreLD.category].values()

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
                dictmodelpart_content += f"\n'{tab + tab_what2decorrdict}"
            modelpart_1stline = f"'{modelpart2decor}': " + "{"
            tab_modelpart = spacestring_like(modelpart_1stline)
            dictmodelpart_content += modelpart_1stline
            dictdecorrcat_content = ""
            for decorr_model_name in self.available_decorrelationmodel_names:
                if len(dictdecorrcat_content) > 0:
                    dictdecorrcat_content += f"\n'{tab + tab_what2decorrdict + tab_modelpart}"
                decorr_model = self.get_DecorrModel(decorrmodel_cat=decorr_model_name)
                decorr_model_current_config_dict = self.decorrelation_config.get(instmod_obj.full_name, {}).get(decorr_model_name, {})
                dictdecorrcat_content += decorr_model.create_text_decorr_paramfile(inst_mod_obj=instmod_obj,
                                                                                   decorrelation_config_inst=decorr_model_current_config_dict,
                                                                                   tab=tab + tab_what2decorrdict + tab_modelpart)
            dictmodelpart_content += dictdecorrcat_content + f"\n{tab + tab_what2decorrdict + tab_modelpart}" + "}"

        return "'what to decorrelate': {" + f"{dictmodelpart_content}\n{tab + tab_what2decorrdict}" + "}"

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
        # OOT variation parametrisation
        inst_mod_obj.init_OOT_var_parameters(with_OOT_var=self.model_instance.parametrisation_kwargs.get("with_OOT_var", False),
                                             OOT_var_order=self.model_instance.parametrisation_kwargs.get("OOT_var_order", None))

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
