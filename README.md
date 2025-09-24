# lisa

## Installation

1. Clone the lisa repository

git clone https://github.com/odemangeon/lisa.git

2. Install the dependancies in a new anaconda environment:

The dependencies are specified in the environment.yml file.

conda env create -f environment.yml 

This will create a new lisa environment with all the dependencies except for 
for PyGLS that I modified and so cannot be installed using conda/pip and need to be installed from source. So you need to clone PyGLS in a different folder:

git clone https://github.com/LucaMalavolta/PyGLS.git

and then install it from the source in the lisa environment

conda activate lisa
conda develop <path_to_the_directory_where_you_cloned_PyGLS>

3. Install lisa in the anaconda environment

conda activate lisa
conda develop <path_to_the_directory_where_you_cloned_lisa>

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
