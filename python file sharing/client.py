import socket, os, datetime

IP = '192.168.1.8'
PORT = 10000
FILE_TRANSFER_PORT = 10001
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

    try:
        # try to connect to other end file socket
        while True:
            code = file_socket.connect_ex((IP, FILE_TRANSFER_PORT))
            if code == 0:
                break

        print("connected to %s:%s File Transfer Socket" % (x, FILE_TRANSFER_PORT))
        FILE_TRANSFER_PORT = FILE_TRANSFER_PORT + 1

        # Send all data
        file_socket.sendall(str({
            'ips': localnet_ips,
            'files': hash_files
            }).encode())

        # Recieve data
        data = json.dumps(file_socket.recv(1024).decode())

        # Calculate differences
        ips_diff = set(localnet_ips) - set(data['ips'])
        file_diff = get_diff(hash_files, data['files'])

        # Send differences
        file_socket.sendall(str({
            'ips_diff' : ips_diff,
            'file_diff': file_diff
        }).encode())

        data_diff = json.dumps(file_socket.recv(1024).decode())

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