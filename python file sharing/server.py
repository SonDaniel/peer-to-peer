import socket, os, datetime, pickle

IP = '10.0.1.2'
PORT = 5000
FILE_TRANSFER_PORT = 5000
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

    print(hash_files)

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
            data = pickle.loads(conn.recv(1024))


            # Send my data to other end
            conn.sendall(pickle.dumps({
                'ips': localnet_ips,
                'files': pickle.dumps(hash_files)
            }))

            # Calculate differences
            ips_diff = set(localnet_ips) - set(data['ips'])
            file_diff = get_diff(hash_files, pickle.loads(data['files']))

            print('ips_diff is: {0}'.format(ips_diff))
            print('file_diff is: {0}'.format(file_diff))

            # Receive difference object data from other end
            data_diff = pickle.loads(conn.recv(1024))

            print('data_diff is: {0}'.format(data_diff))
            print(pickle.loads(data_diff['file_diff']))

            # Concat difference of IP List
            for diff_ip in data_diff['ips_diff']:
                localnet_ips.append(diff_ip)

            print('localnet ip is: {0}'.format(localnet_ips))
            # Send object of difference
            conn.sendall(pickle.dumps({
                'ips_diff': ips_diff,
                'file_diff': pickle.dumps(file_diff)
            }))

            print('sent')

            # create infinite loop to send files, then break when ip_diff and file_diff done
            while True:
                for diff_file in file_diff:
                    print(diff_file)
                    ##########################################################
                    #                Logic to send file                      #
                    ##########################################################
                    fileWriter = open((FILE_PATH + diff_file), 'rb+')
                    fileRead = fileWriter.read(1024)
                    print(fileRead)
                    while fileRead:
                        conn.send(fileRead)
                        fileRead = fileWriter.read(1024)
                    fileWriter.close()
                    # Add or overwrite value of data
                    hash_files[diff_file] = file_diff[diff_file]
                break


                


            # TODO: need to make logic to disconnect from discover port while letting file port continue
    
        # time.sleep(3)
except socket.error as err:
    # If you cannot bind, exit out of program
    print('Bind failed. Error Code : ' + str(err.errno))