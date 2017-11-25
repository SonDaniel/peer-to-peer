# TODO: Make a description of class and all
import socket, socketserver, subprocess, ipaddress, os, re
import multiprocessing, sys, _thread, json, datetime, time

class Network:
    DISCOVER_PORT = 9000
    FILE_TRANSFER_PORT = 10000
    TIMEOUT = 5  # in seconds
    CONCURRENCY = 100  # how many pings in parallel?
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
            # Get list of file directory
            files = os.listdir(self.FILE_PATH)
            
            # Go through each file and get stats
            for x in files:
                # Get stats for file
                stats = os.stat((self.FILE_PATH + '/' + x))
                # save file stats
                self.hash_files[x] = datetime.datetime.fromtimestamp(stats.st_mtime)

            # Sleep process for 5 seconds
            time.sleep(5)

    def get_diff(obj_1, obj_2):
        diff = {}
        for key in obj_1.keys():
            value = obj_1[key]
            if key not in a:
                diff[key] = value
            else:
                if a[key] != value:
                    diff[key] = value

        return diff


    def create_socket(self):
        try:
            return socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as err:
            print("socket creation failed with error %s" %(err))
            return None

    def connect_socket(self):
        # Initialize discovery socket
        self.discover_socket = self.create_socket()

        # infinite loop to listen for local IPs
        while True:
            print('connect_socket running')
            # loop through list to see if connection works
            for x in self.localnet_ips:
                try:
                    # Try to connect to other ends discovery port 
                    self.discover_socket.connect((x, self.DISCOVER_PORT))
                    print("Connected to %s:%s" % (x, self.DISCOVER_PORT))

                    # Send FILE_TRANSFER_PORT to ip
                    self.discover_socket.sendall(str(self.FILE_TRANSFER_PORT).encode())

                    # create file socket
                    file_socket = self.create_socket()

                    try:
                        # try to connect to other end file socket
                        file_socket.connect((x, self.FILE_TRANSFER_PORT))

                        print("connected to %s:%s File Transfer Socket" % (x, self.FILE_TRANSFER_PORT))
                        self.FILE_TRANSFER_PORT = self.FILE_TRANSFER_PORT + 1

                        # Send all data
                        file_socket.sendall(str({
                            'ips': self.localnet_ips,
                            'files': self.hash_files
                            }).encode())

                        # Recieve data
                        data = json(file_socket.recv(1024))

                        # Calculate differences
                        ips_diff = set(self.localnet_ips) - set(data['ips'])
                        file_diff = self.get_diff(self.hash_files, data['files'])

                        # Send differences
                        file_socket.sendall(str({
                            'ips_diff' : ips_diff,
                            'file_diff': file_diff
                        }))

                        data_diff = json(file_socket.recv(1024))

                        ##########################################################
                        #                Logic to receive file                   #
                        ##########################################################
                        for fileName in data_diff['file_diff']:
                            file_data = file_socket.recv(1024)
                            downloadFile = open((self.FILE_PATH, fileName), 'wb')
                            while file_data:
                                downloadFile.write(file_data)
                                file_data = file_socket.recv(1024)
                        

                    except socket.error as e:
                        print("Connection to %s:%s failed: %s" % (x, self.FILE_TRANSFER_PORT, e))

                except socket.error as err:
                    print("Connection to %s:%s failed: %s" % (x, self.DISCOVER_PORT, err))

            # TODO: Debug this section if delay actually happens 
            # Delay by 3 seconds 
            time.sleep(3)

    def listen_socket(self):
        # Initialize listener socket
        self.listen_socket = self.create_socket()

        while True:
            print('listen_socket running')
            try:
                # Bind socket to listen to own IP
                self.listen_socket.bind((self.my_ip, self.DISCOVER_PORT))
            except socket.error as err:
                # If you cannot bind, exit out of program
                print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])

            # Start listening for connections
            # Integer means to allow up to x un-accept()ed incoming TCP connections
            # to be queued up by the TCP stack at the same time
            self.listen_socket.listen(2)

            # While loop keeps waiting for connection
            while 1:
                # Wait for connection to be accepted
                conn, addr = self.listen_socket.accept()
                print('Connected Listener Protocol with ' + addr[0] + ':' + str(addr[1]))

                with conn:
                    # get file port number from other end
                    file_port = int(conn.recv(1024).decode())

                # Listener port will create file socket to persist
                file_socket = self.create_socket()
                file_socket.bind((self.my_ip, file_port))

                file_socket.listen(1)

                while 1:
                    # accept connection from other end
                    file_conn, file_addr = file_socket.accept()
                    print('Connected File Protocol with ' + addr[0] + ':' + str(add[1]))

                    with file_conn:
                        # Recieve data from other end
                        data = json(file_conn.recv(1024).decode())

                        # Send my data to other end
                        file_conn.sendall(str({
                            'ips': self.localnet_ips,
                            'files': self.hash_files
                        }).encode())

                        # Calculate differences
                        ips_diff = set(self.localnet_ips) - set(data['ips'])
                        file_diff = self.get_diff(self.hash_files, data['files'])

                        # Receive difference object data from other end
                        data_diff = json(file_conn.recv(1024).decode())

                        # Concat difference of IP List
                        for diff_ip in data_diff['ips_diff'].keys():
                            self.localnet_ips.append(diff_ip)

                        # Send object of difference
                        file_conn.sendall(str({
                            'ips_diff': ips_diff,
                            'file_diff': file_diff
                        }))

                        # create infinite loop to send files, then break when ip_diff and file_diff done
                        while True:
                            
                            for diff_file in data_diff['file_diff']:
                                try:
                                    ##########################################################
                                    #                Logic to send file                      #
                                    ##########################################################
                                    with open((self.FILE_PATH, diff_file), 'r') as f:
                                        fileRead = f.read(1024)
                                        while fileRead:
                                            file_conn.send(fileRead)
                                            fileRead = f.read(1024)
                                    # Add or overwrite value of data
                                    self.hash_files[diff_file] = data_diff['file_diff'].value(diff_file)
                                except IOError:
                                    print('file: ', diff_file, ' not found')
                            break


                        


                    # TODO: need to make logic to disconnect from discover port while letting file port continue
            
            s.close()

    # def client_connection_thread(conn):
    #     # Infinite loop so thread does not end
    #     while True:
    #         #Receiving from client
    #         data = conn.recv(1024)

    #         # reply = 'OK...' + data
    #         if data == -1:
    #             break
        
    #         # conn.sendall(reply)
        
    #     #came out of loop
    #     conn.close()

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
