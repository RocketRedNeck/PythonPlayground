# Standard
import time

# 3rd Party 
import zmq

# Local
import DataModel

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.bind('tcp://*:12345')
socket.setsockopt_string(zmq.SUBSCRIBE, '')
socket.RCVTIMEO = 1200 # in milliseconds

# Set High Water Mark to 1 if latency through queue is too high
# This will cause publisher to block until queue has been read
socket.set_hwm(1)

header = DataModel.Header()

wait_count = 0
while True:
    try:
        pyobj = socket.recv_pyobj()
        type_pyobj = type(pyobj)
        if isinstance(pyobj,DataModel.Header):
            print(f'@ {pyobj.time} = {pyobj.count}')
        else:
            print(f'Unknown Type Received: {type_pyobj}')
        wait_count = 0
    except KeyboardInterrupt:
        break
    except zmq.error.Again:
        wait_count += 1
        print(f'Waiting {wait_count}...')
