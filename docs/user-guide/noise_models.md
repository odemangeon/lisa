# Noise Models

## Noise Models Category Definition

You need to specify the category of noise model for each instrument model in the `d_noise_model_def` dictionary of the config file. There is only two categories:

- `gaussian`
- `GP1D`

The syntax for the `d_noise_model_def` dictionary is as follows:

```python
d_noise_model_def = {
    ...
    "<INSTRUMENT_CATEGORY>": {
        "<INSTRUMENT_NAME>": {
            "<INSTRUMENT_MODEL_NAME1>": "<NOISE_MODEL_CATEGORY_1>", 
            "<INSTRUMENT_MODEL_NAME2>": "<NOISE_MODEL_CATEGORY_1>",
        },
    },
    ...
}
```

Once you have attributed a noise model category to each instrument model, you have to configure the parameters of these noise models. There is one section of the configuration file for each noise model category.

## Gaussian Noise Models Configuration

The gaussian noise models are configured in the `gaussian_models` dictionary. The syntax is as follows:

```python
gaussian_models = {
    ...
    "<INSTRUMENT_MODEL_NAME>": {
        "args": {"jitter_type": "<JITTER_TYPE>"},
        "param_extensions": {"instrument": {"<JITTER_PARAM_NAME>": "<PARAMETERNAME_EXTENSION>"}},
        "parametrisation": {"log10": False, "use_Baluevfactor": False},
    },
    ...
},
```
There is dictionary entry for each instrument model to which you attributed the `"gaussian"` noise model category and entry entry contains a dictionary to configure the gaussian noise model of each instrument model. 
There are two possible `jitter_type`s: `"additive"` and `"multiplicative"`. If you use `"additive"` the `"<JITTER_PARAM_NAME>"` is `"jitter"` otherwise it is `"jittermulti"` and you can select whatever `"<PARAMETERNAME_EXTENSION>"` string that you want to use (use `""` for now extension). 

The gaussian noise model category has two extra `"parametrisation"` arguments:

- `"log10"`: If set to `True` the jumping parameter will be the log10 of the jitter. 
- `"use_Baluevfactor"`: If set to `True` a normalisation factor is used in the probability density function expression according to Baluev+2009

## 1D Gaussian Process Noise Models Configuration

The 1D gaussian process noise models are configured in the `GP1D_models` dictionary. The syntax is as follows:

```python
GP1D_models = {
    "GPmodel4instrument": {
        ...
        "<INSTRUMENT_NAME>": "<GPMODEL_NAME>", 
        ...
        },
    "GPmodel_definitions": {
        ...
        "<GPMODEL_NAME>": {
            "category": "<GPMODEL_CATEGORY>",
            "param_extensions": {"GP": {
                ...
                "<GP_PARAM_NAME>": "<PARAMETERNAME_EXTENSION>", 
                ...
                }
            },
            "parametrisation": {
                ...
                "<ARGUMENT_1>": Value argument 1,
                ...
            },
        },
        ...
    },
    "jittermodel_definitions": {
        ...
        "<INSTRUMENT_NAME>": {
            "args": {"jitter_type": "<JITTER_TYPE>"},
            "param_extensions": {"instrument": {"<JITTER_PARAM_NAME>": "<PARAMETERNAME_EXTENSION>"}},
            "parametrisation": {"log10": False, "use_Baluevfactor": False},
        },
        ...
    },
}
```

For each instrument to which you attributed the `"GP1D"` noise model category. The `GP1D_models` dictionary possess three keys `"GPmodel4instrument"`, `"GPmodel_definitions"` and `"jittermodel_definitions"` all containing a dictionary. The `"GPmodel4instrument"` dictionary let you define the number of independant GP models that you will use and to which instrument model(s) they will apply. The `"GPmodel_definitions"` contains the definition of the these GP models. Finally
whatever the GP model that you decide to use, each instrument model has a jitter parameter whose behavior you can configure in the `"jittermodel_definitions"` dictionary.

In the `"GPmodel4instrument"` dictionary, there is an entry for each instrument model (`"<INSTRUMENT_NAME>"`) to which you attributed the `"GP1D"` noise model category. The value should be a string of you choice `"<GPMODEL_NAME>"`, but you need to use the same string if you want to use the same GP model for different instrument model.

In the `"GPmodel_definitions"` dictionary, there is an entry for each GP model name (`"<GPMODEL_NAME>"`) that you defined in `"GPmodel4instrument"`. Each entry contains a dictionary that define each GP model. These GP model definition dictionaries contains three keys corresponding to three dictionary: 

- `"category"`: Which define the type of GP kernel that you want to use. The categories available are provided in the table below;
- `"param_extensions"`: Which allows to define extension to the hyperparameters' name of the GP kernel. Each GP kernel category has its specific set of hyperparameters provided in the table below;
- `"parametrisation"`: Which allows to configure the parametrisation of the GP kernel. Each GP kernel category has its specific set of arguments provided in the table below. All kernel has the `"log10"` argument which is a dictionary whose keys are the hyperparameter names and whose value is a boolean defining whether you want to use the hyperparameter or its log10 has jumping parameter.

| Category | Hyperparameter names | Parametrisation arguments | Description |
|---|---|---|---|
| `"QPGeorge"` | `"A"`, `"P"`, `"tau"`, `"gamma"` | `"log10"={...}` | Quasi Periodic kernel implemented with the `george` package, see Rasmussen & Williams 2006, Roberts+2013 or Nicholson & Aigrain 2022 |
| `"QPCGeorge"` | `"A"`, `"f"`, `"P"`, `"tau"`, `"gamma"` | `"log10"={...}` | Quasi Periodic Cosine kernel implemented with the `george` package, see Perger+2021 or Nicholson & Aigrain 2022 |
| `"QPCelerite"` | `"B"`, `"C"`, `"P"`, `"L"` | `"log10"={...}` | Quasi Periodic kernel implemented with the `Celerite2` package, see Foreman-Mackey+2017 |
| `"RotationCelerite"` | `"A"`, `"P"`, `"Q0"`, `"dQ"`, `"f"` | `"log10"={...}` | Rotation kernel implemented with the `Celerite2` package, see celerite documentation |
| `"SHOCelerite"` | `"A" or "S0"`, `"rho" or "omega0"`, `"Q" or "tau"` | `"use_A=True"`, `"user_rho=True"`, `"user_Q=True"`, `"log10"={...}` | Single Harmonic Oscillator kernel implemented with the `Celerite2` package, see celerite documentation |
| `"Matern32Celerite"` | `"A"`, `"rho"` | `"log10"={...}` | Matern 3/2 kernel implemented with the `Celerite2` package, see celerite documentation |


