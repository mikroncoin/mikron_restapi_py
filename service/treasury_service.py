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

# Example: curl -d "{'dest_addr':'mik_1naij1wkner3gb6j4o1tsf4me3zz8q9t1km9wnm5qzmnycfa44t8tkbq4srs', 'amount': '3', 'unique_id': '1234500017'}" http://localhost:8090/treasury/send
@route('/treasury/send', method='POST')
def send():
    global config
    if config['treasury_service.enabled'] != 'true':
        setHeaders()
        return {"error": "service not enabled"}

    postdata = request.body.read().decode('utf8')
    #print("postdata ", postdata)
    postjson = json.loads(postdata.replace("'", '"'))
    #print("postjson ", postjson)

    #pool_account_id = postjson["pool_account_id"]   # ignore for now
    #pool_account_password = postjson["pool_account_password"]   # ignore for now

    dest_addr = postjson["dest_addr"]
    #dest_addr = "mik_1naij1wkner3gb6j4o1tsf4me3zz8q9t1km9wnm5qzmnycfa44t8tkbq4srs"
    amount = postjson["amount"]
    unique_id = postjson["unique_id"]
    #unique_id = "1234500010"
    #print("dest_addr ", dest_addr, " amount ", amount, " id ", unique_id)

    # TODO, these should come from config, based on pool_account_id and pass
    src_addr = "mik_1rn3b9rhijhsehzn4aoudkczhixys7fumptohji6zeecctu4jb5ozfci5me3"
    src_walletid = "763952E04622426364BD62DD9A24056E6C0E48A2013BD3367AC8091F28FB274E"

    # debug: retrieve balance
    src_orig_balance = node_rpc_helper.getAccountBalance(src_addr)
    print("orig src balance", src_orig_balance)

    resp = node_rpc_helper.doSend(src_walletid, src_addr, dest_addr, amount, unique_id)
    setHeaders()
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
