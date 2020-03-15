# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 11:07:30 2020

@author: abrate
"""
import ProcessNDL as ndl

datapath = "/home/abrate/endf-viii/ENDF-B-VIII.0/neutrons"
inpath="/home/abrate/endf-viii/njoyinp/n"
outpath="/home/abrate/endf-viii"
# datapath = "Z:\\endf-viii\\ENDF-B-VIII.0\\neutrons"
# outpath="Z:\\endf-viii"
# inpath="Z:\\endf-viii\\njoyinp\\n"
pattern = "n-Z_AS_A.endf"
libname = "ENDF-B/VIII.0"
njoyver = "2016"
proj = "n"
ndl.buildacelib(inpath, datapath, libext="endf", outpath=outpath, njoyver=2016)