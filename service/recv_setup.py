import config
import recv_db
import node_rpc_helper

# Check the receiver accounts; compare accounts in the node wallets and in the DB
def setup_check():
    global config
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
    ret_msg = \
        str(len(in_db)) + " in_db " +\
        str(len(in_node)) + " in_node " +\
        str(count_in_both) + " in_both " +\
        str(count_in_db_only) + " in_db_only " +\
        str(count_in_node_only) + " in_node_only"
    print(ret_msg)
    return ret_msg

config = config.readConfig()
setup_check()
