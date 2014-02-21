#!/usr/bin/env python

import sqlite3, json, sys

RAW_TABLE = 'events_raw'

FIELDS = (
    '_id',
    '_n',
    '_t',
    '_p',
)
LOAD_RAW_DATA = True

def create_table(conn):
    fields = (
        'id INTEGER PRIMARY KEY AUTOINCREMENT',
        'raw_event VARCHAR',
        'timestamp INTEGER',
        'person VARCHAR',
        'raw_json TEXT',
    )
    stmt = "CREATE TABLE IF NOT EXISTS %s (%s)" % (RAW_TABLE, ", ".join(fields))
    
    print "Executing: %s" % stmt
    
    c = conn.cursor()
    c.execute(stmt)
    conn.commit()

def get_latest_timestamp(conn):
    c = conn.cursor()
    c.execute("SELECT timestamp FROM %s ORDER BY timestamp DESC LIMIT 1" % RAW_TABLE)
    data = c.fetchone() or [0]
    return data[0]

def load_km_index(fname, lower_timestamp_limit):
    import csv
    data = []
    with open(fname, 'rb') as csvfile:
        indexreader = csv.DictReader(csvfile)
        for row in indexreader:
            if int(row['max_timestamp']) > lower_timestamp_limit:
                data.append(row['filename'])
    return data

def clean_event_data(raw_data):
    data = []
    for raw_key in FIELDS:
        if raw_key in raw_data:
            data.append(raw_data[raw_key])
        else:
            data.append(None)
    
    if LOAD_RAW_DATA:
        data.append(json.dumps(raw_data))
    else:
        data.append(None)
    
    return tuple(data)

def process_data_file(conn, fname, latest_timestamp=0):
    with open(fname, 'r') as datafile:
        s = datafile.readlines()
        event_data = []
        for line in s:
            try:
                raw_event_data = json.loads(line)
                if int(raw_event_data['_t']) > latest_timestamp:
                    event_data.append(clean_event_data(raw_event_data))
            except ValueError, e: pass
    
    if len(event_data) > 0:
        c = conn.cursor()
        
        sys.stdout.write('.')
        sys.stdout.flush()
        
        c.executemany("INSERT INTO " + RAW_TABLE + " VALUES (" + "?, " * len(FIELDS) + "?)", event_data)
        conn.commit()
    
    else:
        sys.stdout.write('o')
        sys.stdout.flush()

def load_latest_data(conn):
    latest_timestamp = get_latest_timestamp(conn)
    new_data_files = load_km_index('kissmetrics/index.csv', latest_timestamp)
    
    print "Processing %d data files..." % len(new_data_files)
    for data_file in new_data_files:
        process_data_file(conn, 'kissmetrics/' + data_file, latest_timestamp=latest_timestamp)
    print "\n\nDone."

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Parses sentences.")
    parser.add_argument('-d', '--database', help="database file", default='data.db')
    parser.add_argument('-t', '--table-name', help="events table name", default='events')
    args = parser.parse_args()
    
    connection = sqlite3.connect(args.database)
    
    create_table(connection)
    load_latest_data(connection)
