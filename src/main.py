#!/usr/bin/env python

import sqlite3
import os, sys
import datetime
import math

from collections import defaultdict

from sklearn.cluster import MeanShift

def batches(l, n):
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

def bucket_discretely(field, l):
    l = map(lambda x: (x[field], x - (x[field],)), events)
    return reduce(lambda x, (k,v): x[k].append(v) or x, l, defaultdict(list))

def create_table(conn):
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS user_models (person VARCHAR, feature VARCHAR, value REAL, PRIMARY KEY (person, feature))')
    conn.commit()

# Feature support

def clear_feature_values(conn, feature_name):
    c = conn.cursor()
    c.execute('DELETE FROM user_models WHERE feature = ?', (feature_name,))
    conn.commit()

def insert_feature_values(conn, feature_name, values):
    """Parameter values should be tuples of (person, value) for feature called feature_name."""
    new_rows = map(lambda t: (feature_name,) + tuple(t), values)
    
    print "Inserting %d values for feature '%s'." % (len(new_rows), feature_name)
    
    c = conn.cursor()
    c.executemany('INSERT INTO user_models (feature, person, value) VALUES (?, ?, ?)', new_rows)
    conn.commit()

def analyze_feature(conn, feature):
    c = conn.cursor()
    c.execute('SELECT SUM(value) as sum, COUNT(value) as count, MAX(value) as max, MIN(value) as min FROM user_models WHERE feature = ?', (feature,))
    aggregates = c.fetchone()
    
    c.execute('SELECT value FROM user_models WHERE feature = ?', (feature,))
    values = c.fetchall()
    
    average = aggregates['sum'] / aggregates['count']
    stddev = math.sqrt(sum(map(lambda row: (row[0] - average)**2, values)) / aggregates['count'])
    
    print "Analyzing feature '%s':" % feature
    for agg in aggregates.keys():
        print "%s: %.1f" % (agg, aggregates[agg])
    print "average: %.1f" % average
    print "stddev:  %.1f" % stddev
    print 

def get_feature_values(conn, feature):
    c = conn.cursor()
    c.execute('SELECT value FROM user_models WHERE feature = ?', (feature,))
    return map(lambda x: x[0], c.fetchall())

def plot_feature(conn, feature, log=False):
    """Do a simple histogram to determine distribution."""
    values = get_feature_values(conn, feature)
    
    # Yay, mutability
    if log: values = map(lambda x: math.log(x), filter(lambda x: x, values))
    
    import matplotlib.pyplot as plt
    plt.hist(values, bins=50)
    plt.show()

# Features

def rooms_claimed(c):
    c.execute('SELECT person, COUNT(distinct roomname) AS count FROM events_ref WHERE event_type = \'room claimed\' GROUP BY person')
    rows = c.fetchall()
    return rows

def rooms_used(c):
    c.execute('SELECT person, COUNT(distinct roomname) AS count FROM events_ref WHERE event_type = \'visited room\' GROUP BY person')
    rows = c.fetchall()
    return rows

def roomnames_generated(c):
    c.execute('SELECT person, COUNT(*) AS count FROM events_ref WHERE event_verb = \'randomized new room name\' GROUP BY person')
    rows = c.fetchall()
    return rows

def frequency_last_month(c):
    a_month_ago = ((datetime.datetime.now() - datetime.timedelta(weeks=4)) - datetime.datetime(1970, 1, 1)).total_seconds()
    c.execute('SELECT person, COUNT(*) AS count FROM events_ref WHERE event_type = \'in a conversation\' ' +
              'AND timestamp > ? GROUP BY person', (a_month_ago,))
    rows = c.fetchall()
    return rows



FEATURES = (rooms_used, rooms_claimed, roomnames_generated, frequency_last_month)

if __name__ == '__main__':
    from util import load_config
    current_dir = os.path.dirname(os.path.abspath(__file__))
    CONFIG = load_config(os.path.join(current_dir, 'config.json'))
    
    import argparse
    parser = argparse.ArgumentParser(description="Parses sentences.")
    parser.add_argument('-d', '--database', help="database file", default=os.path.join(CONFIG['data_root'], 'data.db'))
    parser.add_argument('-b', '--batch-size', help="batch size", type=int, default=50000)
    parser.add_argument('--reset', help="clear clean table before running", action='store_true', default=False)
    parser.add_argument('--analyze', help="analyze features", action='store_true', default=False)
    parser.add_argument('--build', help="rebuild feature index", action='store_true', default=False)
    args = parser.parse_args()
    
    connection = sqlite3.connect(args.database)
    connection.row_factory = sqlite3.Row
    
    if args.build:
        create_table(connection)
    
        for feature_fn in FEATURES:
            name = feature_fn.__name__
            values = feature_fn(connection.cursor())
        
            clear_feature_values(connection, name)
            insert_feature_values(connection, name, values)
    
    if args.analyze:
        print "\n\nFeature analysis:\n"
        for feature_fn in FEATURES:
            name = feature_fn.__name__
            analyze_feature(connection, name)
        
        for feature_fn in FEATURES:
            name = feature_fn.__name__
            plot_feature(connection, name)
    
    print "Let's cluster!"
    
    # print n_rooms_used(connection).get('bxkoh5pb3hm/0vwmsbtu1/vrliq=', 0)
    # print n_rooms_claimed(connection).get('bxkoh5pb3hm/0vwmsbtu1/vrliq=', 0)
    
    # build_user_model(connection, 'bxkoh5pb3hm/0vwmsbtu1/vrliq=')
    
