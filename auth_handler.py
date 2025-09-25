#!/usr/bin/env python3
"""
Authentication handler for Schrimp Chat Server
"""

import socket


# ==============================================================================
# AUTHENTICATION HANDLER
# ==============================================================================

class AuthHandler:
    """Handles client authentication"""
    
    def __init__(self, password=None):
        self.password = password
    
    def send_welcome_message(self, client_socket):
        """Send welcome message to client"""
        welcome_msg = "\n" + "="*50 + "\n"
        welcome_msg += "Welcome to Schrimp Chat!\n"
        welcome_msg += "="*50 + "\n"
        
        if self.password:
            welcome_msg += "Password required\n"
            welcome_msg += "Enter password: "
        else:
            welcome_msg += "Enter your username: "
            
        client_socket.send(welcome_msg.encode('utf-8'))
        return not bool(self.password)  # Return True if no password required
    
    def authenticate_client(self, client_socket):
        """Authenticate client with password"""
        if not self.password:
            return True
            
        password_attempt = client_socket.recv(1024).decode('utf-8').strip()
        if password_attempt == self.password:
            client_socket.send("Authentication successful!\nEnter your username: ".encode('utf-8'))
            return True
        else:
            client_socket.send("Incorrect password. Connection closed.\n".encode('utf-8'))
            return False
    
    def get_username(self, client_socket, client_address, client_manager):
        """Get and validate username from client"""
        pseudo_input = client_socket.recv(1024).decode('utf-8').strip()
        pseudo = pseudo_input if pseudo_input else f"Anonymous_{client_address[1]}"
        
        # Check if username is already taken
        while client_manager.is_username_taken(pseudo):
            client_socket.send(f"Username '{pseudo}' is already taken. Choose another: ".encode('utf-8'))
            pseudo_input = client_socket.recv(1024).decode('utf-8').strip()
            pseudo = pseudo_input if pseudo_input else f"Anonymous_{client_address[1]}"
        
        return pseudo
    
    def send_connection_info(self, client_socket, pseudo, client_count):
        """Send connection information to newly connected client"""
        info_msg = f"\nConnected as: {pseudo}\n"
        info_msg += f"Connected users: {client_count}\n"
        info_msg += "Type your messages and press Enter\n"
        info_msg += "Type '/quit' to leave\n"
        info_msg += "Type '/users' to see connected users\n"
        info_msg += "-" * 30 + "\n"
        client_socket.send(info_msg.encode('utf-8'))