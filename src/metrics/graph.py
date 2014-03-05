import sys

import numpy as np
import matplotlib.pyplot as plt

from util import batches

def get_all_persons(cursor):
    cursor.execute("""SELECT DISTINCT person FROM room_presences""")
    return map(lambda x: x[0], cursor.fetchall())

def count_for_person(cursor, person):
    cursor.execute("""SELECT if(person1 = %s, person1, person2) as person, count(*) from user_graph where person1 = %s or person2 = %s""", (person,) * 3)
    row = cursor.fetchone()
    if row is None or row[0] is None:
        return (person, 0)
    else:
        return row

def sum_for_person(cursor, person):
    cursor.execute("""SELECT if(person1 = %s, person1, person2) as person, sum(weight) from user_graph where person1 = %s or person2 = %s""", (person,) * 3)
    row = cursor.fetchone()
    if row is None or row[0] is None:
        return (person, 0)
    else:
        return row

def persons_mapped(cursor, fn, batch_size):
    # Get every distinct person in table
    all_persons = get_all_persons(cursor)
    
    # Count conversations for each one
    for persons in batches(all_persons, batch_size):
        batch_results = map(lambda p: fn(cursor, p), persons)
        yield batch_results

def conversation_partners_per_person(cursor, batch_size=500):
    return persons_mapped(cursor, count_for_person, batch_size=batch_size)

def conversations_per_person(cursor, batch_size=500):
    return persons_mapped(cursor, sum_for_person, batch_size=batch_size)

def analyze_conversation_partners(conn):
    c = conn.cursor()
    
    person_counts = conversation_partners_per_person(c, limit=500)
    
    # Grab raw numbers for analytics
    counts = map(lambda x: x[1], person_counts)
    print np.mean(counts)
    print np.std(counts)
    
    plt.hist(counts, bins=100, range=(5, 200))
    plt.show()
