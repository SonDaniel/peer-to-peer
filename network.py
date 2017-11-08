# TODO: Make a description of class and all
import socket, socketserver, subprocess, ipaddress, os, re, multiprocessing, sys
import thread

class Network:
    DISCOVER_PORT = 9000
    FILE_TRANSFER_PORT = 10000
    TIMEOUT = 5  # in seconds
    CONCURRENCY = 100  # how many pings in parallel?

    base_ip = None
    my_ip = None

    listen_socket = None
    discover_socket = None
    file_socket = None
    localnet_ips = None

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

    def create_socket(self):
        try:
            return socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print "Socket successfully created"
        except socket.error as err:
            print "socket creation failed with error %s" %(err)
            return None

    def connect_socket(self, ip):
        self.discover_socket = self.create_socket()
        while True:
            # loop through list to see if connection works
            for x in self.localnet_ips:
                try:
                    self.discover_socket.connect((x, self.DISCOVER_PORT))
                    print("Connected to %s:%s" % (x, self.DISCOVER_PORT))
                    return True
                except socket.error as err:
                    print("Connection to %s:%s failed: %s" % (x, self.DISCOVER_PORT, err))
                    return False
                

            time.sleep(3)

    def listen_socket(self):
        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.listen_socket.bind(self.my_ip, self.DISCOVER_PORT)
        except socket.error as err:
            print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
            sys.exit()
        # Start listening for connections
        self.listen_socket.listen()
        #now keep talking with the client
        while 1:
            # Wait for connection
            conn, addr = self.listen_socket.accept()
            print('Connected with ' + addr[0] + ':' + str(addr[1]))
            
            #start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
            thread.start_new_thread(client_connection_thread, (conn))
        
        s.close()

        def client_connection_thread(conn):
            # Infinite loop so thread does not end
            while True:
                #Receiving from client
                data = conn.recv(1024)
                # reply = 'OK...' + data
                if data === -1:
                    break
            
                # conn.sendall(reply)
            
            #came out of loop
            conn.close()

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
        self.localnet_ips = list(set(online_ip))