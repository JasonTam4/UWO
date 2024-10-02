from socket import *
import threading
#import more modules if needed 

class Server:
    def __init__(self, addr, port, timeout):
        self.addr = addr
        self.port = port
        self.timeout = timeout
        self.sessions = {}
        self.server_socket = socket(AF_INET,SOCK_STREAM)
        self.server_socket.bind(('',port))
        self.server_socket.listen(1)
        print('The server is ready to receive')

    def start_server(self):
        while True:
            self.connection_socket, addr = self.server_socket.accept()
            self.connection_socket.settimeout(10)
            # sentence = connection_socket.recv(1024).decode()
            # capitalizedSentence = sentence.upper()
            # connection_socket.send(capitalizedSentence.encode())
            self.connection_socket.close()
    
    def stop_server(self):
        self.server_socket.close()
    
    def parse_request(self, request_data):
        pass
    
    def handle_request(self, client_socket):
        pass
    
    def handle_unsupported_method(self, client_socket, method):
        pass
    
    def handle_get_request(self, client_socket, file_path):
        pass
    
    def handle_post_request(self, client_socket, path, headers, body):
        pass