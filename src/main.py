#!/usr/bin/env python

import sqlite3
import os, sys

from analysis import clustering, features
import util

def create_table(conn):
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS user_models (person VARCHAR(120), feature VARCHAR(150), value REAL, PRIMARY KEY (person, feature))')
    conn.commit()

# Feature metric functions
from metrics.simple import rooms_used, rooms_claimed, roomnames_generated, frequency_last_month, chat_message_sent
from metrics.graph import first_degree_conversation_partners, second_degree_conversation_partners, conversations

FEATURES = (first_degree_conversation_partners,
            second_degree_conversation_partners,
            conversations,
            rooms_used,
            rooms_claimed,
            roomnames_generated,
            frequency_last_month,
            chat_message_sent)

def map_persons_in_batches(cursor, fn, batch_size=None):
    """
    Maps persons to fn with the provided batch_size.

    fn is called as follows: fn(person, cursor=cursor).
    """

    # Get every distinct person in table
    all_persons = util.get_all_persons(cursor)

    # Count conversations for each one
    for persons in util.batches(all_persons, batch_size or len(all_persons)):
        batch_results = map(lambda p: fn(p, cursor=cursor), persons)
        yield zip(persons, batch_results)

def build_feature_set(args, connection, feature_names):
    """
    Clears and rebuilds selected features from various general data sources.

    The feature_fn call is deferred to persons_mapped.
    """

    if args.create:
        create_table(connection)

    feature_fns = dict(zip(map(lambda fn: fn.__name__, FEATURES), FEATURES))

    for name in feature_names:
        feature_fn = feature_fns[name]

        if args.reset or raw_input("Rebuild feature '%s'? [yN] " % name) in ("y", "Y"):

            print name

            print "  - clearing old values"
            features.clear_values(connection, name)

            print "  - extracting feature values: ",
            for batch in map_persons_in_batches(connection.cursor(), feature_fn, batch_size=args.batch_size):
                features.insert_values(connection, name, batch)
                sys.stdout.write('.')
                sys.stdout.flush()
            print

def analyze_feature_set(args, connection, feature_names):
    """Analyzes and plots various standard metrics for each feature."""

    for name in feature_names:
        values = util.get_feature_values(connection, name)

        stats.analyze_feature(connection, name, values)

        if args.visualize:
            visualize.plot_feature(connection, name, values)

if __name__ == '__main__':
    from util import load_config, connect_db
    CONFIG = load_config()

    connection = connect_db(CONFIG)

    feature_names = map(lambda f: f.__name__, FEATURES)
    algorithm_names = map(lambda a: a.__name__, clustering.ENABLED_ALGORITHMS)

    import argparse
    parser = argparse.ArgumentParser(description="Parses sentences.")
    parser.add_argument('-b', '--batch-size', help="batch size", type=int, default=500)
    parser.add_argument('--reset', help="clear features before rebuilding", action='store_true', default=False)
    parser.add_argument('--create', help="attempt to create user model table before starting", action='store_true', default=False)
    parser.add_argument('--analyze', help="analyze features", action='store_true', default=False)
    parser.add_argument('--build', help="rebuild feature index", action='store_true', default=False)
    parser.add_argument('--visualize', help="visualize features upon analysis", action='store_true', default=False)
    parser.add_argument('--algorithm', help="selected clustering algorithm", choices=algorithm_names, default=algorithm_names[0])
    parser.add_argument('--n-clusters', help="for algorithms requiring explicit number of clusters", type=int, default=8)
    parser.add_argument('--n-jobs', help="number of parallel jobs (used where applicable)", type=int, default=2)
    parser.add_argument('features', help="override feature selection", nargs=argparse.REMAINDER, choices=feature_names)
    args = parser.parse_args()

    selected_feature_names = args.features or feature_names

    print "~ Using %d features" % len(selected_feature_names)

    if args.build:
        print "~ Building feature set"
        build_feature_set(args, connection, selected_feature_names)
        print

    if args.analyze:
        print "~ Feature set analysis"
        analyze_feature_set(args, connection, selected_feature_names)
        print

    print "~ Perform clustering routine"
    clustering.run(args, connection, selected_feature_names)
    print
