import os, sys, subprocess

def load_config(fname):
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

def connect_db(dbclass, config):
    conf = config.get(dbclass.__name__, {})
    return dbclass.connect(**conf)
