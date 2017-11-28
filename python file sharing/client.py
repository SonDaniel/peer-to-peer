import socket, os, datetime, json

IP = '192.168.1.8'
MY_IP = '192.168.1.11'
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
    # Try to connect to other ends discovery port 
    my_socket.connect((IP , PORT))

    # Send all data
    my_socket.sendall(json.dumps({
        'ips': localnet_ips,
        'files': json.dumps(hash_files, default=datetime_handler)
        }).encode())
        
    # Recieve data
    data = json.loads(my_socket.recv(1024).decode())



    # Calculate differences
    ips_diff = set(localnet_ips) - set(data['ips'])
    file_diff = get_diff(hash_files, json.loads(data['files']))

    # Send differences
    my_socket.sendall(json.dumps({
        'ips_diff' : ips_diff,
        'file_diff': json.dumps(file_diff, default=datetime_handler)
    }).encode())

    data_diff = json.loads(my_socket.recv(1024).decode())

    ##########################################################
    #                Logic to receive file                   #
    ##########################################################
    for fileName in json.loads(data_diff['file_diff']).keys():
        file_data = my_socket.recv(1024)
        downloadFile = open((FILE_PATH, fileName), 'wb')
        while file_data:
            downloadFile.write(file_data)
            file_data = my_socket.recv(1024)

except socket.error as err:
    print("Discovery Connection to %s:%s failed: %s" % (IP, PORT, err))