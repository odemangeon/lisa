# Instruments and datasets

## Instrument categories, instrument name and instrument models

`Lisa` allows to analyse different categories of datasets:

- Light-curves: `"LC"`;
- Radial velocities: `"RV"`.

These are the `instrument categories`. Whatever the category, `lisa` use `instrument name`, which are the name of the instrument providing this category of data. For example for the `"LC"` category, instrument names can be `"CHEOPS"`, `"Kepler"` or `"K2"`. For the `"RV"` category, instrument names can be `"ESPRESSO"`, `"HARPS"` or `"SOPHIE"`. All of these instruments are not entirely stable, meaning that you might want to model the instrumental behavior differently for different dataset even if they come from the same instrument. One example of this is the classical RV offset that one need to use when analysing data from a RV spectrograph after an important technical intervention. Another example is the baseline offset that needs to be modelled when analysing two separate observation from `"CHEOPS"` or any relative high precision, high cadence photometer due to the lack of absolute flux calibration. This is why lisa uses `instrument models`. A given instrument can be modelled by several instrument models.

Instrument model names follow a specific syntax:

`"<INSTRUMENT_CATEGORY>_<INSTRUMENT_NAME>_<INSTRUMENT_MODEL_EXTENSION>"`

As mentioned previously `<INSTRUMENT_CATEGORY>` can be either `LC` or `RV`. `<INSTRUMENT_NAME>` can be whatever you want, but it is advised to keep it explicit, for example `CHEOPS`, `ESPRESSO`.
`<INSTRUMENT_MODEL_EXTENSION>` can be whatever you want. Possible examples are `inst`, `inst0`, ...
So examples of instrument model names are `"LC_CHEOPS_inst0"`, `"RV_ESPRESSO_18"`.

## Datasets

Similarly, the names of the datasets need to follow a specific format:

`"<INSTRUMENT_CATEGORY>_<INSTRUMENT_NAME>_<DATASET_NUMBER>"`

We already discussed `<INSTRUMENT_CATEGORY>` and `<INSTRUMENT_NAME>`. They carry the same meaning and need to match between a dataset and the instrument model used to model it. `<DATASET_NUMBER>` is the index of the dataset, as a given instrument can yield multiple datasets.

The name of the dataset input files needs to follow this convention with the .txt extension.

## Definition of the datasets and their instrument models

In the configuration file, the list `l_dataset` defines the list of all the datasets that `lisa` has to use.
The dictionary `d_inst_model_def` defines which instrument model to use for each dataset.

It's syntaxt is as follows:
```python
d_inst_model_def = {
    ...
    "<INSTRUMENT_CATEGORY>": {
        ...
        "<INSTRUMENT_NAME>": {
            ...
            "<DATASET_NUMBER>": "<INSTRUMENT_MODEL_EXTENSION>",
            ...
        },
    },
    ...
}
```

Within a given instrument name entry, using the same instrument model extension for several dataset numbers means that the same instrument model will be used to model these datasets.