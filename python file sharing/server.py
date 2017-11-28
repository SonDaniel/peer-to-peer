import socket, os, datetime, json

IP = '192.168.1.8'
PORT = 3000
FILE_TRANSFER_PORT = 3001
FILE_PATH = '../sync/'
listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
hash_files = {}
localnet_ips = [3,4,5]

def get_diff(obj_1, obj_2):
    diff = {}
    for key in obj_1.keys():
        value = obj_1[key]
        if key not in obj_2.keys():
            diff[key] = value
        else:
            if obj_2[key] != value:
                diff[key] = value

    return diff

def datetime_handler(x):
    if isinstance(x, datetime.datetime):
        return x.isoformat()
    raise TypeError("Unknown type")

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
            data = json.loads(conn.recv(1024).decode())

            print(data)
            print(data['ips'])
            # Send my data to other end
            conn.sendall(json.dumps({
                'ips': localnet_ips,
                'files': json.dumps(hash_files, default=datetime_handler)
            }).encode())

            # Calculate differences
            ips_diff = set(localnet_ips) - set(data['ips'])
            file_diff = get_diff(hash_files, json.loads(data['files']))

            # Receive difference object data from other end
            data_diff = json.loads(conn.recv(1024).decode())

            # Concat difference of IP List
            for diff_ip in data_diff['ips_diff'].keys():
                localnet_ips.append(diff_ip)

            # Send object of difference
            file_conn.sendall(json.dumps({
                'ips_diff': ips_diff,
                'file_diff': json.dumps(file_diff, default=datetime_handler)
            }).encode())

            # create infinite loop to send files, then break when ip_diff and file_diff done
            while True:
                
                for diff_file in json.loads(data_diff['file_diff']).keys():
                    try:
                        ##########################################################
                        #                Logic to send file                      #
                        ##########################################################
                        with open((FILE_PATH, diff_file), 'r') as f:
                            fileRead = f.read(1024)
                            while fileRead:
                                conn.send(fileRead)
                                fileRead = f.read(1024)
                        # Add or overwrite value of data
                        hash_files[diff_file] = data_diff['file_diff'].value(diff_file)
                    except IOError:
                        print('file: ', diff_file, ' not found')
                break


                


            # TODO: need to make logic to disconnect from discover port while letting file port continue
    
        # time.sleep(3)
except socket.error as err:
    # If you cannot bind, exit out of program
    print('Bind failed. Error Code : ' + str(err.errno))