import config
import account_helper
import node_rpc_helper

import os
import json
from bottle import run, post, request, response, get, route, static_file
from threading import Thread

def setHeaders():
    response.content_type = 'application/json'
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

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

@route('/account/balance/<account_id>', method='GET')
def getAccountBalance(account_id):
    balance = account_helper.getAccountBalance(account_id)
    result = str(balance)
    setHeaders()
    return result

@route('/peers/count', method='GET')
def getPeerCount():
    count = '0'
    try:
        peers = node_rpc_helper.getPeers()
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
    except:
        peers ='ERROR'
    setHeaders()
    return peers

# Entry, startup
config = config.readConfig()

print('listen.host', config['listen.host'])
print('listen.port', config['listen.port'])
print('config', config)

run(host=config['listen.host'], port=config['listen.port'], debug=True)
