import config
import account_helper

import json
import requests
from time import sleep

class Rai:
    def __getattr__(self, name, *args):
        def function (*args):
            global server
            if server:
                request = {}
                request["action"] = name
                if args:
                    for key, value in args[0].items():
                        request[key] = value
                try:
                    r = requests.post(server, data = json.dumps(request)).json()

                    if "error" not in r:
                        return r
                    else:
                        print(r["error"])
                        return r
                except:
                    try:
                        sleep(0.5)
                        r = requests.post(server, data = json.dumps(request)).json()

                        if "error" not in r:
                            return r
                        else:
                            print(r["error"])
                            return r
                    except:
                        return {"error": "RPC connection error"}

            else:
                print("Wrong server configuration.")

        return function

def getBlockCount():
    global rai
    resp = 'ERROR'
    try:
        resp = rai.block_count({})
        if 'error' in resp:
            return resp['error']
        if 'count' not in resp:
            return 'ERROR'
    except:
        return 'ERROR'
    return resp['count']

def getBlockCountUnchecked():
    global rai
    resp = 'ERROR'
    try:
        resp = rai.block_count({})
        if 'error' in resp:
            return resp['error']
        if 'unchecked' not in resp:
            return 'ERROR'
    except:
        return 'ERROR'
    return resp['unchecked']

def getFrontierCount():
    global rai
    resp = 'ERROR'
    try:
        resp = rai.frontier_count({})
        if 'error' in resp:
            return resp['error']
        if 'count' not in resp:
            return 'ERROR'
    except:
        return 'ERROR'
    return resp['count']

def getAccountBalance(accId):
    global rai
    try:	
        #print("getAccountBalance ", accId)
        balance = rai.account_balance({"account": accId})
    except:
        return "ERROR: could not retrieve"
    try:
        if balance is None:
            return 'ERROR'
        if 'error' in balance:
            return 'ERROR: ' + balance['error']
        if 'balance' not in balance:
            return 'ERROR'
    except:
        return "ERROR"
    # Unit conversion
    balMik = account_helper.fromRawToMikron(balance['balance'])
    return balMik

def getAccountHistory(accId, count, offset = 0):
    global rai
    try:
        params = {"account": accId, "count": count}
        if offset > 0:
            params["offset"] = offset
        history = rai.account_history(params)
        #print(history)
    except:
        return {"error": "exception"}
    try:
        if history is None:
            return {"error": "empty response"}
        if 'error' in history:
            return {"error": history['error']}
        if 'history' not in history:
            return {"error": "Missing history"}
    except:
        return {"error": "error"}
    #print(history['history'])
    # Unit conversions
    for h in history['history']:
        #print(h)
        if 'amount' in h:
            amntMik = account_helper.fromRawToMikron(h['amount'])
            #print(h['amount'], amntMik)
            h['amount'] = amntMik
        if 'balance' in h:
            balMik = account_helper.fromRawToMikron(h['balance'])
            h['balance'] = balMik
    return history

def getBlock(block_hash):
    global rai
    try:	
        #print("getBlock ", block_hash)
        block = rai.block({"hash": block_hash})
    except:
        return {"error": "exception"}
    try:
        if block is None:
            return {"error": "empty response"}
        if 'error' in block:
            return {"error": block['error']}
        if 'contents' not in block:
            return {"error": "Missing contents"}
    except:
        return {"error": "error"}
    # Unit conversions
    bc = json.loads(block['contents'])
    if 'balance' in bc:
        balMik = account_helper.fromRawToMikron(bc['balance'])
        bc['balance'] = balMik
    return bc

def getBlockInfo(block_hash):
    blocks = getBlockInfos([block_hash])
    # take out this block
    if 'blocks' in blocks:
        if block_hash in blocks['blocks']:
            return blocks['blocks'][block_hash]
    # fallback
    return blocks

# Get extended block info, for multiple blocks
def getBlockInfos(block_hash_array):
    global rai
    try:	
        #print("getBlockInfos ", block_hash_array)
        blocks = rai.blocks_info({"hashes": block_hash_array})
        #print(blocks)
    except:
        return {"error": "exception"}
    try:
        if blocks is None:
            return {"error": "empty response"}
        if 'error' in blocks:
            return {"error": blocks['error']}
        if 'blocks' not in blocks:
            return {"error": "Missing blocks"}
    except:
        return {"error": "error"}
    # Unit conversions
    for block_hash in blocks['blocks']:
        block = blocks['blocks'][block_hash]
        amountMik = 0
        if 'amount' in block:
            amountMik = account_helper.fromRawToMikron(block['amount'])
            block['amount'] = amountMik
        if 'contents' in block:
            cont_str = block['contents']
            cont = json.loads(cont_str)
            if 'balance' in cont:
                balMik = account_helper.fromRawToMikron(cont['balance'])
                cont['balance'] = balMik
            if 'creation_time' in cont:
                cont['creation_time'] = 1535760000 + int(cont['creation_time'])
            # copy over the amount and amount_sign to the contents
            if 'amount' in block:
                cont['amount'] = amountMik
            if 'amount_sign' in block:
                cont['amount_sign'] = block['amount_sign']
            # replace string contents with Json
            block['contents'] = ''
            block['contents'] = cont
    return blocks

def getPeers():
    global rai
    try:
        peers = rai.peers()
        #print(peers)
        if peers is None:
            return 'ERROR'
        if 'error' in peers:
            return 'ERROR: ' + peers['error']
        if 'peers' not in peers:
            return 'ERROR'
    except:
        return 'ERROR'
    return peers['peers']

def getFrontiers(count):
    global rai
    try:
        count = min(50, int(count))
        frontiers = rai.frontiers({"account": "mik_1111111111111111111111111111111111111111111111111111hifc8npp", "count": count})
        #print(frontiers)
        if frontiers is None:
            return 'ERROR'
        if 'error' in frontiers:
            return 'ERROR: ' + frontiers['error']
        if 'frontiers' not in frontiers:
            return 'ERROR'
    except:
        return 'ERROR'
    return frontiers['frontiers']

# Top accounts by balance
def getAccountsTop(count):
    global rai
    try:
        count = min(50, int(count))
        ledger = rai.ledger({
            "sorting": "true",
            "count": count
        })
        #print(ledger)
        if ledger is None:
            return 'ERROR'
        if 'error' in ledger:
            return 'ERROR: ' + ledger['error']
        if 'accounts' not in ledger:
            return 'ERROR'
    except:
        return 'ERROR'
    # Unit conversions
    for acc in ledger['accounts']:
        if 'balance' in ledger['accounts'][acc]:
            balMik = account_helper.fromRawToMikron(ledger['accounts'][acc]['balance'])
            ledger['accounts'][acc]['balance'] = balMik
    return ledger['accounts']

# Accounts with most recent transactions
def getAccountsRecent(count):
    global rai
    try:
        count = min(50, int(count))
        # get accounts with most recent transactions
        ledger = rai.ledger({
            "sorting_by_time": "true",
            "count": count
        })
        #print('ledger', ledger)
        if ledger is None:
            return 'ERROR'
        if 'error' in ledger:
            return 'ERROR: ' + ledger['error']
        if 'accounts' not in ledger:
            return 'ERROR'
        #print(ledger['accounts'])
        # take out frontier hashes
        hashes = []
        for acc in ledger['accounts']:
            #print(acc)
            if 'frontier' in ledger['accounts'][acc]:
                hashes.append(ledger['accounts'][acc]['frontier'])
        #print(hashes)
        block_infos = {}
        if len(hashes) > 0:
            block_infos_raw = getBlockInfos(hashes)
            #print(block_infos_raw)
            if 'blocks' in block_infos_raw:
                block_infos = block_infos_raw['blocks']
        #print(block_infos)
        return block_infos
    except:
        return 'ERROR'
    return 'ERROR'

def doSend(src_walletid, src_account, dest_account, amount, unique_id):
    global rai
    try:
        #print("amount", amount)
        amount_raw = account_helper.fromMikronToRaw(amount)
        #print(amount_raw)
        send_params = {"wallet": src_walletid, "source": src_account, "destination": dest_account, "amount": amount_raw, "id": unique_id}
        #print("send_params", send_params)
        resp = rai.send(send_params)
        #print(resp)
        return resp
    except:
        return {"error": "exception"}

def doCreateAccount(src_walletid):
    global rai
    try:
        send_params = {"wallet": src_walletid}
        #print("send_params", send_params)
        resp = rai.account_create(send_params)
        #print(resp)
        return resp
    except:
        return {"error": "exception"}

def doAccountList(wallet_id):
    global rai
    try:
        send_params = {"wallet": wallet_id}
        #print("send_params", send_params)
        resp = rai.account_list(send_params)
        #print(resp)
        return resp
    except:
        return {"error": "exception"}

config = config.readConfig()
server = '?'
if 'rpc.baseurl' in config:
    server = config['rpc.baseurl']
rai = Rai()
