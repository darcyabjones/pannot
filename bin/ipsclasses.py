#! /usr/bin/env python3

from __future__ import print_function

program = "ipsclasses"
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

################################## Classes ###################################

class InterproscanRecord(object):

    """ . """

    def __init__(self, line, sep='\t'):
        """ . """
        self.cols = [
            ('seqid', self._parse_str),
            ('md5', self._parse_str),
            ('length', self._parse_int),
            ('analysis', self._parse_str),
            ('accession', self._parse_acc),
            ('description', self._parse_str),
            ('start', self._parse_int),
            ('end', self._parse_int),
            ('score', self._parse_float),
            ('status', self._parse_bool),
            ('date', self._parse_str),
            ('ipr_accesssion', self._parse_ipracc),
            ('ipr_description', self._parse_str),
            ('go', self._parse_go),
            ('pathways', self._parse_str),
            ]
        line = line.rstrip('\n')
        sline = line.split(sep)
        for (col, fn), val in zip(self.cols, sline):
            fn(col, val)

    def _parse_str(self, col, str):
        str = str.strip()
        if str == '':
            str = None
        self.__dict__.update({col: str})
        return

    def _parse_int(self, col, str):
        str = str.strip()
        if str == '':
            str = None
        else:
            str = int(str)
        self.__dict__.update({col: str})
        return

    def _parse_float(self, col, str):
        str = str.strip()
        # Prosite patterns has no score always '-'
        if str == '' or str == '-':
            str = None
        else:
            str = float(str)
        self.__dict__.update({col: str})
        return

    def _parse_bool(self, col, str):
        str = str.strip()
        if str == '':
            str = None
        str = bool(str)
        self.__dict__.update({col: str})
        return

    def _parse_acc(self, col, str):
        prefixes = {
            'Gene3D': 'G3DSA:',
            'Pfam': 'PF',
            'SUPERFAMILY': 'SSF',
            'ProSiteProfiles': 'PS',
            'ProSitePatterns': 'PS',
            'PRINTS': 'PR',
            'PANTHER': 'PTHR',
            'SMART': 'SM',
            'TIGRFAM': 'TIGR',
            'Coils': '',
            'Hamap': 'MF_',
            'PIRSF': 'PIRSF',
            'ProDom': 'PD',
            }
        analysis = self.analysis
        str = str.strip()
        acc = str
        self.__dict__.update({col: acc})
        return

    def _parse_ipracc(self, col, str):
        #str = str.strip().lstrip('IPR')
        self.__dict__.update({col: str})
        return

    def _parse_go(self, col, str):
        str = str.strip()
        gos = str.split('|')
        gos = [go.lstrip('GO:') for go in gos]
        self.__dict__.update({col: gos})
        return

class InterproscanResult(dict):

    """ . """

    def __init__(self, fp):
        """ . """
        self.fp = fp
        self._parse()
        return

    def _parse(self):
        with open(self.fp, 'rU') as handle:
            for line in handle:
                record = InterproscanRecord(line)

                if record.seqid not in self:
                    self[record.seqid] = dict()

                if record.analysis not in self[record.seqid]:
                    self[record.seqid][record.analysis] = list()

                self[record.seqid][record.analysis].append(record)
        return


class Record(object):

    """ . """

    def __init__(self,
            id,
            name=None,
            ontologies=None,
            pathways=None,
            protein_cls=None,
            parents=None,
            ):
        """ . """
        self.id = id
        self.name = name
        self.ontologies = ontologies if ontologies is not None else list()
        self.pathways = pathways if pathways is not None else list()
        self.protein_cls = protein_cls
        self.parents = parents if parents is not None else list()


class Ontology(object):

    """ . """

    def __init__(self, id, term=None, domain=None):
        """ . """
        self.id = id
        self.term = term
        self.domain = domain
        return


class External2GO(dict):

    """ . """

    def __init__(self, fp=None, fmt='go'):
        """ . """
        self.fmt = fmt
        self.fmt2parser = {
            'go': self._go_mapping,
            'superfamily': self._sf_mapping,
            'panther': self._panther_mapping
            }
        if fp is not None:
            self.parse(fp, fmt)

    def parse(self, fp, fmt=None):
        """ . """
        if fmt is None:
            fmt = self.fmt

        with open(fp, 'rU') as handle:
            first = True
            for line in handle:
                if fmt == 'go' and line.startswith('!'):
                    continue
                elif fmt == 'superfamily' and line.startswith('#'):
                    continue
                elif fmt == 'superfamily' and first:
                    first = False
                    continue
                record = self.fmt2parser[fmt](line)
                if record.id in self:
                    self[record.id].ontologies.extend(record.ontologies)
                    self[record.id].pathways.extend(record.pathways)
                    self[record.id].parents.extend(record.parents)
                else:
                    self[record.id] = record

    def _go_mapping(self, line):
        # external database:term identifier (id/name) > GO:GO term name ; GO:id
        line = line.rstrip('\n')
        db_bits, go_bits = re.split(r'\s>\s', line)
        try:
            dbid, name = db_bits.split(' ', 1)
        except:
            dbid = db_bits
            name = None
        db, id = dbid.split(':', 1)
        goterm, goid = re.split(r'\s;\s', go_bits)
        ontology = Ontology(id=goid, term=goterm)
        return Record(
            id=id,
            name=name,
            ontologies=[ontology],
            )

    def _sf_mapping(self, line):
        # Domain_type	Domain_sunid	GO_id	GO_name	GO_subontologies	Information_content	Annotation_origin (Direct:1, Inherited:0)
        line = line.rstrip('\n')
        cols = [
            ('type', self._parse_str),
            ('id', self._parse_sfid),
            ('goid', self._parse_str),
            ('goterm', self._parse_str),
            ('godomain', self._parse_str),
            ('information_content', self._parse_float),
            ('annotation_origin', self._parse_int),
            ]
        line = line.rstrip('\n').split('\t')
        record = dict()
        for (col, fn), val in zip(cols, line):
            record.update(fn(col, val, **record))

        ontology = Ontology(
            id=record['goid'],
            term=record['goterm'],
            domain=record['godomain'].replace('_', ' '),
            )
        return Record(
            id=record['id'],
            ontologies=[ontology],
            )

    def _parse_str(self, col, str, **kwargs):
        return {col: str}

    def _parse_int(self, col, str, **kwargs):
        return {col: int(str)}

    def _parse_float(self, col, str, **kwargs):
        return {col: float(str)}

    def _parse_sfid(self, col, str, type, **kwargs):
        dbmap = {
            'sf': 'SSF',
            'fa': 'FA',
            }
        this_id = dbmap[type] + str
        return {col: this_id}

    def _panther_mapping(self, line):
        line = line.rstrip('\n')
        comment_pattern = '#'
        cols = [
            ('id', self._parse_pantherid),
            ('name', self._parse_str),
            ('molecular_function', self._parse_panthergo),
            ('biological_process', self._parse_panthergo),
            ('cellular_component', self._parse_panthergo),
            ('protein_class', self._parse_str),
            ('pathway', self._parse_str),
            ]
        sline = line.split('\t')
        record = {'ontologies': list()}
        for i, (col, fn) in enumerate(cols):
            if col in {'molecular_function',
                       'biological_process',
                       'cellular_component',
                       }:
                for k, v in fn(col, sline[i]).items():
                    record[k].extend(v)
            else:
                record.update(fn(col, sline[i]))
        return Record(
            id=record['id'],
            name=record['name'],
            ontologies=record['ontologies'],
            )

    def _parse_pantherid(self, col, string):
        string = string.split(':')
        if len(string) == 1:
            family, subfamily = string[0], None
        else:
            family, subfamily = string
        return {
            'family': family,
            'subfamily': subfamily,
            'id':':'.join(string)
            }

    def _parse_panthergo(self, col, str):
        ontologies = str.split(';')
        l = list()
        for ontology in ontologies:
            if ontology == '':
                continue
            name, id_ = ontology.split('#')
            l.append(Ontology(term=name, id=id_))
        return {'ontologies': l}

################################## Functions #################################
