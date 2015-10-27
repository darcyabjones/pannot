#! /usr/bin/env python3

from __future__ import print_function

program = "locatorp"
version = "0.1.0"
author = "Darcy Jones"
date = "1 October 2015"
email = "darcy.ab.jones@gmail.com"
short_blurb = (
    'Parses output from SignalP, TargetP, SecretomeP, and TMHMM and outputs '
    'probable cellular locations.'
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

split_regex = re.compile(r'\s+')

def inhandler(fp, mode='r'):
    if fp == sys.stdin or fp == '-':
        return sys.stdin
    else:
        return open(fp, mode)

def outhandler(fp, mode='w'):
    if fp == sys.stdou or fp == '-':
        return sys.stdout
    else:
        return open(fp, mode)

def signalp_handler(handle):
    cols = [
        ('name', str),
        ('cmax', float),
        ('cmax_pos', int),
        ('ymax', float),
        ('ymax_pos', int),
        ('smax', float),
        ('smax_pos', int),
        ('smean', float),
        ('d', float),
        ('signal_peptide', str),  # ? column
        ('dmaxcut', float),
        ('networks_used', str),
        ]
    i = 0
    for line in handle:
        if line.startswith('#'):
            continue
        line = split_regex.split(line.strip)
        l = dict()
        for (name, type_), val in zip(cols, line):
            if name == 'signal_peptide':
                l[name] = True if val == 'Y' else False
            else:
                l[name] = type_(val)
        yield i, l
        i += 1

def secretomep_handler(handle):
    cols = [
        ('name', str),
        ('nnscore', float),
        ('odds', float),
        ('weighted', float),
        ('warning', float),
        ]
    i = 0
    for line in handle:
        if line.startswith('#'):
            continue
        line = split_regex.split(line.strip)
        l = dict()
        for (name, type_), val in zip(cols, line):
            l[name] = type_(val)
        yield i, l
        i += 1

def targetp_handler(handle):
    cols = [
        ('name', str),
        ('len', int),
        ('ctp', float),
        ('mtp', float),
        ('sp', float),
        ('other', float),
        ('loc', str),
        ('rc', int),
        ('tplen', int),
        ]
    i = 0
    for line in handle:
        if line.startswith('#'):
            continue
        line = split_regex.split(line.strip)
        if len(line) == 8:
            cTP = cols.pop(2)
        l = dict()
        for (name, type_), val in zip(cols, line):
            if name == 'tplen' and val == '-':
                l[name] = None
            if name == 'loc' and val == '_':
                l[name] = None
            else:
                l[name] = type_(val)
        yield i, l
        i += 1

def tmhmm_handler(handle):
    cols = [
        ('name', str),
        ('program', str),
        ('location', str),
        ('start', int),
        ('end', int),
        ]
    i = 0
    for line in handle:
        if line.startswith('#'):
            continue
        line = split_regex.split(line.strip)
        l = dict()
        for (name, type_), val in zip(cols, line):
            l[name] = type_(val)
        yield i, l
        i += 1

def out_writer(line, sep='\t'):
    cols = [
        'name',
        'location'
        ]
    line = list()
    for col in cols:
        if line[col] == None:
            line.append('')
        else:
            line.append(str(line[col]))
    return sep.join(line)

def main(signalp, secretomep, tmhmm, targetp, outfile, secretomep_thres=0.8):
    targetp_table = list()
    secretomep_table = list()
    signalp_table = list()
    tmhmm_table = list()

    names = defaultdict(lambda: defaultdict(list))

    # Process signalp
    with inhandler(signalp) as handle:
        for i, line in signalp_handler(handle):
            signalp_table.append(line)
            names[line['name']]['signalp'].append(i)

    # Process secretomep
    with inhandler(secretomep) as handle:
        for i, line in secretomep_handler(handle):
            secretomep_table.append(line)
            names[line['name']]['secretomep'].append(i)

    # Process targetp
    with inhandler(targetp) as handle:
        for i, line in targetp_handler(handle):
            targetp_table.append(line)
            names[line['name']]['targetp'].append(i)

    # Process tmhmm
    with inhandler(tmhmm) as handle:
        for i, line in tmhmm_handler(handle):
            tmhmm_table.append(line)
            names[line['name']]['tmhmm'].append(i)

    for name, d in names.items():
        signal = False
        for line in d['signalp']:
            signal = signalp_table[line]['signal_peptide']
            if signal:
                break

        secreted = False
        for line in d['secretomep']:
            secreted = secretomep_table[line]['nnscore'] >= secretomep_thres
            if secreted:
                break

        trasmembrane = False
        




    return
############################ Argument Handling ###############################

if __name__== '__main__':
    arg_parser = argparse.ArgumentParser(
      description=license,
      )
    arg_parser.add_argument(
        "-s", "--signalp",
        help=""
        )
    arg_parser.add_argument(
        "-e", "--secretomep",
        help=""
        )
    arg_parser.add_argument(
        "-t", "--tmhmm",
        help=""
        )
    arg_parser.add_argument(
        "-a", "--targetp",
        help=""
        )
    arg_parser.add_argument(
        "-o", "--outfile",
        default='-',
        help="Default is '-' (stdout)."
        )
    args = arg_parser.parse_args()

    main(**args.__dict__)
