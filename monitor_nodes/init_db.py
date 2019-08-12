import os
import db_raw
import db_compute

# Create table noderaw
def reinit_db():
    # raw DB files are created automatically
    print("raw DB files will be created automatically")

# Create table nodeperiod and nodedaily
def upgrade1():
    if os.path.exists(db_compute.get_db_name_nodecompute()):
        os.remove(db_compute.get_db_name_nodecompute())
    db_compute.create_db_nodeperiod()
    db_compute.create_db_nodedaily()

# Update tables nodeperiod and nodedaily with column net_version
def upgrade2():
    db_compute.upgrade_db_nodeperiod_2()
    db_compute.upgrade_db_nodedaily_2()

### reinit_db()
### upgrade1()
### upgrade2()
