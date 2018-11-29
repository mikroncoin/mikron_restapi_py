import config
import account_helper
import node_rpc_helper

import os
import json
from bottle import post, request, response, get, route, static_file
from threading import Thread

def setHeaders():
    response.content_type = 'application/json'
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

@route('/treasury/send', method='OPTIONS')
def sendOptions():
    setHeaders()
    return "OK"

# Example: curl -d "{'pool_account_id': 'FaucetPool', 'pool_account_password': 'some_password', 'dest_account': 'mik_1naij1wkner3gb6j4o1tsf4me3zz8q9t1km9wnm5qzmnycfa44t8tkbq4srs', 'amount': '1', 'unique_id': '1234500017'}" http://localhost:8090/treasury/send
@route('/treasury/send', method='POST')
def send():
    global config
    setHeaders()
    if config['treasury_service.enabled'] != 'true':
        return {"error": "service not enabled"}

    postdata = request.body.read().decode('utf8')
    #print("postdata ", postdata)
    postjson = json.loads(postdata.replace("'", '"'))
    #print("postjson ", postjson)

    pool_account_id = postjson["pool_account_id"]
    pool_account_password = postjson["pool_account_password"]
    dest_account = postjson["dest_account"]
    amount = postjson["amount"]
    unique_id = postjson["unique_id"]

    #print("dest_account ", dest_account, " amount ", amount, " id ", unique_id)
    if (pool_account_id not in config["treasury_service.account"]) or (pool_account_password != config["treasury_service.account"][pool_account_id]["password"]):
        return {"error": "source account not found or wrong password"}
    src_account = config["treasury_service.account"][pool_account_id]["account"]
    src_walletid = config["treasury_service.account"][pool_account_id]["walletid"]
    #print("src_account ", src_account, " walletid ", src_walletid)

    max_amount = min(500000, float(config["treasury_service.max_amount"]))
    min_amount = max(0.000000001, float(config["treasury_service.min_amount"]))
    resp = sendIntern(src_account, src_walletid, dest_account, amount, unique_id, max_amount, min_amount)
    #print("resp ", resp)
    return resp

def sendIntern(src_account, src_walletid, dest_account, amount, unique_id, max_amount, min_amount):
    amountFloat = 0
    try:
        amountFloat = float(amount)
    except:
        return {"error": "Invalid amount"}
    if (amountFloat > max_amount):
        return {"error": "Amount too high (max " + str(max_amount) + ")"}
    if (amountFloat < min_amount):
        return {"error": "Amount too small (min " + str(min_amount) + ")"}
    # debug: retrieve balance
    src_orig_balance = node_rpc_helper.getAccountBalance(src_account)
    print("sendIntern: orig src balance", src_orig_balance)

    resp = node_rpc_helper.doSend(src_walletid, src_account, dest_account, amount, unique_id)
    print("sendIntern: send complete, amount ", amount, "dest", dest_account)
    if 'error' in resp:
        return resp
    if 'block' not in resp:
        return {"error": "no block in response"}
    return {
        "id": unique_id, 
        "amount": amount,
        "block_hash": resp['block']
    }

config = config.readConfig()
