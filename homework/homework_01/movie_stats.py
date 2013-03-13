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
    with infilename as infile:
        ratings = pd.read_csv(infile, names=["user_id", "movie_id", "rating", "timestamp"],
                              dtype={"user_id": np.int32, "movie_id": np.int32,
                                     "rating": np.float64, "timestamp": np.int32})
        return ratings


def find_rankings(ratings):
    rankings = ratings.copy()
    del rankings["user_id"]
    rankings_by_movie = rankings.groupby("movie_id")
    movie_rankings = rankings_by_movie.agg({"rating": sum}).sort_index(by="rating", ascending=False)
    movie_rankings["ranking"] = movie_rankings.rank(ascending=False, method='min')
    return movie_rankings


def find_satisfaction(ratings, movie_rankings, satisfaction_level=1.0):
    ratings_by_user = ratings.groupby("user_id")

    # select users who have seen at least 10 movies
    ratings_by_user_clean = ratings_by_user.ix[ratings_by_user.movie_id.size() >= 10]

    num_users = ratings.user_id.unique().size
    num_movies = movie_rankings.shape[0]

    inventory_levels = np.zeros(num_movies)

    for user in ratings_by_user_clean.keys():
        users_ratings = ratings_by_user.get_group(user)
        df = pd.concat([users_ratings, movie_rankings], axis=1, join_axes=[users_ratings.movie_id])
        df = df.sort_index(by="ranking")
        satisfaction_percentile_row = int(np.floor(satisfaction_level * df.shape[0])) - 1
        del df["user_id"]
        del df["movie_id"]
        del df["rating"]
        satisfaction_inventory = int(df.reset_index().ranking.ix[satisfaction_percentile_row])
        inventory_levels[satisfaction_inventory] += 1

    # us = pd.DataFrame.from_records(user_satisfaction, columns=["user_id", "inventory_level"])
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
    movie_rankings = find_rankings(ratings)
    us_levels = find_satisfaction(ratings, movie_rankings)

    rc('text', usetex=True)
    plt.title('Percent of Users Satisfied vs Inventory Size in the MovieLens Dataset')
    plt.xlabel('Inventory Size')
    plt.ylabel('Percent of Users Satisfied')
    plt.plot(us_levels)
    d = datetime.datetime.utcnow().isoformat()
    plt.savefig('user_satisfaction_%s.png' % d)


if __name__ == '__main__':
    main()
