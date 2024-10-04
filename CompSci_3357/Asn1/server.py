from socket import *
import threading
import os
import traceback
import time
"""
Jason Tam
251171681
Thurs Oct 3, 2024
"""

class Server:
    """
    Initialize the variables
    """
    def __init__(self, addr, port, timeout):
        self.addr = addr
        self.port = port
        self.timeout = timeout
        self.sessions = {}
        self.server_socket = socket(AF_INET,SOCK_STREAM)
        self.server_socket.bind((addr,port))
        self.server_socket.listen(1)
        print('The server is ready to receive')

    """
    Starts the server
    """
    def start_server(self):
        while True:
            try:
                self.server_socket.settimeout(self.timeout)
                connection_socket, addr = self.server_socket.accept()
                client_session = threading.Thread(target=self.handle_request, args=(connection_socket,))
                client_session.start()
            except timeout:
                print("Connection Timeout")
                self.stop_server()
                time.sleep(1)
                break
    
    """
    Stops the server
    """
    def stop_server(self):
        self.server_socket.close()
    
    """
    Parses request data
    """
    def parse_request(self, request_data):
        lines = request_data.split('\r\n')
        request_line = lines[0]
        headers = {}
        body = ''
        
        # Parse headers
        for line in lines[1:]:
            if line == '':
                break
            try:
                key, value = line.split(': ', 1)
                headers[key] = value
            except ValueError:
                continue
        
        # Get body if present
        if '\r\n\r\n' in request_data:
            body = request_data.split('\r\n\r\n', 1)[1]
        
        return request_line, headers, body
    
    """
    Handles each thread as a request
    """
    def handle_request(self, client_socket):
        try:
            request = client_socket.recv(1024).decode()
            if request == '':
                print("Empty request received")
                return
            request_line, headers, body = self.parse_request(request)
            method, path, version = request_line.split()
            
            if path == '/':
                path = "index.html"

            if method == "GET":
                self.handle_get_request(client_socket, path)
            elif method == "POST":
                self.handle_post_request(client_socket, path, headers, body)
            else:
                self.handle_unsupported_method(client_socket, method)

        except Exception as e:
            print(f"Error handling request: {e}")
            traceback.print_exc() 
        finally:
            client_socket.close()
    
    """
    Returns a 405 Method Not Allowed response to unsupported methods
    """
    def handle_unsupported_method(self, client_socket, method):
        response = f"HTTP/1.1 405 Method Not Allowed\r\n"
        response += "Content-Type: text/html\r\n"
        response += "\r\n"
        response += f"<h1>405 Method Not Allowed</h1><p>The {method} method is not supported.</p>"
        client_socket.send(response.encode())
    
    """
    Checks the path and sets the name of the client if it exists in sessions, otherwise sets it to Guest
    """
    def handle_get_request(self, client_socket, file_path):
        client_ip = client_socket.getpeername()[0]
        file_path = os.path.join(os.path.dirname(__file__), 'assets', file_path)
        
        #thread_str = self.sessions[client_address]
        #client_name = str(thread_str).strip('<>').split('(')[1].split()[0] if thread_str else "Guest"
        if client_ip in self.sessions:
            client_name = self.sessions[client_ip]
        else:
            client_name = "Guest"
        
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                content = file.read()
            
            content = content.replace('{{name}}', client_name)
            
            response = "HTTP/1.1 200 OK\r\n"
            response += "Content-Type: text/html\r\n"
            response += f"Content-Length: {len(content)}\r\n"
            response += "\r\n"
            response += content
        else:
            response = "HTTP/1.1 404 Not Found\r\n"
            response += "Content-Type: text/html\r\n"
            response += "\r\n"
            response += "<h1>404 Not Found</h1>"
        
        client_socket.send(response.encode())
    
    
    """
    Sets the name of the client in sessions to the corresponding ip address
    """
    def handle_post_request(self, client_socket, path, headers, body):
        client_ip = client_socket.getpeername()[0]
        name = body.split('=')[1]
        if path == "/change_name":            
            self.sessions[client_ip] = name
            response = "HTTP/1.1 200 OK\r\n"
            response += "Content-Type: text/html\r\n"
            response += "\r\n"
            response += "<h1>Name updated</h1>"
        else:
            response = "HTTP/1.1 404 Not Found\r\n"
            response += "Content-Type: text/html\r\n"
            response += "\r\n"
            response += "<h1>404 Not Found</h1>"
        
        client_socket.send(response.encode())