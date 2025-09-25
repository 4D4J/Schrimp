#!/usr/bin/env python3
"""
Secure Chat Client - Schrimp
Client with encryption support for secure communications
"""

import socket
import threading
import sys
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


# ==============================================================================
# SECURE CLIENT
# ==============================================================================

class SecureChatClient:
    """Secure chat client with encryption support"""
    
    def __init__(self, host, port, encryption_password=None):
        self.host = host
        self.port = port
        self.socket = None
        self.encryption_password = encryption_password
        self.cipher = None
        self.running = False
        
        if encryption_password:
            self._setup_encryption()
    
    def _setup_encryption(self):
        """Setup encryption cipher"""
        salt = b'schrimp_salt_2025'  # Must match server salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.encryption_password.encode()))
        self.cipher = Fernet(key)
    
    def encrypt_message(self, message):
        """Encrypt outgoing message"""
        if not self.cipher:
            return message
        try:
            encrypted = self.cipher.encrypt(message.encode('utf-8'))
            return base64.b64encode(encrypted).decode('utf-8')
        except:
            return message
    
    def decrypt_message(self, encrypted_message):
        """Decrypt incoming message"""
        if not self.cipher:
            return encrypted_message
        try:
            encrypted_bytes = base64.b64decode(encrypted_message.encode('utf-8'))
            decrypted = self.cipher.decrypt(encrypted_bytes)
            return decrypted.decode('utf-8')
        except:
            return encrypted_message
    
    def connect(self):
        """Connect to the chat server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.running = True
            
            print(f"Connected to {self.host}:{self.port}")
            if self.cipher:
                print("Encryption enabled")
            else:
                print("No encryption - messages are sent in plain text")
            
            # Start receiving thread
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
            # Main input loop
            self.input_loop()
            
        except Exception as e:
            print(f"Connection error: {e}")
        finally:
            self.disconnect()
    
    def receive_messages(self):
        """Receive and display messages from server"""
        while self.running:
            try:
                message = self.socket.recv(1024).decode('utf-8')
                if not message:
                    break
                
                # Try to decrypt if it looks like encrypted data
                if self.cipher and len(message) > 50 and message.replace('=', '').replace('+', '').replace('/', '').isalnum():
                    decrypted = self.decrypt_message(message)
                    if decrypted != message:  # Successfully decrypted
                        print(f"🔒 {decrypted}")
                    else:
                        print(message)  # Plain text message
                else:
                    print(message)
                    
            except Exception as e:
                if self.running:
                    print(f"Receive error: {e}")
                break
    
    def input_loop(self):
        """Handle user input and send messages"""
        try:
            while self.running:
                message = input()
                if message.lower() in ['/quit', '/exit']:
                    break
                
                if message.strip():
                    # Encrypt message before sending if encryption is enabled
                    if self.cipher:
                        encrypted_message = self.encrypt_message(message)
                        self.socket.send(encrypted_message.encode('utf-8'))
                    else:
                        self.socket.send(message.encode('utf-8'))
                        
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f"Input error: {e}")
    
    def disconnect(self):
        """Disconnect from server"""
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        print("\nDisconnected from server")


# ==============================================================================
# MAIN FUNCTION
# ==============================================================================

def main():
    """Main function to start secure client"""
    if len(sys.argv) < 3:
        print("Usage: python secure_client.py <host> <port> [encryption_password]")
        print("Example: python secure_client.py localhost 8888")
        print("Example: python secure_client.py localhost 8888 mypassword")
        sys.exit(1)
    
    host = sys.argv[1]
    try:
        port = int(sys.argv[2])
    except ValueError:
        print("Error: Port must be a number")
        sys.exit(1)
    
    encryption_password = sys.argv[3] if len(sys.argv) > 3 else None
    
    client = SecureChatClient(host, port, encryption_password)
    
    try:
        client.connect()
    except KeyboardInterrupt:
        print("\nShutting down...")
        client.disconnect()


if __name__ == "__main__":
    main()