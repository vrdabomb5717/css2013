#!/usr/bin/env python

from __future__ import division
from __future__ import print_function

import argparse
import datetime

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt, rc


__author__ = "Varun Ravishankar <vr2263@columbia.edu>"
__date__ = "Mar 6, 2013"


def read_inputs(infilename):
    """Read MovieLens ratings CSV into a Pandas dataframe."""
    with infilename as infile:
        ratings = pd.read_csv(infile, names=["user_id", "movie_id", "rating", "timestamp"],
                              dtype={"user_id": np.int32, "movie_id": np.int32,
                                     "rating": np.float64, "timestamp": np.int32})
        return ratings


def find_movie_rankings(ratings):
    """Find the ranking for movies, measured by the number of ratings they have received."""
    rankings = ratings.copy()
    rankings = rankings.drop("user_id", axis=1)
    rankings_by_movie = rankings.groupby("movie_id")

    # aggregate movies by the number of ratings
    movie_rankings = rankings_by_movie.agg({"rating": len})
    movie_rankings["ranking"] = movie_rankings.rank(ascending=False, method='min').astype(int)
    movie_rankings = movie_rankings.drop("rating", axis=1)
    movie_rankings.reset_index(inplace=True)
    return movie_rankings


def find_user_rankings(ratings, movie_rankings):
    """Find the movie ranking for each movie that a user has seen."""
    # Do an equijoin on movie_id, projecting out user_id and ranking
    user_rankings = pd.merge(ratings, movie_rankings, on="movie_id", sort=False)
    user_rankings.reset_index(drop=True, inplace=True)
    user_rankings = user_rankings.drop("movie_id", axis=1)
    user_rankings.sort_index(by=("user_id", "ranking"), inplace=True)
    user_rankings.reset_index(drop=True, inplace=True)
    return user_rankings


def clean_rankings(user_rankings):
    """Remove users who have seen fewer than 10 movies."""
    rankings_by_user = user_rankings.groupby("user_id")
    num_movies_seen = rankings_by_user.agg({"ranking": len})
    b = (num_movies_seen >= 10).values
    b = np.ndarray.flatten(b)
    users_to_keep = num_movies_seen[b]
    user_rankings_clean = user_rankings[user_rankings['user_id'].isin(users_to_keep.index)]
    return user_rankings_clean


def find_satisfaction(user_rankings, num_users, num_movies, satisfaction_level=1.0):
    rankings_by_user = user_rankings.groupby("user_id")
    inventory_levels = np.zeros(num_movies)

    def satisfaction(group):
        """For each group, find the inventory level that satisfies a user p%."""
        satisfaction_percentile_row = int(np.floor(satisfaction_level * group.shape[0])) - 1
        level = group.values[satisfaction_percentile_row]
        return level

    # Find the inventory level that satisfies a user p%
    satisfactions = rankings_by_user.agg({"ranking": satisfaction})
    satisfactions = satisfactions.rename(columns={'ranking': 'levels'})

    for x in satisfactions.levels.values:
        inventory_levels[x] += 1

    # Find the percent of users satisfied p% at a given inventory level
    user_satisfaction = inventory_levels.cumsum() / num_users
    return user_satisfaction


def main():
    parser = argparse.ArgumentParser(description="""Compute subset of users who rated at
                                     least 10 movies and plot fraction of users satisfied
                                     as a function of inventory size.""")
    parser.add_argument("infilename",
                        help="Read from this file.", type=open)
    args = parser.parse_args()

    ratings = read_inputs(args.infilename)
    ratings = ratings.drop("timestamp", axis=1)
    movie_rankings = find_movie_rankings(ratings)
    ratings = ratings.drop("rating", axis=1)
    user_rankings = find_user_rankings(ratings, movie_rankings)
    num_users = user_rankings.user_id.unique().size
    num_movies = movie_rankings.shape[0]
    user_rankings = clean_rankings(user_rankings)

    us_levels_100 = find_satisfaction(user_rankings, num_users, num_movies)
    us_levels_90 = find_satisfaction(user_rankings, num_users, num_movies, satisfaction_level=0.9)

    rc('text', usetex=True)
    plt.title('Percent of Users Satisfied vs Inventory Size in the MovieLens Dataset')
    plt.xlabel('Inventory Size')
    plt.ylabel('Percent of Users Satisfied')
    plt.plot(us_levels_100, 'b', label=r'$100\% \ satisfaction$')
    plt.plot(us_levels_90, 'r--', label=r'$90\% \ satisfaction$')
    plt.legend()
    d = datetime.datetime.now().isoformat()
    plt.savefig('user_satisfaction_%s.png' % d)


if __name__ == '__main__':
    main()
