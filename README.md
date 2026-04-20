# lisa

`lisa` is a Python package for joint modelling and analysis of exoplanet radial
velocity and photometric time series.

The codebase contains the core `lisa` package, example analyses, plotting and
chain-analysis scripts, and tests used during development.

## Installation

The recommended installation uses Conda for the scientific Python environment
and `pip` for installing the local `lisa` package.

Clone the repository:

```bash
git clone https://github.com/odemangeon/lisa.git
cd lisa
```

Create the Conda environment from the repository root:

```bash
conda env create -f environment.yml
conda activate lisa
```

The environment file installs the scientific dependencies and then installs this
repository in editable mode with:

```yaml
- pip:
    - -e .
```

Editable mode is useful while developing `lisa`: changes made inside the `lisa/`
package are immediately available in the active environment.

To check that the installation worked:

```bash
python -c "import lisa; print(lisa.__file__)"
```

### Updating an existing environment

After changing `environment.yml`, update the existing environment with:

```bash
conda activate lisa
conda env update -f environment.yml --prune
python -m pip install -e .
```

## Quick Start

The `examples/` directory contains complete example analyses with input data and
analysis scripts. A typical workflow is:

```bash
conda activate lisa
cd examples/WASP-151
ipython
```

Then, from IPython:

```python
%run script_mcmcexploration.py
%run script_chainanalysis.py
```

Other examples are available in:

- `examples/K2-19/`
- `examples/WASP-151/`
- `examples/helios/`

The `script_and_functions/` directory contains reusable analysis and plotting
scripts that can be copied into a working directory and adapted for a specific
target.

## Repository Layout

- `lisa/`: main Python package.
- `examples/`: example analyses and input data.
- `script_and_functions/`: reusable scripts for exploration, chain analysis, and plotting.
- `tests/`: unit tests and development tests.
- `environment.yml`: Conda environment used for installation and development.
- `pyproject.toml`: Python packaging and tool configuration.

## Running Tests

After activating the environment, install the test runner if needed:

```bash
conda install pytest
```

Then run the unit tests with:

```bash
pytest tests/unit_tests
```

Some tests and example scripts may require local data products or optional
dependencies, depending on the workflow being exercised.

## Development Notes

For day-to-day development, install with the Conda workflow above and keep the
package editable. The project metadata lives in `pyproject.toml`, while the full
scientific environment is described in `environment.yml`.

Useful development commands:

```bash
conda activate lisa
conda install pytest ruff mypy
python -m pip install -e .
pytest tests/unit_tests
ruff check lisa tests
ruff format lisa tests
```

## Documentation

This README is the entry point for installation and first use. The next step is
to add online documentation with a structure such as:

- Installation
- Quick-start tutorial
- Worked examples
- User guide
- API reference
- Development guide

A good documentation layout for this repository would be:

```text
docs/
  index.md
  installation.md
  quickstart.md
  examples.md
  user-guide/
  api-reference/
  development.md
```

The examples already in this repository are a strong base for future tutorials:
each one can become a short documentation page explaining the input files, model
configuration, exploration step, and chain-analysis step.
