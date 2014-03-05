from collections import defaultdict

from sklearn.cluster import KMeans, MeanShift, estimate_bandwidth
import numpy as np

from analysis import util

def feature_values_for_person(cursor, person, valid_features):
    cursor.execute('SELECT feature, value FROM user_models WHERE person = %s ORDER BY feature', (person,))
    feature_values = defaultdict(int, cursor.fetchall())
    return tuple(feature_values[f] for f in valid_features)

def get_data_vectors(cursor, features):
    
    # Ensure the feature set is sorted
    features = sorted(features)
    
    # Get all persons present in user_models for wanted features
    persons = util.get_all_persons(cursor)
    
    # Map each person to value vector for features
    vectors = map(lambda person: feature_values_for_person(cursor, person, features), persons)
    
    return np.array(vectors)

def run(args, connection, features):
    """Runs clustering routine."""
    
    X = get_data_vectors(connection.cursor(), features)
    
    # bandwidth = estimate_bandwidth(X, quantile=0.5, n_samples=5000)
    # ms = MeanShift(bandwidth=bandwidth, bin_seeding=True)
    ms = KMeans(n_clusters=5, n_jobs=-1)
    
    ms.fit(X)
    
    labels = ms.labels_
    cluster_centers = ms.cluster_centers_
    
    labeled_centers = map(lambda c: zip(features, c), cluster_centers)
    print "Centers:"
    print "\n".join(map(str, labeled_centers))
    
    labels_unique = np.unique(labels)
    n_clusters_ = len(labels_unique)
    
    import pylab as pl
    from itertools import cycle

    pl.figure(1)
    pl.clf()

    colors = cycle('bgrcmykbgrcmykbgrcmykbgrcmyk')
    for k, col in zip(range(n_clusters_), colors):
        my_members = labels == k
        cluster_center = cluster_centers[k]
        pl.plot(X[my_members, 0], X[my_members, 1], col + '.')
        pl.plot(cluster_center[0], cluster_center[1], 'o', markerfacecolor=col, markeredgecolor='k', markersize=14)
    pl.title('Estimated number of clusters: %d' % n_clusters_)
    pl.show()
