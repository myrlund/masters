from cluster_dists import get_feature_values_for_persons_in_cluster, get_cluster_ids

import numpy as np
import matplotlib.pyplot as plt

if __name__ == '__main__':
    from util import load_config, connect_db
    CONFIG = load_config()

    connection = connect_db(CONFIG)

    import argparse
    parser = argparse.ArgumentParser(description="Analyze weird parts of clusters.")
    parser.add_argument('--clusters', help="comma-separated cluster ids")
    parser.add_argument('--run', help='run id')
    parser.add_argument('--table', help="select entry table", default="classifications")
    parser.add_argument('features', help="select features", nargs=argparse.REMAINDER)

    args = parser.parse_args()

    from main import MODEL_FEATURES

    features = args.features
    if len(features) == 0:
        features = map(lambda fn: fn.__name__, MODEL_FEATURES)

    if args.run:
        cluster_ids = get_cluster_ids(connection.cursor(), args.run)
    else:
        cluster_ids = args.clusters.split(',')

    for feature in features:
        print "FEATURE: %s" % feature
        feature_values = {}
        for cluster_id in cluster_ids:
            values = get_feature_values_for_persons_in_cluster(connection.cursor(), cluster_id, feature, args.table)
            for do_log in (True, False):
                plt.hist(values, max(values) or 1, log=do_log)
                plt.xlabel(feature)
                plt.ylabel('instances')
                plt.savefig("images/feature-correlations-%s-cluster-%d%s.png" % (feature, cluster_id, '-log' if do_log else ''))
                plt.clf()

            feature_values[cluster_id] = values

        all_values = sum(feature_values.values(), [])
        print all_values[:10]

        for cluster_id, values in feature_values.iteritems():
            print "  cluster %s" % str(cluster_id)
            print "    count: %d" % len(values)
            print "    mean: %.3f" % np.mean(values)
            print "    median: %.3f" % np.median(values)
            print "    max: %d" % max(values)
            print "    n_not_0: %d" % len([v for v in values if v > 0.0])
            print "    w_n_not_0: %.3f" % (1.0 * len([v for v in values if v > 0.0]) / len(values))
            print "    variation: %.3f" % np.var(values)
            # print "    correlation with entire pop: %s" % str(np.correlate(values, all_values, mode='same'))
