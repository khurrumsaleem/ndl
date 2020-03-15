# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 11:07:30 2020

@author: abrate
"""
import ProcessNDL as ndl

# datapath = "/home/abrate/endf-viii/ENDF-B-VIII.0/neutrons"
n_datapath = "Z:\\endf-viii\\ENDF-B-VIII.0\\neutrons"
pa_datapath = "Z:\\endf-viii\\ENDF-B-VIII.0\\photoat"
ar_datapath = "Z:\\endf-viii\\ENDF-B-VIII.0\\atomic_relax"

# inpath="/home/abrate/endf-viii/njoyinp/n"
# outpath="/home/abrate/endf-viii"
outpath="Z:\\endf-viii"
inpath="Z:\\endf-viii\\njoyinp\\n"
pattern = "AS-A.endf"
libname = "ENDF-B/VIII.0"
njoyver = "2016"
broad_temp = [300, 600, 900, 1200, 1500, 1800]
ndl.makeinput(n_datapath, pattern, "n", libname, broad_temp, outpath=outpath)
ndl.makeinput(pa_datapath, "AS.endf", "pa", libname, None, outpath=outpath,
              atomrelax_datapath=ar_datapath)
