# Quick Start

## Running lisa

`lisa` is designed to produce models, posteriors, likelihoods and priors for the analysis of exoplanet datasets.

The minimal workflow to use `lisa` is simple:
```python
from lisa import Posterior

post_instance = Posterior()
post_instance.configure_posterior(path_config_file="config_file.py")
```

The command `Posterior()` creates an empty 'Posterior' instance and its method `configure_posterior(path_config_file="config_file.py")` configures it. `config_file.py` is the name of the [configuration file](user-guide/configfile_overview.md) which contains the full configuration: the datasets to model, the model, likelihoods, priors parametrisation. If it exists lisa will try to load the configuration that it contains. If it doesn't, it will ask you to create it from scratch and guide you through the process of filling its content.

Once the Posterior instance is configured you can generate all the functions (models, priors, likelihoods, posteriors) using:
```python
post_instance.create_allfunctions()
```
and *Voilà*!

## Fitting data using lisa

Creating models, likelihoods, priors and posteriors is nice, but it's not a finality. What everybody ultimately wants is to use interpret, infer, fit data. For that you need a ['fitting algorithm'](user-guide/inference_overview.md).
`lisa` can be used in conjunction with any 'fitting algorithm' that use posteriors, likelihood, priors or forward model functions.
If you are already very familiar with such a fitting algorithm you only need to know [how to access the function that lisa generate and how to use them](user-guide/lisa_functions.md)). You can also find navigated to the description of one way to use lisa with [emcee](user-guide/emcee.md) and [dynesty](user-guide/dynesty.md).

Otherwise, the fastest way to learn the workflow is to run one of the examples included in the repository. Go the [overview of the examples available](user-guide/examples_overview.md) and select the example that matches the type of data you want to analyse and the type of inference that you want to make.
