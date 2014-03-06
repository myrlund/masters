from py2neo import neo4j

def connect():
    return neo4j.GraphDatabaseService("http://localhost:7474/db/data/")
connection = connect()

def first_degree_aquaintances(person, **kwargs):
    q =

def first_degree_aquaintances(person, **kwargs):
    q = "START n = node:PERSON(_p = '%s') MATCH n -[:TALKED_TO]-> b RETURN COUNT(DISTINCT b)" % person
    return neo4j.CypherQuery(connection, q).execute_one()

def second_degree_aquaintances(person, **kwargs):
    q = "START n = node:PERSON(_p = '%s') MATCH n -[:TALKED_TO]-> b -[:TALKED_TO]-> c RETURN COUNT(DISTINCT c)" % person
    return neo4j.CypherQuery(connection, q).execute_one()

if __name__ == "__main__":
    import sys
    print "First degree:"
    print zip(sys.argv[1:], map(first_degree_aquaintances, sys.argv[1:]))
    print "Second degree:"
    print zip(sys.argv[1:], map(second_degree_aquaintances, sys.argv[1:]))
