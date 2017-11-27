import socket, os, datetime

IP = '192.168.1.8'
PORT = 10000
FILE_TRANSFER_PORT = 10001
FILE_PATH = '../sync/'
listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
hash_files = {}
localnet_ips = [3,4,5]

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

def get_files():
    print('get_files function running.')
    # Get list of file directory
    files = os.listdir(FILE_PATH)
    
    # Go through each file and get stats
    for x in files:
        # Get stats for file
        stats = os.stat((FILE_PATH + '/' + x))
        # save file stats
        hash_files[x] = datetime.datetime.fromtimestamp(stats.st_mtime)

get_files()

try:
    # Bind socket to listen to own IP
    listen_socket.bind((IP, PORT))

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
            # get file port number from other end
            file_port = int(conn.recv(1024).decode())

        # Listener port will create file socket to persist
        file_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        file_socket.bind((IP, file_port))

        file_socket.listen(1)

        while True:
            # accept connection from other end
            file_conn, file_addr = file_socket.accept()
            print('Connected File Protocol with ' + addr[0] + ':' + str(addr[1]))

            with file_conn:
                # Recieve data from other end
                data = json.dumps(file_conn.recv(1024).decode())

                # Send my data to other end
                file_conn.sendall(str({
                    'ips': localnet_ips,
                    'files': hash_files
                }).encode())

                # Calculate differences
                ips_diff = set(localnet_ips) - set(data['ips'])
                file_diff = get_diff(hash_files, data['files'])

                # Receive difference object data from other end
                data_diff = json.dumps(file_conn.recv(1024).decode())

                # Concat difference of IP List
                for diff_ip in data_diff['ips_diff'].keys():
                    localnet_ips.append(diff_ip)

                # Send object of difference
                file_conn.sendall(str({
                    'ips_diff': ips_diff,
                    'file_diff': file_diff
                }).encode())

                # create infinite loop to send files, then break when ip_diff and file_diff done
                while True:
                    
                    for diff_file in data_diff['file_diff']:
                        try:
                            ##########################################################
                            #                Logic to send file                      #
                            ##########################################################
                            with open((FILE_PATH, diff_file), 'r') as f:
                                fileRead = f.read(1024)
                                while fileRead:
                                    file_conn.send(fileRead)
                                    fileRead = f.read(1024)
                            # Add or overwrite value of data
                            hash_files[diff_file] = data_diff['file_diff'].value(diff_file)
                        except IOError:
                            print('file: ', diff_file, ' not found')
                    break


                


            # TODO: need to make logic to disconnect from discover port while letting file port continue
    
        time.sleep(3)
except socket.error as err:
    # If you cannot bind, exit out of program
    print('Bind failed. Error Code : ' + str(err.errno))