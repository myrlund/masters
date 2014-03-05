import os, sys, subprocess

def batches(l, n):
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

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
