# Emcee

## Typical Workflow

To analyse a new dataset using `lisa` and `emcee`.

1. Make sure that `lisa` is installed and that the `lisa` anaconda environment is activated (see [Installation](installation.md));
2. Copy the `script_EmceeExploration.py` from the `script_and_functions` directory of the `lisa` repository into a working directory;
3. In this directory, open an 'IPython' session and run it: `%run script_EmceeExploration.py`;
4. It will walk you through the creation of the configuration file and start the Emcee exploration;
5. Once the exploration is concluded, copy the Jupyter notebook `chain_analysis_Emcee.ipynb` from `script_and_functions` into your working directory;
6. Run the notebook. It will walk you through a way to analyse the chain and extract the parameter inferences.
7. If needed adjust the `script_EmceeExploration.py` to run a follow-up Emcee exploration, analyse with `chain_analysis_Emcee.ipynb` and repeat as needed.

[The plotting](plotting.md) sections describes how to make plot to visualize your dataset and models.

## Quick description of script_EmceeExploration.py

The 'script_EmceeExploration.py' create a 'lisa' model for the data and start a fit using the `emcee` package.

## Quick description of chain_analysis_Emcee.ipynb
