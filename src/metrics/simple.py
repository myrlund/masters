import datetime

def rooms_claimed(c, **options):
    c.execute('SELECT person, COUNT(distinct roomname) AS count FROM events_ref WHERE event_type = \'room claimed\' GROUP BY person')
    rows = c.fetchall()
    return [rows]

def rooms_used(c, **options):
    c.execute('SELECT person, COUNT(distinct roomname) AS count FROM events_ref WHERE event_type = \'visited room\' GROUP BY person')
    rows = c.fetchall()
    return [rows]

def roomnames_generated(c, **options):
    c.execute('SELECT person, COUNT(*) AS count FROM events_ref WHERE event_verb = \'randomized new room name\' GROUP BY person')
    rows = c.fetchall()
    return [rows]

def frequency_last_month(c, **options):
    a_month_ago = ((datetime.datetime.now() - datetime.timedelta(weeks=4)) - datetime.datetime(1970, 1, 1)).total_seconds()
    c.execute('SELECT person, COUNT(*) AS count FROM events_ref WHERE event_type = \'in a conversation\' ' +
              'AND timestamp > %s GROUP BY person', (a_month_ago,))
    rows = c.fetchall()
    return [rows]

def chat_message_sent(c, **options):
    c.execute('SELECT person, COUNT(*) FROM events_ref WHERE event_type = \'room\' AND event_verb = \'message sent\' GROUP BY person')
    rows = c.fetchall()
    return [rows]
