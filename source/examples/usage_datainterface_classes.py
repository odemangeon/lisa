import logging
import pdb
import sys
import matplotlib
matplotlib.use('Qt5Agg')

from source.problems.posterior.systemmodel.data_interface.classes import ExoP_datasets
from source.problems.posterior.systemmodel.data_interface.classes import LightCurve
from source.problems.posterior.systemmodel.data_interface.classes import RV
from source.run import set_up_run

# pdb.set_trace()

logger = logging.getLogger()
logger.setLevel("DEBUG")

if len(logger.handlers) == 0:
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

datasets_file = set_up_run(target="K2-29", run_name="runtest")

input("Check that all datasets_file you want to use are listed in {} and press Enter."
      "".format(datasets_file))

# Create an object which will contains all the dataset available in the folder data/k2-29
K2_29_dataset = ExoP_datasets("K2-29", datasets_file=datasets_file)

# The data are stored in OrderedDict whihc are behaving more or less like normal dict
# This gives the keys of all the datasets available
print("List of all datasets:{}".format(K2_29_dataset.get_dataset_keys()))

# This gives the keys of all the LC datasets available
print("List of LC datasets:{}".format(K2_29_dataset.get_LC_dataset_keys()))

# This gives the keys of all the RV datasets available
print("List of RV datasets:{}".format(K2_29_dataset.get_RV_dataset_keys()))

# This gives the keys of all the RV datasets available
print("List of all instruments:{}".format(K2_29_dataset.get_instrument_keys()))

# If you want to access a particular LC dataset you do. This is a LightCurve Object.
if K2_29_dataset.isin_LC_datasets("K2"):
    print("The K2 LC of K2_29 has been loaded. Here is the content of this dataset")
    # print(K2_29_dataset.lc_datasets['K2'])
    print(K2_29_dataset.lc_datasets['K2'].data)
    print("Here is a plot of the data")
    K2_29_dataset.lc_datasets['K2'].plot()

# Same thing for the RVs
if K2_29_dataset.isin_RV_datasets("SOPHIE"):
    print("The SOPHIE RVs of K2_29 has been loaded. Here is the content of this dataset")
    # print(K2_29_dataset.rv_datasets['SOPHIE'])
    print(K2_29_dataset.rv_datasets['SOPHIE'].data)
    print("Here is a plot of the data")
    K2_29_dataset.rv_datasets['SOPHIE'].plot()
