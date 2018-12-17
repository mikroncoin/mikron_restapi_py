import db

import datetime
import sys
import time

def dump_raw():
    nodes = db.get_all_nodes_unordered()
    print(str(len(nodes)) + " nodes")
    for n in nodes:
        print(int(n['time_sec']), n['ip'], n['port'], n['balance'], n['account'], sep=', ')

# Aggregate data into periods of period seconds
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
            node_dict = {}
            for n in nodes:
                endpoint = n['ip'] + ':' + n['port']
                if endpoint not in node_dict:
                    node_dict[endpoint] = {
                        'ip': n['ip'],
                        'port': n['port'],
                        'count': 0, 
                        'sum_bal': 0, 
                        'account': n['account']
                    }
                #print('  ', endpoint, n['balance'])
                entry = node_dict[endpoint]
                node_dict[endpoint]['count'] = entry['count'] + 1
                node_dict[endpoint]['sum_bal'] = entry['sum_bal'] + float(n['balance'])
            # aggregated results
            for e in node_dict:
                count = node_dict[e]['count']
                sum_bal = node_dict[e]['sum_bal']
                avg_bal = float(sum_bal) / float(count)
                account = node_dict[e]['account']
                #print('  .', start, end, count_total, node_dict[e]['ip'], node_dict[e]['port'], count, account, avg_bal)
                db.add_period_entry(start, end, count_total, node_dict[e]['ip'], node_dict[e]['port'], count, account, avg_bal)
                if avg_bal > 0:
                    #account = '0'  # hide print, just visual
                    print(e, count, avg_bal, account)

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

    for i in range(0, count):
        day_start = min_adj + i * period_day
        day_end = day_start + period_day
        #print('Range', start, end-1)
        # collect IPs in the day
        node_dict = {}
        period = 600
        for j in range(0, int(period_day / period)):  # 10-min periods
            start = day_start + j * period
            end = start * period
            nodes = db.get_nodes_period_filter_time(start, end)
            #print('Range', start, end-1, period)
            for e in nodes:
                ip = e['ip']
                if ip not in node_dict:
                    node_dict[ip] = {
                        'ip': ip,
                        'port': e['port'],
                        'count_pos': 0,
                        'count_neg': 0,
                        'account': e['account'],
                        'sum_bal': 0.0,
                    }
        # Print IPs
        print('IPs found on day', day_start, datetime.datetime.utcfromtimestamp(day_start).isoformat())
        for n in node_dict:
            print('  ', day_start, n, node_dict[n]['ip'])
        # Aggregate positive and negative counts

        # TODO: revisit negative handling
        for j in range(0, int(period_day / period)):  # 10-min periods
            start = day_start + j * period
            end = start * period
            nodes = db.get_nodes_period_filter_time(start, end)
            count_tot = len(nodes)
            # only count if there area at least 1 measurements in this period
            if count_tot > 0:
                for e in nodes:
                    ip =  e['ip']
                    count_tot = e['count_tot']
                    count = e['count']
                    if ip in node_dict:
                        port = node_dict[ip]['port']
                        if port == e['port']:
                            # take into account only one port
                            if count_tot > 0:
                                if count > 0:
                                    count_pos = node_dict[ip]['count_pos'] + 1
                                    node_dict[ip]['count_pos'] = count_pos
                                else:
                                    count_neg = node_dict[ip]['count_neg'] + 1
                                    node_dict[ip]['count_neg'] = count_neg
                                sum_bal = node_dict[ip]['sum_bal'] + float(e['avg_bal'])
                                node_dict[ip]['sum_bal'] = sum_bal
        # Print aggregated
        for ip in node_dict:
            count_pos = node_dict[ip]['count_pos']
            count_neg = node_dict[ip]['count_neg']
            sum_bal = node_dict[ip]['sum_bal']
            print('  ', ip, count_pos, count_neg, sum_bal)

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
    ret = db.get_all_daily_sorted()
    print('Retrieved', len(ret), 'daily records')
    for e in ret:
        time_start = int(e['time_start'])
        date_time_start = datetime.datetime.utcfromtimestamp(time_start)
        count_tot = int(e['count_tot'])
        count = int(e['count'])
        avg_bal = float(e['avg_bal'])
        # filter printout
        if count_tot > 0 and count > 0 and avg_bal > 0:
            print('  ', time_start, e['time_end'], date_time_start.isoformat(), count_tot, e['ip'], e['port'], count, e['account'], avg_bal)
