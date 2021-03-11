"""
author: N. Abrate.

file: makelib.py

description: Build ACE library for Serpent-2.
"""

import sys
import pathlib

pwd = pathlib.Path.cwd()
src = (pwd.parent).joinpath("source")
sys.path.append(str(src))

import ProcessNDL as ndl

# define "tutorial" path
pwd = pathlib.Path.cwd()
datapath = pwd.joinpath("endf")

# absolute path of NJOY input
inpath = datapath.joinpath("njoyinp")

# generate neutron library
ndl.buildacelib(str(inpath), str(datapath), "neutrons", "endf",
                ["n"], copyflag=True, np=12)  # np is the number of CPUs

# generate photo-atomic library
ndl.buildacelib(str(inpath), str(datapath), "photoat", "endf", ["pa"],
                atom_relax="atomic_relax", np=12)
