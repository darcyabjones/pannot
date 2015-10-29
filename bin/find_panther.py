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


class DB2GO(Base):
    __tablename__ = 'db2go'
    db = Column(String, index=True)
    id = Column(String, index=True)
    name = Column(String, default=None)
    domain = Column(String, default=None)
    goid = Column(String)
    goterm = Column(String)
    index = Index()






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

def parse_panther(handle):
    def parse_id(col, string):
        string = string.split(':')
        if len(string) == 1:
            family, subfamily = string[0], None
        else:
            family, subfamily = string
        return {'family': family, 'subfamily': subfamily, 'id':':'.join(string)}

    def parse_str(col, str):
        return {col: str}

    def parse_go(col, str):
        ontologies = str.split(';')
        l = list()
        for ontology in ontologies:
            name, id_ = ontology.split('#')
            l.append({'name': name, 'id': id_})
        return {col: l}

    cols = [
        ('id', parse_id),
        ('name', parse_str),
        ('molecular_function', parse_go),
        ('biological_process', parse_go),
        ('cellular_components', parse_go),
        ('protein_class', parse_go),
        ('pathway', parse_go),
        ]

    db = defaultdict(dict)
    for line in handle:
        line = line.strip()
        if line.startswith('#'):
            continue
        line = line.split('\t')
        entry = dict()
        for (col, fn), val in zip(cols, line):
            entry.update(fn(col, val))
        db[entry['id']] = entry
    return db

pantherdb

def parse_dbcan(handle):
    cols = [
        ('family'),
        ('domain'),
        ('class'),
        ('note'),
        ('activities'),
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
    db = defaultdict(dict)
    for line in handle:
        line = line.strip()
        if line.startswith('#'):
            continue
        line = line.split('\t')
        entry = dict()
        for col, val in zip(cols, line):
            entry[col] = val
        entry['class_longname'] = fam_map[entry['class']]
        db[entry['family']] = entry
    return db



def main(infile, pantherfile, dbcanfile, outfile):
    with open(pantherfile, 'rU') as handle:
        pantherdb = parse_panther(handle)

    with open(dbcanfile, 'rU') as handle:
        dbcan = parse_dbcan(handle)



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
