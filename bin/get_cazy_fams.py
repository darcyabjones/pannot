#! /usr/bin/env python3

from __future__ import print_function

program = "get_cazy_fams"
version = "0.1.0"
author = "Darcy Jones"
date = "1 October 2015"
email = "darcy.ab.jones@gmail.com"
short_blurb = (
    ''
    )
license = (
    '{program}-{version}\n'
    '{short_blurb}\n\n'
    'Copyright (C) {date}, {author}'
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

from ipsclasses import InterproscanResult


################################## Functions #################################

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



def fam_line(line):
    cols = [
        'family',
        'domain',
        'class',
        'note',
        'activities',
        ]
    fam_map = {
        'Cellulosome': 'Cellulosome',
        'GH': 'Glycoside Hydrolase',
        'GT': 'Glycosyl hydrolase',
        'PL': 'Polysaccharide lyase',
        'CE': 'Carbohydrate esterase',
        'AA': 'CAZyme auxiliary redox enzyme',
        'CBM': 'Carbohydrate-binding module',
        }
    line = line.rstrip('\n').split('\t')
    record = dict()
    for col, val in zip(cols, line):
        record[col] = val
    record['classname'] = fam_map[record['class']]
    return record

def match_line(line):
    def _parse_str(col, val):
        return {col: val}

    def _parse_int(col, val):
        return {col: int(val)}

    def _parse_float(col, val):
        return {col: float(val)}

    def _parse_fam(col, val):
        fam, hmm = val.split('.', 1)
        return {col: fam}

    cols = [
        ('family', _parse_fam),
        ('hmm_length', _parse_int),
        ('seqid', _parse_str),
        ('seqid_length', _parse_int),
        ('evalue', _parse_float),
        ('hmm_start', _parse_int),
        ('hmm_end', _parse_int),
        ('query_start', _parse_int),
        ('query_end', _parse_int),
        ('coverage', _parse_float),
        ]
    line = line.rstrip('\n').split('\t')
    record = dict()
    for (col, fn), val in zip(cols, line):
        record.update(fn(col, val))
    return record

def main(infile, outfile, families, evalue_threshold=1e-17, cov_threshold=0.45):

    fams = dict()
    with open(families, 'rU') as handle:
        for line in handle:
            if line.startswith('#') or line.strip() == '':
                continue
            record = fam_line(line.rstrip('\n'))
            fams[record['family']] = record

    template = '{seqid}\t{family}\t{classname}\t{activities}\t{note}\n'
    with inhandler(infile) as inhandle, outhandler(outfile) as outhandle:
        for line in inhandle:
            result = match_line(line.rstrip('\n'))
            try:
                result.update(fams[result['family']])
            except KeyError:
                result.update({'classname': '', 'activities': '', 'note': ''})

            if (result['evalue'] < evalue_threshold and
                    result['coverage'] > cov_threshold):
                outhandle.write(template.format(**result))



############################ Argument Handling ###############################


if __name__== '__main__':
    arg_parser = argparse.ArgumentParser(
      description=license,
      )
    arg_parser.add_argument(
        "-i", "--infile",
        default="-",
        help="Default is '-' (stdin)."
        )
    arg_parser.add_argument(
        "-o", "--outfile",
        default='-',
        help="Default is '-' (stdout)."
        )
    arg_parser.add_argument(
        "-f", "--families",
        default='FamInfo.txt',
        help=""
        )
    arg_parser.add_argument(
        "-e", "--evalue-threshold",
        dest='evalue_threshold',
        default=1e-17,
        help=""
        )
    arg_parser.add_argument(
        "-c", "--cov-threshold",
        dest='cov_threshold',
        default=0.45,
        help=""
        )
    args = arg_parser.parse_args()

    main(**args.__dict__)
