#!/usr/bin/env python

import json, sys, os
import MySQLdb as mysql

from util import connect_db, load_config

INTERESTING_EVENT_TYPES = (
    'chat',
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
    'visited room',
    'room lock changed',
)

def batches(l, n):
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

def get_dirty_data(cursor, batch_size=50000):
    cursor.arraysize = batch_size

    cursor.execute("SELECT max(timestamp) from events_ref")
    max_timestamp1 = cursor.fetchone()[0] or 0
    cursor.execute("SELECT max(timestamp) from events_ref_omitted")
    max_timestamp2 = cursor.fetchone()[0] or 0

    max_timestamp = max(max_timestamp1, max_timestamp2)

    fields = ('id', 'raw_event', 'timestamp', 'person', 'raw_json')
    cursor.execute("""SELECT %s FROM events_raw
                  WHERE timestamp > %d ORDER BY timestamp""" % (", ".join(fields), max_timestamp))
    rows = cursor.fetchmany()

    return rows

def insert_clean_data(conn, clean_data):
    c = conn.cursor()
    for row in clean_data:
        if len(clean_data[6]) > 200:
            continue
        c.execute('INSERT INTO events_ref VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', row)
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
        event = normalize_event(row[1])
    except AttributeError:
        return None

    # Get special properties
    json_data = json.loads(row[4])
    roomname = json_data.get('roomname', None)

    # Don't support ridiculously long roomnames
    if roomname is not None and len(roomname) > 200:
        return None

    url = json_data.get('url', None)

    return (row[0], row[3], row[2]) + event + (roomname, url)

def omit_uninteresting_events(conn, events):
    c = conn.cursor()
    interesting_events = []
    uninteresting_events = []
    for event in events:
        if event[3] not in INTERESTING_EVENT_TYPES:
            uninteresting_events.append((event[0], event[2]))
        else:
            interesting_events.append(event)

    c.executemany('INSERT INTO events_ref_omitted VALUES (%s, %s)', uninteresting_events)
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

    print "Resetting room presences."
    c.execute("""DELETE FROM room_presences""")

    print "Extracting room presences."
    c.execute("""INSERT INTO room_presences (id, person, timestamp, roomname)
                 SELECT raw_id, person, timestamp, roomname FROM events_ref
                     WHERE event_type = 'visited room' AND person IS NOT NULL""")

    print
    print "Deleting user graph entries."
    c.execute("""DELETE FROM user_graph""")

    print "Building new user graph entries."
    c.execute("""INSERT INTO user_graph (person1, person2, timestamp)
                 SELECT p1.person, p2.person, p1.timestamp from room_presences as p1
                 LEFT JOIN room_presences AS p2
                     ON p1.person < p2.person AND p1.roomname = p2.roomname AND p1.timestamp < p2.timestamp + 900 AND p1.timestamp > p2.timestamp - 900
                 GROUP BY p1.person, p2.person HAVING p1.person IS NOT NULL AND p2.person IS NOT NULL""")

    conn.commit()

if __name__ == '__main__':
    CONFIG = load_config()
    connection = connect_db(CONFIG)

    import argparse
    parser = argparse.ArgumentParser(description="Parses sentences.")
    parser.add_argument('-b', '--batch-size', help="batch size", type=int, default=50000)
    parser.add_argument('--reset', help="clear clean table before running", action='store_true', default=False)
    args = parser.parse_args()

    if args.reset:
        print "Clearing clean table..."
        clear_clean(connection)
        print "Done."

    print "Building new version of cleaned table."
    while True:
        dirty_data = get_dirty_data(connection.cursor(), batch_size=args.batch_size)
        clean_data = filter(drop_falsy, map(clean_row, dirty_data))

        if not clean_data: break

        events = omit_uninteresting_events(connection, clean_data)

        insert_clean_data(connection, events)

        sys.stdout.write('.')
        sys.stdout.flush()
    print "Done."
    print

    build_user_graph(connection)
    print "Done."
