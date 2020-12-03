"""
author: N. Abrate.

file: runBOXR2COV.py

description:
"""
import os
import itertools
import subprocess
import shutil as sh
from ProcessNDL import parseENDF6

def execute(commands):
    # execute job in the shell
    process = subprocess.Popen('./boxr2cov1000.exe', stdout=subprocess.PIPE,
                               stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                               shell=True, encoding='utf8')
    # communicate with process
    stream, stderr = process.communicate('\n'.join(commands) + '\n')

    # write output to file
    with open('boxr2cov1000.out', 'w') as out:
        out.write(stream)
    # write output to file
    with open('boxr2cov1000.err', 'w') as out:
        out.write(stderr)


if __name__ == '__main__':
    pwd = os.getcwd()
    # nuclides ZAid
    # zaid = [942390, 942400, 942410, 942420, 922380]
    nuclides = [922340, 922350, 922360, 942380, 952410]
    # temperatures [K]
    # temp = [600, 900, 1200]
    temp = [600]
    # MT reactions
    MT = [18, 102]
    # nuclides id
    MTs = [p for p in itertools.combinations_with_replacement(MT, r=2)]
    # define error message
    errmsg = '***ERROR IN BOXR***CANNOT FIND ITYPE,MAT,MT,MAT1,MT1'

    for za in nuclides:
        for t in temp:
            cwd = os.path.join(pwd, (os.path.join('%d' % za, '%dK' % t)))
            # move .exe file, enter dir
            sh.copyfile(os.path.join(pwd, 'boxr2cov1000.exe'),
                        os.path.join(cwd, 'boxr2cov1000.exe'))
            # parse MAT number
            _, mat, _, _ = parseENDF6(os.path.join(pwd, 'tape20'))
            os.chdir(cwd)
            args = ['tape78', '', '', 'tmp', '0,0']
            for m1, m2 in MTs:
                args[1] = 'MT%dMT%d' % (m1, m2)
                args[2] = '3,%d,%d,%d,%d' % (mat, m1, mat, m2)
                # execute
                execute(args)
            # remove 'tmp'
            for m1, m2 in MTs:
                with open('MT%dMT%d' % (m1, m2)) as f:
                    for x in range(2):
                        head = next(f)
                if errmsg in head:
                    os.remove('MT%dMT%d' % (m1, m2))

            # remove executable
            os.remove('boxr2cov1000.exe')
            # remove 'tmp'
            try:
                os.remove('tmp')
            except FileNotFoundError:
                pass
            os.chdir(pwd)
