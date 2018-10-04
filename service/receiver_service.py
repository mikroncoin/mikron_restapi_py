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

@route('/receiver/create_account', method='OPTIONS')
def createAccountOptions():
    setHeaders()
    return "OK"

# Example: curl -d "{'pool_account_id': 'ReceiverPool', 'pool_account_password': 'some_password'}" http://localhost:8090/receiver/create_account
@route('/receiver/create_account', method='POST')
def createAccount():
    global config
    setHeaders()
    if config['receiver_service.enabled'] != 'true':
        return {"error": "service not enabled"}

    postdata = request.body.read().decode('utf8')
    #print("postdata ", postdata)
    postjson = json.loads(postdata.replace("'", '"'))
    #print("postjson ", postjson)

    pool_account_id = postjson["pool_account_id"]
    pool_account_password = postjson["pool_account_password"]

    if (pool_account_id not in config["receiver_service.account"]) or (pool_account_password != config["receiver_service.account"][pool_account_id]["password"]):
        return {"error": "source account not found or wrong password"}
    src_account = config["receiver_service.account"][pool_account_id]["account"]
    src_walletid = config["receiver_service.account"][pool_account_id]["walletid"]
    #print("walletid ", src_walletid)

    resp = node_rpc_helper.doCreateAccount(src_walletid)
    if 'error' in resp:
        return resp
    if 'account' not in resp:
        return {"error": "no account in response"}
    return {
        "account": resp['account']
    }

config = config.readConfig()
