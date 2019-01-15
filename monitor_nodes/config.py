import json
import configparser

def readConfig():
    tmpconfig = configparser.ConfigParser()
    tmpconfig.read('config.cfg')

    config = {}

    # defaults
    config['monitor_nodes.enabled'] = 'false'
    config['monitor_nodes.host'] = 'localhost'
    config['monitor_nodes.port'] = 8231

    if 'monitor_nodes' in tmpconfig:
        if 'enabled' in tmpconfig['monitor_nodes']:
            config['monitor_nodes.enabled'] = tmpconfig['monitor_nodes']['enabled']

        # support more configured observers
        config['monitor_nodes.observers'] = []
        for i in range(20):
            obs_pref = 'observer.' + str(i+1) + '.'
            if (obs_pref+'url' in tmpconfig['monitor_nodes']) and (obs_pref+'firewall' in tmpconfig['monitor_nodes']):
                config['monitor_nodes.observers'].append({
                    'url': tmpconfig['monitor_nodes'][obs_pref+'url'],
                    'firewall': tmpconfig['monitor_nodes'][obs_pref+'firewall']
                })

        if 'listen.host' in tmpconfig['monitor_nodes']:
            config['monitor_nodes.host'] = tmpconfig['monitor_nodes']['listen.host']
        if 'listen.port' in tmpconfig['monitor_nodes']:
            config['monitor_nodes.port'] = int(tmpconfig['monitor_nodes']['listen.port'])
        if 'sendout.service_url' in tmpconfig['monitor_nodes']:
            config['monitor_nodes.sendout.service_url'] = tmpconfig['monitor_nodes']['sendout.service_url']
        if 'sendout.account_id' in tmpconfig['monitor_nodes']:
            config['monitor_nodes.sendout.account_id'] = tmpconfig['monitor_nodes']['sendout.account_id']
        if 'sendout.account_password' in tmpconfig['monitor_nodes']:
            config['monitor_nodes.sendout.account_password'] = tmpconfig['monitor_nodes']['sendout.account_password']

    return config
