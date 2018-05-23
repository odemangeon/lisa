#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Script template to visualise the chains contained in the .dat files produced by the explore function

@TODO:
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as pl
import argparse
from matplotlib.pyplot import savefig

from source.tools.emcee_tools import read_datfile, plot_chains, show

parser = argparse.ArgumentParser()
parser.add_argument("datfile", help="Path to the .dat file.", type=str)
parser.add_argument("--outfile", help="Path of the output file containing the trace plot.", type=str, default="trace_plot.png")
args = parser.parse_args()

chains, lnpost, l_params = read_datfile(args.datfile)

plot_chains(chains, lnpost, l_params)
savefig(args.outfile)
show()
