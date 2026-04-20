# Priors

## Where Priors Are Used

Explain `individual_priors` and `joint_priors` in `config_file.py`.

## Joint Prior Syntax

The typical syntax is:
```python
joint_priors = {
    "eccentricity_prior_b": {
        "category": "polar",
        "params": {
            "x": "b_ecosw",
            "y": "b_esinw",
        },
        "args": {
            "r_prior": {"category": "uniform", "args": {"vmin": 0.0, "vmax": 1.0}},
            "theta_prior": {"category": "uniform", "args": {"vmin": -np.pi, "vmax": np.pi}},
        },
    }
}
```


## Individual Prior Syntax

Individual priors live in the `individual_priors` dictionary. All free parameters that are not already addressed in the `joint_priors` dictionary, should appear here and you should define a prior for each. The syntax is:

```python
individual_priors = {
...
"<PARAMETER_NAME>": {
    "category": "<PRIOR_CATEGORY>",
    "args": {"<ARGUMENT_1>": 1.0, "<ARGUMENT_2>": 0.1, ...},
    "unit": "UNIT",
},
...
```
You need to specify the prior category. All available categories are listed in the '**Category**' column of the table below.
You also need to specify the arguments for the priors and their values. There are mandatory arguments and optional arguments that are listed in the '**Arguments**' and '**Optional Arguments**' columns for each prior category.

The available priors are:

| Category | Arguments | Optional Arguments | Comments |
|---|---|---|---|
| `uniform` | `vmin`, `vmax` | | |
| `normal` | `mu`, `sigma` | `"lims"=(0,1)`, `"sigma_lims"=(-3,3)` | If `lims` or `sigma_lims` are provided, it implements a  truncated normal distribution |
| `lognormal` | `mu`, `sigma` | `"lims"=(1,10)` | If `lims` is provided, it implements a truncated log-normal distribution |
| `jeffreys` | `vmin`, `vmax` | |  |
| `sine`| `vmin`, `vmax` | `"rad"=True` | |
| `Beta`| `a`, `b` | |  |
