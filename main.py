# CECS 327 Networks and Distributed Systems
# Daniel Son
# Anthony Giacalone
# Lab #1: Peer to Peer Networks
from multiprocessing import Process
from network import Network
import os, errno, time

directory = os.path.dirname(file_path)
net = Network()

# Set folder for sync
try:
    # Create folder
    os.makedirs(directory)
except OSError as e:
    # Ignore if folder is there
    net.get_files()
    # Some other error
    if e.errno != errno.EEXIST:
        raise

net.scan_network()

p1 = Process(target=net.listen_socket)
p2 = Process(target=net.connect_socket)
p3 = Process(target=net.get_files)
print('process 1 start: listen sockets')
p1.start()
print('process 2 start: connection sockets')
p2.start()
print('process 3 start: file listener')
p3.start()