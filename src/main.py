import os, sys, glob

from util import load_config

def main():
    data_root = CONFIG['data_root']
    kissmetrics_revisions_dir = os.path.join(data_root, 'kissmetrics', 'revisions')
    revision_paths = glob.glob(os.path.join(kissmetrics_revisions_dir, "*"))
    revision_names = map(lambda path: os.path.join('revisions', os.path.basename(path)), revision_paths)
    print revision_names

if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.abspath(__file__))

    import argparse
    parser = argparse.ArgumentParser(description="Processes log data for appear.in.")
    parser.add_argument('-c', '--config', help="location of config file", default = current_dir + '/config.json')
    parser.add_argument('-d', '--debug', action='store_true', help="print debug information")

    args = parser.parse_args()

    DEBUG = args.debug
    CONFIG = load_config(args.config)

    main()
