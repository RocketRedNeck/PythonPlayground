# Standard
import time

# 3rd Party 
import zmq

# Local
import DataModel

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind('tcp://*:12345')    # In the guide, the publisher binds to an interface and waits for connections

socket.set_hwm(1)   # High Water Marks help define the backlog we can handle, in this case if we are behind, just let things drop

header = DataModel.Header()
footer = DataModel.Footer()

t0 = 0

mod_count = 0
while True:
    try:
        header.time = time.perf_counter() - t0
        header.count += 1
        print(f'@ {header.time} = {header.count}')
        socket.send_pyobj(header)
        
        time.sleep(1.0)
        mod_count += 1
        if mod_count % 5 == 0:
            socket.send_pyobj(footer)

    except KeyboardInterrupt:
        break
