import db

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

    nodes = db.get_all_daily_sorted_filter_time(start)
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
                'count_pos': n['count_pos'],
                'count_neg': n['count_neg'],
                'count_nonempty': n['count_nonempty'],
                'avg_bal': n['avg_bal'],
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
        nodes = db.get_nodes_period_filter_time(start, end)
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
                'avg_bal': n['avg_bal'],
            })
    except:
        ret = ['ERROR']
    setHeaders()
    return json.dumps(ret)

# TODO reward for ip/account for last 10 dasy
# TODO period for ip for last 3 days
