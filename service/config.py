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
    config['treasury_service.enabled'] = 'false'
    config['treasury_service.max_amount'] = 100
    config['treasury_service.min_amount'] = 0.000000001
    config['treasury_service.account'] = { }
    config['receiver_service.enabled'] = 'false'
    config['receiver_service.account'] = { }

    if 'main' in tmpconfig:
        if 'listen.host' in tmpconfig['main']:
            config['listen.host'] = tmpconfig['main']['listen.host']
        if 'listen.port' in tmpconfig['main']:
            config['listen.port'] = int(tmpconfig['main']['listen.port'])
        if 'rpc.baseurl' in tmpconfig['main']:
            config['rpc.baseurl'] = tmpconfig['main']['rpc.baseurl']
    if 'treasury_service' in tmpconfig:
        if 'enabled' in tmpconfig['treasury_service']:
            config['treasury_service.enabled'] = tmpconfig['treasury_service']['enabled']
        if 'max_amount' in tmpconfig['treasury_service']:
            config['treasury_service.max_amount'] = tmpconfig['treasury_service']['max_amount']
        if 'min_amount' in tmpconfig['treasury_service']:
            config['treasury_service.min_amount'] = tmpconfig['treasury_service']['min_amount']
        if 'treasury_service.account' not in config:
            config['treasury_service.account'] = {}
        # support more configured accounts
        for i in range(20):
            acc_pref = 'account.' + str(i+1) + '.'
            if acc_pref+'id' in tmpconfig['treasury_service']:
                account = tmpconfig['treasury_service'][acc_pref+'id']
                #print('account:', account)
                config['treasury_service.account'][account] = {}
                config['treasury_service.account'][account]['id'] = account
            if acc_pref+'password' in tmpconfig['treasury_service']:
                config['treasury_service.account'][account]['password'] = tmpconfig['treasury_service'][acc_pref+'password']
            if acc_pref+'walletid' in tmpconfig['treasury_service']:
                config['treasury_service.account'][account]['walletid'] = tmpconfig['treasury_service'][acc_pref+'walletid']
            if acc_pref+'account' in tmpconfig['treasury_service']:
                config['treasury_service.account'][account]['account'] = tmpconfig['treasury_service'][acc_pref+'account']
    if 'receiver_service' in tmpconfig:
        if 'enabled' in tmpconfig['receiver_service']:
            config['receiver_service.enabled'] = tmpconfig['receiver_service']['enabled']
        if 'receiver_service.account' not in config:
            config['receiver_service.account'] = {}
        # support more configured accounts
        for i in range(20):
            acc_pref = 'account.' + str(i+1) + '.'
            if acc_pref+'id' in tmpconfig['receiver_service']:
                account = tmpconfig['receiver_service'][acc_pref+'id']
                print('account:', i+1, account)
                config['receiver_service.account'][account] = {}
                config['receiver_service.account'][account]['id'] = account
            if acc_pref+'password' in tmpconfig['receiver_service']:
                config['receiver_service.account'][account]['password'] = tmpconfig['receiver_service'][acc_pref+'password']
            if acc_pref+'walletid' in tmpconfig['receiver_service']:
                config['receiver_service.account'][account]['walletid'] = tmpconfig['receiver_service'][acc_pref+'walletid']
            if acc_pref+'account' in tmpconfig['receiver_service']:
                config['receiver_service.account'][account]['account'] = tmpconfig['receiver_service'][acc_pref+'account']
            if acc_pref+'receiver_webhook' in tmpconfig['receiver_service']:
                config['receiver_service.account'][account]['receiver_webhook'] = tmpconfig['receiver_service'][acc_pref+'receiver_webhook']
            if acc_pref+'auto_forward_to' in tmpconfig['receiver_service']:
                config['receiver_service.account'][account]['auto_forward_to'] = tmpconfig['receiver_service'][acc_pref+'auto_forward_to']

    return config
