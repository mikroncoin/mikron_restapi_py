import os
import db

def reinit_db():
    if os.path.exists(db.get_db_name_noderaw()):
        os.remove(db.get_db_name_noderaw())

    db.create_db_noderaw()

### reinit_db()
