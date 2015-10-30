#! /usr/bin/env python3

from __future__ import print_function

program = "get_panther_fams"
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

def annot_line(line):
    cols = [
        'catid',
        'id',
        'level',
        'scopclass',
        'cla',
        'name'
        ]
    line = line.split('\t')
    record = dict()
    for col, val in zip(cols, line):
        record[col] = val
    return record

def desc_line(line):
    cols = [
        'id',
        'level',
        'scopclass',
        'cla',
        'name'
        ]
    line = line.split('\t')
    record = dict()
    for col, val in zip(cols, line):
        record[col] = val
    return record

def cat_line(line):
    cols = [
        'category',
        'catid',
        'short_catname',
        'long_catname',
        ]
    line = line.split('\t')
    record = dict()
    for col, val in zip(cols, line):
        record[col] = val
    return record


def main(infile, outfile, annotations, descriptions, categories):

    cats = dict()
    with open(categories, 'rU') as handle:
        for line in handle:
            if line.startswith('#') or line.strip() == '':
                continue
            line = line.rstrip('\n')
            record = cat_line(line)
            cats[record['catid']] = record

    annots = dict()
    with open(annotations, 'rU') as handle:
        for line in handle:
            if line.startswith('#') or line.strip() == '':
                continue
            line = line.rstrip('\n')
            record = annot_line(line)
            cat = record['catid']
            record.update(cats[cat])
            annots[record['id']] = record

    descs = dict()
    with open(descriptions, 'rU') as handle:
        for line in handle:
            if line.startswith('#') or line.strip() == '':
                continue
            line = line.rstrip('\n')
            record = desc_line(line)
            record['category'] = ''
            record['short_catname'] = ''
            record['long_catname'] = ''
            descs[record['id']] = record


    ips = InterproscanResult(infile)
    with outhandler(outfile) as handle:
        for query, analyses in ips.items():
            results = list()
            if 'SUPERFAMILY' in analyses:
                analysis = analyses['SUPERFAMILY']
                sfids = set()
                for record in analysis:
                    acc = record.accession.lstrip('SSF')
                    sfids.add(acc)
                for acc in sfids:
                    try:
                        results.append(annots[acc])
                    except KeyError:
                        results.append(descs[acc])

            template = '{seqid}\t{category}\t{short_catname}\t{long_catname}\t{id}\t{name}\n'
            for result in results:
                handle.write(template.format(seqid=query, **result))
    return


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
        "-d", "--descriptions",
        default='dir.des.scop.txt_1.75',
        help=""
        )
    arg_parser.add_argument(
        "-a", "--annotations",
        default='scop.annotation.1.73.txt',
        help=""
        )
    arg_parser.add_argument(
        "-c", "--categories",
        default='scop.larger.categories',
        help=""
        )

    args = arg_parser.parse_args()

    main(**args.__dict__)
