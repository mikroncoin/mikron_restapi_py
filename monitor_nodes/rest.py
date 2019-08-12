import db_compute
import payout

#import os
import json
from bottle import post, request, response, get, route, static_file
from threading import Thread
import datetime
import time

@route('/monitor_nodes/', method='GET')
@route('/monitor_nodes', method='GET')
def get_control_panel_index():
    return static_file("control_panel.html", root="monitor_nodes/")

def setHeaders():
    response.content_type = 'application/json'
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

# List of rewards for last 3 days
@route('/monitor_nodes/rewards/last3', method='GET')
def getRewards3():
    period_day = 24 * 3600
    start0 = int(time.time()) - 3 * period_day
    start = int(start0 / period_day) * period_day

    nodes = db_compute.get_all_daily_sorted_filter_time_rev(start)
    ret = []
    try:
        for n in nodes:
            time_start = int(n['time_start'])
            dat = datetime.datetime.utcfromtimestamp(time_start).isoformat()
            ret.append({
                'date': dat,
                'time_start': time_start,
                'time_end': n['time_end'],
                'ip': n['ip'],
                'port': n['port'],
                'account': n['account'],
                'net_version': n['net_version'],
                'count_pos': n['count_pos'],
                'count_neg': n['count_neg'],
                'count_nonempty': n['count_nonempty'],
                'avg_bal': 0.001 * int(1000 * float(n['avg_bal'])),
                'eligible': n['eligible'],
                'deny_reason': n['deny_reason'],
                'reward_elig': n['reward_elig'],
                'reward_sent': n['reward_sent'],
                'sent_hash': n['sent_hash'],
                'sent_time': n['sent_time'],
            })
    except:
        ret = ['ERROR']
    setHeaders()
    return json.dumps(ret)

# List of periods for last 6 10-min-periods
@route('/monitor_nodes/periods/last6', method='GET')
def getPeriods6():
    period = 600
    now = int(time.time())
    start = int((now - 6 * period) / period) * period
    end = int((now + period) / period) * period
    ret = []
    try:
        nodes = db_compute.get_nodes_period_filter_time(start, end)
        for n in nodes:
            time_start = int(n['time_start'])
            dat = datetime.datetime.utcfromtimestamp(time_start).isoformat()
            ret.append({
                'date': dat,
                'time_start': time_start,
                'time_end': n['time_end'],
                'count_tot': n['count_tot'],
                'ip': n['ip'],
                'port': n['port'],
                'count': n['count'],
                'account': n['account'],
                'avg_bal': 0.001 * int(1000 * float(n['avg_bal'])),
                'net_version': n['net_version'],
            })
    except:
        ret = ['ERROR']
    setHeaders()
    return json.dumps(ret)

# TODO reward for ip/account for last 10 dasy
# TODO period for ip for last 3 days

# Sample send callback, used for testing
#  Example: curl -d "{'id': '1234500017', 'amount': '3', 'block_hash': 'D70BB005723EF4AE3850861FB8819628CD101EE1F3A4FF40808213EB5B99FECF'}" http://localhost:8090/treasury/sample-send-callback
@route('/monitor_nodes/send-callback', method='POST')
def send_callback():
    global config
    setHeaders()
    postdata = request.body.read().decode('utf8')
    #print("postdata ", postdata)
    postjson = json.loads(postdata.replace("'", '"'))
    #print("postjson ", postjson)

    if 'error' in postjson:
        print('Send callback', 'ERROR', postjson['error'])
    else:
        id = ''
        if 'id' in postjson:
            id = postjson['id']
        amount = 0
        if 'amount' in postjson:
            amount = postjson['amount']
        block_hash = ''
        if 'block_hash' in postjson:
            block_hash = postjson['block_hash']
        #print('Send callback', 'id', id, 'amount', amount, 'block_hash', block_hash)
        payout.payout_callback(id, amount, block_hash)
