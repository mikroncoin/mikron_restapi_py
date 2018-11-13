import os
import db

def reinit_db():
    if os.path.exists(db.get_db_name()):
        os.remove(db.get_db_name())

    db.create_dbs()

### reinit_db()