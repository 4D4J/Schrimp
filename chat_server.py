#!/usr/bin/env python3
"""
Simple Chat Server - Schrimp
Allows users to connect via netcat (nc) to chat
Usage: python chat_server.py [port] [password]
Client connection: nc <server_ip> <port>
"""

import socket
import threading
import time
import sys
import json
from datetime import datetime

class ChatServer:
    def __init__(self, host='0.0.0.0', port=8888, password=None):
        self.host = host
        self.port = port
        self.password = password
        self.clients = {}  # {socket: {'pseudo': str, 'ip': str, 'connected_at': datetime}}
        self.server_socket = None
        self.running = False
        
    def start(self):
        """Starts the chat server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(10)
            self.running = True
            
            print(f"Chat server started on {self.host}:{self.port}")
            if self.password:
                print(f"Password required: {self.password}")
            else:
                print("No password required")
            print(f"Connection: nc {self.host} {self.port}")
            print("=" * 50)
            
            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    print(f"New connection from {client_address[0]}:{client_address[1]}")
                    
                    # Create a thread for each client
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except socket.error:
                    if self.running:
                        print("Error accepting connection")
                        
        except Exception as e:
            print(f"Server startup error: {e}")
        finally:
            self.stop()
    
    def handle_client(self, client_socket, client_address):
        """Handles a connected client"""
        pseudo = None
        authenticated = False
        
        try:
            # Welcome message
            welcome_msg = "\n" + "="*50 + "\n"
            welcome_msg += "Welcome to Schrimp Chat!\n"
            welcome_msg += "="*50 + "\n"
            
            if self.password:
                welcome_msg += "Password required\n"
                welcome_msg += "Enter password: "
            else:
                welcome_msg += "Enter your username: "
                authenticated = True
                
            client_socket.send(welcome_msg.encode('utf-8'))
            
            # Authentication if necessary
            if self.password:
                password_attempt = client_socket.recv(1024).decode('utf-8').strip()
                if password_attempt == self.password:
                    authenticated = True
                    client_socket.send("Authentication successful!\nEnter your username: ".encode('utf-8'))
                else:
                    client_socket.send("Incorrect password. Connection closed.\n".encode('utf-8'))
                    return
            
            if authenticated:
                # Ask for username
                pseudo_input = client_socket.recv(1024).decode('utf-8').strip()
                pseudo = pseudo_input if pseudo_input else f"Anonymous_{client_address[1]}"
                
                # Check if username is already taken
                while any(client_info['pseudo'] == pseudo for client_info in self.clients.values()):
                    client_socket.send(f"Username '{pseudo}' is already taken. Choose another: ".encode('utf-8'))
                    pseudo_input = client_socket.recv(1024).decode('utf-8').strip()
                    pseudo = pseudo_input if pseudo_input else f"Anonymous_{client_address[1]}"
                
                # Register the client
                self.clients[client_socket] = {
                    'pseudo': pseudo,
                    'ip': client_address[0],
                    'connected_at': datetime.now()
                }
                
                # Connection messages
                join_msg = f"{pseudo} joined the chat!"
                print(f"{pseudo} ({client_address[0]}) connected")
                self.broadcast_message(join_msg, exclude_client=client_socket)
                
                # Send connection info to client
                info_msg = f"\nConnected as: {pseudo}\n"
                info_msg += f"Connected users: {len(self.clients)}\n"
                info_msg += "Type your messages and press Enter\n"
                info_msg += "Type '/quit' to leave\n"
                info_msg += "Type '/users' to see connected users\n"
                info_msg += "-" * 30 + "\n"
                client_socket.send(info_msg.encode('utf-8'))
                
                # Message reception loop
                while self.running:
                    try:
                        message = client_socket.recv(1024).decode('utf-8').strip()
                        if not message:
                            break
                            
                        # Special commands
                        if message.lower() == '/quit':
                            break
                        elif message.lower() == '/users':
                            users_list = "Connected users:\n"
                            for client_info in self.clients.values():
                                users_list += f"  • {client_info['pseudo']} ({client_info['ip']})\n"
                            client_socket.send(users_list.encode('utf-8'))
                            continue
                        
                        # Broadcast the message
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        formatted_message = f"[{timestamp}] {pseudo}: {message}"
                        print(formatted_message)
                        self.broadcast_message(formatted_message, exclude_client=client_socket)
                        
                    except socket.error:
                        break
                        
        except Exception as e:
            print(f"Error with client {client_address}: {e}")
        finally:
            # Cleanup on disconnection
            if client_socket in self.clients:
                pseudo = self.clients[client_socket]['pseudo']
                del self.clients[client_socket]
                
                disconnect_msg = f"{pseudo} left the chat"
                print(f"{pseudo} disconnected")
                self.broadcast_message(disconnect_msg)
                
            try:
                client_socket.close()
            except:
                pass
    
    def broadcast_message(self, message, exclude_client=None):
        """Broadcasts a message to all connected clients"""
        disconnected_clients = []
        
        for client_socket in list(self.clients.keys()):
            if client_socket != exclude_client:
                try:
                    client_socket.send((message + "\n").encode('utf-8'))
                except socket.error:
                    disconnected_clients.append(client_socket)
        
        # Clean up disconnected clients
        for client_socket in disconnected_clients:
            if client_socket in self.clients:
                pseudo = self.clients[client_socket]['pseudo']
                del self.clients[client_socket]
                print(f"{pseudo} disconnected (network error)")
    
    def stop(self):
        """Stops the server"""
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        print("\nServer stopped")

def main():
    # Handle command line arguments
    port = 8888
    password = None
    
    if len(sys.argv) >= 2:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Invalid port, using default port 8888")
    
    if len(sys.argv) >= 3:
        password = sys.argv[2]
    
    # Create and start server
    server = ChatServer(port=port, password=password)
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nStopping server...")
        server.stop()

if __name__ == "__main__":
    main()