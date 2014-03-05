from util import load_config, connect_db

from metrics import graphs

if __name__ == '__main__':
    config = load_config()
    conn = connect_db(config)
    
    graphs.average_distinct_partners(conn)
