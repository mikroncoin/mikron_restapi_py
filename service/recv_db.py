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
            create_root_acc text,
            acc_idx int,
            create_wallet_id text,
            created_time int,
            status text,
            updated_time int
            )''')
    get_logger().info("DB table rec_account created")

    close(conn)

def upgrade1():
    # add columns create_root_acc, acc_idx.  Copy the table for proper column order
    c, conn = connect()
    get_logger().info("Upgrading table rec_account")
    c.execute("ALTER TABLE rec_account RENAME TO rec_account_old;")
    c.execute("CREATE TABLE rec_account (rec_acc text, pool_account_id text, user_data text, create_root_acc text, acc_idx int, create_wallet_id text, created_time int, status text, updated_time int);")
    c.execute("INSERT INTO rec_account SELECT rec_acc, pool_account_id, user_data, '', -1, create_wallet_id, created_time, status, updated_time FROM rec_account_old ORDER BY created_time ASC;")
    c.execute("DROP TABLE rec_account_old;")
    get_logger().info("Upgrade complete")
    close(conn)

def add_new_rec_account(rec_acc, pool_account_id, user_data, root_acc, acc_idx, wallet_id):
    c, conn = connect()
    now = str(int(time.time()))
    c.execute("INSERT INTO rec_account VALUES ('" + 
        str(rec_acc) + "', '" +
        str(pool_account_id) + "', '" +
        str(user_data) + "', '" +
        str(root_acc) + "', '" +
        str(acc_idx) + "', '" +
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
