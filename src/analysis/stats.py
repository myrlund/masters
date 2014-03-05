import numpy as np
import math

def analyze_feature(conn, feature, values):
    aggregate_keys = ('sum', 'count', 'max', 'min')
    
    c = conn.cursor()
    c.execute('SELECT SUM(value) as sum, COUNT(value) as count, MAX(value) as max, MIN(value) as min FROM user_models WHERE feature = %s', (feature,))
    aggregates = dict(zip(aggregate_keys, c.fetchone()))
    
    average = aggregates['sum'] / aggregates['count']
    stddev = np.std(values)
    
    print "Analyzing feature '%s':" % feature
    for agg in aggregates.keys():
        print "%s: %.1f" % (agg, aggregates[agg])
    print "average: %.1f" % average
    print "stddev:  %.1f" % stddev
    print "median:  %.1f" % values[len(values) / 2]
    print 
