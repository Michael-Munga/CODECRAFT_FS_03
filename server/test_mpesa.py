#!/usr/bin/env python3
"""
Test script for M-Pesa integration
"""

import os
import sys
from dotenv import load_dotenv
from mpesa_utils import mpesa_service

# Add the server directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()



def test_mpesa_connection():
    """Test M-Pesa connection and access token generation"""
    print("Testing M-Pesa integration...")
    
    # Test access token generation
    print("\n1. Testing access token generation...")
    token = mpesa_service.get_access_token()
    if token:
        print(f"✓ Access token generated successfully")
        print(f"  Token: {token[:20]}..." if len(token) > 20 else f"  Token: {token}")
    else:
        print("✗ Failed to generate access token")
        return False
    
    # Test password generation
    print("\n2. Testing password generation...")
    password, timestamp = mpesa_service.generate_password()
    if password and timestamp:
        print("✓ Password and timestamp generated successfully")
        print(f"  Password: {password[:20]}..." if len(password) > 20 else f"  Password: {password}")
        print(f"  Timestamp: {timestamp}")
    else:
        print("✗ Failed to generate password")
        return False
    
    print("\n✓ All tests passed! M-Pesa integration is properly configured.")
    return True

if __name__ == "__main__":
    test_mpesa_connection()