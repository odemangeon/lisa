from os import getcwd, makedirs
from os.path import join


def get_def_output_folders(run_folder=None):
    """Provides the default output folder to store the outputs of the exploration and analysis.

    This function creates the output folder tree if there are not already present in the run_folder.

    :param str run_folder: Path to run_folder where the output folder tree is expected to be. If None,
        the current working directory is used instead
    :return dict output_folders: key, path
    """
    if run_folder is None:
        run_folder = getcwd()

    output_folders = {}

    exploration_output_folder = join(run_folder, "outputs/exploration")
    makedirs(exploration_output_folder, exist_ok=True)
    output_folders["pickles_explore"] = join(exploration_output_folder, "pickles")
    makedirs(output_folders["pickles_explore"], exist_ok=True)
    output_folders["dats"] = join(exploration_output_folder, "dats")
    makedirs(output_folders["dats"], exist_ok=True)
    chain_analysis_output_folder = join(getcwd(), "outputs/chain_analysis")
    makedirs(chain_analysis_output_folder, exist_ok=True)
    output_folders["plots"] = join(chain_analysis_output_folder, "plots")
    makedirs(output_folders["plots"], exist_ok=True)
    output_folders["pickles_analyze"] = join(chain_analysis_output_folder, "pickles")
    makedirs(output_folders["pickles_analyze"], exist_ok=True)
    output_folders["tables"] = join(chain_analysis_output_folder, "tables")
    makedirs(output_folders["tables"], exist_ok=True)

    return output_folders
