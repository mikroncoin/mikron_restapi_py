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

config = config.readConfig()
server = '?'
if 'rpc.baseurl' in config:
    server = config['rpc.baseurl']
rai = Rai()
