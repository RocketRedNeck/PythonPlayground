# Standard
import time

# 3rd Party 
import zmq

# Local

context = zmq.Context()

frontend = context.socket(zmq.XSUB)
frontend.bind('tcp://*:5500')                     # We are the proxy, so publishers connect to us

backend = context.socket(zmq.XPUB)
backend.bind('tcp://*:5501')                     # We are the proxy, so subscribers connect to us

zmq.proxy(frontend, backend)

# We never get here...
frontend.close()
backend.close()
context.term()
