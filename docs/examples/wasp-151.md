# WASP-151 Example

The `examples/WASP-151/` directory contains a complete example analysis using
radial velocity and photometric time-series data.

## Files

```text
examples/WASP-151/
  README.md
  config_file.py
  script_mcmcexploration.py
  script_chainanalysis.py
  script_mcmcexploration_fuprun.py
  script_chainanalysis_fuprun.py
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
%run script_mcmcexploration.py
```

When the exploration is complete, run:

```python
%run script_chainanalysis.py
```

## Before Adapting the Example

Read through:

- `config_file.py`
- `script_mcmcexploration.py`
- `script_chainanalysis.py`

These files define the datasets, model setup, exploration settings, and analysis
steps. For a new target, copy the scripts into a separate working directory and
adapt the configuration and input data files.

## Follow-up Run

The files with the `_fuprun` suffix are intended for a follow-up run using the
same example structure:

```python
%run script_mcmcexploration_fuprun.py
%run script_chainanalysis_fuprun.py
```
