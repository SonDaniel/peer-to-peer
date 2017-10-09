import socket, socketserver, subprocess, ipaddress
try:
    import threading
except ImportError:
    import dummy_threading as threading

class Network:
    # Network Address 
    net_addr = '192.168.1.0/24'
    ip_net = None
    all_hosts = None
    ip_address = None

    # Network Constructor 
    def __init__(self):
        # Get self IP 
        ip_address = socket.gethostbyname(socket.getfqdn())

        # Create network
        ip_net = ipaddress.ip_network(net_addr)
        # Get all hosts on the network 
        all_hosts = list(ip_net.hosts())

    # Scan network based off net_addr
    def scan_network():
        for i in range(len(all_hosts)):
            output = subprocess.Popen(['ping', '-n', '1', '-w', '500', str(all_hosts[i])], stdout=subprocess.PIPE, startupinfo=info).communicate()[0]
            # TO DO: ping each hosts, if online, then do something