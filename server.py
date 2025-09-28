#!/usr/bin/env python3
"""
Main Chat Server - Schrimp
Core server implementation that orchestrates all components
"""

import socket
import threading
from client_manager import ClientManager

# Try to import security components (anti-spam, rate limiting, etc.)
try:
    from secure import SecurityManager
    SECURITY_AVAILABLE = True
except ImportError:
    SECURITY_AVAILABLE = False
    print("Security features not available")
from auth_handler import AuthHandler
from message_handler import MessageHandler

# Try to import security features (optional)
try:
    from secure import SecurityManager, generate_session_token
    SECURITY_AVAILABLE = True
except ImportError:
    SECURITY_AVAILABLE = False
    print("⚠️  Security features not available (missing cryptography library)")
    print("   Install with: pip install cryptography")


# ========================================================
# ======================
# MAIN CHAT SERVER  
# ==============================================================================

class ChatServer:
    """Main chat server class that coordinates all components"""
    
    def __init__(self, host='0.0.0.0', port=3031, password=None):
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        
        # Initialize components
        self.client_manager = ClientManager()
        self.auth_handler = AuthHandler(password)
        self.message_handler = MessageHandler()
        
        # Initialize security (rate limiting, anti-spam) - NO encryption
        if SECURITY_AVAILABLE:
            self.security_manager = SecurityManager(enable_security=True)
        else:
            self.security_manager = None

    # --------------------------------------------------------------------------
    # SERVER MANAGEMENT
    # --------------------------------------------------------------------------
        
    def start(self):
        """Starts the chat server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(10)
            self.running = True
            
            print(f"Chat server started on {self.host}:{self.port}")
            if self.security_manager:
                print("Security: Rate limiting and anti-spam ENABLED")
            else:
                print("Security: DISABLED")
            if self.auth_handler.password:
                print(f"Password required: {self.auth_handler.password}")
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

    # --------------------------------------------------------------------------
    # CLIENT HANDLING
    # --------------------------------------------------------------------------
    
    def handle_client(self, client_socket, client_address):
        """Handles a connected client"""
        pseudo = None
        
        try:
            # ------------------------------------------------------------------
            # AUTHENTICATION PROCESS
            # ------------------------------------------------------------------
            
            # Send welcome message and check if password is required
            authenticated = self.auth_handler.send_welcome_message(client_socket)
            
            # Authenticate if password is required
            if not authenticated:
                authenticated = self.auth_handler.authenticate_client(client_socket)
                if not authenticated:
                    return
            
            # ------------------------------------------------------------------
            # USER REGISTRATION
            # ------------------------------------------------------------------
            
            if authenticated:
                # Get and validate username
                pseudo = self.auth_handler.get_username(client_socket, client_address, self.client_manager)
                
                # Register the client
                self.client_manager.add_client(client_socket, pseudo, client_address[0])
                
                # Announce user joined
                join_msg = f"{pseudo} joined the chat!"
                self.client_manager.broadcast_message(join_msg, exclude_client=client_socket)
                
                # Send connection info to client
                self.auth_handler.send_connection_info(client_socket, pseudo, self.client_manager.get_client_count())
                
                # --------------------------------------------------------------
                # MESSAGE HANDLING LOOP
                # --------------------------------------------------------------
                
                # Handle messages until client disconnects
                self.message_handler.handle_message_loop(
                    client_socket, 
                    pseudo, 
                    self.client_manager, 
                    lambda: self.running
                )
                        
        except Exception as e:
            print(f"Error with client {client_address}: {e}")
        finally:
            # ------------------------------------------------------------------
            # CLEANUP ON DISCONNECTION
            # ------------------------------------------------------------------
            
            # Remove client and announce departure
            departed_pseudo = self.client_manager.remove_client(client_socket)
            if departed_pseudo:
                disconnect_msg = f"{departed_pseudo} left the chat"
                self.client_manager.broadcast_message(disconnect_msg)
                
            try:
                client_socket.close()
            except:
                pass

    # --------------------------------------------------------------------------
    # SERVER SHUTDOWN
    # --------------------------------------------------------------------------
    
    def stop(self):
        """Stops the server"""
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        print("Server stopped")