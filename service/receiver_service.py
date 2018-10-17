import config
import account_helper
import node_rpc_helper

import os
import json
from bottle import post, request, response, get, route, static_file
from threading import Thread
import requests

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

# Invoked by the node, RPC callback
@route('/rpccallback', method='POST')
def rpcCallback():
    global config
    postdata = request.body.read().decode('utf8')
    #print("postdata ", postdata)
    postjson = json.loads(postdata.replace("'", '"'))
    #print("postjson ", postjson)
    if 'account' not in postjson:
        return
    account = postjson['account']
    print("RPC callback", "account", account)

    # TODO: filter out if account is among to be watched!!!

    webhook = config['receiver_service.account']['ReceiverPool']['receiver_webhook']
    #print(webhook)
    invokeWebhook (webhook, account)
    return "ok"

# Call into the hook of a partner site, URL of the form 'https://mikron.io/webhook/{account}'
def invokeWebhook (webHookUrl, account):
    url = webHookUrl.replace('{account}', account)
    print("Invoking Web hook, url: ", url)
    res = requests.get(url)
    print(res.text)

config = config.readConfig()
