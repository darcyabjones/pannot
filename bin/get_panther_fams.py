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

from ipsclasses import External2GO
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

def main(infile, outfile, pantherfile):
    pantherdb = External2GO(pantherfile, fmt='panther')
    ips = InterproscanResult(infile)
    with outhandler(outfile) as handle:
        for query, analyses in ips.items():
            if 'PANTHER' in analyses:
                panther_ids = [f.accession for f in analyses['PANTHER']]
                panther_names = [pantherdb[f].name for f in panther_ids]
                unnamed = [
                    i for i, val in enumerate(panther_names) if
                    val in {'FAMILY NOT NAMED', 'SUBFAMILY NOT NAMED'}
                    ]
                subfamily = [i for i, val in enumerate(panther_ids) if ":" in val]
                family = [i for i, val in enumerate(panther_ids) if ":" not in val]
                represented_fams = set()

                ids = list()
                names = list()
                for sf in subfamily:
                    fam = panther_ids[sf].split(':')[0]
                    if sf in unnamed or panther_ids[sf] in represented_fams:
                        continue
                    represented_fams.add(fam)
                    represented_fams.add(panther_ids[sf])

                    ids.append(panther_ids[sf])
                    names.append(panther_names[sf])

                for f in family:
                    if f in unnamed or panther_ids[f] in represented_fams:
                        continue
                    represented_fams.add(panther_ids[f])
                    ids.append(panther_ids[f])
                    names.append(panther_names[f])
            else:
                names = []
                ids = []

            if len(names) == 0 and len(ids) == 0:
                continue

            template = '{seqid}\t{ids}\t{names}\n'
            handle.write(template.format(
                seqid=query,
                ids=';'.join(ids),
                names=';'.join(names)
                ))




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
        "-p", "--panther-db",
        dest='pantherfile',
        default='PANTHER10.0_HMM_classifications',
        help="Path to panther terms file"
        )

    args = arg_parser.parse_args()

    main(**args.__dict__)
