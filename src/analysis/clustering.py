import json

from collections import defaultdict

from sklearn.cluster import KMeans, MeanShift, DBSCAN, estimate_bandwidth
from sklearn import preprocessing

import numpy as np
import warnings
warnings.filterwarnings("ignore")

from analysis import util

def feature_values_for_person(cursor, person, valid_features):
    cursor.execute('SELECT feature, value FROM user_models WHERE person = %s ORDER BY feature', (person,))
    feature_values = defaultdict(int, cursor.fetchall())
    return tuple(feature_values[f] for f in valid_features)

def get_data_vectors(cursor, features, normalize=True):

    # Get all persons present in user_models for wanted features
    persons = util.get_all_persons(cursor)

    # Map each person to value vector for features
    raw_vectors = map(lambda person: feature_values_for_person(cursor, person, features), persons)

    vectors = np.array(raw_vectors)
    normalized_vectors = None
    if normalize:
        print "  - normalizing vectors"
        normalized_vectors = preprocessing.normalize(vectors)

    return persons, vectors, normalized_vectors

def dbscan(args):
    return DBSCAN(3.0, 10)

def mean_shift(args):
    return MeanShift(bin_seeding=True)

def k_means(args):
    print "  - k_means with %d clusters." % args.n_clusters
    return KMeans(args.n_clusters, n_jobs=args.n_jobs)

ENABLED_ALGORITHMS = (
    dbscan,
    mean_shift,
    k_means,
)

def visualize_clusters(clusterer, features, X, n_clusters, labels):
    import pylab as pl
    from itertools import cycle

    pl.figure(1)
    pl.clf()

    colors = cycle('bgrcmykbgrcmykbgrcmykbgrcmyk')
    for k, col in zip(range(n_clusters), colors):
        my_members = labels == k
        pl.plot(X[my_members, 0], X[my_members, 1], col + '.')

    pl.title('Number of clusters: %d' % n_clusters)
    fname = 'images/%s-%d-features-%d-clusters.png' % (clusterer.__class__.__name__.lower(), len(features), n_clusters)
    pl.savefig(fname)
    print "  - wrote cluster visualization to %s." % fname

def save_run(connection, data, args):
    c = connection.cursor()

    yaml_features = "---\n" + "\n".join(["- " + feature for feature in data['features']])
    c.execute("INSERT INTO runs (algorithm, features, params, eval_db, eval_dunn, timespan_from, timespan_to) VALUES (%s, %s, %s, %s, %s, %s, %s)", (data['algorithm'], yaml_features, data['params'], data['evaluation']['davies_bouldin'], data['evaluation']['dunn']) + args.timespan)
    run_id = connection.insert_id()

    for cluster in data['clusters']:
        yaml_center = "---\n" + "\n".join(["- " + str(v) for v in cluster['center']])
        c.execute("INSERT INTO clusters (run_id, center) VALUES (%s, %s)", (run_id, yaml_center))
        cluster_id = connection.insert_id()

        for member in cluster['members']:
            c.execute("INSERT INTO classifications (cluster_id, person) VALUES (%s, %s)", (cluster_id, member['person']))
            classification_id = connection.insert_id()

            for feature, value, normalized_value in member['feature_values']:
                c.execute("INSERT INTO feature_values (classification_id, feature, value, normalized_value) VALUES (%s, %s, %s, %s)", (classification_id, feature, value, normalized_value))

    connection.commit()

def cluster(algorithm, persons, X, X_raw, features, args):
    # clusterer = KMeans(n_clusters, n_jobs=1)
    clusterer = algorithm(args)
    clusterer.fit(X)

    labels = clusterer.labels_
    labels_unique = np.unique(labels)
    n_clusters = len(labels_unique)

    cluster_centers = [(None,) * len(features)] * n_clusters
    try:
        cluster_centers = clusterer.cluster_centers_
    except AttributeError:
        pass

    run_data = {
        'algorithm': clusterer.__class__.__name__,
        'features': features,
        'params': json.dumps(vars(args)),
        'clusters': [],
    }

    for i in xrange(n_clusters):
        # label = labels[i]
        center = cluster_centers[i]

        run_data['clusters'].append({'center': center, 'members': []})

    for person, sample, normalized_sample in zip(persons, X_raw, X):

        # Use either real sample or the normalized sample
        predictive_sample = normalized_sample if args.normalize else sample

        cluster_index = clusterer.predict(predictive_sample)
        feature_values = zip(features, sample, normalized_sample)

        person_data = {
            'person': person,
            'feature_values': feature_values,
        }

        run_data['clusters'][cluster_index]['members'].append(person_data)

    run_data['evaluation'] = evaluate_run(run_data['clusters'])

    visualize_clusters(clusterer, features, X, n_clusters, labels)

    return run_data

def evaluate_run(data):
    centers = []
    cluster_data = {}
    for i in xrange(len(data)):
        centers.append(data[i]['center'])
        cluster_data[i] = []
        for person in data[i]['members']:
            cluster_data[i].append(map(lambda p: p[2], person['feature_values']))

    from evaluation.cluster import davies_bouldin, dunn

    eval_fns = (davies_bouldin, dunn)
    results = {}
    for eval_fn in eval_fns:
        evaluation = eval_fn(centers, cluster_data)
        results[eval_fn.__name__] = evaluation
        print "  - %s evaluation result: %.2f" % (eval_fn.__name__, evaluation)

    return results

def run(args, connection, features):
    """Runs clustering routine."""

    # Select algorithm
    algorithm_names = map(lambda a: a.__name__, ENABLED_ALGORITHMS)
    algorithm_fn = dict(zip(algorithm_names, ENABLED_ALGORITHMS))[args.algorithm]

    # Ensure the feature set is sorted
    features = sorted(features)

    # Grab user model vectors
    print "  - retrieving user models"
    persons, X_raw, X = get_data_vectors(connection.cursor(), features, normalize=args.normalize)

    # Loop through requested cluster cardinalities
    print "  - clustering %d times with the %s algorithm" % (args.n_runs, args.algorithm)
    evals = []
    runs = []
    run_data = cluster(algorithm_fn, persons, X, X_raw, features=features, args=args)
    runs.append(run_data)
    evals.append(run_data['evaluation']['davies_bouldin'])

    # Grab the best one, the one with the minimal davies-bouldin index
    data = runs[evals.index(min(evals))]

    save_run(connection, data, args=args)

    # print "Centers for n = %d:" % n_clusters
    # print "\n".join(map(str, centers))

