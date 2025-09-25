#!/usr/bin/env python3
"""
Client management for Schrimp Chat Server
"""

import socket
from datetime import datetime


# ==============================================================================
# CLIENT MANAGEMENT
# ==============================================================================

class ClientManager:
    """Manages connected clients"""
    
    def __init__(self):
        self.clients = {}  # {socket: {'pseudo': str, 'ip': str, 'connected_at': datetime}}
    
    def add_client(self, client_socket, pseudo, ip):
        """Add a new client to the manager"""
        self.clients[client_socket] = {
            'pseudo': pseudo,
            'ip': ip,
            'connected_at': datetime.now()
        }
        print(f"{pseudo} ({ip}) connected")
    
    def remove_client(self, client_socket):
        """Remove a client from the manager"""
        if client_socket in self.clients:
            pseudo = self.clients[client_socket]['pseudo']
            del self.clients[client_socket]
            print(f"{pseudo} disconnected")
            return pseudo
        return None
    
    def is_username_taken(self, username):
        """Check if a username is already taken"""
        return any(client_info['pseudo'] == username for client_info in self.clients.values())
    
    def get_client_count(self):
        """Get the number of connected clients"""
        return len(self.clients)
    
    def get_clients_list(self):
        """Get a formatted list of connected clients"""
        users_list = "Connected users:\n"
        for client_info in self.clients.values():
            users_list += f"  • {client_info['pseudo']} ({client_info['ip']})\n"
        return users_list
    
    def broadcast_message(self, message, exclude_client=None):
        """Broadcast a message to all connected clients"""
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