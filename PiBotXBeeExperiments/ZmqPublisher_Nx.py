# Standard
import argparse
import time

# 3rd Party 
import zmq

# Local
import DataModel

# Create arg parser
parser = argparse.ArgumentParser()

parser.add_argument('--id', required=True, type = int, default=1, help='Publisher ID')

# Parse the args
args = vars(parser.parse_args())

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.connect('tcp://localhost:5500')    # Connect to a proxy subscriber to avoid needing worry about scalabilitys
socket.setsockopt(zmq.SNDHWM, 10000)      # Send High Water Mark allows for late subscribers to get some old messages



header = DataModel.Header()
header.src = args['id']

t0 = 0

while True:
    try:
        header.time = time.perf_counter() - t0
        header.count += 1
        print(f'@ {header.time} = {header.count}')
        socket.send_pyobj(header)
        
        time.sleep(1.0)

    except KeyboardInterrupt:
        break
