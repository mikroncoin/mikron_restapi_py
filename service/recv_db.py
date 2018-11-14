import sqlite3
import time
import datetime
import logging

logging.basicConfig(level=logging.INFO)

def get_logger():
    """ Get named logger """
    return logging.getLogger(__name__)

def get_db_name():
    return 'recv_db.db'

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

    c.execute('''CREATE TABLE rec_account (
            rec_acc text,
            pool_account_id text,
            user_data text,
            create_wallet_id text,
            created_time int,
            status text,
            updated_time int
            )''')
    get_logger().info("DB table rec_account created")

    close(conn)

def add_new_rec_account(rec_acc, pool_account_id, user_data, wallet_id):
    c, conn = connect()
    now = str(int(time.time()))
    c.execute("INSERT INTO rec_account VALUES ('" + 
        str(rec_acc) + "', '" +
        str(pool_account_id) + "', '" +
        str(user_data) + "', '" +
        str(wallet_id) + "', '" +
        now + "', 'ACTIVE', '" +
        now + "');")
    get_logger().info("Inserted into table rec_account, " + str(rec_acc))

    close(conn)

def get_all_accounts():
    c, conn = connect()
    c.execute("SELECT * FROM rec_account;")
    ret = c.fetchall()
    close(conn)
    return ret

#def list_all_accounts():
#    accounts = get_all_accounts()
#    for a in accounts:
#        print(a['rec_acc'], a['created_time'], a['pool_account_id'], a['status'])

# list_all_accounts()
