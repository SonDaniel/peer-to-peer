# TODO: Make a description of class and all
import socket, socketserver, subprocess, ipaddress, os, re
import multiprocessing, sys, time, pickle
import threading

class Network:
    """Global variables:
    - DISCOVERY_PORT -- Port used for discovery to other nodes.
    - FILE_TRANSFER_PORT -- Port used to transfer files to other nodes.
    - TIMEOUT -- Integer used to set time out for socket or subprocess (seconds)
    - CONCURRENCY -- Integer how many pings in parallel
    - FILE_PATH -- path of sync folder
    - base_ip -- the core ip
    - my_ip -- current computer's ip
    - localnet_ips -- an Array of IP strings
    - hash_files -- object key/value. key: string of file name. value: modified time
    """
    DISCOVER_PORT = 5000
    FILE_TRANSFER_PORT = 6000
    TIMEOUT = 5  # in seconds
    CONCURRENCY = 100  # how many pings in parallel
    FILE_PATH = './sync/'
    base_ip = None
    my_ip = None

    localnet_ips = None
    hash_files = {}

    # Network Constructor 
    def __init__(self):
        """constructor of the network class."""
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
                    self.hash_files[(root.replace(self.FILE_PATH, '') + '/' + x)] = stats.st_mtime

            print(self.hash_files)
            # Sleep process for 5 seconds
            time.sleep(5)

    def get_diff(self, obj_1, obj_2):
        """
        gets obj_1 and compares key and value with obj_2.

        returns difference of what obj_2 does not have of obj_1
        """
        diff = {}
        for key in obj_1.keys():
            value = obj_1[key]
            if key not in obj_2.keys():
                diff[key] = value
            else:
                if obj_2[key] != value:
                    diff[key] = value

        return diff

    def make_dirs(self, path):
        """
        Gets path and creates sub directory. Ignored creation if directory exists.
        """
        result = re.search('^(.+)\/([^/]+)$', path)
        if result:
            try:
                os.makedirs(self.FILE_PATH + result.group(1))
            except:
                print('directory exists.')

    def create_socket(self):
        """
        Creates socket object and returns socket.
        """
        try:
            create_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            create_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            return create_socket
        except socket.error as err:
            print("socket creation failed with error %s" %(err))
            return None

    def connect_socket(self):
        """
        Goes through list of IPs and tries to connect.
        If connection is successful, IP list and hash_file are sent to each other.
        Differences are returned and file sharing occurs.
        """
        while True:
            for ip in self.localnet_ips:
                try:
                    # Create socket
                    my_socket = self.create_socket()
                    # Set timeout so no blocking occurs
                    my_socket.settimeout(self.TIMEOUT)

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

                    # Send differences
                    my_socket.sendall(pickle.dumps({
                        'ips_diff' : ips_diff,
                        'file_diff': pickle.dumps(file_diff)
                    }))

                    # Receive data difference
                    data_diff = pickle.loads(my_socket.recv(1024))

                    # Concat difference of IP List
                    for diff_ip in data_diff['ips_diff']:
                        self.localnet_ips.append(diff_ip)

                    ##########################################################
                    #                START: Logic to receive file            #
                    ##########################################################
                    for fileName in pickle.loads(data_diff['file_diff']):
                        # Create sub-directories if needed
                        self.make_dirs(fileName)

                        # Create file socket
                        file_socket = self.create_socket()
                        file_socket.connect((ip, self.FILE_TRANSFER_PORT))

                        # Create/Open file
                        fileWriter = open((self.FILE_PATH + fileName), 'wb+')

                        # Grab data and write until done
                        file_data = file_socket.recv(1024)
                        while file_data:
                            fileWriter.write(file_data)
                            file_data = file_socket.recv(1024)
                        
                        # Close file opener and file_socket
                        fileWriter.close()
                        file_socket.close()
                    ##########################################################
                    #               END: Logic to receive file               #
                    ##########################################################

                    print('All files saved.')
                    ##########################################################
                    #                START: Logic to send file               #
                    ##########################################################
                    for diff_file in file_diff:
                        # Create file socket
                        file_socket = self.create_socket()
                        file_socket.bind((self.my_ip, self.FILE_TRANSFER_PORT))
                        file_socket.listen(1)

                        # wait for connection
                        file_conn, file_addr = file_socket.accept()

                        # open file to send
                        fileWriter = open((self.FILE_PATH + diff_file), 'rb+')

                        # read data and send file until done
                        fileRead = fileWriter.read(1024)
                        while fileRead:
                            file_conn.send(fileRead)
                            fileRead = fileWriter.read(1024)

                        # Close file opener and file_socket
                        fileWriter.close()
                        file_conn.close()

                        # Add or overwrite value of data
                        self.hash_files[diff_file] = file_diff[diff_file]
                    ##########################################################
                    #                 END: Logic to send file                #
                    ##########################################################
                    print('Files sent.')

                    # Close discovery socket
                    my_socket.close()

                except socket.error as err:
                    print("Discovery Connection to %s:%s failed: %s" % (ip, self.DISCOVER_PORT, err))

                # Sleep discovery socket thread for 3 seconds
                time.sleep(3)

    def listen_socket(self):
        """
        Listen to my IP with discovery port.
        If connection happens, exchange IP list and hash_files.
        Get differences and start file sharing.
        """
        try:
            # Create listener socket
            listen_socket = self.create_socket()

            # Bind socket to listen to own IP
            listen_socket.bind((self.my_ip, self.DISCOVER_PORT))

            # Start listening for connections
            listen_socket.listen(1)

            # While loop keeps waiting for connection
            while True:
                print('listen_socket running')
                # Wait for connection to be accepted
                conn, addr = listen_socket.accept()
                print('Connected Listener Protocol with ' + addr[0] + ':' + str(addr[1]))

                with conn:
                    # get data from other side
                    data = pickle.loads(conn.recv(1024))

                    # Send my data to other end
                    conn.sendall(pickle.dumps({
                        'ips': self.localnet_ips,
                        'files': pickle.dumps(self.hash_files)
                    }))

                    # Calculate differences
                    ips_diff = set(self.localnet_ips) - set(data['ips'])
                    file_diff = self.get_diff(self.hash_files, pickle.loads(data['files']))

                    # Receive difference object data from other end
                    data_diff = pickle.loads(conn.recv(1024))

                    # Concat difference of IP List
                    for diff_ip in data_diff['ips_diff']:
                        self.localnet_ips.append(diff_ip)

                    # Send object of difference
                    conn.sendall(pickle.dumps({
                        'ips_diff': ips_diff,
                        'file_diff': pickle.dumps(file_diff)
                    }))

                    ##########################################################
                    #                START: Logic to send file               #
                    ##########################################################
                    for diff_file in file_diff:
                        # create file_socket
                        file_socket = self.create_socket()
                        file_socket.bind((self.my_ip, self.FILE_TRANSFER_PORT))
                        file_socket.listen(1)

                        # wait for connection
                        file_conn, file_addr = file_socket.accept()

                        # open file and read and send file until done
                        fileWriter = open((self.FILE_PATH + diff_file), 'rb+')
                        fileRead = fileWriter.read(1024)
                        while fileRead:
                            file_conn.send(fileRead)
                            fileRead = fileWriter.read(1024)

                        # close file opener and file_socket
                        fileWriter.close()
                        file_conn.close()
                        # Add or overwrite value of data
                        self.hash_files[diff_file] = file_diff[diff_file]
                    ##########################################################
                    #                END: Logic to send file                 #
                    ##########################################################

                    print('All files sent. Receiving files....')
                    time.sleep(2)
                    ##########################################################
                    #               START: Logic to receive file             #
                    ##########################################################
                    for fileName in pickle.loads(data_diff['file_diff']):
                        # create sub-directory if needed
                        self.make_dirs(fileName)

                        # create file_socket
                        file_socket = self.create_socket()
                        file_socket.connect((addr[0], self.FILE_TRANSFER_PORT))

                        # open file and read and send file until done
                        fileWriter = open((self.FILE_PATH + fileName), 'wb+')
                        file_data = file_socket.recv(1024)
                        while file_data:
                            fileWriter.write(file_data)
                            file_data = file_socket.recv(1024)

                        # close file opener and socket
                        fileWriter.close()
                        file_socket.close()
                    ##########################################################
                    #               END: Logic to receive file               #
                    ##########################################################
                    print('Files received.')

        except socket.error as err:
            print('Bind failed. Error Code : {0}'.format(err))

    def ping_network(self):
        """
        Pings network range from 1 - 255 using multiprocessors.
        """
        # create range of ips from base ip - 1:255
        ips = (self.base_ip + '.%d' % i for i in range(1, 255))

        # Create multiprocessing pool that pings
        with multiprocessing.Pool(self.CONCURRENCY) as p:
            # map each ip to processor of the function ping
            p.map(self.ping, ips)

    def ping(self, ip):
        """
        creates a sub-processor and pings given ip with given timeout.
        """
        # create subprocess that pings at certain ips
        subprocess.call(
            ['ping', '-W', str(self.TIMEOUT), '-c', '1', ip],
            stdout=subprocess.DEVNULL)

    def scan_network(self):
        """
        Creates subprocessor to call command arp -a.
        Using regex, find all the IPs specified.
        Strip any white spaces and save in localnet_ip.
        """
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
