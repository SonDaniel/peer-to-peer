# CECS 327 Networks and Distributed Systems
# Daniel Son
# Anthony Giacalone
# Lab #1: Peer to Peer Networks

# from threading import Thread
import multiprocessing as mp
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

p1 = mp.Process(target=net.listen_socket)
p2 = mp.Process(target=net.connect_socket)
p3 = mp.Process(target=net.get_files)

print('thread 1 start: listen sockets')
p1.start()
print('thread 2 start: connection sockets')
p2.start()
print('thread 3 start: file listener')
p3.start()