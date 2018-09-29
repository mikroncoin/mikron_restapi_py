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
    config['treasury_service.account'] = {
        "TestPool": {
            "id": "FaucetPool",
            "password": "some_password",
            "walletid": "74A552E04622426364BD62DD9A24056E6C0E48A2013BD3367AC8091F28FB274E",
            "address": "mik_2pn3b9rhijhsehzn4aoudkczhixys7fumptohji6zeecctu4jb5ozfci5ac4"
        }
    }

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
        # TODO: support more accounts
        if 'account.1.id' in tmpconfig['treasury_service']:
            account = tmpconfig['treasury_service']['account.1.id']
            config['treasury_service.account'][account] = {}
            config['treasury_service.account'][account]['id'] = account
        if 'account.1.password' in tmpconfig['treasury_service']:
            config['treasury_service.account'][account]['password'] = tmpconfig['treasury_service']['account.1.password']
        if 'account.1.walletid' in tmpconfig['treasury_service']:
            config['treasury_service.account'][account]['walletid'] = tmpconfig['treasury_service']['account.1.walletid']
        if 'account.1.address' in tmpconfig['treasury_service']:
            config['treasury_service.account'][account]['address'] = tmpconfig['treasury_service']['account.1.address']

    return config
