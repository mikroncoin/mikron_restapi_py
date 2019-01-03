import db

import logging
import time

# Perform payout of node rewards

def get_logger():
    # Get named logger
    return logging.getLogger(__name__)

def do_payout(time_start, config):
    now = int(time.time())
    sendout_url = config['monitor_nodes.sendout.service_url']
    account_id = config['monitor_nodes.sendout.account_id']
    #account_password = config['monitor_nodes.sendout.account_password']
    get_logger().info('Doing Payouts ' + str(now) + ' ' + account_id + ' ' + sendout_url + ' ')
    to_pay = db.get_daily_filter_topay_time(time_start)
    get_logger().info('Found ' + str(len(to_pay)) + ' rewards to pay out')
    for n in to_pay:
        get_logger().info('reward elig/sent: ' + str(n['reward_elig']) + ' ' + str(n['reward_sent']) + ' ' + str(n))
    # TODO perform payouts

