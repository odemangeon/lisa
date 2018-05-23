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

parser = argparse.ArgumentParser()
parser.add_argument("datfile", help="Path to the .dat file.", type=str)
parser.add_argument("--outfile", help="Path of the output file containing the trace plot.", type=str, default="trace_plot.png")
args = parser.parse_args()

df = pd.read_table(args.datfile, sep="\s+", header=0)
nb_walker = df["i_walker"].max() - df["i_walker"].min() + 1
df["iteration"] = np.array(df.index) // 88

print("Current iteration number: {}".format(df["iteration"].max()))

df.set_index(['i_walker', 'iteration'], inplace=True)

nb_param = len(df.columns)

plot_height=2
plot_width=8
fig, ax = pl.subplots(nrows=nb_param, figsize=(plot_width, nb_param * plot_height))
for ii, param in enumerate(df.columns):
    ax[ii].set_title(param)
    for walker in range(nb_walker):
        ax[ii].plot(df[param].loc[walker])
fig.tight_layout()
fig.savefig(args.outfile)
pl.show()
