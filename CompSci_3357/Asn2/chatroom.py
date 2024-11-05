"""
Jason Tam
251171681
CompSci 3357 Asn 2
"""

from socket import *
import threading

""" TCP """
class ServerTCP:
    def __init__(self, server_port):
        self.server_port = server_port
        self.server_socket = socket(AF_INET,SOCK_STREAM)
        self.server_socket.bind(('',self.server_port))
        self.server_socket.listen(1)
        self.clients = {} #adresses and names
        self.run_event = threading.Event()
        self.handle_event = threading.Event()
        print(f"Server started on port {self.server_port}")
        
        
    def accept_client(self):
        while self.run_event.is_set():  # Keep accepting clients while the server is running
            try:
                client_socket, client_address = self.server_socket.accept()  # Accept a new client connection
                print(f"client scoket: {client_socket}")
                print(f"Connection established with {client_address}")

                # Receive the client's name
                client_name = client_socket.recv(1024).decode('utf-8').strip()

                # Check if the name is unique
                if client_name in self.clients.values():
                    client_socket.send("Name already taken".encode('utf-8'))
                    client_socket.close()  # Close the connection if the name is taken
                    return False

                # Send a welcome message to the new client
                client_socket.send("Welcome to the chatroom!".encode('utf-8'))

                # Add the client to the clients dictionary
                self.clients[client_socket] = client_name

                # Broadcast the new client's arrival
                self.broadcast(client_socket, 'join')

                # Start a new thread to handle the client
                threading.Thread(target=self.handle_client, args=(client_socket,)).start()
                return True

            except Exception as e:
                print(f"Error accepting client: {e}")

    def close_client(self, client_socket):
        if client_socket in self.clients:
            client_name = self.clients[client_socket]  # Get the client's name
            del self.clients[client_socket]
            client_socket.close()  # Close the client's socket
            print(f"Client {client_name} has been disconnected.")
            return True 
        return False  

    def broadcast(self, client_socket_sent, message):
        if message == 'join':
            broadcast_message = f"User {self.clients[client_socket_sent]} has joined the chat."
        elif message == 'exit':
            broadcast_message = f"User {self.clients[client_socket_sent]} has left the chat."
        elif client_socket_sent == None:
            broadcast_message = f"{message}"
        else:
            broadcast_message = f"{self.clients[client_socket_sent]}: {message}"


        # Send the broadcast message to all connected clients except the one who sent it
        for client_socket in self.clients.keys():
            if client_socket != client_socket_sent:
                try:
                    client_socket.send(broadcast_message.encode('utf-8'))
                except Exception as e:
                    print(f"Error sending message to {self.clients[client_socket]}: {e}")
                    self.close_client(client_socket)  # Close the client if there's an error

    def shutdown(self):
        # Notify all clients that the server is shutting down
        self.broadcast(None, "Server is shutting down.")

        # Set the handle_event to stop handling messages
        self.handle_event.set()

        # Close all client connections
        for client_socket in list(self.clients.keys()):  # Create a list to avoid modifying the dictionary during iteration
            self.close_client(client_socket)

        self.server_socket.close()  # Close the server socket
        print("Server has been shut down.")

    def get_clients_number(self): 
        print(f"Number of clients: {len(self.clients)}")  # Debugging output
        return len(self.clients)
    
    def handle_client(self, client_socket):
        while not self.handle_event.is_set():
            try:
                # Receive a message from the client
                message = client_socket.recv(1024).decode('utf-8').strip()
                
                if message.lower() == 'exit':
                    # If the client sends 'exit', close the client connection
                    self.broadcast(client_socket, 'exit')  # Notify others that the user has left
                    self.close_client(client_socket)
                    break

                # Broadcast the received message to other clients
                self.broadcast(client_socket, message)

            except Exception as e:
                print(f"Error handling client {self.clients[client_socket]}: {e}")
                self.close_client(client_socket)  # Close the client if there's an error
                break

    def run(self):
        self.run_event.set()  # Indicate that the server is running
        print("Server is running...")
        
        while self.run_event.is_set():  # Continue accepting clients while the event is set
            self.accept_client() 



class ClientTCP:
    def __init__(self, client_name, server_port):
        self.server_addr = gethostbyname(gethostname()) 
        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.server_port = server_port 
        self.client_name = client_name 
        self.exit_run = threading.Event()  
        self.exit_receive = threading.Event()  
        
    def connect_server(self):
        try:
            # Connect to the server
            self.client_socket.connect((self.server_addr, self.server_port))
            
            # Send the client's name to the server
            self.client_socket.send(self.client_name.encode('utf-8'))
            
            # Wait for a welcome message from the server
            welcome_message = self.client_socket.recv(1024).decode('utf-8')
            if welcome_message == "Welcome to the chatroom!":
                print(welcome_message)
                return True  # Connection successful
            else:
                print("Failed to connect: ", welcome_message)
                return False  # Connection failed
        except Exception as e:
            print(f"Error connecting to server: {e}")
            return False  # Return False if there was an error

    def send(self, text):
        try:
            # Send the given text to the server
            self.client_socket.send(text.encode('utf-8'))
        except Exception as e:
            print(f"Error sending message: {e}")

    def receive(self):
        while not self.exit_receive.is_set():  # Continue until exit_receive is set
            try:
                # Receive a message from the server
                message = self.client_socket.recv(1024).decode('utf-8').strip()
                
                if message == "server-shutdown":
                    print("The server has shut down.")
                    self.exit_run.set()  # Signal to exit the main loop
                    self.exit_receive.set()
                    break  

                # Print the received message
                print(message)

            except Exception as e:
                print(f"Error receiving message: {e}")
                self.exit_run.set()  # Signal to exit the main loop
                break 

    def run(self):
        # Connect to the server
        if not self.connect_server():
            print("Failed to connect to the server.")
            return  

        # Start a thread to receive messages from the server
        threading.Thread(target=self.receive).start()

        print("You can start sending messages. Type 'exit' to leave the chatroom.")
        
        while not self.exit_run.is_set():  # Continue until exit_run is set
            message = input()  # Get user input
            if message.lower() == 'exit':
                self.send('exit')  
                self.exit_run.set()
            else:
                self.send(message) 


""" UDP """
class ServerUDP:
    def __init__(self, server_port):
        self.server_port = server_port 
        self.server_socket = socket(AF_INET, SOCK_DGRAM)  
        self.server_socket.bind(('', self.server_port))  
        self.clients = {} 
        self.messages = [] 
        self.run_event = threading.Event() 
        print(f"UDP Server started on port {self.server_port}")

    def accept_client(self, client_addr, message):
        client_name = message.decode('utf-8').split(": ")[0]

        # Check if the name is already in use
        if client_name[0] in self.clients.values():
            self.server_socket.sendto("Name already taken".encode('utf-8'), client_addr)
            return False

        self.server_socket.sendto("Welcome to the chatroom!".encode('utf-8'), client_addr)
        self.clients[client_addr] = client_name[0]
        self.messages.append((client_addr, f"User {client_name[0]} joined"))
        
        self.broadcast()
        
        return True

    def close_client(self, client_addr):
        if client_addr in self.clients:
            client_name = self.clients[client_addr]
            del self.clients[client_addr]  # Remove the client from the dictionary
            self.messages.append((client_addr, f"User {client_name} left"))
            
            # Broadcast the departure message to all other clients
            self.broadcast()
            
            print(f"Client {client_name} has been disconnected.")
            return True 
        return False 

    def broadcast(self):
        # Check if there are any messages to broadcast
        if not self.messages:
            return  # If there are no messages, exit the method

        # Get the most recent message from the messages list
        last_message = self.messages[-1]  # Get the last message tuple (client_addr, message_content)
        message_content = last_message[1]
        client_addr = last_message[0]

        # Send the broadcast message to all connected clients except the one who sent it
        for client in self.clients.keys():
            if client != client_addr:  # Exclude the sender
                self.server_socket.sendto(message_content.encode('utf-8'), client)

    def shutdown(self):
        # Notify all clients that the server is shutting down
        for client_addr in list(self.clients.keys()):  # Create a list to avoid modifying the dictionary during iteration
            self.server_socket.sendto("server-shutdown".encode('utf-8'), client_addr)
            self.close_client(client_addr)  # Close client connections

        self.server_socket.close()  # Close the server socket
        print("UDP Server has been shut down.")
        self.run_event.clear()  # Clear the run event to stop the server loop

    def get_clients_number(self):
        return len(self.clients)
    
    def run(self):
        self.run_event.set()  # Indicate that the server is running
        print("UDP Server is running...")

        while self.run_event.is_set():  # Continue listening for messages while the server is running
            try:
                # Receive message from clients
                message, client_addr = self.server_socket.recvfrom(1024)
                print(f"Received message from {client_addr}: {message.decode('utf-8')}")

                # Handle new client connection or message
                if client_addr not in self.clients:
                    self.accept_client(client_addr, message)
                elif message.decode('utf-8').split(": ")[1].strip().lower() == 'exit':
                    self.close_client(client_addr)
                else:
                    # Broadcast the received message to other clients
                    self.messages.append((client_addr, message.decode('utf-8')))  # Store the message for broadcasting
                    self.broadcast()

            except Exception as e:
                print(f"Error receiving message: {e}")
                break  # Exit the loop on error


class ClientUDP:
    def __init__(self, client_name, server_port):
        self.server_addr = gethostbyname(gethostname()) 
        self.client_socket = socket(AF_INET, SOCK_DGRAM)
        self.server_port = server_port
        self.client_name = client_name 
        self.exit_run = threading.Event()
        self.exit_receive = threading.Event() 

    def connect_server(self):
        self.send('join')
        
        # Wait for a welcome message from the server
        welcome_message, _ = self.client_socket.recvfrom(1024)
        welcome_message = welcome_message.decode('utf-8')
        
        if welcome_message == "Welcome to the chatroom!":
            print(welcome_message)
            return True  # Connection successful
        else:
            print("Failed to connect: ", welcome_message)
            return False  # Connection failed

    def send(self, text):
        # Send the given text to the server
        message = f"{self.client_name}: {text}"  # Format the message
        self.client_socket.sendto(message.encode('utf-8'), (self.server_addr, self.server_port))


    def receive(self):
        while not self.exit_receive.is_set():
            try:
                # Receive messages from the server
                message, _ = self.client_socket.recvfrom(1024)
                message = message.decode('utf-8')
                
                if message == "server-shutdown":
                    print("The server has shut down.")
                    self.exit_run.set()  # Signal to exit the main loop
                    self.exit_receive.set()  # Stop receiving messages
                    break

                print(message)

            except Exception as e:
                print(f"Error receiving message: {e}")
                self.exit_run.set()  # Signal to exit the main loop
                break  # Exit the receive loop

    def run(self):
        # Connect to the server
        if not self.connect_server():
            print("Failed to connect to the server.")
            return  # Exit if the connection fails

        # Start a thread to receive messages from the server
        thread_rec = threading.Thread(target=self.receive, daemon=True).start()

        print("You can start sending messages. Type 'exit' to leave the chatroom.")

        while not self.exit_run.is_set():  # Continue until exit_run is set
            message = input() 
            if message.lower() == 'exit':
                self.send('exit') 
                self.exit_run.set()  # Signal to exit the main loop
            else:
                self.send(message) 
        #self.client_socket.close() 

