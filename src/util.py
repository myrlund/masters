import sys

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
