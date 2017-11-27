# CECS 327 Networks and Distributed Systems
# Daniel Son
# Anthony Giacalone
# Lab #1: Peer to Peer Networks

# from threading import Thread
from threading import Thread
from network import Network
import os, errno, time

if __name__ == '__main__':
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
    p1 = Thread(target=net.listen_socket)
    p2 = Thread(target=net.connect_socket)
    p3 = Thread(target=net.get_files)

    print('thread 1 start: listen sockets')
    p1.start()
    print('thread 2 start: connection sockets')
    p2.start()
    print('thread 3 start: file listener')
    p3.start()