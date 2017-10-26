import socket, socketserver, subprocess, ipaddress, os, re

# Support thread if not available 
try:
    import threading
except ImportError:
    import dummy_threading as threading

class Network:
    DISCOVER_PORT = 9000
    FILE_TRANSFER_PORT = 10000

    # Network Address 
    # 10.0.0.0/8 : figure out in lab
    # 192.168.0.0/16 : 0/24
    network_range = ''
    ip_net = None
    all_hosts = None
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

        # Create network
        base_ip = '.'.join(re.split('\.', self.my_ip)[:-1])
        self.network_range = base_ip + '.0/24'
        print("Network Range: ", self.network_range)
        self.ip_net = ipaddress.ip_network(self.network_range)

        # Get all hosts on the network 
        self.all_hosts = list(self.ip_net.hosts())

    def connect_socket(self):
        self.my_socket = socket.socket()
        self.my_socket.connect((self.localnet_ip,self.port_number))

    def scan_network(self):
        # TODO: Need to optimize ping (use threads?)
        # network_list = list(ipaddress.ip_network(self.network_range).hosts())
        # For each IP address in the subnet, 
        # run the ping command with subprocess.popen interface
        # for i in range(len(self.all_hosts)):
        #     with open(os.devnull, "w") as f:
        #         subprocess.call(['ping', '-c', '1', '-W', '1', str(self.all_hosts[i])], stdout=f)

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