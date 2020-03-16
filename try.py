import ProcessNDL as ndl

# absolute path of nuclear data library
datapath = "/home/abrate/endf-viii/ENDF-B-VIII.0"
# absolute path of NJOY input
inpath="/home/abrate/endf-viii/njoyinp"


# generate photo-atomic library
ndl.buildacelib(inpath, datapath, "photoat", "endf", ["pa"], 
                atom_relax="atomic_relax")

# generate neutron library
ndl.buildacelib(inpath, datapath, "neutrons", "endf", ["n"])