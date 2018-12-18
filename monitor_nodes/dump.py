import db

import datetime
import sys
import time

def dump_raw():
    nodes = db.get_all_nodes_unordered()
    print(str(len(nodes)) + " nodes")
    for n in nodes:
        print(int(n['time_sec']), n['ip'], n['port'], n['balance'], n['account'], sep=', ')

# Phase 1: Aggregate data into periods of period seconds
def recompute_aggregated_period(time_start, period):
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
            print('Range', start, end-1, period, 'count', count_total)
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

# Evaluate eligibility based on aggregated daily info
def evaluate_daily(time_start):
    now = int(time.time())
    ret = db.get_all_daily_sorted_filter_time(time_start)
    print('Retrieved', len(ret), 'daily records')
    for e in ret:
        time_start = int(e['time_start'])
        time_end = int(e['time_end'])
        date_time_start = datetime.datetime.utcfromtimestamp(time_start)
        ip = e['ip']
        count_pos = int(e['count_pos'])
        count_neg = int(e['count_neg'])
        avg_bal = float(e['avg_bal'])

        eligible = 1
        deny_reason = 'OK'
        reward_elig = 0

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

        # Evaluate: check reserve size
        if eligible > 0:
            if (avg_bal < 1000.0):
                eligible = 0
                deny_reason = 'Not enough reserve ' + str(avg_bal) + ' (min. 1000)'
            else:
                if (avg_bal < 25000.0):
                    eligible = 1
                    reward_elig = 25
                    deny_reason = 'Eligible for reward ' + str(reward_elig) + ' (min. 1000)'
                # TODO larger sums

        # Save result
        db.update_daily_eligible(time_start, ip, eligible, deny_reason, reward_elig)
        # Print result
        #print('  ', time_start, e['time_end'], date_time_start.isoformat(), ip, eligible, deny_reason, count_pos, count_neg, avg_bal, e['port'], e['account'])

# Aggregate data into days
def recompute_aggregated_days(time_start):
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

    evaluate_daily(min_adj)

# Print aggregated data, by periods
def regen_and_dump_aggregated_period(time_start_rel_day, period):
    now = int(time.time())
    time_start0 = now - 24 * 3600 * time_start_rel_day
    #print(time_start0)
    recompute_aggregated_period(time_start0, period)
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
def regen_and_dump_aggregated_daily(time_start_rel_day):
    now = int(time.time())
    time_start0 = now - 24 * 3600 * time_start_rel_day
    #print(time_start0)
    recompute_aggregated_period(time_start0, 600)  # 10-min
    recompute_aggregated_days(time_start0)
    ret = db.get_all_daily_sorted_filter_time(time_start0 - 24 *3600)
    #print('Retrieved', len(ret), 'daily records')
    print('Eligible nodes:')
    for e in ret:
        time_start = int(e['time_start'])
        date_time_start = datetime.datetime.utcfromtimestamp(time_start)
        ip = e['ip']
        eligible = int(e['eligible'])
        if eligible != 0:
            print('  ', date_time_start.isoformat(), ip, eligible, e['deny_reason'], e['count_pos'], e['count_neg'], e['count_nonempty'], e['avg_bal'], e['port'], e['account'])
    print('Non-eligible nodes:')
    for e in ret:
        time_start = int(e['time_start'])
        date_time_start = datetime.datetime.utcfromtimestamp(time_start)
        ip = e['ip']
        eligible = int(e['eligible'])
        if eligible == 0:
            print('  ', date_time_start.isoformat(), ip, eligible, e['deny_reason'], e['count_pos'], e['count_neg'], e['count_nonempty'], e['avg_bal'], e['port'], e['account'])
