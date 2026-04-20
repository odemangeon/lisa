# Quick Start

The fastest way to learn the workflow is to run one of the examples included in
the repository.

## Run the WASP-151 Example

Install and activate the environment first:

```bash
conda env create -f environment.yml
conda activate lisa
```

Then run the example:

```bash
cd examples/WASP-151
ipython
```

From IPython:

```python
%run script_mcmcexploration.py
```

After the exploration has produced chains and output files, run the chain
analysis script:

```python
%run script_chainanalysis.py
```

## Other Examples

Additional examples are available in:

- `examples/K2-19/`
- `examples/WASP-151/`
- `examples/helios/`

Each example contains input data and scripts that can be copied into a separate
working directory and adapted for a new target.

## Typical Workflow

1. Choose an example close to the target analysis.
2. Copy the example scripts into a working directory.
3. Update the configuration and input data paths.
4. Run the exploration script.
5. Run the chain-analysis and plotting scripts.
6. Inspect the generated outputs and iterate on the model configuration.
