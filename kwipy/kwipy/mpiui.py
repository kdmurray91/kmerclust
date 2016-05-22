# Copyright 2016 Kevin Murray <spam@kdmurray.id.au>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function, division, absolute_import

from mpi4py import MPI
from docopt import docopt
import numpy as np
import numexpr as ne
from pymer import CountMinKmerCounter
import bcolz

import itertools as itl
from glob import glob
import os
from os import path
import re
from sys import stderr, stdout

from .logging import (
    progress,
    info,
    warn,
)
from .utils import (
    calc_kernel,
    count_reads,
    stripext,
)


def count_mpi_main():
    cli = '''
    USAGE:
        kwipy-count-mpi [options] OUTDIR READFILES ...

    OPTIONS:
        -k KSIZE    Kmer length [default: 20]
        -v CVLEN    Count vector length [default: 1e9]

    Counts k-mers into individual count vectors, parallelised using MPI.

    Will use about 6 * CVLEN bytes of RAM.
    '''

    opts = docopt(cli)
    k = int(opts['-k'])
    cvsize = int(float(opts['-v']))
    outdir = opts['OUTDIR']
    readfiles = opts['READFILES']

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()

    if rank == 0:
        size = comm.Get_size()
        if size > len(readfiles):
            warn('Number of MPI ranks is greater than number of comparisons')
            warn('This is harmless but silly')
        pieces = [list() for x in range(size)]
        for i, readfile in enumerate(readfiles):
            pieces[i % size].append(readfile)
    else:
        pieces = None

    our_readfiles = comm.scatter(pieces, root=0)

    for readfile in our_readfiles:
        base = stripext(readfile, ['fa', 'fq', 'fasta', 'fastq', 'gz', ])
        outfile = path.join(outdir, base + '.kct')
        counts = count_reads([readfile, ], k=k, cvsize=cvsize)
        counts.save(outfile)


def kernel_mpi_main():
    cli = '''
    USAGE:
        kwipy-kernel-mpi [options] OUTDIR WEIGHTFILE COUNTFILES ...

    OPTIONS:
        -c      Resume previous calculation to OUTDIR

    '''
    opts = docopt(cli)
    outdir = opts['OUTDIR']
    weightfile = opts['WEIGHTFILE']
    countfiles = opts['COUNTFILES']
    resume = opts['-c']

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()

    pairs = list(itl.combinations_with_replacement(countfiles, 2))

    if rank == 0:
        if resume:
            existing_kernlogs = glob(path.join(outdir, 'kernellog_*'))
            pairs_done = set()
            for kl in existing_kernlogs:
                with open(kl) as fh:
                    for line in fh:
                        a, b, kern = line.strip().split('\t')
                        pairs_done.add((a, b))
            pairs = pairs.filter(lambda x: x not in pairs_done)
        size = comm.Get_size()
        if size > len(pairs):
            warn('Number of MPI ranks is greater than number of comparisons')
            warn('This is harmless but silly')
        pieces = [list() for x in range(size)]
        for i, pair in enumerate(pairs):
            pieces[i % size].append(pair)
    else:
        pieces = None

    pairs = comm.scatter(pieces, root=0)

    outfile = path.join(outdir, 'kernellog_{}'.format(rank))
    if not resume:
        with open(outfile, 'w') as fh:
            pass

    for afile, bfile in pairs:
        a, b, k = calc_kernel(weightfile, (afile, bfile))
        print(a, b, k)
        with open(outfile, 'a') as kfh:
            print(a, b, k, sep='\t', file=kfh)