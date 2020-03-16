import ProcessNDL as ndl

# absolute path of nuclear data library
datapath = "/home/abrate/endf-viii/ENDF-B-VIII.0"
# absolute path of NJOY input
inpath="/home/abrate/endf-viii/njoyinp"

# number of CPUs to perform the job
np = 16

# generate neutron library
ndl.buildacelib(inpath, datapath, "neutrons", "endf", ["n"])