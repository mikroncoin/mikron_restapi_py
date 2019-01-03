import nodes1_job
import nodes2_job
import rest
import config

from threading import Thread
from bottle import run

config = config.readConfig()
print('monitor_nodes.host', config['monitor_nodes.host'])
print('monitor_nodes.port', config['monitor_nodes.port'])
print('monitor_nodes.enabled', config['monitor_nodes.enabled'])
print('config', config)

if config['monitor_nodes.enabled'] != 'true':
    print('Not enabled, check config!')
else:
    nodes1_job.start_background()
    nodes2_job.start_background()

    run(host=config['monitor_nodes.host'], port=config['monitor_nodes.port'], debug=True)

    print('Exiting (stand by...)')
    nodes2_job.stop_background()
    nodes1_job.stop_background()
