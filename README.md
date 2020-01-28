# lisa

## Installation

1. Dependancies:

Rely on python3.6. Python package dependencies:
- unittest
- ajplanet*
- matplotlib
- astropy
- scipy
- rebound
- PIL
- batman
- numpy
- dill
- pytransit*
- gzip
- pandas
- george
- celerite
- radvel
- emcee=2.2.1
- tqdm
- PyAstronomy

2. Clone the repository

3. Create the software parameters file:

In lisa/lisa/ create a file called software_parameters.py which contains the following lines:

```python3
#!/usr/bin/python
# -*- coding:  utf-8 -*-
from os.path import join

# Define the lisa main folder
lisa_main_folder = "/Users/olivier/Softwares/lisa-dev"  # Replace by the location where you clone the lisa repo.

# Define run and data main folder
input_run_folder = join(lisa_main_folder, "run")
input_data_folder = join(lisa_main_folder, "data")

# Define the relative path of the setup files folder
setup_files_folder = "setup_files"

# Datasets and instruments setup file
setupfile_dataset_inst = join(lisa_main_folder, setup_files_folder, "dataset_inst_setup_file.py")

# Models setup file
setupfile_model = join(lisa_main_folder, setup_files_folder, "model_setup_file.py")

# Priors setup file
setupfile_prior = join(lisa_main_folder, setup_files_folder, "prior_setup_file.py")

# Noise models setup file
setupfile_noise_model = join(lisa_main_folder, setup_files_folder, "noise_model_setup_file.py")
```

4. Insert the path to the lisa folder in your python path.

## Quick start

Copy/paste the python file: script_analysis/script_mcmcexploration.py in another folder where you are going to work. Modify it to suit your needs.
When the exploration is performed, you can Copy/paste the python file script_analysis/script_chainanalysis.py in the same directory and modify it to suit your needs and interpret the results.

## Description of the different folders in the repository

### source

Folder which contains the source/code of the lisa software:

### ocode and olivier

Olivier's personal codes: The ocode folder contains the code developed with the Kunal. I put the all content of the folder he made so there is text file and png file not only python codes (I will try to clean it later).
The main last version of the python codes are in the directory final_commentedcodes_from_kunal. All the rest is all the older version of codes that he developed before.
*Final fight.py* was the version of the main code when he left. Yes Kunal is a funny guy.

### scode and susana

Susana's personal codes.

### data

Some datasets used to test and performs some examples

### examples

Examples on how to use lisa

### script_analysis

Template of scripts to use lisa and interpret the results.

### setup_files

Folder which contains the files defining the setup of lisa.

### tests

Folder with the tests of the code.
