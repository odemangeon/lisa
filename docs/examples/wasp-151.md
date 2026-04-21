# WASP-151 Example

The `examples/WASP-151/` directory contains a complete example analysis using
radial velocity and photometric time-series data.

## Files

```text
examples/WASP-151/
  README.md
  config_file.py
  script_EmceeExploration.py
  chain_analysis_Emcee.ipynb
  data/
```

The `data/` directory contains the input light-curve and radial-velocity files.
The Python scripts define and run the exploration and analysis workflow.

## Run

From the repository root:

```bash
conda activate lisa
cd examples/WASP-151
ipython
```

From IPython:

```python
%run script_EmceeExploration.py
```

When the exploration is complete, run the jupyter notebook `chain_analysis_Emcee.ipynb`

## Description

Describe the example, the dataset and the model setup.
Provide overview of the expected results and some plots.

