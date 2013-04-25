#!/usr/bin/env python

from __future__ import division
from __future__ import print_function

import argparse

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt, rc


__author__ = "Varun Ravishankar <vr2263@columbia.edu>"
__date__ = "Apr 24, 2013"


def read_inputs(infilename):
    """Read Wikipedia page counts into a Pandas dataframe."""
    with infilename as infile:
        counts = pd.read_csv(infile, names=["page_id", "url", "page_count"],
                             dtype={"page_id": np.longlong, "url": np.str,
                             "page_count": np.longlong}, delim_whitespace=True)
        return counts


def main():
    parser = argparse.ArgumentParser(description="""Compute degree distribution of incoming
                                      links to Wikipedia pages.""")
    parser.add_argument("infilename",
                        help="Read from this file.", type=open)
    args = parser.parse_args()

    page_counts = read_inputs(args.infilename)
    page_counts = page_counts.drop("url", axis=1)
    page_counts = page_counts.drop("page_id", axis=1)

    rc('text', usetex=True)
    plt.title('Degree Distribution for Incoming Links Across All Wikipedia Articles')
    plt.xlabel('Inventory Size')
    plt.ylabel('Number of pages with degree')
    plt.hist(page_counts.page_count, log=True, range=[1, 130000])
    plt.savefig('degree_distribution.png')


if __name__ == '__main__':
    main()
