import sqlite3
import time
import datetime
import logging

logging.basicConfig(level=logging.INFO)

def get_logger():
    """ Get named logger
    """
    return logging.getLogger(__name__)

def get_db_name_noderaw():
    return 'noderaw_db.db'

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def connect(dbname):
    conn = sqlite3.connect(dbname)
    conn.row_factory = dict_factory
    return conn.cursor(), conn

def close(conn):
    conn.commit()
    conn.close()

def create_db_noderaw():
    c, conn = connect(get_db_name_noderaw())
    #        obs_srv text,      # observer service
    #        obs_firewall int,  # observer service behind firewall (1) or not (0)
    #        ip text,           # node endpoint IP
    #        port text,         # node endpoint port
    #        account text       # node ID account of the node
    #        balance text       # current balance of the node ID account (cached, within 1 hour)
    c.execute('''CREATE TABLE noderaw
            (time_sec long,
            obs_srv text,
            obs_firewall int,
            ip text,
            port text,
            account text,
            balance text
            )''')
    get_logger().info("DB table noderaw created")
    close(conn)

def save_node(time, obs_srv, obs_firewall, host, port, account, balance):
    c, conn = connect(get_db_name_noderaw())
    sql_command = "INSERT INTO noderaw VALUES ('"+\
        str(time) + "', '"+\
        str(obs_srv) + "', '" +\
        str(obs_firewall) + "', '"+\
        str(host) + "', '"+\
        str(port) + "', '"+\
        str(account) + "', '"+\
        str(balance) + "'"+\
        ");"
    #print(sql_command)
    c.execute(sql_command)

    #get_logger().info("node saved, time " + str(time) + ", host " + str(host))

    close(conn)

def get_all_nodes_unordered():
    c, conn = connect(get_db_name_noderaw())
    c.execute("SELECT * FROM noderaw;")
    ret = c.fetchall()
    close(conn)
    return ret