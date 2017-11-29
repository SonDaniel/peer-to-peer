# CECS 327 Networks and Distributed Systems
# Daniel Son
# Anthony Giacalone
# Lab #1: Peer to Peer Networks

# from threading import Thread
import threading
from network import Network
import os, errno, time

directory = os.path.dirname('./sync/')
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

net.scan_network()

if __name__ == '__main__':
    p1 = threading.Thread(target=net.listen_socket)

    print('thread 1 start: listen sockets')
    p1.start()

    p3 = threading.Thread(target=net.get_files)
    print('thread 3 start: file listener')
    p3.start()

    while True:
        net.connect_socket()