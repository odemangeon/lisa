#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Script template to visualise the chains contained in the .dat files produced by the explore function

@TODO:
"""
import argparse
from matplotlib.pyplot import savefig, show
from shutil import copyfile
from datetime import datetime
from os.path import splitext
from os import remove

from source.tools.emcee_tools import read_datfile, plot_chains

# Argument parsing
parser = argparse.ArgumentParser()
parser.add_argument("chain_datfile", help="Path to the chain.dat file.", type=str)
parser.add_argument("--outfile", help="Path of the output file containing the trace plot.", type=str, default="trace_plot.png")
args = parser.parse_args()

# Get current date and time
now = datetime.now()

# Copy the .dat file
datfile_root, datfile_ext = splitext(args.chain_datfile)
copied_datefile =  datfile_root + "_tmp_{0.year}{0.month}{0.day}{0.hour}{0.min}{0.sec}".format(now) + datfile_ext
copyfile(args.chain_datfile, copied_datefile)

# Read the chain dat file
chains, lnpost, l_params = read_datfile(copied_datefile)

# Produce trace plot
plot_chains(chains, lnpost, l_params)
savefig(args.outfile)
show()

# rm the copie of the files
remove(copied_datefile)
