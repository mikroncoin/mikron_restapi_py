import account_helper
import node_rpc_helper
import cache

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
        cached = cache.get_cache_entry('blocks/count')
        if cached != None:
            #print("Found in cache", cached)
            count = cached
        else:
            count = node_rpc_helper.getBlockCount();
            cache.add_cache_entry('blocks/count', count, 60)
            #print("Put in cache", count)
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
        cached = cache.get_cache_entry('frontiers/count')
        if cached != None:
            count = cached
        else:
            count = node_rpc_helper.getFrontierCount();
            cache.add_cache_entry('frontiers/count', count)
    except:
        count = 'ERROR'
    setHeaders()
    return count

@route('/frontiers/last/<count>', method='GET')
def getFrontiers(count):
    count = min(50, int(count))
    frontiers = node_rpc_helper.getFrontiers(count)
    setHeaders()
    return frontiers

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
    return getAccountHistoryPage(account_id, 0)

@route('/account/history/<account_id>/<page>', method='GET')
def getAccountHistoryPage(account_id, page):
    pagesize = 50
    offset = 0
    if int(page) >= 1:
        offset = int(page) * pagesize
    history = node_rpc_helper.getAccountHistory(account_id, pagesize, offset)
    setHeaders()
    return history

# Example: curl http://localhost:8090/block/8884FF53AE28F1DD5499F78733FC1A075864FFC428CEEC9A9C8A4ECCA98BB134
@route('/block/<block_hash>', method='GET')
def getBlock(block_hash):
    block = node_rpc_helper.getBlockInfo(block_hash)
    setHeaders()
    # return the contents
    if 'contents' in block:
        return block['contents']
    # fallback
    return block

@route('/peers/count', method='GET')
def getPeerCount():
    count = '0'
    try:
        cached = cache.get_cache_entry('peers/count')
        if cached != None:
            count = cached
        else:
            peers = node_rpc_helper.getPeers()
            #print(peers)
            #print(type(peers))
            if ((type(peers) is str) and peers == ''):
                # empty peer list, valid
                count = '0'
            else:
                if (type(peers) is not dict) and (type(peers) is not list):
                    count = 0
                else:
                    count = str(len(peers))
            cache.add_cache_entry('peers/count', count, 60)
    except:
        count = 'ERROR'
    setHeaders()
    return count

@route('/peers/list', method='GET')
def getPeerList():
    try:
        peers = node_rpc_helper.getPeers()
        #print(peers)
        #print(type(peers))
        if len(peers) == 0:
            peers = '{"peer_list": []}'
        else:
            peers = '{"peer_list": ' + str(peers).replace("'", '"') + '}'
    except:
        peers ='ERROR'
    #print(peers)
    setHeaders()
    return peers
