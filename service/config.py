import json
import configparser

def readConfig():
    tmpconfig = configparser.ConfigParser()
    tmpconfig.read('config.cfg')

    config = {}

    # defaults
    config['listen.host'] = 'localhost'
    config['listen.port'] = 8080
    config['rpc.baseurl'] = 'http://localhost:54300'

    if 'main' in tmpconfig:
        if 'listen.host' in tmpconfig['main']:
            config['listen.host'] = tmpconfig['main']['listen.host']
        if 'listen.port' in tmpconfig['main']:
            config['listen.port'] = int(tmpconfig['main']['listen.port'])
        if 'rpc.baseurl' in tmpconfig['main']:
            config['rpc.baseurl'] = tmpconfig['main']['rpc.baseurl']

    return config
