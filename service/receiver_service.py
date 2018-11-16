import config
import account_helper
import node_rpc_helper
import recv_db
import node_rpc_helper

import os
import json
from bottle import post, request, response, get, route, static_file
from threading import Thread
import requests
import time

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
def createAccountApi():
    global config
    setHeaders()
    if config['receiver_service.enabled'] != 'true':
        return {"error": "service not enabled"}

    postdata = request.body.read().decode('utf8')
    #print("postdata ", postdata)
    postjson = json.loads(postdata.replace("'", '"'))
    #print("postjson ", postjson)

    if ("pool_account_id" not in postjson) or ("pool_account_password" not in postjson):
        return {"error": "Missing pool account parameters"}
    pool_account_id = postjson["pool_account_id"]
    pool_account_password = postjson["pool_account_password"]
    user_data = ''
    if "user_data" in postjson:
        user_data = postjson["user_data"]

    return createAccount(pool_account_id, pool_account_password, user_data)

def createAccount(pool_account_id, pool_account_password, user_data):
    global config

    if (pool_account_id not in config["receiver_service.account"]) or (pool_account_password != config["receiver_service.account"][pool_account_id]["password"]):
        return {"error": "source account not found or wrong password"}
    src_walletid = config["receiver_service.account"][pool_account_id]["walletid"]
    root_account = config["receiver_service.account"][pool_account_id]["account"]
    #print("walletid ", src_walletid)

    resp = node_rpc_helper.doCreateAccount(src_walletid)
    if 'error' in resp:
        return resp
    if 'account' not in resp:
        return {"error": "no account in response"}
    account = resp['account']
    account_idx = -1   # this is supposed to be the index of this account in the wallet, but we don't know it

    try:
        # OK, put it in DB
        recv_db.add_new_rec_account(account, pool_account_id, user_data, root_account, account_idx, src_walletid)
    except:
        print("could not save to DB", account)

    return {
        "account": account
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
        print("Error: no account in callback info")
        return
    account = postjson['account']
    print("RPC callback", "account", account)

    # find receiver account in DB
    pool_account_id = ''
    try:
        db_acc = recv_db.get_account(account)
        #print(len(db_acc))
        if len(db_acc) >= 1:
            #print(db_acc[0])
            if 'pool_account_id' in db_acc[0]:
                pool_account_id = db_acc[0]['pool_account_id']
    except:
        print('Error looking up in DB')
    if (len(pool_account_id) <= 0) or (pool_account_id not in config['receiver_service.account']):
        print('Could not match account to a configured receiver account!', account)
        # DO NOT call into any webhooks...     # invokeWebhookForPoolAccount('', account)
    else:
        # pool account is known
        # check auto-forward
        invokeWebhookForPoolAccount(pool_account_id, account)
        handleAutoForward(account, pool_account_id, postjson)
    return "ok"
    
# Call into the hook of a partner site, URL of the form 'https://mikron.io/webhook/{account}'
def invokeWebhookForPoolAccount(pool_account_id, account):
    if (len(pool_account_id) <= 0) or (pool_account_id not in config['receiver_service.account']):
        # no pool account, call into *all* webhooks anyways
        for rec_account in config['receiver_service.account']:
            if 'receiver_webhook' in config['receiver_service.account'][rec_account]:
                webhook = config['receiver_service.account'][rec_account]['receiver_webhook']
                #print(webhook)
                invokeWebhook(webhook, account)
    else:
        if 'receiver_webhook' in config['receiver_service.account'][pool_account_id]:
            webhook = config['receiver_service.account'][pool_account_id]['receiver_webhook']
            #print(webhook)
            invokeWebhook(webhook, account)

def invokeWebhook(webHookUrl, account):
    url = webHookUrl.replace('{account}', account)
    print("Invoking Web hook in background, url: ", url)
    t = Thread(target=invokeInBg, args=(url,))
    t.start()

def handleAutoForward(account, pool_account_id, postjson):
    # check auto-forward
    if pool_account_id in config['receiver_service.account']:
        if 'auto_forward_to' in config['receiver_service.account'][pool_account_id]:
            forward_acc = config['receiver_service.account'][pool_account_id]['auto_forward_to']
            #print(forward_acc)
            latest_balance = 0
            if "block" in postjson:
                block_json = json.loads(postjson["block"])
                if "balance" in block_json:
                    latest_balance_str = block_json["balance"]
                    latest_balance = int(latest_balance_str)
            #print("latest_balance", latest_balance)
            if latest_balance > 0:
                wallet_id = config['receiver_service.account'][pool_account_id]['walletid']
                unique_id = str(time.time()) + account[:16]
                latest_balance_mik = account_helper.fromRawToMikron(latest_balance)
                #print("latest_balance_mik", latest_balance_mik)
                node_rpc_helper.doSend(wallet_id, account, forward_acc, latest_balance_mik, unique_id)
                print("Auto forwarded", latest_balance_mik, "to", forward_acc)

def invokeInBg(url):
    response = requests.get(url)
    print(response.url, response.text[:200])

config = config.readConfig()
