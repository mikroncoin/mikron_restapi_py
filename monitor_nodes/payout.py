import db

import logging
import time
import requests
import json

# Perform payout of node rewards

def get_logger():
    # Get named logger
    return logging.getLogger(__name__)

def do_payout_one(ip, start_time, dest_account, dest_amount, sendout_url, account_id, account_password, my_url):
    unique_id = str(ip) + "_" + str(start_time)
    callback = my_url + '/monitor_nodes/send-callback'
    url = sendout_url + '/treasury/send'
    get_logger().info('Sendout ' + str(account_id) + ' ' + str(unique_id) + ' ' + str(dest_amount) + ' ' + str(dest_account) + ' ' + url)
    send_data = {
        'pool_account_id': account_id,
        'pool_account_password': account_password,
        'dest_account': dest_account,
        'amount': dest_amount,
        'unique_id': unique_id,
        'callback': callback
    }
    try:
        #print(url)
        #print(send_data)
        response = requests.post(url, data = json.dumps(send_data))
        #print(response)
        #print(response.status_code)
        #print(response.text)
        get_logger().info('Response: ' + str(response.text))
    except:
        get_logger().error('Exception')
        return
    # Assume callback will be called and send processed there

def payout_callback(id, amount, hash):
    get_logger().info('payout_callback ' + str(id) + ' ' + str(amount) + ' ' + str(hash))
    # split ip and time from id
    index = id.find('_')
    if index < 0:
        get_logger().error('Wrong id ' + str(id))
        return
    ip = id[:index]
    time_start = id[index+1:]
    #print(ip, time)
    ret = db.update_daily_sent(time_start, ip, amount, int(time.time()), hash)
    get_logger().info('Post-send DB update ' + str(len(ret)))

def do_payout(time_start, config):
    now = int(time.time())
    sendout_url = config['monitor_nodes.sendout.service_url']
    account_id = config['monitor_nodes.sendout.account_id']
    account_password = config['monitor_nodes.sendout.account_password']
    my_url = 'http://' + config['monitor_nodes.host'] + ':' + str(config['monitor_nodes.port'])
    get_logger().info('Doing Payouts ' + str(now) + ' ' + account_id + ' ' + sendout_url + ' ')
    to_pay = db.get_daily_filter_topay_time(time_start)
    get_logger().info('Found ' + str(len(to_pay)) + ' rewards to pay out')
    for n in to_pay:
        get_logger().info('reward elig/sent: ' + str(n['reward_elig']) + ' ' + str(n['reward_sent']) + ' ' + str(n))
    
    # Perform payouts
    cnt = 0
    cnt_sum = 0
    for n in to_pay:
        reward_elig = float(n['reward_elig'])
        if reward_elig > 0:
            do_payout_one(n['ip'], n['time_start'], n['account'], reward_elig, sendout_url, account_id, account_password, my_url)
            cnt += 1
            cnt_sum += reward_elig

    get_logger().info('Rewards paid out, cnt ' + str(cnt) + ' sum ' + str(cnt_sum))
