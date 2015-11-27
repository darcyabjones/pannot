#! /usr/bin/env python3

from __future__ import print_function

program = "rename_fasta"
version = "0.1.0"
author = "Darcy Jones"
date = "1 October 2015"
email = "darcy.ab.jones@gmail.com"
short_blurb = (
    'Renames fasta sequences.\n'
    'Codes sequence IDs as g followed by an integer left-filled with zeros (e.g. g0001, g0002).\n'
    'Can replace original sequence IDs from coded output using a simple regular expression system.'
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

def main(infile, outfile, json_file, length, decode=False):
    start_regex = re.compile(r'>')
    if not decode:
        with inhandler(infile, mode='rU') as inhandle, \
                outhandler(outfile, mode='w') as outhandle:
            record_num = 0
            lines = list()
            new_ids = dict()

            for line in inhandle:
                line = line.strip()
                if line == '':
                    continue
                elif start_regex.match(line) is not None:
                    outhandle.write('\n'.join(lines) + '\n')
                    lines = list()

                    new_id = ("g{{:0={}}}".format(length)).format(record_num)
                    new_ids[new_id] = line.lstrip('>').strip().split(' ')[0]
                    line = '>{}'.format(new_id)
                    record_num += 1
                lines.append(line)

            outhandle.write('\n'.join(lines) + '\n')
            with outhandler(json_file, mode='w') as jsonhandle:
                json.dump(new_ids, jsonhandle)
    else:
        with inhandler(json_file, mode='r') as jsonhandle:
            new_ids = json.load(jsonhandle)

        with inhandler(infile, mode='rU') as inhandle,\
                outhandler(outfile, mode='w') as outhandle:

            def repl(m):
                return new_ids[m.group(0)]

            id_regex = re.compile('|'.join(new_ids.keys()))

            for line in inhandle:
                line = line.strip()
                if line == '':
                    outhandle.write('\n')
                else:
                    line = id_regex.sub(repl, line)
                    outhandle.write(line + '\n')
    return

############################ Argument Handling ###############################

if __name__== '__main__':
    arg_parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=license,
        epilog=(
            'Example usage:'
            '\n'
            '$ %(prog)s -i my_fasta.fa -o my_fasta.coded.fa -j ./codes.json\n'
            '$ annoyingprogram --in my_fasta.coded.fa --out my_output.coded.dat\n'
            '$ %(prog)s -i my_output.coded.dat -o my_output.dat -j ./codes.json --decode\n'
            '\n'
            'Note: Currently you can\'t have the coding and decoding steps in the same piped-chain e.g.:\n'
            '\n'
            '$ %(prog)s -i my_fasta.fa | annoyingprogram | %(prog)s -o my_output.dat --decode \n'
            '\n'
            'Would give an error because the decoding step is trying to read the JSON before it is written. '
            'Try using an intermediate file instead.\n'
            )
        )
    arg_parser.add_argument(
        "-i", "--infile",
        default='-',
        help=(
            "Path to the input file."
            "Default is '-' (stdin)."
            )
        )
    arg_parser.add_argument(
        "-o", "--outfile",
        default='-',
        help=(
            "Path to write output to."
            "Default is '-' (stdout)."
            )
        )
    arg_parser.add_argument(
        "-j", "--json",
        dest='json_file',
        default='codes.json',
        help=(
            "Path to JSON file to store codes/retrieve original names from."
            "Default is 'codes.json'."
            )
        )
    arg_parser.add_argument(
        "-l", "--length",
        default='9',
        help=(
            "Length of the integer to give. Default is 9, (e.g. g000000000)."
            )
        )
    arg_parser.add_argument(
        "-d", "--decode",
        default=False,
        action='store_true',
        help=(
            "Flag signalling that the program should replace codes with "
            "the original names."
            )
        )


    args = arg_parser.parse_args()

    main(**args.__dict__)
