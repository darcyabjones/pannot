#! /usr/bin/env python3

from __future__ import print_function

program = "splitter"
version = "0.1.0"
author = "Darcy Jones"
date = "1 October 2015"
email = "darcy.ab.jones@gmail.com"
short_blurb = (
    'A simple script that parses output from '
    '[tandem repeat finder (TRF)](https://tandem.bu.edu/trf/trf.html) '
    'and returns the corresponding GFF3 file.\n'
    )
license = (
    '{program}-{version}\n'
    '{short_blurb}\n\n'
    'Copyright (C) {date},  {author}'
    '\n\n'
    'This program is free software: you can redistribute it and/or modify '
    'it under the terms of the GNU General Public License as published by '
    'the Free Software Foundation, either version 3 of the License, or '
    '(at your option) any later version.'
    '\n\n'
    'This program is distributed in the hope that it will be useful, '
    'but WITHOUT ANY WARRANTY; without even the implied warranty of '
    'MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the '
    'GNU General Public License for more details.'
    '\n\n'
    'You should have received a copy of the GNU General Public License '
    'along with this program. If not, see <http://www.gnu.org/licenses/>.'
    )

license = license.format(**locals())

############################ Import all modules ##############################

import os
from os.path import split as psplit
from os.path import splitext as splitext
import re
import argparse
import sys
from collections import defaultdict

################################## Classes ###################################

start_regex = re.compile(r'>')

def inhandler(fp, mode='r'):
    if fp == sys.stdin or fp == '-':
        return sys.stdin
    else:
        return open(fp, mode)

def main(infile, prefix, num_records, no_write=False, verbose=False):
    num_records = int(num_records)
    d = os.listdir(psplit(prefix)[0])
    d = [f for f in d if f.startswith(psplit(prefix)[1])]
    d = [int(splitext(f)[0].split('-')[-1]) for f in d if f.endswith('.fasta')]
    if len(d) > 0:
        chunk_num = max(d) + 1
    else:
        chunk_num = 1

    filepaths = list()
    with inhandler(infile, mode='rU') as inhandle:
        record_num = 0
        lines = list()
        for line in inhandle:
            line = line.strip()
            if line == '':
                continue
            if start_regex.match(line) is not None:
                if record_num >= num_records:
                    fp = prefix + '-' + str(chunk_num) + '.fasta'
                    if not no_write:
                        with open(fp, 'w') as handle:
                            handle.write('\n'.join(lines))
                    filepaths.append(fp)
                    chunk_num += 1
                    record_num = 0
                    lines = list()
                record_num += 1
            lines.append(line)
        fp = prefix + '-' + str(chunk_num) + '.fasta'
        if not no_write:
            with open(fp, 'w') as handle:
                handle.write('\n'.join(lines))
        filepaths.append(fp)

    if verbose:
        print(' '.join(filepaths))

    return

############################ Argument Handling ###############################

if __name__== '__main__':
    arg_parser = argparse.ArgumentParser(
      description=license,
      )
    arg_parser.add_argument(
        "-i", "--infile",
        default='-',
        help="Input TRF dat file. Default is '-' (stdin)"
        )
    arg_parser.add_argument(
        "-n",
        dest='num_records',
        default=100,
        help=""
        )
    arg_parser.add_argument(
        "-p","--prefix",
        default='split',
        help=""
        )
    arg_parser.add_argument(
        "-w","--no-write",
        dest='no_write',
        default=False,
        action='store_true',
        help=""
        )
    arg_parser.add_argument(
        "-v","--verbose",
        default=False,
        action='store_true',
        help=""
        )

    args = arg_parser.parse_args()

    main(**args.__dict__)
