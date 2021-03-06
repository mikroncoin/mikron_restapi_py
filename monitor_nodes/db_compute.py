import sqlite3
import time
import datetime
import logging

logging.basicConfig(level=logging.INFO)

def get_logger():
    """ Get named logger
    """
    return logging.getLogger(__name__)

def get_db_name_nodecompute():
    return 'nodecompute_db.db'

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

def create_db_nodeperiod():
    c, conn = connect(get_db_name_nodecompute())
    c.execute('''CREATE TABLE nodeperiod
            (time_start long,
            time_end long,
            count_tot int,
            ip text,
            port text,
            count int,
            account text,
            avg_bal text
            )''')
    get_logger().info("DB table nodeperiod created")
    close(conn)

def upgrade_db_nodeperiod_2():
        c, conn = connect(get_db_name_nodecompute())
        c.execute('''ALTER TABLE nodeperiod ADD COLUMN net_version text''')
        get_logger().info("DB table nodeperiod upgraded")
        close(conn)

def create_db_nodedaily():
    c, conn = connect(get_db_name_nodecompute())
    c.execute('''CREATE TABLE nodedaily
            (time_start long,
            time_end long,
            ip text,
            port text,
            account text,
            count_pos int,
            count_neg int,
            count_nonempty int,
            avg_bal text,
            eligible int,
            deny_reason text,
            reward_elig text,
            reward_sent text,
            sent_hash text,
            sent_time text
            )''')
    get_logger().info("DB table nodedaily created")
    close(conn)

def upgrade_db_nodedaily_2():
        c, conn = connect(get_db_name_nodecompute())
        c.execute('''ALTER TABLE nodedaily ADD COLUMN net_version text''')
        get_logger().info("DB table nodedaily upgraded")
        close(conn)

def delete_period_filter_time(time_start):
    c, conn = connect(get_db_name_nodecompute())
    sql_command = "DELETE FROM nodeperiod WHERE time_start >= " + str(time_start) + ";"
    #print(sql_command)
    c.execute(sql_command)
    ret = c.fetchall()
    close(conn)
    return ret

def add_period_entry(time_start, time_end, count_tot, ip, port, count, account, avg_bal):
    #now = time.time()
    c, conn = connect(get_db_name_nodecompute())
    sql_command = "INSERT INTO nodeperiod VALUES ("+\
        str(time_start) + ", "+\
        str(time_end) + ", " +\
        str(count_tot) + ", '"+\
        str(ip) + "', '"+\
        str(port) + "', "+\
        str(count) + ", '"+\
        str(account) + "', "+\
        str(avg_bal) + ""+\
        ");"
    c.execute(sql_command)
    ret = c.fetchall()
    close(conn)
    #now2 = time.time()
    #print('add_period_entry', 0.1 * int(10000 * (now2 - now)), now, now2)
    return ret

def add_period_entries(entries):
    #now = time.time()
    results = []
    c, conn = connect(get_db_name_nodecompute())
    for e in entries:
        sql_command = "INSERT INTO nodeperiod VALUES ("+\
            str(e['time_start']) + ", "+\
            str(e['time_end']) + ", " +\
            str(e['count_tot']) + ", '"+\
            str(e['ip']) + "', '"+\
            str(e['port']) + "', "+\
            str(e['count']) + ", '"+\
            str(e['account']) + "', "+\
            str(e['avg_bal']) + ", '"+\
            str(e['net_version']) + "'"+\
            ");"
        c.execute(sql_command)
        ret = c.fetchall()
        results.append(ret)
    close(conn)
    #now2 = time.time()
    #print('add_period_entries', len(entries), 0.1 * int(10000 * (now2 - now)), 'ms', now, now2)
    return results

def get_all_period_sorted():
    c, conn = connect(get_db_name_nodecompute())
    sql_command = "SELECT * FROM nodeperiod ORDER BY time_start ASC, ip ASC;"
    c.execute(sql_command)
    ret = c.fetchall()
    close(conn)
    return ret

# Get the min and max of the observed period times
'''
def get_min_max_time_period():
    c, conn = connect(get_db_name_nodecompute())
    c.execute("SELECT MIN(time_start) AS min, MAX(time_start) AS max FROM nodeperiod;")
    ret = c.fetchall()
    close(conn)
    return ret
'''

# get period entries, filtered by a time range
def get_nodes_period_filter_time(start, end):
    c, conn = connect(get_db_name_nodecompute())
    sql_command = "SELECT * FROM nodeperiod WHERE time_start >= " + str(start) + " AND time_start < " + str(end) + ";"
    #print(sql_command)
    c.execute(sql_command)
    ret = c.fetchall()
    close(conn)
    #print(len(ret))
    return ret

def delete_daily_filter_time(time_start):
    c, conn = connect(get_db_name_nodecompute())
    # Do not delete nodes for which payment has already made!
    sql_command = "DELETE FROM nodedaily WHERE time_start >= " + str(time_start) + " AND reward_sent='';"
    #print(sql_command)
    c.execute(sql_command)
    ret = c.fetchall()
    close(conn)
    return ret

def get_all_daily_sorted_filter_time(time_start):
    c, conn = connect(get_db_name_nodecompute())
    sql_command = "SELECT * FROM nodedaily WHERE time_start >= " + str(time_start) + " ORDER BY time_start ASC, ip ASC;"
    c.execute(sql_command)
    ret = c.fetchall()
    close(conn)
    return ret

def get_all_daily_sorted_filter_time_rev(time_start):
    c, conn = connect(get_db_name_nodecompute())
    sql_command = "SELECT * FROM nodedaily WHERE time_start >= " + str(time_start) + " ORDER BY time_start DESC, ip ASC;"
    c.execute(sql_command)
    ret = c.fetchall()
    close(conn)
    return ret

def get_daily_sorted_filter_elig_time(time_start):
    c, conn = connect(get_db_name_nodecompute())
    sql_command = "SELECT * FROM nodedaily WHERE eligible > 0 AND time_start >= " + str(time_start) + " ORDER BY time_start ASC, ip ASC;"
    c.execute(sql_command)
    ret = c.fetchall()
    close(conn)
    return ret

def get_daily_filter_topay_time(time_start):
    c, conn = connect(get_db_name_nodecompute())
    sql_command = "SELECT * FROM nodedaily WHERE eligible > 0 AND reward_elig > 0 AND (reward_sent = '' OR reward_sent = '0') AND time_start >= " + str(time_start) + ";"
    c.execute(sql_command)
    ret = c.fetchall()
    close(conn)
    return ret

# Get the latest node for which a send was already made
def get_daily_latest_sent_time():
    c, conn = connect(get_db_name_nodecompute())
    sql_command = "SELECT MAX(time_start) AS max FROM nodedaily WHERE reward_sent != '' ;"
    c.execute(sql_command)
    ret = c.fetchall()
    close(conn)
    #print(ret)
    if len(ret) < 1:
        return 0
    if 'max' not in ret[0]:
        return 0
    if ret[0]['max'] is None:
        return 0
    return ret[0]['max']

def add_daily(time_start, time_end, ip, port, account, count_pos, count_neg, count_nonempty, avg_bal, net_version):
    c, conn = connect(get_db_name_nodecompute())
    sql_command = "INSERT INTO nodedaily VALUES ("+\
        str(time_start) + ", "+\
        str(time_end) + ", '" +\
        str(ip) + "', '"+\
        str(port) + "', '"+\
        str(account) + "', "+\
        str(count_pos) + ", "+\
        str(count_neg) + ", "+\
        str(count_nonempty) + ", '"+\
        str(avg_bal) + "'," +\
        "0, '?', '', '', " +\
        "'', '', '" +\
        str(net_version) + "'" +\
        ");"
    c.execute(sql_command)
    ret = c.fetchall()
    close(conn)
    return ret

def update_daily_eligible(time_start, ip, eligible, deny_reason, reward_elig):
    c, conn = connect(get_db_name_nodecompute())
    # do not modify nodes with already sent-out rewards
    sql_command = "UPDATE nodedaily SET " +\
        "eligible=" + str(eligible) + ", " +\
        "deny_reason='" + str(deny_reason) + "', " +\
        "reward_elig='" + str(reward_elig) + "', " +\
        "reward_sent='' WHERE " +\
        "time_start=" + str(time_start) +\
        " AND ip='" + str(ip) + "' AND " +\
        "reward_sent=''" +\
        ";"
    #print(sql_command)
    c.execute(sql_command)
    ret = c.fetchall()
    close(conn)
    return ret

def update_daily_sent(time_start, ip, reward_sent, sent_time, sent_hash):
    c, conn = connect(get_db_name_nodecompute())
    sql_command = "UPDATE nodedaily SET " +\
        "reward_sent='" + str(reward_sent) + "', " +\
        "sent_time='" + str(sent_time) + "', " +\
        "sent_hash='" + str(sent_hash) + "' WHERE " +\
        "time_start=" + str(time_start) +\
        " AND ip='" + str(ip) + "' AND " +\
        "reward_sent=''" +\
        ";"
    #print(sql_command)
    c.execute(sql_command)
    ret = c.fetchall()
    close(conn)
    return ret
