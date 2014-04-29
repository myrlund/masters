import datetime

def simple_query(c, sql, *args, **options):
    if 'timespan' in options and all(options['timespan']):
        sql  += " AND timestamp >= %s AND timestamp < %s"
        args += options['timespan']

    c.execute(sql, args)
    result = c.fetchone()[0]
    return result

def rooms_claimed(person, cursor, **options):
    return simple_query(cursor, 'SELECT COUNT(distinct roomname) FROM events_ref WHERE event_type = \'room claimed\' AND person = %s', person, **options)

def rooms_followed(person, cursor, **options):
    return simple_query(cursor, 'SELECT COUNT(*) FROM events_ref WHERE event_type = \'follow room\' AND person = %s', person, **options)

def rooms_used(person, cursor, **options):
    return simple_query(cursor, 'SELECT COUNT(distinct roomname) FROM events_ref WHERE event_type = \'visited room\' AND person = %s', person, **options)

def roomnames_generated(person, cursor, **options):
    return simple_query(cursor, 'SELECT COUNT(*) FROM events_ref WHERE event_verb = \'randomized new room name\' AND person = %s', person, **options)

# def frequency_last_month(person, cursor, **options):
#     a_month_ago = ((datetime.datetime.now() - datetime.timedelta(weeks=4)) - datetime.datetime(1970, 1, 1)).total_seconds()
#     return simple_query(cursor, 'SELECT COUNT(*) FROM events_ref WHERE event_type = \'in a conversation\' AND timestamp > %s AND person = %s', (a_month_ago, person), **options)

def chat_message_sent(person, cursor, **options):
    return simple_query(cursor, 'SELECT COUNT(*) FROM events_ref WHERE event_type = \'room\' AND event_verb = \'message sent\' AND person = %s', person, **options)

def invitee(person, cursor, **options):
    return simple_query(cursor, 'SELECT COUNT(*) FROM events_ref WHERE event_type = \'entered existing room\' AND person = %s', person, **options)

def inviter(person, cursor, **options):
    return simple_query(cursor, 'SELECT COUNT(*) FROM events_ref WHERE event_type = \'entered new room\' AND person = %s', person, **options)
