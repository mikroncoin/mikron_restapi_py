import db

import datetime
import sys

def dump_raw():
    nodes = db.get_all_nodes_unordered()
    print(str(len(nodes)) + " nodes")
    for n in nodes:
        print(int(n['time_sec']), n['ip'], n['port'], n['balance'], n['account'], sep=', ')

# Aggregate data into periods of period seconds
def dump_aggregated(period):
    minmax = db.get_min_max_time()
    #print(minmax)
    min = int(float(minmax[0]['min']))
    max = int(float(minmax[0]['max']))
    min_adj = int(min / period) * period
    max_adj = int(max / period) * period
    count = int((max_adj-min_adj)/period) + 1
    print('Time range:', min_adj, '--', max_adj + period - 1, 'count', count, 'unadjusted', min, '-', max, max-min)
    for i in range(0, count):
        start = min_adj + i * period
        end = start + period
        #print('Range', start, end-1)
        nodes = db.get_nodes_filter_time(start, end)
        if len(nodes) == 0:
            #print('Range', start, end-1, 'no data')
            noop = 0
        else:
            print('Range', start, end-1, 'count', len(nodes))
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
                if avg_bal == 0:
                    account = '0'  # hide print, just visual
                print(e, count, avg_bal, account)
