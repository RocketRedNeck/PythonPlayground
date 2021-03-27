# Standard
import time

# 3rd Party 
import zmq

# Local
import DataModel

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect('tcp://localhost:5501')          # In the guide, the subscribers connect to well know addresses (in this we stay local)
socket.setsockopt_string(zmq.SUBSCRIBE, '')     # If you don't actually subscribe, you don't get anything! In this case any topic.
socket.RCVTIMEO = 1200                          # timeout in milliseconds so we can tell if there is anything happening while waiting for data
socket.setsockopt(zmq.RCVHWM, 1000)             # Allows us to get behind by approx this many messages 

header = DataModel.Header()

wait_count = 0
while True:
    try:
        pyobj = socket.recv_pyobj()
        type_pyobj = type(pyobj)
        if isinstance(pyobj,DataModel.Header):
            print(f'@ {pyobj.time} = {pyobj.count} from {pyobj.src}')
        else:
            print(f'Unknown Type Received: {type_pyobj}')
        wait_count = 0
    except KeyboardInterrupt:
        break
    except zmq.error.Again:
        wait_count += 1
        print(f'Waiting {wait_count}...')
