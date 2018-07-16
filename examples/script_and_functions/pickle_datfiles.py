#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Script template to transform the chains dat file and the acceptance fraction dat file into pickles.

@TODO:
"""
import argparse
from shutil import copyfile
from datetime import datetime
from os.path import splitext, basename
from os import remove

from source.tools.emcee_tools import read_chaindatfile, read_acceptfracdatfile, extension_pickle, pickle_stuff

# Argument parsing
parser = argparse.ArgumentParser()
parser.add_argument("chain_datfile", help="Path to the chains.dat file.", type=str)
parser.add_argument("acceptfrac_datfile", help="Path to the acceptfrac.dat file.", type=str)
parser.add_argument("--objname", help= ("Name of the studied object (used to name the pickle files)."
                                        "If not provided the object will be infered from chain_datfile"
                                        ", assuming that its name follows the following format"
                                        "objname(_*).dat."),
                    type=str, default=None)
args = parser.parse_args()

# Get current date and time
now = datetime.now()

# Copy the .dat files
dico_files = {"chain": {"original": args.chain_datfile, "copy": None},
              "acceptfrac": {"original": args.acceptfrac_datfile, "copy": None}}
for key, item in dico_files.items():
    datfile_root, datfile_ext = splitext(item["original"])
    item["copy"] = datfile_root + "_tmp_{0.year}{0.month}{0.day}{0.hour}{0.minute}{0.second}".format(now) + datfile_ext
    copyfile(item["original"], item["copy"])

if args.objname is None:
    filename_root, _ = splitext(basename(dico_files["chain"]["original"]))
    obj_name = filename_root.split("_")[0]
else:
    obj_name = args.objname

# Read the chain dat file and pickle the info
chains, lnpost, l_params = read_chaindatfile(dico_files["chain"]["copy"])
# Save chain in a pickle
pickle_stuff(chains, "{}{}".format(obj_name, extension_pickle["chain"]))
# Save lnprobability in a pickle
pickle_stuff(lnpost, "{}{}".format(obj_name, extension_pickle["lnpost"]))
# Save l_param_name in a pickle
pickle_stuff(l_params, "{}{}".format(obj_name, extension_pickle["l_param_name"]))


# Read the acceptance fraction dat file and pickle the info
acceptance_fraction = read_acceptfracdatfile(dico_files["acceptfrac"]["copy"])
# Save acceptance_fraction in a pickle
pickle_stuff(acceptance_fraction, "{}{}".format(obj_name, extension_pickle["acceptfrac"]))

# rm the copie of the files
for key, item in dico_files.items():
    remove(item["copy"])
