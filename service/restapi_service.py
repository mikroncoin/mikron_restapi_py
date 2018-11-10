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

# Example: curl http://localhost:8090/blocks/count
@route('/blocks/count', method='GET')
def getBlockCount():
    count = ''
    try:
        count = node_rpc_helper.getBlockCount();
    except:
        count = 'ERROR'
    setHeaders()
    return count

@route('/blocks/count_unchecked', method='GET')
def getBlockCountUnchecked():
    count = ''
    try:
        count = node_rpc_helper.getBlockCountUnchecked();
    except:
        count = 'ERROR'
    setHeaders()
    return count

@route('/frontiers/count', method='GET')
def getFrontierCount():
    count = ''
    try:
        count = node_rpc_helper.getFrontierCount();
    except:
        count = 'ERROR'
    setHeaders()
    return count

# Example: curl http://localhost:8090/account/balance/mik_1naij1wkner3gb6j4o1tsf4me3zz8q9t1km9wnm5qzmnycfa44t8tkbq4srs
@route('/account/balance/<account_id>', method='GET')
def getAccountBalance(account_id):
    balance = node_rpc_helper.getAccountBalance(account_id)
    result = str(balance)
    setHeaders()
    return result

# Example: curl http://localhost:8090/account/history/mik_1naij1wkner3gb6j4o1tsf4me3zz8q9t1km9wnm5qzmnycfa44t8tkbq4srs
@route('/account/history/<account_id>', method='GET')
def getAccountHistory(account_id):
    history = node_rpc_helper.getAccountHistory(account_id, 20)
    setHeaders()
    return history

@route('/peers/count', method='GET')
def getPeerCount():
    count = '0'
    try:
        peers = node_rpc_helper.getPeers()
        print(peers)
        print(type(peers))
        if ((type(peers) is str) and peers == ''):
            # empty peer list, valid
            count = '0'
        else:
            if (type(peers) is not dict) and (type(peers) is not list):
                return peers
            count = str(len(peers))
    except:
        count ='ERROR'
    setHeaders()
    return count

@route('/peers/list', method='GET')
def getPeerList():
    try:
        peers = node_rpc_helper.getPeers()
        print(peers)
        print(type(peers))
        peers = '{"peer_list": ' + str(peers).replace("'", '"') + '}'
    except:
        peers ='ERROR'
    #print(peers)
    setHeaders()
    return peers
