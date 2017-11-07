# TODO: Make a description of class and all
import socket, socketserver, subprocess, ipaddress, os, re, multiprocessing

# Support thread if not available 
try:
    import threading
except ImportError:
    import dummy_threading as threading

class Network:
    DISCOVER_PORT = 9000
    FILE_TRANSFER_PORT = 10000
    TIMEOUT = 5  # in seconds
    CONCURRENCY = 100  # how many pings in parallel?

    base_ip = None

    my_ip = None
    my_socket = None

    localnet_ip = None

    threads = []

    # Network Constructor 
    def __init__(self):
        print('Node setup...')
        print('Finding my IP...')
        # Get self IP using Socket Library
        ifconfig_call = subprocess.check_output('ifconfig').decode('utf-8')

        # Regex find and split line with my IP and broadcast IP
        response = re.split(' ', re.findall('.+ broadcast{1} .+', ifconfig_call)[0])

        # First Index is my IP
        self.my_ip = response[1]
        print("Current IP Address: ", self.my_ip)

        # Create IP
        self.base_ip = '.'.join(re.split('\.', self.my_ip)[:-1])
        print("Base IP: ", self.base_ip)

        # Discovering network through ping
        self.ping_network()
        self.scan_network()

    def connect_socket(self, ip):
        self.my_socket = socket.socket()
        self.my_socket.connect((ip, self.DISCOVER_PORT))

    def listen_socket(self):
        return

    def ping_network(self):
        # TODO: Need to optimize ping (use 5 threads)
        # You need to port scan to see if nodes port is open
        # if port is open, add to ip list
        # keep port open, create new thread and new port
        # disconnect connection port and start listening again
        ips = (self.base_ip + '.%d' % i for i in range(1, 255))

        with multiprocessing.Pool(self.CONCURRENCY) as p:
            p.map(self.ping, ips)

    def ping(self, ip):
        subprocess.call(
            ['ping', '-W', str(self.TIMEOUT), '-c', '1', ip],
            stdout=subprocess.DEVNULL)

    def scan_network(self):
        # discover online IP's after ping
        arp_output = subprocess.check_output(['arp', '-a']).decode('utf-8')
        
        online_ip = []

        # Regex for 192.168.-, 10.0.-, 172.16.-
        for ip in re.findall('(192\.168\.\d*\.\d*)|(10\.0\.\d*\.\d*)|(172\.16\.\d*\.\d*)', arp_output):
            # Remove empty string from tuple
            online_ip.append(list(filter(None, ip))[0])

        # Make List unique (duplicate IPs)
        online_ip = list(set(online_ip))

        print(online_ip)