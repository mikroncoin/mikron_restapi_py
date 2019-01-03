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
        if 'observer.1.url' in tmpconfig['monitor_nodes']:
            config['monitor_nodes.observer.1.url'] = tmpconfig['monitor_nodes']['observer.1.url']
        if 'observer.1.firewall' in tmpconfig['monitor_nodes']:
            config['monitor_nodes.observer.1.firewall'] = int(tmpconfig['monitor_nodes']['observer.1.firewall'])
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
