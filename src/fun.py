#!/usr/bin/env python

import numpy as np

from py2neo import neo4j
from metrics.graph import NEO4J_CONNECTION

from cluster_dists import get_persons_in_cluster

def get_first_degree_conversation_partners_for_person(person):
    q = "START n = node:PERSON(_p = '%s') MATCH n -[:TALKED_TO]-> b RETURN DISTINCT(b.id)" % person
    result = neo4j.CypherQuery(NEO4J_CONNECTION, q).execute()
    return [r.values[0] for r in result]

def get_first_degree_conversation_partners_for_cluster(c, cluster_id):
    # Get persons in cluster
    persons = get_persons_in_cluster(c, cluster_id)

    # Get their conversation partners
    partners = map(get_first_degree_conversation_partners_for_person, persons)

    # Flatten and return unique
    return np.unique(sum(partners, []))

if __name__ == '__main__':
    from util import load_config, connect_db
    CONFIG = load_config()

    connection = connect_db(CONFIG)

    for cluster_id in (1233, 1235):
        tag = "partners-cluster-%d" % cluster_id

        print "processing cluster %d" % cluster_id
        all_partners = get_first_degree_conversation_partners_for_cluster(connection.cursor(), cluster_id)

        c = connection.cursor()

        data = zip([tag] * len(all_partners), all_partners)

        print "inserting %d rows into tmp, tagged %s." % (len(data), tag)
        c.executemany('INSERT INTO tmp (cluster_id, person) VALUES (%s, %s)', data)

        print "committing."
        connection.commit()

