import time

from py2neo import neo4j

def current_time():
    return int(time.time())

def connect():
    return neo4j.GraphDatabaseService("http://localhost:7474/db/data/")
NEO4J_CONNECTION = connect()

def run_query(q, **options):
    where = ''
    if 'timespan' in options:
        where = "WHERE ALL(r IN rs WHERE r.timestamp >= %s AND r.timestamp < %s)" % options['timespan']
    return neo4j.CypherQuery(NEO4J_CONNECTION, q % where).execute_one()

def first_degree_conversation_partners(person, **k):
    q = "START n = node:PERSON(_p = '%s') MATCH n -[rs:TALKED_TO*1]-> b %%s RETURN COUNT(DISTINCT b)" % person
    return run_query(q, **k)

def second_degree_conversation_partners(person, **k):
    q = "START n = node:PERSON(_p = '%s') MATCH n -[rs:TALKED_TO*2]-> c %%s RETURN COUNT(DISTINCT c)" % person
    return run_query(q, **k)

def conversations(person, **k):
    q = "START n = node:PERSON(_p = '%s') MATCH n -[rs:TALKED_TO*1]-> b %%s RETURN COUNT(rs)" % person
    return  run_query(q, **k)

def second_degree_conversations(person, **k):
    q = "START n = node:PERSON(_p = '%s') MATCH n -[rs:TALKED_TO*2]-> c %%s RETURN COUNT(rs)" % person
    return  run_query(q, **k)

if __name__ == "__main__":
    import sys
    print "First degree:"
    print zip(sys.argv[1:], map(first_degree_aquaintances, sys.argv[1:]))
    print "Second degree:"
    print zip(sys.argv[1:], map(second_degree_aquaintances, sys.argv[1:]))
