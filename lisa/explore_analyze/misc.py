from loguru import logger
from os import getcwd, makedirs
from os.path import join
from copy import deepcopy, copy
from matplotlib.ticker import ScalarFormatter, FuncFormatter

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
mgr_inst_dst.load_setup()


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
    possible_keys = ['all', ]
    if l_row_name is not None:
        possible_keys.extend(l_row_name)
    if l_col_name is not None:
        possible_keys.extend(l_col_name)
    if spec_user is None:
        pass
    elif any([isinstance(spec_user, type_i) for type_i in l_type_spec]):
        spec['all'] = spec_user
    elif isinstance(spec_user, dict) and all([key in possible_keys for key in spec_user]):
        spec.update(spec_user)
    else:
        raise ValueError(f"spec_user should be a None or a {l_type_spec} or a dict with keys in {possible_keys}"
                         f" and values of type {l_type_spec} which specify the spec per row or per column,"
                         f" got {spec_user}"
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
    l_bottom_keys = l_row_name + l_col_name + ['all', ]
    spec_user_for_define_spec = {key: None for key in l_top_keys}
    if spec_user is None:
        pass
    elif any([isinstance(spec_user, type_i) for type_i in l_type_spec]):
        for key in l_top_keys:
            spec_def[key] = spec_user
    elif isinstance(spec_user, dict) and all([key in l_top_keys for key in spec_user]):
        spec_user_for_define_spec.update(spec_user)
    else:
        raise ValueError(f"spec_user should be a None or a {l_type_spec} or a dict with keys in {l_top_keys}"
                         f" and values that or None or a {l_type_spec} or a dict with keys in {l_bottom_keys}"
                         f" and values of type {l_type_spec} which specify the spec per row or per column for each in {l_top_keys},"
                         f" got {spec_user}")
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


def check_datasetname4model4row(datasetname4model4row, datasetnames4rowidx, l_model, l_model_1_per_row):
    """
    """
    datasetname4model4row_user = datasetname4model4row if datasetname4model4row is not None else {}
    datasetname4model4row = {}
    for model in l_model:
        if model in l_model_1_per_row:
            datasetname4model4row[model] = {i_row: datasetnames_i_row[0] for i_row, datasetnames_i_row in enumerate(datasetnames4rowidx)}
        else:
            datasetname4model4row[model] = {i_row: 'all' for i_row, datasetnames_i_row in enumerate(datasetnames4rowidx)}
    for model in datasetname4model4row_user:
        datasetname4model4row[model].update(datasetname4model4row_user[model])
    return datasetname4model4row


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
    if row_name in x_or_ylims:
        x_or_ylims_to_use = x_or_ylims[row_name]
    if col_name in x_or_ylims:
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


def check_row4datasetname(row4datasetname, datasetnames):
    """Check the row4datasetname and return the checked row4datasetname and datasetnames4rowidx
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


def get_pl_kwargs(pl_kwargs, dico_nb_dstperinsts, datasetnames, bin_size, one_binning_per_row,
                  nb_rows, alpha_def_data=1., color_def_data=None, show_error_data_def=True):
    """
    """
    pl_kwarg_data_def = {"fmt": ".", "alpha": alpha_def_data, "zorder": 20}
    if color_def_data is not None:
        pl_kwarg_data_def["color"] = color_def_data
    pl_kwarg_databinned_def = {"color": "r", "fmt": ".", "alpha": 1.0, "zorder": 30}
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
    show_error_data = show_error_data_def
    show_error_databinned = True

    if pl_kwargs is None:
        pl_kwargs = {}
    pl_kwarg_final = {}
    pl_kwarg_jitter = {}
    pl_show_error = {}

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
