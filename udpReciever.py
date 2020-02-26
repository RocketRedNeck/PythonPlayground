import socket
import time

ANY = "0.0.0.0"
MCAST_ADDR = "224.168.2.9"
MCAST_PORT = 53425

# create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

# allow multiple sockets to use the same PORT number
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind to the port that we know will receive multi-cast data
sock.bind((ANY, MCAST_PORT))

# tell the kernel that we are a multi-cast socket
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 255)

# Tell the kernel that we want to add ourselves to a multi-cast group
# The address for the multi-cast group is the third param
status = sock.setsockopt(socket.IPPROTO_IP,
socket.IP_ADD_MEMBERSHIP,
socket.inet_aton(MCAST_ADDR) + socket.inet_aton(ANY))

sock.setblocking(0)
ts = time.time()
while True:
    try:
        data, addr = sock.recvfrom(1024)
        print("We got data!")
        print("FROM: ", addr)
        print("DATA: ", data)
    except socket.error as e:
        print(e)
