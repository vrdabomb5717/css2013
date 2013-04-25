#!/usr/bin/env python

from __future__ import print_function
from __future__ import division

import argparse
import cPickle
import csv
import heapq

import numpy as np
from matplotlib import pyplot as plt, rc


def read_nodes(infile):
    """Read nodes into list."""
    with infile as nodes_in:
        nodes_reader = csv.reader(nodes_in, delimiter=' ')
        nodes = [row[1] for row in nodes_reader]
        return nodes


def read_adjacency(infile):
    """Read edges into dict.

    Multiple lines starting with the same author are
    treated as extensions of the same edge list.

    FIXME: read edges into all other edges

    """
    with infile as adjacency_in:
        adjacency_reader = csv.reader(adjacency_in, delimiter=' ')
        adjacencies = {}

        for row in adjacency_reader:
            author = int(row[0])
            edges = set(map(int, row[1:]))
            existing_edges = adjacencies.get(author, set())
            adjacencies[author] = existing_edges | edges

            for edge in edges:
                existing_edges = adjacencies.get(edge, set())
                adjacencies[edge] = existing_edges | set([author])

        return adjacencies


def calculate_tie_strength(authors, adjacencies, i):
    """Calculate the Jaccard index for each pair of authors."""
    tie_strengths = {}

    # iterate over all pairs of distinct authors
    for j, second_author in enumerate(authors, start=1):
        if i != j:
            edges_first = adjacencies[i]
            edges_second = adjacencies[j]

            # find number of co-authors in common
            common = len(edges_first & edges_second)

            # find total number of distinct co-authors between pair
            distinct = len(edges_first | edges_second)

            tie_strengths[j] = common / distinct

    return tie_strengths


def write_output(authors, adjacencies, outfile, k=3):
    """Write output to provided file.

    Write each author, their total number of collaborators, and their top
    k collaborators ordered by descending tie strength to a tab-separated
    file.

    """
    with outfile as out:
        outwriter = csv.writer(out, delimiter='\t')

        ties = np.array([])

        for i, author in enumerate(authors, start=1):
            collaborators = len(adjacencies[i])

            tie_strengths = calculate_tie_strength(authors, adjacencies, i)
            ties = np.append(ties, tie_strengths.values())
            strengths = []

            # iterate over the other authors to find max tie strengths
            for j in tie_strengths:
                strength = tie_strengths[j]
                heapq.heappush(strengths, (strength, j))

            top_k_strengths = heapq.nlargest(k, strengths)
            top_k_coauthors = [authors[s[1] - 1] for s in top_k_strengths]
            coauthors = '; '.join(top_k_coauthors)

            outwriter.writerow([author, collaborators, coauthors])
        return ties


def plot_tie_strengths(tie_strengths):
    """Plot the tie strength distribution histogram."""
    rc('text', usetex=True)
    plt.title('Tie Strength Distribution for the Erdos 02 Network')
    plt.xlabel('Tie Strengths')
    plt.ylabel('Number of pairs with tie strength')
    plt.hist(tie_strengths, log=True)
    plt.savefig('tie_strength_distribution.png')


def main():
    parser = argparse.ArgumentParser(description="""Compute tie strength between
                                     coauthors in the Erdos graph.""")
    parser.add_argument("-n", "--nodes", type=open,
                        dest='nodes', required=True,
                        help="The list of nodes for the Erdos graph.")
    parser.add_argument("-a", "--adjacency", type=open,
                        dest='adjacency', required=True,
                        help="The adjacency list for the Erdos graph.")
    parser.add_argument("-o", "--output", type=argparse.FileType('w'),
                        dest='outfile', default="answer.tsv",
                        help="The file to write the output to.")
    args = parser.parse_args()

    nodes = args.nodes
    adjacency_list = args.adjacency
    outfile = args.outfile

    authors = read_nodes(nodes)
    adjacencies = read_adjacency(adjacency_list)
    tie_strengths = write_output(authors, adjacencies, outfile)
    output = open('ties.pkl', 'wb')
    cPickle.dump(tie_strengths, output, -1)
    plot_tie_strengths(tie_strengths)


if __name__ == '__main__':
    main()
