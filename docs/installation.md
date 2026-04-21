# Installation

The recommended installation uses Conda for the scientific Python environment
and `pip` for installing the local `lisa` package.

## Requirements

- Git
- Conda or Mamba
- Python 3.11, provided by the Conda environment

## Install From Source

Clone the repository:

```bash
git clone https://github.com/odemangeon/lisa.git
cd lisa
```

Create and activate the Conda environment:

```bash
conda env create -f environment.yml
conda activate lisa
```

The environment file installs this repository in editable mode with:

```yaml
- pip:
    - -e .
```

Editable mode means that changes made inside the `lisa/` package are immediately
available in the active environment.

Check that the package can be imported:

```bash
python -c "import lisa; print(lisa.__file__)"
```

## Update an Existing Environment

After changing `environment.yml`, update the existing environment with:

```bash
conda activate lisa
conda env update -f environment.yml --prune
python -m pip install -e .
```

## Build the Documentation Locally

Install the documentation tools:

```bash
conda activate lisa
python -m pip install mkdocs mkdocs-material
```

Start a local documentation server from the repository root:

```bash
mkdocs serve
```

MkDocs will print a local URL, usually `http://127.0.0.1:8000/`.

If the port 8000 is already used, use another one with
```bash
mkdocs serve -a 127.0.0.1:8001
```
