"""
author: N. Abrate.

file: makelib.py

description: Convert xsdir files to a single .xsdata file for Serpent-2.
"""
import os
import ProcessNDL as ndl

# define "tutorial" path
pwd = os.getcwd()
datapath = os.path.join(pwd, "endf")

# absolute path of NJOY input
inpath = os.path.join(pwd, "njoyinp")

# generate neutron library
ndl.buildacelib(inpath, datapath, "neutrons", "endf", ["n"], copyflag=True,
                np=6)

# generate photo-atomic library
ndl.buildacelib(inpath, datapath, "photoat", "endf", ["pa"], atom_relax="atomic_relax",
                np=6)
