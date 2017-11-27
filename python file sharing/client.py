import socket

IP = '192.168.1.8'
PORT = 10000
FILE_TRANSFER_PORT = 10001
FILE_PATH = '../sync/'
my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
hast_files = {}

def get_files():
    while True:
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
        file_socket.connect((x, self.FILE_TRANSFER_PORT))

        print("connected to %s:%s File Transfer Socket" % (x, self.FILE_TRANSFER_PORT))
        self.FILE_TRANSFER_PORT = self.FILE_TRANSFER_PORT + 1

        # Send all data
        file_socket.sendall(str({
            'ips': self.localnet_ips,
            'files': self.hash_files
            }).encode())

        # Recieve data
        data = json.dumps(file_socket.recv(1024).decode())

        # Calculate differences
        ips_diff = set(self.localnet_ips) - set(data['ips'])
        file_diff = self.get_diff(self.hash_files, data['files'])

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
            downloadFile = open((self.FILE_PATH, fileName), 'wb')
            while file_data:
                downloadFile.write(file_data)
                file_data = file_socket.recv(1024)
        

    except socket.error as e:
        print("File Transfer Connection to %s:%s failed: %s" % (x, self.FILE_TRANSFER_PORT, e))

except socket.error as err:
    print("Discovery Connection to %s:%s failed: %s" % (x, self.DISCOVER_PORT, err))