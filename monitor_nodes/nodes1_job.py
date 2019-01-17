import db
import balance
import config

import logging
import time
import threading
import requests
import json

# monitor (retrieve and save) nodes
# job delay in sec
delay = 120
config = config.readConfig()
logging.basicConfig(level=logging.INFO)

def get_logger():
    # Get named logger
    return logging.getLogger(__name__)

def parse_endpoint(endpoint):
    if ':' not in endpoint:
        # no port
        return (endpoint, 0)
    if ('[' not in endpoint) and (']' not in endpoint):
        # simple host:port
        colon_idx = endpoint.rfind(':')
        return (endpoint[:colon_idx], endpoint[colon_idx+1:])
    # both [] and :, take last 
    colon_idx = endpoint.rfind(':')
    return (endpoint[:colon_idx], endpoint[colon_idx+1:])

def nodes_one():
    global config
    session = requests.Session()
    for obs in config['monitor_nodes.observers']:
        save_nodes(session, obs['url'], obs['firewall'])

def save_node(time, obs_srv, obs_firewall, host, port, account, balance):
    db.save_node(time, obs_srv, obs_firewall, host, port, account, balance)
    #print("Saved node:", time, obs_srv, obs_firewall, host, port, account, ".")

def save_nodes_int(session, obs_srv, obs_firewall):
    now = int(time.time())
    try:
        url = obs_srv + "/peers/list"
        response = session.get(url)
        if response.status_code != 200:
            get_logger().error('ERROR accessing node list ' + str(response.status_code) + ' ' + str(response.text))
            return 0
        #print(response.text)
        peers_json = json.loads(response.text)
        #print(peers_json)
        if 'peer_list' not in peers_json:
            return 0
        # process peer list
        cnt = 0
        for node in peers_json['peer_list']:
            #print(elem)
            if 'endpoint' in node:
                (host, port) = parse_endpoint(node['endpoint'])
                node_id = ''
                balan = 0
                if 'node_id' in node:
                    node_id = node['node_id']
                    balan = balance.get_account_balance_cached(now, session, obs_srv, node_id)
                    #print('balan', balan)
                save_node(now, obs_srv, obs_firewall, host, port, node_id, balan)
                cnt = cnt + 1
        return cnt
    except Exception as e:
        get_logger().error('ERROR accessing node list, exception ' + str(e))
        return 0
    return 0

def save_nodes(session, obs_srv, obs_firewall):
    #now = int(time.time())
    get_logger().info('Retrieving node list, srv ' + str(obs_srv) + ' ' + str(obs_firewall))
    no_nodes_saved = save_nodes_int(session, obs_srv, obs_firewall)
    if no_nodes_saved == 0:
        get_logger().error('Error retrieving node list, no nodes could be retrieved')
    else:
        get_logger().info('Nodes saved, cnt ' + str(no_nodes_saved) + ' srv ' + str(obs_srv))

def start_job():
    now = int(time.time())
    next_update = now + 1
    get_logger().info('Started')
    while getattr(threading.currentThread(), "do_run", True):
        now = int(time.time())
        if now >= next_update:
            nodes_one()
            next_update = max(int((next_update + delay) / delay) * delay, now + 1)   # max: prevent next_update in the past
            #get_logger().info("Next check in " + str(next_update - now) + " sec");
        to_sleep = min(30, max(0.5, (next_update - now) / 2 - 1))
        #get_logger().info("Sleep for " + str(to_sleep) + " sec");
        time.sleep(to_sleep)
    get_logger().info('Stopping')

bg_thread = None
def start_background():
    global bg_thread
    bg_thread = threading.Thread(target=start_job)
    bg_thread.start()

def stop_background():
    global bg_thread
    bg_thread.do_run = False
    bg_thread.join()
