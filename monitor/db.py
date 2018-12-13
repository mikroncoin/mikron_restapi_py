import sqlite3
import time
import datetime
import logging

logging.basicConfig(level=logging.INFO)

def get_logger():
    """ Get named logger
    """
    return logging.getLogger(__name__)

def get_db_name_monitor():
    return 'monitor_db.db'

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

def create_db_monitor():
    c, conn = connect(get_db_name_monitor())
    c.execute('''CREATE TABLE monitor
            (time_sec long,
            no_nodes int,
            no_blocks long,
            no_frontiers long)''')
    get_logger().info("DB table monitor created")
    close(conn)

def add_line(timestamp, no_nodes, no_blocks, no_frontiers):
    c, conn = connect(get_db_name_monitor())
    sql_command = "INSERT INTO monitor VALUES ('"+\
        str(timestamp) + "', '"+\
        str(no_nodes) + "', '" +\
        str(no_blocks) + "', '"+\
        str(no_frontiers) + "'"+\
        ");"
    c.execute(sql_command)

    get_logger().info("new line added, time " + str(timestamp) + ", nodes " + str(no_nodes) + ", blocks " + str(no_blocks))

    close(conn)

def get_all_lines_unordered():
    c, conn = connect(get_db_name_monitor())
    c.execute("SELECT * FROM monitor;")
    ret = c.fetchall()
    close(conn)
    return ret

def get_all_lines_ordered():
    c, conn = connect(get_db_name_monitor())
    c.execute("SELECT * FROM monitor ORDER BY time_sec ASC;")
    ret = c.fetchall()
    close(conn)
    return ret
