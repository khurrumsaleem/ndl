# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 11:07:30 2020

@author: abrate
"""
import ProcessNDL as ndl

# datapath = "/home/abrate/endf-viii/ENDF-B-VIII.0/neutrons"
datapath = "Z:\\endf-viii\\ENDF-B-VIII.0\\neutrons"
# inpath="/home/abrate/endf-viii/njoyinp/n"
# outpath="/home/abrate/endf-viii"
outpath="Z:\\endf-viii"
inpath="Z:\\endf-viii\\njoyinp\\n"
pattern = "AS-A.endf"
libname = "ENDF-B/VIII.0"
njoyver = "2016"
proj = "n"
broad_temp = [300, 600, 900, 1200, 1500, 1800]
ndl.makeinput(datapath, pattern, proj, libname, broad_temp, outpath=outpath)
# ndl.buildacelib(inpath, datapath, libext="endf", outpath=outpath, njoyver=2016)