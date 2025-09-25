#!/usr/bin/env python3
"""
Logging utilities for Schrimp Chat Server
"""

import logging
import os


# ==============================================================================
# LOGGING UTILITIES
# ==============================================================================

class ChatLogger:
    """Handles logging for the chat server"""
    
    def __init__(self, log_file='schrimp_chat.log'):
        self.log_file = log_file
        self.logger = None
        self.setup_logging()
    
    def setup_logging(self):
        """Configure logging to file and console"""
        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(self.log_file) if os.path.dirname(self.log_file) else '.'
        if not os.path.exists(log_dir) and log_dir != '.':
            os.makedirs(log_dir)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file, encoding='utf-8'),
                logging.StreamHandler()  # Also log to console
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def log_and_print(self, message, level='info'):
        """Log message to file and print to console"""
        if level == 'info':
            self.logger.info(message)
        elif level == 'error':
            self.logger.error(message)
        elif level == 'warning':
            self.logger.warning(message)