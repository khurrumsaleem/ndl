"""
author: N. Abrate.

file: makeinp.py

description: Make NJOY input for neutrons and photo-atomic evaluations.
"""

import sys
import pathlib

pwd = pathlib.Path.cwd()
src = (pwd.parent).joinpath("source")
sys.path.append(str(src))
import ProcessNDL as ndl

# define "tutorial" path
pwd = pathlib.Path.cwd()
tutorialpath = pwd.joinpath("endf")
# define path
n_datapath = tutorialpath.joinpath("neutrons")
pa_datapath = tutorialpath.joinpath("photoat")
ar_datapath = tutorialpath.joinpath("atomic_relax")

# define additional arguments for NJOY input creation
outpath = tutorialpath
pattern_n = "S-A.endf"
pattern_pa = "S.endf"
libname = "ENDF-B/VIII.0"
njoyver = "2016"
broad_temp = [300]

# make input for neutron evaluations
ndl.makeinput(n_datapath, pattern_n, "n", libname, broad_temp, outpath=outpath)
# make input for photo-atomic evaluations
ndl.makeinput(pa_datapath, pattern_pa, "pa", libname, broad_temp=None,
              outpath=outpath, atomrelax_datapath=ar_datapath)
