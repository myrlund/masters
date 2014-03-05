from collections import defaultdict

def bucket_discretely(field, l):
    l = map(lambda x: (x[field], x - (x[field],)), events)
    return reduce(lambda x, (k,v): x[k].append(v) or x, l, defaultdict(list))

# Feature support

def get_all_persons(c):
    c.execute('SELECT DISTINCT person FROM user_models')
    return c.fetchall()

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

def get_feature_values(conn, feature):
    c = conn.cursor()
    c.execute('SELECT value FROM user_models WHERE feature = %s', (feature,))
    return map(lambda x: x[0], c.fetchall())

def get_feature_values(conn, feature):
    c = conn.cursor()
    c.execute('SELECT person, value FROM user_models WHERE feature = %s', (feature,))
    return c.fetchall()
