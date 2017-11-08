# CECS 327 Networks and Distributed Systems
# Daniel Son
# Anthony Giacalone
# Lab #1: Peer to Peer Networks
from multiprocessing import Process
from network import Network
import os, errno, time

file_path = "./sync/"
directory = os.path.dirname(file_path)

# Set folder for sync
try:
    # Create folder
    os.makedirs(directory)
except OSError as e:
    # Ignore if folder is there
    if e.errno != errno.EEXIST:
        raise

net = Network()

# p1 = Process(target=net.scan_network())
# p2 = Process(target=net.connect_socket())
# while True:
#     p1.start()
#     p2.start()
