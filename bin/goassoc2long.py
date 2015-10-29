#! /usr/bin/env python

from __future__ import print_function

program = "get_gos"
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
from os.path import join as pjoin
import re
import argparse
import sys
from collections import defaultdict

from goatools.obo_parser import GODag


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

def main(infile, outfile, obofile):
    """ . """
    godag = GODag(obofile)

    with inhandler(infile) as inhandle, outhandler(outfile) as outhandle:
        for line in inhandle:
            line = line.rstrip('\n')
            seqid, gos = line.split('\t')
            gos = set(gos.split(';'))
            ontologies = set()
            for go in gos:
                domain = godag[go].namespace.replace('_', ' ')
                term = godag[go].name
                ontologies.add((go, term, domain))

            if len(ontologies) == 0:
                continue

            template = "{seqid}\t{go}\t{term}\t{domain}\n"

            for ontology in ontologies:
                go, term, domain = ontology
                outhandle.write(template.format(
                    seqid=seqid,
                    go=go,
                    term=term,
                    domain=domain,
                    ))
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
        "--obofile",
        default='go-basic.obo',
        help=""
        )
    args = arg_parser.parse_args()

    main(**args.__dict__)
