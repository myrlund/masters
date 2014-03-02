#!/usr/bin/env python

import sqlite3, json, sys

INTERESTING_EVENT_TYPES = ('chat',
                           'claim room',
                           'connection',
                           'customization',
                           'entered existing room',
                           'entered new room',
                           'follow room',
                           'frontpage',
                           'in a conversation',
                           'room',
                           'room claimed',
                           'visited room')

def batches(l, n):
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

def get_dirty_data(cursor, batch_size=5000):
    cursor.arraysize = batch_size
    
    fields = ('id', 'raw_event', 'timestamp', 'person', 'raw_json')
    cursor.execute("""SELECT %s FROM events_raw
                  WHERE id NOT IN (
                   SELECT raw_id FROM events_ref
                  ) AND id NOT IN (
                   SELECT raw_id FROM events_ref_omitted
                  )""" % (", ".join(fields),))
    rows = cursor.fetchmany()
    
    if len(rows) > 0:
        return fields, rows
    else:
        return None

def insert_clean_data(conn, clean_data):
    c = conn.cursor()
    c.executemany('INSERT INTO events_ref VALUES (?, ?, ?, ?, ?, ?, ?, ?)', clean_data)
    conn.commit()

def normalize_event(raw_event):
    event_parts = raw_event.split("  ")
    
    event_type   = None
    event_verb   = None
    event_object = None
    try:
        event_type   = event_parts[0]
        event_verb   = event_parts[1]
        event_object = event_parts[2]
    except IndexError: pass
    
    return event_type, event_verb, event_object

def clean_row(row):
    # Normalize into three parts
    try:
        event = normalize_event(row['raw_event'])
    except AttributeError:
        return None
    
    # Get special properties
    json_data = json.loads(row['raw_json'])
    roomname = json_data.get('roomname', None)
    url = json_data.get('url', None)
    
    return (row['id'], row['person'], row['timestamp']) + event + (roomname, url)

def omit_uninteresting_events(conn, events):
    c = conn.cursor()
    interesting_events = []
    uninteresting_events = []
    for event in events:
        if event[3] not in INTERESTING_EVENT_TYPES:
            uninteresting_events.append(event[0])
        else:
            interesting_events.append(event)
    
    c.executemany('INSERT INTO events_ref_omitted VALUES (?)', map(lambda id: (id,), uninteresting_events))
    conn.commit()
    
    return interesting_events

def drop_falsy(row):
    return row

def clear_clean(conn):
    c = conn.cursor()
    c.execute('DELETE FROM events_ref')
    conn.commit()

def clear_user_graph(conn):
    c = conn.cursor()
    c.execute('DELETE FROM user_graph')
    conn.commit()

def build_user_graph(conn, batch_size=50000):
    c = conn.cursor()
    c.arraysize = batch_size
    
    c.execute("""SELECT p1.person AS person1, p2.person AS person2, COUNT(*) AS n_conversations
        FROM events_ref AS p1 LEFT JOIN events_ref AS p2 ON
            p1.roomname = p2.roomname
            AND p1.person < p2.person
            AND p1.timestamp > p2.timestamp - 900 AND p1.timestamp < p2.timestamp + 900 -- join within half an hour of each other
        WHERE
            -- p1.timestamp > 1388534400 AND p2.timestamp > 1388534400 AND
            
            p1.roomname IS NOT NULL
            AND p1.event_type = 'visited room' AND p2.event_type = 'visited room'
            
            -- Allow for batching
            -- AND p1.person NOT IN (SELECT person1 FROM user_graph WHERE person1 < p2.person)
            -- AND p2.person NOT IN (SELECT person2 FROM user_graph WHERE person2 > p1.person)
        GROUP BY
            p1.person, p2.person""")
    
    # Simply insert fetched data into new table
    rows = c.fetchall()
    c.executemany('INSERT INTO user_graph VALUES (?, ?, ?)', rows)
    conn.commit()
    return len(rows)
    

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Parses sentences.")
    parser.add_argument('-d', '--database', help="database file", default='data.db')
    parser.add_argument('-b', '--batch-size', help="batch size", type=int, default=50000)
    parser.add_argument('--reset', help="clear clean table before running", action='store_true', default=False)
    args = parser.parse_args()
    
    connection = sqlite3.connect(args.database)
    
    if args.reset:
        print "Clearing clean table..."
        clear_clean(connection)
        print "Done."
    
    print "Building new version of cleaned table."
    while True:
        connection.row_factory = sqlite3.Row
        
        fields, dirty_data = get_dirty_data(connection.cursor(), batch_size=args.batch_size)
        clean_data = filter(drop_falsy, map(clean_row, dirty_data))
        
        if not clean_data: break
        
        events = omit_uninteresting_events(connection, clean_data)
        
        insert_clean_data(connection, events)
        
        sys.stdout.write('.')
        sys.stdout.flush()
    print "Done."
    print
    
    connection.row_factory = None
    
    print "Clearing user graph..."
    clear_user_graph(connection)
    
    print "OK. Now, building a new user graph..."
    build_user_graph(connection)
    print "Done."
