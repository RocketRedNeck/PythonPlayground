# Standard
import time

# 3rd Party 
import zmq

# Local
import DataModel

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.connect('tcp://localhost:12345')

# Set High Water Mark to 1 if latency through queue is too high
# This will cause publisher to block until queue has been read
socket.set_hwm(1)

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
