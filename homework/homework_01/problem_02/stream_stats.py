#!/usr/bin/env python

import sys
import fileinput
from itertools import groupby


def first_col(line):
    return line.split('\t')[0]

if __name__ == '__main__':

    # check for input filename given as first argument
    if len(sys.argv) < 2:
        sys.stderr.write('reading input from stdin\n')

    # read input one line at a time, grouping by key in first column
    for key, lines in groupby(fileinput.input(), key=first_col):

        # iterate over lines in each group
        for line in lines:
            # strip newline, split on tab, and return value from second column
            value = line.rstrip('\n').split('\t')[1]

            # print key and value
            print key, value

        print "--"
