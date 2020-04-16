"""
author: N. Abrate.

file: makexsdata.py

description: Convert xsdir files to a single .xsdata file for Serpent-2.
"""
import os
import ProcessNDL as ndl

# define "tutorial" path
pwd = os.getcwd()
tutorialpath = os.path.join(pwd, "endf")

# define path
out_datapath = os.path.join(tutorialpath, "out")

proj = ["n", "pa"]
libname = "endf8"
# nuclear data library path final location
ndlpath = "/opt/serpent/xsdata/endfb8/acedir"
# convert xsdir into xsdata single file
ndl.convertxsdir(datapath, proj, libname, ndlpath, currpath=None)
