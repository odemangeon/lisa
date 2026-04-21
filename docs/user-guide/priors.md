# Priors

## Where Priors Are Used

Explain `individual_priors` and `joint_priors` in `config_file.py`.

## Joint Prior Syntax

Joint priors live in the `joint_priors` dictionary. They are priors whose probability density function relies on more than one parameter and cannot be reduced to the product of mono-argument probability density function. The joint priors defined in lisa are used to convert a set of parameter into a different set of parameters (called `hidden parameters`) for which the definition of individual probability density function is more natural. The syntax for the `joint_priors` dictionary is the following:

```python
joint_priors = {
    "<NAME_FOR_JOINTPRIOR_1>": {
        ... joint prior 1 definition
    },
    "<NAME_FOR_JOINTPRIOR_2>": {
        ... joint prior 2 definition
    },
    ...
}
```

The joint prior definitions dictionaries all follow the same structure and relie on the 

```python
joint_priors = {
    "<NAME_FOR_JOINTPRIOR_1>": {
        "category": "<JOINTPRIOR_CATEGORY>",
        "args": {
            "<HIDDENPARAM_NAME_1>_prior": {
                ... individual hidden parameter 1 definition
            },
            "<HIDDENPARAM_NAME_2>_prior": {
                ... individual hidden parameter 2 definition
            },
            "<EXTRA_ARGUMENT_1>": ... extra argument 1 value,
            "<EXTRA_ARGUMENT_2>": ... extra argument 2 value,
        },
        "params": {"<PARAMNAME_INJOINTPRIOR_1>": "<PARAMNAME_INYOURMODEL_1>", "<PARAMNAME_INJOINTPRIOR_2>": "<PARAMNAME_INYOURMODEL_2>"},
    },
}
```
The table below provide the available joint priors categories and their associated internal paramater names (`<PARAMNAME_INJOINTPRIOR>`), hidden parameter names (`<HIDDENPARAM_NAME>`) and extra arguments.


| Category | Parameter names | hidden parameter names | Extra arguments |
|---|---|---|---|
| `polar` | `x`, `y` | `r`, `theta` | |
| `supinf` | `sup`, `inf`  | `sup`, `y`  | `k=1` |
| `sum` | `x`, `y`  | `x`, `sum`  | `ymin=0`, `ymax=0` |
| `Ptphi` | `P`, `t`  | `P`, `t`, `Phi` | `t_ref=...`, `Phi_lims=(0, 1)`|
| `transiting` | `aR`, `cosinc`, `Rrat`  | `aR`, `b`, `Rrat` | `transiting=True`, `allow_grazing=True`|
| `transiting_rho` | `rhostar`, `P`, `tic`, `cosinc`, `Rrat`| `rhostar`, `P`, `Phi`, `b`, `Rrat` | `transiting=True`, `allow_grazing=True`, `t_ref=...`|



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
| `beta`| `a`, `b` | |  |
| `betaecc`| none | | `a=0.867` and `b = 3.03` following Kipping+2013|
