#! /usr/bin/env python3

from __future__ import print_function

program = "combine_panther"
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

from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

################################## Classes ###################################

Base = declarative_base()


class PANTHERRecord(object):
    def __init__(self, line, sep='\t'):
        self.sep = sep
        self.line = line.rstrip('\n')
        self.comment_pattern = '#'
        self.cols = [
            ('id', _parse_id),
            ('name', _parse_str),
            ('molecular_function', _parse_go),
            ('biological_process', _parse_go),
            ('cellular_components', _parse_go),
            ('protein_class', _parse_go),
            ('pathway', _parse_go),
            ]
        sline = line.split(self.sep)
        for i, (col, fn) in enumerate(self.cols):
            val = fn(col, sline[i])

        return

    def _parse_id(self, col, string):
        string = string.split(':')
        if len(string) == 1:
            family, subfamily = string[0], None
        else:
            family, subfamily = string
        self.__dict__.update({
            'family': family,
            'subfamily': subfamily,
            'id':':'.join(string)
            })
            return

    def _parse_str(col, str):
        self.__dict__.update({col: str})

    def _parse_go(col, str):
        ontologies = str.split(';')
        l = list()
        for ontology in ontologies:
            name, id_ = ontology.split('#')
            l.append({'name': name, 'id': id_})
        self.__dict__.update({col: l})

class PANTHER2GO(dict):
    def __init__(self, fp):
        self.fp = fp
        self.parse()
        return

    def parse(self):
        with open(self.fp, 'rU') as handle:
            for line in handle:
                rec = PANTHERRecord(line)
                self[rec.id] = rec
        return

class 



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

def main(infile, pantherfile, outfile):
    pantherdb = PANTHER2GO(pantherfile)
    with inhandler(infile) as handle:

    return

############################ Argument Handling ###############################

if __name__== '__main__':
    arg_parser = argparse.ArgumentParser(
      description=license,
      )
    arg_parser.add_argument(
        "-i", "--infile",
        default='-',
        help="Default is '-' (stdin)"
        )


    args = arg_parser.parse_args()

    main(**args.__dict__)
