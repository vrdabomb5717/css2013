#!/usr/bin/env python

from __future__ import division
from __future__ import print_function

import sys
import fileinput
from itertools import groupby


__author__ = "Varun Ravishankar <vr2263@columbia.edu>"
__date__ = "Mar 13, 2013"


def first_col(line):
    return line.split('\t')[0]


def main():
    # check for input filename given as first argument
    if len(sys.argv) < 2:
        sys.stderr.write('reading input from stdin\n')

    # read input one line at a time, grouping by key in first column
    for key, lines in groupby(fileinput.input(), key=first_col):

        current_min = float("inf")
        current_max = float("-inf")
        current_sum = 0
        observations_seen = 0

        # iterate over lines in each group
        for line in lines:
            # strip newline, split on tab, and return value from second column
            value = int(line.rstrip('\n').split('\t')[1])

            current_sum += value
            observations_seen += 1

            if value < current_min:
                current_min = value
            if value > current_max:
                current_max = value

            # print key and value
            # print(key, value)

        average = current_sum / observations_seen

        print(key, current_min, average, current_max)


if __name__ == '__main__':
    main()
