from collections import defaultdict

from sklearn.cluster import KMeans, MeanShift, DBSCAN, estimate_bandwidth
import numpy as np

from analysis import util

def feature_values_for_person(cursor, person, valid_features):
    cursor.execute('SELECT feature, value FROM user_models WHERE person = %s ORDER BY feature', (person,))
    feature_values = defaultdict(int, cursor.fetchall())
    return tuple(feature_values[f] for f in valid_features)

def get_data_vectors(cursor, features):

    # Get all persons present in user_models for wanted features
    persons = util.get_all_persons(cursor)

    # Map each person to value vector for features
    vectors = map(lambda person: feature_values_for_person(cursor, person, features), persons)

    return np.array(vectors)

def cluster(X, n_clusters, features):
    # bandwidth = estimate_bandwidth(X, quantile=0.5, n_samples=5000)
    # clusterer = MeanShift(bandwidth=bandwidth, bin_seeding=True)
    # clusterer = KMeans(n_clusters, n_jobs=1)
    clusterer = DBSCAN(3.0, 10)
    clusterer.fit(X)

    labels = clusterer.labels_
    # cluster_centers = clusterer.cluster_centers_

    # labeled_centers = map(lambda c: zip(features, c), cluster_centers)

    labels_unique = np.unique(labels)
    n_clusters_ = len(labels_unique)

    import pylab as pl
    from itertools import cycle

    pl.figure(1)
    pl.clf()

    colors = cycle('bgrcmykbgrcmykbgrcmykbgrcmyk')
    for k, col in zip(range(n_clusters_), colors):
        my_members = labels == k
        # cluster_center = cluster_centers[k]
        pl.plot(X[my_members, 0], X[my_members, 1], col + '.')
        # pl.plot(cluster_center[0], cluster_center[1], 'o', markerfacecolor=col, markeredgecolor='k', markersize=14)
    pl.title('Number of clusters: %d' % n_clusters_)
    fname = 'images/%s-%d-features-%d-clusters.png' % (clusterer.__class__.__name__.lower(), len(features), n_clusters_)
    pl.savefig(fname)
    print " - wrote cluster visualization to %s." % fname

    # return labeled_centers

def run(args, connection, features):
    """Runs clustering routine."""

    # Ensure the feature set is sorted
    features = sorted(features)

    # Grab user model vectors
    X = get_data_vectors(connection.cursor(), features)

    # Loop through requested cluster cardinalities
    # for n_clusters in xrange(2, 6+1):
    cluster(X, n_clusters=None, features=features)
    # print "Centers for n = %d:" % n_clusters
    # print "\n".join(map(str, centers))

