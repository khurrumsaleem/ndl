################################
#  _   _ ______ __  __  ____   #
# | \ | |  ____|  \/  |/ __ \  #
# |  \| | |__  | \  / | |  | | #
# | . ` |  __| | |\/| | |  | | #
# | |\  | |____| |  | | |__| | #
# |_| \_|______|_|  |_|\____/  #
#                              #
################################
# Authors: N. Abrate (inspired by an Octave script by D. Caron, C. Di Gesare)
# File: ProcessNDL.py
# Description:

import os
import re
import gzip
import glob
import time as t
import numpy as np
import shutil as sh
import multiprocessing as mp
from datetime import datetime
from socket import gethostname
from operator import itemgetter
from os.path import isfile, join


# define particles synonims dict
partdict = {"n": ["neutron", "neutrons", "neutronic", "n"],
            "pa": ["photon", "photons", "photo-atomic", "photoatomic",
                   "pa"],
            "pn": ["gamma", "photo-nuclear", "photonuclear", "pn"]}


def buildacelib(inpath, libpath, data, libext, particles, njoyver=2016, 
                atom_relax=None):

    # define "out" tree
    baseoutpath = os.path.join(libpath, "out")

    if type(particles) is str:
        particles = [particles] 
    # loop over projectiles
    for part in particles:
        # define particle key
        for key, names in partdict.items():
            if part in names:
                proj = key

        # define particle-wise directory
        outpath = os.path.join(baseoutpath, proj)
        # create "out" sub-dirs
        outdirs = {"n": ["pendfdir_bin", "acedir", "xsdir", "njoyout", 
                         "njoyinp", "viewheatdir", "viewacedir"],
                   "pa": ["acedir", "xsdir", "njoyout", "njoyinp"],
                   "pn": ["pendfdir_bin", "acedir", "xsdir", "njoyout",
                          "njoyinp", "viewacedir"]}

        [mkdir(name, outpath) for name in outdirs[proj]]
    
        # gather input files
        inpfiles = [f for f in sorted(os.listdir(os.path.join(inpath, proj)))
                    if isfile(join(inpath, proj, f))
                    if f.endswith(".njoyinp")]
        # print warning for the user
        if inpfiles == []:
            print("Warning: %s is empty!" % os.path.join(inpath, proj))
    
        # change working directory
        os.chdir(outpath)
        # process input with NJOY
        for f in inpfiles:
            # FIXME make CPU-wise tmp dirs, use multiprocessing
            # move input file
            sh.move(os.path.join(inpath, proj, f), os.path.join(outpath, f))
            # define file names
            fname_tmp, ext = os.path.splitext(f)
            fname, tmp = fname_tmp.split("_")

            if libext is not None:
                endfname = fname+"."+libext
            else:
                endfname = fname
            # move ENDF-6 files in input dir
            sh.move(os.path.join(libpath, data, endfname), 
                    os.path.join(outpath, "tape20"))

            # move atomic relaxation ENDF-6 files in input dir
            if proj == "pa":
                sh.move(os.path.join(libpath, atom_relax, endfname), 
                    os.path.join(outpath, "tape21"))

            # run NJOY, then clean directory
            start_time = t.time()
            print("Processing %s..." % f.split(".")[0])
            run_njoy(f, njoyver=2016)
            move_and_clean(f, outpath, libpath, data, endfname, proj, 
                           atom_relax)
            print("DONE")
            # print elapsed time
            printime(start_time)

        # final message for the user
        print("The processed library is in %s" %outpath)

def move_and_clean(inp, path, libpath, data, endfname, proj, atom_relax=None):

    # split input name
    ZAIDT, ext = os.path.splitext(inp)
    datapath = os.path.join(libpath, data)
    if atom_relax is not None:
        atom_relax_datapath = os.path.join(libpath, atom_relax)
    else:
        atom_relax_datapath=None

    # define common dictionaries
    # neutrons dict with names of files to be kept when cleaning files
    dir_names = {"n": {datapath: "tape20", "pendfdir_bin": "tape26", "acedir":
                       "tape29", "xsdir": "tape30_1", "njoyout": "out.gz",
                       "viewheatdir": "tape35", "viewacedir": "tape34",
                       "njoyinp": inp},
                "pa": {datapath: "tape20", atom_relax_datapath: "tape21",
                       "acedir": "tape29", "xsdir": "tape30_1", 
                       "njoyout": "out.gz", "njoyinp": inp},
                "pn": {datapath: "tape20", "pendfdir_bin": "tape22", "acedir":
                       "tape29", "xsdir": "tape30_1", "njoyout": "out.gz",
                       "viewacedir": "tape34", "njoyinp": inp}}

    # neutrons dict with new names when moving files
    ext_names = {"n": {"tape20": endfname, "tape21": endfname,
                       "tape26": ".pendf", "tape29": ".ace",
                       "tape30_1": ".xsdir", "out.gz": ".out.gz",
                       "tape34": ".eps", "tape35": ".eps", inp: ".njoyinp"},
                 "pa": {"tape20": endfname, "tape21": endfname,
                        "tape29": ".ace", "tape30_1": ".xsdir",
                        "out.gz": ".out.gz", inp: ".njoyinp"},
                 "pn": {"tape20": endfname, "tape22": ".pendf",
                        "tape29": ".ace", "tape30_1": ".xsdir",
                        "out.gz": ".out.gz", "tape34": ".eps", 
                        inp: ".njoyinp"}}

    # edit xsdir default content
    find_replace = {"filename": ZAIDT+".ace", "route": "0"} 
    with open("tape30") as fold:
        with open("tape30_1", "w") as fnew:
            for line in fold:
                for key in find_replace:
                    # replace if key is in file line
                    if key in line:
                        line = line.replace(key, find_replace[key])
                # write new line in new file
                fnew.write(line)

    # loop over dictionaries
    for dirname, fname in dir_names[proj].items():
        # other files in "out" tree
        if fname != "tape20" and fname != "tape21":
            ipath = os.path.join(path, fname)
            opath = os.path.join(path, dirname, ZAIDT+ext_names[proj][fname])
            # move and rename file
            sh.move(ipath, opath)
        # ENDF-6 back to data directory
        else:
            # ENDF-6 back to data dir
            ipath = os.path.join(path, fname)
            opath = os.path.join(dirname, ext_names[proj][fname])
            sh.move(ipath, opath)

    # clean base directory from other NJOY tapes
    f_del = glob.glob(os.path.join(path, "tape*"))
    for f in f_del:
        os.remove(f)
    # remove output file
    os.remove("output")


def run_njoy(inp, njoyver=2016):
    # split input name
    fname, ext = os.path.splitext(inp)
    # run NJOY in the system
    if njoyver == 2016:
        stream = os.popen('njoy2016 < %s' % inp).read()
    elif njoyver == 2021:
        stream = os.popen('njoy2021 -i %s' % inp).read()
    else:
        print("The specified NJOY version is not available.")
        raise OSError

    # compress output stream
    with gzip.GzipFile("out.gz", mode='w') as fgz:
        fgz.write(stream.encode())


def makeinput(datapath, pattern, part, libname, broad_temp=None, outpath=None,
              atomrelax_datapath=None, njoyver=2016):

    # FIXME try glob module to simplify these lines
    # find pattern separators
    pattern, lib_extension = os.path.splitext(pattern)
    filesep = re.split(r"[ A Z AS]+", pattern)
    # join for using re.split later
    filesep = "|".join(filesep)
    # add escape character "\" in front of special character "-", if any
    filesep = filesep.replace("-", r"\-")
    # split according to separators
    keys = re.split(r"["+filesep+"]+", pattern)
    # squeeze out empty strings, if any
    keys = list(filter(None, keys))
    # make dictionary to identify keys position in filename
    patterndict = {s: ipos for ipos, s in enumerate(keys)}
    # replace A, AS and Z (if present) with \w+ for regex later use
    str_iterator = re.finditer(r"[A Z AS]+", pattern)
    str_pos = [val.span() for val in str_iterator]
    min_pos = min(str_pos, key=itemgetter(0))[0]
    max_pos = max(str_pos, key=itemgetter(1))[1]
    pattern = pattern[min_pos:max_pos]
    # store separator between AS, Z and A
    filesep = list(filter(None, re.split(r"[ A Z AS]+", pattern)))
    # join for using re.split later
    filesep = "|".join(filesep)
    # replace A, AS and Z (if present) with \w+ for regex later use
    pattern = pattern.replace("Z", "\w+").replace("AS", "\w+").replace("A",
                                                                        "\w+")
    # define general pattern
    pattern = re.compile(pattern)
    # gather all files in datapath
    endfiles = [f for f in sorted(os.listdir(datapath))
                if isfile(join(datapath, f))
                if f.endswith(lib_extension)]
    
    # print warning for the user
    if endfiles == []:
        print("Warning: %s is empty!" % datapath)
            
    # define particle key
    for key, names in partdict.items():
        if part in names:
            proj = key

    # gather atomic relaxation ENDF-6 files in datapath
    if atomrelax_datapath is None and proj == "pa":
        raise OSError("Atomic relaxation data path not provided!")
    if atomrelax_datapath is not None:
        ar_endfiles = [f for f in sorted(os.listdir(atomrelax_datapath))
                       if isfile(join(atomrelax_datapath, f))
                       if f.endswith(lib_extension)]

    outpath = mkdir("njoyinp", outpath)
    # make projectile-wise dir
    outpath = mkdir(proj, outpath)

    # generates input only for files with AS or Z inside elementdict
    for ifile, endf in enumerate(endfiles):

        # split extension
        nuclname, lib_extension = os.path.splitext(endf)
        # split according to separators
        iS, iE = re.search(pattern, endf).span()
        nuclname = nuclname[iS:iE]
        if filesep != '':
            keys = re.split(r"["+filesep+"]+", nuclname)
        else:
            keys = [nuclname]
        # get atomic number Z and atomic symbol AS
        try:  # name contains atomic symbol explicitly
            # get atomic symbol
            AS = keys[patterndict["AS"]]  # get position with dict val
            # get atomic number
            try:
                Z = ASZ_periodic_table()[AS]
            except KeyError:
                Z = -1  # if AS is not inside the dict, dummy value for Z

        except KeyError:  # name contains atomic number
            # get atomic number
            try:
                Z = keys[patterndict["Z"]]
            except KeyError:
                raise OSError("ENDF-6 file names does not contain neither" +
                              " Z nor the atomic symbol!")
            # get atomic symbol
            try:
                AS = ZAS_periodic_table()[Z]
            except KeyError:
                AS = ""  # if AS is not inside the dict, dummy value for AS
                Z = -1  # if AS is not inside the dict, dummy value for AS

        metaflag = 0
        # get mass number A
        if Z != -1 and (proj == "n" or proj == "pn"):
            try:
                A = keys[patterndict["A"]]
                # check if nuclide is metastable
                try:
                    int(A)
                    # metastable element flag
                    metaflag = None
                except ValueError:
                    # look for "m" char (metastable nuclide)
                    A = A.split("m")[0]
                    # metastable element flag
                    metaflag = 1
            except KeyError:
                raise OSError("ENDF-6 filename should contain mass number!")

            # define ASA (atomic symbol and mass number)
            if metaflag is None:
                ASA = AS+"-"+A
            else:
                ASA = AS+"-"+A+"m"
            # define ZAID (atomic and mass number)
            ZAID = str(Z)+A
            if metaflag == 1:
                ZAID = str(int(ZAID)+100)
        
            # parse MAT number from library file
            endf = os.path.join(datapath, endf)
            fp = open(endf)
            for iline, line in enumerate(fp):
                if iline == 2:
                    # read MAT number inside ENDF-6 format file
                    MAT = line[66:70]
                elif iline > 2:
                    break
            fp.close()
            # rename ENDF-6 file with PoliTo nomenclature
            sh.move(endf, os.path.join(datapath, ASA+lib_extension))

            # generate njoy input file
            for tmp in broad_temp:  # loop over temperatures
                # print message for the user
                print("Building input file for %s at T=%s K..." % (endf, tmp))
                # define file content
                njoyinp = build_njoy_deck(ZAID, ASA, MAT, tmp, proj, libname, 
                                          njoyver)
                # save file in proper directory
                fname = ASA+"_"+"{:02d}".format(int(tmp/100))
                # define complete path
                if outpath is not None:
                    fname = os.path.join(outpath, fname)
                f = open(fname+".njoyinp", "w")
                f.write(njoyinp)
                f.close()
                print("DONE \n")
        elif Z != -1 and proj == "pa":
            # rename ENDF-6 file with PoliTo nomenclature
            endf = os.path.join(datapath, endf)
            sh.move(endf, os.path.join(datapath, AS+lib_extension))
            
            # rename also atomic relaxation ENDF-6 files
            ar_endf = os.path.join(atomrelax_datapath, ar_endfiles[ifile])
            sh.move(ar_endf, os.path.join(atomrelax_datapath, AS+lib_extension))
            # print message for the user
            print("Building input file for %s..." % (endf))
            # define file content
            njoyinp = build_njoy_deck(str(Z), AS, None, None, proj, libname, 
                                      njoyver)
            # save file in proper directory
            fname = AS+"_00"
            # define complete path
            if outpath is not None:
                fname = os.path.join(outpath, fname)
            f = open(fname+".njoyinp", "w")
            f.write(njoyinp)
            f.close()
            print("DONE \n")
        else:  # dummy value of Z means fake element
            print("Skipping %s-%s. It is not an element." % (AS, Z))
            
            
def build_njoy_deck(elem, ASA, MAT, tmp, proj, libname, vers):
    # list preallocation
    lst = []
    lstapp = lst.append
    # define temperature suffix
    if tmp is not None: 
        tmpsuff = "{:02d}".format(int(tmp/100))
    # save datetime
    now = datetime.now()
    now = now.strftime("%d/%m/%Y, %H:%M:%S")
    # save host name
    hostname = gethostname()
    if proj == "n":  # fast (continuous-energy) neutron data

        # MODER module
        lstapp("moder")
        lstapp("20 -21/")  # convert tape20 in block-binary mode for efficiency
        # RECONR module
        lstapp("reconr")
        lstapp("-21 -22/")
        lstapp("/")
        lstapp("%s 2/" % MAT)
        lstapp("0.01 0.0 0.01 5.0e-7/")
        lstapp("/")
        lstapp("/")
        lstapp("0/")
        # BROADR module
        lstapp("broadr")
        lstapp("-21 -22 -23/")
        lstapp("%s 1/" % MAT)
        lstapp("0.01 2.0e6 0.01 5.0e-7/")
        lstapp("%12.5e/" % tmp)
        lstapp("0/")
        # HEATR module
        lstapp("heatr")
        lstapp("-21 -23 -24 40/")
        lstapp("%s 7 0 1 1 2/" % MAT)
        lstapp("302 303 304 318 402 443 444/")
        # GASPR module
        lstapp("gaspr")
        lstapp("-21 -24 -25/")
        # PURR module
        lstapp("purr")
        lstapp("-21 -25 -26/")
        lstapp("%s 1 5 20 64/" % MAT)
        lstapp("%12.5e/" % tmp)
        lstapp("1.0e10 1.0e4 1.0e3 1.0e2 1.0e1/")
        lstapp("0/")
        # ACER module
        lstapp("acer")
        lstapp("-21 -26 0 27 28/")
        lstapp("1 0 1 .%s/" % tmpsuff)
        lstapp("'%s, %s, NJOY%s, %s %s'/" % (ASA, libname, vers,
                                             hostname, now))
        lstapp("%s %12.5e/" % (MAT, tmp))
        lstapp("/")
        lstapp("/")
        lstapp("acer")  # re-run for QA checks
        lstapp("0 27 33 29 30/")
        lstapp("7 1 1 .%s/" % tmpsuff)
        lstapp("/")
        # VIEWR module
        lstapp("viewr")
        lstapp("33 34/")  # plot ACER output
        lstapp("viewr")
        lstapp("40 35/")  # plot HEATR output


    elif proj == "pa":  # photo-atomic data
        elem = elem+"00"
        # ACER module
        lstapp("acer")
        lstapp("20 21 0 29 30/")
        lstapp("4 1 1 .00/")
        lstapp("'%s, %s, NJOY%s, %s %s'/" % (ASA, libname, vers,
                                             hostname, now))
        lstapp(" %s/" % elem)
        # no QA checks, no ACER plot available for this kind of data (2020)

    elif proj == "pn":  # photo-nuclear data
        # FIXME: NJOY docs do not contain any pn complete example
        # MODER module
        lstapp("moder")
        lstapp("20 -21/")  # convert tape20 in block-binary mode for efficiency
        # RECONR module
        lstapp("reconr")
        lstapp("-21 -22/")
        lstapp("/")
        lstapp("%s 1 0/" % MAT)
        lstapp("0.001 0./")
        lstapp("/")
        lstapp("0/")
        # ACER module
        lstapp("acer")
        lstapp("-21 -22 0 27 28/")
        lstapp("5 0 1 .%s/" % tmpsuff)
        lstapp("'%s, %s, NJOY%s, %s %s'/" % (ASA, libname, vers,
                                             hostname, now))
        lstapp("%s/" % MAT)
        lstapp("acer")  # re-run for QA checks
        lstapp("0 27 33 29 30/")
        lstapp("7 1 1 .%s/" % tmpsuff)
        lstapp("/")
        # VIEWR module
        lstapp("viewr")
        lstapp("33 34/")  # plot ACER output

    # add STOP card in whatever input deck
    lstapp("stop")
    # concatenate list with "\n" into a string
    outstr = "\n".join(lst)
    return outstr


def ASZ_periodic_table():
    # define atomic symbols list
    AS = ['H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne', 'Na', 'Mg',
          'Al', 'Si', 'P', 'S', 'Cl', 'Ar', 'K', 'Ca', 'Sc', 'Ti', 'V', 'Cr',
          'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se', 'Br',
          'Kr', 'Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd',
          'Ag', 'Cd', 'In', 'Sn', 'Sb', 'Te', 'I', 'Xe', 'Cs', 'Ba', 'La',
          'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er',
          'Tm', 'Yb', 'Lu', 'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au',
          'Hg', 'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn', 'Fr', 'Ra', 'Ac', 'Th',
          'Pa', 'U', 'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 'Es', 'Fm', 'Md',
          'No', 'Lr', 'Rf', 'Db', 'Sg', 'Bh', 'Hs', 'Mt', 'Ds', 'Rg', 'Cn',
          'Nh', 'Fl', 'Mc', 'Lv', 'Ts', 'Og']
    # atomic number
    Z = np.arange(1, 119)
    # define dict
    periodictable = dict(zip(AS, Z))
    # return element dict
    return periodictable


def ZAS_periodic_table():
    # define atomic symbols list
    AS = ['H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne', 'Na', 'Mg',
          'Al', 'Si', 'P', 'S', 'Cl', 'Ar', 'K', 'Ca', 'Sc', 'Ti', 'V', 'Cr',
          'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se', 'Br',
          'Kr', 'Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd',
          'Ag', 'Cd', 'In', 'Sn', 'Sb', 'Te', 'I', 'Xe', 'Cs', 'Ba', 'La',
          'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er',
          'Tm', 'Yb', 'Lu', 'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au',
          'Hg', 'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn', 'Fr', 'Ra', 'Ac', 'Th',
          'Pa', 'U', 'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 'Es', 'Fm', 'Md',
          'No', 'Lr', 'Rf', 'Db', 'Sg', 'Bh', 'Hs', 'Mt', 'Ds', 'Rg', 'Cn',
          'Nh', 'Fl', 'Mc', 'Lv', 'Ts', 'Og']
    # atomic number
    Z = np.arange(1, 119)
    # define dict
    periodictable = dict(zip(Z, AS))
    # return element dict
    return periodictable


def mkdir(dirname, path):
    if path is None:
        path = dirname
    else:
        path = os.path.join(path, dirname)
    os.makedirs((path), exist_ok=True)
    return path


def printime(start_time):

    dt = t.time() - start_time
    if dt < 60:
        print("Elapsed time %f s." % dt)
    elif dt >= 60:
        print("Elapsed time %f m." % dt/60)
    elif dt >= 3600:
        print("Elapsed time %f h." % dt/3600)
        
        