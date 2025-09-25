#!/usr/bin/env python3
"""
Security utilities for Schrimp Chat Server
Provides encryption, anti-spam, and other security features
"""

import base64
import hashlib
import time
import secrets
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


# ==============================================================================
# ENCRYPTION UTILITIES
# ==============================================================================

class ChatEncryption:
    """Handles message encryption/decryption for secure communications"""
    
    def __init__(self, password=None):
        self.password = password or "default_schrimp_key"
        self.salt = b'schrimp_salt_2025'  # In production, use random salt per session
        self.cipher = self._generate_cipher()
    
    def _generate_cipher(self):
        """Generate Fernet cipher from password"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.password.encode()))
        return Fernet(key)
    
    def encrypt_message(self, message):
        """Encrypt a message"""
        try:
            encrypted = self.cipher.encrypt(message.encode('utf-8'))
            return base64.b64encode(encrypted).decode('utf-8')
        except Exception:
            return message  # Fallback to plain text if encryption fails
    
    def decrypt_message(self, encrypted_message):
        """Decrypt a message"""
        try:
            encrypted_bytes = base64.b64decode(encrypted_message.encode('utf-8'))
            decrypted = self.cipher.decrypt(encrypted_bytes)
            return decrypted.decode('utf-8')
        except Exception:
            return encrypted_message  # Assume it's already plain text


# ==============================================================================
# ANTI-SPAM SYSTEM
# ==============================================================================

class AntiSpam:
    """Anti-spam system to prevent message flooding"""
    
    def __init__(self):
        self.client_history = {}  # {client_id: {'messages': [], 'last_message': '', 'warnings': 0}}
        self.max_messages_per_minute = 15
        self.max_duplicate_messages = 3
        self.max_warnings = 3
    
    def check_spam(self, client_id, message):
        """Check if message is spam. Returns (is_spam, reason)"""
        now = time.time()
        
        # Initialize client history if not exists
        if client_id not in self.client_history:
            self.client_history[client_id] = {
                'messages': [],
                'last_message': '',
                'warnings': 0
            }
        
        client_data = self.client_history[client_id]
        
        # Remove messages older than 1 minute
        client_data['messages'] = [
            msg_time for msg_time in client_data['messages'] 
            if now - msg_time < 60
        ]
        
        # Check rate limiting
        if len(client_data['messages']) >= self.max_messages_per_minute:
            return True, "Rate limit exceeded"
        
        # Check duplicate messages
        if message == client_data['last_message']:
            client_data['warnings'] += 1
            if client_data['warnings'] >= self.max_duplicate_messages:
                return True, "Too many duplicate messages"
        else:
            client_data['warnings'] = 0  # Reset warnings for different message
        
        # Check for excessive warnings
        if client_data['warnings'] >= self.max_warnings:
            return True, "Too many spam warnings"
        
        # Update client data
        client_data['messages'].append(now)
        client_data['last_message'] = message
        
        return False, ""
    
    def reset_client(self, client_id):
        """Reset spam data for a client"""
        if client_id in self.client_history:
            del self.client_history[client_id]


# ==============================================================================
# CONTENT FILTER
# ==============================================================================

class ContentFilter:
    """Filter inappropriate content from messages"""
    
    def __init__(self):
        # Basic word filter - in production, use more sophisticated filtering
        self.banned_words = {
            'spam', 'hack', 'exploit', 'ddos', 'attack'
        }
        
        self.max_message_length = 500
        self.max_caps_percentage = 70  # Max percentage of caps letters
    
    def filter_message(self, message):
        """Filter and clean message. Returns (filtered_message, is_blocked, reason)"""
        original_message = message
        
        # Check message length
        if len(message) > self.max_message_length:
            return "", True, f"Message too long (max {self.max_message_length} chars)"
        
        # Check for excessive caps
        if len(message) > 5:  # Only check if message is longer than 5 chars
            caps_count = sum(1 for c in message if c.isupper())
            caps_percentage = (caps_count / len(message)) * 100
            if caps_percentage > self.max_caps_percentage:
                message = message.lower().capitalize()
        
        # Check for banned words
        message_lower = message.lower()
        for word in self.banned_words:
            if word in message_lower:
                return "", True, f"Message contains inappropriate content"
        
        # Clean multiple spaces and newlines
        message = ' '.join(message.split())
        
        return message, False, ""


# ==============================================================================
# RATE LIMITER
# ==============================================================================

class RateLimiter:
    """Rate limiting for connections and actions"""
    
    def __init__(self):
        self.connection_attempts = {}  # {ip: [timestamps]}
        self.max_connections_per_minute = 5
        self.blocked_ips = {}  # {ip: unblock_time}
        self.block_duration = 300  # 5 minutes
    
    def check_connection_rate(self, ip):
        """Check if IP is allowed to connect. Returns (allowed, reason)"""
        now = time.time()
        
        # Check if IP is currently blocked
        if ip in self.blocked_ips:
            if now < self.blocked_ips[ip]:
                remaining = int(self.blocked_ips[ip] - now)
                return False, f"IP blocked for {remaining} more seconds"
            else:
                del self.blocked_ips[ip]
        
        # Initialize IP history if not exists
        if ip not in self.connection_attempts:
            self.connection_attempts[ip] = []
        
        # Remove attempts older than 1 minute
        self.connection_attempts[ip] = [
            attempt_time for attempt_time in self.connection_attempts[ip]
            if now - attempt_time < 60
        ]
        
        # Check rate limit
        if len(self.connection_attempts[ip]) >= self.max_connections_per_minute:
            # Block IP
            self.blocked_ips[ip] = now + self.block_duration
            return False, "Too many connection attempts - IP blocked"
        
        # Record this attempt
        self.connection_attempts[ip].append(now)
        return True, ""


# ==============================================================================
# SECURITY MANAGER
# ==============================================================================

class SecurityManager:
    """Main security manager that coordinates all security features"""
    
    def __init__(self, encryption_password=None, enable_encryption=True):
        self.encryption = ChatEncryption(encryption_password) if enable_encryption else None
        self.anti_spam = AntiSpam()
        self.content_filter = ContentFilter()
        self.rate_limiter = RateLimiter()
        self.enable_encryption = enable_encryption
    
    def check_connection_allowed(self, ip):
        """Check if connection from IP is allowed"""
        return self.rate_limiter.check_connection_rate(ip)
    
    def process_outgoing_message(self, message, client_id):
        """Process message before sending (filter + encrypt)"""
        # Filter content
        filtered_message, is_blocked, reason = self.content_filter.filter_message(message)
        if is_blocked:
            return None, f"Message blocked: {reason}"
        
        # Check spam
        is_spam, spam_reason = self.anti_spam.check_spam(client_id, filtered_message)
        if is_spam:
            return None, f"Spam detected: {spam_reason}"
        
        # Encrypt if enabled
        if self.enable_encryption and filtered_message:
            filtered_message = self.encryption.encrypt_message(filtered_message)
        
        return filtered_message, ""
    
    def process_incoming_message(self, message):
        """Process incoming message (decrypt)"""
        if self.enable_encryption and message:
            return self.encryption.decrypt_message(message)
        return message
    
    def reset_client_security(self, client_id):
        """Reset security data for a client"""
        self.anti_spam.reset_client(client_id)


# ==============================================================================
# SECURITY UTILITIES
# ==============================================================================

def generate_session_token():
    """Generate a secure session token"""
    return secrets.token_urlsafe(32)

def hash_password(password):
    """Hash a password securely"""
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}:{pwd_hash.hex()}"

def verify_password(password, hashed):
    """Verify a password against its hash"""
    try:
        salt, pwd_hash = hashed.split(':')
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex() == pwd_hash
    except:
        return False