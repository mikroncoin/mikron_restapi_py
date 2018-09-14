import config

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

server = 'http://localhost:54300'
rai = Rai()

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
        if balance is None:
            return 'ERROR'
        if 'error' in resp:
            return 'ERROR: ' + resp['error']
        if 'balance' not in balance:
            return 'ERROR'
    except:
        return "ERROR"
    return balance['balance']
