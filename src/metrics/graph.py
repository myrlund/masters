from py2neo import neo4j

def connect():
    return neo4j.GraphDatabaseService("http://localhost:7474/db/data/")
NEO4J_CONNECTION = connect()

def first_degree_conversation_partners(person, **k):
    q = "START n = node:PERSON(_p = '%s') MATCH n -[:TALKED_TO]-> b RETURN COUNT(DISTINCT b)" % person
    return neo4j.CypherQuery(NEO4J_CONNECTION, q).execute_one()

def second_degree_conversation_partners(person, **k):
    q = "START n = node:PERSON(_p = '%s') MATCH n -[:TALKED_TO]-> b -[:TALKED_TO]-> c RETURN COUNT(DISTINCT c)" % person
    return neo4j.CypherQuery(NEO4J_CONNECTION, q).execute_one()

def conversations(person, **k):
    q = "START n = node:PERSON(_p = '%s') MATCH n -[r:TALKED_TO]-> b RETURN SUM(r.weight)" % person
    return neo4j.CypherQuery(NEO4J_CONNECTION, q).execute_one()

def second_degree_conversations(person, **k):
    q = "START n = node:PERSON(_p = '%s') MATCH n -[r1:TALKED_TO]-> b -[r2:TALKED_TO]-> c RETURN SUM(r1.weight) + SUM(r2.weight)" % person
    return neo4j.CypherQuery(NEO4J_CONNECTION, q).execute_one()

if __name__ == "__main__":
    import sys
    print "First degree:"
    print zip(sys.argv[1:], map(first_degree_aquaintances, sys.argv[1:]))
    print "Second degree:"
    print zip(sys.argv[1:], map(second_degree_aquaintances, sys.argv[1:]))
