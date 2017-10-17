import socket, socketserver, subprocess, ipaddress

# Support thread if not available 
try:
    import threading
except ImportError:
    import dummy_threading as threading

class Network:
    # Network Address 
    broadcast_ip = None
    ip_net = None
    all_hosts = None
    my_ip = None
    my_socket = None

    localnet_ip = None
    port_number = None

    threads = []

    # Network Constructor 
    def __init__(self):
        print('Node setup...')
        # Get self IP using Socket Library
        self.my_ip = socket.gethostbyname(socket.getfqdn())
        print("Current IP Address: ", self.my_ip)

        # Create network
        self.broadcast_ip = ipaddress.inet_ntoa( inet_aton(self.my_ip)[:3] + b'\xff')
        print('Broadcast IP: ', self.broadcast_ip)

        # self.ip_net = ipaddress.ip_network(self.net_addr)
        # # Get all hosts on the network 
        # self.all_hosts = list(self.ip_net.hosts())

    def connect_socket(self):
        self.my_socket = socket.socket()
        self.my_socket.connect((self.localnet_ip,self.port_number))