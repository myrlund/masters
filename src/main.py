#!/usr/bin/env python

import sqlite3
import os, sys

from analysis import util, clustering, stats, visualize

def create_table(conn):
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS user_models (person VARCHAR(120), feature VARCHAR(150), value REAL, PRIMARY KEY (person, feature))')
    conn.commit()

# Feature metric functions
from metrics.simple import rooms_used, rooms_claimed, roomnames_generated, frequency_last_month
from metrics.graph import conversation_partners_per_person, conversations_per_person

FEATURES = (conversation_partners_per_person, conversations_per_person, rooms_used) # , rooms_claimed, roomnames_generated, frequency_last_month

def build_feature_set(args, connection):
    """Clears and rebuilds selected features from various general data sources."""
    
    if args.create:
        create_table(connection)
    
    for feature_fn in FEATURES:
        name = feature_fn.__name__
        
        if args.reset or raw_input("Rebuild feature '%s'? [yN] " % name) in ("y", "Y"):
        
            print name
            
            print "  - clearing old values"
            util.clear_feature_values(connection, name)
            
            print "  - extracting feature values: ",
            for batch in feature_fn(connection.cursor(), batch_size=args.batch_size):
                util.insert_feature_values(connection, name, batch)
                sys.stdout.write('.')
                sys.stdout.flush()
            print

def analyze_feature_set(args, connection):
    """Analyzes and plots various standard metrics for each feature."""
    
    for feature_fn in FEATURES:
        name = feature_fn.__name__
        
        values = util.get_feature_values(connection, name)
        
        stats.analyze_feature(connection, name, values)
        
        if args.visualize:
            visualize.plot_feature(connection, name, values)

if __name__ == '__main__':
    from util import load_config, connect_db
    CONFIG = load_config()
    
    connection = connect_db(CONFIG)
    
    import argparse
    parser = argparse.ArgumentParser(description="Parses sentences.")
    parser.add_argument('-b', '--batch-size', help="batch size", type=int, default=500)
    parser.add_argument('--reset', help="clear features before rebuilding", action='store_true', default=False)
    parser.add_argument('--create', help="attempt to create user model table before starting", action='store_true', default=False)
    parser.add_argument('--analyze', help="analyze features", action='store_true', default=False)
    parser.add_argument('--build', help="rebuild feature index", action='store_true', default=False)
    parser.add_argument('--visualize', help="visualize features upon analysis", action='store_true', default=False)
    args = parser.parse_args()
    
    if args.build:
        print "~ Building feature set"
        build_feature_set(args, connection)
        print
    
    if args.analyze:
        print "~ Feature set analysis"
        analyze_feature_set(args, connection)
        print
    
    print "~ Perform clustering routine"
    feature_names = map(lambda f: f.__name__, FEATURES)
    clustering.run(args, connection, feature_names)
    print
