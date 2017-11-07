# CECS 327 Networks and Distributed Systems
# Daniel Son
# Anthony Giacalone
# Lab #1: Peer to Peer Networks

from network import Network
import os, errno

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
