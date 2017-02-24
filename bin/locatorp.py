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
    if fp == sys.stdout or fp == '-':
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
        line = split_regex.split(line.strip())
        l = dict()
        for (name, type_), val in zip(cols, line):
            if name == 'signal_peptide':
                l[name] = True if val == 'Y' else False
            else:
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
        line = split_regex.split(line.strip())
        if len(line) == 8 and len(cols) == 9:
            cTP = cols.pop(2)
        if len(line) <= 1:
            continue
        l = dict()
        for (name, type_), val in zip(cols, line):
            if name == 'tplen' and val == '-':
                l[name] = None
            elif name == 'loc' and val == '_':
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
    prop_split = re.compile(r':\s*')
    i = 0
    for line in handle:
        props = None
        if line.startswith('#'):
            line = line.lstrip('#').strip().split(' ', 1)
            name, prop = line
            if prop == 'POSSIBLE N-term signal sequence':
                continue
            key, val = prop_split.split(prop)
            val = float(val)
            yield None, {'name': name}, {key: val}
            continue

        line = split_regex.split(line.strip())
        l = dict()
        for (name, type_), val in zip(cols, line):
            l[name] = type_(val)
        yield i, l, props
        i += 1

def out_writer(line, sep='\t'):
    cols = [
        'name',
        'location',
        'signal',
        'membrane',
        ]
    outline = list()
    for col in cols:
        if line[col] == None:
            outline.append('')
        else:
            outline.append(str(line[col]))
    return sep.join(outline)

def main(signalp, tmhmm, targetp, outfile, secretomep_thres=0.8):
    targetp_table = list()
    signalp_table = list()
    tmhmm_table = list()

    names = defaultdict(lambda: defaultdict(list))
    tmhmm_props = defaultdict(dict)

    # Process signalp
    with inhandler(signalp) as handle:
        for i, line in signalp_handler(handle):
            signalp_table.append(line)
            names[line['name']]['signalp'].append(i)

    # Process targetp
    with inhandler(targetp) as handle:
        for i, line in targetp_handler(handle):
            targetp_table.append(line)
            names[line['name']]['targetp'].append(i)

    # Process tmhmm
    with inhandler(tmhmm) as handle:
        for i, line, props in tmhmm_handler(handle):
            if props is not None:
                tmhmm_props[line['name']].update(props)
                continue
            tmhmm_table.append(line)
            names[line['name']]['tmhmm'].append(i)

    with outhandler(outfile) as handle:
        cols = {
            'name': 'name',
            'location': 'location',
            'signal': 'signal',
            'membrane': 'membrane'
            }
        handle.write(out_writer(cols) + '\n')

        for name, d in names.items():
            signal = False
            for line in d['signalp']:
                signal = signalp_table[line]['signal_peptide']
                if signal:
                    break

            mito_target = False
            secreted_target = False
            for line in d['targetp']:
                mito_target = targetp_table[line]['loc'] == 'M'
                secreted_target = targetp_table[line]['loc'] == 'S'

            transmembrane = False
            tmhmmd = tmhmm_props[name]
            """
            try:
                if (tmhmmd['Number of predicted TMHs'] == 1 and
                        tmhmmd['Exp number, first 60 AAs'] >= 10):
                    pass
                elif tmhmmd['Exp number of AAs in TMHs'] > 18:
                    transmembrane = True
            except KeyError:
                pass
                # No predicted transmembrane regions
            """
            num_tm = 0
            firstn = 60
            first_thres = 10
            firstaa = set(range(0, firstn))
            for line in d['tmhmm']:
                l = tmhmm_table[line]
                if l['location'] == 'TMhelix':
                    num_tm += 1
                    tm_range = set(range(l['start'] -1, l['end']))
                    firstaa -= tm_range

            if all([num_tm == 1,
                    firstn - len(firstaa) > first_thres,
                    signal]):
                pass
            elif num_tm > 0:
                transmembrane = True


            line = {'name': name, 'membrane': transmembrane, 'signal': signal}
            if secreted_target:
                line['location'] = 'secreted'
            elif mito_target:
                line['location'] = 'mitochondrial'
            else:
                line['location'] = None

            handle.write(out_writer(line) + '\n')
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
