import os, sys, subprocess

# Feature-related

def get_all_persons(c, feature=None):
    sql = 'SELECT DISTINCT person FROM user_models'
    params = []
    if feature is not None:
        sql += ' WHERE feature = %s'
        params.append(feature)

    c.execute(sql, params)
    return [vec[0] for vec in c.fetchall()]

def get_feature_values(c, feature):
    sql = 'SELECT value FROM user_models WHERE feature = %s'
    c.execute(sql, (feature,))
    return map(lambda vec: vec[0], c.fetchall())

def clear_feature_values(conn, feature_name):
    c = conn.cursor()
    c.execute('DELETE FROM user_models WHERE feature = %s', (feature_name,))
    conn.commit()

def insert_feature_values(conn, feature_name, values):
    """Parameter values should be tuples of (person, value) for feature called feature_name."""
    c = conn.cursor()
    for row in values:
        if row[0] is None:
            print row
        c.execute('INSERT INTO user_models (feature, person, value) VALUES (%s, %s, %s)', (feature_name,) + row)
    conn.commit()

# Handy iterator stuff

def batches(l, n):
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

def bucket_discretely(field, l):
    l = map(lambda x: (x[field], x - (x[field],)), events)
    return reduce(lambda x, (k,v): x[k].append(v) or x, l, defaultdict(list))

# Config and project setup

def load_config(rel_fname='config.json'):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    fname = os.path.join(current_dir, rel_fname)

    import json
    f = open(fname, 'r')
    try:
        return json.load(f)
    except IOError:
        sys.exit(1)
    finally:
        f.close()
    return None

def run_update(config):
    cmd = config.get('data_update_cmd', None)
    if cmd:
        result = subprocess.check_call(cmd)
        return result == 0
    else:
        print "No command described in config (data_update_cmd)."
        return False

def connect_db(config):
    import MySQLdb as dbclass
    conf = config.get(dbclass.__name__, {})
    return dbclass.connect(**conf)
