from source.problems.posterior.systemmodel.data_interface.classes import ExoP_datasets
from source.problems.posterior.systemmodel.data_interface.classes import LightCurve
from source.problems.posterior.systemmodel.data_interface.classes import RV

# Create an object which will contains all the dataset available in the folder data/k2-29
K2_29_dataset = ExoP_datasets("K2-29")

# The data are stored in OrderedDict whihc are behaving more or less like normal dict
# This gives the keys of all the datasets available
K2_29_dataset.get_dataset_keys()

# This gives the keys of all the LC datasets available
K2_29_dataset.get_LC_dataset_keys()

# This gives the keys of all the LC datasets available
K2_29_dataset.get_RV_dataset_keys()

# If you want to access a particular LC dataset you do. This is a LightCurve Object.
K2_29_dataset.lc_datasets['K2']

# The Dataframe containing the data, it's
K2_29_dataset.lc_datasets['K2'].data

# If you want to plot the light-curve you do
K2_29_dataset.lc_datasets['K2'].plot()

# Same thing for the RVs
K2_29_dataset.rv_datasets['SOPHIE']
K2_29_dataset.rv_datasets['SOPHIE'].data
K2_29_dataset.rv_datasets['SOPHIE'].plot()
