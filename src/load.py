#!/usr/bin/env python

import json, sys, os
import MySQLdb as mysql

from util import connect_db

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
        'id INTEGER PRIMARY KEY AUTO_INCREMENT',
        'raw_event VARCHAR(250)',
        'timestamp INTEGER',
        'person VARCHAR(120)',
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
        sql = "INSERT INTO %s VALUES (%%s, %%s, %%s, %%s, %%s)" % RAW_TABLE
        for row in event_data:
            c.execute(sql, row)
        conn.commit()
    
    else:
        sys.stdout.write('o')
        sys.stdout.flush()

def load_latest_data(conn):
    data_path = os.path.join(CONFIG["data_root"], "kissmetrics")
    
    latest_timestamp = get_latest_timestamp(conn)
    new_data_files = load_km_index(os.path.join(data_path, 'index.csv'), latest_timestamp)
    
    print "Processing %d data files..." % len(new_data_files)
    for data_file in new_data_files:
        process_data_file(conn, os.path.join(data_path, data_file), latest_timestamp=latest_timestamp)
    print "\n\nDone."

if __name__ == '__main__':
    from util import load_config
    current_dir = os.path.dirname(os.path.abspath(__file__))
    CONFIG = load_config(os.path.join(current_dir, 'config.json'))
    
    import argparse
    parser = argparse.ArgumentParser(description="Parses sentences.")
    parser.add_argument('-t', '--table-name', help="events table name", default='events')
    args = parser.parse_args()
    
    connection = connect_db(mysql, CONFIG)
    
    create_table(connection)
    load_latest_data(connection)
