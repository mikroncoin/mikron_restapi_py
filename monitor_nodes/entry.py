import nodes1_job
import rest

from threading import Thread
from bottle import run

nodes1_job.start_background()

host = 'localhost'
port = 8229

run(host=host, port=port, debug=True)

#nodes1_job.stop_background()
