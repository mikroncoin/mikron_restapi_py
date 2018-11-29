import config
import recv_db
import node_rpc_helper

import threading
from time import sleep, time

setup_check_background_result = {"msg": "(uninitialized)"}
config = config.readConfig()
last_check_time = time() - 100

def get_setup_check_background():
    global setup_check_background_result
    return setup_check_background_result

def setup_check_async():
    bg_thread = threading.Thread(target = setup_check_sync)
    bg_thread.start()    

def setup_check_sync():
    global setup_check_background_result
    global config
    global last_check_time
    now = time()
    age = now - last_check_time
    if (age < 300):
        setup_check_background_result["msg"] = "(status check skipped " + str(int(age)) + ")"
    else:
        setup_check_background_result["msg"] = "(status check scheduled)"
        sleep(5)
        last_check_time = now
        setup_check_background_result["msg"] = "(status check executing)"
        status = setup_check(config)
        #print("status", status)
        setup_check_background_result = status

# Check the receiver accounts; compare accounts in the node wallets and in the DB
def setup_check(config):
    print("Receiving accounts:")
    # in DB
    in_db = {}
    a_in_db = recv_db.get_all_accounts()
    for a in a_in_db:
        in_db[a["rec_acc"]] = {"pool": a["pool_account_id"]}
    print("- ", len(in_db), "in DB")
    #for a in in_db:
    #    print(a, in_db[a]["pool"])

    # in node wallets -- no RPC for wallet list, take from config
    wallets = {}
    for pool in config["receiver_service.account"]:
        pool_id = config["receiver_service.account"][pool]["id"]
        wallet = config["receiver_service.account"][pool]["walletid"]
        wallets[pool_id] = wallet
        #print(pool_id, wallet)
    in_node = {}
    for pool in wallets:
        wallet = wallets[pool]
        print(pool, wallet)
        wresp = node_rpc_helper.doAccountList(wallet)
        #print(wresp)
        if "error" in wresp:
            print("Error", wresp)
        else:
            if "accounts" in wresp:
                for a in wresp["accounts"]:
                    in_node[a] = {"pool": pool, "wallet": wallet}
    print("- ", len(in_node), "in node wallets")
    #for a in in_node:
    #    print(a, in_node[a]["pool"])

    # find those in DB only
    count_in_both = 0
    count_in_db_only = 0
    for a in in_db:
        if (a in in_node) and (in_db[a]["pool"] == in_node[a]["pool"]):
            # in both, OK
            count_in_both = count_in_both + 1
        else:
            # in DB, but not in node!
            print("Error: acc", a, in_db[a]["pool"], "is in DB but not in Node!")
            count_in_db_only = count_in_db_only + 1
    print("- ", count_in_both, "in both DB and Node")
    print("- ", count_in_db_only, "in DB only")
    # find those in Node wallets only
    count_in_node_only = 0
    for a in in_node:
        if a not in in_db:
            # in Node, but not in DB!
            print("Error: acc", a, in_node[a]["pool"], "is in Node but not in DB!")
            count_in_node_only = count_in_node_only + 1
    print("- ", count_in_node_only, "in Node only")
    status = {
        "in_db": len(in_db),
        "in_node": len(in_node),
        "in_both": count_in_both,
        "in_db_only": count_in_db_only,
        "in_node_only": count_in_node_only
    }
    print(status)
    return status

#config = config.readConfig()
#msg = setup_check(config)
#print("setup_check", msg)
