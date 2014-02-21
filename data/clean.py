#!/usr/bin/env python

import sqlite3, json, sys

def get_dirty_data(cursor, batch_size=5000):
    cursor.arraysize = batch_size
    
    fields = ('id', 'raw_event', 'timestamp', 'person', 'raw_json')
    cursor.execute("""SELECT %s FROM events_raw
                  WHERE id NOT IN (
                   SELECT raw_id FROM events_ref
                  )""" % ", ".join(fields))
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

def drop_falsy(row):
    return row

def clear_clean(conn):
    c = conn.cursor()
    c.execute('DELETE FROM events_ref')
    conn.commit()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Parses sentences.")
    parser.add_argument('-d', '--database', help="database file", default='data.db')
    parser.add_argument('-b', '--batch-size', help="batch size", type=int, default=50000)
    parser.add_argument('--reset', help="clear clean table before running", action='store_true', default=False)
    args = parser.parse_args()
    
    connection = sqlite3.connect(args.database)
    connection.row_factory = sqlite3.Row
    
    if args.reset:
        print "Clearing clean table..."
        clear_clean(connection)
        print "Done."
    
    while True:
        fields, dirty_data = get_dirty_data(connection.cursor(), batch_size=args.batch_size)
        clean_data = filter(drop_falsy, map(clean_row, dirty_data))
        
        if not clean_data: break
        
        insert_clean_data(connection, clean_data)
        
        sys.stdout.write('.')
        sys.stdout.flush()

    print "Done."
