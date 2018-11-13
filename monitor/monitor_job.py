import db

import logging
import time
import threading
import requests

"""job delay in sec"""
delay = 300
baseUrl = "http://server2.mikron.io:8226/"
logging.basicConfig(level=logging.INFO)

def get_logger():
    """ Get named logger """
    return logging.getLogger(__name__)

def monitor_one():
    now = int(time.time())
    #print('monitor_one', now)
    session = requests.Session()
    no_nodes = get_nodes_count(session)
    no_blocks = get_block_count(session)
    no_frontiers = get_frontier_count(session)
    db.add_line(now, no_nodes, no_blocks, no_frontiers)

def get_nodes_count(session):
    try:
        url = baseUrl + "peers/count"
        response = session.get(url)
        if response.status_code == 200:
            return 1 + int(response.text)
    except:
        return 0
    return 0

def get_block_count(session):
    try:
        url = baseUrl + "blocks/count"
        response = session.get(url)
        if response.status_code == 200:
            return int(response.text)
    except:
        return 0
    return 0

def get_frontier_count(session):
    try:
        url = baseUrl + "frontiers/count"
        response = session.get(url)
        if response.status_code == 200:
            return int(response.text)
    except:
        return 0
    return 0

def start_job():
    now = int(time.time())
    next_update = now + 1
    while getattr(threading.currentThread(), "do_run", True):
        now = int(time.time())
        if now >= next_update:
            monitor_one()
            next_update = int((next_update + delay) / delay) * delay
            #get_logger().info("Next check in " + str(next_update - now) + " sec");
        to_sleep = max((next_update - now) / 2 - 1, 0.5)
        #get_logger().info("Sleep for " + str(to_sleep) + " sec");
        time.sleep(to_sleep)

bg_thread = None
def start_background():
    bg_thread = threading.Thread(target=start_job)
    bg_thread.start()

def stop_background():
    bg_thread.do_run = False
    bg_thread.join()
