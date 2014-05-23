import sys

from py2neo import neo4j

NODE_INDEX        = 'PERSON'
RELATIONSHIP_TYPE = 'TALKED_TO'

def export_row(service, row):
    """Exports p1, p2, weight tuple."""

    p1, p2, timestamp = row

    node1 = service.get_or_create_indexed_node(NODE_INDEX, '_p', p1, {'id': p1})
    node2 = service.get_or_create_indexed_node(NODE_INDEX, '_p', p2, {'id': p2})
    rels = node1.create_path((RELATIONSHIP_TYPE, {'timestamp': timestamp}), node2)

    sys.stdout.write('.'); sys.stdout.flush()

    return (node1, node2, rels)

def export(relationships):
    service = neo4j.GraphDatabaseService("http://localhost:7474/db/data/")

    # Clear all existing nodes and relationships
    print "  - clearing existing"
    service.clear()

    # Export new ones
    print "  - exporting new ones"
    return map(lambda row: export_row(service, row), relationships)

