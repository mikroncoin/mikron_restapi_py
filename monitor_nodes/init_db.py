import os
import db

# Create table noderaw
def reinit_db():
    if os.path.exists(db.get_db_name_noderaw()):
        os.remove(db.get_db_name_noderaw())
    db.create_db_noderaw()

# Create table nodeperiod and nodedaily
def upgrade1():
    if os.path.exists(db.get_db_name_nodecompute()):
        os.remove(db.get_db_name_nodecompute())
    db.create_db_nodeperiod()
    db.create_db_nodedaily()

### reinit_db()
### upgrade1()
