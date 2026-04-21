# lisa

`lisa` is a Python package for joint modelling and analysis of exoplanet radial
velocity and photometric time series.

The package is built around reusable modelling, exploration, plotting, and chain
analysis tools. The repository also includes worked examples that can be used as
starting points for new analyses.

## Where to Start

- [Installation](installation.md): create the Conda environment and install `lisa`.
- [Quick Start](quickstart.md): run an example analysis from the repository.
- [WASP-151 example](examples/wasp-151.md): first worked example page.

## Documentation Status

These pages are an initial documentation scaffold. The next useful additions are:

- more worked examples `example/cheops/` `examples/K2-19/` and `examples/helios/` ;
- an API reference generated from the Python package.

## Repository Layout

```text
lisa/
  lisa/                 Python package
  examples/             Example analyses and input data
  script_and_functions/ Reusable analysis and plotting scripts
  tests/                Unit tests and development tests
  environment.yml       Conda environment
  pyproject.toml        Python package metadata and tool configuration
```
