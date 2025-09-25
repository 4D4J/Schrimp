#!/usr/bin/env python3
"""
Simple Chat Server - Schrimp
Main entry point for the chat server application

Usage: python chat_server.py [port] [password]
Client connection: nc <server_ip> <port>

Arguments:
- port: Server port (default: 3031)
- password: Optional password for authentication
"""

import sys
from server import ChatServer


# ==============================================================================
# MAIN FUNCTION
# ==============================================================================

def main():
    """Main function to parse arguments and start the server"""
    # Handle command line arguments
    port = 3031
    password = None
    
    if len(sys.argv) >= 2:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Invalid port, using default port 8888")
    
    if len(sys.argv) >= 3:
        password = sys.argv[2]
    
    # --------------------------------------------------------------------------
    # SERVER INITIALIZATION
    # --------------------------------------------------------------------------
    
    # Create and start server
    server = ChatServer(port=port, password=password)
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nStopping server...")
        server.stop()


# ==============================================================================
# SCRIPT ENTRY POINT
# ==============================================================================

if __name__ == "__main__":
    main()