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

from ipsclasses import External2GO
from ipsclasses import InterproscanResult

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

def main(
        infile,
        outfile,
        obofile,
        outfmt='long',
        pantherfile=None,
        pfamfile=None,
        smartfile=None,
        interprofile=None,
        prositefile=None,
        printsfile=None,
        prodomfile=None,
        tigrfamfile=None,
        pirsffile=None,
        hamapfile=None,
        domainfile=None,
        datadir=None,
        ):
    """ . """
    if datadir is None:
        datadir = ''

    dbs = dict()

    if pantherfile is not None:
        pantherdb = External2GO(pjoin(datadir, pantherfile), fmt='panther')
        dbs['PANTHER'] = pantherdb
    if pfamfile is not None:
        pfamdb = External2GO(pjoin(datadir, pfamfile))
        dbs['Pfam'] = pfamdb
    if smartfile is not None:
        smartdb = External2GO(pjoin(datadir, smartfile))
        dbs['SMART'] = smartdb
    if interprofile is not None:
        interprodb = External2GO(pjoin(datadir, interprofile))
        dbs['IPR'] = interprodb
    if prositefile is not None:
        prositedb = External2GO(pjoin(datadir, prositefile))
        dbs['ProSitePatterns'] = prositedb
        dbs['ProSiteProfiles'] = prositedb
    if printsfile is not None:
        printsdb = External2GO(pjoin(datadir, printsfile))
        dbs['PRINTS'] = printsdb
    if prodomfile is not None:
        prodomdb = External2GO(pjoin(datadir, prodomfile))
        dbs['ProDom'] = prodomdb
    if tigrfamfile is not None:
        tigrfamdb = External2GO(pjoin(datadir, tigrfamfile))
        dbs['TIGRFAM'] = tigrfamdb
    if pirsffile is not None:
        pirsfdb = External2GO(pjoin(datadir, pirsffile))
        dbs['PIRSF'] = pirsfdb
    if hamapfile is not None:
        hamapdb = External2GO(pjoin(datadir, hamapfile))
        dbs['Hamap'] = hamapdb
    if domainfile is not None:
        domaindb = External2GO(pjoin(datadir, domainfile), fmt='superfamily')
        dbs['SUPERFAMILY'] = domaindb

    ips = InterproscanResult(infile)
    godag = GODag(pjoin(datadir, obofile))

    with outhandler(outfile) as handle:
        for query, analyses in ips.items():
            ontologies = set()
            for analysis, records in analyses.items():
                for record in records:
                    if analysis not in dbs:
                        continue
                    acc = record.accession
                    if acc not in dbs[analysis]:
                        continue
                    gos = [g.id for g in dbs[analysis][acc].ontologies]
                    for go in gos:
                        domain = godag[go].namespace.replace('_', ' ')
                        term = godag[go].name
                        ontologies.add((go, term, domain))

            if len(ontologies) == 0:
                continue

            if outfmt == 'long':
                template = "{seqid}\t{go}\t{term}\t{domain}\n"
                for ontology in ontologies:
                    go, term, domain = ontology
                    handle.write(template.format(
                        seqid=query,
                        go=go,
                        term=term,
                        domain=domain,
                        ))
            elif outfmt == 'association':
                template = "{seqid}\t{gos}\n"
                gos = [go for go, term, domain in ontologies]
                handle.write(template.format(
                    seqid=query,
                    gos=';'.join(gos)
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
        "-f", "--format",
        dest='outfmt',
        default='long',
        choices=['long', 'association'],
        help=""
        )
    arg_parser.add_argument(
        "--obofile",
        default='go-basic.obo',
        help=""
        )
    arg_parser.add_argument(
        "--pantherfile",
        default=None,
        help="Path to panther terms file"
        )
    arg_parser.add_argument(
        "--pfamfile",
        default=None,
        help=""
        )
    arg_parser.add_argument(
        "--smartfile",
        default=None,
        help=""
        )
    arg_parser.add_argument(
        "--interprofile",
        default=None,
        help=""
        )
    arg_parser.add_argument(
        "--prositefile",
        default=None,
        help=""
        )
    arg_parser.add_argument(
        "--printsfile",
        default=None,
        help=""
        )
    arg_parser.add_argument(
        "--prodomfile",
        default=None,
        help=""
        )
    arg_parser.add_argument(
        "--tigrfamfile",
        default=None,
        help=""
        )
    arg_parser.add_argument(
        "--pirsffile",
        default=None,
        help=""
        )
    arg_parser.add_argument(
        "--hamapfile",
        default=None,
        help=""
        )
    arg_parser.add_argument(
        "--domainfile",
        default=None,
        help=""
        )
    arg_parser.add_argument(
        "--datadir",
        default=None,
        help=""
        )

    args = arg_parser.parse_args()

    main(**args.__dict__)
