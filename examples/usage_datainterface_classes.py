import logging
import pdb
import sys
import matplotlib
matplotlib.use('Qt5Agg')

import source.posterior.core.dataset_and_instrument.manager_dataset_instrument as mgr
from source.run import set_up_run

# pdb.set_trace()

logger = logging.getLogger()
if logger.level > logging.DEBUG:
    logger.setLevel(logging.DEBUG)
if len(logger.handlers) == 0:
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

logger.info("First let's deal with on data file.")

logger.info("mgr.Manager_Inst_Dataset() creates the Manager. This manager has to be used to create"
            "the Dataset subclass. Indeed it will interpret the name of the data file and use the "
            "information to create the correct Dataset subclass and attach the correct instrument"
            "to the data.")
manager = mgr.Manager_Inst_Dataset()

logger.info("In order to do that the manager needs to know what are the Dataset subclasses and"
            "the instrument available. This information is provided by the user to the manager"
            "through the dataset_inst_setup_file that the user has to fill.\nmanager.load_setup()"
            " loads the dataset_inst_setup_file")
manager.load_setup()

filepath_LC = "/Users/olivier/Softwares/lisa/data/K2-29/LC_K2-29_K2.txt"
logger.info("The name of the data files is very important because from this name the software will "
            "infer a lot of information that he needs to properly handle the data.\nSo the "
            "data file name needs to respect a format: 'instrument type'_'name of observed object'"
            "_'name of isntrument'(_'number').* .\nFor example, {}, is a good a data file name.\n"
            "".format(mgr.get_filename_from_file_path(filepath_LC)))

logger.info("Let's try to create an Dataset from this data file.")

logger.info("manager.create_dataset(file_path=filepath_LC) create an instance of the good subclass "
            "of Dataset to handle the data file and return it. Here we called our instance "
            "dataset_K2.")
dataset_K2 = manager.create_dataset(file_path=filepath_LC)

logger.info("To read the data for the file you have to use dataset_K2.get_data(). It bhaves as the"
            " method pandas.read_table with some default values defined and thus returns a "
            "pandas.DataFrame object.")
data = dataset_K2.get_data()
logger.info("Here is the info regarding the loaded data:\n{}".format(data.info()))
logger.info("By default those data will not be loaded into the Dataset subclass. But if you want to"
            ", pass the argument store=True to get data.")

logger.info("You can also plot the data using the plot method of the Dataset sublass. It behaves "
            "exactly like the pandas.plot function.")
dataset_K2.plot()

filepath_RV = "/Users/olivier/Softwares/lisa/data/K2-29/RV_K2-29_SOPHIE.rdb"
logger.info("Now if we try to create a dataset from another file: {}\n Let's call it dataset_SOPHIE"
            ".".format(mgr.get_filename_from_file_path(filepath_RV)))
dataset_SOPHIE = manager.create_dataset(file_path=filepath_RV)

logger.info("If you look at the type of dataset_K2, you get: {}\n"
            "If you look at the type of dataset_SOPHIE, you get: {}\n"
            "".format(type(dataset_K2), type(dataset_SOPHIE)))
logger.info("It's the manager who, thanks to the information provided by the setup file, created"
            " a LC_Dataset for {} and an RV_Dataset for {} !".format(filepath_LC, filepath_RV))

logger.info("You can also plot the data of dataset_SOPHIE using the plot method.")
dataset_SOPHIE.plot()

logger.info("Now let's try to load all the data file related to one analysis the we want to do. "
            "This is not dealt dorectly be the manager. It's deal by the Posterior which uses "
            "the manager to create the Dataset instance as we have just see.")

logger.info("TBD.")

# datasets_file = set_up_run(target="K2-29", run_name="runtest")
#
# input("Check that all datasets_file you want to use are listed in {} and press Enter."
#       "".format(datasets_file))
#
# # Create an object which will contains all the dataset available in the folder data/k2-29
# K2_29_dataset = ExoP_datasets("K2-29", datasets_file=datasets_file)
#
# # The data are stored in OrderedDict whihc are behaving more or less like normal dict
# # This gives the keys of all the datasets available
# print("List of all datasets:{}".format(K2_29_dataset.get_dataset_keys()))
#
# # This gives the keys of all the LC datasets available
# print("List of LC datasets:{}".format(K2_29_dataset.get_LC_dataset_keys()))
#
# # This gives the keys of all the RV datasets available
# print("List of RV datasets:{}".format(K2_29_dataset.get_RV_dataset_keys()))
#
# # This gives the keys of all the RV datasets available
# print("List of all instruments:{}".format(K2_29_dataset.get_instrument_keys()))
#
# # If you want to access a particular LC dataset you do. This is a LightCurve Object.
# if K2_29_dataset.isin_LC_datasets("K2"):
#     print("The K2 LC of K2_29 has been loaded. Here is the content of this dataset")
#     # print(K2_29_dataset.lc_datasets['K2'])
#     print(K2_29_dataset.lc_datasets['K2'].data)
#     print("Here is a plot of the data")
#     K2_29_dataset.lc_datasets['K2'].plot()
#
# # Same thing for the RVs
# if K2_29_dataset.isin_RV_datasets("SOPHIE"):
#     print("The SOPHIE RVs of K2_29 has been loaded. Here is the content of this dataset")
#     # print(K2_29_dataset.rv_datasets['SOPHIE'])
#     print(K2_29_dataset.rv_datasets['SOPHIE'].data)
#     print("Here is a plot of the data")
#     K2_29_dataset.rv_datasets['SOPHIE'].plot()
