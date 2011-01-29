#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import re
from optparse import OptionParser
import os

USAGE = "%prog [OPTIONS] dict_filename file1 <file2 ... fileN>"
misspellings = {}
options = None

#OPTIONS:
#
#ARGUMENTS:
#    dict_filename       The file containing the dictionary of misspellings.
#                        If set to '-', it will be read from stdin
#    file1 .. fileN      Files to check spelling

class Mispell:
    def __init__(self, data, fix):
        self.data = data
        self.fix = fix


class TermColors:
    def __init__(self):
        self.FILE = '\033[33m'
        self.WWORD = '\033[31m'
        self.FWORD = '\033[32m'
        self.DISABLE = '\033[0m'

    def disable(self):
        self.FILE = ''
        self.WWORD = ''
        self.FWORD = ''
        self.DISABLE = ''

# -.-:-.-:-.-:-.:-.-:-.-:-.-:-.-:-.:-.-:-.-:-.-:-.-:-.:-.-:-

def parse_options(args):
    parser = OptionParser(usage=USAGE)

    parser.add_option('-d', '--disable-colors',
                        action = 'store_true', default = False,
                        help = 'Disable colors even when printing to terminal')
    parser.add_option('-r', '-R',
                        action = 'store_true', default = False,
                        dest = 'recursive',
                        help = 'parse directories recursively')

    (options, args) = parser.parse_args()
    if (len(args) < 2):
        print('ERROR: you need to specify a file!', file=sys.stderr)
        parser.print_help()
        sys.exit(1)

    return options, args


def build_dict(filename):
    with open(filename, 'r') as f:
        for line in f:
            [key, data] = line.split('->')
            misspellings[key] = Mispell(data, data.find(',') + 1)

def parse_file(filename, colors):
    with open(filename, 'r') as f:
        i = 1
        for line in f:
            for word in re.findall('\w+', line):
                if word in misspellings:
                    cfilename = "%s%s" % (colors.FILE, filename)
                    cline = "%d%s" % (i, colors.DISABLE)
                    cwrongword = "%s%s%s" % (colors.WWORD, word, colors.DISABLE)
                    crightword = "%s%s%s" % (colors.FWORD, \
                                                misspellings[word].data, \
                                                colors.DISABLE)

                    print ("%(FILENAME)s:%(LINE)s: %(WRONGWORD)s "             \
                            " ==> %(RIGHTWORD)s"      \
                            % {'FILENAME': cfilename, 'LINE': cline,           \
                               'WRONGWORD': cwrongword,                        \
                               'RIGHTWORD': crightword }, end='')
            i += 1


def main(*args):
    (options, args) = parse_options(args)

    build_dict(args[0])
    colors = TermColors();
    if options.disable_colors:
        colors.disable()

    for filename in args[1:]:
        if len(filename) > 1 and filename[0] == '.':
            continue

        if not options.recursive and os.path.isdir(filename):
            continue

        if os.path.isdir(filename):
            for root, dirs, files in os.walk(filename):
                for file in files:
                    parse_file(os.path.join(root, file), colors)

            continue

        parse_file(filename, colors)

if __name__ == '__main__':
    sys.exit(main(*sys.argv))
