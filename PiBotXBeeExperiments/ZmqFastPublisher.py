# Standard
import time

# 3rd Party 
import zmq

# Local
import DataModel

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind('tcp://*:12345')    # In the guide, the publisher binds to an interface and waits for connections

socket.set_hwm(1000)   # High Water Marks help define the backlog we can handle, in this case if we are behind, just let things drop

header = DataModel.Header()

t0 = 0

while True:
    try:
        header.time = time.perf_counter() - t0
        header.count += 1
        socket.send_pyobj(header)
        print(f'@ {header.time} = {header.count}')
        
    except KeyboardInterrupt:
        break
