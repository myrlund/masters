
import math

def distance(a, b):
    assert len(a) == len(b), "vectors not the same length"

    return math.sqrt(sum(map(lambda d: (d[0] - d[1])**2, zip(a, b))))

def davies_bouldin(centers, cluster_data):
    k = len(centers)

    distances = {}
    avg_distances = {}
    for i in xrange(k):
        distances[i] = map(lambda x: distance(x, centers[i]), cluster_data[i])
        avg_distances[i] = 1.0 * sum(distances[i]) / len(distances[i])

    db_indices = []
    for i in xrange(k):
        candidates = []
        for j in xrange(k):
            if i == j: continue
            candidate = (avg_distances[i] + avg_distances[j]) / distance(centers[i], centers[j])
            candidates.append(candidate)

        db_indices.append(max(candidates))

    return 1.0 * sum(db_indices) / k

def dunn(centers, cluster_data):
    return 0.0

if __name__ == '__main__':
    centers = [(4, 5), (-1, -1)]
    cluster_data = {
        0: [(5, 6), (7, 5), (3, 2)],
        1: [(-4, -2), (0, 0), (-2, 0)],
    }
    print davies_bouldin(centers, cluster_data)
