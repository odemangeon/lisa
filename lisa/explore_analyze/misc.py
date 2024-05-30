from __future__ import annotations
from loguru import logger
from os import getcwd, makedirs
from os.path import join
from copy import deepcopy, copy
from matplotlib.ticker import ScalarFormatter, FuncFormatter
from collections.abc import Sequence
from typing import Dict, List
from numpy import nan, float_, ndarray, isfinite
from numpy.typing import NDArray

from ..posterior.core.dataset_and_instrument.manager_dataset_instrument import Manager_Inst_Dataset
from ..posterior.core.model.core_model import Core_Model


### for the A&A article class
AandA_width = 3.543311946  # in inches = \hsize = 256.0748pt
AandA_full_width = 7.2712643025  # in inches = \hsize = 523.53 pt

default_figwidth = AandA_width
default_figheight_factor = 0.75

AandA_fontsize = 8

key_whole = Core_Model.key_whole

# Formatter for the Ticks major of the period axis
sf = ScalarFormatter(useOffset=False, useMathText=True)
sf.set_scientific(True)


def sci_not_str(x, pos):
    return f"${sf.format_data(x)}$"  # f"${sf._formatSciNotation('%1.10e' % x)}$"


fmt_sci_not = FuncFormatter(sci_not_str)

# managers
mgr_inst_dst = Manager_Inst_Dataset()


def get_def_output_folders(run_folder=None, output_folder=None):
    """Provides the default output folder to store the outputs of the exploration and analysis.

    This function creates the output folder tree if there are not already present in the run_folder.
    You can provide the location of the output folder tree two ways:
    - Provide run_folder, then the top output folder in the tree will be called outputs and will be
    located in the provided run_folder
    - Provide outputs_folder, and you provide both the location and the name of the top folder in the tree

    Arguments
    ---------
    run_folder      : str
        Path to run_folder where the output folder tree is expected to be. If None, the current working
        directory is used instead
    output_folder  : str
        Path to the main outputs folder tree you would like. If None, then run_folder is used

    Returns
    -------
    dict_output_folders  : dict
        Dictionary which gives the path to the output folders. The available keys are:
        pickles_explore, pickles_analyze, dats, plots, tables
    """
    if (run_folder is not None) and (output_folder is not None):
        raise ValueError("You cannot provide both run_folder and output_folder.")
    if output_folder is None:
        if run_folder is None:
            run_folder = getcwd()
        output_folder = join(run_folder, "outputs")
    makedirs(output_folder, exist_ok=True)

    dict_output_folders = {}
    dict_output_folders["log"] = join(output_folder, "log")
    makedirs(dict_output_folders["log"], exist_ok=True)
    exploration_output_folder = join(output_folder, "exploration")
    makedirs(exploration_output_folder, exist_ok=True)
    dict_output_folders["pickles_explore"] = join(exploration_output_folder, "pickles")
    makedirs(dict_output_folders["pickles_explore"], exist_ok=True)
    dict_output_folders["dats"] = join(exploration_output_folder, "dats")
    makedirs(dict_output_folders["dats"], exist_ok=True)
    chain_analysis_output_folder = join(output_folder, "chain_analysis")
    makedirs(chain_analysis_output_folder, exist_ok=True)
    dict_output_folders["plots"] = join(chain_analysis_output_folder, "plots")
    makedirs(dict_output_folders["plots"], exist_ok=True)
    dict_output_folders["pickles_analyze"] = join(chain_analysis_output_folder, "pickles")
    makedirs(dict_output_folders["pickles_analyze"], exist_ok=True)
    dict_output_folders["tables"] = join(chain_analysis_output_folder, "tables")
    makedirs(dict_output_folders["tables"], exist_ok=True)

    return dict_output_folders


def check_spec_by_column_or_row(spec_user, l_type_spec, spec_def, l_row_name=None, l_col_name=None):
    """Define the spec dictionary based on the user input by row or column name or all

    Arguments
    ---------
    specs_user  : None or type_spec or dict_of_type_spec
        If None, use the default behavior (specified by spec_def)
        If type_spec, this defines the spec of all axes
        If dict, the keys should be the name of the name of a row, a column or 'all' and the values
            should be instances of a type in l_type_spec which defines the spec for a column or a row.
    l_row_name  : list
        List of the names used for the rows
    l_col_name  : list
        List of the names used for the columns
    l_type_spec : list of type
        List of possible types for the spec
    spec_def    : type_spec
        Default value for the spec

    Return
    ------
    specs   : dict_of_type_spec
        keys are either 'all' or in l_row_name or in l_col_name and the values are instances of a type
        in l_type_spec
    """
    spec = {'all': spec_def}
    possible_top_keys = ['all', 'col', 'row', 'row,col']
   
    if spec_user is None:
        pass
    elif any([isinstance(spec_user, type_i) for type_i in l_type_spec]):
        spec['all'] = spec_user
    elif isinstance(spec_user, dict):
        for top_key in spec_user:
            if top_key not in possible_top_keys:
                raise ValueError(f"{top_key} is not in the list of possible top keys ({possible_top_keys}).")
            else:
                if top_key == 'all':
                    if any([isinstance(spec_user['all'], type_i) for type_i in l_type_spec]):
                        spec['all'] = spec_user['all']
                    else:
                        raise ValueError(f"The type of the content of 'all' ({type(spec_user['all'])}) is not within the valid types ({l_type_spec}).")
                else:
                    spec[top_key] = {}
                    if top_key == 'row':
                        possible_bottom_keys = l_row_name
                    elif top_key == 'col':
                        possible_bottom_keys = l_col_name
                    else:  # top_key == 'row,col'
                        possible_bottom_keys = []
                        for row_name in l_row_name:
                            for col_name in l_col_name:
                                possible_bottom_keys.append(f"{row_name},{col_name}")
                    if (possible_bottom_keys is None) or (len(possible_bottom_keys) == 0):
                        raise ValueError("Unable to build the list of possible bottom keys. This can happen if either l_row_name or l_col_name is None or empty.")
                    for bottom_key in spec_user[top_key]:
                        if bottom_key not in possible_bottom_keys:
                            raise ValueError(f"{bottom_key} is not in the list of possible key for {top_key} ({possible_bottom_keys}).")
                        if any([isinstance(spec_user[top_key][bottom_key], type_i) for type_i in l_type_spec]):
                            spec[top_key][bottom_key] = spec_user[top_key][bottom_key]
                        else:
                            raise ValueError(f"The type of the content of top_key '{top_key}' and bottom_key '{bottom_key}' ({type(spec[top_key][bottom_key])}) is not within the valid types ({l_type_spec}).")
    else:
        raise ValueError(f"spec_user should be a None or a {l_type_spec} or a dict with keys in {possible_top_keys}."
                         )
    return spec


def check_spec_data_or_resi(spec_user, l_type_spec, spec_def):
    """Define the spec dictionary based on the user input by row or column name or all

    Arguments
    ---------
    specs_user  : None or type_spec or dict_of_type_spec
        If None, use the default behavior (specified by spec_def)
        If type_spec, this defines the spec of all axes
        If dict, the keys should be the name of the name of a row, a column or 'all' and the values
            should be instances of a type in l_type_spec which defines the spec for a column or a row.
    l_type_spec : list of type
        List of possible types for the spec
    spec_def    : type_spec
        Default value for the spec

    Return
    ------
    specs   : dict_of_type_spec
        keys are either 'all' or in l_row_name or in l_col_name and the values are instances of a type
        in l_type_spec
    """
    l_keys = ['data', 'resi']
    if any([isinstance(spec_user, type_i) for type_i in l_type_spec]):
        spec_def = spec_user
    spec = {key: spec_def for key in l_keys}
    if (spec_user is None) or any([isinstance(spec_user, type_i) for type_i in l_type_spec]):
        pass
    elif isinstance(spec_user, dict) and all([key in l_keys for key in spec_user]):
        spec.update(spec_user)
    else:
        raise ValueError(f"spec_user should be a None or a {l_type_spec} or a dict with keys in {l_keys}"
                         f" and values of type {l_type_spec} which specify the spec for each in {l_keys},"
                         f" got {spec_user}"
                         )
    return spec


def check_spec_for_data_or_resi_by_column_or_row(spec_user, l_row_name, l_col_name, l_type_spec, spec_def):
    """Define the spec dictionary based on the user input by row or column name or all for the data and the resi axes

    Arguments
    ---------
    specs_user  : None or type_spec or dict_of_dict_type_spec
        If None, use the default behavior (specified by spec_def)
        If type_spec, this defines the spec of all axes for both the data and resi
        If dict_of_dict_type_spec, the first keys should be in ['data', 'resi'], the second keys should
            be the name of a row, a column or 'all' and the values should be instances of a type in
            l_type_spec which defines the spec for a column or a row.
    l_row_name  : list
        List of the names used for the rows
    l_col_name  : list
        List of the names used for the columns
    l_type_spec : list of type
        List of possible types for the spec
    spec_def    : dict_of_type_spec
        key are data or resi and value defines the default value for the spec

    Return
    ------
    specs   : dict_of_type_spec
        keys are either 'all' or in l_row_name or in l_col_name and the values are instances of a type
        in l_type_spec
    """
    l_top_keys = ['data', 'resi']
    spec_user_for_define_spec = {key: None for key in l_top_keys}
    if spec_user is None:
        pass
    elif any([isinstance(spec_user, type_i) for type_i in l_type_spec]):
        for key in l_top_keys:
            spec_def[key] = spec_user
    elif isinstance(spec_user, dict) and all([key in l_top_keys for key in spec_user]):
        spec_user_for_define_spec.update(spec_user)
    else:
        raise ValueError(f"spec_user should be a None or a {l_type_spec} or a dict with keys in {l_top_keys}.")
    spec = {}
    for key in ['data', 'resi']:
        spec[key] = check_spec_by_column_or_row(spec_user=spec_user_for_define_spec[key], l_row_name=l_row_name,
                                                l_col_name=l_col_name, l_type_spec=l_type_spec, spec_def=spec_def[key])
    return spec


def check_kwargs_by_column_and_row(kwargs_user, l_row_name, l_col_name, kwargs_def, kwargs_init=None):
    """Define the kwargs dictionary based on the user input by row and column name for each data axis

    Arguments
    ---------
    kwargs_user : dict
        kwargs define by the user when running the plotting function keys can be 'all' or in l_col_name or l_row_name.
    l_row_name  : list of key
        list of row key
    l_col_name  : list of key
        list of column key
    kwargs_def  : dict
        kwargs that will be attributed by default to all column and row at first. This will be altered by kwargs_init and then kwargs_user,
        if they are provided
    kwargs_init : dict
        kwargs to alter the kwargs of some column and rows after kwargs_def is applied. This served as a more complex default behavior than
        affecting kwargs_def to everything.

    Returns
    -------
    kwargs  :
    """
    kwargs = {col_name: {i_row: copy(kwargs_def) for i_row in l_row_name} for col_name in l_col_name}
    if kwargs_init is not None:
        for col_name in kwargs_init:
            for row_name in kwargs_init[col_name]:
                kwargs[col_name][row_name].update(kwargs_init[col_name][row_name])
    if kwargs_user is None:
        pass
    elif isinstance(kwargs_user, dict):
        if 'all' in kwargs_user:
            for col_name in kwargs:
                for i_row in kwargs[col_name]:
                    kwargs[col_name][i_row].update(kwargs_user['all'])
        for key in kwargs_user:
            if key == 'all':
                pass
            elif key in l_col_name:
                if all([key2 in l_row_name for key2 in kwargs_user[key]]):
                    for key2 in kwargs_user[key]:
                        kwargs[key][key2].update(kwargs_user[key][key2])
                else:
                    for key2 in l_row_name:
                        kwargs[key][key2].update(kwargs_user[key])
            elif key in l_row_name:
                if all([key2 in l_col_name for key2 in kwargs_user[key]]):
                    for key2 in kwargs_user[key]:
                        kwargs[key2][key].update(kwargs_user[key][key2])
                else:
                    for key2 in range(l_col_name):
                        kwargs[key2][key].update(kwargs_user[key])
            else:
                raise ValueError(f"{key} is not a valid key for kwargs. Should be 'all' or a name in"
                                 f"l_col_name or l_row_name.")
    return kwargs


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
        initial_set_models = models2plot.get_model2show(row_idx=i_row)
        for model_i in initial_set_models:
            if model_i.datasetname is None:
                model_i.datasetname = datasetnames4rowidx[i_row][0]
                if model_i.model not in l_model_1_per_row:
                    set_models_of_currentmodel = models2plot.get_model2show(row_idx=i_row, model=model_i.model)
                    datasetname_4_currentmodel = [model_j.datasetname for model_j in set_models_of_currentmodel]
                    for datasetname_i in datasetnames4rowidx[i_row][1:]:
                        if datasetname_i not in datasetname_4_currentmodel:
                            models2plot.add_model_2_plot(model=model_i.model, row_idx=i_row, datasetname=datasetname_i)
    return models2plot


def check_datasetnameformodel4row(datasetnameformodel4row, datasetnames4rowidx):
    """
    """
    datasetname4model4row_user = datasetnameformodel4row if datasetnameformodel4row is not None else {}
    datasetname4model4row = {i_row: datasetnames_i_row[0] for i_row, datasetnames_i_row in enumerate(datasetnames4rowidx)}
    datasetname4model4row.update(datasetname4model4row_user)
    return datasetname4model4row


def set_legend(ax, legend_kwargs, fontsize_def=AandA_fontsize):
    """
    """
    legend_kwargs_copy = legend_kwargs.copy()
    if legend_kwargs_copy['do']:
        legend_kwargs_copy.pop('do')
        if ('prop' not in legend_kwargs_copy) and ('fontsize' not in legend_kwargs_copy):
            legend_kwargs_copy['fontsize']  = fontsize_def
        ax.legend(**legend_kwargs_copy)


def define_x_or_y_lims(x_or_ylims, row_name, col_name):
    """
    """
    x_or_ylims_to_use = x_or_ylims['all']
    if not(("row" in x_or_ylims) and ("col" in x_or_ylims)):
        if "row" in x_or_ylims:
            if row_name in x_or_ylims["row"]:
                x_or_ylims_to_use = x_or_ylims["row"][row_name]
        elif "col" in x_or_ylims:
            if col_name in x_or_ylims["col"]:
                x_or_ylims_to_use = x_or_ylims["col"][col_name]
    else:
        raise ValueError("You cannot provide both 'row' and 'col' in x_or_ylims. You have to provide one or the other or 'row,col' or none of the 3.")
    if "row,col" in x_or_ylims:
        if f"{row_name},{col_name}" in x_or_ylims:
            x_or_ylims_to_use = x_or_ylims["row,col"][f"{row_name},{col_name}"]
    else:
        if (row_name in x_or_ylims) and (col_name in x_or_ylims):
            raise ValueError(f"Your definition is ambiguous as both row_name ({row_name}) and col_name ({col_name}) are in x_or_ylims.")
        else:
            if row_name in x_or_ylims:
                x_or_ylims_to_use = x_or_ylims[row_name]
            elif col_name in x_or_ylims:
                x_or_ylims_to_use = x_or_ylims[col_name]
    return x_or_ylims_to_use


def print_rms(ax, text_pos, row_name, start_with_rmsequal, add_rms_row, datasetnames_in_row,
              pl_kwargs, text_rms, text_rms_binned, fontsize, unit=None):
    """
    """
    if unit is not None:
        text_unit = f" {unit}"
    else:
        text_unit = ''
    text_rms_to_plot = ""
    for i_dst, datasetname in enumerate(datasetnames_in_row):
        # text_rms_to_plot_dst = f"{pl_kwarg_final[datasetname]['data']['label']}: {text_rms[datasetname]}"
        text_rms_to_plot_dst = f"{pl_kwargs[datasetname]['data']['label']}: {text_rms[datasetname]}"
        if datasetname in text_rms_binned:
            text_rms_to_plot_dst += f", {text_rms_binned[datasetname]} (bin)"
        if start_with_rmsequal and (i_dst == 0):
            text_rms_to_plot_dst = "rms = " + text_rms_to_plot_dst
        text_rms_to_plot += text_rms_to_plot_dst + f"{text_unit} ; "
    if (f"row{row_name}" in text_rms_binned) and add_rms_row:
        text_rms_to_plot += "\n"
        text_rms_to_plot += f"rms bin = {text_rms_binned[f'row{row_name}']}{text_unit}"
    ax.text(*text_pos, text_rms_to_plot, fontsize=fontsize, transform=ax.transAxes)


def check_row4datasetname(row4datasetname: Dict[str, int]|None, datasetnames: Sequence[str]) -> tuple[Dict[str, int], List[List[str]]]:
    """Check the row4datasetname and return the checked row4datasetname and datasetnames4rowidx

    TODO: Ultimately I would like to have one classe Datasets2plot (in th same spirit as Models2plot) that would specify which dataset to plot on which row

    Arguments
    ---------
    row4datasetname : Dictionary specifying on which row a given dataset (specified by its name) should be plotted
    datasetnames    : Sequence of all available dataset name

    Returns
    -------
    row4datasetname : Dictionary specifying on which row a given dataset (specified by its name) should be plotted.
        It differs from the argument only if the argument was None. In this case each dataset is to be plotted in a separate row
    datasetnames4rowidx : List which as the same number of element than the rows mentioned in row4datasetname. 
        Each element of this list is itself a list of the strings giving the datasetnames to be plot in each row.
    """
    if row4datasetname is None:
        row4datasetname = {datasetname: ii for ii, datasetname in enumerate(datasetnames)}
    # Check that all datasets are in row4datasetname
    if (set(row4datasetname.keys()) != set(datasetnames)) or (len(list(row4datasetname.keys())) != len(datasetnames)):
        raise ValueError(f"row4datasetname is not correct ! Datasetnames are {datasetnames} while row4datasetname keys are {row4datasetname.keys()}")
    # Check the row idx values and determine the number of rows to use.
    set_row_idx = set(row4datasetname.values())
    nb_rows = len(set_row_idx)
    assert min(set_row_idx) == 0
    assert max(set_row_idx) == (nb_rows - 1)
    # Create datasetnames_per_row from row4datasetname
    datasetnames4rowidx = [[] for i_row in range(nb_rows)]
    for datasetname in datasetnames:
        datasetnames4rowidx[row4datasetname[datasetname]].append(datasetname)
    return row4datasetname, datasetnames4rowidx


def get_pl_kwargs(pl_kwargs, dico_nb_dstperinsts, datasetnames, bin_size, one_binning_per_row, nb_rows):
    """
    """
    if pl_kwargs is None:
        pl_kwargs = {}
    pl_kwarg_final = {}
    pl_kwarg_jitter = {}
    pl_show_error = {}

    pl_kwarg_data_def = {"fmt": ".", "color": None, "alpha": 1, "zorder": 20}
    pl_kwarg_data_def.update(pl_kwargs.get("all", {}).get("data", {}))
    pl_kwarg_databinned_def = {"color": "r", "fmt": ".", "alpha": 1.0, "zorder": 30}
    pl_kwarg_databinned_def.update(pl_kwargs.get("all", {}).get("data_binned", {}))
    pl_kwarg_modelraw_def = {"color": "k", "fmt": '', "alpha": 1., "linestyle": "-", "label": "model", "zorder": 10}
    pl_kwarg_modelbinned_def = {"color": "r", "fmt": '', "lw": 0.8, "alpha": 1., "zorder": 10}  # , "label": f"model: bin={bin_size}{bin_size_unit}"}
    pl_kwarg_GP_def = {"color": "C0", "linestyle": "-", "label": "GP", "zorder": 10}
    pl_kwarg_GP_err_def = {"color": "C0", "linestyle": "-", "zorder": 0}
    pl_kwarg_wGP_def = {"color": "C4", "linestyle": "-", "label": "model + GP", "zorder": 10}
    pl_kwarg_wGP_err_def = {"color": "C4", "linestyle": "-", "zorder": 0}
    pl_kwarg_GPbinned_def = {"color": "C5", "linestyle": "-", "zorder": 10}
    pl_kwarg_GPbinned_err_def = {"color": "C5", "linestyle": "-", "zorder": 0}
    pl_kwarg_wGPbinned_def = {"color": "C6", "linestyle": "-", "label": "model + GP", "zorder": 10}
    pl_kwarg_wGPbinned_err_def = {"color": "C6", "linestyle": "-", "zorder": 0}
    pl_kwarg_instvar_def = {"color": "C1", "linestyle": "-", "label": "inst.", "zorder": 10}
    pl_kwarg_stellarvar_def = {"color": "C2", "linestyle": "-", "label": "stellar", "zorder": 10}
    pl_kwarg_decorr_def = {"color": "C3", "linestyle": "-", "label": "decorr.", "zorder": 10}
    pl_kwarg_decorr_like_def = {"color": "C3", "linestyle": "-", "label": "decorr.", "zorder": 10}
    show_error_data = True
    show_error_databinned = True

    set_standard_keys = set(["model", "GP", "GP_err", "inst_var", "stellar_var", "sys_var", "decorrelation", "decorrelation_likelihood"])
    set_extra_keys = set(pl_kwargs.keys()) - set(datasetnames) - set_standard_keys
    for datasetname in datasetnames:
        set_keys = set_standard_keys.copy()
        set_keys.update(set_extra_keys)
        set_keys.update(set(pl_kwargs.get(datasetname, {}).keys()) - set_standard_keys)
        # Set the labels
        filename_info = mgr_inst_dst.interpret_data_filename(datasetname)
        if dico_nb_dstperinsts[filename_info["inst_name"]] == 1:
            label_dst = filename_info["inst_name"]
        else:
            label_dst = filename_info["inst_name"] + "({})".format(filename_info["number"])
        pl_kwarg_final[datasetname] = {"model": deepcopy(pl_kwarg_modelraw_def),
                                       "model_binned": deepcopy(pl_kwarg_modelbinned_def),
                                       "data": {"label": label_dst, },
                                       "data_binned": {},  # "label": f"{label_dst}: bin={bin_size}{bin_size_unit}",
                                       "GP": deepcopy(pl_kwarg_GP_def),
                                       "GP_err": deepcopy(pl_kwarg_GP_err_def),
                                       "GP_binned": deepcopy(pl_kwarg_GPbinned_def),
                                       "GP_err_binned": deepcopy(pl_kwarg_GPbinned_err_def),
                                       "model_wGP": deepcopy(pl_kwarg_wGP_def),
                                       "model_wGP_err": deepcopy(pl_kwarg_wGP_err_def),
                                       "model_wGP_binned": deepcopy(pl_kwarg_wGPbinned_def),
                                       "model_wGP_err_binned": deepcopy(pl_kwarg_wGPbinned_err_def),
                                       "inst_var": deepcopy(pl_kwarg_instvar_def),
                                       "inst_var_binned": {},
                                       "stellar_var": deepcopy(pl_kwarg_stellarvar_def),
                                       "stellar_var_binned": {},
                                       "sys_var": deepcopy(pl_kwarg_stellarvar_def),
                                       "sys_var_binned": {},
                                       "decorrelation": deepcopy(pl_kwarg_decorr_def),
                                       "decorrelation_binned": {},
                                       "decorrelation_likelihood": deepcopy(pl_kwarg_decorr_like_def),
                                       "decorrelation_likelihood_binned": {},
                                       }
        pl_kwarg_jitter[datasetname] = {}
        pl_show_error[datasetname] = {"data": show_error_data, "data_binned": show_error_databinned}
        for key in set_keys:
            # Update with the user's inputs
            for binned in [False, True]:
                if binned:
                    key = key + "_binned"
                if key in pl_kwarg_final[datasetname]:
                    pl_kwarg_final[datasetname][key].update(pl_kwargs.get(key, {}))
                else:
                    pl_kwarg_final[datasetname][key] = pl_kwargs.get(key, {})
                pl_kwarg_final[datasetname][key].update(pl_kwargs.get(datasetname, {}).get(key, {}))
        for dataordatabinned, pl_kwarg_def in zip(["data", "data_binned"], [pl_kwarg_data_def, pl_kwarg_databinned_def]):
            # Load default values in pl_kwarg_final[datasetname]
            pl_kwarg_final[datasetname][dataordatabinned].update(deepcopy(pl_kwarg_def))
            # Update with the user's inputs
            pl_kwarg_final[datasetname][dataordatabinned].update(pl_kwargs.get(datasetname, {}).get(dataordatabinned, {}))
            # Update pl_show_error[datasetname] with user input (Needs to be done before pl_kwarg_final is copied into pl_kwarg_jitter)
            if "show_error" in pl_kwarg_final[datasetname][dataordatabinned]:
                pl_show_error[datasetname][dataordatabinned] = pl_kwarg_final[datasetname][dataordatabinned].pop("show_error")
            # Init pl_kwarg_jitter[datasetname]
            pl_kwarg_jitter[datasetname][dataordatabinned] = deepcopy(pl_kwarg_final[datasetname][dataordatabinned])
            # Update with the user's inputs
            if "jitter" in pl_kwarg_final[datasetname][dataordatabinned]:
                dico_jitter = pl_kwarg_final[datasetname][dataordatabinned].pop("jitter")
            else:
                dico_jitter = {}
            dico_jitter["fmt"] = "none"  # To ensure that only the error bars are drawn
            pl_kwarg_jitter[datasetname][dataordatabinned].update(dico_jitter)
            if "label" in pl_kwarg_jitter[datasetname][dataordatabinned]:
                pl_kwarg_jitter[datasetname][dataordatabinned].pop("label")  # To ensure that a second label doesn't appear on the legend
            # default value for alpha jitter
            if "alpha" not in dico_jitter:
                if "alpha" in pl_kwarg_jitter[datasetname][dataordatabinned]:
                    pl_kwarg_jitter[datasetname][dataordatabinned]["alpha"] = pl_kwarg_jitter[datasetname][dataordatabinned]["alpha"] / 2
                else:
                    pl_kwarg_jitter[datasetname][dataordatabinned]["alpha"] = 0.5
            # default value for ecolor
            if ("ecolor" not in pl_kwarg_jitter[datasetname][dataordatabinned]) and ("color" in pl_kwarg_jitter[datasetname][dataordatabinned]):
                pl_kwarg_jitter[datasetname][dataordatabinned]["ecolor"] = pl_kwarg_jitter[datasetname][dataordatabinned]["color"]

    # Fill pl_kwargs_final and pl_kwarg_jitter the databinned of each row if needed
    if (bin_size > 0.) and one_binning_per_row:
        for i_row in range(nb_rows):
            # pl_kwarg_final[f"row{i_row}"] = {"label": f"bin={bin_size}{bin_size_unit}", }
            # Load default values
            pl_kwarg_final[f"row{i_row}"] = deepcopy(pl_kwarg_databinned_def)
            # Update with the user's inputs
            pl_kwarg_final[f"row{i_row}"].update(pl_kwargs.get(f"row{i_row}", {}))
            # Init pl_kwarg_jitter
            pl_kwarg_jitter[f"row{i_row}"] = deepcopy(pl_kwarg_final[f"row{i_row}"])
            # Update with the user's inputs
            if "jitter" in pl_kwarg_final[f"row{i_row}"]:
                dico_jitter = pl_kwarg_final[f"row{i_row}"].pop("jitter")
            else:
                dico_jitter = {}
            dico_jitter["fmt"] = "none"  # To ensure that only the error bars are drawn
            pl_kwarg_jitter[f"row{i_row}"].update(dico_jitter)
            # pl_kwarg_jitter[f"row{i_row}"].pop("label")  # To  ensure that a second label doesn't appear on the legend
            # default value for alpha jitter
            if "alpha" not in dico_jitter:
                if "alpha" in pl_kwarg_jitter[f"row{i_row}"]:
                    pl_kwarg_jitter[f"row{i_row}"]["alpha"] = pl_kwarg_jitter[f"row{i_row}"]["alpha"] / 2
                else:
                    pl_kwarg_jitter[f"row{i_row}"]["alpha"] = 0.5
            # default value for ecolor
            if ("ecolor" not in pl_kwarg_jitter[f"row{i_row}"]) and ("color" in pl_kwarg_jitter[f"row{i_row}"]):
                pl_kwarg_jitter[f"row{i_row}"]["ecolor"] = pl_kwarg_jitter[f"row{i_row}"]["color"]
            # Initialise pl_show_error
            pl_show_error[f"row{i_row}"] = True
            # Update with user input
            if "show_error" in pl_kwarg_final[f"row{i_row}"]:
                pl_show_error[f"row{i_row}"] = pl_kwarg_final[f"row{i_row}"].pop("show_error")
    return pl_kwarg_final, pl_kwarg_jitter, pl_show_error


def update_model_binned_label(pl_kwarg, key_model, extension_binned, datasetname, bin_size, bin_size_unit):
    """
    """
    if bin_size > 0.:
        if bin_size_unit is None:
            text_bin_size_unit = ""
        else:
            text_bin_size_unit = f" [{bin_size_unit}]"
        pl_kwarg[datasetname][f"{key_model}{extension_binned}"]["label"] = f"{key_model}: bin={bin_size:.2g}{text_bin_size_unit}"                
    

def update_data_binned_label(pl_kwarg, key_data_binned, datasetnames, bin_size, bin_size_unit, one_binning_per_row,
                             nb_rows):
    """
    """
    if bin_size > 0.:
        if bin_size_unit is None:
            text_bin_size_unit = ""
        else:
            text_bin_size_unit = f" [{bin_size_unit}]"
        if one_binning_per_row:
            for i_row in range(nb_rows):
                pl_kwarg[f"row{i_row}"]["label"] = f"bin={bin_size:.2g}{text_bin_size_unit}"
        else:
            for datasetname in datasetnames:
                pl_kwarg[datasetname][key_data_binned]["label"] = f"bin={bin_size:.2g}{text_bin_size_unit}"            


def do_suptitle(fig, post_instance, datasetnames, fontsize, dico_models, model_removed_or_add_dict,
                data_remove_or_add_dict, suptitle_kwargs=None):
    """Make the suptitle

    Arguments
    ---------
    fig                     : Figure
        Figure instance
    post_instance           : Posterior
        Posterior instance
    fontsize                : int
        Font size to use for the suptitle

    suptitle_kwargs         : dict
        keys are
            do                      : bool
                If True does the suptitle
            show_removed            : bool
                If True does the component of the model that have been removed from the data and the
                model to produce the plot
            show_system_name        : bool
                If True show the name of the system on top of the plot
            system_name             : str
                If you don't want to use the system name defined in the post_instance object you can
                specify a different name for the system here.
    """
    suptitle_kwargs_default = {"do": True, "show_removed": True, "show_system_name": True}
    if suptitle_kwargs is None:
        suptitle_kwargs = {}
    # Do the suptitle
    if suptitle_kwargs.get("do", suptitle_kwargs_default["do"]):
        suptitle_text = ""
        if suptitle_kwargs.get("show_system_name", suptitle_kwargs_default["show_system_name"]):
            suptitle_text = f"{suptitle_kwargs.get('system_name', post_instance.full_name)} system"
        if suptitle_kwargs.get("show_removed", suptitle_kwargs_default["show_system_name"]):
            for model_or_data, model_or_data_removed_or_add_dict in zip(["model", "data"],
                                                                        [model_removed_or_add_dict, data_remove_or_add_dict]
                                                                        ):
                text = ""
                for add_or_remove, remove_or_add_dict in zip(["added", "removed"],
                                                             [model_or_data_removed_or_add_dict["add_dict"], model_or_data_removed_or_add_dict["remove_dict"]]
                                                             ):
                    text_remove_or_add = ""
                    for key_model, asked2remove in remove_or_add_dict.items():
                        if asked2remove and any([key_model in dico_models[dst_name] for dst_name in datasetnames]):
                            text_remove_or_add += f"{key_model}, "
                    if len(text_remove_or_add) > 0:
                        text_remove_or_add = text_remove_or_add[:-2]
                        text_remove_or_add += f" ({add_or_remove}); "
                        text += text_remove_or_add
                if len(text) > 0:
                    text = text[:-2]
                    text = f"{model_or_data}: " + text
                    suptitle_text += "\n" + text

        if suptitle_text != "":
            fig.suptitle(suptitle_text, fontsize=fontsize)


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

    def add_models_2_show(self, models: Sequence[str], row_idx: int|None = None, datasetnames: Sequence[str|None]|None=None, npts: Sequence[int|None]|None=None, tlims: Sequence[tuple[float, float]|None]|None=None, pl_kwargs: Sequence[Dict|None]|None=None):
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
    
    def __init__(self, model: str, datasetname: str|None=None, npt: int|None=None, tlims: tuple[float, float]|None=None, pl_kwargs: Dict|None=None):
        """"""
        self.__model: str = model
        self.__time_values: NDArray[float_]|None = None
        self.__model_values: Dict[float, Dict[int, NDArray[float_]]]|None= None
        self.__model_values_err: Dict[float, Dict[int, NDArray[float_]|None]]|None= None
        self.__datasetname: str|None = None
        if datasetname is not None:
            self.datasetname = datasetname
        self.__npt: int|None = None
        if npt is not None:
            self.npt = npt
        self.__tlims: tuple[float, float]|None = None
        if tlims is not None:
            self.tlims = tlims
        self.pl_kwargs = pl_kwargs

    @property
    def model(self):
        """Model name"""
        return self.__model
    
    @property
    def model_stored(self) -> bool:
        """Return True if the model has been computed and stored"""
        return self.__time_values is not None
    
    @property
    def npt(self):
        """Number of point in the model"""
        return self.__npt
    
    @npt.setter
    def npt(self, new_npt):
        """Number of point in the model"""
        if self.model_stored:
            raise ValueError(self.__err_msg_model_already_computed.format("npt"))
        if not(isinstance(new_npt, int)) or (new_npt <= 0):
            raise ValueError(f"npt should be an strictly positive int, got {new_npt}")
        self.__npt = new_npt
    
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
        return self.__tlims
    
    @tlims.setter
    def tlims(self, new_tlims: tuple[float, float]):
        """Tuple giving the min and max values for the model"""
        if not(isinstance(new_tlims, tuple)) or (len(new_tlims) != 2) or not(all([isinstance(val, float) for val in new_tlims])) or not(all([isfinite(val) for val in new_tlims])):
            raise ValueError(f"tlims should be a tuple of 2 finite floats, got {new_tlims}")
        if new_tlims[0] >= new_tlims[1]:
            raise ValueError(f"tlims[0] cannot be equal or higher than t_lims[1] got {new_tlims}")
        self.__tlims = new_tlims

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
