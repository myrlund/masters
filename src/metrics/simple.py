import datetime

def simple_query(c, *sql):
    c.execute(*sql)
    return c.fetchone()[0]

def rooms_claimed(person, cursor):
    return simple_query(cursor, 'SELECT COUNT(distinct roomname) FROM events_ref WHERE event_type = \'room claimed\' AND person = %s', person)

def rooms_used(person, cursor):
    return simple_query(cursor, 'SELECT COUNT(distinct roomname) FROM events_ref WHERE event_type = \'visited room\' AND person = %s', person)

def roomnames_generated(person, cursor):
    return simple_query(cursor, 'SELECT COUNT(*) FROM events_ref WHERE event_verb = \'randomized new room name\' AND person = %s', person)

def frequency_last_month(person, cursor):
    a_month_ago = ((datetime.datetime.now() - datetime.timedelta(weeks=4)) - datetime.datetime(1970, 1, 1)).total_seconds()
    return simple_query(cursor, 'SELECT COUNT(*) FROM events_ref WHERE event_type = \'in a conversation\' AND timestamp > %s AND person = %s', (a_month_ago, person))

def chat_message_sent(person, cursor):
    return simple_query(cursor, 'SELECT COUNT(*) FROM events_ref WHERE event_type = \'room\' AND event_verb = \'message sent\' AND person = %s', person)
