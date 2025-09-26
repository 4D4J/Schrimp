#!/usr/bin/env python3
"""
Basic security features for Schrimp Chat Server
No encryption - just rate limiting, anti-spam, and content filtering
"""

import time
from collections import defaultdict, deque


class AntiSpam:
    def __init__(self, max_messages=15, time_window=60):
        self.max_messages = max_messages
        self.time_window = time_window
        self.user_messages = defaultdict(deque)
        self.last_messages = defaultdict(str)
    
    def check_rate_limit(self, username):
        current_time = time.time()
        user_queue = self.user_messages[username]
        
        while user_queue and current_time - user_queue[0] > self.time_window:
            user_queue.popleft()
        
        if len(user_queue) >= self.max_messages:
            return False
        
        user_queue.append(current_time)
        return True
    
    def check_duplicate(self, username, message):
        if self.last_messages[username] == message:
            return False
        
        self.last_messages[username] = message
        return True


class ContentFilter:
    def __init__(self, max_length=500):
        self.max_length = max_length
        self.banned_words = ['spam', 'hack', 'exploit']
    
    def filter_message(self, message):
        if not message or not message.strip():
            return None
        
        if len(message) > self.max_length:
            return f"{message[:self.max_length]}... [truncated]"
        
        for word in self.banned_words:
            if word.lower() in message.lower():
                message = message.replace(word, "*" * len(word))
        
        return message


class SecurityManager:
    def __init__(self, enable_security=True):
        if enable_security:
            self.anti_spam = AntiSpam()
            self.content_filter = ContentFilter()
            self.enabled = True
        else:
            self.anti_spam = None
            self.content_filter = None
            self.enabled = False
    
    def check_rate_limit(self, username):
        if not self.enabled or not self.anti_spam:
            return True
        return self.anti_spam.check_rate_limit(username)
    
    def filter_content(self, message):
        if not self.enabled or not self.content_filter:
            return message
        filtered = self.content_filter.filter_message(message)
        return filtered if filtered is not None else message
    
    def check_duplicate(self, username, message):
        if not self.enabled or not self.anti_spam:
            return True
        return self.anti_spam.check_duplicate(username, message)
