from os import getcwd, makedirs
from os.path import join


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
