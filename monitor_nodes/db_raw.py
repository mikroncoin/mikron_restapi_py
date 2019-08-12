import sqlite3
import time
import datetime
import logging

logging.basicConfig(level=logging.INFO)

def get_logger():
    """ Get named logger
    """
    return logging.getLogger(__name__)

def __db_name_default():
    return 'noderaw_db.db'

def __db_name_suffix_from_time(time):
    return int(time / 86400)

def __db_name_suffixes_from_times(time_from, time_to):
    idx1 = int(time_from / 86400)
    idx2 = int(time_to / 86400)
    suffixes = [idx1]
    if idx2 > idx1:
        for i in range(0, idx2 - idx1):
            suffixes.append(idx1 + i + 1)
    return suffixes

def __db_name_with_suffix(suffix):
    return 'noderaw_db_' + str(suffix) + '.db'

def __get_db_name_time(time):
    # No need for transition any more...  17932 Feb 5 Tue, 17932 * 86400 = 1549324800
    #if time < 1549324800:
    #    return __db_name_default()
    return __db_name_with_suffix(__db_name_suffix_from_time(time))

# returns the list of db names for the given time range (both inclusive), plus a default
def __get_db_names_from_times(time_from, time_to):
    suffixes = __db_name_suffixes_from_times(time_from, time_to)
    names = []
    for s in suffixes:
        names.append(__db_name_with_suffix(s))
    defname = __db_name_default()
    return (names, defname)

# TODO del
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

def create_db_noderaw_dbname(dbname):
    c, conn = connect(dbname)
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
            balance text,
            net_version text
            )''')
    get_logger().info("DB table noderaw created, " + dbname)
    close(conn)

def save_node1(dbname, time, obs_srv, obs_firewall, host, port, account, balance, net_version):
    c, conn = connect(dbname)
    sql_command = "INSERT INTO noderaw VALUES ('"+\
        str(time) + "', '"+\
        str(obs_srv) + "', '" +\
        str(obs_firewall) + "', '"+\
        str(host) + "', '"+\
        str(port) + "', '"+\
        str(account) + "', '"+\
        str(balance) + "', '"+\
        str(net_version) + "'"+\
        ");"
    #print(sql_command)
    c.execute(sql_command)

    #get_logger().info("node saved, time " + str(time) + ", host " + str(host))

    close(conn)

def save_node(time, obs_srv, obs_firewall, host, port, account, balance, net_version):
    dbname = __get_db_name_time(time)
    try:
        save_node1(dbname, time, obs_srv, obs_firewall, host, port, account, balance, net_version)
    except Exception as e:
        # try creating table
        try:
            get_logger().error("Could not save nodes, maybe table does not exits, DB: " + str(dbname) + " e: " + str(e))
            create_db_noderaw_dbname(dbname)
            save_node1(dbname, time, obs_srv, obs_firewall, host, port, account, balance, net_version)
        except Exception as e2:
            get_logger().error("Could not save node to DB " + str(dbname) + " e: " + str(e2))

def get_all_nodes_unordered(time_start_rel_day):
    now = int(time.time())
    return get_nodes_filter_time(now - time_start_rel_day * 86400, now + 2 * 86400)

# without time range, should not be used
def get_all_nodes_unordered_all():
    now = int(time.time())
    return get_nodes_filter_time(now - 60 * 86400, now + 2 * 86400)

# Get the min and max of the observed times
'''
def get_min_max_time_raw():
    #now = time.time()
    c, conn = connect(get_db_name_noderaw())
    c.execute("SELECT MIN(time_sec) AS min, MAX(time_sec) AS max FROM noderaw;")
    ret = c.fetchall()
    close(conn)
    #now2 = time.time()
    #print('get_min_max_time_raw', 0.1 * int(10000 * (now2 - now)), now, now2)
    return ret
'''

def get_nodes_filter_time1(dbname, start, end):
    #now = time.time()
    c, conn = connect(dbname)
    c.execute("SELECT * FROM noderaw WHERE time_sec >= " + str(start) + " AND time_sec < " + str(end) + ";")
    ret = c.fetchall()
    close(conn)
    #now2 = time.time()
    #print('get_nodes_filter_time1', dbname, end - start, 0.1 * int(10000 * (now2 - now)), 'ms', now, now2)
    return ret

# get entries, filtered by a time range
def get_nodes_filter_time(start, end):
    #now = time.time()
    dbnames, defaultdbname = __get_db_names_from_times(start, end)
    #print("DB2", defaultdbname, dbnames)
    ret = []
    we_tried_default = False
    for db1 in dbnames:
        try:
            ret1 = get_nodes_filter_time1(db1, start, end)
            for r in ret1:
                ret.append(r)
        except Exception as e:
            get_logger().error("Error in sub-query, db1 " + str(db1) + ", ignoring, " + str(e))
            if not we_tried_default:
                we_tried_default = True
                get_logger().info("Trying default DB, " + str(defaultdbname))
                try:
                    ret1 = get_nodes_filter_time1(defaultdbname, start, end)
                    for r in ret1:
                        ret.append(r)
                except Exception as e:
                    get_logger().error("Error in default sub-query, " + str(defaultdbname) + ", ignoring, " + str(e))
    #now2 = time.time()
    #print('get_nodes_filter_time', end - start, 0.1 * int(10000 * (now2 - now)), 'ms', now, now2)
    return ret

# get entries aggregate, for a time range.  Doesn't work
'''
def get_nodes_aggregate_time(start, end):
    c, conn = connect(get_db_name_noderaw())
    #c.execute("SELECT ip, COUNT(1) AS count FROM noderaw GROUP BY ip;")
    c.execute("SELECT ip, COUNT(1) AS count FROM noderaw WHERE time_sec >= " + str(start) + " AND time_sec < " + str(end) + " GROUP BY ip;")
    ret = c.fetchall()
    close(conn)
    return ret
'''
