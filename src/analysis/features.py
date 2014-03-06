from collections import defaultdict

def clear_values(conn, feature_name):
    c = conn.cursor()
    c.execute('DELETE FROM user_models WHERE feature = %s', (feature_name,))
    conn.commit()

def insert_values(conn, feature_name, batch):
    """Parameter values should be tuples of (person, value) for feature called feature_name."""
    c = conn.cursor()
    for person, value in batch:
        c.execute('INSERT INTO user_models (feature, person, value) VALUES (%s, %s, %s)', (feature_name, person, value))
    conn.commit()

def get_values(conn, feature):
    c = conn.cursor()
    c.execute('SELECT value FROM user_models WHERE feature = %s', (feature,))
    return map(lambda x: x[0], c.fetchall())

def get_values(conn, feature):
    c = conn.cursor()
    c.execute('SELECT person, value FROM user_models WHERE feature = %s', (feature,))
    return c.fetchall()
