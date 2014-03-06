import util

from export import neo4j

def get_all_relationships(cursor):
    cursor.execute('SELECT * FROM user_graph')
    return cursor.fetchall()

if __name__ == '__main__':
    connection = util.connect_db(util.load_config())
    print "Fetching all relationships"
    relationships = get_all_relationships(connection.cursor())
    print "  - fetched %d relationships" % len(relationships)
    print "Exporting to neo4j"
    neo4j.export(relationships)
    print "\n  - done"

