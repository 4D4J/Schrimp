#!/usr/bin/env python3
"""
Test script for integrated security in Schrimp Chat Server
"""

from server import ChatServer

def test_security_integration():
    """Test that security integration works correctly"""
    
    print("Testing Schrimp Chat Server Security Integration")
    print("=" * 50)
    
    # Test 1: Server without security
    print("\n1. Testing server without security...")
    try:
        server1 = ChatServer(port=3032, password="test")
        print("✓ Server created without security")
        server1.stop()
    except Exception as e:
        print(f"✗ Error creating server without security: {e}")
    
    # Test 2: Server with security (if cryptography available)
    print("\n2. Testing server with security...")
    try:
        server2 = ChatServer(
            port=3033, 
            password="test", 
            encryption_password="secret123",
            enable_encryption=True
        )
        print("✓ Server created with security")
        server2.stop()
    except Exception as e:
        print(f"✗ Error creating server with security: {e}")
    
    print("\n" + "=" * 50)
    print("Integration test completed!")

if __name__ == "__main__":
    test_security_integration()