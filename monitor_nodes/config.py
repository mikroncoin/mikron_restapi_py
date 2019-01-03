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
        if 'listen.host' in tmpconfig['monitor_nodes']:
            config['monitor_nodes.host'] = tmpconfig['monitor_nodes']['listen.host']
        if 'listen.port' in tmpconfig['monitor_nodes']:
            config['monitor_nodes.port'] = int(tmpconfig['monitor_nodes']['listen.port'])

    return config
