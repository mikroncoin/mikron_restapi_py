import evaluate
import payout
import db
import config

import logging
import time
import threading
#import requests
import json

# Evaluate node data
# After the end of every 10 minute period, after 1 minute run evaluation of the last 2+ slots
# After the end of every 4-hours, reevaluate the last 1+ days

config = config.readConfig()
logging.basicConfig(level=logging.INFO)

evaluate_period_last_started = 100000
evaluate_period_last_finished = 100000
evaluate_daily_last_started = 100000
evaluate_daily_last_finished = 100000

def get_logger():
    # Get named logger
    return logging.getLogger(__name__)

def start_job():
    global config
    time.sleep(30)
    get_logger().info('Started')
    global evaluate_period_last_started
    global evaluate_period_last_finished
    global evaluate_daily_last_started
    global evaluate_daily_last_finished
    while getattr(threading.currentThread(), "do_run", True):
        now = int(time.time())
        ten_minute = 600
        remainder_10min = now - (int(now / ten_minute) * ten_minute)
        # if remainder < 2 minutes, do nothing
        if remainder_10min >= 60:
            #get_logger('nodes2_job', 'Check', remainder_10min, now)
            if (now - evaluate_period_last_started) >= 300:
                # evaluate period now
                earliest_start_time = now - 7 * 24* 3600
                start_time = max(earliest_start_time, evaluate_period_last_started)
                get_logger().info('Do evaluate_periods ' + str(remainder_10min) + ' ' + str(now) + ' ' + str(start_time))
                evaluate_period_last_started = now
                evaluate.evaluate_periods(start_time, ten_minute)
                now = int(time.time())
                evaluate_period_last_finished = now
                get_logger().info('Done evaluate_periods ' + str(now))

                if (now - evaluate_daily_last_started) >= 4*3600:
                    # evaluate days now
                    earliest_start_time = now - 7 * 24* 3600
                    start_time = max(earliest_start_time, evaluate_daily_last_started)
                    get_logger().info('Do evaluate_days ' + str(now) + ' ' + str(start_time))
                    evaluate_daily_last_started = now
                    evaluate.evaluate_days(start_time)
                    now = int(time.time())
                    evaluate_daily_last_finished = now
                    get_logger().info('Done evaluate_days ' + str(now))

                    time.sleep(5)
                    get_logger().info('Do Payouts ' + str(now))
                    payout.do_payout(start_time, config)
                    get_logger().info('Done Payouts ' + str(now))
        time.sleep(30)
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