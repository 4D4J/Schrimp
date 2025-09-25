#!/usr/bin/env python3
"""
Message handler for Schrimp Chat Server
"""

import socket
from datetime import datetime


# ==============================================================================
# MESSAGE HANDLER
# ==============================================================================

class MessageHandler:
    """Handles message processing and commands"""
    
    def __init__(self, logger):
        self.logger = logger
    
    def process_message(self, message, pseudo, client_socket, client_manager):
        """Process incoming message and return action"""
        message = message.strip()
        
        if not message:
            return 'disconnect'
            
        # Special commands
        if message.lower() == '/quit':
            return 'disconnect'
        elif message.lower() == '/users':
            users_list = client_manager.get_clients_list()
            client_socket.send(users_list.encode('utf-8'))
            return 'continue'
        
        # Regular message - broadcast it
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {pseudo}: {message}"
        self.logger.log_and_print(formatted_message)
        client_manager.broadcast_message(formatted_message, exclude_client=client_socket)
        return 'continue'
    
    def handle_message_loop(self, client_socket, pseudo, client_manager, server_running):
        """Handle the main message reception loop"""
        while server_running():
            try:
                message = client_socket.recv(1024).decode('utf-8')
                if not message:
                    break
                    
                action = self.process_message(message, pseudo, client_socket, client_manager)
                if action == 'disconnect':
                    break
                    
            except socket.error:
                break