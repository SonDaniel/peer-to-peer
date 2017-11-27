import socket, os, datetime

IP = '192.168.1.8'
PORT = 3000
FILE_TRANSFER_PORT = 3001
FILE_PATH = '../sync/'
my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
hash_files = {}
localnet_ips = [1,2,3]

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
    # Try to connect to other ends discovery port 
    my_socket.connect((IP , PORT))

    # Send FILE_TRANSFER_PORT to ip
    my_socket.sendall(str(FILE_TRANSFER_PORT).encode())

    # create file socket
    file_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    file_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        my_socket.recv(1024)
        # try to connect to other end file socket
        file_socket.connect((IP, FILE_TRANSFER_PORT))

        print("connected to %s:%s File Transfer Socket" % (IP, FILE_TRANSFER_PORT))
        
        # Recieve data
        data = file_socket.recv(1024).decode()
        
        # Send all data
        file_socket.sendall(str({
            'ips': localnet_ips,
            'files': hash_files
            }).encode())

        # Calculate differences
        ips_diff = set(localnet_ips) - set(data['ips'])
        file_diff = get_diff(hash_files, data['files'])

        # Send differences
        file_socket.sendall(str({
            'ips_diff' : ips_diff,
            'file_diff': file_diff
        }).encode())

        data_diff = file_socket.recv(1024).decode()

        ##########################################################
        #                Logic to receive file                   #
        ##########################################################
        for fileName in data_diff['file_diff']:
            file_data = file_socket.recv(1024)
            downloadFile = open((FILE_PATH, fileName), 'wb')
            while file_data:
                downloadFile.write(file_data)
                file_data = file_socket.recv(1024)
        

    except socket.error as e:
        print("File Transfer Connection to %s:%s failed: %s" % (IP, FILE_TRANSFER_PORT, e))

except socket.error as err:
    print("Discovery Connection to %s:%s failed: %s" % (IP, PORT, err))