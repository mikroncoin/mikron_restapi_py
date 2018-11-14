import os
import db

def reinit_db():
    if os.path.exists(db.get_db_name()):
        os.remove(db.get_db_name())

    db.create_dbs()

def upgrade1():
    # remove columns time_day_ordinal and time_iso from table monitor, they are generated later during dump
    c, conn = db.connect()

    db.get_logger().info("Upgrading table monitor")
    c.execute('''ALTER TABLE monitor RENAME TO monitor_old;''')
    c.execute('''CREATE TABLE monitor (time_sec long, no_nodes int, no_blocks long, no_frontiers long);''')
    c.execute('''INSERT INTO monitor SELECT time_sec long, no_nodes int, no_blocks long, no_frontiers long FROM monitor_old ORDER BY time_sec ASC;''')
    c.execute('''DROP TABLE monitor_old;''')
    db.get_logger().info("Upgrade complete")

    db.close(conn)

### reinit_db()
### upgrade1()
