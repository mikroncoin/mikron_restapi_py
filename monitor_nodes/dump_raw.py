import db
import datetime
import sys

def dump_raw():
    nodes = db.get_all_nodes_unordered()
    print(str(len(nodes)) + " nodes")
    for n in nodes:
        ts = int(n['time_sec'])
        print(ts, n['ep_ip'], n['ep_account'], sep=', ')

dump_raw()