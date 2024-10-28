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
        self.port = server_port
        self.server_socket = socket(AF_INET,SOCK_STREAM)
        self.server_socket.bind(('',self.port))
        self.server_socket.listen(1)
        self.clients = {} #adresses and names
        self.run_event = threading.Event()
        self.handle_event = threading.Event()
        print(f"Server started on port {self.port}")
        
        
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
        self.broadcast(None, "Server is shutting down.")  # Use None to indicate a server message

        # Set the handle_event to stop handling messages
        self.handle_event.set()

        # Close all client connections
        for client_socket in list(self.clients.keys()):  # Create a list to avoid modifying the dictionary during iteration
            self.close_client(client_socket)

        self.server_socket.close()  # Close the server socket
        print("Server has been shut down.")

    def get_clients_number(self): 
        return len(self.clients)
    
    def handle_client(self, client_socket):
        while not self.handle_event.is_set():
            try:
                # Receive a message from the client
                message = client_socket.recv(1024).decode('utf-8').strip()
                
                if message.lower() == 'exit':
                    # If the client sends 'exit', close the client connection
                    self.broadcast(client_socket, 'exit')  # Notify others that the user has left
                    self.close_client(client_socket)  # Close the client socket
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
            return  # Exit if the connection fails

        # Start a thread to receive messages from the server
        threading.Thread(target=self.receive).start()

        print("You can start sending messages. Type 'exit' to leave the chatroom.")
        
        while not self.exit_run.is_set():  # Continue until exit_run is set
            message = input()  # Get user input
            if message.lower() == 'exit':
                self.send('exit')  # Notify the server that the client is leaving
                self.exit_run.set()  # Signal to exit the main loop
            else:
                self.send(message)  # Send the message to the server


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
        client_name = message.decode('utf-8')  # Decode the message to get the client's name

        # Check if the client is already connected
        if client_addr in self.clients:
            self.server_socket.sendto("Name already taken".encode('utf-8'), client_addr)
            return False

        # Check if the name is already in use
        if client_name in self.clients.values():
            self.server_socket.sendto("Name already taken".encode('utf-8'), client_addr)
            return False

        # Send a welcome message to the client
        self.server_socket.sendto("Welcome to the chatroom!".encode('utf-8'), client_addr)

        # Add the client to the clients dictionary
        self.clients[client_addr] = client_name

        # Append the join message to the messages list
        self.messages.append((client_addr, f"User {client_name} joined"))
        
        # Broadcast the new client's arrival to all other clients
        self.broadcast()  # Call broadcast without arguments
        
        return True

    def close_client(self, client_addr):
        if client_addr in self.clients:
            client_name = self.clients[client_addr]  # Get the client's name
            del self.clients[client_addr]  # Remove the client from the dictionary
            
            # Append a message indicating the user has left
            self.messages.append((client_addr, f"User {client_name} left"))
            
            # Broadcast the departure message to all other clients
            self.broadcast()  # Call broadcast without arguments
            
            print(f"Client {client_name} has been disconnected.")
            return True  # Return True if the client was successfully removed
        return False  # Return False if the client was not found

    def broadcast(self):
        # Check if there are any messages to broadcast
        if not self.messages:
            return  # If there are no messages, exit the method

        # Get the most recent message from the messages list
        last_message = self.messages[-1]  # Get the last message tuple (client_addr, message_content)
        message_content = last_message[1]  # Extract the message content
        client_addr = last_message[0]  # Get the address of the client who sent the message

        # Send the broadcast message to all connected clients except the one who sent it
        for client in self.clients.keys():
            if client != client_addr:  # Exclude the sender
                self.server_socket.sendto(message_content.encode('utf-8'), client)

    def shutdown(self):
        # Notify all clients that the server is shutting down
        for client_addr in list(self.clients.keys()):  # Create a list to avoid modifying the dictionary during iteration
            self.server_socket.sendto("Server is shutting down.".encode('utf-8'), client_addr)
            self.close_client(client_addr)  # Close client connections

        self.server_socket.close()  # Close the server socket
        print("UDP Server has been shut down.")

    def get_clients_number(self):
        return len(self.clients)
    
    def run(self):
        self.run_event.set()  # Indicate that the server is running
        print("UDP Server is running...")

        while self.run_event.is_set():  # Continue listening for messages while the server is running
            try:
                # Receive message from clients
                message, client_addr = self.server_socket.recvfrom(1024)  # Buffer size is 1024 bytes
                print(f"Received message from {client_addr}: {message.decode('utf-8')}")

                # Handle new client connection or message
                if client_addr not in self.clients:  # Check if it's a new client
                    self.accept_client(client_addr, message)  # Accept new client
                elif message.decode('utf-8').lower() == 'exit':
                    self.close_client(client_addr)  # Close client connection
                else:
                    # Broadcast the received message to other clients
                    self.messages.append((client_addr, message.decode('utf-8')))  # Store the message for broadcasting
                    self.broadcast()  # Call broadcast without arguments

            except Exception as e:
                print(f"Error receiving message: {e}")


class ClientUDP:
    def __init__(self, client_name, server_port):
        self.server_addr = gethostbyname(gethostname()) 
        self.client_socket = socket(AF_INET, SOCK_DGRAM)
        self.server_port = server_port
        self.client_name = client_name 
        self.exit_run = threading.Event()
        self.exit_receive = threading.Event() 

    def connect_server(self):
        # Send a 'join' message to the server
        self.send('join')  # Send the join message with the client's name
        
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
        while not self.exit_receive.is_set():  # Continue until exit_receive is set
            try:
                # Receive messages from the server
                message, _ = self.client_socket.recvfrom(1024)  # Buffer size is 1024 bytes
                message = message.decode('utf-8')
                
                if message == "Server is shutting down.":
                    print("The server has shut down.")
                    self.exit_run.set()  # Signal to exit the main loop
                    self.exit_receive.set()  # Stop receiving messages
                    break

                # Print the received message
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
        threading.Thread(target=self.receive, daemon=True).start()

        print("You can start sending messages. Type 'exit' to leave the chatroom.")
        
        while not self.exit_run.is_set():  # Continue until exit_run is set
            message = input()  # Get user input
            if message.lower() == 'exit':
                self.send('exit')  # Notify the server that the client is leaving
                self.exit_run.set()  # Signal to exit the main loop
            else:
                self.send(message) 




