import nodes1_job
import nodes2_job
import rest

from threading import Thread
from bottle import run

nodes1_job.start_background()
nodes2_job.start_background()

host = 'localhost'
port = 8231

run(host=host, port=port, debug=True)

print('Exiting (stand by...)')
nodes2_job.stop_background()
nodes1_job.stop_background()
