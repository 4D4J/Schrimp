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
    
    def __init__(self):
        pass
    
    def process_message(self, message, pseudo, client_socket, client_manager, security_manager=None):
        """Process incoming message and return action"""
        message = message.strip()
        
        if not message:
            return 'disconnect'
            
        # Security checks
        if security_manager:
            # Check rate limiting
            if not security_manager.check_rate_limit(pseudo):
                warning = "Rate limit exceeded. Please slow down."
                self._send_to_client(client_socket, warning, security_manager)
                return 'continue'
            
            # Filter content
            filtered_message = security_manager.filter_content(message)
            if filtered_message != message:
                message = filtered_message  # Use filtered version
            
        # Special commands
        if message.lower() == '/quit':
            return 'disconnect'
        elif message.lower() == '/users':
            users_list = client_manager.get_clients_list()
            self._send_to_client(client_socket, users_list, security_manager)
            return 'continue'
        
        # Regular message - broadcast it
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {pseudo}: {message}"
        print(formatted_message)
        self._broadcast_message(formatted_message, client_manager, exclude_client=client_socket, security_manager=security_manager)
        return 'continue'
    
    def _send_to_client(self, client_socket, message, security_manager=None):
        """Send message to a specific client (no encryption)"""
        try:
            client_socket.send(message.encode('utf-8'))
        except Exception as e:
            print(f"Error sending message to client: {e}")
    
    def _broadcast_message(self, message, client_manager, exclude_client=None, security_manager=None):
        """Broadcast message to all clients (no encryption)"""
        client_manager.broadcast_message(message, exclude_client=exclude_client)
    
    def handle_message_loop(self, client_socket, pseudo, client_manager, server_running, security_manager=None):
        """Handle the main message reception loop"""
        while server_running():
            try:
                raw_message = client_socket.recv(1024)
                if not raw_message:
                    break
                
                # No decryption - direct message handling
                message = raw_message.decode('utf-8')
                    
                action = self.process_message(message, pseudo, client_socket, client_manager, security_manager)
                if action == 'disconnect':
                    break
                    
            except socket.error:
                break