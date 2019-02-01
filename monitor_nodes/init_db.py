import os
import db_raw
import db_compute

# Create table noderaw
def reinit_db():
    if os.path.exists(db_raw.get_db_name_noderaw()):
        os.remove(db_raw.get_db_name_noderaw())
    db_raw.create_db_noderaw()

# Create table nodeperiod and nodedaily
def upgrade1():
    if os.path.exists(db_compute.get_db_name_nodecompute()):
        os.remove(db_compute.get_db_name_nodecompute())
    db_compute.create_db_nodeperiod()
    db_compute.create_db_nodedaily()

### reinit_db()
### upgrade1()
