#!/usr/bin/python
# -*- coding:  utf-8 -*-
import numpy as np

import source.posterior.core.prior.prior_function as pf1
import susana.prior as pf2

from IPython import get_ipython
ipython = get_ipython()

f1 = pf1.UniformPrior(0., 1.).create_logpdf()
f2 = pf2.UniformPrior(0., 1.)

print("Timeit results for UniformPrior:")
print("Ours:")
ipython.magic("timeit f1(0.5)")
print("Suzanne's:")
ipython.magic("timeit f2(0.5)")

f1 = pf1.NormalPrior(0., 1.).create_logpdf()
f2 = pf2.NormalPrior(0., 1., lims=[-np.inf, np.inf])

print("\nTimeit results for NormalPrior:")
print("Ours:")
ipython.magic("timeit f1(0.5)")
print("Suzanne's:")
ipython.magic("timeit f2(0.5)")

f1 = pf1.LogNormPrior(0.1, 100.).create_logpdf()
f2 = pf2.LogNormPrior(0.1, 100., lims=[-np.inf, np.inf])

print("\nTimeit results for LogNormPrior:")
print("Ours:")
ipython.magic("timeit f1(1.)")
print("Suzanne's:")
ipython.magic("timeit f2(1.)")

f1 = pf1.JeffreysPrior(0.1, 100.).create_logpdf()
f2 = pf2.JeffreysPrior(0.1, 100.)

print("\nTimeit results for JeffreysPrior:")
print("Ours:")
ipython.magic("timeit f1(1.)")
print("Suzanne's:")
ipython.magic("timeit f2(1.)")

f1 = pf1.SinePrior(0., 180.).create_logpdf()
f2 = pf2.SinePrior(0., 180.)

print("\nTimeit results for SinePrior:")
print("Ours:")
ipython.magic("timeit f1(1.)")
print("Suzanne's:")
ipython.magic("timeit f2(1.)")
