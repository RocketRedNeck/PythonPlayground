# Standard
import time

# 3rd Party 
import zmq

# Local
import DataModel

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect('tcp://localhost:12345')         # In the guide, the subscribers connect to well know addresses (in this we stay local)
socket.setsockopt_string(zmq.SUBSCRIBE, '')     # If you don't actually subscribe, you don't get anything! In this case any topic.
socket.RCVTIMEO = 1000                          # timeout in milliseconds so we can tell if there is anything happening while waiting for data

socket.set_hwm(1)   # High Water Marks help define the backlog we can handle, in this case if we are behind, just let things drop

header = DataModel.Header()

wait_count = 0
last_header_count = 0
while True:
    try:
        pyobj = socket.recv_pyobj()
        type_pyobj = type(pyobj)
        if isinstance(pyobj,DataModel.Header):
            print(f'@ {pyobj.time} = {pyobj.count}')
            if last_header_count != 0 and pyobj.count > last_header_count + 1:
                print(f'Lost {pyobj.count - last_header_count - 1} Messages !!!!!')
            last_header_count = pyobj.count
        else:
            print(f'Unknown Type Received: {type_pyobj}')
        wait_count = 0
    except KeyboardInterrupt:
        break
    except zmq.error.Again:
        wait_count += 1
        print(f'Waiting {wait_count}...')
