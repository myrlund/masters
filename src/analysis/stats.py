import numpy as np
import math

def analyze_feature(conn, feature, all_values):
    values = filter(lambda v: v is not None, all_values)

    aggregate_keys = ('sum', 'count', 'max', 'min')

    c = conn.cursor()
    c.execute('SELECT SUM(value) as sum, COUNT(value) as count, MAX(value) as max, MIN(value) as min FROM user_models WHERE feature = %s', (feature,))
    aggregates = dict(zip(aggregate_keys, c.fetchone()))

    average = aggregates['sum'] / aggregates['count']
    stddev = math.sqrt(sum([(x - average)**2 for x in values]))

    print "Analyzing feature '%s':" % feature
    for agg in aggregates.keys():
        print "%s: %.1f" % (agg, aggregates[agg])
    print "average: %.1f" % average
    print "stddev:  %.1f" % stddev
    print "median:  %.1f" % values[len(values) / 2]
    print
