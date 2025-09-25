#!/usr/bin/env python3
"""
Simple Chat Server - Schrimp
Main entry point for the chat server application

Usage: python chat_server.py [port] [password] [log_file]
Client connection: nc <server_ip> <port>

Arguments:
- port: Server port (default: 8888)
- password: Optional password for authentication
- log_file: Log file path (default: schrimp_chat.log)
"""

import sys
from server import ChatServer


# ==============================================================================
# MAIN FUNCTION
# ==============================================================================

def main():
    """Main function to parse arguments and start the server"""
    # Handle command line arguments
    port = 8888
    password = None
    log_file = 'schrimp_chat.log'
    
    if len(sys.argv) >= 2:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Invalid port, using default port 8888")
    
    if len(sys.argv) >= 3:
        password = sys.argv[2]
    
    if len(sys.argv) >= 4:
        log_file = sys.argv[3]
    
    # --------------------------------------------------------------------------
    # SERVER INITIALIZATION
    # --------------------------------------------------------------------------
    
    # Create and start server
    server = ChatServer(port=port, password=password, log_file=log_file)
    
    try:
        server.start()
    except KeyboardInterrupt:
        server.logger.log_and_print("\nStopping server...")
        server.stop()


# ==============================================================================
# SCRIPT ENTRY POINT
# ==============================================================================

if __name__ == "__main__":
    main()