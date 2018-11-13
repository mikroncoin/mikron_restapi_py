import sqlite3
import time
import logging

logging.basicConfig(level=logging.INFO)

def get_logger():
    """ Get named logger
    """
    return logging.getLogger(__name__)

def get_db_name():
    return 'monitor_db.db'

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def connect():
    conn = sqlite3.connect(get_db_name())
    conn.row_factory = dict_factory
    return conn.cursor(), conn

def close(conn):
    conn.commit()
    conn.close()

def create_dbs():
    c, conn = connect()

    c.execute('''CREATE TABLE monitor
            (timestamp long,
            no_nodes int,
            no_blocks long,
            no_frontiers long)''')

    get_logger().info("DB table monitor created")

    close(conn)

def add_line(timestamp, no_nodes, no_blocks, no_frontiers):
    c, conn = connect()
    sql_command = "INSERT INTO monitor VALUES ('"+\
        str(timestamp)+ "', '"+\
        str(no_nodes) + "', '" +\
        str(no_blocks) + "', '"+\
        str(no_frontiers) + "'"+\
        ");"
    c.execute(sql_command)

    get_logger().info("new line added, time " + str(timestamp) + ", nodes " + str(no_nodes) + ", blocks " + str(no_blocks))

    close(conn)

def get_all_lines():
    c, conn = connect()

    c.execute("SELECT * FROM monitor ORDER BY timestamp ASC")
    ret = c.fetchall()
    close(conn)

    return ret
