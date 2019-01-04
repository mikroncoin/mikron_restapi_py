import db

import datetime
import sys
import time
import logging

is_running_evaluate_periods = False
is_running_evaluate_days = False
def start_evaluate_periods():
    global is_running_evaluate_periods
    now = int(time.time())
    if is_running_evaluate_periods:
        print('WARNING', 'evaluate_periods', 'already running', now)
        return
    is_running_evaluate_periods = True
    #print('start_evaluate_periods', now)
def stop_evaluate_periods():
    global is_running_evaluate_periods
    now = int(time.time())
    if not is_running_evaluate_periods:
        print('WARNING', 'evaluate_periods', 'not running', now)
        return
    is_running_evaluate_periods = False
    #print('stop_evaluate_periods', now)
def start_evaluate_days():
    global is_running_evaluate_days
    now = int(time.time())
    if is_running_evaluate_days:
        print('WARNING', 'evaluate_days', 'already running', now)
        return
    is_running_evaluate_days = True
    #print('start_evaluate_days', now)
def stop_evaluate_days():
    global is_running_evaluate_days
    now = int(time.time())
    if not is_running_evaluate_days:
        print('WARNING', 'evaluate_days', 'not running', now)
        return
    is_running_evaluate_days = False
    #print('stop_evaluate_days', now)

def get_logger():
    # Get named logger
    return logging.getLogger(__name__)

# Phase 1: Aggregate data into periods of period seconds
def evaluate_periods(time_start, period):
    if is_running_evaluate_periods:
        return
    start_evaluate_periods()

    minmax = db.get_min_max_time_raw()
    #print(minmax)
    min = int(float(minmax[0]['min']))
    if time_start > min:
        min = time_start
    max = int(float(minmax[0]['max']))
    min_adj = int(min / period) * period
    max_adj = int(max / period) * period
    count = int((max_adj-min_adj)/period) + 1
    print('Time range:', min_adj, '--', max_adj + period - 1, 'count', count, 'unadjusted', min, '-', max, max-min)

    db.delete_period_filter_time(min_adj)

    for i in range(0, count):
        start = min_adj + i * period
        end = start + period
        #print('Range', start, end-1)
        nodes = db.get_nodes_filter_time(start, end)
        count_total = len(nodes)
        if count_total == 0:
            #print('Range', start, end-1, 'no data')
            noop = 0
        else:
            #print('Range', start, end-1, period, 'count', count_total)
            #for n in nodes:
            #    print(int(n['time_sec']), n['ip'], n['port'], n['balance'], n['account'], sep=', ')
            # Aggregate by node
            node_dict = {}   # key is endpoint
            for n in nodes:
                endpoint = n['ip'] + ':' + n['port']
                if endpoint not in node_dict:
                    node_dict[endpoint] = {
                        'ip': n['ip'],
                        'port': n['port'],
                        'count': 0, 
                        'sum_bal': 0, 
                        'account': n['account'],
                    }
                #print('  ', endpoint, n['balance'])
                entry = node_dict[endpoint]
                node_dict[endpoint]['count'] = entry['count'] + 1
                node_dict[endpoint]['sum_bal'] = entry['sum_bal'] + float(n['balance'])
            # aggregated results
            for ep in node_dict:
                count = node_dict[ep]['count']
                sum_bal = node_dict[ep]['sum_bal']
                avg_bal = float(sum_bal) / float(count)
                account = node_dict[ep]['account']
                #print('  .', start, end, count_total, node_dict[ep]['ip'], node_dict[ep]['port'], count, account, avg_bal)
                db.add_period_entry(start, end, count_total, node_dict[ep]['ip'], node_dict[ep]['port'], count, account, avg_bal)
                #if avg_bal > 0:
                    #account = '0'  # hide print, just visual
                    #print(start, ep, count, avg_bal, account)

    stop_evaluate_periods()

# Evaluate eligibility based on aggregated daily info
# 25 MIK/day, min. 1000 MIK reserve; max 200 (total daily 5000)
# 375+25 MIK/day, min. 25K reserve; max 20 (total daily 7500)
# 4600+375+25 MIK/day, min. 1M reserve; max 5 (total daily 23000)
def __evaluate_daily(time_start):
    now = int(time.time())
    daynodes = db.get_all_daily_sorted_filter_time(time_start)
    print('Retrieved', len(daynodes), 'daily records')
    # Evaluate being online criteria
    for e in daynodes:
        time_start = int(e['time_start'])
        time_end = int(e['time_end'])
        date_time_start = datetime.datetime.utcfromtimestamp(time_start)
        ip = e['ip']
        count_pos = int(e['count_pos'])
        count_neg = int(e['count_neg'])
        avg_bal = float(e['avg_bal'])

        eligible = 1
        deny_reason = 'OK'
        e['reward_elig'] = 0

        # Evaluate: deny if day is not still complete
        if eligible > 0:
            if (time_end > now):
                eligible = 0
                deny_reason = 'Day has not passed yet'
        # Evaluate: deny if not online enough
        if eligible > 0:
            if (count_neg >= 29):
                eligible = 0
                deny_reason = 'Not online enough, not seen in ' + str(count_neg) + ' 10-minute periods'

        e['eligible'] = eligible
        e['deny_reason'] = deny_reason

    # Collect relevant balances
    avail_balance = {} # key is reserve account
    for e in daynodes:
        if e['eligible'] > 0:
            acc = e['account']
            bal = e['avg_bal']
            avail_balance[acc] = {'tot': avg_bal, 'avail': avg_bal}

    # Reward categories
    limit_cat1 = 1000
    limit_cat2 = 25000
    limit_cat3 = 1000000
    reward_cat1 = 25
    reward_cat2 = 375
    reward_cat3 = 4600
    max_count_cat1 = 200
    max_count_cat2 = 20
    max_count_cat3 = 5

    # Count candidates per categories (to compute reqards if over limit)
    count_cat1 = 0
    count_cat2 = 0
    count_cat3 = 0
    for e in daynodes:
        if e['eligible'] > 0:
            acc = e['account']
            if acc not in avail_balance:
                get_logger().error('Internal ERROR: Account not found in avail_balance ' + str(acc) + str(e['ip']))
            else:
                if avail_balance[acc]['avail'] >= limit_cat3:
                    count_cat3 += 1
                    avail_balance[acc]['avail'] -= limit_cat3
                if avail_balance[acc]['avail'] >= limit_cat2:
                    count_cat2 += 1
                    avail_balance[acc]['avail'] -= limit_cat2
                if avail_balance[acc]['avail'] >= limit_cat1:
                    count_cat1 += 1
                    avail_balance[acc]['avail'] -= limit_cat1
    
    # Compute reward amounts
    capped_count_cat1 = max(count_cat1, max_count_cat1)
    capped_count_cat2 = max(count_cat2, max_count_cat2)
    capped_count_cat3 = max(count_cat3, max_count_cat3)
    reward_cat1 = (max_count_cat1 * reward_cat1) / float(capped_count_cat1)
    reward_cat2 = (max_count_cat2 * reward_cat2) / float(capped_count_cat2)
    reward_cat3 = (max_count_cat3 * reward_cat3) / float(capped_count_cat3)
    # Print candidates per category, and rewards
    get_logger().info('Candidates in category 1: ' + str(count_cat1) + ' (' + str(capped_count_cat1) + ') rew ' + str(reward_cat1) + ' (lim ' + str(limit_cat1) + ')')
    get_logger().info('Candidates in category 2: ' + str(count_cat2) + ' (' + str(capped_count_cat2) + ') rew ' + str(reward_cat2) + ' (lim ' + str(limit_cat2) + ')')
    get_logger().info('Candidates in category 3: ' + str(count_cat3) + ' (' + str(capped_count_cat3) + ') rew ' + str(reward_cat3) + ' (lim ' + str(limit_cat3) + ')')

    for acc in avail_balance:
        #print(acc)
        avail_balance[acc]['avail'] = avail_balance[acc]['tot']
    # Evaluate reserve criteria (balance)
    for e in daynodes:
        if e['eligible'] > 0:
            avg_bal = float(e['avg_bal'])
            if avg_bal < limit_cat1:
                e['eligible'] = 0
                e['deny_reason'] = 'Not enough Reserve ' + str(avg_bal) + ' (limit ' + str(limit_cat1) + ')'
            else:
                if avg_bal < limit_cat2:
                    e['eligible'] = 1
                    e['reward_elig'] = reward_cat1
                    e['deny_reason'] = 'Eligible for Reward, ' + str(reward_cat1) + ' (C1, limit ' + str(limit_cat1) + ')'
                else:
                    if avg_bal < limit_cat3:
                        e['eligible'] = 1
                        e['reward_elig'] = reward_cat2 + reward_cat1
                        e['deny_reason'] = 'Eligible for Reward, ' + str(reward_cat2) + ' + ' + str(reward_cat1) + ' (C2, limit ' + str(limit_cat2) + ')'
                    else:
                        e['eligible'] = 1
                        e['reward_elig'] = reward_cat3 + reward_cat2 + reward_cat1
                        e['deny_reason'] = 'Eligible for Reward, ' + str(reward_cat3) + ' + ' + str(reward_cat2) + ' + ' + str(reward_cat1) + ' (C3, limit ' + str(limit_cat3) + ')'

    # Save result
    for e in daynodes:
        db.update_daily_eligible(e['time_start'], e['ip'], e['eligible'], e['deny_reason'], e['reward_elig'])  # TODO key is it enough?
        # Print result
        #print('  ', time_start, e['time_end'], date_time_start.isoformat(), ip, eligible, deny_reason, count_pos, count_neg, avg_bal, e['port'], e['account'])

# Aggregate data into days
def evaluate_days(time_start):
    if is_running_evaluate_days:
        return
    start_evaluate_days()

    # TODO do not evaluate period for which payment has already made!
    minmax = db.get_min_max_time_raw()
    #print(minmax)
    min = int(float(minmax[0]['min']))
    if time_start > min:
        min = time_start
    max = int(float(minmax[0]['max']))
    period_day = 24 * 3600
    min_adj = int(min / period_day) * period_day
    max_adj = int(max / period_day) * period_day
    count = int((max_adj-min_adj)/period_day) + 1
    print('Time range:', min_adj, '--', max_adj + period_day - 1, 'count', count, 'unadjusted', min, '-', max, max-min)

    db.delete_daily_filter_time(min_adj)

    period = 600
    periods_per_day = int(period_day / period)
    for i in range(0, count):
        day_start = min_adj + i * period_day
        day_end = day_start + period_day
        print('Day', day_start, datetime.datetime.utcfromtimestamp(day_start).isoformat())

        # Phase 2a  Check each 10-minute period within the day -- if there are any with 0 measurements, those will be ignored (not counted as negative)
        # Also collect IPs in the day, and the first port and account associated to it
        period_count_dict = {}  # key is period number, 0-143
        node_dict = {}  # key is IP
        #print('Periods:')
        period_cnt_nonempty = 0
        for j in range(0, periods_per_day):  # 10-min periods, 144
            start = day_start + j * period
            end = start + period
            #print('Range', start, end-1, period)
            nodes = db.get_nodes_period_filter_time(start, end)
            len_nodes = len(nodes)
            #print('Range', start, end-1, period, len_nodes)
            period_count_dict[j] = len_nodes
            #print(len_nodes, ' ', end='')
            if len_nodes > 0:
                #print('Range', start, end-1, period, len_nodes)
                period_cnt_nonempty = period_cnt_nonempty + 1
                for e in nodes:
                    ip = e['ip']
                    #if ip not in node_dict:
                    node_dict[ip] = {
                        'ip': ip,
                        'port': e['port'],
                        'account': e['account'],
                        'count_pos': 0,
                        'count_neg': 0,
                        'sum_bal': 0.0,
                        'avg_bal': 0.0,
                        'eligible': 1,
                        'deny_reason': 'OK'
                    }
        #print('.')
        period_cnt_empty = periods_per_day - period_cnt_nonempty
        print('Non-empty periods:', period_cnt_nonempty, 'empty periods', period_cnt_empty, '(of', periods_per_day, ')')
        # Print IPs
        #print('IPs found:')
        #for ip in node_dict:
        #    print('  ', ip, node_dict[ip]['port'], node_dict[ip]['account'])
        
        # Phase 2: Aggregate positive and negative counts
        for j in range(0, periods_per_day):  # 10-min periods, 144
            start = day_start + j * period
            end = start + period
            #print('Period', j, start, end-1, period)
            nodes = db.get_nodes_period_filter_time(start, end)
            len_nodes = len(nodes)
            if len_nodes > 0:
                #print('DEBUG', j, 'len_nodes', len_nodes)
                for e in nodes:
                    ip =  e['ip']
                    count_tot = e['count_tot']
                    count = e['count']
                    if ip not in node_dict:
                        print('ERROR, ip not found', ip)
                    else:
                        #print(e['ip'], e['port'], e['avg_bal'], e['account'])
                        if e['port'] == node_dict[ip]['port']:  # have to have the same port
                            if e['account'] == node_dict[ip]['account']:  # have to have the same port
                                if count_tot > 0:
                                    if count > 0:
                                        count_pos = node_dict[ip]['count_pos'] + 1
                                        node_dict[ip]['count_pos'] = count_pos
                                        sum_bal = node_dict[ip]['sum_bal'] + float(e['avg_bal'])
                                        node_dict[ip]['sum_bal'] = sum_bal
                    #if count_pos >= 143:
                    #    print('DEBUG', count_pos, j, start, e['ip'], e['port'], e['avg_bal'], e['account'])
        # Compute some derived values: count_neg, avg_bal
        for ip in node_dict:
            count_pos = int(node_dict[ip]['count_pos'])
            count_neg = period_cnt_nonempty - count_pos
            node_dict[ip]['count_neg'] = count_neg
            sum_bal = float(node_dict[ip]['sum_bal'])
            avg_bal = 0
            if count_pos > 0:
                avg_bal = sum_bal / float(count_pos)
            node_dict[ip]['avg_bal'] = avg_bal
            #print('  ', ip, count_pos, count_neg, period_cnt_nonempty, avg_bal, node_dict[ip]['port'], node_dict[ip]['account'])
            db.add_daily(day_start, day_end, ip, node_dict[ip]['port'], node_dict[ip]['account'], count_pos, count_neg, period_cnt_nonempty, avg_bal)
    # end days cycle

    __evaluate_daily(min_adj)

    stop_evaluate_days()

# Dump all raw data
def dump_raw():
    nodes = db.get_all_nodes_unordered()
    print(str(len(nodes)) + " nodes")
    for n in nodes:
        print(int(n['time_sec']), n['ip'], n['port'], n['balance'], n['account'], sep=', ')

# Print aggregated data, by periods
def regen_and_dump_aggregated_period(time_start_rel_day, period):
    now = int(time.time())
    time_start0 = now - 24 * 3600 * time_start_rel_day
    #print(time_start0)
    evaluate_periods(time_start0, period)
    ret = db.get_all_period_sorted()
    print('Retrieved', len(ret), 'period records')
    for e in ret:
        time_start = int(e['time_start'])
        date_time_start = datetime.datetime.utcfromtimestamp(time_start)
        count_tot = int(e['count_tot'])
        count = int(e['count'])
        avg_bal = float(e['avg_bal'])
        # filter printout
        if count_tot > 0 and count > 0 and avg_bal > 0:
            print('  ', time_start, e['time_end'], date_time_start.isoformat(), count_tot, e['ip'], e['port'], count, e['account'], avg_bal)

# Print aggregated data, by days
def dump_aggregated_daily(time_start_rel_day):
    now = int(time.time())
    time_start0 = now - time_start_rel_day * 24 * 3600
    #print(time_start0)

    ret = db.get_all_daily_sorted_filter_time(time_start0 - 24 * 3600)
    print('Retrieved', len(ret), 'daily records')
    print('Eligible nodes:')
    for e in ret:
        time_start = int(e['time_start'])
        date_time_start = datetime.datetime.utcfromtimestamp(time_start)
        ip = e['ip']
        eligible = int(e['eligible'])
        if eligible != 0:
            print('  ', date_time_start.isoformat(), time_start, ip, eligible, e['deny_reason'], e['count_pos'], e['count_neg'], e['count_nonempty'], e['avg_bal'], e['port'], e['account'], e['reward_elig'], e['reward_sent'], e['sent_time'], e['sent_hash'])
    print('Non-eligible nodes:')
    for e in ret:
        time_start = int(e['time_start'])
        date_time_start = datetime.datetime.utcfromtimestamp(time_start)
        ip = e['ip']
        eligible = int(e['eligible'])
        if eligible == 0:
            print('  ', date_time_start.isoformat(), time_start, ip, eligible, e['deny_reason'], e['count_pos'], e['count_neg'], e['count_nonempty'], e['avg_bal'], e['port'], e['account'], e['reward_elig'], e['reward_sent'], e['sent_time'], e['sent_hash'])

# Reevaluate daily data
def regen_aggregated_daily(time_start_rel_day, reeval_periods = False):
    now = int(time.time())
    time_start0 = now - time_start_rel_day * 24 * 3600
    #print(time_start0)

    if reeval_periods:
        evaluate_periods(time_start0, 600)  # 10-min
    evaluate_days(time_start0)
