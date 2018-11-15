import os
import recv_db

def reinit_db():
    if os.path.exists(recv_db.get_db_name()):
        os.remove(recv_db.get_db_name())

    recv_db.create_dbs()

### reinit_db()
### recv_db.upgrade1()
