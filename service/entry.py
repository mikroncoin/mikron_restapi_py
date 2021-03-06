import config
#import account_helper
#import node_rpc_helper
import restapi_service
import treasury_service
import receiver_service
import explorer_hoster
import recv_setup

from bottle import run

#import os
#import json
#from bottle import run, post, request, response, get, route, static_file
#from threading import Thread

# Entry, startup
config = config.readConfig()

# Recevier status, initial check in background
if config['receiver_service.enabled'] == 'true':
    recv_setup.setup_check_async()

print('listen.host', config['listen.host'])
print('listen.port', config['listen.port'])
print('treasury_service.enabled', config['treasury_service.enabled'])
print('config', config)

run(host=config['listen.host'], port=config['listen.port'], debug=True)
