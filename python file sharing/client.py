import socket, os, datetime, json, pickle

IP = '192.168.1.8'
MY_IP = '192.168.1.11'
PORT = 5000
FILE_TRANSFER_PORT = 8000
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

    print(hash_files)

get_files()

try:
    # Try to connect to other ends discovery port 
    my_socket.connect((IP , PORT))

    # Send all data
    my_socket.sendall(pickle.dumps({
        'ips': localnet_ips,
        'files': pickle.dumps(hash_files)
        }))
        
    # Recieve data
    data = pickle.loads(my_socket.recv(1024))



    # Calculate differences
    ips_diff = set(localnet_ips) - set(data['ips'])
    file_diff = get_diff(hash_files, pickle.loads(data['files']))

    print('ips_diff is: {0}'.format(ips_diff))
    print('file_diff is: {0}'.format(file_diff))

    # Send differences
    my_socket.sendall(pickle.dumps({
        'ips_diff' : ips_diff,
        'file_diff': pickle.dumps(file_diff)
    }))

    data_diff = pickle.loads(my_socket.recv(1024))
    my_socket.close()
    print('data_diff is: {0}'.format(data_diff))

    ##########################################################
    #                Logic to receive file                   #
    ##########################################################
    for fileName in pickle.loads(data_diff['file_diff']):
        file_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        file_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        file_socket.connect((IP, FILE_TRANSFER_PORT))

        print(fileName)
        fileWriter = open((FILE_PATH + fileName), 'wb+')
        file_data = file_socket.recv(1024)
        print(file_data)
        while file_data:
            fileWriter.write(file_data)
            file_data = file_socket.recv(1024)
        fileWriter.close()
        file_socket.close()
except socket.error as err:
    print("Discovery Connection to %s:%s failed: %s" % (IP, PORT, err))