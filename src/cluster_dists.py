#!/usr/bin/env python

import numpy as np

def get_cluster_ids(c, run_id):
    c.execute('SELECT id FROM clusters WHERE run_id = %s', (run_id,))
    return map(lambda x: x[0], c.fetchall())

def get_persons_in_cluster(c, cluster_id):
    c.execute('SELECT person FROM classifications WHERE cluster_id = %s', (cluster_id,))
    return map(lambda row: row[0], c.fetchall())

def get_feature_values_for_persons_in_cluster(c, cluster_id, feature, table):
    c.execute("""SELECT value FROM user_models WHERE feature = %%s AND person IN (
        SELECT person FROM %s WHERE cluster_id = %%s
    )""" % table, (feature, cluster_id))

    return map(lambda row: row[0], c.fetchall())

# def print_stats(feature, values, weight=1):
#     print '  feature: %s' % feature
#     print '    n:       %d' % len(values)
#     print '    mean:    %.2f' % (np.mean(values) * weight)
#     print '    median:  %.2f' % np.median(values)
#     print '    std:     %.2f' % np.std(values)
#     print
#
# def get_variation_count_for_persons_in_cluster(c, cluster_id, variation, conversation_measure):
#     cluster_filter = "e1.person in (select person from classifications where cluster_id = %s) and" % cluster_id
#     return get_variation_count_for_persons(c, variation, conversion_measure, filter=cluster_filter)
#
# def get_variation_count_for_persons(c, variation, conversion_measure, filter=''):
#     c.execute("""SELECT count(distinct e1.person) from events_ref as e1
#                     left join events_ref as e2 on
#                         e1.person = e2.person and e2.timestamp > e1.timestamp and e2.timestamp < e1.timestamp + 500
#                     where
#                     %s
#                     e1.data like '%"alternative frontpage": "%s"%' and e2.event_type = '%s'
#     """ % cluster_filter, (variation, conversation_measure))
#     return c.fetchone()[0]

def get_converted_count_in_variation(c, cluster_id, variation, conversion_event):
    variation_filter = "%%\"alternative frontpage\": \"%s\"%%" % variation
    c.execute("""SELECT count(distinct e1.person) from events_ref as e1
                    left join events_ref as e2 on
                        e1.person = e2.person and e2.timestamp > e1.timestamp and e2.timestamp < e1.timestamp + 1800
                    where
                        e1.person in (select person from classifications where cluster_id = %s) and
                        e1.data like %s and
                        e2.event_type = %s""", (cluster_id, variation_filter, conversion_event))
    return c.fetchone()[0]
def get_person_count_in_variation(c, cluster_id, variation):
    variation_filter = "%%\"alternative frontpage\": \"%s\"%%" % variation
    c.execute("""SELECT count(distinct person) from events_ref where
                    person IN (select person from classifications where cluster_id = %s) and
                    data like %s""", (cluster_id, variation_filter))
    return c.fetchone()[0]

def visited_room(*args):
    return get_converted_count_in_variation(*args, conversion_event='visited room')

def in_a_conversation(*args):
    return get_converted_count_in_variation(*args, conversion_event='in a conversation')

def claimed_room(*args):
    return get_converted_count_in_variation(*args, conversion_event='room claimed')

def followed_room(*args):
    return get_converted_count_in_variation(*args, conversion_event='follow room')

CONVERSION_MEASURES = (visited_room, in_a_conversation, followed_room)

if __name__ == '__main__':

    from util import load_config, connect_db
    CONFIG = load_config()

    connection = connect_db(CONFIG)

    conversion_measure_names = map(lambda fn: fn.__name__, CONVERSION_MEASURES)

    import argparse
    parser = argparse.ArgumentParser(description="Analyze weird parts of clusters.")
    parser.add_argument('--clusters', help="comma-separated cluster ids")
    parser.add_argument('--run', help="run id")
    parser.add_argument('--conversion-measure', help="conversion measure", choices=conversion_measure_names, default=conversion_measure_names[0])
    parser.add_argument('variations', help="comma-separated conversion measures", nargs=argparse.REMAINDER)

    args = parser.parse_args()

    if args.run:
        cluster_ids = get_cluster_ids(connection.cursor(), args.run)
    else:
        cluster_ids = args.clusters.split(",")

    print "<table><thead><tr><th></th>"
    for variation in args.variations + ['total']:
        print "<th colspan='3'>%s</th>" % variation
    print "<th></th></tr><tr><th></th>"
    for variation in args.variations + ['total']:
        print "<th>n</th><th>converted</th><th>%</th>"
    print "<th>preferred variation</th></tr></thead><tbody>"

    conversion_measure_fn = dict(zip(conversion_measure_names, CONVERSION_MEASURES))[args.conversion_measure]

    for cluster_id in cluster_ids:
        print "<tr><th>Cluster %s</th>" % str(cluster_id)
        ns = []
        cs = []
        rs = []
        for variation in args.variations:
            n = get_person_count_in_variation(connection.cursor(), cluster_id, variation)
            c = conversion_measure_fn(connection.cursor(), cluster_id, variation)
            print "<td>%d</td><td>%d</td><td>%.2f</td>" % (n, c, 100.0*c/n)

            ns.append(n)
            cs.append(c)
            rs.append(1.0*c/n)
        print "<td>%d</td><td>%d</td><td>%.2f</td>" % (sum(ns), sum(cs), 100.0*sum(cs)/sum(ns))
        print "<td>%s</td>" % args.variations[rs.index(max(rs))]

        print "</tr>"

    print "</tbody></table>"
