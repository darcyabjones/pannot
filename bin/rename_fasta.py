#! /usr/bin/env python3

from __future__ import print_function

program = "rename_fasta"
version = "0.1.0"
author = "Darcy Jones"
date = "1 October 2015"
email = "darcy.ab.jones@gmail.com"
short_blurb = (
    'Renames fasta sequences.'
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
import json

################################## Classes ###################################


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

def main(infile, outfile, json_file, decode=False, split=r'\s+', col=0, hold=False):
    start_regex = re.compile(r'>')
    split_regex = re.compile(split)
    if not decode:
        with inhandler(infile, mode='rU') as inhandle, \
                outhandler(outfile, mode='w') as outhandle, \
                outhandler(json_file, mode='w') as jsonhandle:
            record_num = 0
            lines = list()
            new_ids = dict()
            for line in inhandle:
                line = line.strip()
                if line == '':
                    continue
                elif start_regex.match(line) is not None:
                    if not hold:
                        outhandle.write('\n'.join(lines) + '\n')
                        lines = list()
                    new_id = "g{:0=9}".format(record_num)
                    new_ids[new_id] = line.lstrip('>').strip().split(' ')[0]
                    line = '>{}'.format(new_id)
                    record_num += 1
                lines.append(line)
            json.dump(new_ids, jsonhandle)
            outhandle.write('\n'.join(lines) + '\n')
    else:
        with inhandler(infile, mode='rU') as inhandle,\
                outhandler(outfile, mode='w') as outhandle,\
                inhandler(json_file, mode='r') as jsonhandle:
            new_ids = json.load(jsonhandle)
            def repl(m):
                return new_ids[m.group(0)]

            id_regex = re.compile('|'.join(new_ids.keys()))
            lines = list()
            for line in inhandle:
                line = line.strip()
                if line == '' or line.startswith('#'):
                    lines.append(line)
                    if not hold:
                        outhandle.write(line + '\n')
                else:
                    sline = split_regex.split(line)
                    line = id_regex.sub(repl, line)
                    lines.append(line)
                    if not hold:
                        outhandle.write(line + '\n')
            if hold:
                outhandle.write('\n'.join(lines))
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
    arg_parser.add_argument(
        "-o", "--outfile",
        default='-',
        help="Default is '-' (stdout)"
        )
    arg_parser.add_argument(
        "-j", "--json",
        dest='json_file',
        default='codes.json',
        help="",
        )
    arg_parser.add_argument(
        "-d", "--decode",
        default=False,
        action='store_true',
        help="",
        )
    arg_parser.add_argument(
        "-s", "--split",
        default=r'\s+',
        help="",
        )
    arg_parser.add_argument(
        "-c", "--col",
        default=0,
        help="",
        )
    arg_parser.add_argument(
        "-l", "--hold",
        default=False,
        action='store_true',
        help="",
        )


    args = arg_parser.parse_args()

    main(**args.__dict__)
