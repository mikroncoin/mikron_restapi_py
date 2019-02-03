import os
import db_raw
import db_compute

# Create table noderaw
def reinit_db():
    # raw DB files are created automatically

# Create table nodeperiod and nodedaily
def upgrade1():
    if os.path.exists(db_compute.get_db_name_nodecompute()):
        os.remove(db_compute.get_db_name_nodecompute())
    db_compute.create_db_nodeperiod()
    db_compute.create_db_nodedaily()

### reinit_db()
### upgrade1()
