# CECS 327 Networks and Distributed Systems
# Daniel Son
# Anthony Giacalone
# Lab #1: Peer to Peer Networks
###############################################################################################
import threading
from network import Network
import os, errno, time

directory = os.path.dirname('./sync/')

# Create Network Object
net = Network()

# Set folder for sync
try:
    # Create folder
    os.makedirs(directory)
except OSError as e:
    # Ignore if folder is there
    # Some other error
    if e.errno != errno.EEXIST:
        raise

# Scan network to get list of IPs.
net.scan_network()

if __name__ == '__main__':
    # Create Thread for listen socket
    p1 = threading.Thread(target=net.listen_socket)
    print('thread 1 start: listen sockets')
    p1.start()

    # Create Thread for connect socket
    p2 = threading.Thread(target=net.connect_socket)
    print('thread 2 start: connect sockets')
    p2.start()

    # Create Thread for file listener
    p3 = threading.Thread(target=net.get_files)
    print('thread 3 start: file listener')
    p3.start()