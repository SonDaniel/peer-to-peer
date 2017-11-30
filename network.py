# TODO: Make a description of class and all
import socket, socketserver, subprocess, ipaddress, os, re
import multiprocessing, sys, datetime, time, pickle
import threading

class Network:
    DISCOVER_PORT = 5000
    FILE_TRANSFER_PORT = 6000
    TIMEOUT = 5  # in seconds
    CONCURRENCY = 100  # how many pings in parallel
    FILE_PATH = './sync/'
    base_ip = None
    my_ip = None

    listen_socket = None
    discover_socket = None
    file_socket = None
    localnet_ips = None

    hash_files = {}

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

    def get_files(self):
        while True:
            print('get_files function running.')
            # walk through folder
            for root, subdirs, files in os.walk(self.FILE_PATH):
                for x in files:
                    # get stats of file
                    stats = os.stat((root + '/' + x))

                    # append file with its modified time as a datetime
                    self.hash_files[(root.replace(self.FILE_PATH, '') + '/' + x)] = datetime.datetime.fromtimestamp(stats.st_mtime)

            # Sleep process for 5 seconds
            time.sleep(5)

    def get_diff(self, obj_1, obj_2):
        diff = {}
        for key in obj_1.keys():
            value = obj_1[key]
            if key not in obj_2.keys():
                diff[key] = value
            else:
                if obj_2[key] != value:
                    diff[key] = value

        return diff

    def create_socket(self):
        try:
            create_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            create_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            return create_socket
        except socket.error as err:
            print("socket creation failed with error %s" %(err))
            return None

    def connect_socket(self):
        while True:
            print(self.localnet_ips)
            for ip in self.localnet_ips:
                try:
                    my_socket = self.create_socket()
                    my_socket.settimeout(3)
                    # Try to connect to other ends discovery port 
                    my_socket.connect((ip, self.DISCOVER_PORT))
                    # Send all data
                    my_socket.sendall(pickle.dumps({
                        'ips': self.localnet_ips,
                        'files': pickle.dumps(self.hash_files)
                        }))
                        
                    # Recieve data
                    data = pickle.loads(my_socket.recv(1024))



                    # Calculate differences
                    ips_diff = set(self.localnet_ips) - set(data['ips'])
                    file_diff = self.get_diff(self.hash_files, pickle.loads(data['files']))

                    print('ips_diff is: {0}'.format(ips_diff))
                    print('file_diff is: {0}'.format(file_diff))

                    # Send differences
                    my_socket.sendall(pickle.dumps({
                        'ips_diff' : ips_diff,
                        'file_diff': pickle.dumps(file_diff)
                    }))

                    data_diff = pickle.loads(my_socket.recv(1024))

                    # Concat difference of IP List
                    for diff_ip in data_diff['ips_diff']:
                        self.localnet_ips.append(diff_ip)

                    print('data_diff is: {0}'.format(data_diff))

                    ##########################################################
                    #                Logic to receive file                   #
                    ##########################################################
                    for fileName in pickle.loads(data_diff['file_diff']):
                        file_socket = self.create_socket()
                        file_socket.connect((ip, self.FILE_TRANSFER_PORT))
                        fileWriter = open((self.FILE_PATH + fileName), 'wb+')
                        file_data = file_socket.recv(1024)
                        while file_data:
                            fileWriter.write(file_data)
                            file_data = file_socket.recv(1024)
                        fileWriter.close()
                        file_socket.close()


                    print('All files saved.')
                    ##########################################################
                    #                Logic to send file                      #
                    ##########################################################
                    for diff_file in file_diff:
                        file_socket = self.create_socket()
                        file_socket.bind((self.my_ip, self.FILE_TRANSFER_PORT))
                        file_socket.listen(1)
                        file_conn, file_addr = file_socket.accept()
                        fileWriter = open((self.FILE_PATH + diff_file), 'rb+')
                        fileRead = fileWriter.read(1024)
                        while fileRead:
                            file_conn.send(fileRead)
                            fileRead = fileWriter.read(1024)
                        fileWriter.close()
                        file_conn.close()
                        # Add or overwrite value of data
                        self.hash_files[diff_file] = file_diff[diff_file]

                    print('Files sent.')

                    my_socket.close()
                except socket.error as err:
                    print("Discovery Connection to %s:%s failed: %s" % (ip, self.DISCOVER_PORT, err))

                time.sleep(3)

    def listen_socket(self):
        try:
            listen_socket = self.create_socket()
            # Bind socket to listen to own IP
            listen_socket.bind((self.my_ip, self.DISCOVER_PORT))

            # Start listening for connections
            # Integer means to allow up to x un-accept()ed incoming TCP connections
            listen_socket.listen(1)

            # While loop keeps waiting for connection
            while True:
                print('listen_socket running')
                # Wait for connection to be accepted
                conn, addr = listen_socket.accept()
                print('Connected Listener Protocol with ' + addr[0] + ':' + str(addr[1]))

                with conn:
                    data = pickle.loads(conn.recv(1024))


                    # Send my data to other end
                    conn.sendall(pickle.dumps({
                        'ips': self.localnet_ips,
                        'files': pickle.dumps(self.hash_files)
                    }))

                    # Calculate differences
                    ips_diff = set(self.localnet_ips) - set(data['ips'])
                    file_diff = self.get_diff(self.hash_files, pickle.loads(data['files']))

                    print('ips_diff is: {0}'.format(ips_diff))
                    print('file_diff is: {0}'.format(file_diff))

                    # Receive difference object data from other end
                    data_diff = pickle.loads(conn.recv(1024))

                    print('data_diff is: {0}'.format(data_diff))
                    print(pickle.loads(data_diff['file_diff']))

                    # Concat difference of IP List
                    for diff_ip in data_diff['ips_diff']:
                        self.localnet_ips.append(diff_ip)

                    print('localnet ip is: {0}'.format(self.localnet_ips))

                    # Send object of difference
                    conn.sendall(pickle.dumps({
                        'ips_diff': ips_diff,
                        'file_diff': pickle.dumps(file_diff)
                    }))

                    ##########################################################
                    #                Logic to send file                      #
                    ##########################################################
                    for diff_file in file_diff:
                        file_socket = self.create_socket()
                        file_socket.bind((self.my_ip, self.FILE_TRANSFER_PORT))
                        file_socket.listen(1)
                        file_conn, file_addr = file_socket.accept()
                        fileWriter = open((self.FILE_PATH + diff_file), 'rb+')
                        fileRead = fileWriter.read(1024)
                        while fileRead:
                            file_conn.send(fileRead)
                            fileRead = fileWriter.read(1024)
                        fileWriter.close()
                        file_conn.close()
                        # Add or overwrite value of data
                        self.hash_files[diff_file] = file_diff[diff_file]

                    print('All files sent. Receiving files....')
                    time.sleep(2)
                    ##########################################################
                    #                Logic to receive file                   #
                    ##########################################################
                    for fileName in pickle.loads(data_diff['file_diff']):
                        file_socket = self.create_socket()
                        file_socket.connect((addr[0], self.FILE_TRANSFER_PORT))
                        fileWriter = open((self.FILE_PATH + fileName), 'wb+')
                        file_data = file_socket.recv(1024)
                        while file_data:
                            fileWriter.write(file_data)
                            file_data = file_socket.recv(1024)
                        fileWriter.close()
                        file_socket.close()

                    print('Files received.')

        except socket.error as err:
            # If you cannot bind, exit out of program
            print('Bind failed. Error Code : {0}'.format(err))

    def ping_network(self):
        # create range of ips from base ip - 1:255
        ips = (self.base_ip + '.%d' % i for i in range(1, 255))

        # Create multiprocessing pool that pings
        with multiprocessing.Pool(self.CONCURRENCY) as p:
            p.map(self.ping, ips)

    def ping(self, ip):
        # create subprocess that pings at certain ips
        subprocess.call(
            ['ping', '-W', str(self.TIMEOUT), '-c', '1', ip],
            stdout=subprocess.DEVNULL)

    def scan_network(self):
        # discover online IP's after ping
        arp_output = subprocess.check_output(['arp', '-a']).decode('utf-8')
        online_ip = []
        
        # Regex for 192.168.-, 10.0.-, 172.16.- with mac address
        for ip in re.findall('((192\.168\.\d*\.\d*)|(10\.\d*\.\d*\.\d*)|(172\.16\.\d*\.\d*))(\W*)(at\W)(.{1,2}:.{1,2}:.{1,2}:.{1,2}:.{1,2}:.{1,2})', arp_output):
            # do not save my IP in list
            stripped_ip = list(filter(None, ip))[0]
            
            if stripped_ip != self.my_ip:
                # Remove empty string from tuple
                online_ip.append(stripped_ip)
                    
        # Make List unique (duplicate IPs)
        self.localnet_ips = list(set(online_ip))
